"""Resident scenario provenance, separate from territories and visitor-days."""

from __future__ import annotations

from dataclasses import asdict, dataclass
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
