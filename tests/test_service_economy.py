import math

import pytest

from faerun.economy import _commodity_markets, price_for
from faerun.location import location_detail
from faerun.materials import _economy_cache, location_requirements
from faerun.models import C, S
from faerun.world import World


EXPECTED_SECTORS = {
    "health", "religion", "animals", "administration", "knowledge", "commerce",
    "logistics", "communications", "hospitality", "utilities", "civil_security",
    "maintenance", "culture", "professional",
}


@pytest.fixture(scope="module")
def world():
    w = World()
    price_for("Waterdeep", "grain", world=w)
    return w


def test_every_location_has_service_and_local_accounts(world):
    snapshots = _economy_cache(world)[world.economy_state_key()]
    assert set(snapshots) == set(world.settlements)
    for sid, result in snapshots.items():
        assert {row["id"] for row in result["industries"]} == EXPECTED_SECTORS
        assert sum(row["workers"] for row in result["industries"]) <= world.settlements[sid].population * .5 + 1e-6
        accounts = result["accounts"]
        assert accounts["gross_local_product_gp_per_day"] == pytest.approx(
            accounts["goods_output_gp_per_day"] - accounts["goods_intermediate_gp_per_day"]
            + accounts["service_output_gp_per_day"] - accounts["service_intermediate_gp_per_day"])
        assert accounts["gross_local_product_gp_per_year"] == pytest.approx(
            accounts["gross_local_product_gp_per_day"] * 365)
        assert all(math.isfinite(value) for value in accounts.values() if isinstance(value, (float, int)))
        for row in result["industries"]:
            assert 0 <= row["delivered_per_day"] <= row["planned_per_day"] + 1e-7
            assert row["planned_per_day"] <= row["capacity_per_day"] + 1e-7
            assert row["unmet_per_day"] == pytest.approx(row["demand_per_day"] - row["delivered_per_day"])
            for ingredient in row["inputs"]:
                assert ingredient["consumed_per_day"] <= ingredient["reserved_per_day"] + 1e-7


def test_goods_and_domestic_gold_flows_conserve_across_all_locations(world):
    snapshots = _economy_cache(world)[world.economy_state_key()]
    accounts = [row["accounts"] for row in snapshots.values()]
    assert sum(a["goods_exports_gp_per_day"] for a in accounts) == pytest.approx(
        sum(a["goods_imports_gp_per_day"] for a in accounts), rel=1e-10)
    assert sum(a["visitor_receipts_gp_per_day"] for a in accounts) > 0
    assert sum(a["visitor_receipts_gp_per_day"] for a in accounts) == pytest.approx(
        sum(a["resident_travel_spending_gp_per_day"] for a in accounts), rel=1e-10)
    assert sum(a["external_balance_gp_per_day"] for a in accounts) == pytest.approx(0, abs=1e-5)
    for c in world.commodities.values():
        for q in _commodity_markets(world, c).values():
            assert q.production_per_day + q.imports_per_day == pytest.approx(
                q.exports_per_day + q.final_consumption_per_day
                + q.processing_consumption_per_day + q.material_closing_stock, abs=1e-6)
            assert sum(q.consumption_sectors.values()) == pytest.approx(q.final_consumption_per_day, abs=1e-7)
            assert all(value >= -1e-9 and math.isfinite(value) for value in q.consumption_sectors.values())


def test_visitors_have_matched_origins_fixed_beds_and_resource_demand(world):
    results = _economy_cache(world)[world.economy_state_key()]
    incoming = sum(row["visitors"]["visitors_per_day"] for row in results.values())
    outgoing = sum(row["visitors"]["outbound_visitors_per_day"] for row in results.values())
    assert incoming > 0
    assert incoming == pytest.approx(outgoing)
    assert any(row["visitors"]["visitor_goods_demand_weight_lb_per_day"] > 0 for row in results.values())
    for result in results.values():
        visitors = result["visitors"]
        assert visitors["overnight_visitors_per_day"] <= visitors["beds"] + 1e-6
        assert visitors["visitor_goods_supplied_weight_lb_per_day"] <= visitors["visitor_goods_demand_weight_lb_per_day"] + 1e-6
        assert sum(row["spending_gp_per_day"] for row in visitors["origins"]) == pytest.approx(visitors["visitor_spending_gp_per_day"])
        assert sum(row["spending_gp_per_day"] for row in visitors["destinations"]) == pytest.approx(visitors["visitor_spending_abroad_gp_per_day"])


def small_world():
    return World(settlements=[
        S("City", "Test", "test", 3000, 0, 0, wealth=1.35, ind="craft3 trade3 paper2 arcane2",
          traits="cosmopolitan academic arcane"),
        S("Shrine", "Test", "test", 500, 30, 0, terrain="hills", ind="farm1 temple3",
          traits="temple agrarian"),
    ])


def test_visitors_change_demand_without_resizing_baseline_production():
    w = small_world()
    w.config.visitor_scale = 0
    before = location_requirements("Shrine", w)
    w.config.visitor_scale = 5
    after = location_requirements("Shrine", w)
    assert after["economy"]["visitors"]["visitors_per_day"] > 0
    assert after["economy"]["visitors"]["visitor_spending_gp_per_day"] > 0
    old = {row["commodity_id"]: row for row in before["materials"]}
    assert any(row["sectors"].get("visitors", 0) > 0 for row in after["materials"])
    for row in after["materials"]:
        assert row["capacity_per_day"] == old[row["commodity_id"]]["capacity_per_day"]
    assert after["economy"]["visitors"]["beds"] == before["economy"]["visitors"]["beds"]


def test_feature_flags_and_detail_cache_are_consistent():
    w = small_world()
    active = location_detail("City", world=w)
    assert active["requirements"]["economy"]["industries"]
    w.config.service_economy = False
    legacy = location_detail("City", world=w)
    assert not legacy["requirements"]["economy"]["industries"]
    assert not legacy["requirements"]["economy"]["visitors"]["enabled"]
    assert legacy["requirements"]["economy"]["accounts"]["service_output_gp_per_day"] == 0


def test_selected_month_and_repeated_reads_do_not_mutate_population_or_wealth():
    w = small_world()
    before = [(s.population, s.wealth) for s in w.settlements.values()]
    date = w.date
    month = date.absolute_month() + 1
    first = location_detail("City", world=w, month=month)
    second = location_detail("City", world=w, month=month)
    assert first == second
    assert w.date == date
    assert [(s.population, s.wealth) for s in w.settlements.values()] == before
    assert first["requirements"]["date"] == str(date.advance(1))


def test_empty_place_has_zero_output_and_no_per_capita_division():
    w = World(settlements=[S("Empty", "Test", "test", 0, 0, 0)],
              commodities=[C("grain", "Grain", "food", 1, "bushel", 60, "farm")])
    result = location_requirements("Empty", w)["economy"]
    assert result["accounts"]["gross_local_product_gp_per_day"] == 0
    assert result["accounts"]["glp_per_resident_gp_per_year"] is None
    assert result["visitors"]["visitors_per_day"] == 0


def test_market_and_trade_apis_share_the_same_accounts(world):
    from faerun.economy import market_report, trade_summary
    from faerun.materials import economic_report

    accounts = economic_report("Waterdeep", world)["accounts"]
    assert market_report("Waterdeep", world=world, commodities=["grain"])["accounts"] == accounts
    assert trade_summary("Waterdeep", world=world)["accounts"] == accounts
