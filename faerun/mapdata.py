"""Geography for the 3D world map.

The gazetteer in :mod:`faerun.data.settlements` gives every settlement an
``x``/``y`` position in miles (x grows east, y grows south).  That is enough to
plot dots, but a map wants land, sea and mountains as well.  This module adds
that missing layer: a hand-authored sketch of Faerun -- coastlines, inland
seas, mountain ranges and broad terrain zones -- which is rasterised into a
heightfield the browser can render as a 3D relief map.

The sketch is deliberately coarse.  One grid cell is roughly thirty miles
across, so features smaller than that (the Dragonmere, for instance) simply do
not survive.  What matters is that the continent reads as Faerun and that every
settlement sits on solid ground.  The second guarantee is structural rather
than hopeful: after the polygons are rasterised, a blob is stamped around every
settlement, so a city can never end up in the sea even if the coastline drawn
here is wrong.
"""

from __future__ import annotations

import json
import math
import os
import re
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .calibration import (
    base_coordinates, build_warp, load_control_points, warp_for,
)
from .atlas import AtlasError, normalise, project_root

# ---------------------------------------------------------------------------
# grid definition
# ---------------------------------------------------------------------------

#: world-space bounds of the map, in miles: (west, north, east, south)
#:
#: These are the bounds the hand-authored terrain below was drawn against, and
#: they are what the map uses when there is nothing else to accommodate.  Two
#: things stretch it, and both only ever grow it - see `_resolve_frame`:
#: a surveyed poster, whose footprint reaches a good deal further east than
#: this hand-drawn window, and a realignment, which moves the markets out to
#: match.  The grid follows the frame so the cells stay square either way.
SHIPPED_BOUNDS: Tuple[float, float, float, float] = (250.0, 80.0, 2250.0, 3120.0)
BOUNDS: Tuple[float, float, float, float] = SHIPPED_BOUNDS

#: Empty miles kept between the outermost market and the edge of the map.
FRAME_MARGIN = 140.0

#: Target heightfield cell, in miles.  A grown frame keeps this roughly
#: constant instead of stretching the cells, so detail does not thin out.
CELL_MILES = 20.8

#: Hard ceiling on the field, because the rasteriser is O(cells x polygons)
#: and a runaway survey should slow the map down, not hang it.  The real
#: governor is the cell *count*: capping each axis on its own is what turns
#: square cells oblong, and an oblong cell shows as a coastline smeared in one
#: direction only.  The per-axis numbers below are just a backstop against a
#: frame that is absurd in one dimension.
#:
#: 26000 is a little under twice the shipped 96 x 146 field, which is what the
#: continent-wide poster frame costs.  The field is built once and cached, and
#: the renderer decimates with ``state.step`` while dragging, so this is paid
#: at load and not per frame.
MAX_CELLS = 26000
MAX_GRID_W = 320
MAX_GRID_H = 320

#: How far a surveyed terrain label may sit from where the market realignment
#: alone predicts, before it is treated as a bad match rather than a
#: correction.  A poster letters a mountain range along its spine rather than
#: at its middle, so some slack is required; but a label several hundred miles
#: adrift means the name matched the wrong thing, and pinning the terrain to it
#: would tear the coastline apart.
TERRAIN_ANCHOR_LIMIT = 350.0

#: heightfield resolution.  96 x 146 divides the portrait bounds above into
#: almost exactly square cells of 20.8 x 20.8 miles -- half the width of the
#: old 64 x 96 field, so coastlines and river valleys carry noticeably more
#: detail.  Cost scales with the cell count (2.3x), but the field is built once
#: and cached, and the renderer decimates with ``state.step`` while dragging.
SHIPPED_GRID_W = 96
SHIPPED_GRID_H = 146
GRID_W = SHIPPED_GRID_W
GRID_H = SHIPPED_GRID_H

#: terrain single-character codes used in the transferred payload
CODES = {
    "ocean": "o",
    "water": "w",
    "coast": "c",
    "plains": "p",
    "steppe": "g",
    "forest": "f",
    "taiga": "T",
    "tundra": "t",
    "glacier": "i",
    "hills": "h",
    "mountains": "m",
    "desert": "d",
    "jungle": "j",
    "marsh": "s",
}

#: human readable names for the codes, shipped to the client for its legend
LEGEND = {code: name for name, code in CODES.items()}

LOCATION_TERRAIN_NAMES = ("location-terrain.json", "terrain-locations.json")
LOCATION_TERRAIN_POINTER = "location-terrain.path"
DETAIL_TERRAIN_NAME = "terrain-5-mile.json"
TERRAIN_OVERRIDES_NAME = "terrain-overrides.json"
ROAD_GEOMETRY_NAMES = ("road-geometries.json", "roads.json")
ROAD_GEOMETRY_POINTER = "road-geometries.path"
SEA_AIR_GEOMETRY_NAMES = ("sea-air-routes.json", "sea-routes.json")
SEA_AIR_GEOMETRY_POINTER = "sea-air-routes.path"
FPS_MILES_PER_UNIT = 120.0
POSTER_PIXELS_PER_FPS_UNIT = 150.5
SURVEY_INFLUENCE_MILES = 35.0
ROAD_ENDPOINT_LIMIT_MILES = 65.0
_FPS_PATTERN = re.compile(
    r"^FPS1:WD:X(?P<x>[+-]\d+(?:\.\d+)?):Y(?P<y>[+-]\d+(?:\.\d+)?)$"
)

_SURVEY_TERRAIN = {
    "cleared_mixed": "plains",
    "forest": "forest",
    "hills": "hills",
    "mountains": "mountains",
    "plains": "plains",
    "sandy_desert": "desert",
    "wetland": "marsh",
}

_FULL_GRID_TERRAIN = {
    "S": "ocean",
    "W": "water",
    "P": "plains",
    "C": "plains",
    "F": "forest",
    "J": "jungle",
    "H": "hills",
    "M": "mountains",
    "T": "marsh",
    "O": "tundra",
    "D": "desert",
    "R": "desert",
    "I": "glacier",
}


def _terrain_overrides_path() -> Path:
    return project_root() / "maps" / TERRAIN_OVERRIDES_NAME


def terrain_overrides() -> Dict[str, str]:
    """Load small, user-authored corrections to the rendered world grid."""
    path = _terrain_overrides_path()
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read terrain overrides %s: %s" % (path, exc)) from exc
    if not isinstance(payload, dict) or payload.get("format") != "faerun-terrain-overrides-v1":
        raise AtlasError("terrain overrides have an unsupported format")
    cells = payload.get("cells")
    if not isinstance(cells, dict):
        raise AtlasError("terrain overrides need a cells object")
    valid_codes = set(CODES.values())
    clean: Dict[str, str] = {}
    for key, code in cells.items():
        if not isinstance(key, str) or not isinstance(code, str) or code not in valid_codes:
            raise AtlasError("terrain override cells need grid keys and valid terrain codes")
        clean[key] = code
    return clean


def terrain_overrides_stamp() -> str:
    path = _terrain_overrides_path()
    if not path.is_file():
        return "-"
    stat = path.stat()
    return "%d:%d" % (stat.st_mtime_ns, stat.st_size)


def save_terrain_override(column: int, row: int, terrain: str) -> int:
    """Persist or remove one rendered world-grid correction."""
    if column < 0 or column >= GRID_W or row < 0 or row >= GRID_H:
        raise AtlasError("terrain cell is outside the world grid")
    if terrain and terrain not in CODES.values():
        raise AtlasError("unknown terrain code %r" % terrain)
    cells = terrain_overrides()
    key = "%d,%d" % (column, row)
    if terrain:
        cells[key] = terrain
    else:
        cells.pop(key, None)
    path = _terrain_overrides_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "format": "faerun-terrain-overrides-v1",
        "grid": [GRID_W, GRID_H],
        "cells": dict(sorted(cells.items())),
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)
    _CACHE.clear()
    return len(cells)


Point = Tuple[float, float]
Poly = Sequence[Point]
#: (west, north, east, south) in miles, the same shape as BOUNDS
Rect = Tuple[float, float, float, float]


def location_terrain_path() -> Optional[Path]:
    """Find the optional 10-mile location terrain survey."""
    configured = os.environ.get("FAERUN_TERRAIN_SURVEY", "").strip()
    if configured:
        path = Path(configured).expanduser()
        if not path.is_file():
            raise AtlasError(
                "FAERUN_TERRAIN_SURVEY does not point to a file: %s" % path
            )
        return path

    root = project_root()
    for folder in (root / "maps", root, Path.cwd() / "maps", Path.cwd()):
        for name in LOCATION_TERRAIN_NAMES:
            path = folder / name
            if path.is_file():
                return path
        pointer = folder / LOCATION_TERRAIN_POINTER
        if pointer.is_file():
            try:
                target = Path(pointer.read_text(encoding="utf-8").strip()).expanduser()
            except (OSError, UnicodeError) as exc:
                raise AtlasError(
                    "cannot read location terrain pointer %s: %s" % (pointer, exc)
                )
            if not target.is_file():
                raise AtlasError(
                    "location terrain pointer %s does not point to a file: %s"
                    % (pointer, target)
                )
            return target
    return None


def _parse_location_terrain(payload: object) -> Dict[str, Dict[str, object]]:
    """Index the survey by normalized location name."""
    if not isinstance(payload, dict) or not isinstance(payload.get("locations"), list):
        raise AtlasError("location terrain survey needs a locations array")

    contexts: Dict[str, Dict[str, object]] = {}
    for row in payload["locations"]:
        if not isinstance(row, dict):
            raise AtlasError("every location terrain entry must be an object")
        name = str(row.get("name", "")).strip()
        key = normalise(name)
        if not key:
            continue
        dominant = str(row.get("cell_dominant_terrain", "")).strip().lower()
        terrain = _SURVEY_TERRAIN.get(dominant, "")
        relief = str(row.get("cell_relief", "")).strip().lower()
        fps = str(row.get("fps", "")).strip()
        match = _FPS_PATTERN.match(fps)
        floor = 0.0
        if dominant == "mountains" or "mountain" in relief:
            floor = 0.58
        elif dominant == "hills" or "hill" in relief or "rugged" in relief:
            floor = 0.28
        elif terrain and ("gentle" in relief or "low_relief" in relief):
            floor = 0.06
        contexts[key] = {
            "name": name,
            "terrain": terrain,
            "floor": floor,
            "dominant": dominant,
            "east": float(match.group("x")) * FPS_MILES_PER_UNIT if match else None,
            "north": float(match.group("y")) * FPS_MILES_PER_UNIT if match else None,
        }
    return contexts


def _parse_full_terrain(payload: object) -> Dict[str, object]:
    """Validate the contiguous 10-mile terrain-grid format."""
    if not isinstance(payload, dict) or payload.get("format") != "faerun-terrain-simple-v1":
        return {}
    rows = payload.get("rows")
    if not isinstance(rows, dict):
        raise AtlasError("full terrain survey needs a rows object")
    try:
        column_min = int(payload["column_min"])
        column_max = int(payload["column_max"])
        row_min = int(payload["row_min"])
        row_max = int(payload["row_max"])
        width = int(payload["width"])
        cell_miles = float(payload["cell_miles"])
    except (KeyError, TypeError, ValueError) as exc:
        raise AtlasError("full terrain survey has invalid grid metadata") from exc
    if width != column_max - column_min + 1 or cell_miles <= 0:
        raise AtlasError("full terrain survey dimensions are inconsistent")
    for row in range(row_min, row_max + 1):
        value = rows.get(str(row))
        if not isinstance(value, str) or len(value) != width:
            raise AtlasError("full terrain survey row %d has the wrong width" % row)
    return {
        "rows": rows,
        "column_min": column_min,
        "column_max": column_max,
        "row_min": row_min,
        "row_max": row_max,
        "width": width,
        "cell_miles": cell_miles,
        "cell_count": int(payload.get("cell_count", width * len(rows))),
    }


def _full_terrain_cell(grid: Dict[str, object], east: float,
                       north: float) -> str:
    """Return the engine terrain name at a Waterdeep-relative position."""
    if not grid:
        return ""
    cell_miles = float(grid["cell_miles"])
    column = math.floor(east / cell_miles)
    row = math.floor(north / cell_miles)
    if (
        column < int(grid["column_min"])
        or column > int(grid["column_max"])
        or row < int(grid["row_min"])
        or row > int(grid["row_max"])
    ):
        return ""
    rows = grid["rows"]
    assert isinstance(rows, dict)
    value = rows.get(str(row), "")
    if not isinstance(value, str):
        return ""
    letter = value[column - int(grid["column_min"])]
    return _FULL_GRID_TERRAIN.get(letter, "")


def location_terrain_contexts() -> Tuple[Dict[str, Dict[str, object]], str]:
    """Load location-cell context, leaving the generated terrain usable if absent."""
    path = location_terrain_path()
    if path is None:
        return {}, ""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read location terrain survey %s: %s" % (path, exc))
    if isinstance(payload, dict) and payload.get("format") == "faerun-terrain-simple-v1":
        return {}, str(path)
    return _parse_location_terrain(payload), str(path)


def full_terrain_grid() -> Tuple[Dict[str, object], str]:
    """Load a contiguous terrain grid when the configured survey provides one."""
    path = location_terrain_path()
    if path is None:
        return {}, ""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read terrain grid %s: %s" % (path, exc))
    return _parse_full_terrain(payload), str(path)


def location_terrain_stamp() -> str:
    path = location_terrain_path()
    if path is None:
        return "-"
    stat = path.stat()
    return "%s:%d:%d" % (path, stat.st_mtime_ns, stat.st_size)


def road_geometry_path() -> Optional[Path]:
    """Find optional poster-traced road and trail polylines."""
    root = project_root()
    for folder in (root / "maps", root, Path.cwd() / "maps", Path.cwd()):
        for name in ROAD_GEOMETRY_NAMES:
            path = folder / name
            if path.is_file():
                return path
        pointer = folder / ROAD_GEOMETRY_POINTER
        if pointer.is_file():
            try:
                target = Path(pointer.read_text(encoding="utf-8").strip()).expanduser()
            except (OSError, UnicodeError) as exc:
                raise AtlasError(
                    "cannot read road geometry pointer %s: %s" % (pointer, exc)
                )
            if not target.is_file():
                raise AtlasError(
                    "road geometry pointer %s does not point to a file: %s"
                    % (pointer, target)
                )
            return target
    return None


def _parse_road_geometries(payload: object) -> List[Dict[str, object]]:
    """Validate poster-traced FPS road corridors."""
    if not isinstance(payload, dict) or not isinstance(payload.get("corridors"), list):
        raise AtlasError("road geometry file needs a corridors array")
    corridors: List[Dict[str, object]] = []
    for row in payload["corridors"]:
        if not isinstance(row, dict):
            raise AtlasError("every road corridor must be an object")
        waypoints = row.get("fps_waypoints")
        if not isinstance(waypoints, list) or len(waypoints) < 2:
            continue
        points: List[List[float]] = []
        for waypoint in waypoints:
            if not isinstance(waypoint, dict):
                raise AtlasError("road corridor waypoints must be objects")
            try:
                points.append([float(waypoint["x"]), float(waypoint["y"])])
            except (KeyError, TypeError, ValueError) as exc:
                raise AtlasError("road corridor has an invalid FPS waypoint") from exc
        surface = str(row.get("surface", "road")).strip().lower()
        if surface not in ("road", "trail", "track"):
            surface = "road"
        corridors.append({
            "id": str(row.get("id", "")).strip(),
            "name": str(row.get("name", "")).strip(),
            "surface": surface,
            "fps": points,
        })
    return _connect_dragon_coast_trails(_compose_named_road_routes(corridors))


def _connect_dragon_coast_trails(corridors):
    by_id = {corridor["id"]: corridor for corridor in corridors}
    coast = by_id.get("elversult-starmantle-trail")
    if coast is not None:
        coast["stops"] = ["elversult", "starmantle"]
        coast["exclusive_stops"] = True
    branch = by_id.get("dragon-coast-shining-trail")
    plains = by_id.get("shining-plains-road")
    if coast is None or branch is None or plains is None:
        return corridors

    def junction(points, endpoint):
        distance, progress = _point_on_road(tuple(endpoint), points)
        if distance * FPS_MILES_PER_UNIT > 10:
            return None
        index = min(int(progress), len(points) - 2)
        fraction = progress - index
        point = [points[index][axis] + fraction * (points[index + 1][axis] - points[index][axis])
                 for axis in (0, 1)]
        if fraction < 1e-8:
            return index, points[index]
        if fraction > 1 - 1e-8:
            return index + 1, points[index + 1]
        points.insert(index + 1, point)
        return index + 1, point

    north = junction(coast["fps"], branch["fps"][0])
    south = junction(plains["fps"], branch["fps"][-1])
    if north is None or south is None:
        return corridors
    destination = [(2037 - 694) / 150.5, (682 - 1550) / 150.5]
    destination_join = junction(plains["fps"], destination)
    if destination_join is None:
        return corridors
    south_index = plains["fps"].index(south[1])
    destination_index = destination_join[0]
    if destination_index <= south_index:
        approach = list(reversed(plains["fps"][destination_index:south_index + 1]))
    else:
        approach = plains["fps"][south_index:destination_index + 1]
    branch["fps"] = coast["fps"][:north[0] + 1] + branch["fps"][1:-1] + approach
    branch["stops"] = ["elversult", "lheshayl"]
    branch["exclusive_stops"] = True
    return corridors


def _compose_named_road_routes(
    corridors: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    """Join traced corridor fragments that form one named trade route."""
    by_id = {str(corridor["id"]): corridor for corridor in corridors}
    if "corm-orp-south" in by_id:
        by_id["corm-orp-south"]["stops"] = ["corm_orp", "hluthvar"]
        by_id["corm-orp-south"]["exclusive_stops"] = True
    if "shaar-main-road" in by_id:
        road = by_id["shaar-main-road"]
        pixels = [
            (2779, 2262), (2820, 2264), (2850, 2268), (2870, 2277),
            (2900, 2290), (2920, 2293), (2944, 2291), (2980, 2284),
            (3005, 2288), (3050, 2292), (3075, 2292), (3110, 2287),
            (3150, 2285), (3190, 2278), (3210, 2276), (3245, 2289),
            (3280, 2300), (3315, 2321), (3350, 2322), (3381, 2327),
            (3404, 2341), (3415, 2358), (3437, 2374), (3473, 2392),
            (3520, 2393), (3573, 2392), (3610, 2387), (3656, 2385),
            (3696, 2383),
        ]
        road["fps"] = [[(east - 694) / 150.5, (682 - south) / 150.5]
                       for east, south in pixels]
        road["stops"] = ["shaarmid", "kholtar", "eartheart", "delzimmer"]
        road["exclusive_stops"] = True
        road["geometry_source"] = "Manually corrected against Faerun Hires.jpg road symbols"
    shining_ids = {"riatavin-lheshayl", "shining-road-east"}
    if shining_ids.issubset(by_id):
        west = list(by_id["riatavin-lheshayl"]["fps"])
        east = list(by_id["shining-road-east"]["fps"])
        shining = {
            "id": "shining-plains-road",
            "name": "The Shining Plains Road",
            "surface": "road",
            "fps": west + east[1:],
            "stops": ["riatavin", "lheshayl", "ormath", "hlondeth"],
        }
        corridors = [
            corridor for corridor in corridors
            if corridor["id"] not in shining_ids
        ] + [shining]
        by_id = {str(corridor["id"]): corridor for corridor in corridors}

    source_ids = {"emerald-way", "arrabar-emerald-way", "golden-road-south"}
    if not source_ids.issubset(by_id):
        return corridors

    emerald = list(by_id["emerald-way"]["fps"])
    arrabar = list(reversed(by_id["arrabar-emerald-way"]["fps"]))
    golden = list(by_id["golden-road-south"]["fps"])
    ormpetarr_fps = (12.39, -7.33)
    ormpetarr_index = min(
        range(len(golden)),
        key=lambda index: math.dist(golden[index], ormpetarr_fps),
    )
    innarlith_fps = (13.39, -8.68)
    innarlith_index = min(
        range(ormpetarr_index, len(golden)),
        key=lambda index: math.dist(golden[index], innarlith_fps),
    )

    route = [
        {
            "id": "vilhon-road-hlath-arrabar",
            "name": "The Vilhon Road",
            "surface": "road",
            "fps": emerald + arrabar,
        },
        {
            "id": "vilhon-road-arrabar-ormpetarr",
            "name": "The Vilhon Road",
            "surface": "road",
            "fps": golden[:ormpetarr_index + 1],
        },
        {
            "id": "golden-road-ormpetarr-innarlith",
            "name": "The Golden Road: Ormpetarr to Innarlith",
            "surface": "road",
            "fps": golden[ormpetarr_index:innarlith_index + 1],
        },
        {
            "id": "golden-road-innarlith-shaarmid",
            "name": "The Golden Road: Innarlith to Shaarmid",
            "surface": "road",
            "fps": golden[innarlith_index:],
        },
    ]
    return [corridor for corridor in corridors if corridor["id"] not in source_ids] + route


def _point_on_road(
    point: Tuple[float, float], points: Sequence[Sequence[float]],
) -> Tuple[float, float]:
    """Return distance and fractional waypoint index nearest to ``point``."""
    best_distance = float("inf")
    best_progress = 0.0
    for index, (start, end) in enumerate(zip(points, points[1:])):
        dx = float(end[0]) - float(start[0])
        dy = float(end[1]) - float(start[1])
        length_sq = dx * dx + dy * dy
        fraction = 0.0 if length_sq == 0.0 else max(0.0, min(1.0, (
            (point[0] - float(start[0])) * dx
            + (point[1] - float(start[1])) * dy
        ) / length_sq))
        projected = (
            float(start[0]) + dx * fraction,
            float(start[1]) + dy * fraction,
        )
        distance = math.dist(point, projected)
        if distance < best_distance:
            best_distance = distance
            best_progress = index + fraction
    return best_distance, best_progress


def _align_road_geometry(
    corridor: Dict[str, object], settlements: Sequence[object],
) -> Optional[Dict[str, object]]:
    """Clip a traced corridor to settlements and pin named stops exactly."""
    settlements = [place for place in settlements if not getattr(place, "underdark", False)]
    if not settlements:
        return None
    points = corridor["points"]
    assert isinstance(points, list)
    if len(points) < 2:
        return None

    def words(value: object) -> str:
        text = unicodedata.normalize("NFKD", str(value or ""))
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        return " ".join(re.findall(r"[a-z0-9]+", text.lower()))

    route_name = " %s " % words(corridor["name"])
    stop_ids = {str(stop) for stop in corridor.get("stops", [])}
    named = []
    for settlement in settlements:
        location_name = words(getattr(settlement, "name", ""))
        named_in_title = (
            len(location_name) >= 4
            and " %s " % location_name in route_name
        )
        if settlement.id not in stop_ids and not named_in_title:
            continue
        location = (float(settlement.x), float(settlement.y))
        distance, progress = _point_on_road(location, points)
        if distance <= ROAD_ENDPOINT_LIMIT_MILES:
            named.append((progress, settlement))

    def nearest(point: Sequence[float]) -> Optional[object]:
        distance, settlement = min(
            (math.dist(point, (float(item.x), float(item.y))), item)
            for item in settlements
        )
        return settlement if distance <= ROAD_ENDPOINT_LIMIT_MILES else None

    named.sort(key=lambda item: item[0])
    start = named[0][1] if named and math.dist(
        points[0], (float(named[0][1].x), float(named[0][1].y)),
    ) <= ROAD_ENDPOINT_LIMIT_MILES else nearest(points[0])
    end = named[-1][1] if named and math.dist(
        points[-1], (float(named[-1][1].x), float(named[-1][1].y)),
    ) <= ROAD_ENDPOINT_LIMIT_MILES else nearest(points[-1])
    if start is None or end is None or start.id == end.id:
        return None

    anchors = [(0.0, start)]
    anchors.extend(
        (progress, settlement) for progress, settlement in named
        if settlement.id not in (start.id, end.id)
    )
    anchors.append((float(len(points) - 1), end))
    anchors.sort(key=lambda item: item[0])

    aligned: List[List[float]] = []
    anchor_indexes = []
    previous = -1.0
    locations = []
    for progress, settlement in anchors:
        for index in range(math.floor(previous) + 1, math.ceil(progress)):
            if 0 < index < len(points) - 1:
                aligned.append([float(points[index][0]), float(points[index][1])])
        aligned.append([float(settlement.x), float(settlement.y)])
        anchor_indexes.append(len(aligned) - 1)
        locations.append(settlement.id)
        previous = progress

    return {
        **corridor,
        "points": aligned,
        "anchors": anchor_indexes,
        "locations": locations,
    }


def road_geometries(settlements: Sequence[object]) -> List[Dict[str, object]]:
    """Load traced roads and convert FPS coordinates to world miles."""
    path = road_geometry_path()
    if path is None:
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read road geometry file %s: %s" % (path, exc))
    corridors = _parse_road_geometries(payload)
    waterdeep = next(
        (s for s in settlements if normalise(getattr(s, "name", "")) == "waterdeep"),
        None,
    )
    if waterdeep is None:
        return []
    result: List[Dict[str, object]] = []
    for corridor in corridors:
        fps = corridor["fps"]
        assert isinstance(fps, list)
        aligned = _align_road_geometry({
            "id": corridor["id"],
            "name": corridor["name"],
            "surface": corridor["surface"],
            "stops": corridor.get("stops", []),
            "exclusive_stops": corridor.get("exclusive_stops", False),
            "points": [
                [
                    float(waterdeep.x) + float(point[0]) * FPS_MILES_PER_UNIT,
                    float(waterdeep.y) - float(point[1]) * FPS_MILES_PER_UNIT,
                ]
                for point in fps
            ],
        }, settlements)
        if aligned is not None:
            result.append(aligned)
    return result


def road_connections(
    settlements: Sequence[object], *, include_spanning: bool = False,
) -> List[Dict[str, object]]:
    """Return consecutive settlements served by each traced road corridor."""
    places = [place for place in settlements if not getattr(place, "underdark", False)]
    connections: List[Dict[str, object]] = []
    for road in road_geometries(places):
        points = road["points"]
        assert isinstance(points, list)
        cumulative = [0.0]
        for start_point, end_point in zip(points, points[1:]):
            cumulative.append(cumulative[-1] + math.dist(start_point, end_point))

        def distance_at(progress: float) -> float:
            index = min(int(progress), len(points) - 2)
            return cumulative[index] + (progress - index) * (
                cumulative[index + 1] - cumulative[index]
            )

        nearby: Dict[str, Tuple[float, object]] = {}

        # Preserve explicit endpoint/title anchors even where another road is
        # marginally closer at a junction.
        for anchor_index, location_id in zip(road.get("anchors", []), road.get("locations", [])):
            settlement = next(
                (place for place in places if place.id == location_id), None
            )
            if settlement is None:
                continue
            nearby[settlement.id] = (float(anchor_index), settlement)

        for settlement in places:
            if settlement.id in nearby:
                continue
            if road.get("exclusive_stops"):
                continue
            distance, progress = _point_on_road(
                (float(settlement.x), float(settlement.y)), points
            )
            if distance <= ROAD_ENDPOINT_LIMIT_MILES:
                nearby[settlement.id] = (progress, settlement)

        ordered = sorted(
            nearby.values(), key=lambda item: (item[0], item[1].id)
        )
        pairs = (
            (start_index, end_index)
            for start_index in range(len(ordered) - 1)
            for end_index in range(start_index + 1, len(ordered))
            if include_spanning or end_index == start_index + 1
        )
        for start_index, end_index in pairs:
            start_progress, start = ordered[start_index]
            end_progress, end = ordered[end_index]
            if start.id == end.id:
                continue
            start_access, _ = _point_on_road((float(start.x), float(start.y)), points)
            end_access, _ = _point_on_road((float(end.x), float(end.y)), points)
            connections.append({
                "a": start.id,
                "b": end.id,
                "kind": str(road["surface"]),
                "name": str(road["name"]),
                "distance": distance_at(end_progress) - distance_at(start_progress)
                + start_access + end_access,
                "consecutive": end_index == start_index + 1,
            })
    return connections


def sea_air_geometry_path() -> Optional[Path]:
    """Find optional water-routed sea and schematic air polylines."""
    root = project_root()
    for folder in (root / "maps", root, Path.cwd() / "maps", Path.cwd()):
        for name in SEA_AIR_GEOMETRY_NAMES:
            path = folder / name
            if path.is_file():
                return path
        pointer = folder / SEA_AIR_GEOMETRY_POINTER
        if pointer.is_file():
            try:
                target = Path(pointer.read_text(encoding="utf-8").strip()).expanduser()
            except (OSError, UnicodeError) as exc:
                raise AtlasError(
                    "cannot read sea/air geometry pointer %s: %s" % (pointer, exc)
                )
            if not target.is_file():
                raise AtlasError(
                    "sea/air geometry pointer %s does not point to a file: %s"
                    % (pointer, target)
                )
            return target
    return None


def _parse_sea_air_geometries(payload: object) -> List[Dict[str, object]]:
    """Validate drawable legs from the water-routed sea/air route export."""
    if not isinstance(payload, dict) or not isinstance(payload.get("routes"), list):
        raise AtlasError("sea/air geometry file needs a routes array")
    geometries: List[Dict[str, object]] = []
    for route in payload["routes"]:
        if not isinstance(route, dict):
            raise AtlasError("every sea/air route must be an object")
        modes = route.get("modes")
        if not isinstance(modes, list):
            modes = str(route.get("mode", "")).split("+")
        clean_modes = [str(mode).strip().lower() for mode in modes if str(mode).strip()]
        primary = clean_modes[0] if clean_modes else "sea"
        legs = route.get("legs")
        if not isinstance(legs, list):
            continue
        for leg in legs:
            if not isinstance(leg, dict):
                raise AtlasError("every sea/air route leg must be an object")
            status = str(leg.get("status", "")).strip().lower()
            points = leg.get("water_pixels") if status == "water_routed" else leg.get("pixels")
            if status == "mapped_schematic" and "air" not in clean_modes:
                continue
            if status not in ("water_routed", "mapped_schematic"):
                continue
            if not isinstance(points, list) or len(points) < 2:
                continue
            clean_points: List[List[float]] = []
            for point in points:
                if not isinstance(point, list) or len(point) != 2:
                    raise AtlasError("sea/air route leg has an invalid pixel waypoint")
                try:
                    clean_points.append([float(point[0]), float(point[1])])
                except (TypeError, ValueError) as exc:
                    raise AtlasError(
                        "sea/air route leg has an invalid pixel waypoint"
                    ) from exc
            geometries.append({
                "id": "%s-leg-%s" % (
                    str(route.get("route_id", "")).strip(),
                    str(leg.get("leg_index", "")).strip(),
                ),
                "name": str(route.get("name", "")).strip(),
                "from": str(leg.get("from", "")).strip(),
                "to": str(leg.get("to", "")).strip(),
                "surface": primary,
                "multimodal": len(clean_modes) > 1,
                "pixels": clean_points,
            })
    return geometries


def sea_air_geometries(settlements: Sequence[object]) -> List[Dict[str, object]]:
    """Load sea/air legs and convert calibrated poster pixels to world miles."""
    path = sea_air_geometry_path()
    if path is None:
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AtlasError("cannot read sea/air geometry file %s: %s" % (path, exc))
    geometries = _parse_sea_air_geometries(payload)
    waterdeep = next(
        (s for s in settlements if normalise(getattr(s, "name", "")) == "waterdeep"),
        None,
    )
    if waterdeep is None:
        return []
    miles_per_pixel = FPS_MILES_PER_UNIT / POSTER_PIXELS_PER_FPS_UNIT
    result: List[Dict[str, object]] = []
    for geometry in geometries:
        pixels = geometry["pixels"]
        assert isinstance(pixels, list)
        result.append({
            "id": geometry["id"],
            "name": geometry["name"],
            "from": geometry["from"],
            "to": geometry["to"],
            "surface": geometry["surface"],
            "multimodal": geometry["multimodal"],
            "points": [
                [
                    float(waterdeep.x) + (float(point[0]) - 694.0) * miles_per_pixel,
                    float(waterdeep.y) + (float(point[1]) - 682.0) * miles_per_pixel,
                ]
                for point in pixels
            ],
        })
    return result

# ---------------------------------------------------------------------------
# coastlines
# ---------------------------------------------------------------------------

#: The Faerun mainland, walked as a single closed loop: down the Sword Coast,
#: east along the Great Sea, north up the edge of the Endless Waste, then back
#: west along the Cold Lands to Icewind Dale.
MAINLAND: List[Point] = [
    (395, 195), (350, 255), (385, 320), (425, 395), (450, 480),
    (462, 560), (478, 645), (486, 730), (474, 812), (498, 890),
    (524, 952), (546, 1035), (556, 1125), (568, 1205), (556, 1290),
    (538, 1378), (520, 1466), (508, 1560), (516, 1656), (528, 1745),
    (544, 1836), (536, 1922), (548, 2015), (566, 2110), (578, 2205),
    (566, 2300), (578, 2400), (596, 2492), (618, 2570), (646, 2648),
    (684, 2716), (744, 2764), (824, 2792), (906, 2802), (1006, 2786),
    (1108, 2802), (1212, 2822), (1352, 2832), (1500, 2822), (1652, 2804),
    (1804, 2792), (1952, 2778), (2078, 2760), (2152, 2698), (2206, 2596),
    (2228, 2404), (2238, 2206), (2228, 2008), (2238, 1806), (2228, 1604),
    (2238, 1402), (2228, 1200), (2238, 998), (2226, 800), (2196, 604),
    (2148, 452), (2004, 398), (1852, 418), (1700, 448), (1552, 476),
    (1400, 496), (1252, 478), (1104, 440), (956, 402), (854, 370),
    (778, 332), (700, 300), (622, 288), (560, 302), (500, 275),
    (410, 215),
]

#: Chult, drawn separately so the Shining Sea stays open water.
CHULT: List[Point] = [
    (690, 2860), (704, 2818), (742, 2772), (810, 2766), (872, 2802),
    (908, 2876), (908, 2940), (892, 3018), (830, 3066), (756, 3054),
    (700, 3000), (672, 2930),
]

LANDMASSES: List[Tuple[str, List[Point]]] = [
    ("Faerun", MAINLAND),
    ("Chult", CHULT),
]

# ---------------------------------------------------------------------------
# inland seas, carved back out of the landmasses
# ---------------------------------------------------------------------------

SEAS: List[Tuple[str, List[Point]]] = [
    ("Sea of Fallen Stars", [
        (1566, 1738), (1650, 1690), (1740, 1652), (1826, 1634), (1888, 1660),
        (1924, 1576), (1962, 1516), (1986, 1580), (1956, 1672), (1930, 1752),
        (1946, 1838), (1902, 1908), (1820, 1950), (1720, 1968), (1622, 1958),
        (1560, 1912), (1536, 1836),
    ]),
    ("Moonsea", [
        (1548, 1408), (1620, 1384), (1700, 1374), (1780, 1380), (1840, 1400),
        (1806, 1436), (1730, 1444), (1650, 1440), (1580, 1430),
    ]),
    ("Lake of Steam", [
        (896, 2178), (980, 2156), (1070, 2158), (1148, 2182), (1090, 2216),
        (1000, 2222), (930, 2210),
    ]),
    ("Lake Ashane", [
        (1930, 1160), (1980, 1150), (1996, 1250), (1946, 1268),
    ]),
]

# ---------------------------------------------------------------------------
# mountain ranges: a spine polyline, a half-width in miles, and a peak weight
# ---------------------------------------------------------------------------

RANGES: List[Tuple[str, List[Point], float, float]] = [
    ("Spine of the World", [
        (430, 560), (560, 540), (700, 530), (840, 545), (960, 580), (1060, 620),
    ], 62.0, 1.00),
    ("Novularond", [(1130, 420), (1250, 442)], 46.0, 0.72),
    ("Nether Mountains", [(880, 700), (980, 690), (1072, 702)], 42.0, 0.70),
    ("Sword Mountains", [(602, 1012), (622, 1112), (638, 1210)], 34.0, 0.60),
    ("Greypeak Mountains", [(880, 1080), (900, 1180), (916, 1272)], 40.0, 0.72),
    ("Storm Horns", [(1400, 1630), (1440, 1700), (1470, 1760)], 36.0, 0.66),
    ("Galena Mountains", [
        (1560, 900), (1600, 1002), (1630, 1110), (1652, 1220),
    ], 42.0, 0.78),
    ("Earthspur Mountains", [(1620, 1180), (1662, 1282), (1692, 1372)], 40.0, 0.72),
    ("Sunrise Mountains", [(2060, 1420), (2076, 1560), (2086, 1700)], 38.0, 0.70),
    ("Cloud Peaks", [(620, 2020), (720, 2036), (810, 2050)], 36.0, 0.66),
    ("Snowflake Mountains", [(900, 2100), (962, 2142)], 32.0, 0.60),
    ("Marching Mountains", [(700, 2480), (800, 2500), (900, 2512)], 36.0, 0.60),
    ("Orsraun Mountains", [(1560, 2020), (1650, 2050), (1740, 2062)], 38.0, 0.66),
    ("Star Mountains", [(1980, 1980), (2042, 2042)], 36.0, 0.62),
    ("Firepeaks of Chult", [(760, 2940), (830, 2962)], 32.0, 0.55),
]

# ---------------------------------------------------------------------------
# broad terrain zones
# ---------------------------------------------------------------------------

ZONES: List[Tuple[str, str, List[Point]]] = [
    ("Anauroch", "desert", [
        (1120, 700), (1300, 660), (1430, 720), (1470, 900), (1450, 1100),
        (1380, 1290), (1260, 1360), (1150, 1280), (1100, 1080), (1090, 880),
    ]),
    ("The Great Glacier", "glacier", [
        (1500, 340), (1750, 330), (1980, 360), (2060, 470), (1980, 600),
        (1780, 650), (1580, 620), (1470, 500),
    ]),
    ("Icewind Dale", "tundra", [
        (378, 190), (500, 202), (540, 300), (470, 362), (388, 330),
    ]),
    ("The Frozenfar", "taiga", [
        (520, 330), (760, 350), (1000, 430), (1010, 540), (760, 500),
        (540, 470),
    ]),
    ("The High Forest", "forest", [
        (700, 900), (830, 860), (940, 930), (950, 1080), (870, 1180),
        (750, 1150), (690, 1030),
    ]),
    ("Cormanthor", "forest", [
        (1560, 1560), (1700, 1540), (1790, 1610), (1760, 1730), (1640, 1760),
        (1560, 1690),
    ]),
    ("The Chondalwood", "forest", [
        (1560, 2100), (1700, 2090), (1760, 2180), (1620, 2220), (1540, 2180),
    ]),
    ("Chult", "jungle", [
        (682, 2866), (708, 2816), (746, 2774), (816, 2768), (878, 2806),
        (900, 2880), (900, 3010), (760, 3060), (690, 2980),
    ]),
    ("The Calim Desert", "desert", [
        (560, 2480), (700, 2450), (800, 2510), (790, 2640), (660, 2690),
        (570, 2610),
    ]),
    ("Plain of Standing Stones", "desert", [
        (1450, 1200), (1560, 1180), (1580, 1300), (1470, 1330),
    ]),
    ("Raurin", "desert", [
        (2050, 1980), (2230, 1960), (2240, 2260), (2060, 2280),
    ]),
    ("The Endless Waste", "steppe", [
        (2120, 700), (2262, 690), (2270, 1400), (2130, 1400),
    ]),
    ("The Shaar", "steppe", [
        (1150, 2400), (1500, 2380), (1600, 2560), (1300, 2620), (1150, 2560),
    ]),
    ("The Vast Swamp", "marsh", [
        (1462, 1830), (1560, 1820), (1584, 1892), (1486, 1904),
    ]),
    ("The Farsea Marshes", "marsh", [
        (1310, 1600), (1400, 1590), (1412, 1660), (1320, 1670),
    ]),
]

# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------


def _bbox(poly: Poly) -> Tuple[float, float, float, float]:
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))


def _inside(px: float, py: float, poly: Poly,
            box: Tuple[float, float, float, float]) -> bool:
    """Crossing-number point-in-polygon test with a bounding-box shortcut."""
    if px < box[0] or px > box[2] or py < box[1] or py > box[3]:
        return False
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > py) != (yj > py):
            t = (py - yi) / (yj - yi)
            if px < xi + (xj - xi) * t:
                inside = not inside
        j = i
    return inside


def _seg_distance(px: float, py: float, ax: float, ay: float,
                  bx: float, by: float) -> float:
    dx = bx - ax
    dy = by - ay
    length = dx * dx + dy * dy
    if length <= 0.0:
        t = 0.0
    else:
        t = ((px - ax) * dx + (py - ay) * dy) / length
        if t < 0.0:
            t = 0.0
        elif t > 1.0:
            t = 1.0
    qx = ax + t * dx
    qy = ay + t * dy
    return math.hypot(px - qx, py - qy)


def _polyline_distance(px: float, py: float, line: Sequence[Point]) -> float:
    best = 1.0e9
    for i in range(len(line) - 1):
        ax, ay = line[i]
        bx, by = line[i + 1]
        d = _seg_distance(px, py, ax, ay, bx, by)
        if d < best:
            best = d
    return best


def _smooth(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def _hash2(ix: int, iy: int, seed: int) -> float:
    h = (ix * 374761393 + iy * 668265263 + seed * 1274126177) & 0x7FFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0x7FFFFFFF
    h = (h ^ (h >> 16)) & 0x7FFFFFFF
    return (h & 0xFFFF) / 65535.0


def _value_noise(x: float, y: float, seed: int) -> float:
    ix = math.floor(x)
    iy = math.floor(y)
    fx = _smooth(x - ix)
    fy = _smooth(y - iy)
    a = _hash2(ix, iy, seed)
    b = _hash2(ix + 1, iy, seed)
    c = _hash2(ix, iy + 1, seed)
    d = _hash2(ix + 1, iy + 1, seed)
    top = a + (b - a) * fx
    bottom = c + (d - c) * fx
    return top + (bottom - top) * fy


def _fbm(x: float, y: float, seed: int) -> float:
    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    norm = 0.0
    for octave in range(3):
        total += _value_noise(x * frequency, y * frequency, seed + octave) * amplitude
        norm += amplitude
        amplitude *= 0.5
        frequency *= 2.13
    return total / norm


# ---------------------------------------------------------------------------
# rasteriser
# ---------------------------------------------------------------------------

#: how far a settlement pushes back the sea, in miles
BLOB_MAINLAND = 78.0
BLOB_ISLAND = 58.0
#: a settlement standing inside one of the inland seas only reclaims this much
BLOB_IN_SEA = 40.0

_MAINLAND_BOXES = [(name, poly, _bbox(poly)) for name, poly in LANDMASSES]
_SEA_BOXES = [(name, poly, _bbox(poly)) for name, poly in SEAS]
_ZONE_BOXES = [(name, kind, poly, _bbox(poly)) for name, kind, poly in ZONES]


def _terrain_code(name: str) -> str:
    return CODES.get(name, CODES["plains"])


# ---------------------------------------------------------------------------
# adapting the frame to a realignment
# ---------------------------------------------------------------------------


def poster_frame(settlements: Sequence[object]) -> Optional[Rect]:
    """The rectangle the user's poster map occupies, in world miles.

    The survey knows which pixel of the poster is the anchor town and how many
    miles a pixel covers, so the image has a real footprint in the same space
    the terrain is drawn in.  Returns None when there is no survey, no poster,
    or anything at all wrong with either: the map has to draw regardless.
    """
    try:
        from . import atlas as atlas_mod

        fit = atlas_mod.underlay_placement(settlements)
        if not fit.get("available"):
            return None
        x = float(fit["x"])
        y = float(fit["y"])
        w = float(fit["widthMiles"])
        h = float(fit["heightMiles"])
    except Exception:  # noqa: BLE001 - a poster must never cost us the map
        return None
    if not (w > 0.0 and h > 0.0):
        return None
    return (x, y, x + w, y + h)


def _grid_for(width: float, height: float) -> Tuple[int, int]:
    """A heightfield sized for a frame this big, with cells as square as we can.

    Cells are held at CELL_MILES until the total count runs past MAX_CELLS, and
    the reduction after that is applied to both axes at once so they stay
    square.  There is deliberately no per-axis floor: a frame that has grown
    much wider than it is tall should spend its budget on width, and pinning
    one axis to the shipped number is what would make the cells oblong again.
    """
    w = max(2, int(round(width / CELL_MILES)))
    h = max(2, int(round(height / CELL_MILES)))
    if w * h > MAX_CELLS:
        shrink = math.sqrt((w * h) / float(MAX_CELLS))
        w = max(2, int(w / shrink))
        h = max(2, int(h / shrink))
    return min(w, MAX_GRID_W), min(h, MAX_GRID_H)


def _resolve_frame(settlements: Sequence[object], calibrated: bool) -> None:
    """Point BOUNDS and the grid size at the world we are about to draw.

    The frame grows - never shrinks - to hold three things:

    * the shipped bounds, which is what the hand-drawn terrain was authored
      against and must always fit;
    * the poster map's own footprint, whenever the survey can work one out, so
      the ground plane spans the whole image instead of leaving three quarters
      of it hanging off the eastern edge with nothing underneath;
    * every market plus a margin once a realignment is in force, because a
      survey reaches considerably further east than the hand-placed
      coordinates ever did.

    With none of those in play this restores the shipped frame exactly, so an
    install with no poster and no calibration draws what it always drew.
    """
    global BOUNDS, GRID_W, GRID_H

    west, north, east, south = SHIPPED_BOUNDS

    poster = poster_frame(settlements)
    if poster is not None:
        west = min(west, poster[0])
        north = min(north, poster[1])
        east = max(east, poster[2])
        south = max(south, poster[3])

    if calibrated:
        for s in settlements:
            try:
                x = float(s.x)  # type: ignore[attr-defined]
                y = float(s.y)  # type: ignore[attr-defined]
            except (AttributeError, TypeError, ValueError):
                continue
            west = min(west, x - FRAME_MARGIN)
            north = min(north, y - FRAME_MARGIN)
            east = max(east, x + FRAME_MARGIN)
            south = max(south, y + FRAME_MARGIN)

    BOUNDS = (west, north, east, south)
    if BOUNDS == SHIPPED_BOUNDS:
        GRID_W, GRID_H = SHIPPED_GRID_W, SHIPPED_GRID_H
        return
    GRID_W, GRID_H = _grid_for(east - west, south - north)


def _warped_geometry(warp):
    """Carry the hand-drawn coastline along with a realignment.

    The landmasses, seas, ranges and climate zones were drawn to fit the
    shipped coordinates.  Moving the markets without moving the ink would put
    Waterdeep in the ocean, so the same warp that repositions the markets is
    pushed through every polygon vertex.  It is exact at each control point and
    smooth in between, so the coast keeps its shape and simply follows the
    towns it was drawn around.
    """
    if warp is None:
        return _MAINLAND_BOXES, _SEA_BOXES, _ZONE_BOXES, RANGES

    def move(poly):
        return [warp(px, py) for px, py in poly]

    mainland = [(name, move(poly)) for name, poly in LANDMASSES]
    seas = [(name, move(poly)) for name, poly in SEAS]
    zones = [(name, kind, move(poly)) for name, kind, poly in ZONES]
    ranges = [(name, move(line), width, peak)
              for name, line, width, peak in RANGES]
    return (
        [(n, p, _bbox(p)) for n, p in mainland],
        [(n, p, _bbox(p)) for n, p in seas],
        [(n, k, p, _bbox(p)) for n, k, p in zones],
        ranges,
    )


def _centre(points: Sequence[Point]) -> Point:
    n = float(len(points))
    return (sum(p[0] for p in points) / n, sum(p[1] for p in points) / n)


def terrain_landmarks() -> List[Tuple[str, Point]]:
    """The named terrain of the map, each reduced to one reference point.

    These are the things a poster puts a label on - seas, deserts, forests,
    mountain ranges - so they are exactly the features a survey of that poster
    can tell us the true position of.  The landmasses are deliberately left
    out: "Faerun" is the whole continent and its centre means nothing.
    """
    marks: List[Tuple[str, Point]] = [(n, _centre(p)) for n, p in SEAS]
    marks += [(n, _centre(p)) for n, _kind, p in ZONES]
    marks += [(n, _centre(line)) for n, line, _w, _peak in RANGES]
    return marks


def _terrain_pairs(settlements: Sequence[object], coarse) -> List[Tuple[Point, Point]]:
    """Extra warp anchors that pin the scenery, not just the towns.

    Warping the map from market positions alone works where markets are dense
    and drifts badly where they are not - and the empty quarters are precisely
    the ones with the most map in them: Anauroch, the Great Glacier, Raurin,
    the open Sea of Fallen Stars.  The survey names those features too, so we
    can nail them down directly instead of extrapolating from the nearest town
    several hundred miles away.

    `coarse` is the market-only warp, used as a sanity check: an anchor is kept
    only if it agrees roughly with where the towns already say the feature
    should go.  That rejects a label matched to the wrong feature without
    needing to understand the artwork.
    """
    from . import atlas as atlas_mod

    survey = atlas_mod.load_atlas()
    if not survey:
        return []
    report = atlas_mod.align(settlements, atlas=survey)
    surveyed = report.get("features") or {}
    if not surveyed:
        return []

    pairs: List[Tuple[Point, Point]] = []
    for name, src in terrain_landmarks():
        found = surveyed.get(atlas_mod.normalise(name))
        if not found:
            continue
        target = (float(found["x"]), float(found["y"]))
        predicted = coarse(src[0], src[1])
        drift = math.hypot(target[0] - predicted[0], target[1] - predicted[1])
        if drift <= TERRAIN_ANCHOR_LIMIT:
            pairs.append((src, target))
    return pairs


def terrain_alignment(
    settlements: Sequence[object],
    points: Optional[Sequence[Dict[str, object]]] = None,
) -> Dict[str, object]:
    """Report how the scenery was pinned, for the CLI and the map screen.

    Rebuilding the map is otherwise invisible - the terrain simply comes out
    somewhere slightly different - so this says which features the survey
    placed, which it never mentioned, and which were rejected for disagreeing
    with the towns around them.
    """
    landmarks = terrain_landmarks()
    out: Dict[str, object] = {
        "landmarks": len(landmarks), "anchored": [], "rejected": [],
        "unsurveyed": [], "limit": TERRAIN_ANCHOR_LIMIT,
    }
    try:
        from . import atlas as atlas_mod

        # Callers previewing an alignment pass the control points they are
        # about to save, so the report describes the map they would get rather
        # than the one they already have.
        control = list(points) if points is not None else load_control_points()
        base = base_coordinates(settlements)
        pairs = [
            (base[p["id"]], (float(p["x"]), float(p["y"])))
            for p in control if p["id"] in base
        ]
        coarse = build_warp(pairs)

        survey = atlas_mod.load_atlas()
        surveyed = atlas_mod.align(
            settlements, atlas=survey)["features"] if survey else {}

        for name, src in landmarks:
            found = surveyed.get(atlas_mod.normalise(name))
            if not found:
                out["unsurveyed"].append(name)  # type: ignore[union-attr]
                continue
            predicted = coarse(src[0], src[1])
            drift = math.hypot(float(found["x"]) - predicted[0],
                               float(found["y"]) - predicted[1])
            row = {"name": name, "survey": found["name"],
                   "drift": round(drift, 1)}
            key = "anchored" if drift <= TERRAIN_ANCHOR_LIMIT else "rejected"
            out[key].append(row)  # type: ignore[union-attr]
    except Exception as exc:  # pragma: no cover - diagnostics only
        out["error"] = str(exc)
    return out


def surveyed_places_base(settlements: Sequence[object]) -> List[Dict[str, object]]:
    """Surveyed towns brought back to the shipped map coordinate space.

    This is also the stable pre-calibration position stored on inferred markets.
    Keeping it separate from their current position means clearing or replacing
    a calibration cannot compound the old warp.
    """
    from . import atlas as atlas_mod

    places = atlas_mod.surveyed_places(settlements)
    if not places:
        return places

    report = atlas_mod.align(settlements)
    base = base_coordinates(settlements)
    pairs = [
        ((float(m["x"]), float(m["y"])), base[m["id"]])
        for m in report["matched"] if m["id"] in base
    ]
    if not pairs:
        return places

    back = build_warp(pairs)
    for p in places:
        x, y = back(float(p["x"]), float(p["y"]))
        p["x"] = round(x, 1)
        p["y"] = round(y, 1)
    return places


def surveyed_places(settlements: Sequence[object]) -> List[Dict[str, object]]:
    """Surveyed towns not already modelled, in the map's current space."""
    if not load_control_points():
        return surveyed_places_base(settlements)

    # With a calibration in force the world already is aligned space.
    from . import atlas as atlas_mod
    return atlas_mod.surveyed_places(settlements)


def _active_warp(settlements: Sequence[object]):
    """The warp currently in force, or None when nothing is calibrated."""
    try:
        points = load_control_points()
        if not points:
            return None
        base = base_coordinates(settlements)
        if not any(p["id"] in base for p in points):
            return None

        coarse = warp_for(settlements, points)
        pairs = [
            (base[p["id"]], (float(p["x"]), float(p["y"])))
            for p in points if p["id"] in base
        ]
        extra = _terrain_pairs(settlements, coarse)
        if not extra:
            return coarse
        # Markets stay exact - the warp reproduces every control point it is
        # given - so adding scenery anchors refines the ink without moving a
        # single town off the spot the survey put it on.
        return build_warp(pairs + extra)
    except Exception:
        # A calibration is a convenience; a broken one must never stop the map
        # from drawing.
        return None


def _build(settlements: Sequence[object]) -> Dict[str, object]:
    warp = _active_warp(settlements)
    _resolve_frame(settlements, warp is not None)
    mainland_boxes, sea_boxes, zone_boxes, ranges = _warped_geometry(warp)

    x0, y0, x1, y1 = BOUNDS
    cell_w = (x1 - x0) / GRID_W
    cell_h = (y1 - y0) / GRID_H
    count = GRID_W * GRID_H

    contexts, context_path = location_terrain_contexts()
    full_grid, full_grid_path = full_terrain_grid()
    if full_grid_path:
        context_path = full_grid_path
    matched_contexts = 0
    applied_grid_cells = 0

    # The survey contains geographic features as well as settlements. Anchor
    # every usable FPS cell on Waterdeep so mountain ranges, forests, marshes,
    # and deserts can shape the terrain even when they are not market records.
    waterdeep = next(
        (s for s in settlements if normalise(getattr(s, "name", "")) == "waterdeep"),
        None,
    )
    survey_seeds: List[Tuple[float, float, str, float]] = []
    if waterdeep is not None:
        for context in contexts.values():
            east = context.get("east")
            north = context.get("north")
            terrain = str(context.get("terrain") or "")
            if terrain not in CODES or east is None or north is None:
                continue
            survey_seeds.append((
                float(waterdeep.x) + float(east),
                float(waterdeep.y) - float(north),
                terrain,
                float(context.get("floor") or 0.0),
            ))

    # settlement seeds: position, blob radius, terrain, relief floor, surveyed
    seeds: List[Tuple[float, float, float, str, float, bool]] = []
    for s in settlements:
        landmass = getattr(s, "landmass", "faerun") or "faerun"
        radius = BLOB_MAINLAND if landmass == "faerun" else BLOB_ISLAND
        terrain = str(getattr(s, "terrain", "plains") or "plains")
        floor = 0.0
        context = contexts.get(normalise(getattr(s, "name", "")))
        surveyed = context is not None
        if context:
            matched_contexts += 1
            terrain = str(context.get("terrain") or terrain)
            floor = float(context.get("floor") or 0.0)
        seeds.append((float(s.x), float(s.y), radius, terrain, floor, surveyed))

    land = [False] * count
    height = [0.0] * count
    codes = [CODES["ocean"]] * count

    for gy in range(GRID_H):
        wy = y0 + (gy + 0.5) * cell_h
        row = gy * GRID_W
        for gx in range(GRID_W):
            wx = x0 + (gx + 0.5) * cell_w
            idx = row + gx
            direct_terrain = ""
            if full_grid and waterdeep is not None:
                direct_terrain = _full_terrain_cell(
                    full_grid,
                    wx - float(waterdeep.x),
                    float(waterdeep.y) - wy,
                )
                if direct_terrain:
                    applied_grid_cells += 1

            in_sea = False
            for _name, poly, box in sea_boxes:
                if _inside(wx, wy, poly, box):
                    in_sea = True
                    break

            base_land = False
            if not in_sea:
                for _name, poly, box in mainland_boxes:
                    if _inside(wx, wy, poly, box):
                        base_land = True
                        break

            # nearest settlement, both raw and normalised by its blob radius
            near_terrain = ""
            near_floor = 0.0
            near_surveyed = False
            near_dist = 1.0e9
            near_ratio = 1.0e9
            for sx, sy, radius, terrain, floor, surveyed in seeds:
                dx = sx - wx
                if dx > 260.0 or dx < -260.0:
                    continue
                dy = sy - wy
                if dy > 260.0 or dy < -260.0:
                    continue
                d = math.hypot(dx, dy)
                if d < near_dist:
                    near_dist = d
                    near_terrain = terrain
                    near_floor = floor
                    near_surveyed = surveyed
                ratio = d / radius
                if ratio < near_ratio:
                    near_ratio = ratio

            survey_terrain = ""
            survey_floor = 0.0
            survey_dist = 1.0e9
            for sx, sy, terrain, floor in survey_seeds:
                dx = sx - wx
                if dx > SURVEY_INFLUENCE_MILES or dx < -SURVEY_INFLUENCE_MILES:
                    continue
                dy = sy - wy
                if dy > SURVEY_INFLUENCE_MILES or dy < -SURVEY_INFLUENCE_MILES:
                    continue
                d = math.hypot(dx, dy)
                if d < survey_dist:
                    survey_dist = d
                    survey_terrain = terrain
                    survey_floor = floor

            if direct_terrain in ("ocean", "water"):
                is_land = near_dist <= BLOB_IN_SEA
                if is_land:
                    direct_terrain = ""
            elif direct_terrain:
                is_land = True
            elif in_sea:
                is_land = near_dist <= BLOB_IN_SEA
            else:
                is_land = base_land or near_ratio <= 1.0
            land[idx] = is_land

            if not is_land:
                continue

            zone_kind = ""
            for _name, kind, poly, box in zone_boxes:
                if _inside(wx, wy, poly, box):
                    zone_kind = kind
                    break

            h = 0.05
            for _name, line, width, peak in ranges:
                reach = width * 2.4
                d = _polyline_distance(wx, wy, line)
                if d < reach:
                    fall = _smooth(1.0 - d / reach)
                    lift = peak * fall
                    if lift > h:
                        h = lift

            if near_dist <= 55.0:
                if near_terrain == "mountains" and h < 0.58:
                    h = 0.58
                elif near_terrain == "hills" and h < 0.28:
                    h = 0.28

            if zone_kind == "glacier" and h < 0.32:
                h = 0.32
            elif zone_kind == "desert" and h < 0.10:
                h = 0.10
            elif zone_kind == "forest" and h < 0.11:
                h = 0.11
            elif zone_kind == "steppe" and h < 0.09:
                h = 0.09
            elif zone_kind == "marsh":
                h = min(h, 0.05)
            # The supplied survey describes a 10-mile containing cell, so it is
            # more local than the broad hand-drawn zones but should not spread
            # beyond the cells immediately surrounding its named location.
            if near_surveyed and near_dist <= 35.0 and near_floor > h:
                h = near_floor
            if direct_terrain == "mountains" and h < 0.58:
                h = 0.58
            elif direct_terrain == "hills" and h < 0.28:
                h = 0.28
            elif direct_terrain and h < 0.06:
                h = 0.06
            if (
                survey_dist <= SURVEY_INFLUENCE_MILES
                and survey_floor > h
            ):
                h = survey_floor

            n = _fbm(wx / 130.0, wy / 130.0, 7717)
            h += (n - 0.5) * 0.11 * (0.45 + h)
            if h < 0.012:
                h = 0.012
            height[idx] = h

            if direct_terrain and direct_terrain in CODES:
                code = _terrain_code(direct_terrain)
            elif (
                survey_dist <= SURVEY_INFLUENCE_MILES
                and survey_terrain in CODES
            ):
                code = _terrain_code(survey_terrain)
            elif near_surveyed and near_dist <= 35.0 and near_terrain in CODES:
                code = _terrain_code(near_terrain)
            elif zone_kind in ("glacier", "jungle", "desert", "steppe", "marsh"):
                code = _terrain_code(zone_kind)
                if h > 0.66:
                    code = CODES["mountains"]
            elif h > 0.60:
                code = CODES["mountains"]
            elif h > 0.30:
                code = CODES["hills"]
            elif zone_kind:
                code = _terrain_code(zone_kind)
            elif near_terrain and near_dist <= 210.0:
                code = _terrain_code(near_terrain)
                if code == CODES["mountains"] or code == CODES["hills"]:
                    code = CODES["plains"]
            else:
                code = CODES["plains"]
            codes[idx] = code

    overrides = terrain_overrides()
    terrain_floor = {
        CODES["mountains"]: 0.58,
        CODES["hills"]: 0.28,
        CODES["forest"]: 0.11,
        CODES["taiga"]: 0.11,
        CODES["jungle"]: 0.11,
        CODES["desert"]: 0.10,
        CODES["steppe"]: 0.09,
        CODES["marsh"]: 0.03,
        CODES["plains"]: 0.05,
        CODES["coast"]: 0.03,
    }
    for key, code in overrides.items():
        try:
            gx_text, gy_text = key.split(",", 1)
            gx, gy = int(gx_text), int(gy_text)
        except ValueError:
            continue
        if gx < 0 or gx >= GRID_W or gy < 0 or gy >= GRID_H:
            continue
        idx = gy * GRID_W + gx
        is_water = code in (CODES["ocean"], CODES["water"])
        land[idx] = not is_water
        if not is_water:
            height[idx] = max(height[idx], terrain_floor.get(code, 0.05))

    _apply_sea_depth(land, height, codes)
    _relax(land, height)
    if not full_grid:
        _mark_coast(land, height, codes)
    for key, code in overrides.items():
        try:
            gx_text, gy_text = key.split(",", 1)
            gx, gy = int(gx_text), int(gy_text)
        except ValueError:
            continue
        if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
            codes[gy * GRID_W + gx] = code

    scaled = [int(round(v * 1000.0)) for v in height]
    return {
        "terrain": "".join(codes),
        "height": scaled,
        "land": land,
        # Carried out so the labels drawn over the relief follow the same warp
        # the relief itself was rasterised with.
        "ranges": [{"name": name, "line": [list(p) for p in line]}
                   for name, line, _w, _p in ranges],
        "bounds": list(BOUNDS),
        "grid": [GRID_W, GRID_H],
        "terrainSurvey": {
            "available": bool(contexts or full_grid),
            "path": context_path,
            "locations": len(contexts),
            "matched": matched_contexts,
            "appliedSamples": applied_grid_cells or len(survey_seeds),
            "sourceCells": int(full_grid.get("cell_count", 0)),
            "mode": "full-grid" if full_grid else "locations",
            "elevations": False,
        },
        "terrainOverrides": len(overrides),
    }


def _neighbours(idx: int) -> Iterable[int]:
    gx = idx % GRID_W
    gy = idx // GRID_W
    for dy in (-1, 0, 1):
        ny = gy + dy
        if ny < 0 or ny >= GRID_H:
            continue
        for dx in (-1, 0, 1):
            nx = gx + dx
            if nx < 0 or nx >= GRID_W or (dx == 0 and dy == 0):
                continue
            yield ny * GRID_W + nx


def _apply_sea_depth(land: List[bool], height: List[float],
                     codes: List[str]) -> None:
    """Give water cells a depth that grows away from the nearest shore."""
    count = GRID_W * GRID_H
    big = 10 ** 6
    dist = [0 if land[i] else big for i in range(count)]

    # two-pass chamfer transform over the grid
    for idx in range(count):
        gx = idx % GRID_W
        gy = idx // GRID_W
        best = dist[idx]
        if gx > 0 and dist[idx - 1] + 1 < best:
            best = dist[idx - 1] + 1
        if gy > 0 and dist[idx - GRID_W] + 1 < best:
            best = dist[idx - GRID_W] + 1
        dist[idx] = best
    for idx in range(count - 1, -1, -1):
        gx = idx % GRID_W
        gy = idx // GRID_W
        best = dist[idx]
        if gx < GRID_W - 1 and dist[idx + 1] + 1 < best:
            best = dist[idx + 1] + 1
        if gy < GRID_H - 1 and dist[idx + GRID_W] + 1 < best:
            best = dist[idx + GRID_W] + 1
        dist[idx] = best

    for idx in range(count):
        if land[idx]:
            continue
        d = min(dist[idx], 7)
        height[idx] = -0.015 - (d / 7.0) * 0.075
        codes[idx] = CODES["water"] if d <= 1 else CODES["ocean"]


def _relax(land: List[bool], height: List[float]) -> None:
    """One gentle smoothing pass so the relief is not blocky."""
    count = GRID_W * GRID_H
    out = list(height)
    for idx in range(count):
        if not land[idx]:
            continue
        total = height[idx] * 2.0
        weight = 2.0
        for n in _neighbours(idx):
            if not land[n]:
                continue
            total += height[n]
            weight += 1.0
        out[idx] = total / weight
    for idx in range(count):
        height[idx] = out[idx]


def _mark_coast(land: List[bool], height: List[float],
                codes: List[str]) -> None:
    for idx in range(GRID_W * GRID_H):
        if not land[idx] or height[idx] > 0.16:
            continue
        if codes[idx] in (CODES["marsh"], CODES["jungle"], CODES["glacier"]):
            continue
        for n in _neighbours(idx):
            if not land[n]:
                codes[idx] = CODES["coast"]
                break


# ---------------------------------------------------------------------------
# public entry point
# ---------------------------------------------------------------------------

_CACHE: Dict[str, object] = {}
_DETAIL_CACHE: Dict[str, object] = {}


def _detail_grid() -> Dict[str, object]:
    path = project_root() / "maps" / DETAIL_TERRAIN_NAME
    if not path.is_file():
        return {}
    stamp = "%s:%d:%d" % (path, path.stat().st_mtime_ns, path.stat().st_size)
    cached = _DETAIL_CACHE.get(stamp)
    if cached is None:
        try:
            cached = _parse_full_terrain(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError, AtlasError):
            return {}
        _DETAIL_CACHE.clear()
        _DETAIL_CACHE[stamp] = cached
    return cached  # type: ignore[return-value]


def terrain_detail(world: object, settlement: str,
                   radius: float = 250.0) -> Dict[str, object]:
    """Return a bounded five-mile terrain patch around one settlement."""
    detail = _detail_grid()
    if not detail:
        raise AtlasError("five-mile terrain detail is not installed")
    selected = world.find_settlement(settlement)  # type: ignore[attr-defined]
    waterdeep = world.find_settlement("Waterdeep")  # type: ignore[attr-defined]
    cell_miles = float(detail["cell_miles"])
    radius = max(50.0, min(400.0, float(radius)))
    center_column = math.floor((float(selected.x) - float(waterdeep.x)) / cell_miles)
    center_row = math.floor((float(waterdeep.y) - float(selected.y)) / cell_miles)
    cells_each_side = max(1, math.ceil(radius / cell_miles))
    column_min = max(int(detail["column_min"]), center_column - cells_each_side)
    column_max = min(int(detail["column_max"]), center_column + cells_each_side)
    row_min = max(int(detail["row_min"]), center_row - cells_each_side)
    row_max = min(int(detail["row_max"]), center_row + cells_each_side)
    width = column_max - column_min + 1
    height = row_max - row_min + 1
    rows = detail["rows"]
    assert isinstance(rows, dict)
    source_column_min = int(detail["column_min"])
    code_map = {
        "S": "o", "W": "w", "P": "p", "C": "p", "F": "f",
        "J": "j", "H": "h", "M": "m", "T": "s", "O": "g",
        "D": "d", "R": "d", "I": "i", "U": "u", "X": "u",
    }
    relief = {"h": 14, "m": 28, "i": 12, "g": 4, "f": 6,
              "j": 7, "s": 0, "p": 2, "d": 3}
    coarse = terrain_grid(list(world.settlements.values()))  # type: ignore[attr-defined]
    terrain: List[str] = []
    heights: List[int] = []
    for output_row, source_row in enumerate(range(row_max, row_min - 1, -1)):
        row = rows.get(str(source_row), "")
        if not isinstance(row, str):
            row = ""
        for output_column, column in enumerate(range(column_min, column_max + 1)):
            offset = column - source_column_min
            letter = row[offset] if 0 <= offset < len(row) else "U"
            code = code_map.get(letter, "u")
            terrain.append(code)
            world_x = float(waterdeep.x) + (column_min + output_column + 0.5) * cell_miles
            world_y = float(waterdeep.y) - (row_max - output_row + 0.5) * cell_miles
            base_height = height_at(coarse, world_x, world_y)
            if code in ("o", "w", "u"):
                heights.append(int(round(min(0.0, base_height) * 1000.0)))
            else:
                heights.append(int(round(base_height * 1000.0)) + relief.get(code, 0))
    return {
        "detail": True,
        "settlement": selected.id,
        "bounds": [
            float(waterdeep.x) + column_min * cell_miles,
            float(waterdeep.y) - (row_max + 1) * cell_miles,
            float(waterdeep.x) + (column_max + 1) * cell_miles,
            float(waterdeep.y) - row_min * cell_miles,
        ],
        "grid": [width, height],
        "terrain": "".join(terrain),
        "height": heights,
        "cellMiles": cell_miles,
        "legend": LEGEND,
    }


def terrain_grid(settlements: Sequence[object]) -> Dict[str, object]:
    """Build (and cache) the heightfield for the supplied settlements.

    The rasteriser walks every grid cell against every polygon, which takes a
    second or two.  The result only depends on the gazetteer, so it is computed
    once and reused - but the key folds in the coordinates as well as the count,
    because calibrating the map against a poster moves settlements at runtime
    and the land blobs stamped around each one would otherwise go stale.
    """
    signature = 0
    for s in settlements:
        signature = (signature * 1000003 + int(s.x * 10) * 65599 + int(s.y * 10)) & 0xFFFFFFFF
    # The frame is stretched to cover the poster too, so dropping one into the
    # maps folder resizes the field.  That has to show up in the key or the
    # first grid built without it would be served forever.
    poster = poster_frame(settlements)
    stamp = "-" if poster is None else "%.0f,%.0f,%.0f,%.0f" % poster
    key = "%d:%08x:%s:%s:%s" % (
        len(settlements), signature, stamp, location_terrain_stamp(),
        terrain_overrides_stamp(),
    )
    cached = _CACHE.get(key)
    if cached is None:
        cached = _build(settlements)
        _CACHE[key] = cached
        # Each heightfield is a large array and only the current one matters,
        # so a long calibration session must not accumulate them.
        for stale in list(_CACHE)[:-3]:
            _CACHE.pop(stale, None)
    return cached  # type: ignore[return-value]


def height_at(grid: Dict[str, object], x: float, y: float) -> float:
    """Bilinear sample of the heightfield at a world position, for markers."""
    # Read the frame off the grid rather than the module globals: grids are
    # cached, so the one passed in may have been rasterised under a different
    # calibration than the one currently loaded.
    x0, y0, x1, y1 = grid.get("bounds", BOUNDS)      # type: ignore[union-attr]
    gw, gh = grid.get("grid", (GRID_W, GRID_H))      # type: ignore[union-attr]
    heights = grid["height"]  # type: ignore[index]
    gx = (x - x0) / (x1 - x0) * gw - 0.5
    gy = (y - y0) / (y1 - y0) * gh - 0.5
    gx = max(0.0, min(gw - 1.001, gx))
    gy = max(0.0, min(gh - 1.001, gy))
    ix = int(gx)
    iy = int(gy)
    fx = gx - ix
    fy = gy - iy
    a = heights[iy * gw + ix] / 1000.0            # type: ignore[index]
    b = heights[iy * gw + ix + 1] / 1000.0        # type: ignore[index]
    c = heights[(iy + 1) * gw + ix] / 1000.0      # type: ignore[index]
    d = heights[(iy + 1) * gw + ix + 1] / 1000.0  # type: ignore[index]
    top = a + (b - a) * fx
    bottom = c + (d - c) * fx
    return top + (bottom - top) * fy


def map_payload(world: object) -> Dict[str, object]:
    """Everything the browser needs to draw the world: relief, pins and roads."""
    settlements = list(world.settlements.values())  # type: ignore[attr-defined]
    grid = terrain_grid(settlements)
    # Shipped positions, so the map screen can preview a realignment against the
    # same baseline the server fits against instead of compounding warps.
    base = base_coordinates(settlements)

    pins = []
    for s in settlements:
        src = base.get(s.id, (s.x, s.y))
        pins.append({
            "id": s.id,
            "name": s.name,
            "region": s.region,
            "size": s.size,
            "population": s.population,
            "x": s.x,
            "y": s.y,
            "bx": src[0],
            "by": src[1],
            # Clamped at sea level: a coastal cell can bilinearly interpolate
            # into the neighbouring ocean, which would sink the pin.
            "z": round(max(0.0, height_at(grid, s.x, s.y)), 4),
            "terrain": s.terrain,
            "landmass": s.landmass,
            "port": s.port,
            "river": s.river,
            "underdark": s.underdark,
            "wealth": s.wealth,
            "surveyed": s.has_trait("surveyed_market"),
        })

    for location in getattr(world, "mobile_locations", {}).values():
        profile = location.profile(world)
        position = profile["position"]
        x, y = position["x"], position["y"]
        pins.append({
            "id": location.id,
            "name": location.name,
            "region": "Travelling Companies",
            "size": "travelling company",
            "population": location.population,
            "x": x,
            "y": y,
            "bx": x,
            "by": y,
            "z": round(max(0.0, height_at(grid, x, y)), 4),
            "terrain": "road",
            "landmass": "faerun",
            "port": None,
            "river": False,
            "underdark": False,
            "wealth": location.wealth,
            "surveyed": False,
            "mobile": True,
            "status": position["status"],
            "host": position["host"],
            "origin": position["origin"],
            "destination": position["destination"],
            "route": position["route"],
        })

    # A world built without survey enrichment can still show the remaining
    # names as plain dots. In the normal world these are empty because every
    # surveyed town/site has been promoted to a priced market.
    try:
        places = surveyed_places(settlements)
    except (AtlasError, OSError, ValueError, TypeError, KeyError):
        # A survey is a bonus; invalid user data must not cost us the map.
        places = []

    seen = set()
    routes = []
    edges = getattr(world, "_edges", {}) or {}
    for src, legs in edges.items():
        for edge in legs:
            key = (src, edge.dst) if src < edge.dst else (edge.dst, src)
            if key in seen:
                continue
            seen.add(key)
            routes.append({
                "a": key[0],
                "b": key[1],
                # The dominant mode drives the stroke style; the full list is
                # sent alongside so a multimodal leg can be drawn broken.
                "kind": edge.primary,
                "modes": list(edge.modes),
                "multimodal": edge.multimodal,
                "inferred": edge.inferred,
                "name": edge.name,
                "distance": round(edge.distance, 1),
                "days": round(edge.days, 2),
                "quality": edge.quality,
                "carriers": edge.carrier_options(),
            })

    return {
        "bounds": list(grid["bounds"]),
        "grid": list(grid["grid"]),
        "terrain": grid["terrain"],
        "height": grid["height"],
        "legend": LEGEND,
        "terrainSurvey": grid.get("terrainSurvey", {}),
        "ranges": grid["ranges"],
        "zones": [
            {"name": name, "kind": kind} for name, kind, _poly in ZONES
        ],
        "seas": [name for name, _poly in SEAS],
        "settlements": pins,
        "places": places,
        "routes": routes,
        "roadGeometries": road_geometries(settlements),
        "seaAirGeometries": sea_air_geometries(settlements),
    }
