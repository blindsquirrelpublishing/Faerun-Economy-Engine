"""Housing estimates from surveyed footprints, never from a target population."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from importlib.resources import files
import json
import math
from typing import Sequence


WARD_NAMES = {
    "castle": "Castle Ward", "north": "North Ward", "sea": "Sea Ward",
    "trades": "Trades Ward", "south": "Southern Ward", "dock": "Dock Ward",
    "city_of_the_dead": "City of the Dead",
}
CLASS_SHARES = {
    "castle": {"B": .4, "C": .4, "D": .2},
    "north": {"B": .6, "C": .4, "D": 0.0},
    "sea": {"B": .7, "C": .3, "D": 0.0},
    "trades": {"B": .3, "C": .4, "D": .3},
    "dock": {"B": .1, "C": .5, "D": .4},
}
CONDITION_MODIFIER = {
    "castle": 0, "north": 1, "sea": 1, "trades": 0, "south": -1, "dock": -1,
}


@dataclass(frozen=True)
class HousingAssumptions:
    name: str
    household_size: float
    apartment_sqft: float
    usable_floor_share: float
    occupied_unit_share: float
    rooming_permanent_share: float

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Housing assumptions require a scenario name")
        for field in ("household_size", "apartment_sqft"):
            value = getattr(self, field)
            if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{field} must be finite and positive")
        for field in ("usable_floor_share", "occupied_unit_share", "rooming_permanent_share"):
            value = getattr(self, field)
            if isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{field} must be between zero and one")


HOUSING_SCENARIOS = (
    HousingAssumptions("low", 4, 650, .65, .85, .25),
    HousingAssumptions("central", 5, 500, .75, .95, .50),
    HousingAssumptions("high", 6, 350, .85, 1.0, .75),
)


@dataclass(frozen=True)
class BuildingFootprint:
    id: str
    ward: str | None
    footprint_sqft: float | None
    verified: bool = False
    building_class: str | None = None
    institutional_residents: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("A footprint requires a stable id")
        if not isinstance(self.verified, bool):
            raise ValueError("Footprint verification must be a boolean")
        if self.ward is not None and self.ward not in WARD_NAMES:
            raise ValueError(f"Unknown census ward: {self.ward}")
        if self.building_class not in (None, "A", "B", "C", "D"):
            raise ValueError(f"Unknown building class: {self.building_class}")
        if self.ward == "city_of_the_dead" and self.building_class not in (None, "A"):
            raise ValueError("City System classifies City of the Dead structures as Class A")
        area = self.footprint_sqft
        if area is not None and (isinstance(area, bool) or not math.isfinite(area) or area <= 0):
            raise ValueError("Footprint area must be finite and positive")
        residents = self.institutional_residents
        if residents is not None:
            if self.building_class != "A":
                raise ValueError("Institutional residents require a separately classified A building")
            if isinstance(residents, bool) or not isinstance(residents, int) or residents < 0:
                raise ValueError("Institutional residents must be a nonnegative integer")


def _condition_share(ward: str) -> float:
    # Construction/major repair is assumed unavailable, not observed vacancy.
    modifier = CONDITION_MODIFIER[ward]
    return sum(roll + modifier not in (0, 1, 7) for roll in range(1, 9)) / 8


def _class_households(building_class: str, area: float, a: HousingAssumptions) -> tuple[float, float]:
    """Expected household-equivalents and separately counted single residents."""
    units_per_floor = area * a.usable_floor_share / a.apartment_sqft
    if building_class == "B":
        # Mean of one to four stories; towers and cellars are not extra housing.
        rooming = .2 * 2.5 * a.rooming_permanent_share
        upper_apartments = .2 * 1.5
        return (units_per_floor * (rooming + upper_apartments) + .1, .1)
    if building_class == "C":
        rooming = .2 * 2.5 * a.rooming_permanent_share
        shop_apartments = .1 * 1.5
        # The two mixed office/apartment outcomes share upper floors equally.
        office_apartments = .2 * 1.5 * .5
        apartments = .2 * 2.5
        return (units_per_floor * (rooming + shop_apartments + office_apartments + apartments)
                + .1 * .5, 0.0)
    if building_class == "D":
        rooming = .1 * a.rooming_permanent_share
        apartments = .1 + .1 * .5
        return (units_per_floor * (rooming + apartments) + .1, 0.0)
    raise ValueError("Class A buildings require individual institutional resident counts")


def estimate_building(building: BuildingFootprint, assumptions: HousingAssumptions) -> dict:
    """Calculate a footprint only when its identity, ward and scale are audited."""
    if not building.verified:
        return {"id": building.id, "estimate": None, "reason": "Unverified roof candidate"}
    if building.ward is None:
        return {"id": building.id, "estimate": None, "reason": "Ward not established"}
    if building.building_class == "A" or building.ward == "city_of_the_dead":
        if building.institutional_residents is None:
            return {"id": building.id, "estimate": None, "reason": "Institutional occupancy unknown"}
        return {
            "id": building.id, "estimate": float(building.institutional_residents),
            "household_equivalents": 0.0,
            "institutional_residents": building.institutional_residents,
        }
    if building.footprint_sqft is None:
        return {"id": building.id, "estimate": None, "reason": "Physical footprint scale not established"}
    if building.building_class is None and building.ward == "south":
        return {
            "id": building.id, "estimate": None,
            "reason": "Southern Ward printed class table leaves rolls 3-4 unassigned; classify this building explicitly",
        }
    shares = (
        {building.building_class: 1.0} if building.building_class is not None
        else CLASS_SHARES[building.ward]
    )
    households = singles = 0.0
    for building_class, probability in shares.items():
        homes, people = _class_households(building_class, building.footprint_sqft, assumptions)
        households += probability * homes
        singles += probability * people
    occupied = _condition_share(building.ward) * assumptions.occupied_unit_share
    return {
        "id": building.id,
        "estimate": (households * assumptions.household_size + singles) * occupied,
        "household_equivalents": households * occupied,
        "institutional_residents": 0,
    }


def housing_census(
    buildings: Sequence[BuildingFootprint], *, coverage_complete: bool,
    overlaps_resolved: bool, class_a_complete: bool,
    subset_deduplicated: bool | None = None,
    scenarios: Sequence[HousingAssumptions] = HOUSING_SCENARIOS,
) -> dict:
    """Return covered estimates; withhold city totals if any required input is missing."""
    if any(not isinstance(flag, bool) for flag in
           (coverage_complete, overlaps_resolved, class_a_complete)):
        raise ValueError("Survey coverage flags must be boolean")
    if subset_deduplicated is None:
        subset_deduplicated = overlaps_resolved
    if not isinstance(subset_deduplicated, bool):
        raise ValueError("Subset deduplication flag must be boolean")
    if overlaps_resolved and not subset_deduplicated:
        raise ValueError("Citywide deduplication cannot exclude the surveyed subset")
    ids = [building.id for building in buildings]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate footprint ids would double-count residents")
    names = [scenario.name for scenario in scenarios]
    if not names or len(names) != len(set(names)):
        raise ValueError("Housing scenario names must be nonempty and unique")
    wards = []
    missing = Counter()
    totals = {name: 0.0 for name in names}
    included = 0
    for ward, ward_name in WARD_NAMES.items():
        members = [building for building in buildings if building.ward == ward]
        sums = {name: 0.0 for name in names}
        estimable = 0
        for building in members:
            results = [estimate_building(building, scenario) for scenario in scenarios]
            reason = next((row["reason"] for row in results if row["estimate"] is None), None)
            if reason:
                missing[reason] += 1
                continue
            estimable += 1
            for name, row in zip(names, results):
                sums[name] += row["estimate"]
        for name in names:
            totals[name] += sums[name]
        included += estimable
        wards.append({
            "id": ward, "name": ward_name, "inventory_records": len(members),
            "estimable_buildings": estimable,
            "covered_residents": sums if estimable and subset_deduplicated else None,
        })
    missing["Ward not established"] += sum(building.ward is None for building in buildings)
    reasons = []
    if not buildings:
        reasons.append("No measured building inventory")
    if not coverage_complete:
        reasons.append("Citywide map coverage is incomplete")
    if not overlaps_resolved:
        reasons.append("Map overlaps have not been fully deduplicated")
    if not subset_deduplicated:
        reasons.append("Even covered footprints are not confirmed unique; subtotals withheld")
    if not class_a_complete:
        reasons.append("Unique Class A buildings and institutional residents are not fully accounted for")
    if included != len(buildings):
        reasons.append("Some inventory records cannot support a resident estimate")
    ready = not reasons
    return {
        "method": "City System footprint-based housing scenario",
        "source_year_dr": 1357,
        "status": "modeled_estimate" if ready else "incomplete_survey",
        "can_replace_population": ready,
        "city_residents": {name: round(totals[name]) for name in names} if ready else None,
        "covered_residents": totals if included and subset_deduplicated else None,
        "inventory_records": len(buildings),
        "verified_buildings": sum(building.verified for building in buildings),
        "estimable_buildings": included,
        "input_readiness": {
            "verified_with_ward": sum(b.verified and b.ward is not None for b in buildings),
            "verified_with_physical_area": sum(b.verified and b.footprint_sqft is not None for b in buildings),
            "verified_with_ward_and_physical_area": sum(
                b.verified and b.ward is not None and b.footprint_sqft is not None for b in buildings
            ),
            "verified_class_a_occupancy_unknown": sum(
                b.verified and (b.building_class == "A" or b.ward == "city_of_the_dead")
                and b.institutional_residents is None for b in buildings
            ),
            "counts_overlap": True,
        },
        "unresolved_counts": dict(sorted((key, value) for key, value in missing.items() if value)),
        "blockers": reasons,
        "wards": wards,
        "scenarios": [asdict(scenario) for scenario in scenarios],
        "confidence_interval": None,
        "formula": "Usable residential floor area / apartment area * occupied share * household size, plus separately classified residents",
        "assumptions": [
            "Source: user-supplied City System, printed pages 10-11 (PDF pages 11-12). Rules generate buildings; they are not an observed census.",
            "Ward classes, building-use probabilities and story distributions follow the guide. Class A buildings are excluded from random mixtures and need individual occupancy records.",
            "Low/central/high are sensitivity scenarios, not statistical confidence bounds or verified minimum/maximum populations.",
            "Household sizes 4/5/6, apartment areas 650/500/350 square feet, usable floor shares .65/.75/.85, and occupied unit shares .85/.95/1 are modeling assumptions.",
            "Rooming-house permanent resident shares .25/.50/.75 are assumed; temporary guests are not added to permanent population.",
            "Mixed upper-floor offices and apartments divide that space equally. Shared storage dwellings allocate half the floor to housing.",
            "Single-family residences count as one household; a noble individual's residence counts as one resident. Additional domestic staff are not independently enumerated.",
            "Derelict buildings and buildings under construction or extensive repair are assumed unoccupied, using the guide's ward-adjusted condition dice.",
            "Cellars, towers and unmeasured partial upper floors add no residential floor area in this model.",
            "The Southern Ward class table leaves rolls 3-4 unspecified. Its probabilities are not silently normalized or repaired.",
            "Covered subtotals are not extrapolated to unsurveyed wards. Unknown institutional occupancy and missing map regions are not zeros.",
            "A 1492 use would assume this 1357 building stock persists; no intervening construction, destruction or demographic growth has been surveyed.",
        ],
    }


def waterdeep_housing_report(settlement_id: str = "waterdeep") -> dict:
    """Read the persistent survey without opening the PDF or importing image tools."""
    if settlement_id != "waterdeep":
        raise KeyError(f"No building census for {settlement_id!r}")
    inventory = json.loads(
        files("faerun").joinpath("data", "waterdeep_buildings.json").read_text(encoding="utf-8")
    )
    if inventory["schema_version"] != 2:
        raise ValueError("Unsupported Waterdeep inventory schema")
    coverage = inventory["coverage"]
    raw_buildings = inventory["buildings"]
    observations = {row["id"]: row for row in inventory["observations"]}
    patches = {row["id"]: row for row in inventory["patches"]}
    if len(observations) != len(inventory["observations"]) or set(observations) != {row["id"] for row in raw_buildings}:
        raise ValueError("Building inventory does not reconcile to reviewed observations")
    if coverage["verified_building_count"] != sum(
        row["status"] == "verified" for row in raw_buildings
    ):
        raise ValueError("Inventory verification count does not reconcile")
    if coverage["ward_assigned_building_count"] != sum(row["ward"] is not None for row in raw_buildings):
        raise ValueError("Ward assignment count does not reconcile")
    if not inventory["source"]["physical_scale_verified"] and any(
        row["footprint_sqft"] is not None for row in raw_buildings
    ):
        raise ValueError("Uncalibrated survey must not assert square-foot areas")
    buildings = []
    for row in raw_buildings:
        if row["status"] not in ("verified", "candidate"):
            raise ValueError(f"Invalid footprint verification status: {row['status']!r}")
        observation = observations[row["id"]]
        if any(row[field] != observation[observed] for field, observed in (
            ("ward", "ward"), ("class", "building_class"),
            ("footprint_sqft", "area_sqft"), ("footprint_area_px2", "area_px2"),
        )):
            raise ValueError("Building classification/area differs from reviewed evidence")
        if any(row["source"][field] != observation[field] for field in (
            "patch_id", "pdf_page", "sheet", "bbox_px", "polygon_px", "ward_evidence_id",
        )):
            raise ValueError("Building source differs from its reviewed footprint")
        if row["ward"] is not None:
            evidence = inventory.get("ward_evidence", {}).get(observation["ward_evidence_id"])
            patch = patches.get(observation["patch_id"])
            if not evidence or not patch or not evidence.get("citations") or evidence["ward"] != row["ward"] or evidence["building_class"] != row["class"]:
                raise ValueError("Confirmed ward/class lacks a source evidence record")
            if patch.get("ward") != row["ward"] or patch.get("ward_evidence_id") != observation["ward_evidence_id"]:
                raise ValueError("Confirmed ward differs from its reviewed patch")
        buildings.append(BuildingFootprint(
            id=row["id"], ward=row["ward"], footprint_sqft=row["footprint_sqft"],
            verified=row["status"] == "verified", building_class=row["class"],
            institutional_residents=row.get("institutional_residents"),
        ))
    report = housing_census(
        buildings, coverage_complete=inventory["complete"],
        overlaps_resolved=inventory["deduplicated"],
        class_a_complete=coverage.get("class_a_complete", False),
        subset_deduplicated=coverage["selected_subset_deduplicated"],
    )
    if not inventory["source"]["physical_scale_verified"]:
        report["blockers"].append("Scan scale is not calibrated to square feet")
        report["can_replace_population"] = False
        report["city_residents"] = None
        report["status"] = "incomplete_survey"
    if inventory["source"].get("verified_for_1492_dr") is not True:
        report["blockers"].append("Historical 1357 DR map evidence is not verified 1492 DR building stock")
        report["can_replace_population"] = False
        report["city_residents"] = None
        report["status"] = "incomplete_survey"
    report.update({
        "settlement_id": "waterdeep",
        "high_resolution_map_survey": {
            "endpoint": "/api/census/hires?settlement=Waterdeep",
            "streets_endpoint": "/api/streets?settlement=Waterdeep",
            "atlas": "waterdeep.html#city-survey",
            "note": "Separate map source and wider boundary; not merged into the historical City System housing calculation.",
        },
        "survey": {
            "id": inventory["survey_id"],
            "status": inventory["status"],
            "source": inventory["source"],
            "coverage": coverage,
            "patches": inventory["patches"],
            "validation": inventory["validation"],
            "exclusions": inventory["exclusions"],
            "limitations": inventory["limitations"],
            "reconstruction": inventory["reconstruction"],
            "ward_evidence": inventory.get("ward_evidence", {}),
        },
        "building_inventory": raw_buildings,
        "unresolved_roof_groups": inventory["unresolved_groups"],
    })
    return report
