"""Transparent daily wage assumptions for the inferred labor model.

Values are scenario inputs, not canonical Forgotten Realms prices. Wages are
quoted in gp per worker-workday; the model separately tracks 365 calendar days
and 240 productive workdays per year.
"""

from __future__ import annotations

import math
from typing import Mapping

from .models import Settlement
from . import data_store

DAYS_PER_YEAR = 365.0
WORKDAYS_PER_YEAR = 240.0

# Baseline gp per productive worker-day at a common, reasonably safe market.
# Occupation ids not listed here use the closest transparent skill class below.
BASE_DAILY_WAGES: Mapping[str, float] = {
    "general": 0.325,
    "builders": 0.65,
    "carpenters": 0.975,
    "farms": 0.325,
    "fisheries": 0.4875,
    "bakeries": 0.585,
    "butchers": 0.65,
    "brewers": 0.65,
    "smiths": 0.975,
    "textiles": 0.585,
    "health": 1.4625,
    "logistics": 0.52,
    "sanitation": 0.39,
    "temples": 0.975,
    "arcane": 4.875,
    "garrison": 0.65,
    "forestry": 0.455,
    "extraction": 0.585,
    "health_service": 1.4625,
    "religion": 0.8125,
    "animals": 0.8125,
    "administration": 1.1375,
    "knowledge": 1.30,
    "commerce": 1.1375,
    "communications": 0.715,
    "hospitality": 0.52,
    "utilities": 0.39,
    "civil_security": 0.65,
    "maintenance": 0.8125,
    "culture": 0.975,
    "professional": 1.95,
}


def _load_wages() -> dict[str, float]:
    rows = data_store._load_json("wages")
    if not rows:
        return dict(BASE_DAILY_WAGES)
    return {str(row["id"]): float(row["daily_wage_gp"]) for row in rows}


DAILY_WAGES = _load_wages()


def list_wages() -> list[dict]:
    return [
        {"id": occupation_id, "daily_wage_gp": value,
         "occupation_class": occupation_class(occupation_id)}
        for occupation_id, value in sorted(DAILY_WAGES.items())
    ]


def create_wage(occupation_id: str, daily_wage: float) -> dict:
    occupation_id = occupation_id.strip()
    if not occupation_id or occupation_id in DAILY_WAGES:
        raise ValueError(f"Wage occupation {occupation_id!r} already exists or is invalid")
    value = _validate_wage(daily_wage)
    DAILY_WAGES[occupation_id] = value
    _save_wages()
    return next(row for row in list_wages() if row["id"] == occupation_id)


def update_wage(occupation_id: str, daily_wage: float) -> dict:
    if occupation_id not in DAILY_WAGES:
        raise ValueError(f"Unknown wage occupation: {occupation_id!r}")
    DAILY_WAGES[occupation_id] = _validate_wage(daily_wage)
    _save_wages()
    return next(row for row in list_wages() if row["id"] == occupation_id)


def delete_wage(occupation_id: str) -> bool:
    removed = DAILY_WAGES.pop(occupation_id, None) is not None
    if removed:
        _save_wages()
    return removed


def _validate_wage(value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("daily_wage must be finite and nonnegative")
    return value


def _save_wages() -> None:
    data_store._save_json(
        "wages", [{"id": key, "daily_wage_gp": value}
                  for key, value in sorted(DAILY_WAGES.items())]
    )


def _clamp(value: float, low: float, high: float) -> float:
    return min(high, max(low, float(value)))


def occupation_class(occupation_id: str) -> str:
    """Resolve dynamic occupation ids such as ``extraction_mine_iron``."""
    if occupation_id.startswith("extraction_"):
        return "extraction"
    return occupation_id if occupation_id in BASE_DAILY_WAGES else "general"


def location_wage_modifier(
    settlement: Settlement, worker_population: float, unallocated_workers: float,
) -> float:
    """Return the local multiplier for baseline wages.

    Prosperity raises reservation wages, a fully allocated labor pool adds
    scarcity pressure, and insecure markets pay a modest risk premium.
    """
    wealth_share = _clamp((float(settlement.wealth) - .65) / .75, 0.0, 1.0)
    prosperity = .75 + .60 * wealth_share
    pool = max(0.0, float(worker_population))
    utilization = 1.0 - _clamp(float(unallocated_workers) / pool, 0.0, 1.0) if pool else 0.0
    scarcity = 1.0 + .25 * utilization
    risk = 1.0 + .10 * (1.0 - _clamp(float(settlement.security), 0.0, 1.0))
    modifier = prosperity * scarcity * risk
    return round(modifier, 6)


def daily_wage_gp(occupation_id: str, modifier: float = 1.0) -> float:
    """Return the modeled wage for one productive worker-day."""
    value = DAILY_WAGES.get(occupation_id, DAILY_WAGES.get(occupation_class(occupation_id),
                                                            DAILY_WAGES["general"])) * float(modifier)
    if not math.isfinite(value) or value < 0:
        raise ValueError("daily wage must be finite and nonnegative")
    return round(value, 6)


def wage_assumptions() -> dict:
    return {
        "currency": "gp per productive worker-day",
        "workdays_per_year": WORKDAYS_PER_YEAR,
        "days_per_year": DAYS_PER_YEAR,
        "baseline_daily_wages_gp": dict(DAILY_WAGES),
        "location_modifier": (
            "baseline * prosperity(.75..1.35) * labor scarcity(1..1.25) * "
            "security risk(1..1.10); wealth is clamped at .65..1.40"
        ),
        "provenance": "Estimated economic scenario, not canon or a wage survey.",
    }
