import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys

import pytest

from faerun.hires_survey import estimate_from_sample, waterdeep_hires_report


ROOT = Path(__file__).resolve().parents[1]


def test_report_source_scope_and_honest_coverage():
    report = waterdeep_hires_report()
    assert report["schema_version"] == 2
    assert report["source"]["width_px"] == 3560
    assert report["source"]["height_px"] == 7256
    assert report["source"]["bytes"] == 2111781
    assert report["source"]["sha256"] == "1c98bab4f7346cf70b0533e31f60f9956b339934ed50a0f6f3aef87c5d2d1797"
    assert "Field Ward" in report["source"]["survey_scope"]
    assert "farms" in report["source"]["survey_scope"]
    assert report["coverage"]["machine_processed"]["complete"] is True
    assert report["coverage"]["complete_visual_building_enumeration"] is False
    manual = report["coverage"]["manually_validated"]
    assert manual["complete"] is False
    assert manual["sample_complete"] is True
    assert manual["sample_cells"] == 40
    assert manual["individual_building_identities_verified"] == 0
    assert report["source"]["physical_scale_verified"] is False
    assert report["estimate"]["population_estimate"] is None
    assert report["estimate"]["exact_building_count"] is None


def test_all_candidates_have_unique_pixel_geometry_and_unverified_status():
    report = waterdeep_hires_report()
    features = report["features"]
    assert isinstance(features, list)
    assert len(features) == report["detector"]["candidate_count"] == 4835
    assert len({f["id"] for f in features}) == len(features)
    assert report["coordinate_system"]["not_lon_lat"] is True
    assert report["coordinate_space"] == {
        "width": 3560, "height": 7256, "units": "image_pixels", "origin": "top_left"
    }
    for feature in features:
        assert feature["geometry"]["type"] == "Polygon"
        points = feature["geometry"]["coordinates"][0]
        assert points[0] == points[-1]
        assert len(points) >= 4
        assert all(0 <= x < 3560 and 0 <= y < 7256 for x, y in points)
        assert feature["properties"]["status"] == "automatic_unverified"
        assert feature["properties"]["ward"] is None
        assert feature["properties"]["verified"] is False
        assert feature["properties"]["footprint_sqft"] is None
        digest = hashlib.sha256(json.dumps(points, separators=(",", ":")).encode()).hexdigest()[:14]
        assert feature["id"] == f"wdhr-{digest}"


def test_boundary_geometry_preserves_richer_feature_metadata():
    report = waterdeep_hires_report()
    boundary = report["boundary"]
    assert boundary["type"] == "MultiPolygon"
    assert report["boundary_features"]["type"] == "FeatureCollection"
    assert boundary["coordinates"] == [
        feature["geometry"]["coordinates"] for feature in report["boundary_features"]["features"]
    ]
    assert len(boundary["coordinates"]) == 3
    for polygon in boundary["coordinates"]:
        for ring in polygon:
            assert ring[0] == ring[-1]
            assert all(0 <= x < 3560 and 0 <= y < 7256 for x, y in ring)


def test_area_frame_is_complete_and_seeded_sample_reproduces():
    report = waterdeep_hires_report()
    cells = report["sampling"]["frame"]
    assert len(cells) == report["coverage"]["machine_processed"]["frame_cells"] == 659
    assert len({c["id"] for c in cells}) == len(cells)
    assert sum(c["candidate_count"] for c in cells) == report["detector"]["candidate_count"]
    assert sum(c["boundary_pixels"] for c in cells) == report["coverage"]["machine_processed"]["boundary_pixels"]
    rng = random.Random(report["sampling"]["seed"])
    selected_ids = []
    for stratum in report["sampling"]["strata"]:
        group = sorted((c["id"] for c in cells if c["stratum"] == stratum["id"]))
        assert len(group) == stratum["population_cells"]
        selected = rng.sample(group, stratum["sample_cells"])
        assert selected == stratum["sample_ids"]
        selected_ids.extend(selected)
    assert set(selected_ids) == {c["id"] for c in cells if c.get("sampled")}
    for cell in cells:
        if cell.get("sampled"):
            assert cell["manual"] is not None
            assert cell["manual"]["lower_interpretation"] <= cell["manual"]["preferred_count"] <= cell["manual"]["upper_interpretation"]
            assert 0 < cell["inclusion_probability"] <= 1


def test_persisted_estimator_reproduces_and_separates_uncertainty():
    report = waterdeep_hires_report()
    calculated = estimate_from_sample(report["sampling"]["frame"], report["sampling"]["strata"])
    assert calculated == report["estimate"]
    assert calculated["value"] > report["detector"]["candidate_count"]
    interval = calculated["sampling_interval"]
    assert interval["lower"] < calculated["value"] < interval["upper"]
    assert interval["includes_observer_or_map_omission_error"] is False
    sensitivity = calculated["interpretation_sensitivity"]
    assert sensitivity["lower"] < calculated["value"] < sensitivity["upper"]
    assert sensitivity["is_confidence_interval"] is False
    assert sensitivity["is_rigorous_bound"] is False


def _tiny_frame():
    cells = [
        {"id": str(i), "stratum": "one", "candidate_count": 2,
         "manual": {"lower_interpretation": y, "preferred_count": y, "upper_interpretation": y}}
        for i, y in enumerate((3, 5, 0, 0))
    ]
    strata = [{"id": "one", "population_cells": 4, "sample_cells": 2,
               "candidate_count": 8, "sample_ids": ["0", "1"]}]
    return cells, strata


def test_difference_estimator_and_finite_population_correction():
    cells, strata = _tiny_frame()
    estimate = estimate_from_sample(cells, strata)
    assert estimate["value"] == 16
    assert estimate["standard_error"] == round((4 ** 2 * (1 - 2 / 4) * 2 / 2) ** .5, 3)
    assert estimate["sampling_interval"]["degrees_of_freedom"] == 1


def test_full_stratum_census_has_zero_sampling_variance():
    cells, strata = _tiny_frame()
    strata[0]["sample_ids"] = ["0", "1", "2", "3"]
    strata[0]["sample_cells"] = 4
    estimate = estimate_from_sample(cells, strata)
    assert estimate["value"] == 8
    assert estimate["standard_error"] == 0
    assert estimate["sampling_interval"]["lower"] == estimate["sampling_interval"]["upper"] == 8


@pytest.mark.parametrize("failure", ["missing_review", "duplicate_sample", "invalid_tally", "wrong_total", "wrong_stratum"])
def test_estimator_rejects_invalid_audit(failure):
    cells, strata = _tiny_frame()
    if failure == "missing_review":
        cells[0]["manual"] = None
    elif failure == "duplicate_sample":
        strata[0]["sample_ids"] = ["0", "0"]
    elif failure == "invalid_tally":
        cells[0]["manual"]["preferred_count"] = -1
    elif failure == "wrong_total":
        strata[0]["candidate_count"] = 1
    elif failure == "wrong_stratum":
        cells[0]["stratum"] = "elsewhere"
    with pytest.raises(ValueError):
        estimate_from_sample(cells, strata)


def test_loader_returns_independent_data():
    first = waterdeep_hires_report()
    first["features"].clear()
    assert waterdeep_hires_report()["detector"]["candidate_count"] == 4835
    assert len(waterdeep_hires_report()["features"]) == 4835


def test_loader_works_without_image_analysis_dependencies():
    code = (
        "import sys; from faerun.hires_survey import waterdeep_hires_report; "
        "r=waterdeep_hires_report(); assert r['estimate']['rounded_estimate']>0; "
        "assert not any(x in sys.modules for x in ('cv2','numpy','PIL','pymupdf'))"
    )
    result = subprocess.run([sys.executable, "-S", "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
