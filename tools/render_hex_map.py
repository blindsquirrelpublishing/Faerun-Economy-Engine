"""Render the one-mile terrain survey as a hex grid, at poster resolution.

Whole sheet at eight pixels to the mile (30368 x 20312, about 600 megapixels):

    .\\.venv\\Scripts\\python.exe tools\\render_hex_map.py

One region, larger, for printing or close reading:

    .\\.venv\\Scripts\\python.exe tools\\render_hex_map.py --center 0,0 --radius 150 --scale 24

Hexes are sized by area, not by width: a hexagon of exactly one square mile is
1.0746 miles flat-to-flat and 1.2408 miles point to point, so the lattice is
not square and a hex does not line up with a survey cell. Each hex takes the
terrain of the survey cell its centre lands in.

The image is built a strip at a time and written as a palette PNG. At eight
pixels to the mile a full-colour buffer would be 1.9 GB where a palette one is
620 MB, and the terrain vocabulary is nine colours plus a grid line.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parents[1]
SURVEY = ROOT / "maps" / "terrain-1-mile.json"
OUTPUT = ROOT / "maps" / "terrain-1-mile-review"

#: Side of a hexagon whose area is one square mile.
HEX_SIDE = math.sqrt(2.0 / (3.0 * math.sqrt(3.0)))
ROOT3 = math.sqrt(3.0)

COLOURS = {
    "S": (94, 150, 196),
    "W": (128, 190, 226),
    "P": (232, 223, 195),
    "G": (198, 210, 152),
    "F": (104, 138, 88),
    "H": (192, 166, 124),
    "M": (140, 118, 110),
    "T": (156, 178, 160),
    "D": (232, 206, 146),
    "I": (238, 244, 250),
    "U": (245, 245, 245),
}
GRID_COLOUR = (70, 70, 74)
STRIP_ROWS = 256


def load_survey() -> Tuple[np.ndarray, dict]:
    """The survey as a letter-index grid, north-first, plus its metadata."""
    payload = json.loads(SURVEY.read_text(encoding="utf-8"))
    letters = "".join(sorted(payload["legend"]))
    lookup = np.full(128, len(letters), np.uint8)
    for index, letter in enumerate(letters):
        lookup[ord(letter)] = index
    height = payload["row_max"] - payload["row_min"] + 1
    width = payload["column_max"] - payload["column_min"] + 1
    grid = np.empty((height, width), np.uint8)
    for offset in range(height):
        row = payload["rows"][str(payload["row_max"] - offset)]
        grid[offset] = lookup[np.frombuffer(row.encode("ascii"), np.uint8)]
    return grid, {"letters": letters, "payload": payload}


def hex_of(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Axial coordinates of the pointy-top hex containing each point."""
    q = (ROOT3 / 3.0 * x - y / 3.0) / HEX_SIDE
    r = (2.0 / 3.0 * y) / HEX_SIDE
    # Cube rounding: round all three, then fix up whichever moved furthest.
    cx, cz = q, r
    cy = -cx - cz
    rx, ry, rz = np.rint(cx), np.rint(cy), np.rint(cz)
    dx, dy, dz = np.abs(rx - cx), np.abs(ry - cy), np.abs(rz - cz)
    swap_x = (dx > dy) & (dx > dz)
    swap_z = ~swap_x & (dz > dy)
    rx = np.where(swap_x, -ry - rz, rx)
    rz = np.where(swap_z, -rx - ry, rz)
    return rx, rz


def hex_centre(q: np.ndarray, r: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    return (HEX_SIDE * (ROOT3 * q + ROOT3 / 2.0 * r), HEX_SIDE * 1.5 * r)


def render(grid: np.ndarray, meta: dict, c0: int, c1: int, r0: int, r1: int,
           scale: int, destination: Path) -> Tuple[int, int]:
    payload = meta["payload"]
    letters = meta["letters"]
    column_min = payload["column_min"]
    row_max = payload["row_max"]
    height_cells = r1 - r0 + 1
    width_cells = c1 - c0 + 1
    width = width_cells * scale
    height = height_cells * scale

    palette = bytearray(768)
    for index, letter in enumerate(letters):
        palette[index * 3:index * 3 + 3] = bytes(COLOURS.get(letter, (255, 0, 255)))
    grid_index = len(letters)
    palette[grid_index * 3:grid_index * 3 + 3] = bytes(GRID_COLOUR)

    canvas = np.empty((height, width), np.uint8)
    columns = (np.arange(width, dtype=np.float32) + 0.5) / scale
    # Survey rows are north-first, and so is the image.
    north_offset = row_max - r1
    west_offset = c0 - column_min

    for top in range(0, height, STRIP_ROWS):
        bottom = min(height, top + STRIP_ROWS)
        # A one-pixel skirt so a hex edge can be found by comparison.
        lo = max(0, top - 1)
        hi = min(height, bottom + 1)
        ys = (np.arange(lo, hi, dtype=np.float32) + 0.5) / scale
        x = np.broadcast_to(columns, (hi - lo, width))
        y = ys[:, None]

        q, r = hex_of(x + west_offset, y + north_offset)
        cx, cy = hex_centre(q, r)
        column = np.clip(np.floor(cx).astype(np.int32), 0, grid.shape[1] - 1)
        row = np.clip(np.floor(cy).astype(np.int32), 0, grid.shape[0] - 1)
        block = grid[row, column]

        edge = np.zeros(block.shape, bool)
        edge[:, 1:] |= (q[:, 1:] != q[:, :-1]) | (r[:, 1:] != r[:, :-1])
        edge[1:, :] |= (q[1:, :] != q[:-1, :]) | (r[1:, :] != r[:-1, :])
        block = np.where(edge, grid_index, block).astype(np.uint8)
        canvas[top:bottom] = block[top - lo:top - lo + (bottom - top)]

    image = Image.fromarray(canvas, mode="P")
    image.putpalette(bytes(palette))
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, optimize=False, compress_level=6)
    return width, height


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=int, default=8,
                        help="pixels per mile (8 makes a hex about 9px across)")
    parser.add_argument("--center", default=None,
                        help="region centre as one-mile column,row from Waterdeep")
    parser.add_argument("--radius", type=int, default=150)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if not SURVEY.is_file():
        raise SystemExit(f"survey not found: {SURVEY}")
    grid, meta = load_survey()
    payload = meta["payload"]

    if args.center:
        column, row = (int(part) for part in args.center.split(","))
        c0 = max(payload["column_min"], column - args.radius)
        c1 = min(payload["column_max"], column + args.radius)
        r0 = max(payload["row_min"], row - args.radius)
        r1 = min(payload["row_max"], row + args.radius)
        name = f"hex-{column}-{row}-x{args.scale}.png"
    else:
        c0, c1 = payload["column_min"], payload["column_max"]
        r0, r1 = payload["row_min"], payload["row_max"]
        name = f"hex-whole-x{args.scale}.png"

    destination = args.output or (OUTPUT / name)
    miles_across = c1 - c0 + 1
    miles_down = r1 - r0 + 1
    hexes = round(miles_across / (ROOT3 * HEX_SIDE) * miles_down / (1.5 * HEX_SIDE))
    print(f"{miles_across} x {miles_down} miles, about {hexes:,} one-square-mile hexes")
    print(f"rendering {miles_across * args.scale:,} x {miles_down * args.scale:,} "
          f"px ({miles_across * args.scale * miles_down * args.scale / 1e6:,.0f} Mpx)")

    width, height = render(grid, meta, c0, c1, r0, r1, args.scale, destination)
    size = destination.stat().st_size / 1e6
    print(f"wrote {width:,} x {height:,} px, {size:,.1f} MB to {destination}")


if __name__ == "__main__":
    main()
