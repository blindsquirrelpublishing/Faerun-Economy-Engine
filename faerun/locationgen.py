"""Location-labeled City System adaptations, isolated from the live world."""

from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json
import random
import unicodedata

from .buildinggen import (
    OCCUPANCY_ASSUMPTIONS, SOURCE, roll_building_details,
    summarize_buildings, validate_building_options,
)
from .models import slugify


VERSION = 1


@dataclass(frozen=True)
class LocationProfile:
    id: str
    name: str
    description: str
    class_weights: tuple[int, int, int]
    condition_modifier: int = 0

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "class_weights": dict(zip("BCD", self.class_weights)),
            "basis": "engine_assumptions",
        }


_PROFILES = {
    p.id: p for p in (
        LocationProfile("village", "Village", "Mostly small Class D buildings; an urban-rule approximation, not a farm survey.", (0, 20, 80)),
        LocationProfile("town", "Town", "A mixture of small buildings and medium shops, housing and storage.", (10, 50, 40)),
        LocationProfile("city", "City", "More medium and large buildings, with mixed-use housing and businesses.", (30, 50, 20)),
        LocationProfile("port", "Port", "Small and medium waterfront-support buildings with a weathering assumption.", (10, 50, 40), -1),
        LocationProfile("fortress", "Fortress", "Ordinary supporting buildings only; the keep, walls and garrison require individual authoring.", (40, 40, 20), 1),
    )
}


def location_profiles() -> dict:
    """Return editable preset values as data, not destination-specific lore."""
    return {
        "schema_version": VERSION, "basis": "engine_assumptions",
        "profiles": [p.to_dict() for p in _PROFILES.values()],
    }


def _effective_profile(profile: str, weights: tuple[int | None, int | None, int | None],
                       condition_modifier: int | None) -> dict:
    key = profile.strip().lower() if isinstance(profile, str) else ""
    if key not in _PROFILES:
        raise ValueError("profile must be village, town, city, port, or fortress")
    preset = _PROFILES[key]
    if all(w is None for w in weights):
        effective_weights = preset.class_weights
    else:
        if any(isinstance(w, bool) or not isinstance(w, int) or not 0 <= w <= 100 for w in weights):
            raise ValueError("class_b_weight, class_c_weight and class_d_weight must all be integers from 0 to 100")
        # The explicit checks narrow optional values and keep custom mixes complete.
        b, c, d = weights
        assert b is not None and c is not None and d is not None
        effective_weights = (b, c, d)
        if sum(effective_weights) != 100:
            raise ValueError("class_b_weight, class_c_weight and class_d_weight must sum to 100")
    modifier = preset.condition_modifier if condition_modifier is None else condition_modifier
    if isinstance(modifier, bool) or not isinstance(modifier, int) or not -1 <= modifier <= 1:
        raise ValueError("condition_modifier must be an integer from -1 to 1")
    return {
        **preset.to_dict(),
        "class_weights": dict(zip("BCD", effective_weights)),
        "condition_modifier": modifier,
        "customized": effective_weights != preset.class_weights or modifier != preset.condition_modifier,
    }


def generate_location(
    location: str, *, profile: str = "town", count: int = 20, seed: int = 1357,
    footprint_sqft: float = 1000, scenario: str = "central",
    class_b_weight: int | None = None, class_c_weight: int | None = None,
    class_d_weight: int | None = None, condition_modifier: int | None = None,
) -> dict:
    """Generate a reproducible building batch for any existing or invented place.

    The label does not resolve, create or modify a world settlement. Class mixes
    and condition modifiers adapt urban source rules; no total population is fit.
    """
    if not isinstance(location, str):
        raise ValueError("location must be a nonblank name of at most 120 characters")
    name = unicodedata.normalize("NFC", " ".join(location.split()))
    if not name or len(name) > 120 or not name.isprintable():
        raise ValueError("location must be a printable, nonblank name of at most 120 characters")
    effective = _effective_profile(
        profile, (class_b_weight, class_c_weight, class_d_weight), condition_modifier,
    )
    assumptions = validate_building_options(count, seed, footprint_sqft, scenario)
    normalized = name.casefold()
    name_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    location_id = f"{slugify(name) or 'location'}_{name_hash}"
    weights = effective["class_weights"]
    modifier = effective["condition_modifier"]
    buildings = []
    for index in range(count):
        identity = json.dumps(
            [VERSION, normalized, effective["id"], weights, modifier, seed, index],
            sort_keys=True, ensure_ascii=False,
        )
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        rng = random.Random(int(digest, 16))
        class_roll = rng.randint(1, 100)
        building_class = "B" if class_roll <= weights["B"] else (
            "C" if class_roll <= weights["B"] + weights["C"] else "D"
        )
        details = roll_building_details(rng, building_class, modifier, footprint_sqft, assumptions)
        details["rolls"]["class_d100"] = class_roll
        buildings.append({
            "id": f"generated_location_{digest[:24]}",
            "label": f"Generated {name} building {index + 1}",
            "location_id": location_id, "location_name": name, "ward": None,
            "provenance": "generated_scenario",
            "building_class": building_class, "class_basis": "profile_assumption",
            "assumed_footprint_sqft": float(footprint_sqft),
            "map_position": None, "historical_business_id": None,
            "citations": deepcopy(SOURCE["citations"][:2]),
            **details,
        })
    return {
        "schema_version": VERSION,
        "generated": True, "surveyed": False, "live_market_integration": False,
        "can_replace_population": False,
        "location": {"id": location_id, "name": name, "basis": "user_supplied_label"},
        "profile": effective,
        "parameters": {
            "location": name, "profile": effective["id"], "count": count, "seed": seed,
            "footprint_sqft": float(footprint_sqft), "scenario": scenario,
            "class_b_weight": weights["B"], "class_c_weight": weights["C"],
            "class_d_weight": weights["D"], "condition_modifier": modifier,
        },
        "source": deepcopy(SOURCE),
        "occupancy_scenario": asdict(assumptions),
        "assumptions": [
            "The location is a user-supplied label, not a verified settlement lookup or a newly created live location.",
            "Village/town/city/port/fortress class percentages and condition modifiers are configurable engine assumptions, not printed source tables or lore about this location.",
            "Class percentages use a modeled d100 selection. City System supplies the B/C/D story dice, building-use tables, condition meanings and proprietor rule.",
            "Urban use tables are reused even for rural and fortress profiles; farms, terrain, streets, local industries and architectural traditions are not independently modeled.",
            "Class A civic, religious and noble institutions need individual authoring. A fortress profile does not generate the keep, walls, soldiers or a garrison census.",
            "Each batch is a scenario, not the full location: building count is selected, not inferred from population or unsurveyed map area.",
            *OCCUPANCY_ASSUMPTIONS,
            "Seed and normalized location/profile/configuration determine buildings. Count extensions preserve the existing prefix; footprint and occupancy changes hold the building dice fixed.",
            "No invented names or automatic lore affiliations. No generated roads, map coordinates or historical businesses are asserted.",
            "Generated batches never change the live economy, population, historical directory or map survey. Download JSON to retain a scenario.",
        ],
        "summary": summarize_buildings(buildings),
        "buildings": buildings,
    }
