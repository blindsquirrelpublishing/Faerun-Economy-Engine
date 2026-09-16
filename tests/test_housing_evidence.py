import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from faerun.housing_evidence import housing_evidence_report, validate_housing_evidence
from tools.survey_waterdeep_housing import digest, geometry_mask, measure, native_polygons, roof


ROOT = Path(__file__).resolve().parents[1]


def rectangle(x, y, x1, y1):
    return {"type": "Polygon", "coordinates": [[[x, y], [x1, y], [x1, y1], [x, y1], [x, y]]]}


def feature(geometry, kind="unclassified_town_roof", evidence="visible_outline"):
    return {"geometry": geometry, "properties": {"kind": kind, "edge_evidence": evidence}}


def ward(name, x, x1):
    return {"name": name, "polygon": rectangle(x, 0, x1, 10)["coordinates"][0]}


def test_clipping_counts_partial_roof_even_when_centroid_outside():
    measured, _, _ = measure([feature(rectangle(-8, 2, 2, 6))], [],
                             [0, 0, 10, 10], rectangle(-20, -20, 20, 20), [])
    assert measured["roof_area_px2"] == 8
    assert measured["area_by_ward_px2"]["unassigned"] == 8


def test_city_clipping_holes_and_overlapping_roof_union():
    first = rectangle(0, 0, 8, 10)
    first["coordinates"].append(rectangle(2, 2, 4, 4)["coordinates"][0])
    measured, _, _ = measure(
        [feature(first), feature(rectangle(6, 0, 10, 10))], [],
        [0, 0, 10, 10], rectangle(0, 0, 9, 10), [],
    )
    assert measured["roof_area_px2"] == 86
    assert measured["traced_area_in_core_before_city_clip_px2"] == 96
    assert measured["removed_outside_city_px2"] == 10
    assert measured["overlapping_trace_area_removed_px2"] == 20
    # A second actual roof within a first polygon's courtyard counts as roof.
    inside, _, _ = measure([feature(first), feature(rectangle(2, 2, 4, 4))], [],
                           [0, 0, 10, 10], rectangle(0, 0, 10, 10), [])
    assert inside["roof_area_px2"] == 80


def test_ward_split_overlap_and_unassigned_never_double_count():
    measured, _, _ = measure([feature(rectangle(0, 0, 10, 10))], [],
                             [0, 0, 10, 10], rectangle(0, 0, 10, 10),
                             [ward("a", 0, 4), ward("b", 3, 8)])
    assert measured["area_by_ward_px2"] == {
        "a": 30, "b": 40, "ambiguous_overlap": 10, "unassigned": 20,
    }
    assert sum(measured["area_by_ward_subpixels"].values()) == measured["roof_subpixel_count"]


def test_conflicting_kind_and_occluded_edges_conserve_union():
    measured, _, _ = measure(
        [feature(rectangle(0, 0, 6, 10)),
         feature(rectangle(4, 0, 10, 10), "cemetery_roof", "partly_label_occluded")],
        [], [0, 0, 10, 10], rectangle(0, 0, 10, 10), [ward("a", 0, 5)],
    )
    assert measured["area_by_kind_px2"] == {
        "unclassified_town_roof": 40, "cemetery_roof": 40,
        "fortification_roof": 0, "ambiguous_class_overlap": 20,
    }
    assert measured["area_by_edge_evidence_px2"] == {"visible_outline": 40, "partly_label_occluded": 60}
    assert sum(sum(row.values()) for row in measured["area_by_ward_and_kind_px2"].values()) == 100


def test_possible_symbols_exclude_roof_union_and_clip_city():
    measured, _, _ = measure([feature(rectangle(0, 0, 6, 10))],
                             [feature(rectangle(4, 0, 12, 10)), feature(rectangle(5, 0, 9, 10))],
                             [0, 0, 10, 10], rectangle(0, 0, 9, 10), [ward("a", 0, 8)])
    assert measured["roof_area_px2"] == 60
    assert measured["possible_additional_roof_area_px2"] == 30
    assert measured["possible_additional_area_by_ward_px2"] == {
        "a": 20, "ambiguous_overlap": 0, "unassigned": 10,
    }


def test_multipolygon_city_hole_and_half_open_adjacent_cells():
    city = rectangle(0, 0, 10, 10)
    city["coordinates"].append(rectangle(2, 2, 4, 4)["coordinates"][0])
    city = {"type": "MultiPolygon", "coordinates": [city["coordinates"],
                                                   rectangle(12, 0, 14, 10)["coordinates"]]}
    pieces = [geometry_mask(city, box).sum() / 9 for box in ([0, 0, 7, 10], [7, 0, 14, 10])]
    assert sum(pieces) == 116


def test_review_coordinate_conversion_and_rejected_resolution():
    converted = native_polygons("test", [160, 320, 320, 480], [roof("72,72 102,72 102,102 72,102")])
    assert converted[0]["geometry"] == rectangle(160, 320, 170, 330)
    with pytest.raises(ValueError):
        geometry_mask(rectangle(0, 0, 10, 10), [0, 0, 10, 10], factor=0)


def test_all_original_samples_strata_boundary_and_source_reconcile():
    report = housing_evidence_report()
    hires = json.loads((ROOT / "faerun" / "data" / "waterdeep_hires_survey.json").read_text())
    selected = {c["id"]: c for c in hires["sampling"]["frame"] if c.get("sampled")}
    assert report["sampling_strata"] == hires["sampling"]["strata"]
    assert report["city_boundary"] == hires["boundary"]
    assert report["source"]["sampling_frame_digest"] == digest(hires["sampling"]["frame"])
    assert set(selected) == {c["id"] for c in report["cells"]}
    for cell in report["cells"]:
        original = selected[cell["id"]]
        for key in ("stratum", "bbox_px", "inclusion_probability"):
            assert cell[key] == original[key]
    image = ROOT / "maps" / "waterdeep-map-hires.jpg"
    assert hashlib.sha256(image.read_bytes()).hexdigest() == report["source"]["sha256"]


def test_zero_cells_and_partial_roofs_are_not_centroid_filtered():
    cells = {c["id"]: c for c in housing_evidence_report()["cells"]}
    assert sum(c["roof_area_px2"] == 0 for c in cells.values()) == 13
    assert cells["x3040-y4960"]["stratum"] == "zero"
    assert cells["x3040-y4960"]["roof_area_px2"] > 0
    assert cells["x3200-y6080"]["area_by_kind_px2"]["fortification_roof"] > 0
    assert cells["x0480-y4800"]["roof_area_px2"] == 0
    assert cells["x0480-y4800"]["possible_additional_roof_area_px2"] > 0
    assert cells["x1280-y4960"]["roof_area_px2"] == 0  # Open piers are not roofs.


def test_reconstruct_every_persisted_cell_from_manual_native_geometry():
    report = housing_evidence_report()
    for cell in report["cells"]:
        calculated, _, _ = measure(cell["manual_polygons"], cell["uncertain_symbol_polygons"],
                                   cell["bbox_px"], report["city_boundary"], report["ward_boundaries"])
        for key, value in calculated.items():
            assert cell[key] == value, (cell["id"], key)
        finer, _, _ = measure(cell["manual_polygons"], cell["uncertain_symbol_polygons"],
                              cell["bbox_px"], report["city_boundary"], report["ward_boundaries"], factor=6)
        assert cell["numerical_resolution_check"]["roof_area_px2"] == finer["roof_area_px2"]


def test_manual_rings_have_no_proper_self_crossings():
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    for cell in housing_evidence_report()["cells"]:
        for trace in cell["manual_polygons"] + cell["uncertain_symbol_polygons"]:
            for ring in trace["geometry"]["coordinates"]:
                edges = list(zip(ring, ring[1:]))
                for i, (a, b) in enumerate(edges):
                    for j, (c, d) in enumerate(edges):
                        if j <= i + 1 or i == 0 and j == len(edges) - 1:
                            continue
                        assert not (cross(a, b, c) * cross(a, b, d) < -1e-10
                                    and cross(c, d, a) * cross(c, d, b) < -1e-10), trace["id"]


def test_external_scale_not_author_certification_or_ground_floor_claim():
    report = housing_evidence_report()
    streets = json.loads((ROOT / "faerun" / "data" / "waterdeep_streets.json").read_text())
    original = streets["source"]["distance_scale"]
    for key in ("coordinate_transform", "source_url", "reference_image_sha256",
                "feet_per_pixel", "square_feet_per_square_pixel"):
        assert report["scale"][key] == original[key]
    assert report["scale"]["map_author_scale_bar_verified"] is False
    assert report["source"]["automatic_segmentation_used_as_area"] is False
    assert report["coverage"]["complete_city_visual_area_enumeration"] is False
    assert "NOT a citywide" in report["totals"]["scope"]
    assert "population_estimate" not in report


@pytest.mark.parametrize("mutation", [
    lambda r: r["cells"].pop(),
    lambda r: r["cells"][0].update(roof_area_px2=float("nan")),
    lambda r: r["cells"][0]["area_by_ward_px2"].update(unassigned=999999),
    lambda r: r["cells"][0]["area_by_ward_and_kind_px2"]["Sea Ward"].update(cemetery_roof=1),
    lambda r: r["cells"][0]["manual_polygons"][0]["properties"].update(verified_ground_floor_footprint=True),
    lambda r: r["sampling_design"].update(samples_replaced=True),
    lambda r: r["totals"].update(roof_area_px2=0),
    lambda r: r["cells"][0]["manual_polygons"][0]["geometry"]["coordinates"][0].pop(),
])
def test_loader_validation_rejects_inconsistent_or_overstated_evidence(mutation):
    report = copy.deepcopy(housing_evidence_report())
    mutation(report)
    with pytest.raises(ValueError):
        validate_housing_evidence(report)


def test_stdlib_only_report_and_independent_return_values():
    subprocess.run([sys.executable, "-S", "-c",
                    "from faerun.housing_evidence import housing_evidence_report; "
                    "assert len(housing_evidence_report()['cells']) == 40"],
                   cwd=ROOT, check=True, capture_output=True, text=True)
    first = housing_evidence_report()
    first["cells"].clear()
    assert len(housing_evidence_report()["cells"]) == 40
