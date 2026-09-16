from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

import faerun.streets as runtime
from faerun.streets import _validate_report, waterdeep_streets_report


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "survey_waterdeep_streets", ROOT / "tools" / "survey_waterdeep_streets.py"
)
SURVEY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SURVEY)


@pytest.fixture(scope="module")
def report():
    return waterdeep_streets_report()


def test_original_pixel_contract_and_real_persistent_paths(report):
    assert report["coordinate_space"] == {
        "units": "image_pixels", "width": 3560, "height": 7256, "origin": "top_left",
    }
    assert report["source"]["sha256"] == SURVEY.SOURCE_HASH
    assert len(report["features"]) > 1000
    _validate_report(report)
    assert all(f["geometry"]["type"] in ("LineString", "MultiLineString")
               for f in report["features"])
    assert any(len(f["geometry"]["coordinates"]) > 10 for f in report["features"])


def test_whole_city_attempt_is_not_claimed_complete(report):
    coverage = report["coverage"]
    assert coverage["full_raster_processed"]
    assert not coverage["complete"]
    assert not coverage["geometric_complete"]
    assert not coverage["naming_complete"]
    assert coverage["geometry_coverage_fraction"] is None
    assert coverage["naming_coverage_fraction"] is None
    areas = {area["name"]: area for area in coverage["areas"]}
    assert set(areas) == {
        "Sea Ward", "North Ward", "Castle Ward", "Trades Ward", "Southern Ward",
        "Dock Ward", "Field Ward", "City of the Dead", "Stormhaven Island",
        "Deepwater Isle",
    }
    assert all(area["processed"] and area["candidate_segments"] > 0
               for area in areas.values())
    assert (sum(a["candidate_segments"] for a in areas.values())
            + coverage["unassigned_area_feature_count"]) == coverage["candidate_segment_count"]


def test_names_remain_distinct_from_unverified_geometry(report):
    named = [f for f in report["features"] if f["properties"]["name"]]
    unknown = [f for f in report["features"] if f["properties"]["name"] is None]
    assert len(named) >= 30
    assert len(unknown) > len(named)
    names = {f["properties"]["name"] for f in named}
    assert {"Swords Street", "Waterdeep Way", "Fillet Lane"} <= names
    assert len(named) == report["coverage"]["named_feature_count"]
    assert len(names) == report["coverage"]["unique_matched_names"]
    candidates = [f for f in named if f["properties"]["status"] == "machine_traced_candidate"]
    assert all(f["properties"]["name_status"] == "source_label_matched_candidate"
               and f["properties"]["label_distance_px"] <= 24 for f in candidates)
    assert all(f["properties"]["name_status"] == "unknown" for f in unknown)
    assert all(observation["status"] == "unverified_ocr_observation"
               for observation in report["label_observations"])


def test_report_is_json_serializable_and_caller_mutation_is_isolated(report):
    assert json.loads(json.dumps(report)) == report
    first = waterdeep_streets_report()
    first["features"][0]["properties"]["name"] = "Not a source street"
    first["coverage"]["complete"] = True
    second = waterdeep_streets_report()
    assert second["features"][0]["properties"]["name"] != "Not a source street"
    assert not second["coverage"]["complete"]


def test_stdlib_only_runtime_without_site_packages():
    result = subprocess.run(
        [sys.executable, "-S", "-c",
         "from faerun.streets import waterdeep_streets_report; "
         "r=waterdeep_streets_report(); assert r['features']; "
         "import sys; assert not {'numpy','cv2','PIL'} & sys.modules.keys()"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("mutation", [
    lambda r: r["coordinate_space"].update(units="longitude_latitude"),
    lambda r: r["features"][0]["geometry"].update(type="Point"),
    lambda r: r["features"][0]["geometry"].update(coordinates=[[0, 0], [3560, 20]]),
    lambda r: r["features"][0]["geometry"].update(coordinates=[[0, 0], [True, 20]]),
    lambda r: r["features"][0]["geometry"].update(coordinates=[[0, 0], [float("nan"), 20]]),
    lambda r: r["features"][0]["geometry"].update(coordinates=[[0, 0], [0, 0]]),
    lambda r: r["features"][0]["properties"].update(name=""),
    lambda r: r["features"][1].update(id=r["features"][0]["id"]),
    lambda r: r["coverage"].update(feature_count=0),
])
def test_invalid_coordinates_names_and_counts_rejected(report, mutation):
    modified = deepcopy(report)
    mutation(modified)
    with pytest.raises(ValueError):
        _validate_report(modified)


def test_bezier_ward_masks_are_flattened_not_misread_as_vertices():
    points = SURVEY.parse_svg_path("M 0,0 L 10,0 C 10,10 20,10 20,0 Z")
    assert points[0] == [0, 0]
    assert points[-1] == [20, 0]
    assert len(points) == 10
    assert [15, 7.5] in points
    with pytest.raises(ValueError):
        SURVEY.parse_svg_path("M 0")


def test_name_matching_does_not_join_roads_or_label_perpendicular_crossing():
    features = [
        {"id": "parallel", "geometry": {"coordinates": [[80, 100], [140, 100]]},
         "properties": {"name": None}},
        {"id": "crossing", "geometry": {"coordinates": [[110, 50], [110, 150]]},
         "properties": {"name": None}},
        {"id": "far", "geometry": {"coordinates": [[800, 100], [900, 100]]},
         "properties": {"name": None}},
    ]
    labels = [{"text": "Swords Street", "rotation_degrees": 0,
               "words": [{"x": 80, "y": 94, "width": 60, "height": 12}]}]
    original_geometry = deepcopy([f["geometry"] for f in features])
    SURVEY.match_names(features, labels)
    assert features[0]["properties"]["name"] == "Swords Street"
    assert features[1]["properties"]["name"] is None
    assert features[2]["properties"]["name"] is None
    assert [f["geometry"] for f in features] == original_geometry


def test_unknown_ocr_never_becomes_a_street_name():
    features = [
        {"id": "candidate", "geometry": {"coordinates": [[80, 100], [140, 100]]},
         "properties": {"name": None}},
    ]
    labels = [{"text": "Unreadabl3 Str33t", "rotation_degrees": 0,
               "words": [{"x": 80, "y": 94, "width": 60, "height": 12}]}]
    SURVEY.match_names(features, labels)
    assert features[0]["properties"]["name"] is None


def test_skeleton_crossing_splits_into_four_real_branches():
    np = pytest.importorskip("numpy")
    pixels = np.zeros((9, 9), dtype=bool)
    pixels[4, 1:8] = True
    pixels[1:8, 4] = True
    paths = SURVEY.trace_graph(pixels)
    assert len(paths) == 4
    assert all((4, 4) in (path[0], path[-1]) for path in paths)
    assert all(pixels[y, x] for path in paths for x, y in path)


def test_skeleton_bend_is_not_shortcut_by_a_guessed_diagonal():
    np = pytest.importorskip("numpy")
    pixels = np.zeros((9, 9), dtype=bool)
    pixels[2, 1:7] = True
    pixels[2:8, 6] = True
    paths = SURVEY.trace_graph(pixels)
    assert len(paths) == 1
    assert (6, 2) in paths[0]
    assert SURVEY.length(paths[0]) == 10
    assert len(paths[0]) == 11


def test_physical_scale_is_sourced_and_registered_not_a_display_assumption(report):
    scale = report["source"]["distance_scale"]
    assert scale["status"] == "external_calibration_with_verified_raster_registration"
    assert scale["source_url"] == SURVEY.BOUNDARY_URL
    assert scale["feet_per_pixel"] == pytest.approx(100 / 31)
    assert scale["square_feet_per_square_pixel"] == pytest.approx(10000 / 961)
    assert scale["native_length_formula"] == "length_ft = length_px * 1000 / 310"
    assert scale["native_area_formula"] == "area_sqft = area_px2 * (1000 / 310) ** 2"
    assert "do not validate" in scale["geometry_validation_caveat"]
    assert scale["local_image_sha256"] == report["source"]["sha256"]
    assert scale["reference_image_dimensions"] == [3560, 7256]
    assert not scale["byte_identical"]
    assert not scale["display_scale_used_as_evidence"]
    assert not scale["map_author_scale_bar_verified"]
    assert not scale["applied"]
    transform = scale["coordinate_transform"]
    assert transform["verified"]
    assert transform["matrix"] == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert len(transform["crop_comparisons"]) == 8
    for crop in transform["crop_comparisons"]:
        assert crop["grayscale_correlation"] >= .90
        assert crop["phase_response"] >= .85
        assert max(abs(value) for value in crop["phase_shift_px"]) <= .25


def test_reviewed_routes_are_separate_from_raw_segments_and_withheld_names(report):
    coverage = report["coverage"]
    reviewed = [f for f in report["features"]
                if f["properties"]["status"] == "assistant_reviewed_route"]
    assert coverage["candidate_segment_count"] == 7417
    assert coverage["candidate_named_segment_count"] == 66
    assert len(reviewed) == coverage["reviewed_route_count"] >= 175
    assert coverage["feature_count"] == 7417 + len(reviewed)
    assert coverage["reviewed_named_street_count"] == len(reviewed)
    assert coverage["proposed_route_count"] == 0
    assert coverage["visually_transcribed_name_count"] >= 267
    assert coverage["withheld_route_count"] > 0
    assert coverage["visually_transcribed_name_count"] == (
        len(reviewed) + coverage["withheld_route_count"]
    )
    survey = report["reviewed_route_survey"]
    assert len(survey["name_inventory"]) == coverage["visually_transcribed_name_count"]
    assert len(survey["source_crop_catalog"]) >= 20
    assert not survey["independent_human_certification"]
    for feature in reviewed:
        props = feature["properties"]
        assert feature["id"].startswith("wd-route-")
        assert props["kind"] == "named_street_route"
        assert props["name_status"] == "visually_transcribed_source_label"
        assert props["source_review"]["overlay_reviewed"]
        assert len(props["source_review"]["approved_geometry_sha256"]) == 64
        assert props["source_review"]["manual_guide_px"]
    areas = {a["name"]: a for a in coverage["areas"]}
    assert all(a["reviewed_routes"] > 0 for name, a in areas.items()
               if name not in {"Deepwater Isle", "Stormhaven Island"})
    assert areas["Field Ward"]["reviewed_routes"] >= 10
    assert all(areas[name]["reviewed_routes"] == 0
               for name in ("Deepwater Isle", "Stormhaven Island"))


@pytest.mark.parametrize("name,minimum_length", [
    ("The High Road", 5000),
    ("The Way of the Dragon", 1700),
    ("Swords Street", 1300),
    ("The Street of the Sword", 1100),
    ("Waterdeep Way", 850),
    ("The Fieldway", 1300),
])
def test_named_routes_span_corridors_not_nearest_tiny_fragments(report, name, minimum_length):
    route = next(f for f in report["features"]
                 if f["properties"]["name"] == name
                 and f["properties"]["status"] == "assistant_reviewed_route")
    assert SURVEY.length(route["geometry"]["coordinates"]) >= minimum_length
    assert route["properties"]["length_px"] == pytest.approx(
        SURVEY.length(route["geometry"]["coordinates"]), abs=.01)


@pytest.mark.parametrize("mutation", [
    lambda f: f["properties"].update(status="manual_corridor_proposal"),
    lambda f: f["properties"].update(name=None),
    lambda f: f["properties"]["source_review"].update(overlay_reviewed=False),
    lambda f: f["properties"]["source_review"].update(source_sha256="changed"),
    lambda f: f["geometry"]["coordinates"][0].__setitem__(0, 20),
])
def test_unapproved_or_changed_reviewed_geometry_is_rejected(report, mutation):
    modified = deepcopy(report)
    route = next(f for f in modified["features"]
                 if f["properties"]["status"] == "assistant_reviewed_route")
    mutation(route)
    with pytest.raises(ValueError):
        _validate_report(modified)


def test_refresh_preserves_approved_and_raw_geometry_and_never_automatically_fits(report, monkeypatch):
    monkeypatch.setattr(SURVEY, "pavement_refiner",
                        lambda: pytest.fail("Metadata refresh must not re-fit approved geometry"))
    first = SURVEY.apply_reviewed_routes(deepcopy(report))
    second = SURVEY.apply_reviewed_routes(deepcopy(first))
    assert first == second
    assert first["features"] == report["features"]
    assert first["source"]["distance_scale"] == report["source"]["distance_scale"]
    _validate_report(first)


def test_new_manual_guides_are_withheld_without_explicit_overlay_approval(report, monkeypatch):
    guides = deepcopy(SURVEY.MANUAL_ROUTES)
    guides["Field Ward"]["New unapproved test guide"] = "1200,400 1250,425"
    monkeypatch.setattr(SURVEY, "MANUAL_ROUTES", guides)
    updated = SURVEY.apply_reviewed_routes(deepcopy(report))
    assert updated["features"] == report["features"]
    assert any(item["name"] == "New unapproved test guide"
               for item in updated["reviewed_route_survey"]["withheld_routes"])
    _validate_report(updated)


def test_loader_observes_replaced_data_without_stale_cache(report, tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    path = tmp_path / "data" / "waterdeep_streets.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    monkeypatch.setattr(runtime, "files", lambda package: tmp_path)
    assert "refresh_marker" not in waterdeep_streets_report()["coverage"]
    updated = deepcopy(report)
    updated["coverage"]["refresh_marker"] = "new serialized revision"
    path.write_text(json.dumps(updated), encoding="utf-8")
    assert waterdeep_streets_report()["coverage"]["refresh_marker"] == "new serialized revision"


def test_atomic_publisher_validates_before_replacing_data(report, tmp_path, monkeypatch):
    output = tmp_path / "streets.json"
    output.write_text("previous data", encoding="utf-8")
    monkeypatch.setattr(SURVEY, "OUTPUT", output)
    invalid = deepcopy(report)
    invalid["coverage"]["feature_count"] = 0
    with pytest.raises(ValueError):
        SURVEY.write_report(invalid)
    assert output.read_text(encoding="utf-8") == "previous data"
    SURVEY.write_report(report)
    assert json.loads(output.read_text(encoding="utf-8")) == report
    assert not list(tmp_path.glob("*.tmp"))


def test_failed_atomic_replace_keeps_previous_file_and_cleans_temporary(report, tmp_path, monkeypatch):
    output = tmp_path / "streets.json"
    output.write_text("previous data", encoding="utf-8")
    monkeypatch.setattr(SURVEY, "OUTPUT", output)

    def fail_replace(source, destination):
        raise PermissionError("simulated sharing violation")

    monkeypatch.setattr(SURVEY.os, "replace", fail_replace)
    with pytest.raises(PermissionError, match="sharing violation"):
        SURVEY.write_report(report)
    assert output.read_text(encoding="utf-8") == "previous data"
    assert not list(tmp_path.glob("*.tmp"))
