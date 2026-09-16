from dataclasses import replace
import json

import pytest

from faerun import web
from faerun.calendar import HarptosDate
from faerun.data.commodities import COMMODITIES
from faerun.data.populations import WATERDEEP_POPULATION
from faerun.data.settlements import SETTLEMENTS
from faerun.economy import market_report
from faerun.models import S
from faerun.population import population_report
from faerun.requirements import final_requirements, settlement_profile
from faerun.world import World


@pytest.fixture
def waterdeep():
    return replace(next(s for s in SETTLEMENTS if s.id == "waterdeep"))


def test_selected_population_has_honest_evidence_and_no_invented_precision(waterdeep):
    report = population_report(waterdeep)
    assert waterdeep.population == report["resident_population"] == 200_000
    assert report["comparison_residents"] == 130_000
    assert report["status"] == "scenario_estimate"
    assert report["reference_year_dr"] == 1492
    assert report["confidence_interval"] is None
    assert report["external_visitors_per_day"] is None
    assert report["regional_population_added_to_demand"] == 0
    assert report["resident_change"] == 70_000
    assert report["resident_change_pct"] == pytest.approx(53.846153846)
    assert "not a verified census" in report["rationale"]
    assert "editorial interpretation" in report["rationale"]
    assert all(row["kind"] == "secondary" for row in report["evidence"])
    assert any("130,000" in row["description"] for row in report["evidence"])
    assert all(row["url"].startswith("https://") for row in report["evidence"])
    assert json.loads(json.dumps(waterdeep.to_dict()))["population_model"] == report


def test_comparison_and_overrides_report_actual_input_without_mutating_default(waterdeep):
    comparison = replace(waterdeep, population=130_000)
    assert population_report(comparison)["status"] == "comparison_baseline"
    assert population_report(comparison)["household_demand_multiplier"] == 1
    assert population_report(comparison)["resident_change"] == 0
    override = population_report(replace(waterdeep, population=175_000))
    assert override["status"] == "scenario_override"
    assert override["resident_population"] == 175_000
    assert waterdeep.population == WATERDEEP_POPULATION.residents == 200_000
    ordinary = population_report(S("Waterdeep", "Test", "test", 17, 0, 0))
    assert ordinary["status"] == "gazetteer_estimate"
    assert ordinary["resident_population"] == 17
    assert ordinary["reference_year_dr"] is None
    assert not ordinary["evidence"]


@pytest.mark.parametrize("value", [-1, True, 1.5, float("nan"), float("inf")])
def test_invalid_resident_counts_are_rejected(waterdeep, value):
    with pytest.raises(ValueError, match="Resident population"):
        population_report(replace(waterdeep, population=value))


@pytest.mark.parametrize("field", ["residents", "comparison_residents", "reference_year"])
@pytest.mark.parametrize("value", [0, -1, True, 2.5, float("nan")])
def test_invalid_population_basis_is_rejected(field, value):
    with pytest.raises(ValueError, match=field):
        replace(WATERDEEP_POPULATION, **{field: value})


def test_real_household_demand_housing_and_worker_counts_use_the_new_baseline(waterdeep):
    comparison = replace(waterdeep, population=130_000)
    old = final_requirements(comparison, COMMODITIES)
    current = final_requirements(waterdeep, COMMODITIES)
    ratio = 200_000 / 130_000
    household_goods = [cid for cid, parts in old.items() if parts.get("household", 0)]
    assert {"bread", "grain", "clothing_common"} <= set(household_goods)
    for cid in household_goods:
        assert current[cid]["household"] == pytest.approx(old[cid]["household"] * ratio)
    profile = settlement_profile(waterdeep)
    assert profile["population_model"] == population_report(waterdeep)
    assert profile["existing_homes"] == 40_000
    assert profile["worker_population"] == 100_000
    assert (sum(row["workers"] for row in profile["establishments"])
            + profile["unallocated_workers"]) == 100_000
    assert (profile["standing_army"] + profile["militia"]
            + profile["mage_population"]) <= 200_000


def test_population_api_is_lightweight_and_historical_dates_do_not_fake_censuses(
    waterdeep, monkeypatch
):
    from faerun import materials

    def no_price_calculation(*args, **kwargs):
        pytest.fail("Population API must not calculate the material economy")

    monkeypatch.setattr(materials, "economic_report", no_price_calculation)
    world = World(settlements=[waterdeep], date=HarptosDate(1492, 9, 16))
    revision = world.revision
    report = web.GET_ROUTES["/api/population"](world, {"settlement": ["Waterdeep"]})
    assert report["date"] == "16 Eleint 1492 DR"
    assert report["resident_population"] == 200_000
    assert world.revision == revision
    historical = World(settlements=[waterdeep], date=HarptosDate(1372, 1, 1))
    old_date = web.api_population(historical, {"settlement": ["waterdeep"]})
    assert old_date["reference_year_dr"] == 1492
    assert old_date["resident_population"] == 200_000
    with pytest.raises(KeyError):
        web.api_population(world, {"settlement": ["Missing city"]})


def test_market_report_and_economy_expose_consistent_populations(waterdeep):
    from faerun.materials import economic_report

    farm = next(s for s in SETTLEMENTS if s.id == "goldenfields")
    world = World(settlements=[waterdeep, farm], date=HarptosDate(1492, 9, 16))
    report = market_report("waterdeep", world=world, category="food")
    assert report["population"] == 200_000
    assert report["population_model"] == population_report(waterdeep)
    visitor = economic_report("waterdeep", world)["visitors"]
    assert visitor["resident_population"] == 200_000
    assert visitor["modeled_present_population"] == pytest.approx(
        200_000 - visitor["outbound_visitors_per_day"] + visitor["visitors_per_day"]
    )
    assert visitor["external_visitors_per_day"] is None


def test_mcp_population_report_uses_the_active_world(waterdeep, monkeypatch):
    pytest.importorskip("mcp")
    from faerun import mcp_server

    world = World(settlements=[waterdeep], date=HarptosDate(1492, 9, 16))
    monkeypatch.setattr(mcp_server, "world", lambda: world)
    assert mcp_server.get_population_report("Waterdeep") == web.api_population(
        world, {"settlement": ["Waterdeep"]}
    )
    assert "error" in mcp_server.get_population_report("Missing city")
