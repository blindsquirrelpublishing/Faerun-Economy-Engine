"""Engine-facing location metadata, separate from market and sourced climate data."""

from copy import deepcopy
from importlib.resources import files
import json


_METADATA_FIELDS = (
    "id", "name", "summary", "evidence_reviewed", "identity", "periods",
    "position", "village_layout", "sketch", "maps", "additional_local_images",
    "collected_research", "sources", "copyright_note",
)


def location_metadata(settlement_id: str) -> dict | None:
    """Return the curated Red Larch record without exposing stale engine snapshots."""
    if settlement_id != "red_larch":
        return None
    resource = files("faerun.data").joinpath("red_larch_location.json")
    record = json.loads(resource.read_text(encoding="utf-8"))
    return deepcopy({key: record[key] for key in _METADATA_FIELDS})
