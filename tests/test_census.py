from dataclasses import replace
from importlib.resources import files
import json

import pytest

from faerun.census import (
    BuildingFootprint,
    CLASS_SHARES,
    HOUSING_SCENARIOS,
    estimate_building,
    housing_census,
    waterdeep_housing_report,
)


def footprint(**changes):
    return replace(BuildingFootprint("roof-1", "castle", 1000, True, "C"), **changes)


def report(buildings, **changes):
    kwargs = {"coverage_complete": True, "overlaps_resolved": True, "class_a_complete": True}
    kwargs.update(changes)
    return housing_census(buildings, **kwargs)


def test_class_probabilities_are_complete_except_explicitly_unresolved_south():
    assert "south" not in CLASS_SHARES
    for shares in CLASS_SHARES.values():
        assert sum(shares.values()) == pytest.approx(1)
        assert all(0 <= value <= 1 for value in shares.values())


def test_central_class_c_calculation_can_be_reproduced_from_source_rolls():
    # 1000 sqft * .75 / 500 = 1.5 unit-equivalents per residential floor.
    # Residential floor expectation: .25 rooming + .15 shops + .15 offices + .5 apartments.
    # Add .05 proprietor households; Castle condition share .75, occupancy .95.
    result = estimate_building(footprint(), HOUSING_SCENARIOS[1])
    homes = (1.5 * (.25 + .15 + .15 + .5) + .05) * .75 * .95
    assert result["household_equivalents"] == pytest.approx(homes)
    assert result["estimate"] == pytest.approx(homes * 5)
    assert result["institutional_residents"] == 0


def test_ward_mix_matches_explicit_classes_and_condition_varies_by_ward():
    central = HOUSING_SCENARIOS[1]
    actual = estimate_building(footprint(building_class=None), central)["estimate"]
    expected = sum(
        share * estimate_building(footprint(building_class=key), central)["estimate"]
        for key, share in CLASS_SHARES["castle"].items()
    )
    assert actual == pytest.approx(expected)
    north = estimate_building(footprint(ward="north"), central)["estimate"]
    dock = estimate_building(footprint(ward="dock"), central)["estimate"]
    assert north / dock == pytest.approx(7 / 5)


def test_institutional_residents_are_separate_and_not_counted_as_households():
    institution = footprint(building_class="A", footprint_sqft=None, institutional_residents=37)
    for scenario in HOUSING_SCENARIOS:
        result = estimate_building(institution, scenario)
        assert result["estimate"] == 37
        assert result["household_equivalents"] == 0
        assert result["institutional_residents"] == 37


def test_cemetery_structures_do_not_inherit_random_apartment_occupancy():
    building = footprint(ward="city_of_the_dead", building_class=None)
    assert estimate_building(building, HOUSING_SCENARIOS[1])["estimate"] is None
    uninhabited = replace(building, building_class="A", institutional_residents=0)
    assert estimate_building(uninhabited, HOUSING_SCENARIOS[1])["estimate"] == 0
    with pytest.raises(ValueError, match="City of the Dead"):
        footprint(ward="city_of_the_dead", building_class="C")


@pytest.mark.parametrize("changes,reason", [
    ({"verified": False}, "Unverified"),
    ({"ward": None}, "Ward not"),
    ({"footprint_sqft": None}, "scale"),
    ({"building_class": "A"}, "Institutional"),
    ({"ward": "south", "building_class": None}, "rolls 3-4"),
])
def test_unknown_inputs_block_estimation_instead_of_becoming_zero(changes, reason):
    building = footprint(**changes)
    estimate = estimate_building(building, HOUSING_SCENARIOS[1])
    assert estimate["estimate"] is None
    assert reason in estimate["reason"]
    census = report([building])
    assert not census["can_replace_population"]
    assert census["city_residents"] is None
    assert census["covered_residents"] is None
    assert census["unresolved_counts"]


def test_explicit_southern_class_does_not_use_ambiguous_probability_table():
    assert estimate_building(footprint(ward="south", building_class="C"), HOUSING_SCENARIOS[1])[
        "estimate"
    ] > 0


def test_partial_survey_reports_only_covered_subtotal():
    census = report(
        [footprint(), footprint(id="roof-2", ward="north", verified=False)],
        coverage_complete=False, overlaps_resolved=False, class_a_complete=False,
        subset_deduplicated=True,
    )
    assert census["status"] == "incomplete_survey"
    assert census["city_residents"] is None
    assert census["confidence_interval"] is None
    assert census["covered_residents"]["central"] > 0
    assert census["inventory_records"] == 2
    assert census["verified_buildings"] == census["estimable_buildings"] == 1
    assert len(census["blockers"]) == 4
    assert census["unresolved_counts"] == {"Unverified roof candidate": 1}
    assert next(ward for ward in census["wards"] if ward["id"] == "north")["covered_residents"] is None


def test_complete_scenarios_reconcile_to_ward_and_building_totals():
    buildings = [footprint(), footprint(id="roof-2", ward="north", building_class="B")]
    census = report(buildings)
    assert census["can_replace_population"]
    assert census["status"] == "modeled_estimate"
    for scenario in HOUSING_SCENARIOS:
        total = sum(estimate_building(building, scenario)["estimate"] for building in buildings)
        assert census["covered_residents"][scenario.name] == pytest.approx(total)
        assert census["city_residents"][scenario.name] == round(total)
        assert sum((ward["covered_residents"] or {}).get(scenario.name, 0)
                   for ward in census["wards"]) == pytest.approx(total)
    low, central, high = (census["covered_residents"][name] for name in ("low", "central", "high"))
    assert low < central < high


def test_population_is_not_reverse_calibrated_to_the_live_baseline():
    small = report([footprint()])
    large = report([footprint(footprint_sqft=2000)])
    assert small["covered_residents"]["central"] < large["covered_residents"]["central"] < 100
    assert "target_population" not in small
    assert "resident_population" not in small


def test_empty_or_duplicate_inventory_cannot_produce_a_census():
    empty = report([])
    assert empty["city_residents"] is None
    assert empty["covered_residents"] is None
    assert "No measured building inventory" in empty["blockers"]
    with pytest.raises(ValueError, match="Duplicate"):
        report([footprint(), footprint()])


def test_unresolved_subset_overlaps_withhold_ward_and_covered_subtotals():
    census = report([footprint()], overlaps_resolved=False)
    assert census["covered_residents"] is None
    assert all(ward["covered_residents"] is None for ward in census["wards"])
    assert census["city_residents"] is None
    with pytest.raises(ValueError, match="deduplication"):
        report([footprint()], subset_deduplicated=False)


@pytest.mark.parametrize("changes", [
    {"id": ""}, {"ward": "unknown"}, {"building_class": "Z"},
    {"footprint_sqft": 0}, {"footprint_sqft": -1}, {"footprint_sqft": float("nan")},
    {"footprint_sqft": True}, {"building_class": "C", "institutional_residents": 3},
    {"building_class": "A", "institutional_residents": -1},
    {"building_class": "A", "institutional_residents": True},
])
def test_invalid_footprints_are_rejected(changes):
    with pytest.raises(ValueError):
        footprint(**changes)


@pytest.mark.parametrize("changes", [
    {"household_size": 0}, {"apartment_sqft": -1}, {"household_size": True},
    {"apartment_sqft": float("inf")}, {"usable_floor_share": 1.1},
    {"occupied_unit_share": -.1}, {"rooming_permanent_share": float("nan")},
])
def test_invalid_occupancy_assumptions_are_rejected(changes):
    with pytest.raises(ValueError):
        replace(HOUSING_SCENARIOS[1], **changes)


def test_real_inventory_is_partial_and_cannot_replace_the_population():
    census = waterdeep_housing_report()
    assert census["inventory_records"] == census["verified_buildings"] == 156
    assert census["estimable_buildings"] == 0
    assert census["city_residents"] is census["covered_residents"] is None
    assert not census["can_replace_population"]
    assert census["status"] == "incomplete_survey"
    assert len(census["building_inventory"]) == 156
    assert len(census["unresolved_roof_groups"]) == 5
    assert census["survey"]["validation"]["detector_status"] == "rejected_for_inventory_and_extrapolation"
    assert census["survey"]["source"]["physical_scale_verified"] is False
    assert len(census["survey"]["patches"]) == 7
    assert census["input_readiness"] == {
        "verified_with_ward": 26, "verified_with_physical_area": 0,
        "verified_with_ward_and_physical_area": 0,
        "verified_class_a_occupancy_unknown": 26, "counts_overlap": True,
    }
    assert census["unresolved_counts"] == {"Ward not established": 130, "Institutional occupancy unknown": 26}
    cemetery = next(w for w in census["wards"] if w["id"] == "city_of_the_dead")
    assert cemetery["inventory_records"] == 26
    assert cemetery["covered_residents"] is None
    assert census["survey"]["ward_evidence"]["city-dead-enclosure"]["ward"] == "city_of_the_dead"
    assert any("1357" in reason and "1492" in reason for reason in census["blockers"])
    with pytest.raises(KeyError, match="No building census"):
        waterdeep_housing_report("daggerford")


@pytest.mark.parametrize("tamper", ["schema", "counts", "scale", "status", "duplicates", "ward", "source", "ward_evidence", "ward_count", "citations"])
def test_corrupt_inventory_is_rejected_in_the_application(tmp_path, monkeypatch, tamper):
    from faerun import census

    raw = json.loads(files("faerun").joinpath(
        "data", "waterdeep_buildings.json").read_text(encoding="utf-8"))
    if tamper == "schema":
        raw["schema_version"] = 99
    elif tamper == "counts":
        raw["coverage"]["verified_building_count"] = 36
    elif tamper == "scale":
        raw["buildings"][0]["footprint_sqft"] = 2000
    elif tamper == "status":
        raw["buildings"][0]["status"] = "fictional"
        raw["coverage"]["verified_building_count"] -= 1
    elif tamper == "ward":
        raw["buildings"][0]["ward"] = "castle"
    elif tamper == "source":
        raw["buildings"][0]["source"]["pdf_page"] = 91
    elif tamper == "ward_evidence":
        raw["ward_evidence"] = {}
    elif tamper == "ward_count":
        raw["coverage"]["ward_assigned_building_count"] += 1
    elif tamper == "citations":
        raw["ward_evidence"]["city-dead-enclosure"]["citations"] = []
    else:
        raw["buildings"][1]["id"] = raw["buildings"][0]["id"]
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "waterdeep_buildings.json").write_text(json.dumps(raw), encoding="utf-8")
    monkeypatch.setattr(census, "files", lambda package: tmp_path)
    with pytest.raises(ValueError):
        census.waterdeep_housing_report()


def test_api_and_mcp_census_are_read_only_and_agree(monkeypatch):
    from faerun import web
    from faerun.calendar import HarptosDate
    from faerun.data.settlements import SETTLEMENTS
    from faerun.world import World

    waterdeep = replace(next(s for s in SETTLEMENTS if s.id == "waterdeep"))
    world = World(settlements=[waterdeep], date=HarptosDate(1492, 9, 16))
    revision = world.revision
    result = web.GET_ROUTES["/api/census"](world, {"settlement": ["Waterdeep"]})
    assert result["date"] == "16 Eleint 1492 DR"
    assert result["active_resident_population"] == waterdeep.population == 200_000
    assert result["active_population_unchanged"]
    assert result["city_residents"] is None
    assert world.revision == revision
    pytest.importorskip("mcp")
    from faerun import mcp_server

    monkeypatch.setattr(mcp_server, "world", lambda: world)
    assert mcp_server.get_housing_census("Waterdeep") == result
    assert "error" in mcp_server.get_housing_census("Unknown")
