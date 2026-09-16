"""Dependency-free, separate approximate map roof-area evidence.

No building identities, habitable floor area, occupancy assumptions or population
estimates are inferred here. Image-processing dependencies are rebuild-only.
"""

from __future__ import annotations

from importlib.resources import files
import json
import math


_SPACE = {"width": 3560, "height": 7256, "units": "image_pixels", "origin": "top_left"}
_IMAGE_SHA = "1c98bab4f7346cf70b0533e31f60f9956b339934ed50a0f6f3aef87c5d2d1797"
_STRATA = {"zero": 78, "sparse": 92, "low": 208, "medium": 237, "high": 44}
_WARDS = {
    "Field Ward", "Castle Ward", "Dock Ward", "North Ward", "Sea Ward",
    "Southern Ward", "Trades Ward", "City of the Dead", "ambiguous_overlap", "unassigned",
}
_KINDS = {
    "unclassified_town_roof", "cemetery_roof", "fortification_roof", "ambiguous_class_overlap",
}
_EDGES = {"visible_outline", "partly_label_occluded"}


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError("Areas and coordinates must be finite nonnegative numbers")
    return value


def _equal(actual, expected):
    if not math.isclose(_number(actual), _number(expected), rel_tol=1e-12, abs_tol=1e-7):
        raise ValueError("Housing evidence area conservation failed")


def _partition(values, keys, total):
    if set(values) != keys:
        raise ValueError("Unexpected area allocation categories")
    _equal(sum(_number(value) for value in values.values()), total)


def _geometry(geometry):
    if geometry["type"] not in ("Polygon", "MultiPolygon"):
        raise ValueError("Housing evidence requires native-pixel polygon geometry")
    polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    if not polygons:
        raise ValueError("Empty polygon geometry")
    for polygon in polygons:
        if not polygon:
            raise ValueError("Polygon needs an exterior ring")
        for ring in polygon:
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError("Polygon rings must be closed with at least three vertices")
            for point in ring:
                if len(point) != 2 or _number(point[0]) > 3560 or _number(point[1]) > 7256:
                    raise ValueError("Polygon coordinate outside source image")


def validate_housing_evidence(report: dict) -> None:
    """Validate persisted metadata/conservation; geometric integration is tested offline."""
    if report["schema_version"] != 1 or report["coordinate_space"] != _SPACE:
        raise ValueError("Unsupported housing evidence schema or coordinate space")
    if report["source"]["sha256"] != _IMAGE_SHA or report["source"]["automatic_segmentation_used_as_area"] is not False:
        raise ValueError("Housing evidence must use the original image and separate visual traces")
    scale = report["scale"]
    if (scale["local_image_sha256"] != _IMAGE_SHA
            or scale["coordinate_transform"]["verified"] is not True
            or scale["map_author_scale_bar_verified"] is not False):
        raise ValueError("Expected externally calibrated, registered, non-author-certified scale")
    _equal(scale["feet_per_pixel"], 1000 / 310)
    _equal(scale["square_feet_per_square_pixel"], (1000 / 310) ** 2)
    if scale["coordinate_transform"]["matrix"] != [[1, 0, 0], [0, 1, 0], [0, 0, 1]]:
        raise ValueError("Expected verified identity registration")
    if len(scale["coordinate_transform"]["crop_comparisons"]) != 8:
        raise ValueError("Missing scale registration comparisons")
    _geometry(report["city_boundary"])
    if {ward["name"] for ward in report["ward_boundaries"]} != _WARDS - {"ambiguous_overlap", "unassigned"}:
        raise ValueError("Expected eight approximate external mainland wards")
    if len(report["ward_boundaries"]) != 8:
        raise ValueError("Duplicate ward boundary")
    for ward in report["ward_boundaries"]:
        points = ward["polygon"]
        closed = points + [points[0]] if points and points[0] != points[-1] else points
        _geometry({"type": "Polygon", "coordinates": [closed]})
    design = report["sampling_design"]
    if (design["seed"] != 20260916 or design["frame_cells"] != 659
            or design["reviewed_cells"] != 40 or design["samples_replaced"] is not False
            or design["all_selected_cells_reviewed"] is not True):
        raise ValueError("The original forty-cell probability design must be retained")
    strata = report["sampling_strata"]
    if len(strata) != 5 or {s["id"]: s["population_cells"] for s in strata} != _STRATA:
        raise ValueError("Unexpected sampling strata")
    selected = {}
    for stratum in strata:
        if stratum["sample_cells"] != 8 or len(stratum["sample_ids"]) != 8:
            raise ValueError("Expected eight original samples per stratum")
        for key in stratum["sample_ids"]:
            if key in selected:
                raise ValueError("Duplicate selected sample")
            selected[key] = stratum["id"]
    cells = report["cells"]
    if len(cells) != 40 or {c["id"] for c in cells} != set(selected):
        raise ValueError("Missing, duplicate or substituted sample review")
    coverage = report["coverage"]
    if (coverage["selected_cells"] != 40 or coverage["visually_reviewed_cells"] != 40
            or coverage["area_overlay_reviewed_cells"] != 40
            or coverage["full_sample_review_complete"] is not True
            or coverage["complete_city_visual_area_enumeration"] is not False
            or coverage["authoritative_footprint_validation"] is not False):
        raise ValueError("Unsupported coverage claims")
    factor = report["clipping"]["subpixels_per_native_axis"]
    if type(factor) is not int or factor < 1:
        raise ValueError("Invalid subpixel resolution")
    unit = factor ** 2
    _equal(report["clipping"]["native_area_per_subpixel"], 1 / unit)
    feature_ids = set()
    for cell in cells:
        key = cell["id"]
        if cell["stratum"] != selected[key] or cell["review_status"] != "visual_area_review_complete_with_limits":
            raise ValueError("Incomplete or misassigned area review")
        _equal(cell["inclusion_probability"], 8 / _STRATA[cell["stratum"]])
        x, y, x1, y1 = cell["bbox_px"]
        if key != f"x{x:04d}-y{y:04d}" or x1 - x != 160 or y1 - y != 160:
            raise ValueError("Sample identifier/core mismatch")
        if not (0 <= x < x1 <= 3560 and 0 <= y < y1 <= 7256) or not cell["review_notes"]:
            raise ValueError("Invalid sample extent or missing review notes")
        ticks = cell["roof_subpixel_count"]
        if type(ticks) is not int or ticks < 0:
            raise ValueError("Invalid integer subpixel tally")
        total = cell["roof_area_px2"]
        _equal(total, ticks / unit)
        _partition(cell["area_by_ward_px2"], _WARDS, total)
        _partition(cell["area_by_kind_px2"], _KINDS, total)
        _partition(cell["area_by_edge_evidence_px2"], _EDGES, total)
        _partition(cell["area_by_ward_subpixels"], _WARDS, ticks)
        for ward, count in cell["area_by_ward_subpixels"].items():
            if type(count) is not int:
                raise ValueError("Ward subpixel tallies must be integers")
            _equal(cell["area_by_ward_px2"][ward], count / unit)
        cross = cell["area_by_ward_and_kind_px2"]
        if set(cross) != _WARDS:
            raise ValueError("Invalid ward/class cross-tabulation")
        for ward in _WARDS:
            _partition(cross[ward], _KINDS, cell["area_by_ward_px2"][ward])
        for kind in _KINDS:
            _equal(sum(cross[w][kind] for w in _WARDS), cell["area_by_kind_px2"][kind])
        possible = _number(cell["possible_additional_roof_area_px2"])
        _partition(cell["possible_additional_area_by_ward_px2"], _WARDS, possible)
        city_area = _number(cell["city_area_in_core_px2"])
        raw_area = _number(cell["traced_area_in_core_before_city_clip_px2"])
        if total + possible > city_area + 1e-7 or city_area > 25600 or raw_area > 25600:
            raise ValueError("Area exceeds its clipping domain")
        _equal(raw_area, total + cell["removed_outside_city_px2"])
        _number(cell["overlapping_trace_area_removed_px2"])
        finer = cell["numerical_resolution_check"]
        if finer["subpixels_per_native_axis"] != 6:
            raise ValueError("Expected finer integration cross-check")
        _equal(finer["absolute_difference_px2"], abs(_number(finer["roof_area_px2"]) - total))
        for field, included in (("manual_polygons", True), ("uncertain_symbol_polygons", False)):
            for feature in cell[field]:
                if feature["type"] != "Feature" or feature["id"] in feature_ids:
                    raise ValueError("Invalid or duplicate trace feature")
                feature_ids.add(feature["id"])
                _geometry(feature["geometry"])
                props = feature["properties"]
                if (props["verified_building_identity"] is not False
                        or props["verified_ground_floor_footprint"] is not False
                        or props["included_in_principal_roof_area"] is not included
                        or props["status"] != "single_assistant_approximate_visual_roof_trace"
                        or props["kind"] not in _KINDS - {"ambiguous_class_overlap"}
                        or props["edge_evidence"] not in _EDGES):
                    raise ValueError("Invalid or overstated trace evidence status")
    totals = report["totals"]
    resolution = report["clipping"]["resolution_check"]
    if resolution["is_confidence_interval"] is not False or resolution["comparison_subpixels_per_native_axis"] != 6:
        raise ValueError("Numerical resolution is not statistical uncertainty")
    _equal(resolution["sample_roof_area_px2"],
           sum(c["numerical_resolution_check"]["roof_area_px2"] for c in cells))
    _equal(resolution["largest_cell_absolute_difference_px2"],
           max(c["numerical_resolution_check"]["absolute_difference_px2"] for c in cells))
    _equal(totals["reviewed_cells"], len(cells))
    _equal(totals["zero_roof_area_cells"], sum(c["roof_area_px2"] == 0 for c in cells))
    _equal(totals["manual_roof_polygons"], sum(len(c["manual_polygons"]) for c in cells))
    _equal(totals["uncertain_symbol_polygons"], sum(len(c["uncertain_symbol_polygons"]) for c in cells))
    _equal(totals["explicit_hole_rings"], sum(len(f["geometry"]["coordinates"]) - 1
                                           for c in cells for f in c["manual_polygons"]))
    for field in ("roof_area_px2", "possible_additional_roof_area_px2",
                  "removed_outside_city_px2", "overlapping_trace_area_removed_px2"):
        _equal(totals[field], sum(c[field] for c in cells))
    _equal(totals["city_area_in_sample_cores_px2"], sum(c["city_area_in_core_px2"] for c in cells))
    for field, keys in (("area_by_ward_px2", _WARDS), ("area_by_kind_px2", _KINDS),
                        ("area_by_edge_evidence_px2", _EDGES)):
        _partition(totals[field], keys, totals["roof_area_px2"])
        for key in keys:
            _equal(totals[field][key], sum(c[field][key] for c in cells))


def housing_evidence_report() -> dict:
    """Return fresh, validated evidence; do not infer occupancy or true footprint area."""
    resource = files("faerun").joinpath("data", "waterdeep_housing_evidence.json")
    report = json.loads(resource.read_text(encoding="utf-8"))
    validate_housing_evidence(report)
    return report
