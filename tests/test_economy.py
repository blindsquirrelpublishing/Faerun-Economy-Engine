"""Data integrity and directional sanity checks for the Faerûn market engine."""

from __future__ import annotations

import pytest

from faerun.calendar import HarptosDate
from faerun.data.commodities import CATEGORIES, COMMODITIES, COMMODITIES_BY_ID
from faerun.data.routes import NAMED_ROUTES, NAMED_SEA_LANES
from faerun.data.settlements import SETTLEMENTS, SETTLEMENTS_BY_ID, ZONE_ADJACENCY
from faerun.economy import (
    commodity_sources,
    compare_prices,
    demand_index,
    find_arbitrage,
    market_report,
    price_for,
    price_history,
    sourcing_catalog,
    trade_summary,
)
from faerun.events import EVENT_TEMPLATES, make_event
from faerun.living import (
    BREAD_GRAIN_EQUIVALENT,
    FLOUR_GRAIN_EQUIVALENT,
    LIVING_STANDARDS,
    daily_requirement,
    per_person_daily_requirements,
    settlement_per_person_daily_requirements,
    settlement_daily_requirements,
)
from faerun.world import World

TERRAINS = {s.terrain for s in SETTLEMENTS}
TRAITS = {t for s in SETTLEMENTS for t in s.traits}
INDUSTRIES = {tag for s in SETTLEMENTS for tag in s.industries}


@pytest.fixture(scope="module")
def world() -> World:
    return World()


# ---------------------------------------------------------------------------
# Static data
# ---------------------------------------------------------------------------


def test_ids_are_unique():
    assert len(COMMODITIES_BY_ID) == len(COMMODITIES)
    assert len(SETTLEMENTS_BY_ID) == len(SETTLEMENTS)


def test_specialties_and_shortages_name_real_goods():
    bad = [
        f"{s.name} references unknown good {cid!r}"
        for s in SETTLEMENTS
        for cid in list(s.specialties) + list(s.shortages)
        if cid not in COMMODITIES_BY_ID
    ]
    assert not bad, "\n".join(bad)


def test_routes_only_link_known_settlements():
    for name, stops, _quality, _kind in NAMED_ROUTES:
        for sid in stops:
            assert sid in SETTLEMENTS_BY_ID, f"{name} stops at unknown {sid!r}"
    # A lane is (name, stops, quality) with an optional fourth kind element.
    for lane in NAMED_SEA_LANES:
        name, stops = lane[0], lane[1]
        for sid in stops:
            assert sid in SETTLEMENTS_BY_ID, f"{name} calls at unknown {sid!r}"


def test_sea_lanes_only_call_at_ports():
    for lane in NAMED_SEA_LANES:
        name, stops = lane[0], lane[1]
        for sid in stops:
            assert SETTLEMENTS_BY_ID[sid].port, f"{name} calls at inland {sid!r}"


def test_zone_adjacency_names_real_zones():
    zones = {s.zone for s in SETTLEMENTS}
    for zone, neighbours in ZONE_ADJACENCY.items():
        assert zone in zones, f"unknown zone {zone!r}"
        for other in neighbours:
            assert other in zones, f"{zone} borders unknown zone {other!r}"


def test_commodity_gates_use_real_terrain_or_traits():
    for c in COMMODITIES:
        for gate in c.requires:
            assert gate in TERRAINS or gate in TRAITS, \
                f"{c.id} requires unknown terrain/trait {gate!r}"
        for trait in c.demand_traits:
            assert trait in TRAITS, f"{c.id} wants unknown trait {trait!r}"
        for other in c.substitutes:
            assert other in COMMODITIES_BY_ID, f"{c.id} substitutes unknown {other!r}"
        assert c.base_price > 0
        assert c.weight > 0
        assert c.category in CATEGORIES


def test_every_good_has_at_least_one_producer(world):
    for c in COMMODITIES:
        makers = [
            s for s in SETTLEMENTS
            if (not c.requires
                or any(s.terrain == g or s.has_trait(g) for g in c.requires))
            and (any(s.industry_level(tag) for tag in c.produced_by)
                 or c.id in s.specialties)
        ]
        assert makers, f"nobody in Faerûn can make {c.id}"


def test_the_world_graph_is_connected(world):
    reachable = {sid for sid in world.settlements
                 if world.route("waterdeep", sid)["reachable"]}
    assert reachable == set(world.settlements)


# ---------------------------------------------------------------------------
# Prices
# ---------------------------------------------------------------------------


def test_unavailable_goods_have_no_allocated_supply(world):
    for c in world.commodities.values():
        for quote in compare_prices(c.id, world=world, limit=10_000)["markets"]:
            if quote["availability"] == "unavailable":
                assert quote["stock"] == 0
                assert quote["production_per_day"] == 0
                assert quote["imports_per_day"] == 0
                assert quote["unmet_demand_per_day"] >= 0
                if quote["unmet_demand_per_day"] == 0:
                    assert quote["demand_per_day"] == 0


def test_prices_stay_inside_sane_bounds(world):
    for c in world.commodities.values():
        for quote in compare_prices(c.id, world=world, limit=10_000)["markets"]:
            ratio = quote["price"] / c.base_price
            assert 0.2 <= ratio <= 40.0, \
                f"{c.id} in {quote['settlement']} is x{ratio:.1f} base"
            assert quote["buy_price"] <= quote["price"], \
                f"{c.id} in {quote['settlement']} buys back above its asking price"


def test_grain_is_cheap_where_it_grows_and_dear_in_the_north(world):
    goldenfields = price_for("Goldenfields", "grain", world=world)
    waterdeep = price_for("Waterdeep", "grain", world=world)
    bryn_shander = price_for("Bryn Shander", "grain", world=world)
    assert goldenfields.price < waterdeep.price < bryn_shander.price
    assert goldenfields.multiplier < 1.0
    assert bryn_shander.multiplier > 3.0


def test_mithral_is_cheap_and_exported_at_the_mine(world):
    quote = price_for("Mithral Hall", "mithral_ingot", world=world)
    assert quote.multiplier < 1.0
    assert quote.exports_per_day > 0


def test_imports_name_their_source(world):
    quote = price_for("Waterdeep", "grain", world=world)
    assert quote.source, "Waterdeep should receive allocated grain imports"
    assert quote.source_distance and quote.source_distance > 0
    assert quote.source_days and quote.source_days > 0
    assert quote.price > price_for(quote.source, "grain", world=world).price


def test_buying_in_bulk_moves_the_market(world):
    one = price_for("Bryn Shander", "grain", world=world, quantity=1)
    many = price_for("Bryn Shander", "grain", world=world, quantity=5000)
    assert many.price > one.price
    assert many.buy_price <= one.buy_price


def test_seasons_move_perishable_prices(world):
    w = World()
    w.set_date(HarptosDate(1492, 2))   # Alturiak, deep winter
    winter = price_for("Waterdeep", "grain", world=w).price
    w.set_date(HarptosDate(1492, 9))   # Eleint, harvest
    harvest = price_for("Waterdeep", "grain", world=w).price
    assert winter > harvest


def test_prices_are_deterministic(world):
    a = price_for("Baldur's Gate", "iron_ingot", world=World()).price
    b = price_for("Baldur's Gate", "iron_ingot", world=World()).price
    assert a == b


def test_the_seed_changes_prices_but_not_much():
    a = World()
    b = World()
    b.config.seed = 7777
    b.revision += 1
    pa = price_for("Baldur's Gate", "iron_ingot", world=a).price
    pb = price_for("Baldur's Gate", "iron_ingot", world=b).price
    assert pa != pb
    assert abs(pa - pb) / pa < 0.25


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


def test_a_siege_raises_the_price_of_food():
    quiet = World()
    besieged = World()
    before = price_for("Goldenfields", "grain", world=quiet).price
    besieged.add_event(make_event(template="siege",
                                  settlements=["Goldenfields"],
                                  world=besieged))
    after = price_for("Goldenfields", "grain", world=besieged).price
    assert after > before * 1.1


def test_clearing_events_restores_the_baseline():
    w = World()
    before = price_for("Goldenfields", "grain", world=w).price
    w.add_event(make_event(template="siege", settlements=["Goldenfields"], world=w))
    assert price_for("Goldenfields", "grain", world=w).price != before
    w.clear_events()
    assert price_for("Goldenfields", "grain", world=w).price == before


def test_every_template_builds_a_usable_event():
    w = World()
    for name in EVENT_TEMPLATES:
        event = make_event(template=name, settlements=["Waterdeep"], world=w)
        assert event.id and event.name
        assert event.settlements == ["waterdeep"]


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------


def test_market_report_covers_every_good(world):
    report = market_report("Waterdeep", world=world)
    assert len(report["prices"]) == len(world.commodities)
    assert report["region"]
    assert report["cheap_here"] and report["dear_here"]


def test_trade_summary_splits_exports_from_imports(world):
    summary = trade_summary("Mithral Hall", world=world, top=5)
    assert len(summary["exports"]) == 5
    assert summary["exports"][0]["x_base"] <= summary["imports"][0]["x_base"]


def test_source_report_distinguishes_local_resources_and_quality(world):
    grain = commodity_sources("grain", world=world)
    coffee = commodity_sources("coffee", world=world)
    iron = commodity_sources("iron_ore", world=world)
    wine = commodity_sources("wine_fine", world=world)

    assert grain["source_scope"] == "widespread"
    assert coffee["source_scope"] == "restricted"
    assert coffee["source_requirements"] == ["jungle"]
    assert {source["terrain"] for source in coffee["sources"]} == {"jungle"}
    assert iron["source_scope"] == "extractive"
    assert any(source["quality"] == "renowned" for source in wine["sources"])


def test_source_catalog_supports_common_crops_and_constrained_salt(world):
    crops = sourcing_catalog(world=world, search="corn")
    salt = commodity_sources("salt", world=world, limit=1000)

    assert crops["count"] == 1
    assert crops["commodities"][0]["source_scope"] == "widespread"
    assert salt["source_scope"] == "extractive"
    assert all(
        world.settlements[source["id"]].industry_level("salt")
        or world.settlements[source["id"]].specialties.get("salt")
        for source in salt["sources"]
    )


def test_blank_spellbooks_come_from_paper_centers_or_specialist_hubs(world):
    sources = commodity_sources("spellbook_blank", world=world, limit=1000)["sources"]

    assert {"waterdeep", "candlekeep", "silverymoon", "sshamath", "halarahh", "eltabbar"} <= {
        source["id"] for source in sources
    }
    assert all(
        world.settlements[source["id"]].industry_level("paper")
        or world.settlements[source["id"]].specialties.get("spellbook_blank")
        for source in sources
    )
    assert "myth_drannor" not in {source["id"] for source in sources}


def test_goods_have_source_driven_quality_prices_and_availability(world):
    standard = price_for("Eltabbar", "spellbook_blank", world=world)
    masterwork = price_for(
        "Eltabbar", "spellbook_blank", world=world, quality="masterwork"
    )
    hlath = price_for("Hlath", "spellbook_blank", world=world)

    assert [offer["quality"] for offer in standard.quality_offers] == [
        "basic", "standard", "fine", "masterwork"
    ]
    assert masterwork.price == pytest.approx(standard.price * 4, abs=0.01)
    assert masterwork.stock < standard.stock
    assert masterwork.availability in {"rare", "scarce", "common", "abundant"}
    assert hlath.source is None
    assert hlath.unmet_demand_per_day == pytest.approx(hlath.demand_per_day, abs=0.001)
    assert price_for(
        "Hlath", "spellbook_blank", world=world, quality="fine"
    ).availability == "unavailable"
    assert price_for(
        "Hlath", "spellbook_blank", world=world, quality="masterwork"
    ).availability == "unavailable"


def test_crafted_goods_have_simple_valid_boms(world):
    assert world.find_commodity("bread").bom == {"flour": 0.02, "salt": 0.001}
    assert world.find_commodity("sword").bom["steel_ingot"] == 0.3
    assert world.find_commodity("cart").bom == {"planks": 0.5, "nails": 0.2}
    assert world.find_commodity("warhorse").bom == {
        "horse_riding": 1.0,
        "grain": 20.0,
        "saddle": 1.0,
    }
    assert world.find_commodity("grain").bom == {}
    assert world.find_commodity("grain").production_type == "raw"
    assert world.find_commodity("bread").production_type == "processed/manufactured"
    assert world.find_commodity("bread").to_dict()["production_type"] == "processed/manufactured"
    assert all(
        component_id in world.commodities and quantity > 0
        for commodity in world.commodities.values()
        for component_id, quantity in commodity.bom.items()
    )


def test_legacy_daily_production_and_demand_use_market_volume():
    world = World()
    world.config.expanded_requirements = False
    local = price_for("Goldenfields", "grain", world=world)
    imported = price_for("Waterdeep", "coffee", world=world)
    goldenfields = world.find_settlement("Goldenfields")
    grain = world.find_commodity("grain")
    baseline_per_day = goldenfields.population * daily_requirement(
        grain.id, goldenfields.wealth, settlement=goldenfields
    )

    assert local.production_per_day == pytest.approx(
        baseline_per_day * local.supply_index, abs=0.01
    )
    assert local.household_demand_per_day == pytest.approx(
        baseline_per_day * demand_index(world, goldenfields, grain), abs=0.001
    )
    assert local.demand_per_day == pytest.approx(
        local.household_demand_per_day + local.processing_demand_per_day, abs=0.001
    )
    assert local.processing_demand_per_day > 0
    assert imported.production_per_day == 0
    assert imported.demand_per_day > 0

    source = commodity_sources("grain", world=world)["sources"][0]
    assert source["production_per_day"] > 0
    assert source["demand_per_day"] > 0
    assert source["unit"] == "bushel"


def test_living_standard_baseline_scales_with_souls(world):
    report = settlement_daily_requirements("Daggerford", world=world)
    grain = next(
        row for row in report["requirements"] if row["commodity_id"] == "grain"
    )

    assert report["population"] == 900
    assert report["living_standard"] == "common"
    assert grain["settlement_per_day"] == pytest.approx(
        grain["per_person_per_day"] * report["population"], abs=0.001
    )
    market = market_report("Daggerford", world=world, commodities=["grain"])
    assert market["living_standard"] == report["living_standard"]
    assert market["daily_requirements"] == report["requirements"]


def test_living_standard_interpolates_between_poor_and_rich_profiles():
    common = per_person_daily_requirements(1.0)
    between = per_person_daily_requirements(1.2)

    assert common == pytest.approx(LIVING_STANDARDS["common"])
    assert common["meat_fresh"] < between["meat_fresh"] < LIVING_STANDARDS["rich"]["meat_fresh"]
    assert per_person_daily_requirements(0.1) == LIVING_STANDARDS["poor"]
    assert per_person_daily_requirements(5.0) == LIVING_STANDARDS["rich"]


def test_staple_baseline_is_allocated_without_double_counting(world):
    market = world.find_settlement("Lheshayl")
    requirements = settlement_per_person_daily_requirements(market)
    grain_equivalent = (
        requirements["grain"]
        + requirements["flour"] * FLOUR_GRAIN_EQUIVALENT
        + requirements["bread"] * BREAD_GRAIN_EQUIVALENT
    )

    assert requirements["bread"] > 0
    assert requirements["flour"] > 0
    assert grain_equivalent == pytest.approx(
        per_person_daily_requirements(market.wealth)["grain"]
    )


def test_price_history_covers_a_year(world):
    history = price_history("Waterdeep", "grain", world=world, months=12)
    assert len(history["series"]) == 12
    assert history["low"] <= history["average"] <= history["high"]
    assert {p["season"] for p in history["series"]} == {
        "winter", "spring", "summer", "autumn"}


def test_arbitrage_finds_profitable_cargoes(world):
    result = find_arbitrage("Waterdeep", world=world, max_days=60, limit=10)
    assert result["deals"]
    for deal in result["deals"]:
        assert deal["profit_per_unit"] > 0
        assert deal["travel_days"] <= 60
        assert deal["destination"] != "Waterdeep"


def test_routes_are_symmetric_and_plausible(world):
    there = world.route("Waterdeep", "Baldur's Gate")
    back = world.route("Baldur's Gate", "Waterdeep")
    assert there["reachable"] and back["reachable"]
    assert there["distance"] == pytest.approx(back["distance"], rel=0.01)
    assert there["legs"][0]["from"] == "Waterdeep"
    assert there["path"][-1] == "Baldur's Gate"
