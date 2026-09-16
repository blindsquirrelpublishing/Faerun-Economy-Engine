import copy
import json
from pathlib import Path

import pytest

from tools.survey_waterdeep import (
    PATCHES, area, bounds, polygons_overlap, rectangle, reviewed_patch_area,
    sheet_page, validate_inventory,
)


INVENTORY = Path(__file__).resolve().parents[1] / "faerun" / "data" / "waterdeep_buildings.json"


def inventory():
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def test_partial_evidence_loads_without_the_pdf_or_image_dependencies():
    payload = inventory()
    assert validate_inventory(payload)
    assert not payload["census_ready"]
    assert payload["coverage"]["citywide_unique_building_count"] is None
    assert payload["coverage"]["city_building_review_fraction"] is None
    assert payload["coverage"]["city_sheets_fully_surveyed"] == 0
    assert payload["coverage"]["selected_unique_verified_map_footprints"] == 156
    assert len(payload["unresolved_groups"]) == 5
    assert all(o["area_sqft"] is None for o in payload["observations"])
    assert sum(o["ward"] is None for o in payload["observations"]) == 130


def test_population_contract_preserves_unknowns_and_qualified_verification():
    payload = inventory()
    assert payload["schema_version"] == 2
    assert payload["complete"] is payload["deduplicated"] is False
    assert payload["coverage"]["selected_subset_deduplicated"] is True
    assert payload["coverage"]["physically_scaled_building_count"] == 0
    assert payload["coverage"]["verified_footprint_sqft"] is None
    assert len(payload["buildings"]) == 156
    for building in payload["buildings"]:
        assert building["status"] == "verified"
        assert building["footprint_sqft"] is None
        assert (building["ward"], building["class"]) in ((None, None), ("city_of_the_dead", "A"))
        assert building["footprint_area_px2"] > 0
        assert building["source"]["pdf_page"] in (45, 53, 73, 91, 99)
        assert len(building["source"]["bbox_px"]) == 4


def test_sheet_tile_manifest_covers_exactly_city_map_pages():
    payload = inventory()
    pages = [tile["pdf_page"] for sheet in payload["sheets"] for tile in sheet["tiles"]]
    assert pages == list(range(34, 114))
    assert sheet_page(3, 0, 3) == 53
    assert sheet_page(5, 1, 3) == 73
    assert all(sheet["city_building_total"] is None for sheet in payload["sheets"])
    assert sum(s["selected_verified_map_footprints"] for s in payload["sheets"]) == 156
    with pytest.raises(ValueError):
        sheet_page(11, 0, 0)


def test_area_and_bbox_handle_irregular_roofs_not_their_bounding_rectangles():
    polygon = [[0, 0], [10, 0], [10, 3], [3, 3], [3, 10], [0, 10]]
    assert bounds(polygon) == [0, 0, 10, 10]
    assert area(polygon) == area(list(reversed(polygon))) == 51


def test_expansion_is_new_geometry_in_located_blocks_not_synthetic_counts():
    payload = inventory()
    expected = {
        "lamp-street-north": (53, 16),
        "wrightstone-sul-shield": (73, 19),
        "net-eel-pelnimbars": (45, 26),
        "lamp-street-south": (53, 26),
        "heroes-garden-favenbar": (73, 24),
        "saerdoun-trollwall": (99, 19),
        "city-dead-north-enclosure": (91, 26),
    }
    assert {p["id"]: (p["pdf_page"], p["verified_map_footprint_count"])
            for p in payload["patches"]} == expected
    assert sum(len(p["footprints"]) for p in PATCHES) == 156
    assert payload["coverage"]["city_sheets_with_samples"] == 5
    assert len({o["pdf_page"] for o in payload["observations"]}) == 5
    for observation in payload["observations"]:
        assert len(observation["polygon_px"]) >= 4
        assert observation["residential_use"] is observation["floor_count"] is None
    dedup = payload["reconstruction"]["selected_subset_deduplication"]
    assert dedup["canonical_pages"] == [45, 53, 73, 91, 99]
    assert dedup["citywide_seam_ownership"] is False


def test_only_source_identified_enclosure_supports_confirmed_ward_and_class():
    payload = inventory()
    assigned = [o for o in payload["observations"] if o["ward"] is not None]
    assert len(assigned) == payload["coverage"]["ward_assigned_building_count"] == 26
    assert payload["coverage"]["class_a_building_count"] == 26
    for observation in assigned:
        assert observation["patch_id"] == "city-dead-north-enclosure"
        assert observation["ward"] == "city_of_the_dead"
        assert observation["building_class"] == "A"
        assert observation["ward_status"] == "verified_enclosure"
        evidence = payload["ward_evidence"][observation["ward_evidence_id"]]
        assert {c["pdf_page"] for c in evidence["citations"]} == {4, 11, 13, 91}
    assert payload["source"]["source_year_dr"] == 1357
    assert payload["source"]["verified_for_1492_dr"] is False
    scale = payload["source"]["scale_audit"]
    assert scale["accepted_physical_calibrations"] == 0
    assert scale["floor_plan_scale_applies_to_city_roofs"] is False


def test_review_area_unions_native_patch_overlap_but_never_implies_city_coverage():
    payload = inventory()
    coverage = payload["coverage"]
    assert coverage["review_patch_area_px2_including_patch_overlaps"] == 394567
    assert coverage["review_patch_area_px2"] == reviewed_patch_area(payload["patches"]) == 393932
    assert coverage["raw_tile_area_review_fraction"] == pytest.approx(393932 / 37503345)
    masks = [
        {"pdf_page": 53, "bbox_px": [0, 0, 10, 10]},
        {"pdf_page": 53, "bbox_px": [5, 5, 15, 15]},
        {"pdf_page": 73, "bbox_px": [0, 0, 10, 10]},
    ]
    assert reviewed_patch_area(masks) == 275


def test_same_page_polygon_deduplication_handles_edges_crossings_and_containment():
    box = rectangle(0, 0, 10, 10)
    assert not polygons_overlap(box, rectangle(10, 0, 20, 10))
    assert not polygons_overlap(box, rectangle(20, 0, 30, 10))
    assert polygons_overlap(box, rectangle(5, 0, 15, 10))
    assert polygons_overlap(box, rectangle(3, 3, 7, 7))
    assert polygons_overlap(box, list(reversed(box)))
    assert polygons_overlap(rectangle(0, 4, 10, 6), rectangle(4, 0, 6, 10))


def test_candidates_are_separate_and_failed_detector_cannot_supply_a_city_count():
    payload = inventory()
    assert payload["validation"]["detector_status"] == "rejected_for_inventory_and_extrapolation"
    assert {o["id"] for o in payload["observations"]}.isdisjoint(
        {c["id"] for c in payload["diagnostic_candidates"]}
    )
    metrics = payload["validation"]["sensitivity"]
    assert all(m["manual_roof_count"] == 16 for m in metrics)
    assert len({m["candidate_count"] for m in metrics}) > 1
    assert any(m["missed_manual_roofs"] for m in metrics)
    assert any(m["false_candidates"] for m in metrics)


@pytest.mark.parametrize("tamper", [
    "city_count", "ready", "area", "sheet_count", "page", "escaped_polygon",
    "contract_area", "deduplication", "ward", "ward_evidence", "patch",
    "patch_count", "review_area", "epoch", "calibration", "classified_count",
    "unresolved_count", "source_hash", "tile_manifest", "review_fraction", "unresolved_geometry",
])
def test_invalid_precision_or_provenance_is_rejected(tamper):
    payload = copy.deepcopy(inventory())
    if tamper == "city_count":
        payload["coverage"]["citywide_unique_building_count"] = 10000
    elif tamper == "ready":
        payload["census_ready"] = True
    elif tamper == "area":
        payload["observations"][0]["area_px2"] += 1
    elif tamper == "sheet_count":
        payload["sheets"][2]["selected_verified_map_footprints"] -= 1
        payload["sheets"][4]["selected_verified_map_footprints"] += 1
    elif tamper == "page":
        payload["observations"][0]["pdf_page"] = 127
    elif tamper == "contract_area":
        payload["buildings"][0]["footprint_sqft"] = 1200
    elif tamper == "deduplication":
        payload["deduplicated"] = True
    elif tamper == "ward":
        payload["observations"][0]["ward"] = payload["buildings"][0]["ward"] = "castle"
    elif tamper == "ward_evidence":
        payload["ward_evidence"]["city-dead-enclosure"]["citations"] = []
    elif tamper == "patch":
        payload["patches"][0]["bbox_px"][2] += 1
    elif tamper == "patch_count":
        payload["patches"][0]["verified_map_footprint_count"] += 1
    elif tamper == "review_area":
        payload["coverage"]["review_patch_area_px2"] += 635
    elif tamper == "epoch":
        payload["source"]["verified_for_1492_dr"] = True
    elif tamper == "calibration":
        payload["source"]["physical_scale_verified"] = True
    elif tamper == "classified_count":
        payload["coverage"]["ward_assigned_building_count"] += 1
    elif tamper == "unresolved_count":
        payload["unresolved_groups"][0]["building_count"] = 2
    elif tamper == "source_hash":
        payload["source"]["sha256"] = "0" * 64
    elif tamper == "tile_manifest":
        payload["sheets"][0]["tiles"].pop()
    elif tamper == "review_fraction":
        payload["coverage"]["raw_tile_area_review_fraction"] *= 2
    elif tamper == "unresolved_geometry":
        payload["unresolved_groups"][0]["polygon_px"][0][0] += 1
    else:
        payload["observations"][0]["polygon_px"][0] = [0, 0]
    with pytest.raises(ValueError):
        validate_inventory(payload)
