"""Gazetteer of Faerûnian markets.

Coordinates are approximate map miles: x increases eastward from the Trackless
Sea, y increases southward from the Sea of Moving Ice.  They are used for
trade-route distance, so they are tuned for plausible travel times rather than
cartographic perfection.

`port` names the sea basin a settlement trades on; ports in the same basin can
be linked by sea lanes.
"""

from __future__ import annotations

from ..calibration import apply_calibration
from ..data_store import load_settlements

WEST = "Sea of Swords"          # west coast, Shining Sea, Trackless Sea
INNER = "Sea of Fallen Stars"   # the Inner Sea and its coasts
MOONSEA = "Moonsea"
STEAM = "Lake of Steam"

# Editable at runtime via the MCP server's settlement tools; rows are
# persisted to faerun/data/store/settlements.json rather than defined here.
SETTLEMENTS = load_settlements()

# If the map screen has been calibrated against a published poster map, the
# saved control points warp every settlement into place before anything else
# reads a coordinate. Uncalibrated installs are untouched.
CALIBRATION_POINTS = apply_calibration(SETTLEMENTS)

SETTLEMENTS_BY_ID = {s.id: s for s in SETTLEMENTS}

# Zones that share land borders; auto-generated caravan roads only link
# settlements within a zone or between adjacent zones.
ZONE_ADJACENCY = {
    "icewind": {"swordcoast_north"},
    "swordcoast_north": {"icewind", "dessarin", "silvermarches", "waterdeep"},
    "silvermarches": {"swordcoast_north", "dessarin", "anauroch"},
    "dessarin": {"swordcoast_north", "waterdeep", "silvermarches", "westernheartlands"},
    "waterdeep": {"dessarin", "swordcoast_north", "westernheartlands", "baldursgate"},
    "westernheartlands": {"waterdeep", "baldursgate", "dessarin", "amn", "dragoncoast",
                          "anauroch", "silvermarches"},
    "baldursgate": {"waterdeep", "westernheartlands", "amn"},
    "amn": {"baldursgate", "tethyr", "westernheartlands"},
    "tethyr": {"amn", "calimshan"},
    "calimshan": {"tethyr", "lakeofsteam"},
    "lakeofsteam": {"calimshan", "vilhon", "halruaa", "chult"},
    "halruaa": {"lakeofsteam", "chult"},
    "chult": {"halruaa", "lakeofsteam"},
    "vilhon": {"lakeofsteam", "turmish", "dragoncoast", "chessenta"},
    "turmish": {"vilhon"},
    "dragoncoast": {"vilhon", "cormyr", "westernheartlands", "sembia"},
    "cormyr": {"dragoncoast", "dales", "sembia", "anauroch"},
    "dales": {"cormyr", "sembia", "moonsea"},
    "sembia": {"cormyr", "dales", "dragoncoast", "vast"},
    "moonsea": {"dales", "vast", "thesk", "anauroch"},
    "vast": {"sembia", "moonsea", "impiltur"},
    "impiltur": {"vast", "thesk", "moonsea"},
    "thesk": {"impiltur", "thay", "aglarond", "moonsea"},
    "thay": {"thesk", "aglarond", "mulhorand"},
    "aglarond": {"thesk", "thay", "chessenta"},
    "chessenta": {"unther", "vilhon", "aglarond"},
    "unther": {"chessenta", "mulhorand"},
    "mulhorand": {"unther", "thay"},
    "anauroch": {"silvermarches", "cormyr", "moonsea", "westernheartlands"},
    "underdark_north": {"underdark_south"},
    "underdark_south": {"underdark_north"},
}
