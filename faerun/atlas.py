"""Read a surveyed location index and turn it into engine coordinates.

The gazetteer in `data/settlements.py` was hand-placed for plausible travel
times, and its error is not uniform: the Sword Coast is close to canon while
the Western Heartlands are squashed and the Backlands stretched.  No single
pan/scale nudge can undo a distortion that changes sign across the map, which
is why the map screen grew a click-to-place calibration mode.

This module is the same idea without the clicking.  If the user drops a
`locations.json` next to their poster in `maps/`, giving pixel positions for
named places on that image plus the scale needed to turn pixels into miles,
every one of those places becomes a calibration control point in one go.

The file this was written against calls its frame "FPS" and anchors it on
Waterdeep::

    {
      "coordinate_system": {
        "origin_name": "Waterdeep",
        "origin_pixel": {"x": 694, "y": 682},
        "pixels_per_unit": 150.5,
        "miles_per_unit": 120,
        "positive_x": "east",
        "positive_y": "north"
      },
      "locations": [
        {"name": "Baldur's Gate", "pixel_x": 1036, "pixel_y": 1157,
         "east_miles": 272.7, "north_miles": -378.7, ...}
      ]
    }

Only two things are actually required of an entry: a name, and a position.
`east_miles`/`north_miles` are used when present; otherwise they are derived
from the pixels and the scale, so a thinner file still works.

Nothing here mutates the gazetteer.  The output is a list of control points in
exactly the shape `calibration.save_control_points` expects, so an atlas
alignment and a hand-clicked one are the same kind of object and the second
simply overwrites the first.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

#: Where a surveyed index is looked for, in order.  `maps/` first because that
#: is where the poster itself lives and the two belong together.
ATLAS_NAMES = ("locations.json", "atlas.json", "coordinates.json")

#: Categories that can stand in for a market.  Geographic features (forests,
#: mountain ranges) are indexed in the same file but are label centres, not
#: places, so they must never be matched against a settlement.
PLACE_CATEGORIES = {"settlement_or_site", "settlement", "site", "city", "town"}

#: Fallback scale, used only if the file omits the header maths entirely.
DEFAULT_MILES_PER_UNIT = 120.0

_WORDS = re.compile(r"[^a-z0-9]+")
_LEADING_THE = re.compile(r"^the\b[\s_-]*")

#: Names that differ between the survey and the gazetteer.  Kept deliberately
#: short: normalisation already handles case, accents, punctuation and a
#: leading "the", so this is only for genuinely different spellings.  Realms
#: and regions need no entry - they are filtered out by category instead.
ALIASES: Dict[str, str] = {
    "waterdeepcityofsplendors": "waterdeep",
    "cityofsplendors": "waterdeep",
    "baldursgatecity": "baldursgate",
    "corwell": "caercorwell",
}


def project_root() -> Path:
    """The directory that holds the `faerun` package."""
    return Path(__file__).resolve().parent.parent


def atlas_candidates() -> List[Path]:
    """Every path that could hold a surveyed location index."""
    root = project_root()
    folders = [root / "maps", root, Path.cwd() / "maps", Path.cwd()]
    seen: List[Path] = []
    for folder in folders:
        for name in ATLAS_NAMES:
            candidate = folder / name
            if candidate not in seen:
                seen.append(candidate)
    return seen


def find_atlas(path: Optional[str] = None) -> Optional[Path]:
    """Locate a surveyed index, or None when there is not one."""
    if path:
        explicit = Path(path).expanduser()
        return explicit if explicit.is_file() else None
    for candidate in atlas_candidates():
        try:
            if candidate.is_file():
                return candidate
        except OSError:
            continue
    return None


def normalise(name: str) -> str:
    """Fold a place name to a comparison key.

    Accents, case, punctuation and a leading "the" all vary between sources and
    none of them distinguish two different towns, so all of them are discarded.
    """
    text = unicodedata.normalize("NFKD", str(name or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    # Drop the article only when it is a word of its own.  Collapsing
    # punctuation first would turn "Thentia" into "ntia".
    text = _LEADING_THE.sub("", text)
    text = _WORDS.sub("", text)
    return ALIASES.get(text, text)


# ---------------------------------------------------------------------------
# reading the file
# ---------------------------------------------------------------------------


class AtlasError(Exception):
    """Raised when a file exists but cannot be understood."""


def _scale_from_header(header: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """(origin_px_x, origin_px_y, miles_per_pixel, north_sign).

    Prefers an explicit scale bar, because that is measured off the artwork
    itself, and falls back to the declared pixels-per-unit.
    """
    origin = header.get("origin_pixel") or {}
    ox = float(origin.get("x", 0.0))
    oy = float(origin.get("y", 0.0))

    miles_per_pixel = 0.0
    bar = header.get("scale_bar") or {}
    try:
        span = abs(float(bar["end_x"]) - float(bar["start_x"]))
        if span > 0:
            miles_per_pixel = float(bar["miles"]) / span
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        miles_per_pixel = 0.0

    if miles_per_pixel <= 0:
        try:
            per_unit = float(header.get("pixels_per_unit", 0.0))
            miles = float(header.get("miles_per_unit", DEFAULT_MILES_PER_UNIT))
            if per_unit > 0:
                miles_per_pixel = miles / per_unit
        except (TypeError, ValueError):
            miles_per_pixel = 0.0

    # `positive_y` says which way the survey counts, independent of the image,
    # whose pixel rows always increase downward.
    north_sign = 1.0 if str(header.get("positive_y", "north")).lower() == "north" else -1.0
    return ox, oy, miles_per_pixel, north_sign


#: the last survey parsed from the discovered file, keyed on its mtime and size
_ATLAS_CACHE: Dict[str, Any] = {"key": None, "value": None}


def load_atlas(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Parse a surveyed index into a header plus a list of places.

    Returns None when no file is present.  Raises AtlasError when a file is
    present but unusable, because that is a mistake worth reporting rather
    than silently ignoring.
    """
    target = find_atlas(path)
    if target is None:
        return None
    # A single map request reads the survey several times over - to place the
    # poster, to size the frame, to fit the markets, to list the extra towns -
    # and it is several hundred entries of JSON.  Keyed on the file's mtime and
    # size, so editing the survey still takes effect without a restart.
    # Only the discovered file is cached.  An explicit path is what tests and
    # the CLI pass, and they expect a straight read of whatever is on disk.
    stamp = None
    if path is None:
        try:
            stat = target.stat()
            stamp = (str(target), stat.st_mtime_ns, stat.st_size)
        except OSError:
            stamp = None
    if stamp is not None and _ATLAS_CACHE.get("key") == stamp:
        return _ATLAS_CACHE["value"]  # type: ignore[return-value]
    try:
        raw = target.read_text(encoding="utf-8")
    except OSError as exc:
        raise AtlasError(f"{target} could not be read: {exc}") from exc
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise AtlasError(f"{target} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AtlasError(f"{target} should hold an object at the top level")

    header = data.get("coordinate_system") or data.get("header") or {}
    if not isinstance(header, dict):
        header = {}
    entries = data.get("locations") or data.get("places") or data.get("entries") or []
    if not isinstance(entries, list):
        raise AtlasError(f"{target} has no list of locations")

    ox, oy, mpp, north_sign = _scale_from_header(header)

    places: List[Dict[str, Any]] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            continue

        east = item.get("east_miles")
        north = item.get("north_miles")
        if east is None or north is None:
            # Derive from pixels.  This is the path for a leaner file that
            # only records where the label sits on the image.
            px = item.get("pixel_x")
            py = item.get("pixel_y")
            if px is None or py is None or mpp <= 0:
                continue
            try:
                east = (float(px) - ox) * mpp
                north = (oy - float(py)) * mpp * north_sign
            except (TypeError, ValueError):
                continue
        try:
            east = float(east)
            north = float(north)
        except (TypeError, ValueError):
            continue

        places.append({
            "name": name,
            "key": normalise(name),
            "category": str(item.get("category") or "").strip().lower(),
            "method": str(item.get("method") or "").strip().lower(),
            "east": east,
            "north": north,
            "pixel_x": item.get("pixel_x"),
            "pixel_y": item.get("pixel_y"),
        })

    result = {
        "path": str(target),
        "origin_name": str(header.get("origin_name") or "Waterdeep"),
        "miles_per_pixel": mpp,
        # Kept so the poster itself can be placed in world miles, not just the
        # places on it: the origin pixel is the one point whose world position
        # is known, and everything else on the image hangs off it.
        "origin_px": (ox, oy),
        "north_sign": north_sign,
        "image": str(header.get("source_image") or ""),
        "image_width": header.get("image_width"),
        "image_height": header.get("image_height"),
        "count": len(places),
        "places": places,
    }
    if stamp is not None:
        _ATLAS_CACHE["key"] = stamp
        _ATLAS_CACHE["value"] = result
    return result


# ---------------------------------------------------------------------------
# turning it into control points
# ---------------------------------------------------------------------------


def _place_index(places: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Key -> place, preferring a settlement over a same-named feature.

    Several entries can normalise to the same key ("Neverwinter" the city and
    "Neverwinter River"); the survey's own category is the tie-breaker, and a
    real market always wins.
    """
    index: Dict[str, Dict[str, Any]] = {}
    for place in places:
        key = place.get("key") or normalise(str(place.get("name") or ""))
        if "east" not in place or "north" not in place:
            place = {
                **place,
                "east": place.get("east_miles"),
                "north": place.get("north_miles"),
            }
        # A file that records no categories at all is still usable, so an empty
        # category counts as "might be a town"; a category that is present and
        # says "forest" does not.
        if not key or not _place_like(place):
            continue
        current = index.get(key)
        if current is None or (
            not _certain(current) and _certain(place)
        ):
            index[key] = place
    return index


def _place_like(place: Dict[str, Any]) -> bool:
    category = place.get("category") or ""
    return not category or category in PLACE_CATEGORIES


def _certain(place: Dict[str, Any]) -> bool:
    return (place.get("category") or "") in PLACE_CATEGORIES


def _survey_frame(
    settlements: Sequence[Any],
    atlas: Dict[str, Any],
    anchor: Optional[str] = None,
) -> Dict[str, Any]:
    """The shared frame that ties survey miles to world coordinates.

    The survey measures everything relative to one origin town, so that town is
    the hinge: it is placed exactly where the gazetteer already has it and every
    other distance is laid out from there.  Keeping the anchor still means an
    alignment never slides the whole world sideways, and because engine
    coordinates *are* miles the survey's distances transfer across unchanged.

    The markets, the terrain and the poster image itself all have to hang off
    the same hinge or they would not line up with each other, so the maths
    lives here once rather than three times.
    """
    index = _place_index(atlas["places"])
    anchor_name = anchor or atlas.get("origin_name") or "Waterdeep"
    anchor_key = normalise(anchor_name)

    # The anchor has to exist on both sides or there is no shared frame.
    anchor_settlement = None
    for s in settlements:
        if normalise(getattr(s, "name", "")) == anchor_key:
            anchor_settlement = s
            break
    if anchor_settlement is None:
        raise AtlasError(
            f"the survey is anchored on {anchor_name!r}, which is not a market "
            "in this gazetteer, so its distances cannot be placed"
        )

    from .calibration import base_coordinates

    base = base_coordinates(settlements)
    ax, ay = base[anchor_settlement.id]

    anchor_place = index.get(anchor_key)
    # An origin entry normally reads (0, 0); honour it if it does not, so a
    # survey anchored on a different town than it measures from still works.
    ox = float(anchor_place["east"]) if anchor_place else 0.0
    oy = float(anchor_place["north"]) if anchor_place else 0.0

    return {
        "index": index, "base": base, "settlement": anchor_settlement,
        "name": getattr(anchor_settlement, "name", anchor_name),
        "ax": ax, "ay": ay, "ox": ox, "oy": oy,
    }


def align(
    settlements: Sequence[Any],
    atlas: Optional[Dict[str, Any]] = None,
    anchor: Optional[str] = None,
) -> Dict[str, Any]:
    """Match a gazetteer against a survey and return control points.

    The survey measures everything relative to one origin town, so the result
    is pinned by placing that town exactly where the gazetteer already has it
    and laying every other distance out from there in miles.  Keeping the
    anchor still means an alignment never slides the whole world sideways, and
    because engine coordinates *are* miles the survey's distances transfer
    across unchanged - which is the entire point, since distance is freight
    cost and freight cost is price.
    """
    if atlas is None:
        atlas = load_atlas()
    if not atlas:
        return {
            "available": False, "matched": [], "missing": [], "unused": [],
            "features": {}, "anchor": "", "count": 0, "path": "",
            "surveyed": 0,
        }

    frame = _survey_frame(settlements, atlas, anchor)
    index = frame["index"]
    base = frame["base"]
    anchor_settlement = frame["settlement"]
    anchor_name = frame["name"]
    ax, ay = frame["ax"], frame["ay"]
    ox, oy = frame["ox"], frame["oy"]

    matched: List[Dict[str, Any]] = []
    missing: List[str] = []
    hit_keys = set()

    for s in settlements:
        key = normalise(getattr(s, "name", ""))
        place = index.get(key)
        if place is None:
            missing.append(getattr(s, "name", "?"))
            continue
        hit_keys.add(key)
        # east grows with x; north grows against y, because the engine counts
        # y southward down the page.
        x = ax + (float(place["east"]) - ox)
        y = ay - (float(place["north"]) - oy)
        src = base.get(s.id, (s.x, s.y))
        matched.append({
            "id": s.id,
            "name": s.name,
            "x": round(x, 1),
            "y": round(y, 1),
            "fromX": round(src[0], 1),
            "fromY": round(src[1], 1),
            "moved": round(math.hypot(x - src[0], y - src[1]), 1),
            "survey": place["name"],
            "method": place.get("method", ""),
        })

    # Forests, deserts, seas and mountain ranges are not markets, but the map
    # is drawn around them and the survey knows where they really are.  Their
    # label positions are handed back so the terrain can be pinned too.
    features: Dict[str, Dict[str, Any]] = {}
    for p in atlas["places"]:
        key = p.get("key") or normalise(str(p.get("name") or ""))
        if not key or _place_like(p):
            continue
        east = p.get("east", p.get("east_miles"))
        north = p.get("north", p.get("north_miles"))
        features[key] = {
            "name": p["name"],
            "x": round(ax + (float(east) - ox), 1),
            "y": round(ay - (float(north) - oy), 1),
        }

    unused = [
        p["name"] for p in atlas["places"]
        # Same filter the index uses, so a survey that records no categories
        # reports its leftovers instead of silently claiming there are none.
        if (p.get("key") or normalise(str(p.get("name") or "")))
        and (p.get("key") or normalise(str(p.get("name") or ""))) not in hit_keys
        and _place_like(p)
    ]

    return {
        "available": True,
        "path": atlas.get("path", ""),
        "anchor": getattr(anchor_settlement, "name", anchor_name),
        "matched": matched,
        "missing": sorted(missing),
        "inferred": sorted(
            m["name"] for m in matched if m["method"] == "engine_inferred"
        ),
        "unused": sorted(unused),
        "features": features,
        "count": len(matched),
        "surveyed": sum(
            1 for m in matched if m["method"] != "engine_inferred"
        ),
    }


def control_points(
    settlements: Sequence[Any],
    atlas: Optional[Dict[str, Any]] = None,
    anchor: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Just the `{id, x, y}` triples, ready for `save_control_points`."""
    report = align(settlements, atlas=atlas, anchor=anchor)
    return [
        {"id": m["id"], "x": m["x"], "y": m["y"]}
        for m in report["matched"]
    ]


def surveyed_places(
    settlements: Sequence[Any],
    atlas: Optional[Dict[str, Any]] = None,
    anchor: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Every surveyed town absent from the supplied markets, placed in miles.

    World assembly uses this list to promote those names into inferred local
    markets. The map also retains it as a graceful fallback when enrichment is
    disabled or a caller supplies its own smaller gazetteer.
    """
    if atlas is None:
        atlas = load_atlas()
    if not atlas:
        return []

    frame = _survey_frame(settlements, atlas, anchor)
    ax, ay = frame["ax"], frame["ay"]
    ox, oy = frame["ox"], frame["oy"]
    taken = {normalise(getattr(s, "name", "")) for s in settlements}

    out: List[Dict[str, Any]] = []
    seen = set()
    for p in atlas["places"]:
        key = p["key"]
        # A market of our own always wins: it has real prices behind it, and a
        # second dot on top of it would just be a smudge.
        if not key or key in taken or key in seen or not _place_like(p):
            continue
        seen.add(key)
        out.append({
            "name": p["name"],
            "x": round(ax + (float(p["east"]) - ox), 1),
            "y": round(ay - (float(p["north"]) - oy), 1),
            "category": p.get("category", ""),
        })
    out.sort(key=lambda p: p["name"])
    return out


def underlay_placement(
    settlements: Sequence[Any],
    atlas: Optional[Dict[str, Any]] = None,
    anchor: Optional[str] = None,
) -> Dict[str, Any]:
    """Where the poster image itself belongs, in world miles.

    The survey records the pixel it measured from and how many miles a pixel
    covers, which is all that is needed to lay the whole image down in world
    coordinates instead of nudging it into place by hand.  The result is the
    rectangle the image occupies: top-left corner plus its size in miles.

    Note the poster only *looks* aligned once the markets have been realigned
    to the same survey.  Before that it is correctly placed and the towns are
    not, which is precisely what makes the overlay worth looking at.
    """
    try:
        if atlas is None:
            atlas = load_atlas()
    except AtlasError as exc:
        return {"available": False, "error": str(exc)}
    if not atlas:
        return {"available": False, "error": "no survey found"}

    mpp = float(atlas.get("miles_per_pixel") or 0.0)
    width = atlas.get("image_width")
    height = atlas.get("image_height")
    try:
        width = float(width)
        height = float(height)
    except (TypeError, ValueError):
        return {"available": False,
                "error": "the survey does not record the image size"}
    if mpp <= 0 or width <= 0 or height <= 0:
        return {"available": False,
                "error": "the survey does not record a usable scale"}

    try:
        frame = _survey_frame(settlements, atlas, anchor)
    except AtlasError as exc:
        return {"available": False, "error": str(exc)}

    px, py = atlas.get("origin_px", (0.0, 0.0))
    sign = float(atlas.get("north_sign", 1.0)) or 1.0
    ax, ay = frame["ax"], frame["ay"]
    ox, oy = frame["ox"], frame["oy"]

    def world(ix: float, iy: float) -> Tuple[float, float]:
        east = (ix - float(px)) * mpp
        north = (float(py) - iy) * mpp * sign
        return (ax + (east - ox), ay - (north - oy))

    x0, y_top = world(0.0, 0.0)
    x1, y_bot = world(width, height)
    # A survey that counts southward would place row 0 at the bottom; taking the
    # extremes keeps the rectangle right way up either way.
    return {
        "available": True,
        "error": "",
        "image": atlas.get("image", ""),
        "imageWidth": int(width),
        "imageHeight": int(height),
        "milesPerPixel": round(mpp, 5),
        "anchor": frame["name"],
        "x": round(min(x0, x1), 1),
        "y": round(min(y_top, y_bot), 1),
        "widthMiles": round(abs(x1 - x0), 1),
        "heightMiles": round(abs(y_bot - y_top), 1),
        "flipped": sign < 0,
    }


def atlas_info(path: Optional[str] = None) -> Dict[str, Any]:
    """A small, JSON-safe summary for the map screen and the CLI."""
    try:
        atlas = load_atlas(path)
    except AtlasError as exc:
        return {"available": False, "error": str(exc),
                "searched": [str(p) for p in atlas_candidates()]}
    if not atlas:
        return {"available": False, "error": "",
                "searched": [str(p) for p in atlas_candidates()]}
    return {
        "available": True,
        "error": "",
        "path": atlas["path"],
        "image": atlas["image"],
        "origin_name": atlas["origin_name"],
        "count": atlas["count"],
        "miles_per_pixel": round(atlas["miles_per_pixel"], 4),
        "searched": [str(p) for p in atlas_candidates()],
    }
