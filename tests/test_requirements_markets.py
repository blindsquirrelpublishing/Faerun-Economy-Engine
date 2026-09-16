import math
from copy import deepcopy

import pytest

from faerun.economy import _commodity_markets, commodity_sources, market_report, price_for
from faerun.location import location_detail
from faerun.materials import _recipe_order, location_requirements
from faerun.models import C, Event, S
from faerun.world import World


@pytest.fixture(scope="module")
def world():
    return World()


def test_all_locations_and_goods_have_finite_conserved_requirements(world):
    for c in world.commodities.values():
        markets = _commodity_markets(world, c)
        assert set(markets) == set(world.settlements)
        assert sum(q.imports_per_day for q in markets.values()) == pytest.approx(
            sum(q.exports_per_day for q in markets.values()), abs=1e-6)
        for q in markets.values():
            values = (q.final_demand_per_day, q.final_consumption_per_day,
                      q.processing_demand_per_day, q.processing_consumption_per_day,
                      q.production_per_day, q.production_capacity_per_day,
                      q.imports_per_day, q.exports_per_day, q.material_closing_stock,
                      q.unmet_demand_per_day)
            assert all(math.isfinite(v) and v >= -1e-7 for v in values)
            assert q.production_per_day <= q.production_capacity_per_day + 1e-7
            assert q.final_consumption_per_day <= q.final_demand_per_day + 1e-7
            assert q.demand_per_day == pytest.approx(
                sum(q.demand_sectors.values()) + q.processing_demand_per_day)
            assert q.production_per_day + q.imports_per_day == pytest.approx(
                q.final_consumption_per_day + q.processing_consumption_per_day
                + q.exports_per_day + q.material_closing_stock, abs=1e-6)
            assert q.exports_per_day <= max(0, q.production_per_day - q.demand_per_day) + 1e-6
            assert q.imports_per_day + q.unmet_demand_per_day == pytest.approx(
                max(0, q.demand_per_day - q.production_per_day), abs=1e-6)
            for row in q.production_inputs:
                coefficient = c.bom[row["commodity"]]
                assert row["consumed_per_day"] == pytest.approx(q.production_per_day * coefficient)
                assert row["consumed_per_day"] <= row["reserved_per_day"] + 1e-7


def test_weapons_cascade_to_smelters_ore_and_fuel(world):
    sword = price_for("Waterdeep", "sword", world=world)
    steel = price_for("Waterdeep", "steel_ingot", world=world)
    iron = price_for("Waterdeep", "iron_ingot", world=world)
    ore = price_for("Waterdeep", "iron_ore", world=world)
    assert sword.demand_sectors["defense"] > 0
    assert sword.production_inputs
    assert steel.processing_demand_per_day > 0
    assert iron.processing_demand_per_day > 0
    assert ore.processing_demand_per_day > 0
    assert ore.imports_per_day + ore.unmet_demand_per_day > 0
    assert {row["commodity"] for row in iron.production_inputs} == {"iron_ore", "charcoal"}


def test_timber_failure_limits_downstream_construction():
    world = World()
    before = price_for("Waterdeep", "planks", world=world)
    assert before.production_per_day > 0
    world.add_event(Event(id="timber_failure", name="No timber", commodities=["timber"], supply=0))
    planks = _commodity_markets(world, world.find_commodity("planks"))
    assert all(q.production_per_day == 0 for q in planks.values())
    assert planks["waterdeep"].unmet_demand_per_day > 0
    assert all(q.production_per_day == 0 for q in
               _commodity_markets(world, world.find_commodity("cart")).values())


def test_exotic_imports_come_from_eligible_producers(world):
    q = price_for("Waterdeep", "black_pepper", world=world)
    assert q.final_demand_per_day > 0
    assert q.production_per_day == 0
    assert q.imports_per_day > 0
    c = world.find_commodity("black_pepper")
    for source in q.sources:
        s = world.settlements[source["source_id"]]
        assert any(s.terrain == gate or s.has_trait(gate) for gate in c.requires)


def test_location_report_uses_market_flows_and_all_goods(world):
    report = location_requirements("Waterdeep", world)
    assert report["enabled"]
    assert {row["commodity_id"] for row in report["materials"]} == set(world.commodities)
    for row in report["materials"]:
        q = price_for("Waterdeep", row["commodity_id"], world=world)
        assert row["demand_per_day"] == q.demand_per_day
        assert row["imports_per_day"] == q.imports_per_day
        assert sum(r["quantity_per_day"] for r in row["export_destinations"]) == pytest.approx(q.exports_per_day)
    assert report["profile"]["standing_army"] > 0
    assert report["profile"]["mage_population"] > 0
    assert report["assumptions"]
    grain = next(row for row in report["materials"] if row["commodity_id"] == "grain")
    assert grain["production_per_day"] > 0
    assert grain["import_need_per_day"] > 0


def test_source_catalog_reports_actual_recipe_limited_production(world):
    for cid in ("sword", "planks", "spellbook_blank", "fish_fresh"):
        sources = commodity_sources(cid, world=world, limit=10000)["sources"]
        assert sources
        for source in sources:
            q = price_for(source["id"], cid, world=world)
            assert source["production_per_day"] == q.production_per_day


def test_repeated_queries_and_legacy_toggle_invalidate_cache():
    world = World(settlements=[S("Test Port", "Test", "test", 2000, 0, 0,
                                terrain="coast", port="Test Sea")])
    expanded = price_for("Test Port", "fish_fresh", world=world)
    assert expanded.production_per_day > 0
    assert price_for("Test Port", "fish_fresh", world=world).to_dict() == expanded.to_dict()
    world.config.expanded_requirements = False
    assert price_for("Test Port", "fish_fresh", world=world).production_per_day == 0
    world.config.expanded_requirements = True
    assert price_for("Test Port", "fish_fresh", world=world).to_dict() == expanded.to_dict()


def test_missing_and_cyclic_recipe_inputs_are_reported():
    a = C("a", "A", "test", 1)
    b = C("b", "B", "test", 1)
    a.bom = {"b": 1}
    with pytest.raises(ValueError, match="Missing recipe ingredient"):
        _recipe_order({"a": a})
    b.bom = {"a": 1}
    with pytest.raises(ValueError, match="cycle"):
        _recipe_order({"a": a, "b": b})


def test_filtered_location_detail_still_contains_complete_requirements():
    world = World(settlements=[deepcopy(S("Test", "Test", "test", 400, 0, 0, ind="farm2 craft2"))])
    detail = location_detail("Test", world=world, category="food")
    assert all(row["category"] == "food" for row in detail["market"]["prices"])
    assert len(detail["requirements"]["materials"]) == len(world.commodities)
    assert set(row["commodity_id"] for row in market_report("Test", world=world)["daily_requirements"]) == set(world.commodities)
    world.config.expanded_requirements = False
    assert location_detail("Test", world=world, category="food")["requirements"]["enabled"] is False


def test_zero_demand_producer_can_supply_another_market(monkeypatch):
    from faerun import materials

    good = C("test_ore", "Test ore", "metal", 1, produced_by="mine_iron")
    world = World(
        settlements=[S("Mine", "Test", "test", 100, 0, 0, ind="mine_iron3"),
                     S("Forge", "Test", "test", 100, 20, 0)],
        commodities=[good],
    )
    monkeypatch.setattr(materials, "final_requirements",
                        lambda s, goods, **kwargs: {"test_ore": {"construction": 0 if s.id == "mine" else 1}})
    monkeypatch.setattr(materials, "local_resource_capacity", lambda s, c: 10 if s.id == "mine" else 0)
    buyer = price_for("Forge", good, world=world)
    assert buyer.imports_per_day == 1
    assert buyer.unmet_demand_per_day == 0
    assert price_for("Mine", good, world=world).exports_per_day == 1


def test_delivery_capacity_is_shared_and_reported_as_unmet(monkeypatch):
    from faerun import materials

    good = C("test_ore", "Test ore", "metal", 1, produced_by="mine_iron")
    world = World(
        settlements=[S("Mine", "Test", "test", 100, 0, 0, ind="mine_iron3"),
                     S("Forge", "Test", "test", 100, 20, 0)],
        commodities=[good],
    )
    monkeypatch.setattr(materials, "final_requirements",
                        lambda s, goods, **kwargs: {"test_ore": {"construction": 0 if s.id == "mine" else 1}})
    monkeypatch.setattr(materials, "local_resource_capacity", lambda s, c: 10 if s.id == "mine" else 0)
    world.config.delivery_limits[("test_ore", "mine", "forge")] = 0.25
    q = price_for("Forge", good, world=world)
    assert q.imports_per_day == 0.25
    assert q.unmet_demand_per_day == 0.75


def test_businesses_do_not_sell_stock_already_committed_to_exports(world):
    from faerun.web import api_businesses

    result = api_businesses(world, {"settlement": ["Waterdeep"]})
    assert result["businesses"]
    for business in result["businesses"]:
        for offer in business["offers"]:
            q = price_for("Waterdeep", offer["commodity"], world=world)
            assert q.stock > 0
            assert offer["stock"] <= q.stock


def test_conservative_resource_mode_exposes_shortages_and_invalidates_cache():
    w = World()
    normal = price_for("Waterdeep", "timber", world=w)
    factor = normal.factors["hinterland_capacity_multiplier"]
    assert factor > 1
    w.config.calibrate_source_districts = False
    conservative = price_for("Waterdeep", "timber", world=w)
    assert conservative.factors["hinterland_capacity_multiplier"] == 1
    assert conservative.unmet_demand_per_day > normal.unmet_demand_per_day


def test_extreme_legacy_event_intensity_stops_supply_without_negative_materials():
    good = C("grain", "Grain", "food", 1, "bushel", 60, "farm")
    w = World(settlements=[S("Farm", "Test", "test", 400, 0, 0, ind="farm2")],
              commodities=[good])
    w.add_event(Event(id="famine", name="Extreme famine", supply=-0.0528, commodities=["grain"]))
    q = price_for("Farm", "grain", world=w)
    assert q.production_per_day == 0
    assert q.unmet_demand_per_day > 0
