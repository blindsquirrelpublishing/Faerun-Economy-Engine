"""Finite, explicitly inferred domestic water sources and access, in gallons."""

from __future__ import annotations

import math
from typing import Mapping

from .models import Settlement


LITRES_PER_GALLON = 3.785411784
DRINKING_GALLONS_PER_PERSON = 3.0 / LITRES_PER_GALLON
COOKING_GALLONS_PER_PERSON = 2.0 / LITRES_PER_GALLON
DOMESTIC_GALLONS_PER_PERSON = 20.0 / LITRES_PER_GALLON
ESSENTIAL_GALLONS_PER_PERSON = DRINKING_GALLONS_PER_PERSON + COOKING_GALLONS_PER_PERSON

# These describe a provisional accessible catchment, not measured aquifers.
GROUNDWATER = {
    "plains": 1.0, "coast": .9, "hills": .8, "forest": 1.1, "jungle": 1.2,
    "marsh": .8, "swamp": .8, "mountains": .65, "taiga": .65,
    "tundra": .35, "desert": .4, "cavern": .5,
}
RAIN_CAPTURE = {
    "plains": 3, "coast": 4, "hills": 3, "forest": 5, "jungle": 8,
    "marsh": 5, "swamp": 5, "mountains": 3, "taiga": 2,
    "tundra": 1, "desert": .4, "cavern": 0,
}
SELF_ACCESS = {"desert": .75, "tundra": .65, "mountains": .8, "cavern": .75}
OVERRIDE_FIELDS = frozenset({
    "natural_gallons_per_day", "source_multiplier", "potable_fraction",
    "household_gallons_per_person_day", "municipal_collection_multiplier",
})


def _quantity(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite non-negative number")
    return float(value)


def validate_overrides(overrides: Mapping | None) -> dict:
    if overrides is None:
        return {}
    if not isinstance(overrides, Mapping):
        raise ValueError("Water overrides must be a mapping")
    unknown = set(overrides) - OVERRIDE_FIELDS
    if unknown:
        raise ValueError(f"Unknown water override fields: {', '.join(sorted(map(str, unknown)))}")
    values = {key: _quantity(value, key) for key, value in overrides.items()}
    if values.get("potable_fraction", 0) > 1:
        raise ValueError("potable_fraction must be between zero and one")
    return values


def water_resources(s: Settlement, season: str = "summer", overrides: Mapping | None = None) -> dict:
    """Estimate raw and usable yields independently of municipal employment."""
    scenario = validate_overrides(overrides)
    pop = _quantity(s.population, "population")
    if season not in {"winter", "spring", "summer", "autumn"}:
        raise ValueError(f"Unknown water season: {season}")
    terrain = "cavern" if s.underdark else s.terrain
    groundwater_season = {"winter": .85, "spring": 1.0, "summer": .9, "autumn": 1.05}[season]
    rain_season = {"winter": .7, "spring": 1.4, "summer": .6, "autumn": 1.2}[season]
    sources = []

    def source(name: str, litres_per_person: float, safe_fraction: float, basis: str) -> None:
        raw = pop * litres_per_person / LITRES_PER_GALLON
        if raw:
            sources.append({"name": name, "raw_gallons_per_day": raw,
                            "potable_fraction": safe_fraction, "basis": basis})

    source("Provisional wells and springs",
           35 * GROUNDWATER.get(terrain, .7) * groundwater_season, .9,
           "Unverified groundwater allowance for an inhabited settlement; terrain and season modify yield. Not evidence of a particular well.")
    if s.river or terrain in {"marsh", "swamp"}:
        source("Accessible surface freshwater", 100 if s.river else 40, .5,
               "River/wetland metadata suggests access, not a measured flow or water-quality survey. Seawater is excluded.")
    source("Rain capture and cistern replenishment",
           RAIN_CAPTURE.get(terrain, 2) * rain_season, .8,
           "Estimated replenishment only: cistern storage is not counted again as a daily source.")
    if "natural_gallons_per_day" in scenario:
        sources = [{
            "name": "Configured local freshwater scenario",
            "raw_gallons_per_day": scenario["natural_gallons_per_day"],
            "potable_fraction": .9,
            "basis": "Explicit scenario replaces all inferred source yields; it is not automatically a verified measurement.",
        }]
    for row in sources:
        row["raw_gallons_per_day"] = _quantity(
            row["raw_gallons_per_day"] * scenario.get("source_multiplier", 1.0), "source yield")
        row["potable_fraction"] = scenario.get("potable_fraction", row["potable_fraction"])
        row["usable_gallons_per_day"] = row["raw_gallons_per_day"] * row["potable_fraction"]
    private_rate = scenario.get(
        "household_gallons_per_person_day",
        10 * SELF_ACCESS.get(terrain, 1.0) / LITRES_PER_GALLON,
    )
    return {
        "unit": "gallon", "season": season,
        "evidence": "scenario override" if scenario else "inferred; hydrology unverified",
        "profile_inferred": s.has_trait("surveyed_market"),
        "sources": sources,
        "natural_gallons_per_day": _quantity(sum(row["raw_gallons_per_day"] for row in sources), "total source yield"),
        "usable_gallons_per_day": _quantity(sum(row["usable_gallons_per_day"] for row in sources), "usable source yield"),
        "household_gallons_per_person_day": private_rate,
        "municipal_collection_multiplier": scenario.get("municipal_collection_multiplier", 1.0),
        "overrides": scenario,
    }


def constrain_utilities(row: dict, resources: dict, profile: dict,
                        resident_presence: float, visitor_person_days: float) -> None:
    """Limit full municipal-service equivalents by labor and usable freshwater."""
    residents = _quantity(resident_presence, "resident_presence")
    visitors = _quantity(visitor_person_days, "visitor_person_days")
    labor_capacity = row["capacity_per_day"]
    multiplier = resources["municipal_collection_multiplier"]
    if multiplier != 1:
        parameters = profile["formula_assumptions"]["service_parameters"]
        base_productivity = row["units_per_worker_workday"]
        # Existing productivity reserves 10% for fire readiness and divides
        # remaining labor between water collection and waste handling.
        waste_time = parameters["waste_lb_per_resident_day"] / parameters["waste_lb_per_worker_day"]
        water_time = max(0.0, .9 / base_productivity - waste_time) if base_productivity else 0.0
        productivity = .9 / (water_time / multiplier + waste_time) if multiplier and base_productivity else 0.0
        labor_capacity = row["workers"] * productivity * row["workdays_per_year"] / 365
        row["units_per_worker_workday"] = productivity
    row["water_collection_multiplier"] = multiplier
    row["labor_capacity_per_day"] = labor_capacity
    row["water_capacity_per_day"] = resources["usable_gallons_per_day"] / DOMESTIC_GALLONS_PER_PERSON
    row["capacity_per_day"] = min(labor_capacity, row["water_capacity_per_day"])
    visitor_count = (row["visitor_demand_per_day"] / row["visitor_units_per_person_day"]
                     if row["visitor_units_per_person_day"] else 0.0)
    row["visitor_units_per_person_day"] = visitors / visitor_count if visitor_count else 0.0
    row["resident_demand_per_day"] = residents
    row["visitor_demand_per_day"] = visitors
    row["demand_per_day"] = residents + visitors
    row["planned_per_day"] = min(row["demand_per_day"], row["capacity_per_day"])
    row["basis"] += (
        " Complete municipal-service equivalents are also limited by modeled usable freshwater. "
        "Water collection productivity is separate from source yield. Household/private collection "
        "is assessed separately and shares the same water pool. Domestic demand uses residents present "
        "plus visitor food-day equivalents. A bundle shortfall is not a death forecast."
    )


def water_balance(resources: dict, resident_presence: float, visitor_person_days: float,
                  municipal_capacity_gallons_per_day: float,
                  municipal_delivered_gallons_per_day: float) -> dict:
    """Allocate one shared safe-water pool; prioritize essentials over other use."""
    residents = _quantity(resident_presence, "resident_presence")
    visitors = _quantity(visitor_person_days, "visitor_person_days")
    municipal_capacity = _quantity(municipal_capacity_gallons_per_day, "municipal_capacity")
    municipal_actual = _quantity(municipal_delivered_gallons_per_day, "municipal_delivery")
    people = _quantity(residents + visitors, "total person-days")
    drinking = people * DRINKING_GALLONS_PER_PERSON
    cooking = people * COOKING_GALLONS_PER_PERSON
    essential = drinking + cooking
    demand = _quantity(people * DOMESTIC_GALLONS_PER_PERSON, "domestic demand")
    usable = resources["usable_gallons_per_day"]
    private_capacity = _quantity(residents * resources["household_gallons_per_person_day"], "household capacity")
    municipal = min(municipal_actual, municipal_capacity, usable, demand)
    private = min(private_capacity, max(0.0, usable - municipal), max(0.0, demand - municipal))
    delivered = municipal + private
    essential_supplied = min(essential, delivered)
    other_need = demand - essential
    other_supplied = min(other_need, max(0.0, delivered - essential_supplied))
    essential_gap = max(0.0, essential - essential_supplied)
    routine_gap = max(0.0, other_need - other_supplied)
    total_capacity = municipal_capacity + private_capacity
    status = ("essential_gap" if essential_gap > 1e-6 else
              "routine_gap" if routine_gap > 1e-6 else "covered")
    return {
        **resources, "status": status, "resident_person_days": residents,
        "visitor_person_days": visitors, "total_person_days": people,
        "drinking_demand_gallons_per_day": drinking,
        "essential_cooking_demand_gallons_per_day": cooking,
        "essential_demand_gallons_per_day": essential,
        "routine_demand_gallons_per_day": other_need,
        "total_demand_gallons_per_day": demand,
        "municipal_capacity_gallons_per_day": municipal_capacity,
        "household_capacity_gallons_per_day": private_capacity,
        "municipal_delivered_gallons_per_day": municipal,
        "household_delivered_gallons_per_day": private,
        "total_delivered_gallons_per_day": delivered,
        "essential_supplied_gallons_per_day": essential_supplied,
        "routine_supplied_gallons_per_day": other_supplied,
        "essential_gap_gallons_per_day": essential_gap,
        "routine_gap_gallons_per_day": routine_gap,
        "source_gap_gallons_per_day": max(0.0, demand - usable),
        "access_gap_gallons_per_day": max(0.0, min(demand, usable) - total_capacity),
        "operations_gap_gallons_per_day": max(0.0, min(demand, usable, total_capacity) - delivered),
        "unused_usable_gallons_per_day": max(0.0, usable - delivered),
        "essential_coverage": essential_supplied / essential if essential else None,
        "mortality_modeled": False, "days_of_supply": None,
        "assumptions": [
            "All volumes are gallons; both supply and demand use the same conversion from the previous model.",
            "Essential planning demand is about 1.321 gallons/person-day: 0.793 drinking plus 0.528 essential cooking. Total routine domestic demand is about 5.283 gallons/person-day. These are scenario targets, not clinical survival thresholds.",
            "Inhabited places receive an explicitly provisional wells/springs and household-collection estimate even when no municipal workforce is recorded. Neither the existence nor yield of a particular well is confirmed.",
            "Raw freshwater, estimated usable/potable yield, collection capacity and actual delivery are distinct. Raw unsafe water is not counted as safe domestic supply.",
            "Municipal delivery and household/private collection share one finite usable-water pool. Essential use is allocated before other domestic use; water cannot be promised twice.",
            "Source footprints follow the permanent population and environment, not current tourist demand. Household collection follows residents present; visitors add food-day-equivalent water demand without creating sources.",
            "Cistern replenishment is counted once; storage inventories, water imports, aqueduct connections, treatment plants, sustained-shortage duration and mortality are not simulated.",
            "This is domestic water accounting, not a river-basin model or an irrigation, livestock and industrial-water budget. Collection productivity can represent improved distribution infrastructure without inventing new source water.",
            "Overrides represent scenarios, not automatically verified measurements. Source loss or contamination is applied after the baseline estimate and is never filled by a compensating viability allowance.",
        ],
    }
