"""Seed the island regions: outline each island from the 5-mile terrain grid.

Run from the repository root::

    python tools/seed_island_regions.py            # preview only
    python tools/seed_island_regions.py --write    # save to faerun/data/store/regions.json

The outlines are a starting point for editing on the map, not surveyed
borders.  A region whose border has already been edited by hand
(``border_source == "manual"``) keeps its polygons; only its profile is
refreshed.
"""
from __future__ import annotations

import argparse
import math
import sys
from collections import deque
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from faerun import mapdata, regions  # noqa: E402
from faerun.coast import fit_ring_to_coast  # noqa: E402
from faerun.territory import outer_loops, simplify_closed  # noqa: E402
from faerun.world import get_world  # noqa: E402

WATER = frozenset("SWUX")
SEARCH_MILES = 60.0
MAX_ISLAND_CELLS = 2500
SIMPLIFY_MILES = 2.5
SEA_BUFFER_MILES = 10.0

PROFILES: Dict[str, Dict[str, object]] = {
    "Lantan": {
        "seeds": ["sundrah", "nemesser"],
        "kind": "island_nation",
        "landmasses": ["lantan"],
        "trade_dependence": "isolationist",
        "summary": ("Gnomish island nation of inventors and artificers. It sells precision "
                    "goods and guards its formulae; foreign trade is channelled through a few "
                    "licensed harbours."),
        "industries": {"alch": 2.0, "craft": 3.0, "glass": 2.0},
        "exports": ["lantan_clockwork", "farseer_lens", "smokepowder"],
        "imports": ["iron_ingot", "coal", "grain"],
        "notes": ("The Lantan hub itself is not in the settlement catalog; Nemesser and Sundrah "
                  "are surveyed markets inferred from it."),
    },
    "Nimbral": {
        "seeds": ["nimbral"],
        "fallback_radius_miles": 30.0,
        "kind": "island_nation",
        "landmasses": ["nimbral"],
        "trade_dependence": "import_dependent",
        "summary": ("Shadow-veiled magocracy of illusionists. Arcane goods and fine wine go "
                    "out; metal, fuel and grain must come in by sea."),
        "industries": {"alch": 2.0, "arcane": 3.0, "craft": 2.0, "vint": 2.0},
        "exports": ["cloudsilk", "illusionists_veil", "reagents_rare", "wine_fine"],
        "imports": ["iron_ingot", "coal", "grain"],
        "notes": ("Fort Beluarian and Sambar carry the Nimbral label but sit far from the "
                  "island; the border report lists them as outside it."),
    },
    "Moonshae Isles": {
        "seeds": ["caer_calidyrr", "caer_corwell", "iron_keep", "llewellyn"],
        "kind": "island_nation",
        "landmasses": ["moonshae"],
        "trade_dependence": "mixed",
        "summary": ("Pastoral, druid-guarded island kingdoms. Wool, cheese and salt fish "
                    "feed the Sword Coast; iron, silk and spice come back in exchange."),
        "industries": {"farm": 3.0, "fish": 3.0, "herd": 3.0, "brew": 2.0},
        "exports": ["wool", "cheese", "fish_salt"],
        "imports": ["iron_ingot", "silk", "spices_exotic"],
    },
    "Sea of Swords": {
        "seeds": ["mintarn", "orlumbor"],
        "kind": "island_nation",
        "landmasses": ["mintarn", "orlumbor"],
        "trade_dependence": "sea_dependent",
        "summary": ("Free-port islands of mercenaries, shipwrights and smugglers. Ships, "
                    "sailcloth and hired swords go out; grain and produce arrive by sea."),
        "industries": {"merc": 3.0, "ship": 3.0, "fish": 3.0, "trade": 2.0},
        "exports": ["ship_boat", "sailcloth", "fish_salt"],
        "imports": ["grain", "vegetables", "fruit"],
    },
    "Trackless Sea": {
        "seeds": ["ruathym"],
        "kind": "island_nation",
        "landmasses": ["ruathym"],
        "trade_dependence": "import_dependent",
        "summary": ("Northmen raider island. Whale oil, amber and longships go out; grain, "
                    "fruit and wine must be bought or taken."),
        "industries": {"whale": 2.0, "fish": 3.0, "ship": 3.0, "amber": 2.0},
        "exports": ["whale_oil", "amber", "fish_salt"],
        "imports": ["grain", "fruit", "wine_common"],
    },
}


def _cell(grid: Dict[str, object], column: int, row: int) -> str:
    rows = grid["rows"]
    line = rows.get(str(row)) if isinstance(rows, dict) else None
    offset = column - int(grid["column_min"])
    if not isinstance(line, str) or not 0 <= offset < len(line):
        return "S"
    return line[offset]


def _is_land(grid, column: int, row: int) -> bool:
    return _cell(grid, column, row) not in WATER


def _nearest_land(grid, column: int, row: int, reach: int):
    best = None
    for dc in range(-reach, reach + 1):
        for dr in range(-reach, reach + 1):
            distance = math.hypot(dc, dr)
            if distance <= reach and _is_land(grid, column + dc, row + dr):
                if best is None or distance < best[0]:
                    best = (distance, column + dc, row + dr)
    return best and (best[1], best[2])


def _flood(grid, start) -> Set[Tuple[int, int]]:
    seen = {start}
    queue = deque([start])
    while queue and len(seen) <= MAX_ISLAND_CELLS:
        column, row = queue.popleft()
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                nxt = (column + dc, row + dr)
                if nxt not in seen and _is_land(grid, *nxt):
                    seen.add(nxt)
                    queue.append(nxt)
    return seen


def _simplified_ring(loop, cell_miles: float, origin) -> List[List[float]]:
    points = [(c * cell_miles, r * cell_miles) for c, r in loop]
    tolerance = SIMPLIFY_MILES
    while tolerance >= 0.2:
        ring = simplify_closed(points, tolerance)
        world = [[origin[0] + east, origin[1] - north] for east, north in ring]
        if len(world) >= 3 and not regions.ring_self_intersects(world):
            return world
        tolerance /= 2.0
    return [[origin[0] + e, origin[1] - n] for e, n in points]


def trace_island(grid, world, seed_ids: Iterable[str], avoid=()):
    waterdeep = world.find_settlement("Waterdeep")
    cell_miles = float(grid["cell_miles"])
    origin = (float(waterdeep.x), float(waterdeep.y))
    claimed: Set[Tuple[int, int]] = set()
    rings: List[List[List[float]]] = []
    notes: List[str] = []
    for seed in seed_ids:
        settlement = world.settlements[seed]
        column = math.floor((settlement.x - origin[0]) / cell_miles)
        row = math.floor((origin[1] - settlement.y) / cell_miles)
        start = _nearest_land(grid, column, row, int(SEARCH_MILES / cell_miles))
        if start is None:
            notes.append("%s: no land within %d miles" % (settlement.name, SEARCH_MILES))
            continue
        if start in claimed:
            continue
        cells = _flood(grid, start)
        if len(cells) > MAX_ISLAND_CELLS:
            notes.append("%s: land is connected to a continent; skipped" % settlement.name)
            continue
        claimed |= cells
        for loop in outer_loops(cells):
            ring = _simplified_ring(loop, cell_miles, origin)
            if regions.ring_area(ring) >= cell_miles * cell_miles * 0.9:
                # Redraw the coarse 5-mile outline along the one-mile coastline,
                # with the sea buffer built into the polygon.
                rings.extend(fit_ring_to_coast(ring, origin, buffer_miles=SEA_BUFFER_MILES, avoid=avoid) or [ring])
        notes.append("%s: %d cells, %d vertices" % (settlement.name, len(cells), sum(len(r) for r in rings)))
    return rings, notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="save the regions to the store")
    args = parser.parse_args()
    world = get_world()
    grid = mapdata._detail_grid()
    if not grid:
        print("terrain-5-mile.json is not installed", file=sys.stderr)
        return 1
    commodities = set(world.commodities)
    for name, spec in PROFILES.items():
        spec = dict(spec)
        seeds = spec.pop("seeds")
        fallback = spec.pop("fallback_radius_miles", None)
        others = [ring for region in regions.load_regions()[1] if not region.matches_label(name)
                  for ring in region.borders]
        rings, notes = trace_island(grid, world, seeds, others)
        source = "terrain-seed"
        if not rings and fallback:
            # Off the end of the terrain survey: a rough circle to edit on the map.
            centre = world.settlements[seeds[0]]
            rings = [[[round(centre.x + fallback * math.cos(a * math.pi / 6), 2),
                       round(centre.y + fallback * math.sin(a * math.pi / 6), 2)] for a in range(12)]]
            source = "placeholder"
            notes.append("outside the terrain survey; placeholder circle of %.0f miles" % fallback)
        existing = regions.find_region(name)
        keep_manual = bool(existing and existing.border_source == "manual" and existing.borders)
        print("%s: %d polygon(s), %.0f sq mi%s" % (
            name, len(rings), sum(regions.ring_area(r) for r in rings),
            " (kept manual border)" if keep_manual else ""))
        for note in notes:
            print("   ", note)
        if args.write:
            values = dict(spec, name=name)
            if not keep_manual:
                values.update(borders=rings, border_source=source)
                if source == "terrain-seed":
                    values["sea_margin_miles"] = 0.0     # the polygon already includes its sea buffer
            regions.upsert_region(name, values, commodities=commodities)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
