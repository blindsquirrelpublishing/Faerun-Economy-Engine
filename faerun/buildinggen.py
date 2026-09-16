"""Seeded City System scenarios, never surveyed buildings or live-world actors."""

from collections import Counter
from copy import deepcopy
from dataclasses import asdict
import hashlib
import math
import random

from .census import CLASS_SHARES, CONDITION_MODIFIER, HOUSING_SCENARIOS, WARD_NAMES, HousingAssumptions
from .models import slugify


SOURCE = {
    "id": "city_system",
    "title": "City System",
    "publisher": "TSR",
    "publication_year": 1988,
    "local_path": r"volo\tsr01040 - AD&D_FR_-_City_System.pdf",
    "pdf_page_count": 130,
    "setting_year_dr": 1357,
    "citations": [
        {"printed_page": 10, "pdf_page": 11, "topic": "Classes, wards, stories and condition"},
        {"printed_page": 11, "pdf_page": 12, "topic": "Building uses"},
        {"printed_page": 4, "pdf_page": 5, "topic": "Setting year"},
    ],
    "era_note": "Historical 1357 DR generation rules, not an observed inventory or verified 1492 DR buildings.",
}

USES = {
    "warehouse": "Warehouse",
    "hoist_warehouse": "Warehouse with an internal hoist",
    "major_offices": "Major business offices",
    "rooming_house": "Rooming house",
    "shop_apartments": "Ground-floor shops with apartments above",
    "office_apartments": "Ground-floor offices with apartments above",
    "noble_family": "Noble family's residence",
    "noble_individual": "Noble individual's residence",
    "shop_offices": "Ground-floor shops with offices above",
    "shop_storage": "Large shop with storage above",
    "shop_mixed": "Ground-floor shops with offices and apartments above",
    "apartments": "Apartment building",
    "single_family": "Single-family dwelling",
    "shop": "Shop",
    "office": "Office",
    "shared_storage": "Dwelling sharing space with rental storage",
}
USE_ROLLS = {
    "B": ("hoist_warehouse", "hoist_warehouse", "major_offices", "major_offices",
          "rooming_house", "rooming_house", "shop_apartments", "office_apartments",
          "noble_family", "noble_individual"),
    "C": ("warehouse", "shop_offices", "shop_apartments", "shop_storage",
          "rooming_house", "rooming_house", "shop_mixed", "shop_mixed",
          "apartments", "apartments"),
    "D": ("warehouse", "warehouse", "warehouse", "warehouse", "single_family",
          "rooming_house", "shop", "office", "apartments", "shared_storage"),
}
CONDITIONS = (
    "Abandoned or boarded up", "Abandoned or boarded up",
    "Ramshackle; repairs needed", "Worn by heavy use", "Worn by heavy use",
    "Well maintained", "Well maintained", "Construction or major repairs",
    "New or recently refurbished", "New or recently refurbished",
)
MAX_BUILDINGS = 100
VERSION = 1
OCCUPANCY_ASSUMPTIONS = (
    "The shared low/central/high housing scenarios supply household size, unit area, usable area, occupancy and rooming-house resident shares.",
    "The entered footprint is an assumption applied to each building, not measured map area.",
    "Whole household-sized units are floored from usable residential floor area. Occupied units and people are rounded to the nearest integer, halves upward.",
    "Rooming-house units are assumed household-sized spaces, not enumerated hotel rooms; nonpermanent occupants are separate lodging guests.",
    "Upper mixed office/apartment floors split equally. Shared-storage dwellings allocate half their floors to housing.",
    "A noble individual or a shop proprietor living above is one resident; family dwellings use one household. Domestic servants are not independently counted.",
    "Normal staffing assumptions: two shop workers; two warehouse workers per story; three office workers per office-floor equivalent rounded up; two rooming-house staff.",
    "A nonresident shop/storage proprietor hires one night watchman in the source; other staff counts are modeling assumptions. Staff are not necessarily all present at once.",
    "Abandoned buildings and construction/major repairs are modeled unavailable with no usual occupants. Squatters, builders and repair crews are not enumerated.",
    "Staff can also be residents: do not add resident and staff counts to produce a population.",
    "Basements and unmeasured towers add no modeled housing. Existing lore names remain linked only to documented establishments, never assigned to random buildings.",
)


def _ward_id(ward: str) -> str:
    key = slugify(ward)
    names = {slugify(name): identifier for identifier, name in WARD_NAMES.items()}
    names.update({identifier: identifier for identifier in WARD_NAMES})
    names["south_ward"] = "south"
    if key not in names:
        raise ValueError(f"Unknown building-generation ward: {ward}")
    return names[key]


def _class_for_roll(ward: str, roll: int) -> str | None:
    if ward == "south":
        return ("B", "B", None, None, "C", "C", "C", "D", "D", "D")[roll - 1]
    threshold = 0
    for building_class, share in CLASS_SHARES[ward].items():
        threshold += round(share * 10)
        if roll <= threshold:
            return building_class
    raise ValueError(f"Incomplete class distribution for {ward}")


def _structure(building_class: str, roll: int) -> dict:
    if building_class == "B":
        return {"stories": (roll - 1) % 4 + 1, "basement": roll >= 5,
                "tower_or_partial_upper": roll == 8}
    if building_class == "C":
        return {"stories": (2, 3, 3, 2)[roll - 1], "basement": roll >= 3,
                "tower_or_partial_upper": False}
    return {"stories": 1, "basement": roll == 3, "tower_or_partial_upper": roll == 4}


def _occupants(use: str, stories: int, area: float, scenario: HousingAssumptions, available: bool,
               proprietor_lives_above: bool | None) -> dict:
    upper = max(0, stories - 1)
    residential_floors = {
        "rooming_house": stories, "shop_apartments": upper,
        "office_apartments": upper, "shop_mixed": upper * .5,
        "apartments": stories, "shared_storage": stories * .5,
    }.get(use, 0)
    unit_capacity = math.floor(area * residential_floors * scenario.usable_floor_share
                               / scenario.apartment_sqft)
    if use in {"single_family", "noble_family"}:
        unit_capacity = 1
    occupied_units = math.floor(unit_capacity * scenario.occupied_unit_share + .5) if available else 0
    residents = math.floor(occupied_units * scenario.household_size + .5)
    guests = 0
    if use == "rooming_house":
        permanent = math.floor(residents * scenario.rooming_permanent_share + .5)
        guests = residents - permanent
        residents = permanent
    if use == "noble_individual" or (use == "shop_storage" and proprietor_lives_above):
        residents = int(available)
    staff: dict[str, int] = {}
    if available:
        if use in {"warehouse", "hoist_warehouse"}:
            staff["Warehouse workers"] = 2 * stories
        if use in {"shop", "shop_apartments", "shop_offices", "shop_storage", "shop_mixed"}:
            staff["Shop workers"] = 2
        office_floors = {
            "office": stories, "major_offices": stories, "office_apartments": 1,
            "shop_offices": upper, "shop_mixed": upper * .5,
        }.get(use, 0)
        if office_floors:
            staff["Office workers"] = math.ceil(office_floors * 3)
        if use == "rooming_house":
            staff["Lodging staff"] = 2
        if use == "shop_storage" and proprietor_lives_above is False:
            staff["Night watchman"] = 1
    return {
        "basis": "modeled_counts_not_census",
        "residential_floor_equivalents": residential_floors,
        "household_sized_unit_capacity": unit_capacity,
        "occupied_household_sized_units": occupied_units,
        "residents": residents,
        "lodging_guests": guests,
        "staff": sum(staff.values()),
        "staff_roles": staff,
        "staff_may_overlap_residents": True,
        "named_people": [],
    }


def validate_building_options(count: int, seed: int, footprint_sqft: float,
                              scenario: str) -> HousingAssumptions:
    """Validate the shared limits and resolve occupancy assumptions."""
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= MAX_BUILDINGS:
        raise ValueError(f"count must be an integer from 1 to {MAX_BUILDINGS}")
    if isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed <= 4294967295:
        raise ValueError("seed must be an integer from 0 to 4294967295")
    if (isinstance(footprint_sqft, bool) or not isinstance(footprint_sqft, (int, float))
            or not math.isfinite(footprint_sqft) or not 1 <= footprint_sqft <= 1000000):
        raise ValueError("footprint_sqft must be finite and between 1 and 1,000,000")
    assumptions = next((a for a in HOUSING_SCENARIOS if a.name == scenario), None)
    if assumptions is None:
        raise ValueError("scenario must be low, central, or high")
    return assumptions


def roll_building_details(rng: random.Random, building_class: str, condition_modifier: int,
                          footprint_sqft: float, assumptions: HousingAssumptions) -> dict:
    """Apply shared source structure/use dice after a caller selects the class."""
    story_die = 8 if building_class == "B" else 4
    story_roll = rng.randint(1, story_die)
    condition_roll = rng.randint(1, 8)
    adjusted = condition_roll + condition_modifier
    use_roll = rng.randint(1, 10)
    use = USE_ROLLS[building_class][use_roll - 1]
    proprietor_roll = rng.randint(1, 4) if use == "shop_storage" else None
    lives_above = None if proprietor_roll is None else proprietor_roll % 2 == 0
    structure = _structure(building_class, story_roll)
    return {
        "status": "generated",
        "rolls": {
            "stories_die": story_die, "stories_roll": story_roll,
            "condition_d8": condition_roll, "condition_modifier": condition_modifier,
            "condition_adjusted": adjusted, "use_d10": use_roll,
            "proprietor_d4": proprietor_roll,
        },
        "structure": structure,
        "condition": CONDITIONS[adjusted],
        "use": {"id": use, "label": USES[use], "proprietor_lives_above": lives_above},
        "occupants": _occupants(use, structure["stories"], footprint_sqft, assumptions,
                               adjusted not in (0, 1, 7), lives_above),
        "warnings": ["Tower/partial upper area is unspecified and adds no modeled housing."]
                    if structure["tower_or_partial_upper"] else [],
    }


def summarize_buildings(buildings: list[dict]) -> dict:
    resolved = [b for b in buildings if b["occupants"] is not None]
    return {
        "buildings": len(buildings), "resolved_buildings": len(resolved),
        "unresolved_buildings": len(buildings) - len(resolved),
        "classes": dict(Counter(b["building_class"] or "unresolved" for b in buildings)),
        "modeled_residents_in_resolved_buildings": sum(b["occupants"]["residents"] for b in resolved),
        "modeled_guests_in_resolved_buildings": sum(b["occupants"]["lodging_guests"] for b in resolved),
        "modeled_staff_in_resolved_buildings": sum(b["occupants"]["staff"] for b in resolved),
        "city_population": None,
    }


def generate_buildings(
    ward: str = "Trades Ward", *, count: int = 20, seed: int = 1357,
    building_class: str | None = None, footprint_sqft: float = 1000,
    scenario: str = "central",
) -> dict:
    """Generate a bounded, repeatable scenario, not an expansion of the survey.

    Named people are never invented or inferred from a matching business type.
    Lore names stay attached only to their documented historical establishments.
    """
    ward_id = _ward_id(ward)
    if ward_id == "city_of_the_dead":
        raise ValueError("City of the Dead buildings are Class A and require individual authoring")
    assumptions = validate_building_options(count, seed, footprint_sqft, scenario)
    if building_class is not None:
        building_class = building_class.strip().upper()
        if building_class not in USE_ROLLS:
            raise ValueError("building_class must be B, C, or D; Class A requires individual authoring")

    buildings = []
    for index in range(count):
        identity = f"{VERSION}|{ward_id}|{seed}|{index}|{building_class}"
        digest = hashlib.sha256(identity.encode("ascii")).hexdigest()
        rng = random.Random(int(digest, 16))
        if building_class:
            class_roll = None
            selected_class = building_class
        else:
            class_roll = rng.randint(1, 10)
            selected_class = _class_for_roll(ward_id, class_roll)
        row = {
            "id": f"generated_{ward_id}_{digest[:16]}",
            "label": f"Generated {WARD_NAMES[ward_id]} building {index + 1}",
            "provenance": "generated_scenario",
            "ward": WARD_NAMES[ward_id],
            "building_class": selected_class,
            "class_basis": "user_choice" if building_class else "source_die_table",
            "rolls": {"class_d10": class_roll},
            "assumed_footprint_sqft": float(footprint_sqft),
            "map_position": None,
            "historical_business_id": None,
            "structure": None, "condition": None, "use": None, "occupants": None,
            "citations": deepcopy(SOURCE["citations"][:2]),
            "warnings": [],
        }
        if selected_class is None:
            row["status"] = "unresolved_source_roll"
            row["warnings"].append(
                "Southern Ward rolls 3-4 have no printed class. No reroll or normalization "
                "was applied; choose an explicit class to create a different scenario."
            )
        else:
            details = roll_building_details(
                rng, selected_class, CONDITION_MODIFIER[ward_id], footprint_sqft, assumptions,
            )
            row["rolls"].update(details.pop("rolls"))
            row.update(details)
        buildings.append(row)

    return {
        "schema_version": VERSION,
        "generated": True, "surveyed": False, "live_market_integration": False,
        "can_replace_population": False,
        "source": deepcopy(SOURCE),
        "parameters": {"ward": WARD_NAMES[ward_id], "count": count, "seed": seed,
                       "building_class": building_class, "footprint_sqft": float(footprint_sqft),
                       "scenario": scenario},
        "occupancy_scenario": asdict(assumptions),
        "assumptions": [
            "Every output is generated, not a mapped roof, historical establishment or known resident.",
            "Class, stories, condition and use follow the cited source dice. Class overrides are user choices.",
            *OCCUPANCY_ASSUMPTIONS,
            "These batches never enter the surveyed roof inventory, historical directory, live businesses, stock or resident population. Export JSON to retain a scenario.",
        ],
        "summary": summarize_buildings(buildings),
        "buildings": buildings,
    }
