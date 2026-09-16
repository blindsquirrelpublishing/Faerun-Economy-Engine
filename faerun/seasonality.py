"""Fictional harvest and consumption calendars, not canonical climate research.

Monthly weights describe daily rates relative to the annual daily baseline.
Festival days inherit their preceding month's rate; length-weighted
normalization therefore preserves exactly 365 baseline days of output/demand.
These helpers do not determine whether a settlement can produce a good.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Any, Sequence

from .calendar import FESTIVAL_MONTHS, HarptosDate, month_name
from .models import Commodity, Settlement, slugify

MONTH_LENGTHS = tuple(31 if month in FESTIVAL_MONTHS else 30 for month in range(1, 13))
_FLAT = (1.0,) * 12
_ZONE_CLIMATES = {
    "icewind": "cold",
    "silvermarches": "cold",
    "islands_north": "cold",
    "chult": "tropical",
    "halruaa": "tropical",
    "islands_south": "tropical",
    "anauroch": "arid",
    "calimshan": "arid",
    "mulhorand": "arid",
}


def climate_for(settlement: Settlement) -> str:
    """Resolve underground status, local traits/terrain, then zone, else temperate.

    Caverns are underground even in a hot surface zone. Explicit local climate
    traits override surface terrain/zone; jungle and desert are climate aliases.
    The broad Sword Coast North zone is not uniformly cold (e.g. Neverwinter).
    """
    traits = {slugify(trait) for trait in settlement.traits}
    terrain = slugify(settlement.terrain)
    zone = slugify(settlement.zone)
    if (settlement.underdark or terrain == "cavern" or "underdark" in traits
            or zone.startswith("underdark")):
        return "underdark"
    for climate, tags in (
        ("cold", {"cold", "tundra", "taiga"}),
        ("tropical", {"tropical", "jungle"}),
        ("arid", {"arid", "desert"}),
        ("temperate", {"temperate"}),
    ):
        if traits & tags:
            return climate
    if terrain in {"tundra", "taiga"}:
        return "cold"
    if terrain == "jungle":
        return "tropical"
    if terrain == "desert":
        return "arid"
    return _ZONE_CLIMATES.get(zone, "temperate")


@lru_cache(maxsize=512)
def _normalized(weights: tuple[float, ...]) -> tuple[float, ...]:
    if not weights:
        return _FLAT
    if len(weights) != 12:
        raise ValueError("expected 12 monthly weights (or [] for a flat profile)")
    if any(isinstance(weight, (str, bytes, bool)) for weight in weights):
        raise ValueError("monthly weights must be finite nonnegative numbers")
    values = tuple(float(weight) for weight in weights)
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("monthly weights must be finite and nonnegative")
    largest = max(values)
    if largest == 0:
        raise ValueError("monthly weights must not be all zero")
    # Scaling first avoids overflow even for valid weights near float's limit.
    scaled = tuple(value / largest for value in values)
    annual_weight = math.fsum(value * days for value, days in zip(scaled, MONTH_LENGTHS))
    return tuple(value * sum(MONTH_LENGTHS) / annual_weight for value in scaled)


def _profile(weights: Sequence[float], label: str) -> tuple[float, ...]:
    try:
        values = tuple(weights)
        # bool/int tuples compare equal as cache keys; reject types before lookup.
        if any(isinstance(value, (str, bytes, bool)) for value in values):
            raise ValueError("monthly weights must be finite nonnegative numbers")
        return _normalized(values)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{label}: {error}") from error


def _production_profile(commodity: Commodity, settlement: Settlement) -> tuple[float, ...]:
    """Prefer settlement id > region > zone > climate > base production profile.

    Keys accept gazetteer spelling or case/accent-insensitive underscore slugs.
    Exact keys win over equivalent slugs at each precedence level. An empty
    override deliberately means flat, rather than falling back to the base.
    Only the selected profile is evaluated; an override can replace the base.
    """
    overrides = commodity.regional_production_profiles
    if overrides:
        for key in (settlement.id, settlement.region, settlement.zone, climate_for(settlement)):
            if key in overrides:
                return _profile(overrides[key], f"{commodity.id} production profile [{key}]")
            normalized_key = slugify(key)
            for override_key, weights in overrides.items():
                if slugify(override_key) == normalized_key:
                    return _profile(weights, f"{commodity.id} production profile [{override_key}]")
    return _profile(commodity.production_profile, f"{commodity.id} production profile")


def production_multiplier(
    commodity: Commodity, settlement: Settlement, date: HarptosDate,
) -> float:
    """Return the applicable harvest/workshop daily multiplier for this month."""
    return _production_profile(commodity, settlement)[date.month - 1]


def demand_multiplier(commodity: Commodity, date: HarptosDate) -> float:
    """Return final-consumption seasonality, never the legacy seasonal price."""
    return _profile(commodity.demand_profile, f"{commodity.id} demand profile")[date.month - 1]


def seasonal_profile(
    commodity: Commodity, settlement: Settlement, date: HarptosDate,
) -> dict[str, Any]:
    """Return the resolved annual calendar and current rates/storage settings."""
    production = _production_profile(commodity, settlement)
    demand = _profile(commodity.demand_profile, f"{commodity.id} demand profile")
    return {
        "climate": climate_for(settlement),
        "months": [
            {
                "month": month,
                "name": month_name(month),
                "production_multiplier": production[month - 1],
                "demand_multiplier": demand[month - 1],
            }
            for month in range(1, 13)
        ],
        "production_multiplier": production[date.month - 1],
        "demand_multiplier": demand[date.month - 1],
        "storage_days": commodity.storage_days,
        "storage_loss": commodity.storage_loss,
        "reserve_days": commodity.reserve_days,
    }
