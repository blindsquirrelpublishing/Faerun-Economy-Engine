"""Climate shown in location details, kept apart from simulated market facts."""

from copy import deepcopy

from .data.climate import LOCAL_NOTES, REGIONAL_CLIMATES, SETTLEMENT_CLIMATES
from .data.lore import LORE
from .data.regional_climate_estimates import regional_climate_estimate
from .data.settlements import SETTLEMENTS_BY_ID
from .models import Settlement, slugify
from .seasonality import climate_for

ENGINE_NOTE = (
    "Model climate class: {name}. It selects regional production calendars when seasonal "
    "inventory is enabled and does not decide whether a settlement can produce a good."
)


def location_climate(settlement: Settlement, season: str = "") -> dict:
    engine_class = climate_for(settlement)
    entry = deepcopy(
        SETTLEMENT_CLIMATES.get(settlement.id) or REGIONAL_CLIMATES.get(slugify(settlement.zone))
    )
    if entry is None:
        if settlement.id in SETTLEMENTS_BY_ID and settlement.id not in LORE:
            entry = regional_climate_estimate(settlement, engine_class)
        else:
            entry = {
                "label": "",
                "summary": "",
                "seasons": [],
                "scope_note": "",
                "calendar_note": "",
                "sources": [],
                "status": "unresearched",
                "era_note": "No sourced climate description has been reviewed for this location yet.",
            }
    else:
        entry["status"] = "sourced"
        entry["era_note"] = ""
    entry["settlement_id"] = settlement.id
    entry["engine_class"] = engine_class
    entry["engine_note"] = ENGINE_NOTE.format(name=engine_class)
    entry["current_season"] = season
    entry["local_notes"] = deepcopy(LOCAL_NOTES.get(settlement.id, []))
    return entry
