"""Racial makeup shown in location details, kept apart from simulated market facts."""

from copy import deepcopy

from .data.demographics import SETTLEMENT_DEMOGRAPHICS, unresearched
from .models import Settlement

MODEL_NOTE = (
    "The model's population of {population:,} is not divided by race. This makeup is "
    "reference or illustrative scenario data and does not change workers, demand, production or prices."
)


def location_demographics(settlement: Settlement) -> dict:
    entry = deepcopy(SETTLEMENT_DEMOGRAPHICS.get(settlement.id) or unresearched())
    entry["settlement_id"] = settlement.id
    entry["model_note"] = MODEL_NOTE.format(population=settlement.population)
    return entry
