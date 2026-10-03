"""Resident scenario provenance, separate from territories and visitor-days."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite, pi, sqrt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Settlement


@dataclass(frozen=True)
class PopulationEvidence:
    title: str
    url: str
    scope: str
    period: str
    description: str
    kind: str = "secondary"
    accessed: str = "2026-09-16"


@dataclass(frozen=True)
class PopulationBasis:
    residents: int
    reference_year: int
    comparison_residents: int
    scope: str
    rationale: str
    evidence: tuple[PopulationEvidence, ...]

    def __post_init__(self) -> None:
        for name in ("residents", "comparison_residents", "reference_year"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"Population basis {name} must be a positive integer")


def land_area_report(
    settlement: Settlement,
    *,
    settlement_density_per_sq_mile: float = 10_000.0,
    agricultural_acres_per_person: float = 2.0,
    local_food_share: float = 1.0,
    usable_farmland_share: float = 0.5,
) -> dict:
    """Estimate resident land needs, not surveyed boundaries or available land."""
    population = settlement.population
    if isinstance(population, bool) or not isinstance(population, int) or population < 0:
        raise ValueError("Resident population must be a nonnegative integer")
    inputs = {
        "settlement_density_per_sq_mile": settlement_density_per_sq_mile,
        "agricultural_acres_per_person": agricultural_acres_per_person,
        "local_food_share": local_food_share,
        "usable_farmland_share": usable_farmland_share,
    }
    for name, value in inputs.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError(f"{name} must be a finite number")
    if settlement_density_per_sq_mile <= 0:
        raise ValueError("settlement_density_per_sq_mile must be positive")
    if agricultural_acres_per_person <= 0:
        raise ValueError("agricultural_acres_per_person must be positive")
    if not 0 <= local_food_share <= 1:
        raise ValueError("local_food_share must be between 0 and 1")
    if not 0 < usable_farmland_share <= 1:
        raise ValueError("usable_farmland_share must be greater than 0 and at most 1")

    footprint = population / settlement_density_per_sq_mile
    farmland_acres = population * agricultural_acres_per_person * local_food_share
    farmland = farmland_acres / 640
    countryside = farmland / usable_farmland_share
    total = footprint + countryside
    if not all(isfinite(value) for value in (footprint, farmland_acres, countryside, total)):
        raise ValueError("Land area calculation exceeds finite numeric limits")
    footprint_radius = sqrt(footprint / pi)
    outer_radius = sqrt(total / pi)
    return {
        "status": "scenario_estimate",
        "resident_population": population,
        "inputs": inputs,
        "settlement_footprint_sq_miles": footprint,
        "required_agricultural_acres": farmland_acres,
        "required_agricultural_sq_miles": farmland,
        "surrounding_support_sq_miles": countryside,
        "combined_sq_miles": total,
        "equivalent_settlement_radius_miles": footprint_radius,
        "equivalent_outer_radius_miles": outer_radius,
        "equivalent_support_ring_width_miles": outer_radius - footprint_radius,
        "assumptions": [
            "Defaults are illustrative scenario assumptions, not surveyed areas or historical facts.",
            "Settlement density includes buildings, streets, yards and public spaces; override for local form.",
            "Agricultural acres per person include yield, diet, fallow and livestock land requirements.",
            "Local food share is assumed, not inferred from trade, prices or magical production.",
            "Surrounding support area excludes the settlement footprint and already includes farmland.",
            "Usable farmland share is assumed, not measured from terrain; water and unsuitable land need allowance.",
            "Equivalent circles are area comparisons, not mapped boundaries or terrain-aware allocations.",
            "Residents only: visitors and additional rural households are not included.",
            "No land is reserved; neighboring support areas may overlap and food capacity is not verified.",
            "Surface agriculture assumptions may not apply to Underdark or other exceptional locations.",
        ],
    }


def population_report(settlement: Settlement) -> dict:
    """Describe the actual settlement input, including deliberate overrides."""
    population = settlement.population
    if isinstance(population, bool) or not isinstance(population, int) or population < 0:
        raise ValueError("Resident population must be a nonnegative integer")
    basis = settlement.population_basis
    report = {
        "settlement_id": settlement.id,
        "settlement": settlement.name,
        "resident_population": population,
        "land_area": land_area_report(settlement),
        "status": "gazetteer_estimate",
        "scope": "Settlement residents; visitors and other settlements excluded",
        "reference_year_dr": None,
        "confidence_interval": None,
        "regional_population_added_to_demand": 0,
        "external_visitors_per_day": None,
        "assumptions": [
            "Residents are a fixed scenario input, not an enumerated census.",
            "Changing the simulation date does not reconstruct historical population or compound growth.",
            "Households, soldiers, militia, mages and workers are subsets of residents, not additional people.",
            "Territorial totals may include this city and other modeled settlements; they are not added to city demand.",
            "External and peak-season visitor counts are unknown, not zero; domestic visits are modeled separately.",
        ],
        "evidence": [],
    }
    if settlement.id == "daggerford":
        report["settlement_analysis_endpoint"] = "/api/settlement-analysis?settlement=Daggerford"
        report["settlement_analysis_page"] = "daggerford.html"
    if basis is None:
        return report
    if settlement.id == "waterdeep":
        report["housing_census_endpoint"] = "/api/census?settlement=Waterdeep"
    status = (
        "scenario_estimate" if population == basis.residents else
        "comparison_baseline" if population == basis.comparison_residents else
        "scenario_override"
    )
    report.update({
        "status": status,
        "scope": basis.scope,
        "reference_year_dr": basis.reference_year,
        "scenario_residents": basis.residents,
        "comparison_residents": basis.comparison_residents,
        "resident_change": population - basis.comparison_residents,
        "resident_change_pct": (population / basis.comparison_residents - 1) * 100,
        "household_demand_multiplier": population / basis.comparison_residents,
        "rationale": basis.rationale,
        "evidence": [asdict(item) for item in basis.evidence],
    })
    report["assumptions"].append(
        "The comparison scales per-person household quantities at unchanged wealth and diet; "
        "prices, staffing rounding, capacity and imports need separate recalculation."
    )
    return report
