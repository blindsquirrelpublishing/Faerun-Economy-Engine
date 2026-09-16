"""Read-only Daggerford evidence, roof-group inventory and conditional geometry.

The public map is an illustration, not a building or population census. Runtime
code uses only the standard library; optional image annotation lives in tools.
"""

from __future__ import annotations

from collections import Counter
import hashlib
from importlib.resources import files
import json
import math
from pathlib import Path
import re


def _finite_number(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def _point_inside(point: list, polygon: list) -> bool:
    x, y = point
    inside = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        cross = (x - a[0]) * (b[1] - a[1]) - (y - a[1]) * (b[0] - a[0])
        if (abs(cross) < 1e-9 and min(a[0], b[0]) <= x <= max(a[0], b[0])
                and min(a[1], b[1]) <= y <= max(a[1], b[1])):
            return True
        if (a[1] > y) != (b[1] > y):
            intersection = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < intersection:
                inside = not inside
    return inside


def _area(polygon: list) -> float:
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(polygon, polygon[1:] + polygon[:1]))) / 2


def _length(points: list) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1])
               for a, b in zip(points, points[1:]))


def validate_daggerford_analysis(data: dict) -> None:
    """Reject broken identities, source hashes and out-of-bound observations."""
    if data.get("schema_version") != 1 or data.get("settlement_id") != "daggerford":
        raise ValueError("Unsupported Daggerford analysis schema")
    image = data["map"]
    if not re.fullmatch(r"[0-9a-f]{64}", image["sha256"]):
        raise ValueError("Map source requires a SHA-256 fingerprint")
    if not image["image_url"].startswith("https://"):
        raise ValueError("Map source requires its public HTTPS URL")
    for dimension in ("width_px", "height_px"):
        if not isinstance(image[dimension], int) or isinstance(image[dimension], bool) or image[dimension] <= 0:
            raise ValueError("Image dimensions must be positive integers")

    def check_point(point: list) -> None:
        if not isinstance(point, list) or len(point) != 2 or not all(_finite_number(v) for v in point):
            raise ValueError("Coordinates must be finite x/y pairs")
        if not (0 <= point[0] < image["width_px"] and 0 <= point[1] < image["height_px"]):
            raise ValueError("Coordinate falls outside the source image")

    polygons = data["scope"]["polygons_px"]
    for polygon in polygons.values():
        if len(polygon) < 3:
            raise ValueError("Survey boundary requires at least three points")
        for point in polygon:
            check_point(point)
        if _area(polygon) <= 0:
            raise ValueError("Survey boundary must enclose an area")

    identities: set[str] = set()
    coordinates: set[tuple] = set()
    roof_ids: set[str] = set()
    for sector, rows in data["roof_groups"].items():
        boundary = polygons["riverfront" if sector == "riverfront" else "walled_town"]
        for row in rows:
            if len(row) != 4:
                raise ValueError("Roof row must contain id, x, y, landmark key")
            identity, x, y, key = row
            if not isinstance(identity, str) or not identity or identity in identities:
                raise ValueError("Survey identities must be unique")
            identities.add(identity)
            roof_ids.add(identity)
            point = [x, y]
            check_point(point)
            if (x, y) in coordinates:
                raise ValueError("Duplicate roof-group coordinate")
            coordinates.add((x, y))
            if not _point_inside(point, boundary):
                raise ValueError(f"{identity} falls outside its {sector} survey boundary")
            if key is not None and str(key) not in data["landmarks"]:
                raise ValueError("Unknown landmark key")
    for group in ("infrastructure", "unresolved_symbols"):
        for row in data[group]:
            if row["id"] in identities:
                raise ValueError("Survey identities must be unique")
            identities.add(row["id"])
            check_point(row["point"])
            if not any(_point_inside(row["point"], polygon) for polygon in polygons.values()):
                raise ValueError("Infrastructure or unresolved symbol outside survey")
    for caveat in data["roof_group_caveats"]:
        if not set(caveat["ids"]) <= roof_ids:
            raise ValueError("Roof caveat references an unknown roof group")
    street_ids: set[str] = set()
    street_names: set[str] = set()
    for street in data["streets"]:
        if street["id"] in street_ids or street["name"] in street_names:
            raise ValueError("Street identities and names must be unique")
        street_ids.add(street["id"])
        street_names.add(street["name"])
        if len(street["points"]) < 2:
            raise ValueError("Street requires at least two points")
        check_point(street["label_point"])
        for point in street["points"]:
            check_point(point)
            if not _point_inside(point, polygons["walled_town"]):
                raise ValueError("Street point outside the town survey boundary")
        if _length(street["points"]) <= 0:
            raise ValueError("Street must have positive length")
    scale = image["scale"]
    for interpretation in scale["interpretations"]:
        values = [interpretation[k] for k in ("start_px", "end_px", "span_feet")]
        if (not all(_finite_number(value) for value in values)
                or not 0 <= values[0] < values[1] < image["width_px"] or values[2] <= 0):
            raise ValueError("Invalid conditional scale interpretation")
    for scenario in data["sensitivity"]["scenarios"]:
        for field in ("household_size", "households_per_residential_group"):
            if not _finite_number(scenario[field]) or scenario[field] <= 0:
                raise ValueError("Occupancy sensitivity requires positive finite inputs")
        for field in ("residential_share", "occupied_unit_share"):
            if not _finite_number(scenario[field]) or not 0 <= scenario[field] <= 1:
                raise ValueError("Occupancy shares must be between zero and one")


def daggerford_analysis_report(settlement=None, *, image_path: str | Path | None = None) -> dict:
    """Return fresh JSON-compatible evidence without changing population inputs.

    Pass the active world's Daggerford Settlement to reflect scenario overrides.
    When omitted, the current built-in settlement row supplies the baseline.
    ``image_path`` is optional local evidence to verify, never a download request.
    """
    if settlement is None:
        from .data.settlements import SETTLEMENTS

        settlement = next(item for item in SETTLEMENTS if item.id == "daggerford")
    if settlement.id != "daggerford":
        raise ValueError("Daggerford analysis requires the Daggerford settlement")
    residents = settlement.population
    if isinstance(residents, bool) or not isinstance(residents, int) or residents < 0:
        raise ValueError("Resident population must be a nonnegative integer")
    resource = files("faerun").joinpath("data", "daggerford_analysis.json")
    payload = resource.read_bytes()
    report = json.loads(payload)
    validate_daggerford_analysis(report)
    report["analysis_sha256"] = hashlib.sha256(payload).hexdigest()
    report["active_baseline"] = {
        "settlement_id": settlement.id,
        "resident_population": residents,
        "status": "Unchanged simulation input; not validated by this map",
        "world_reference_year_dr": report["world_reference_year_dr"],
        "population_source_year_dr": None,
        "mutated": False,
        "note": "Map roof counts and illustrative occupancy assumptions were not fitted to this input.",
    }
    report["map"]["source_hash_verification"] = {
        "status": "not_checked",
        "expected_sha256": report["map"]["sha256"],
        "actual_sha256": None,
        "note": "The dataset pins the public image hash; source bytes are optional and not bundled as licensed package data.",
    }
    if image_path is not None:
        actual = hashlib.sha256(Path(image_path).read_bytes()).hexdigest()
        report["map"]["source_hash_verification"].update({
            "status": "verified" if actual == report["map"]["sha256"] else "mismatch",
            "actual_sha256": actual,
        })
        if actual != report["map"]["sha256"]:
            raise ValueError("Source image SHA-256 does not match the audited Daggerford preview")

    rows = [(sector, row) for sector, members in report["roof_groups"].items() for row in members]
    provisional_ids = {identity for caveat in report["roof_group_caveats"] for identity in caveat["ids"]}
    report["inventory_summary"] = {
        "unit": "Manually indexed roof groups, not buildings",
        "reviewed_roof_groups": len(rows),
        "by_sector": {sector: len(members) for sector, members in report["roof_groups"].items()},
        "groups_with_explicit_caveats": len(provisional_ids),
        "additional_unresolved_symbols": len(report["unresolved_symbols"]),
        "infrastructure_features": dict(Counter(item["kind"] for item in report["infrastructure"])),
        "landmark_keys": len(report["landmarks"]),
        "exact_buildings": None,
        "households": None,
        "is_complete_building_census": False,
    }
    interpretations = report["map"]["scale"]["interpretations"]
    for interpretation in interpretations:
        interpretation["feet_per_pixel"] = interpretation["span_feet"] / (
            interpretation["end_px"] - interpretation["start_px"])
    for street in report["streets"]:
        street["length_px"] = round(_length(street["points"]), 3)
        street["conditional_length_feet"] = {
            item["id"]: round(_length(street["points"]) * item["feet_per_pixel"], 2)
            for item in interpretations
        }
    report["geometry"] = {
        "named_streets": len(report["streets"]),
        "named_route_polyline_sum_px": round(sum(_length(s["points"]) for s in report["streets"]), 3),
        "boundary_polygon_areas_px2": {name: _area(polygon)
                                        for name, polygon in report["scope"]["polygons_px"].items()},
        "area_note": "Areas of approximate inclusion polygons, not roof footprints or precise habitable town area.",
        "adopted_town_area_sqft": None,
        "network_complete": False,
        "route_note": "A sum of approximate named polylines, not a complete or deduplicated street-network length.",
    }
    sensitivity = report["sensitivity"]
    excluded_keys = set(sensitivity["excluded_landmark_keys"])
    eligible = [(sector, row) for sector, row in rows
                if row[3] not in excluded_keys
                and not (sensitivity["exclude_riverfront"] and sector == "riverfront")]
    sensitivity["eligible_roof_groups"] = len(eligible)
    sensitivity["eligible_group_ids"] = [row[0] for _, row in eligible]
    for scenario in sensitivity["scenarios"]:
        per_group = (scenario["residential_share"] * scenario["households_per_residential_group"]
                     * scenario["occupied_unit_share"] * scenario["household_size"])
        scenario["residents_per_100_eligible_groups"] = round(per_group * 100, 3)
        scenario["conditional_noninstitutional_component"] = round(len(eligible) * per_group, 3)
        scenario["town_total"] = None
    report["integration"] = {
        "call": "faerun.daggerford.daggerford_analysis_report(active_daggerford_settlement)",
        "side_effects": "None: no downloads, file writes, population mutation or World construction",
        "package_data_required": "data/daggerford_analysis.json",
        "currency": "Report metadata and source-specific periods do not advance with the simulation clock",
        "population_change_authorized": False,
    }
    return report
