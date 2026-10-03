"""Source-backed gazetteer notes, kept separate from simulated market facts."""

from copy import deepcopy

from .data.lore import LORE, LORE_SOURCE_POLICY
from .models import Settlement


def location_lore(settlement: Settlement) -> dict:
    entry = deepcopy(LORE.get(settlement.id))
    industries = ", ".join(
        name.replace("_", " ") for name in sorted(settlement.industries)
    ) or "no recorded industries"
    context = (
        f"The economy model places {settlement.name} in {settlement.region}, "
        f"with {settlement.terrain.replace('_', ' ')} terrain and a modeled "
        f"population of {settlement.population:,}. Its industry profile includes "
        f"{industries}. These are simulation assumptions, not sourcebook statistics."
    )
    if entry is None:
        entry = {
            "status": "unresearched",
            "paragraphs": [],
            "sources": [],
            "era_note": "No web-researched lore has been verified for this location yet.",
        }
    entry["settlement_id"] = settlement.id
    entry["source_policy"] = deepcopy(LORE_SOURCE_POLICY)
    entry["model_context"] = context
    entry["existing_note"] = settlement.description
    return entry