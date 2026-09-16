from collections import defaultdict
from copy import deepcopy
import math

import pytest

from faerun.data.commodities import COMMODITIES, COMMODITIES_BY_ID
from faerun.data.settlements import SETTLEMENTS
from faerun.models import C, S
from faerun.requirements import DAYS_PER_YEAR, FOOD_COMMODITIES, SECTORS, final_requirements, settlement_profile
from faerun.services import SERVICE_SECTOR_IDS, service_sector_plans


EXPECTED = {
    "health", "religion", "animals", "administration", "knowledge", "commerce",
    "logistics", "communications", "hospitality", "utilities", "civil_security",
    "maintenance", "culture", "professional",
}
FIELDS = {
    "id", "name", "examples", "unit", "workers", "establishments",
    "resident_demand_per_day", "visitor_demand_per_day", "demand_per_day",
    "capacity_per_day", "planned_per_day", "fee_gp_per_unit", "market_service",
    "inputs_per_unit", "visitor_units_per_person_day", "basis",
}


def place(population=1000, **kwargs):
    return S("Service test", "Test", "test", population, 0, 0, **kwargs)


def plans(s, commodities=COMMODITIES, **kwargs):
    return service_sector_plans(
        s, commodities, settlement_profile(s, include_services=False), **kwargs
    )


def indexed(rows):
    return {row["id"]: row for row in rows}


def assert_labor_partition(profile, rows):
    buckets = {row["id"]: row["workers"] for row in profile["establishments"]}
    buckets["unallocated_workers"] = profile["unallocated_workers"]
    allocated = defaultdict(float)
    for row in rows:
        assert row["workers"] == pytest.approx(sum(row["worker_sources"].values()))
        assert row["workers"] == pytest.approx(
            row["reclassified_workers"] + row["newly_allocated_workers"]
        )
        for source, workers in row["worker_sources"].items():
            allocated[source] += workers
    for source, workers in allocated.items():
        assert workers <= buckets[source] + 1e-8
    assert not allocated["arcane"] and not allocated["garrison"]
    assert not allocated["builders"] and not allocated["carpenters"] and not allocated["farms"]
    remaining = sum(buckets.values()) - sum(allocated.values())
    assert remaining >= -1e-8
    assert sum(row["workers"] for row in rows) + remaining == pytest.approx(
        profile["worker_population"]
    )


def test_every_default_has_complete_finite_disjoint_service_plans():
    assert SERVICE_SECTOR_IDS == EXPECTED
    assert EXPECTED <= SECTORS
    assert "visitors" in SECTORS
    assert "visitors" not in SERVICE_SECTOR_IDS
    for s in SETTLEMENTS:
        base = settlement_profile(s, include_services=False)
        rows = service_sector_plans(s, iter(COMMODITIES), base)
        assert len(rows) == 14 and {row["id"] for row in rows} == EXPECTED
        assert_labor_partition(base, rows)
        for row in rows:
            assert FIELDS <= row.keys()
            assert row["examples"] and all(isinstance(x, str) for x in row["examples"])
            assert row["unit"] and "not canon" in row["basis"]
            assert isinstance(row["workers"], float)
            assert isinstance(row["establishments"], int)
            assert isinstance(row["market_service"], bool)
            for key, value in row.items():
                if isinstance(value, (int, float)):
                    assert math.isfinite(value) and value >= 0, (s.id, row["id"], key)
            assert row["demand_per_day"] == pytest.approx(
                row["resident_demand_per_day"] + row["visitor_demand_per_day"]
            )
            assert row["planned_per_day"] == min(row["demand_per_day"], row["capacity_per_day"])
            assert row["capacity_per_day"] == pytest.approx(
                row["workers"] * row["units_per_worker_workday"] * row["workdays_per_year"] / 365
            )
            assert row["inputs_per_unit"].keys() <= COMMODITIES_BY_ID.keys()
            assert all(math.isfinite(x) and x > 0 for x in row["inputs_per_unit"].values())
        by_id = indexed(rows)
        assert by_id["health"]["clerical_healer_workers"] + by_id["religion"]["clergy_workers"] == pytest.approx(
            base["temple_workers"]
        )
        for cid in ("religion", "administration", "utilities", "civil_security"):
            assert not by_id[cid]["market_service"]


def test_zero_population_keeps_fourteen_zero_workload_rows():
    s = place(0, ind="arcane3 temple3 trade3", traits="magocracy temple military")
    rows = plans(s)
    for row in rows:
        for key in ("workers", "establishments", "resident_demand_per_day",
                    "visitor_demand_per_day", "demand_per_day", "capacity_per_day", "planned_per_day"):
            assert row[key] == 0
    assert all(not value for value in final_requirements(s, COMMODITIES).values())


def test_small_poor_places_have_part_time_providers_not_forced_full_hospitals():
    rows = indexed(plans(place(80, wealth=.65)))
    assert 0 < rows["health"]["workers"] < 1
    assert rows["health"]["establishments"] == 1
    assert rows["health"]["capacity_per_day"] < 4
    assert 0 < rows["hospitality"]["lodging_beds"]
    assert not rows["health"]["clerical_healer_workers"]
    assert not rows["religion"]["clergy_workers"]
    assert_labor_partition(settlement_profile(place(80, wealth=.65), include_services=False), list(rows.values()))


def test_visitors_change_workload_not_workers_beds_or_input_intensities():
    s = place(5000, port="Sea", ind="trade3 temple2", traits="temple")
    before = indexed(plans(s))
    after = indexed(plans(s, visitor_days=80, overnight_visitors=30))
    for cid, old in before.items():
        new = after[cid]
        for key in ("workers", "worker_sources", "capacity_per_day", "establishments",
                    "resident_demand_per_day", "fee_gp_per_unit", "inputs_per_unit"):
            assert new[key] == old[key]
        expected = (30 if cid == "hospitality" else 0) + 80 * new["visitor_units_per_person_day"]
        assert new["visitor_demand_per_day"] == expected
        assert new["demand_per_day"] == pytest.approx(old["demand_per_day"] + expected)
        assert new["planned_per_day"] == min(new["demand_per_day"], new["capacity_per_day"])
    assert before["hospitality"]["lodging_beds"] == after["hospitality"]["lodging_beds"] > 0
    assert before["hospitality"]["resident_demand_per_day"] > 0
    assert before["hospitality"]["planned_per_day"] > 0
    assert after["hospitality"]["unit"] == "guest-night equivalent"


@pytest.mark.parametrize("population,wealth", [(0, 1.0), (80, .65), (1000, 1.0), (10000, 1.4)])
def test_hospitality_beds_reserve_resident_work_and_overnight_personal_services(population, wealth):
    s = place(population, wealth=wealth)
    before = indexed(plans(s))["hospitality"]
    capacity = before["capacity_per_day"]
    residents = before["resident_demand_per_day"]
    rate = before["visitor_units_per_person_day"]
    assert before["lodging_beds"] == pytest.approx(
        (capacity - min(residents, capacity)) / (1 + rate)
    )
    assert before["lodging_beds"] <= capacity - min(residents, capacity)
    assert before["resident_demand_per_day"] == pytest.approx(
        population * before["resident_personal_service_units_per_person_day"]
    )
    full = indexed(plans(s, visitor_days=before["lodging_beds"],
                         overnight_visitors=before["lodging_beds"]))["hospitality"]
    if residents <= capacity:
        assert full["demand_per_day"] == pytest.approx(capacity)
    assert full["lodging_beds"] == before["lodging_beds"]
    assert {"barbers", "domestic help", "baths", "laundry"} <= set(before["examples"])


def test_day_visitors_buy_personal_services_without_a_lodging_charge():
    s = place(1000)
    before = indexed(plans(s))["hospitality"]
    after = indexed(plans(s, visitor_days=100))["hospitality"]
    assert after["lodging_demand_per_day"] == 0
    assert after["visitor_demand_per_day"] == after["visitor_personal_service_units_per_day"]
    assert after["visitor_demand_per_day"] == pytest.approx(100 * after["visitor_units_per_person_day"])
    assert after["visitor_demand_per_day"] < 100
    assert after["lodging_beds"] == before["lodging_beds"]
    final = final_requirements(s, COMMODITIES)
    for cid, coefficient in before["inputs_per_unit"].items():
        assert final[cid]["hospitality"] == pytest.approx(before["planned_per_day"] * coefficient)


def test_no_food_or_construction_materials_charged_twice():
    s = place(10000, traits="military temple academic", ind="temple2 trade2")
    service = indexed(plans(s))
    assert not FOOD_COMMODITIES.intersection(service["hospitality"]["inputs_per_unit"])
    assert {"soap", "linen", "charcoal"} <= service["hospitality"]["inputs_per_unit"].keys()
    assert not {"timber", "planks", "granite", "bricks", "nails"}.intersection(
        service["maintenance"]["inputs_per_unit"]
    )
    old = final_requirements(s, COMMODITIES, include_services=False)
    new = final_requirements(s, COMMODITIES)
    for cid in old:
        for sector in ("household", "defense", "arcane", "construction"):
            assert old[cid].get(sector, 0) == new[cid].get(sector, 0), (cid, sector)
    for cid in ("grain", "ox", "plow", "fishing_net", "tools_carpenter"):
        assert old[cid].get("agriculture", 0) == new[cid].get("agriculture", 0)


def test_service_inputs_replace_every_legacy_overlapping_use_exactly():
    s = place(10000, port="Sea", traits="temple academic military", ind="temple3 trade2")
    rows = plans(s)
    demand = final_requirements(s, COMMODITIES)
    for row in rows:
        for cid in COMMODITIES_BY_ID:
            expected = row["planned_per_day"] * row["inputs_per_unit"].get(cid, 0)
            assert demand[cid].get(row["id"], 0) == pytest.approx(expected), (cid, row["id"])
    assert all("civic" not in value for value in demand.values())
    assert demand["holy_water"]["religion"] > 0
    assert "civic" in final_requirements(s, COMMODITIES, include_services=False)["holy_water"]
    assert demand["iron_ore"] == {}
    assert demand["iron_ingot"]["animals"] > 0
    assert demand["iron_ingot"]["maintenance"] > 0
    base = settlement_profile(s, include_services=False)
    assert demand["ship_boat"]["agriculture"] == pytest.approx(base["fishers"] / 4 * .05 / DAYS_PER_YEAR)
    assert demand["rope"]["agriculture"] == pytest.approx(base["fishers"] * 2 * .3 / DAYS_PER_YEAR)


def test_sparse_custom_catalogues_use_only_supplied_ids_and_package_weights():
    s = place(1000, traits="temple", ind="temple2")
    soap = deepcopy(COMMODITIES_BY_ID["soap"])
    soap.weight *= 2
    custom = C("unknown_metal", "Custom metal", "metal", 3, weight=4)
    empty = plans(s, [])
    assert len(empty) == 14 and all(row["inputs_per_unit"] == {} for row in empty)
    sparse = indexed(plans(s, iter([soap, custom])))
    regular = indexed(plans(s))
    for cid in EXPECTED:
        assert sparse[cid]["inputs_per_unit"].keys() <= {"soap", "unknown_metal"}
        assert sparse[cid]["workers"] == regular[cid]["workers"]
        assert sparse[cid]["capacity_per_day"] == regular[cid]["capacity_per_day"]
        if "soap" in regular[cid]["inputs_per_unit"]:
            assert sparse[cid]["inputs_per_unit"]["soap"] == pytest.approx(
                regular[cid]["inputs_per_unit"]["soap"] / 2
            )
    assert final_requirements(s, [custom]) == {"unknown_metal": {}}
    assert final_requirements(s, []) == {}


def test_utility_bundle_has_a_shared_physical_water_waste_and_fire_labor_budget():
    s = place(1000)
    row = indexed(plans(s))["utilities"]
    worker_days = row["workers"] * 240 / 365
    physical_work = row["capacity_per_day"] * (20 / 5000 + 4 / 2500)
    assert physical_work == pytest.approx(worker_days * .9)
    desert = indexed(plans(place(1000, terrain="desert")))["utilities"]
    river = indexed(plans(place(1000, river=True)))["utilities"]
    assert desert["units_per_worker_workday"] < row["units_per_worker_workday"] < river["units_per_worker_workday"]


def test_animal_training_tracks_owned_stocks_and_growth_not_new_warhorse_recipe():
    s = place(10000, traits="military", ind="trade2")
    base = settlement_profile(s, include_services=False)
    row = indexed(service_sector_plans(s, COMMODITIES, base))["animals"]
    expected_stock = base["mounted_troops"] + s.population / 500 * 1.5 + base["resource_assumptions"]["draft_oxen"]
    assert row["owned_training_stock"] == pytest.approx(expected_stock)
    assert row["animal_training_per_year"] == pytest.approx(expected_stock * (.25 + base["annual_growth_rate"]))
    assert not {"grain", "horse_riding", "warhorse", "saddle"}.intersection(row["inputs_per_unit"])
    changed = deepcopy(base)
    changed["defense_equipment"]["warhorse"]["annual_growth_additions"] *= 100
    assert indexed(service_sector_plans(s, COMMODITIES, changed))["animals"] == row
    changed = deepcopy(base)
    changed["annual_growth_rate"] += .01
    growing = indexed(service_sector_plans(s, COMMODITIES, changed))["animals"]
    assert growing["animal_training_per_year"] > row["animal_training_per_year"]
    changed["mounted_troops"] *= 2
    stock = indexed(service_sector_plans(s, COMMODITIES, changed))["animals"]
    assert stock["animal_training_per_year"] > growing["animal_training_per_year"]


def test_extended_profile_preserves_demographics_resources_and_baseline_buckets():
    for s in (place(80), place(1000, traits="temple", ind="temple2"),
              place(15000, traits="magocracy military", ind="arcane3 farm3")):
        original = deepcopy(s)
        base = settlement_profile(s, include_services=False)
        extended = settlement_profile(s)
        assert "service_sectors" not in base and "service_labor" not in base
        assert {key: extended[key] for key in base} == base
        ledger = extended["service_labor"]
        assert ledger["service_workers"] + ledger["other_occupation_workers"] + ledger["remaining_unallocated_workers"] == pytest.approx(
            base["worker_population"]
        )
        assert extended["service_sectors"] == service_sector_plans(s, COMMODITIES, base)
        final_requirements(s, COMMODITIES)
        assert s == original


def test_disabled_model_retains_original_health_civic_carrier_formulas():
    s = place(1000, traits="temple academic", ind="temple2 trade2")
    p = settlement_profile(s, include_services=False)
    rows = final_requirements(s, COMMODITIES, include_services=False)
    assert rows["herbs_healing"]["health"] == pytest.approx(s.population * .002 / COMMODITIES_BY_ID["herbs_healing"].weight)
    assert rows["soap"]["health"] == pytest.approx(s.population * .003 / COMMODITIES_BY_ID["soap"].weight)
    assert rows["linen"]["health"] == pytest.approx(s.population * .0005 / COMMODITIES_BY_ID["linen"].weight)
    assert rows["holy_water"]["civic"] == p["temple_workers"] * .04
    assert rows["paper"]["civic"] == s.population * .003 * 2
    assert rows["ink"]["civic"] == s.population * .0001
    assert rows["cart"]["logistics"] == pytest.approx(s.population / 250 * 1.5 * .12 / DAYS_PER_YEAR)
    assert rows["mule"]["logistics"] == pytest.approx(s.population / 500 * 1.5 * .1 / DAYS_PER_YEAR)
    assert all(set(value) <= {"household", "defense", "arcane", "construction",
                             "health", "logistics", "agriculture", "civic"} for value in rows.values())


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), -1.0])
@pytest.mark.parametrize("field", ["visitor_days", "overnight_visitors"])
def test_rejects_invalid_visitor_workloads(field, value):
    with pytest.raises(ValueError):
        plans(place(), **{field: value})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.0])
@pytest.mark.parametrize("field", ["weight", "base_price", "demand"])
def test_rejects_invalid_catalogue_values(field, value):
    c = C("soap", "Soap", "product", 1)
    setattr(c, field, value)
    with pytest.raises(ValueError):
        plans(place(), [c])
    with pytest.raises(ValueError):
        final_requirements(place(), [c])


def test_rejects_zero_weights_duplicate_ids_and_bad_labor_ledgers():
    with pytest.raises(ValueError):
        plans(place(), [C("soap", "Soap", "product", 1, weight=0)])
    duplicate = C("soap", "Soap", "product", 1)
    with pytest.raises(ValueError):
        final_requirements(place(), [duplicate, duplicate])
    s = place()
    base = settlement_profile(s, include_services=False)
    broken = deepcopy(base)
    broken["unallocated_workers"] += 1
    with pytest.raises(ValueError):
        service_sector_plans(s, COMMODITIES, broken)
    broken = deepcopy(base)
    broken["health_workers"] += 1
    with pytest.raises(ValueError):
        service_sector_plans(s, COMMODITIES, broken)
    broken = deepcopy(base)
    del broken["resource_assumptions"]["draft_oxen"]
    with pytest.raises(KeyError):
        service_sector_plans(s, COMMODITIES, broken)


@pytest.mark.parametrize("field,value", [
    ("population", -1), ("population", 1.5), ("wealth", float("nan")),
    ("security", float("inf")), ("wealth", -1), ("population", float("inf")),
])
def test_enabled_profile_rejects_invalid_settlement_numbers(field, value):
    s = place()
    setattr(s, field, value)
    with pytest.raises(ValueError):
        settlement_profile(s)
    with pytest.raises(ValueError):
        final_requirements(s, COMMODITIES)
