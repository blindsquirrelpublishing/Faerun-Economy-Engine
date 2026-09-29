"""One-time migration: dump the built-in Python catalogues to JSON files.

Run once with ``python tools/migrate_data_to_json.py``. After this the
``faerun/data/*.py`` modules load their catalogues from
``faerun/data/store/*.json`` instead of defining them as Python literals,
which lets the MCP server add, edit and remove entries at runtime.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

STORE = Path(__file__).resolve().parent.parent / "faerun" / "data" / "store"
STORE.mkdir(parents=True, exist_ok=True)


def dump(name: str, rows) -> None:
    path = STORE / f"{name}.json"
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {path} ({len(rows)} rows)")


def main() -> None:
    from faerun.data.commodities import COMMODITIES
    from faerun.data.settlements import SETTLEMENTS
    from faerun.data.businesses import BUSINESSES
    from faerun.data.routes import NAMED_ROUTES, NAMED_SEA_LANES

    commodities = [asdict(c) for c in COMMODITIES]
    dump("commodities", commodities)

    settlements = []
    for s in SETTLEMENTS:
        row = asdict(s)
        row.pop("population_basis", None)  # reattached specially for waterdeep
        row.pop("guilds", None)  # always inferred; explicit chapters unused today
        settlements.append(row)
    dump("settlements", settlements)

    businesses = [asdict(b) for b in BUSINESSES]
    dump("businesses", businesses)

    routes = [
        {"name": name, "stops": stops, "quality": quality, "kind": kind}
        for name, stops, quality, kind in NAMED_ROUTES
    ]
    dump("routes", routes)

    sea_lanes = []
    for lane in NAMED_SEA_LANES:
        name, stops, quality = lane[0], lane[1], lane[2]
        kind = lane[3] if len(lane) > 3 else None
        sea_lanes.append({"name": name, "stops": stops, "quality": quality, "kind": kind})
    dump("sea_lanes", sea_lanes)


if __name__ == "__main__":
    main()
