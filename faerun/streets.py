"""Offline, dependency-free Waterdeep image-coordinate street survey loader."""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from importlib.resources import files
import hashlib
import json
import math


def _validate_report(report: dict) -> None:
    """Reject malformed geometry rather than silently drawing misleading roads."""
    if report.get("schema_version") != 1 or report.get("type") != "FeatureCollection":
        raise ValueError("Unsupported Waterdeep street survey schema")
    space = report["coordinate_space"]
    if space != {
        "units": "image_pixels", "width": 3560, "height": 7256, "origin": "top_left"
    }:
        raise ValueError("Street coordinates must refer to the original Waterdeep raster")
    ids = set()
    if not isinstance(report["features"], list):
        raise ValueError("Street features must be a list")
    reviewed = []
    candidates = []
    for feature in report["features"]:
        identity = feature.get("id")
        if not isinstance(identity, str) or not identity or identity in ids:
            raise ValueError("Street features require unique stable IDs")
        ids.add(identity)
        if feature.get("type") != "Feature":
            raise ValueError("Invalid street feature")
        properties = feature["properties"]
        if properties.get("name") is not None and (
            not isinstance(properties["name"], str) or not properties["name"].strip()
        ):
            raise ValueError("An unresolved street name must be null")
        if not properties.get("status") or not properties.get("kind"):
            raise ValueError("Street provenance status and kind are required")
        if properties["status"] == "machine_traced_candidate":
            candidates.append(feature)
        elif properties["status"] == "assistant_reviewed_route":
            if not properties.get("name") or properties["kind"] != "named_street_route":
                raise ValueError("Reviewed routes need a visually sourced name and route kind")
            evidence = properties.get("source_review", {})
            if (evidence.get("source_sha256") != report["source"]["sha256"]
                    or evidence.get("overlay_reviewed") is not True):
                raise ValueError("Reviewed routes require explicit source-overlay evidence")
            digest = hashlib.sha256(json.dumps(
                feature["geometry"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")).hexdigest()
            if evidence.get("approved_geometry_sha256") != digest:
                raise ValueError("Reviewed geometry changed without renewed source review")
            reviewed.append(feature)
        else:
            raise ValueError("Unapproved route proposals cannot enter the runtime layer")
        geometry = feature["geometry"]
        if geometry["type"] not in {"LineString", "MultiLineString"}:
            raise ValueError("Street features must contain paths, not label points")
        lines = ([geometry["coordinates"]] if geometry["type"] == "LineString"
                 else geometry["coordinates"])
        if not lines:
            raise ValueError("Empty street geometry")
        for line in lines:
            if len(line) < 2 or len({tuple(p) for p in line}) < 2:
                raise ValueError("Street paths need two distinct coordinates")
            for point in line:
                if len(point) != 2:
                    raise ValueError("Invalid pixel coordinate")
                for value, bound in zip(point, (3560, 7256)):
                    if isinstance(value, bool) or not isinstance(value, (int, float)):
                        raise ValueError("Street coordinates must be finite numbers")
                    if not math.isfinite(value) or not 0 <= value < bound:
                        raise ValueError("Street coordinate lies outside the source image")
    coverage = report["coverage"]
    if coverage["feature_count"] != len(ids):
        raise ValueError("Street coverage count does not match features")
    named = sum(feature["properties"]["name"] is not None for feature in report["features"])
    if coverage["named_feature_count"] != named:
        raise ValueError("Named street count does not match features")
    if coverage["unnamed_feature_count"] != len(ids) - named:
        raise ValueError("Unnamed street count does not match features")
    if coverage.get("candidate_segment_count", len(candidates)) != len(candidates):
        raise ValueError("Raw segment count does not match the candidate layer")
    if coverage.get("reviewed_route_count", 0) != len(reviewed):
        raise ValueError("Reviewed route count does not match the reviewed layer")
    if coverage.get("reviewed_named_street_count", 0) != len({
        f["properties"]["name"] for f in reviewed
    }):
        raise ValueError("Reviewed name count does not match the reviewed layer")
    if "reviewed_route_survey" in report:
        withheld = report["reviewed_route_survey"]["withheld_routes"]
        names = {f["properties"]["name"] for f in reviewed}
        withheld_names = {item["name"] for item in withheld}
        if names & withheld_names or len(withheld_names) != len(withheld):
            raise ValueError("Reviewed and withheld name inventories must be disjoint")
        if coverage["withheld_route_count"] != len(withheld):
            raise ValueError("Withheld route count does not match the name inventory")
        if coverage["visually_transcribed_name_count"] != len(names | withheld_names):
            raise ValueError("Visual name inventory count does not match reviewed/withheld names")


@lru_cache(maxsize=1)
def _load_report(serialized: str) -> dict:
    report = json.loads(serialized)
    _validate_report(report)
    return report


def waterdeep_streets_report() -> dict:
    """Return independent, JSON-serializable source, coverage and path evidence.

    Features distinguish assistant-reviewed named routes from raw candidates.
    Names may be null. Coordinates are original image pixels, never WGS84.
    Completeness and naming coverage are reported separately and explicitly.
    """
    resource = files("faerun").joinpath("data", "waterdeep_streets.json")
    return deepcopy(_load_report(resource.read_text(encoding="utf-8")))
