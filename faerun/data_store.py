"""JSON-backed persistence for the editable catalogues.

The built-in commodity, settlement, business and route data used to be
literal Python lists inside ``faerun/data/*.py``. They now live as JSON rows
under ``faerun/data/store/`` so the MCP server (and anything else) can add,
edit or remove entries at runtime and have the change survive a restart.

Each ``load_*`` function reconstructs dataclass instances from the JSON rows;
each ``save_*`` function serializes the current in-memory rows back to disk,
atomically (write to a temp file, then replace).
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .models import Business, Commodity, Settlement

STORE_DIR = Path(__file__).resolve().parent / "data" / "store"


def _load_json(name: str) -> list:
    path = STORE_DIR / f"{name}.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_json(name: str, rows: list) -> None:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    path = STORE_DIR / f"{name}.json"
    tmp = path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    tmp.replace(path)


# ---------------------------------------------------------------------------
# Commodities
# ---------------------------------------------------------------------------

def load_commodities() -> List[Commodity]:
    return [Commodity(**row) for row in _load_json("commodities")]


def save_commodities(commodities: Iterable[Commodity]) -> None:
    _save_json("commodities", [asdict(c) for c in commodities])


# ---------------------------------------------------------------------------
# Settlements
# ---------------------------------------------------------------------------

def load_settlements() -> List[Settlement]:
    from .data.populations import WATERDEEP_POPULATION

    settlements = []
    for row in _load_json("settlements"):
        row = dict(row)
        row.pop("population_basis", None)
        row.pop("guilds", None)
        settlement = Settlement(**row)
        if settlement.id == "waterdeep":
            settlement.population_basis = WATERDEEP_POPULATION
        settlements.append(settlement)
    return settlements


def save_settlements(settlements: Iterable[Settlement]) -> None:
    rows = []
    for s in settlements:
        row = asdict(s)
        row.pop("population_basis", None)
        row.pop("guilds", None)
        rows.append(row)
    _save_json("settlements", rows)


# ---------------------------------------------------------------------------
# Businesses
# ---------------------------------------------------------------------------

def load_businesses() -> List[Business]:
    return [Business(**row) for row in _load_json("businesses")]


def save_businesses(businesses: Iterable[Business]) -> None:
    rows = []
    for b in businesses:
        row = asdict(b)
        row.pop("satellites", None)
        rows.append(row)
    _save_json("businesses", rows)


# ---------------------------------------------------------------------------
# Named routes and sea lanes
# ---------------------------------------------------------------------------
# Kept as (name, [stop ids], quality, kind) tuples so ``World._build_graph``
# needs no changes: it already reads ``NAMED_ROUTES``/``NAMED_SEA_LANES`` as
# plain tuples.

def load_routes() -> List[Tuple[str, List[str], float, str]]:
    return [
        (row["name"], list(row["stops"]), float(row["quality"]), row.get("kind") or "road")
        for row in _load_json("routes")
    ]


def save_routes(routes: Iterable[Tuple[str, List[str], float, str]]) -> None:
    rows = [
        {"name": name, "stops": list(stops), "quality": quality, "kind": kind}
        for name, stops, quality, kind in routes
    ]
    _save_json("routes", rows)


def load_sea_lanes() -> List[tuple]:
    lanes = []
    for row in _load_json("sea_lanes"):
        if row.get("kind"):
            lanes.append((row["name"], list(row["stops"]), float(row["quality"]), row["kind"]))
        else:
            lanes.append((row["name"], list(row["stops"]), float(row["quality"])))
    return lanes


def save_sea_lanes(lanes: Iterable[tuple]) -> None:
    rows = []
    for lane in lanes:
        name, stops, quality = lane[0], lane[1], lane[2]
        kind = lane[3] if len(lane) > 3 else None
        rows.append({"name": name, "stops": list(stops), "quality": quality, "kind": kind})
    _save_json("sea_lanes", rows)
