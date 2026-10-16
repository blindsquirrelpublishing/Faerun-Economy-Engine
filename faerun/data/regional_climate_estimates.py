"""Unsourced climate-context fallback for unreviewed catalog settlements.

These are interpretations of the economy model's coarse class and zone tags,
not observations, canonical weather, or independently researched local climates.
The source-backed descriptions in ``data.climate`` always take precedence.
"""

from ..models import Settlement

# Planning language only: the engine class selects production calendars, not
# temperatures, rainfall, growing seasons at an individual city, or route access.
_CLASS_CONTEXT = {
    "cold": "A cold-climate planning category; local temperature and precipitation are unknown.",
    "temperate": "A temperate planning category; local temperature and precipitation are unknown.",
    "tropical": "A tropical planning category; local temperature and precipitation are unknown.",
    "arid": "An arid planning category; local temperature and precipitation are unknown.",
    "underdark": "An underground planning category; surface weather cannot be inferred for this location.",
}


def regional_climate_estimate(settlement: Settlement, engine_class: str) -> dict:
    """Describe modeled class/zone without asserting city-specific weather.

    Only call this for catalog settlements lacking a sourced climate entry and
    reviewed location lore. This function does not change simulation inputs.
    """
    context = _CLASS_CONTEXT.get(engine_class)
    if context is None:
        raise ValueError(f"Unknown model climate class: {engine_class}")
    return {
        "label": f"Modeled {engine_class} climate (estimate)",
        "summary": context,
        "seasons": [],
        "scope_note": (
            f"Derived from the economy model's {engine_class!r} class and "
            f"{settlement.zone!r} zone tags for {settlement.name}; not a sourced "
            "regional climate description or location-specific weather report."
        ),
        "calendar_note": (
            "The class selects modeled production calendars when enabled; no observed "
            "seasonal onset, temperature, precipitation, or local access is established."
        ),
        "sources": [],
        "status": "estimated",
        "era_note": (
            "Illustrative context for the 1492 DR planning baseline only; no historical "
            "climate evidence or 1492 DR weather has been reviewed for this estimate."
        ),
    }
