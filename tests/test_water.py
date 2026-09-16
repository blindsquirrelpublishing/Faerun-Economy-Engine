import math

import pytest

from faerun.models import C, S
from faerun.water import (
    DOMESTIC_GALLONS_PER_PERSON, ESSENTIAL_GALLONS_PER_PERSON,
    LITRES_PER_GALLON, water_balance, water_resources,
)


def town(terrain="desert", population=2000, **kwargs):
    return S("Water Town", "Test", "test", population, 0, 0, terrain=terrain, **kwargs)


@pytest.mark.parametrize("terrain", ["desert", "tundra", "cavern", "hills", "forest", "plains", "coast"])
def test_no_municipal_workers_does_not_mean_no_usable_water(terrain):
    resources = water_resources(town(terrain), "winter")
    result = water_balance(resources, 2000, 0, 0, 0)
    assert result["natural_gallons_per_day"] > 0
    assert result["household_delivered_gallons_per_day"] > 0
    assert result["essential_gap_gallons_per_day"] == 0
    assert result["evidence"] == "inferred; hydrology unverified"
    assert not result["mortality_modeled"]


@pytest.mark.parametrize("municipal", [0, 500, 50000])
def test_water_is_reserved_once_and_essentials_take_priority(municipal):
    resources = water_resources(town(), overrides={"natural_gallons_per_day": 3000, "potable_fraction": .8})
    result = water_balance(resources, 2000, 0, municipal, municipal)
    assert result["total_delivered_gallons_per_day"] <= 2400
    assert result["municipal_delivered_gallons_per_day"] + result["household_delivered_gallons_per_day"] == pytest.approx(
        result["total_delivered_gallons_per_day"])
    assert result["total_delivered_gallons_per_day"] + result["unused_usable_gallons_per_day"] == pytest.approx(2400)
    assert result["essential_supplied_gallons_per_day"] == 2400
    assert result["routine_supplied_gallons_per_day"] == 0
    gap = result["essential_gap_gallons_per_day"] + result["routine_gap_gallons_per_day"]
    assert gap == pytest.approx(result["source_gap_gallons_per_day"] + result["access_gap_gallons_per_day"] + result["operations_gap_gallons_per_day"])


@pytest.mark.parametrize("override", [
    {"source_multiplier": 0}, {"potable_fraction": 0}, {"natural_gallons_per_day": 0},
])
def test_explicit_source_failure_is_not_filled_by_an_inferred_fallback(override):
    resources = water_resources(town(), overrides=override)
    result = water_balance(resources, 2000, 0, 10000, 10000)
    assert result["total_delivered_gallons_per_day"] == 0
    assert result["status"] == "essential_gap"
    assert result["essential_gap_gallons_per_day"] == pytest.approx(2000 * ESSENTIAL_GALLONS_PER_PERSON)
    assert result["evidence"] == "scenario override"


def test_visitor_demand_does_not_create_sources_or_household_collectors():
    resources = water_resources(town())
    baseline = water_balance(resources, 2000, 0, 2000, 2000)
    busy = water_balance(resources, 2000, 2000, 2000, 2000)
    assert busy["usable_gallons_per_day"] == baseline["usable_gallons_per_day"]
    assert busy["household_capacity_gallons_per_day"] == baseline["household_capacity_gallons_per_day"]
    assert busy["total_demand_gallons_per_day"] == 2 * baseline["total_demand_gallons_per_day"]
    assert busy["essential_gap_gallons_per_day"] >= baseline["essential_gap_gallons_per_day"]


def test_port_metadata_is_not_a_freshwater_source():
    inland = water_resources(town())
    port = water_resources(town(port="Sea", traits="port"))
    assert port["natural_gallons_per_day"] == inland["natural_gallons_per_day"]
    river = water_resources(town(river=True))
    assert river["natural_gallons_per_day"] > inland["natural_gallons_per_day"]


def test_gallon_conversion_and_empty_population():
    result = water_balance(water_resources(town()), 2000, 0, 0, 0)
    assert result["unit"] == "gallon"
    assert result["total_demand_gallons_per_day"] == pytest.approx(40000 / LITRES_PER_GALLON)
    assert DOMESTIC_GALLONS_PER_PERSON == pytest.approx(20 / LITRES_PER_GALLON)
    empty = water_balance(water_resources(town(population=0)), 0, 0, 0, 0)
    assert empty["essential_coverage"] is None
    assert empty["total_demand_gallons_per_day"] == 0
    assert all(math.isfinite(value) for value in empty.values() if isinstance(value, float))


@pytest.mark.parametrize("override", [
    {"source_multiplier": -1}, {"natural_gallons_per_day": float("nan")},
    {"potable_fraction": 1.1}, {"source_multiplier": True},
    {"unknown_source": 10}, {"natural_litres_per_day": 10},
    {"natural_gallons_per_day": 1e308, "source_multiplier": 1e308},
])
def test_invalid_or_wrong_unit_scenarios_fail_explicitly(override):
    with pytest.raises(ValueError):
        water_resources(town(), overrides=override)


def test_yallasch_and_all_location_water_ledgers_reconcile():
    from faerun.materials import economic_report, _economy_cache
    from faerun.world import World

    world = World()
    yallasch = economic_report("Yallasch", world)["water"]
    assert yallasch["essential_gap_gallons_per_day"] == 0
    assert yallasch["household_delivered_gallons_per_day"] > 0
    assert yallasch["profile_inferred"]
    for data in _economy_cache(world)[world.economy_state_key()].values():
        w = data["water"]
        assert w["total_delivered_gallons_per_day"] <= w["usable_gallons_per_day"] + 1e-6
        assert w["total_demand_gallons_per_day"] == pytest.approx(
            w["total_delivered_gallons_per_day"] + w["essential_gap_gallons_per_day"] + w["routine_gap_gallons_per_day"])
        assert w["total_demand_gallons_per_day"] - w["total_delivered_gallons_per_day"] == pytest.approx(
            w["source_gap_gallons_per_day"] + w["access_gap_gallons_per_day"] + w["operations_gap_gallons_per_day"], abs=1e-7)


def test_water_scenarios_limit_services_and_invalidate_nested_cache():
    from faerun.materials import economic_report
    from faerun.world import World

    world = World(settlements=[town(terrain="plains")],
                  commodities=[C("grain", "Grain", "food", 1, "bushel", 60, "farm")])
    before = economic_report("Water Town", world)
    old_key = world.economy_state_key()
    assert next(row for row in before["industries"] if row["id"] == "utilities")["delivered_per_day"] > 0
    world.config.water_overrides["water_town"] = {"source_multiplier": 0}
    assert world.economy_state_key() != old_key
    dry = economic_report("Water Town", world)
    assert dry["water"]["status"] == "essential_gap"
    assert next(row for row in dry["industries"] if row["id"] == "utilities")["delivered_per_day"] == 0
    assert world.settlements["water_town"].population == 2000
    dry_key = world.economy_state_key()
    world.config.water_overrides["water_town"]["source_multiplier"] = 1
    assert world.economy_state_key() != dry_key
    assert economic_report("Water Town", world)["water"]["essential_gap_gallons_per_day"] == 0
