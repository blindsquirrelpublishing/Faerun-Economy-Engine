"""Fit region polygons to the mapped coastline.

The polygon a person draws, or one traced from the 5-mile terrain grid, wanders a
few miles either side of the shore.  ``fit_ring_to_coast`` redraws it along the
coast the map actually shows, using the one-mile terrain survey where it
reaches and the five-mile grid elsewhere:

* sea inside the polygon is cut away, so the outline stops at the shoreline;
* coastal land within ``snap_miles`` of the polygon is taken in, so a polygon
  drawn short of the shore grows out to it;
* only land that is joined to the polygon's own land is kept, so a neighbouring
  island a few miles away is never absorbed;
* inland edges, the political borders, are left where they were drawn;
* optionally the outline is pushed out over the sea by a buffer (ten miles for an
  island nation), smoothed, and kept off other regions' polygons so neighbours
  butt up instead of overlapping.
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from . import mapdata
from .regions import distance_to_ring, point_in_ring, ring_area, ring_self_intersects
from .territory import _distance_field, _fill_land, outer_loops, simplify_closed, smooth_ring

LAND = frozenset("PCGFJHMTODRI")
WATER = frozenset("SW")
DEFAULT_SNAP_MILES = 6.0
MAX_SNAP_MILES = 40.0
DEFAULT_BUFFER_MILES = 10.0
MAX_BUFFER_MILES = 100.0
BUFFER_SMOOTH_MILES = 4.0
COAST_BAND_MILES = 3.0
MAX_GRID = 450
MIN_LAND_SQUARE_MILES = 10.0


def _grids() -> List[Dict[str, Any]]:
    return [grid for grid in (mapdata._fine_grid(), mapdata._detail_grid()) if grid]


def _letter(grid: Dict[str, Any], east: float, north: float) -> str:
    size = float(grid["cell_miles"])
    column = math.floor(east / size)
    row = math.floor(north / size)
    if not (int(grid["column_min"]) <= column <= int(grid["column_max"])
            and int(grid["row_min"]) <= row <= int(grid["row_max"])):
        return ""
    line = grid["rows"].get(str(row))
    offset = column - int(grid["column_min"])
    return line[offset] if isinstance(line, str) and 0 <= offset < len(line) else ""


def _state(grids: Sequence[Dict[str, Any]], x: float, y: float, origin: Tuple[float, float]) -> int:
    """1 land, 0 water, -1 not surveyed."""
    east, north = x - origin[0], origin[1] - y
    for grid in grids:
        letter = _letter(grid, east, north)
        if letter in LAND:
            return 1
        if letter in WATER:
            return 0
    return -1


def _bounds_of(ring: Sequence[Sequence[float]]) -> Tuple[float, float, float, float]:
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


def fit_ring_to_coast(ring: Sequence[Sequence[float]], origin: Tuple[float, float],
                      snap_miles: float = DEFAULT_SNAP_MILES,
                      grids: Optional[Sequence[Dict[str, Any]]] = None,
                      buffer_miles: float = 0.0,
                      avoid: Sequence[Sequence[Sequence[float]]] = ()) -> List[List[List[float]]]:
    """Return the polygon(s) that follow the coast around ``ring``.

    ``origin`` is Waterdeep's position, the origin of the terrain grids.  The
    result is empty when the polygon sits wholly on unsurveyed ground or open
    water, in which case callers should keep the original.

    With ``buffer_miles`` the outline is pushed out over the sea by that
    distance, smoothed, and kept off the other land and off every polygon in
    ``avoid`` (other regions' borders), so neighbouring realms butt up to each
    other rather than overlap.
    """
    snap = max(0.0, min(float(snap_miles), MAX_SNAP_MILES))
    buffer = max(0.0, min(float(buffer_miles), MAX_BUFFER_MILES))
    surveyed = list(_grids() if grids is None else grids)
    if not surveyed:
        return []
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    pad = snap + buffer + COAST_BAND_MILES + 2.0
    x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
    cell = max(1.0, max(x1 - x0, y1 - y0) / MAX_GRID)
    width, height = int(math.ceil((x1 - x0) / cell)), int(math.ceil((y1 - y0) / cell))
    inside = _fill_land([ring], x0, y0, cell, width, height)
    states = [[_state(surveyed, x0 + (i + 0.5) * cell, y0 + (j + 0.5) * cell, origin)
               for i in range(width)] for j in range(height)]
    water = [bytearray(1 if states[j][i] == 0 else 0 for i in range(width)) for j in range(height)]
    to_sea = _distance_field(water, width, height)
    to_polygon = _distance_field(inside, width, height)
    if not any(states[j][i] == 1 for j in range(height) for i in range(width) if inside[j][i]):
        return []
    kept: Set[Tuple[int, int]] = set()
    seeds: List[Tuple[int, int]] = []
    for j in range(height):
        for i in range(width):
            state = states[j][i]
            if inside[j][i]:
                if state != 0:
                    kept.add((i, j))
                    seeds.append((i, j))
            elif (state == 1 and to_polygon[j][i] * cell <= snap
                  and to_sea[j][i] * cell <= max(COAST_BAND_MILES, cell * 1.5)):
                kept.add((i, j))
    linked = _connected(seeds, kept)
    if buffer > 0:
        linked = _with_sea_buffer(linked, states, x0, y0, cell, width, height, buffer, avoid)
    fitted: List[List[List[float]]] = []
    for loop in outer_loops(linked):
        points = [(x0 + c * cell, y0 + r * cell) for c, r in loop]
        if ring_area(points) < MIN_LAND_SQUARE_MILES:
            continue
        tolerance = max(0.6, cell * 0.6)
        while tolerance >= 0.1:
            simple = simplify_closed(points, tolerance)
            candidate = [[round(x, 2), round(y, 2)] for x, y in simple]
            if buffer > 0:
                candidate = smooth_ring(candidate, BUFFER_SMOOTH_MILES, preserve_area=False)
            if len(candidate) >= 3 and not ring_self_intersects(candidate):
                fitted.append(candidate)
                break
            tolerance /= 2.0
        else:
            fitted.append([[round(x, 2), round(y, 2)] for x, y in points])
    return fitted


def _connected(seeds: Sequence[Tuple[int, int]], allowed: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """The cells of ``allowed`` that join the seeds, corners included."""
    linked: Set[Tuple[int, int]] = set(seeds)
    stack = list(seeds)
    while stack:
        i, j = stack.pop()
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                neighbour = (i + di, j + dj)
                if neighbour in allowed and neighbour not in linked:
                    linked.add(neighbour)
                    stack.append(neighbour)
    return linked


def _with_sea_buffer(land: Set[Tuple[int, int]], states: List[List[int]], x0: float, y0: float,
                     cell: float, width: int, height: int, buffer: float,
                     avoid: Sequence[Sequence[Sequence[float]]]) -> Set[Tuple[int, int]]:
    """Grow ``land`` over the sea by ``buffer`` miles, leaving other land and ``avoid`` polygons alone."""
    mask = [bytearray(width) for _ in range(height)]
    for i, j in land:
        mask[j][i] = 1
    reach = _distance_field(mask, width, height)
    others = [(_bounds_of(ring), ring) for ring in avoid]
    grown: Set[Tuple[int, int]] = set(land)
    for j in range(height):
        yc = y0 + (j + 0.5) * cell
        for i in range(width):
            if (i, j) in land or reach[j][i] * cell > buffer or states[j][i] == 1:
                continue
            xc = x0 + (i + 0.5) * cell
            if any(b[0] <= xc <= b[2] and b[1] <= yc <= b[3] and point_in_ring(xc, yc, ring) for b, ring in others):
                continue
            grown.add((i, j))
    return _connected(list(land), grown)


def fit_borders_to_coast(borders: Sequence[Sequence[Sequence[float]]], origin: Tuple[float, float],
                         snap_miles: float = DEFAULT_SNAP_MILES, buffer_miles: float = 0.0,
                         avoid: Sequence[Sequence[Sequence[float]]] = ()) -> Dict[str, Any]:
    """Fit each polygon; a polygon that finds no land is returned unchanged."""
    grids = _grids()
    results: List[List[List[List[float]]]] = []
    reports: List[Dict[str, Any]] = []
    for ring in borders:
        fitted = fit_ring_to_coast(ring, origin, snap_miles, grids, buffer_miles, avoid)
        if not fitted:
            results.append([[list(map(float, p)) for p in ring]])
            reports.append({"pointsBefore": len(ring), "pointsAfter": len(ring), "polygons": 1,
                            "maxShiftMiles": 0.0, "changed": False, "bufferMiles": 0.0,
                            "note": "No mapped land found under this polygon."})
            continue
        shift = max((min(distance_to_ring(x, y, piece) for piece in fitted) for x, y in ring), default=0.0)
        results.append(fitted)
        reports.append({"pointsBefore": len(ring), "pointsAfter": sum(len(piece) for piece in fitted),
                        "polygons": len(fitted), "maxShiftMiles": round(shift, 2), "changed": True,
                        "bufferMiles": float(buffer_miles)})
    return {"fitted": results, "reports": reports}
