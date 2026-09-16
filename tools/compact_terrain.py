"""Convert a detailed FPS terrain export to compact row strings."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import ijson


LETTERS = {
    "sea": "S",
    "inland_water": "W",
    "plains": "P",
    "cleared_mixed": "C",
    "forest": "F",
    "jungle": "J",
    "hills": "H",
    "mountains": "M",
    "wetland": "T",
    "moor": "O",
    "sandy_desert": "D",
    "rocky_desert": "R",
    "ice_glacier": "I",
    "unknown": "U",
    "excluded": "X",
}


def compact(source: Path, destination: Path) -> dict[str, object]:
    opener = gzip.open if source.suffix == ".gz" else open
    rows: dict[int, dict[int, str]] = {}
    with opener(source, "rb") as stream:
        for cell in ijson.items(stream, "cells.item"):
            column = int(cell["column"])
            row = int(cell["row"])
            terrain = str(cell.get("dominant_terrain") or "unknown")
            rows.setdefault(row, {})[column] = LETTERS.get(terrain, "U")

    if not rows:
        raise ValueError(f"No terrain cells found in {source}")
    column_min = min(min(columns) for columns in rows.values())
    column_max = max(max(columns) for columns in rows.values())
    row_min = min(rows)
    row_max = max(rows)
    width = column_max - column_min + 1
    compact_rows = {
        str(row): "".join(
            rows.get(row, {}).get(column, "U")
            for column in range(column_min, column_max + 1)
        )
        for row in range(row_min, row_max + 1)
    }
    payload: dict[str, object] = {
        "format": "faerun-terrain-simple-v1",
        "description": "Compact five-mile terrain cells for lazy local map detail.",
        "frame": "FPS1:WD",
        "origin": "Waterdeep",
        "cell_miles": 5,
        "column_min": column_min,
        "column_max": column_max,
        "row_min": row_min,
        "row_max": row_max,
        "width": width,
        "height": row_max - row_min + 1,
        "cell_count": width * (row_max - row_min + 1),
        "legend": {letter: terrain for terrain, letter in LETTERS.items()},
        "rows": compact_rows,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    payload = compact(args.source, args.destination)
    print(
        f"Wrote {payload['width']} x {payload['height']} five-mile cells "
        f"to {args.destination}"
    )


if __name__ == "__main__":
    main()