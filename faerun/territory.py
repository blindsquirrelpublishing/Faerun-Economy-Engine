"""Smoothing and territory outlines for region borders, in plain Python.

``smooth_ring`` removes the stair-steps a raster-seeded coastline picks up.
``region_territories`` turns each region's land polygons into the territory it
claims: land plus the sea margin, smoothed, and divided with its neighbours so
that two realms whose margins meet share one border instead of overlapping.

A cell of sea goes to the region whose coast is nearest, and land always stays
with the region that owns it.  This is the same rule ``regions.region_at`` uses
for a single point, so the outlines drawn on the map agree with the lookups.
"""
from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .regions import (Region, distance_to_ring, point_in_ring, ring_area,
                      ring_self_intersects, _segment_distance)

Point = Tuple[float, float]

TERRITORY_CELL_MILES = 2.0
TERRITORY_MAX_GRID = 450
TERRITORY_SMOOTH_MILES = 4.0
MIN_TERRITORY_SQUARE_MILES = 4.0
MAX_SMOOTH_MILES = 50.0
_INF = 1e20


# ---------------------------------------------------------------------------
# Rings
# ---------------------------------------------------------------------------

def _perimeter(points: Sequence[Point]) -> float:
    return sum(math.dist(points[i], points[(i + 1) % len(points)]) for i in range(len(points)))


def _resample(points: Sequence[Point], spacing: float) -> List[Point]:
    count = len(points)
    lengths = [math.dist(points[i], points[(i + 1) % count]) for i in range(count)]
    total = sum(lengths)
    samples = max(8, int(round(total / spacing)))
    step = total / samples
    out: List[Point] = []
    edge, travelled = 0, 0.0
    for index in range(samples):
        target = index * step
        while travelled + lengths[edge] < target and edge < count - 1:
            travelled += lengths[edge]
            edge += 1
        start, end = points[edge], points[(edge + 1) % count]
        fraction = (target - travelled) / lengths[edge] if lengths[edge] else 0.0
        out.append((start[0] + (end[0] - start[0]) * fraction, start[1] + (end[1] - start[1]) * fraction))
    return out


def _centroid(points: Sequence[Point]) -> Point:
    return (sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points))


def simplify_open(points: Sequence[Point], tolerance: float) -> List[Point]:
    """Douglas-Peucker over an open path; both ends are kept."""
    if len(points) < 3:
        return list(points)
    first, last = points[0], points[-1]
    worst, index = 0.0, 0
    for i in range(1, len(points) - 1):
        d = _segment_distance(points[i][0], points[i][1], first[0], first[1], last[0], last[1])
        if d > worst:
            worst, index = d, i
    if worst <= tolerance:
        return [first, last]
    return simplify_open(points[:index + 1], tolerance)[:-1] + simplify_open(points[index:], tolerance)


def simplify_closed(points: Sequence[Point], tolerance: float) -> List[Point]:
    """Douglas-Peucker for a ring, split at its two farthest-apart vertices."""
    if len(points) < 4:
        return list(points)
    far = max(range(len(points)), key=lambda i: math.dist(points[0], points[i]))
    first = simplify_open(list(points[:far + 1]), tolerance)
    second = simplify_open(list(points[far:]) + [points[0]], tolerance)
    return first[:-1] + second[:-1]


def smooth_ring(ring: Sequence[Sequence[float]], strength_miles: float, *,
                preserve_area: bool = True) -> List[List[float]]:
    """Round off a polygon over roughly ``strength_miles`` of its outline.

    The ring is resampled evenly, averaged with its neighbours, and thinned
    again.  Averaging pulls a small island inward, so by default the polygon is
    scaled back to its original area.  A result that crosses itself is retried
    with a lighter touch, and in the end the original ring is returned.
    """
    points = [(float(p[0]), float(p[1])) for p in ring]
    strength = max(0.0, min(float(strength_miles), MAX_SMOOTH_MILES))
    perimeter = _perimeter(points) if len(points) >= 3 else 0.0
    # A small island cannot be smoothed over more than a sixth of its outline.
    strength = min(strength, perimeter / 6.0)
    if strength < 0.5:
        return [list(p) for p in points]
    spacing = max(strength / 4.0, 0.5, perimeter / 3000.0)
    samples = _resample(points, spacing)
    original_area = ring_area(points)
    reach = max(1, int(round(strength / (2.0 * spacing))))
    while reach >= 1:
        averaged = samples
        for _ in range(2):  # two passes give a smooth, rounded result rather than a flattened one
            total = len(averaged)
            averaged = [(sum(averaged[(i + d) % total][0] for d in range(-reach, reach + 1)) / (2 * reach + 1),
                         sum(averaged[(i + d) % total][1] for d in range(-reach, reach + 1)) / (2 * reach + 1))
                        for i in range(total)]
        thinned = simplify_closed(averaged, max(0.4, strength / 8.0))
        if preserve_area and original_area > 0:
            area = ring_area(thinned)
            if area > 0 and abs(area - original_area) / original_area > 0.005:
                cx, cy = _centroid(thinned)
                scale = math.sqrt(original_area / area)
                thinned = [(cx + (x - cx) * scale, cy + (y - cy) * scale) for x, y in thinned]
        result = [[round(x, 2), round(y, 2)] for x, y in thinned]
        if len(result) >= 3 and ring_area(result) > 0 and not ring_self_intersects(result):
            return result
        reach -= 1
    return [list(p) for p in points]


def smooth_borders(borders: Sequence[Sequence[Sequence[float]]], strength_miles: float) -> List[List[List[float]]]:
    return [smooth_ring(ring, strength_miles) for ring in borders]


def smooth_report(before: Sequence[Sequence[float]], after: Sequence[Sequence[float]]) -> Dict[str, object]:
    """How much a smoothing pass moved one polygon."""
    shift = max((distance_to_ring(x, y, after) for x, y in before), default=0.0) if len(after) >= 3 else 0.0
    return {"pointsBefore": len(before), "pointsAfter": len(after), "maxShiftMiles": round(shift, 2),
            "changed": [list(map(float, p)) for p in before] != [list(map(float, p)) for p in after]}


# ---------------------------------------------------------------------------
# Raster helpers
# ---------------------------------------------------------------------------

def outer_loops(cells: Set[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    """Counter-clockwise outlines, in cell corners, of a set of grid cells.

    Holes come out clockwise and are dropped.  Where two cells only touch at a
    corner the trace turns right, so diagonal neighbours stay one outline.
    """
    edges: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()
    for column, row in cells:
        for edge in (((column, row), (column + 1, row)), ((column + 1, row), (column + 1, row + 1)),
                     ((column + 1, row + 1), (column, row + 1)), ((column, row + 1), (column, row))):
            reverse = (edge[1], edge[0])
            if reverse in edges:
                edges.remove(reverse)
            else:
                edges.add(edge)
    outgoing: Dict[Tuple[int, int], List[Tuple[int, int]]] = {}
    for start, end in edges:
        outgoing.setdefault(start, []).append(end)
    loops = []
    while outgoing:
        start = next(iter(outgoing))
        loop = [start]
        previous, current = None, start
        while True:
            options = outgoing.get(current, [])
            if not options:
                break
            if len(options) > 1 and previous is not None:
                heading = (current[0] - previous[0], current[1] - previous[1])
                options = sorted(options, key=lambda end: heading[0] * (end[1] - current[1])
                                 - heading[1] * (end[0] - current[0]))
            following = options[0]
            outgoing[current].remove(following)
            if not outgoing[current]:
                del outgoing[current]
            previous, current = current, following
            if current == start:
                break
            loop.append(current)
        if len(loop) >= 3 and sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(loop, loop[1:] + loop[:1])) > 0:
            loops.append(loop)
    return loops


def _squared_distance_1d(f: List[float], n: int) -> List[float]:
    d = [0.0] * n
    v = [0] * n
    z = [0.0] * (n + 1)
    k = 0
    z[0], z[1] = -_INF, _INF
    for q in range(1, n):
        s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k])
        while s <= z[k]:
            k -= 1
            s = ((f[q] + q * q) - (f[v[k]] + v[k] * v[k])) / (2 * q - 2 * v[k])
        k += 1
        v[k] = q
        z[k], z[k + 1] = s, _INF
    k = 0
    for q in range(n):
        while z[k + 1] < q:
            k += 1
        d[q] = (q - v[k]) ** 2 + f[v[k]]
    return d


def _distance_field(land: List[bytearray], width: int, height: int) -> List[List[float]]:
    """Distance, in cells, from every cell to the nearest land cell."""
    columns = [[0.0 if land[j][i] else _INF for j in range(height)] for i in range(width)]
    columns = [_squared_distance_1d(column, height) for column in columns]
    field: List[List[float]] = []
    for j in range(height):
        row = _squared_distance_1d([columns[i][j] for i in range(width)], width)
        field.append([math.sqrt(value) if value < _INF / 2 else math.inf for value in row])
    return field


def _fill_land(rings: Iterable[Sequence[Sequence[float]]], x0: float, y0: float, cell: float,
               width: int, height: int) -> List[bytearray]:
    land = [bytearray(width) for _ in range(height)]
    for ring in rings:
        crossings: Dict[int, List[float]] = {}
        for index in range(len(ring)):
            (ax, ay), (bx, by) = ring[index], ring[(index + 1) % len(ring)]
            if ay == by:
                continue
            low, high = (ay, by) if ay < by else (by, ay)
            first = max(0, int(math.ceil((low - y0) / cell - 0.5)))
            last = min(height - 1, int(math.ceil((high - y0) / cell - 0.5)) - 1)
            for j in range(first, last + 1):
                yc = y0 + (j + 0.5) * cell
                if low <= yc < high:
                    crossings.setdefault(j, []).append(ax + (yc - ay) * (bx - ax) / (by - ay))
        for j, xs in crossings.items():
            xs.sort()
            for a, b in zip(xs[0::2], xs[1::2]):
                start = max(0, int(math.ceil((a - x0) / cell - 0.5)))
                stop = min(width, int(math.ceil((b - x0) / cell - 0.5)))
                for i in range(start, stop):
                    land[j][i] = 1
    return land


def _bounds(region: Region, pad: float) -> Tuple[float, float, float, float]:
    xs = [p[0] for ring in region.borders for p in ring]
    ys = [p[1] for ring in region.borders for p in ring]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def _loses_to_neighbour(region: Region, others: Sequence[Region], x: float, y: float, own: float) -> bool:
    for other in others:
        if other is region:
            continue
        low_x, low_y, high_x, high_y = other._reach
        if not (low_x <= x <= high_x and low_y <= y <= high_y):
            continue
        distance = other.distance_to_territory(x, y)
        if distance > other.sea_margin_miles:
            continue
        if distance == 0 or distance < own - 1e-9 or (abs(distance - own) <= 1e-9 and other.id < region.id):
            return True
    return False


def _sea_territory(region: Region, others: Sequence[Region]) -> List[List[List[float]]]:
    margin = region.sea_margin_miles
    x0, y0, x1, y1 = _bounds(region, margin + 2 * TERRITORY_CELL_MILES)
    cell = max(TERRITORY_CELL_MILES, max(x1 - x0, y1 - y0) / TERRITORY_MAX_GRID)
    width, height = int(math.ceil((x1 - x0) / cell)), int(math.ceil((y1 - y0) / cell))
    land = _fill_land(region.borders, x0, y0, cell, width, height)
    field = _distance_field(land, width, height)
    owned: Set[Tuple[int, int]] = set()
    for j in range(height):
        yc = y0 + (j + 0.5) * cell
        for i in range(width):
            if land[j][i]:
                owned.add((i, j))
                continue
            approximate = field[j][i] * cell
            if approximate > margin + cell:
                continue
            xc = x0 + (i + 0.5) * cell
            # The cell-centre distance is only good to about a cell; measure the
            # cells near the margin against the real outline.
            distance = approximate if approximate <= margin - 2 * cell else region.distance_to_territory(xc, yc)
            if distance > margin:
                continue
            if _loses_to_neighbour(region, others, xc, yc, distance):
                continue
            owned.add((i, j))
    rings: List[List[List[float]]] = []
    for loop in outer_loops(owned):
        ring = [(x0 + c * cell, y0 + r * cell) for c, r in loop]
        if ring_area(ring) < MIN_TERRITORY_SQUARE_MILES:
            continue
        smoothed = smooth_ring(ring, TERRITORY_SMOOTH_MILES, preserve_area=False)
        rings.append(smoothed)
    return rings


def region_territories(regions: Sequence[Region]) -> Dict[str, List[List[List[float]]]]:
    """Territory outlines (land plus sea margin, shared with neighbours) per region id.

    A region without a sea margin simply claims its land polygons.
    """
    claimants = [region for region in regions if region.borders]
    for region in claimants:
        region._reach = _bounds(region, region.sea_margin_miles)
    result: Dict[str, List[List[List[float]]]] = {}
    for region in claimants:
        if region.sea_margin_miles <= 0:
            result[region.id] = [[list(p) for p in ring] for ring in region.borders]
        else:
            result[region.id] = _sea_territory(region, claimants) or \
                [[list(p) for p in ring] for ring in region.borders]
    return result
