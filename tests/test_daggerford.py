from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from faerun.data.settlements import SETTLEMENTS
from faerun.daggerford import daggerford_analysis_report, validate_daggerford_analysis
from faerun.world import World


def _daggerford():
    return next(row for row in SETTLEMENTS if row.id == "daggerford")


def test_current_runtime_baseline_is_reported_but_never_revised():
    world = World()
    settlement = world.settlements["daggerford"]
    before = deepcopy(settlement)
    report = daggerford_analysis_report(settlement)
    assert settlement == before
    assert report["active_baseline"]["resident_population"] == settlement.population == 900
    assert report["active_baseline"]["mutated"] is False
    assert report["population"]["recommended_resident_population"] is None
    assert report["population"]["confidence_interval"] is None
    assert report["population"]["regional_population_added_to_demand"] == 0
    assert report["population"]["external_visitors_per_day"] is None
    assert report["map"]["dr_year"] is None
    assert report["world_reference_year_dr"] == 1492
    assert all(row["admissible_as_historical_census"] is False
               for row in report["population"]["historical_evidence"])


def test_housing_sensitivity_does_not_calibrate_to_active_population():
    baseline = daggerford_analysis_report(_daggerford())
    override = daggerford_analysis_report(replace(_daggerford(), population=31_415))
    assert override["active_baseline"]["resident_population"] == 31_415
    assert baseline["sensitivity"] == override["sensitivity"]
    assert baseline["roof_groups"] == override["roof_groups"]
    assert _daggerford().population == 900
    sensitivity = baseline["sensitivity"]
    assert sensitivity["eligible_roof_groups"] == 122
    assert sensitivity["institutional_residents"] is None
    assert all(not identity.startswith("P") for identity in sensitivity["eligible_group_ids"])
    for scenario in sensitivity["scenarios"]:
        expected = (122 * scenario["household_size"] * scenario["households_per_residential_group"]
                    * scenario["residential_share"] * scenario["occupied_unit_share"])
        assert scenario["conditional_noninstitutional_component"] == pytest.approx(expected, abs=0.0006)
        assert scenario["town_total"] is None


def test_inventory_distinguishes_roofs_infrastructure_keys_and_unknowns():
    report = daggerford_analysis_report()
    summary = report["inventory_summary"]
    assert summary["reviewed_roof_groups"] == 140
    assert summary["by_sector"] == {
        "commons_and_castle": 5, "upper_west": 17, "lower_west": 29,
        "central": 46, "upper_east": 36, "riverfront": 7,
    }
    assert summary["groups_with_explicit_caveats"] == 59
    assert summary["additional_unresolved_symbols"] == 7
    assert summary["landmark_keys"] == 40
    assert summary["infrastructure_features"] == {"cistern": 8, "gate_complex": 3, "wall_tower": 4}
    assert summary["exact_buildings"] is None
    assert summary["households"] is None
    assert summary["is_complete_building_census"] is False
    assert report["map"]["footprint_area_sqft"] is None
    assert len({row[0] for rows in report["roof_groups"].values() for row in rows}) == 140
    assert report["landmarks"]["5"] == "Cisterns"
    assert sum(item["key"] == 5 for item in report["infrastructure"]) == 8


def test_printed_scale_conflict_and_north_orientation_are_not_hidden():
    report = daggerford_analysis_report()
    scale = report["map"]["scale"]
    assert scale["status"] == "internally_inconsistent_printed_scale"
    assert scale["adopted_feet_per_pixel"] is None
    assert "North points LEFT" in report["map"]["coordinate_system"]
    by_id = {item["id"]: item for item in scale["interpretations"]}
    assert by_id["inner_ticks"]["feet_per_pixel"] == pytest.approx(100 / 114)
    assert by_id["terminal_label"]["feet_per_pixel"] == pytest.approx(150 / 228)
    assert by_id["inner_ticks"]["feet_per_pixel"] / by_id["terminal_label"]["feet_per_pixel"] == pytest.approx(4 / 3)
    assert report["geometry"]["adopted_town_area_sqft"] is None


def test_streets_are_named_visual_traces_not_a_fabricated_complete_network():
    report = daggerford_analysis_report()
    streets = report["streets"]
    assert len(streets) == report["geometry"]["named_streets"] == 11
    assert {s["name"] for s in streets} == {
        "Hill Road", "Wall Street", "Farmers' Road", "Field's Lane", "Duke's Way",
        "High Road", "Horse Way", "Kauth Alley", "Water Street", "River Road", "Tanner Way",
    }
    assert report["geometry"]["network_complete"] is False
    assert all(street["length_px"] > 0 for street in streets)
    assert sum(s["length_px"] for s in streets) == pytest.approx(
        report["geometry"]["named_route_polyline_sum_px"], abs=0.01)
    assert all(s["status"] == "visually_traced_approximate" for s in streets)
    assert "The Shanties" not in {s["name"] for s in streets}
    for street in streets:
        assert street["conditional_length_feet"]["inner_ticks"] == pytest.approx(
            street["length_px"] * 100 / 114, abs=0.01)


def test_source_fingerprints_are_explicit_and_reports_are_fresh():
    first = daggerford_analysis_report()
    assert first["map"]["source_hash_verification"]["status"] == "not_checked"
    data_path = Path(__file__).parents[1] / "faerun" / "data" / "daggerford_analysis.json"
    assert first["analysis_sha256"] == hashlib.sha256(data_path.read_bytes()).hexdigest()
    assert first["map"]["sha256"] == "2376ccdf0086444b9cd1d9c5be0a45810c3ed36cdb6cd3c69e1ee22361fc1f7f"
    first["streets"].clear()
    first["roof_groups"]["upper_west"][0][1] = 0
    assert len(daggerford_analysis_report()["streets"]) == 11
    assert daggerford_analysis_report()["roof_groups"]["upper_west"][0][1] == 143
    assert json.loads(json.dumps(daggerford_analysis_report()))["settlement_id"] == "daggerford"


def test_available_author_preview_matches_audited_bytes():
    preview = Path(__file__).parents[1] / "daggerford_diagnostics" / "daggerford_schley_public_lightbox.jpg"
    if not preview.exists():
        pytest.skip("Public copyrighted preview is optional local evidence, not packaged data")
    report = daggerford_analysis_report(image_path=preview)
    assert report["map"]["source_hash_verification"]["status"] == "verified"
    assert report["map"]["source_hash_verification"]["actual_sha256"] == report["map"]["sha256"]


def test_wrong_source_image_is_not_silently_accepted():
    with pytest.raises(ValueError, match="SHA-256"):
        daggerford_analysis_report(image_path=__file__)


@pytest.mark.parametrize("population", [-1, True, 1.25, float("nan"), float("inf")])
def test_invalid_resident_inputs_fail_without_mutating(population):
    with pytest.raises(ValueError, match="Resident population"):
        daggerford_analysis_report(replace(_daggerford(), population=population))
    assert _daggerford().population == 900


def test_another_settlement_cannot_be_mislabeled_as_daggerford():
    with pytest.raises(ValueError, match="Daggerford settlement"):
        daggerford_analysis_report(replace(_daggerford(), id="waterdeep"))


@pytest.mark.parametrize("change,match", [
    (lambda d: d["roof_groups"]["upper_west"][0].__setitem__(0, "K01"), "unique"),
    (lambda d: d["roof_groups"]["upper_west"][0].__setitem__(1, 800), "boundary"),
    (lambda d: d["roof_groups"]["upper_west"][0].__setitem__(1, float("nan")), "finite"),
    (lambda d: d["roof_groups"]["upper_west"][0].__setitem__(3, 999), "landmark"),
    (lambda d: d["map"].__setitem__("sha256", "not-a-hash"), "SHA-256"),
    (lambda d: d["roof_group_caveats"][0]["ids"].append("invented"), "unknown"),
    (lambda d: d["streets"][0]["points"].append([0, 0]), "boundary"),
    (lambda d: d["sensitivity"]["scenarios"][0].__setitem__("residential_share", 1.1), "shares"),
])
def test_geometry_and_assumption_validation_rejects_corrupt_evidence(change, match):
    data = daggerford_analysis_report()
    change(data)
    with pytest.raises(ValueError, match=match):
        validate_daggerford_analysis(data)
