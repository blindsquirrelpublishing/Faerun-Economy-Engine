"""Regions and nations: a general economic profile plus an editable border.

A settlement's ``region`` is only a label.  This module gives each label an
optional record of its own: what kind of realm it is, how it trades, what it
sells and buys, and a border drawn as one or more polygons in world miles (the
same frame as settlement positions, route legs and saved location edits).

Island realms claim open water as well as land.  The polygon is the shoreline;
``sea_margin_miles`` (ten for island nations) widens the territory outward from
it.  Containment is "inside a ring, or within the margin of one", so nothing
needs to be buffered into new geometry for the engine, and the map can draw the
margin as a wide round stroke.

The records live in ``faerun/data/store/regions.json``.  The descriptive
profile does not feed the price model; it is read by reports and the map.
"""
from __future__ import annotations

import copy
import json
import math
import threading
from dataclasses import asdict, dataclass, field, fields
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .data_store import STORE_DIR
from .models import slugify

Point = Tuple[float, float]

REGION_KINDS = frozenset({
    "island_nation", "kingdom", "empire", "city_state_league", "theocracy",
    "magocracy", "frontier", "wilderness", "other",
})
TRADE_DEPENDENCE = frozenset({
    "self_sufficient", "mixed", "sea_dependent", "import_dependent", "isolationist",
})
DEFAULT_ISLAND_MARGIN_MILES = 10.0
MAX_MARGIN_MILES = 200.0
MAX_RINGS = 50
MAX_RING_POINTS = 2000
MAX_POLYGON_NAME = 80
MAX_COORDINATE = 100000.0

_LOCK = threading.Lock()
_CACHE: Dict[str, Any] = {"stamp": None, "revision": 0, "regions": []}


class RegionError(ValueError):
    """A region request was invalid (bad polygon, unknown id, stale revision)."""


@dataclass
class Region:
    id: str
    name: str
    kind: str = "other"
    landmasses: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    summary: str = ""
    trade_dependence: str = "mixed"
    industries: Dict[str, float] = field(default_factory=dict)
    exports: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    wealth: Optional[float] = None
    tariff: Optional[float] = None
    ruler: str = ""
    notes: str = ""
    sea_margin_miles: float = 0.0
    borders: List[List[List[float]]] = field(default_factory=list)
    border_names: List[str] = field(default_factory=list)
    border_source: str = ""

    @property
    def labels(self) -> List[str]:
        return [self.name, *self.aliases]

    def matches_label(self, label: str) -> bool:
        wanted = label.casefold()
        return any(item.casefold() == wanted for item in self.labels)

    def distance_to_territory(self, x: float, y: float) -> float:
        """0 inside the land polygons, otherwise miles to the nearest shoreline."""
        best = math.inf
        for ring in self.borders:
            if point_in_ring(x, y, ring):
                return 0.0
            best = min(best, distance_to_ring(x, y, ring))
        return best

    def contains(self, x: float, y: float) -> bool:
        return self.distance_to_territory(x, y) <= self.sea_margin_miles

    def land_square_miles(self) -> float:
        return round(sum(ring_area(ring) for ring in self.borders), 1)

    def polygon_names(self) -> List[str]:
        """One name per polygon, blank where a polygon has none."""
        return aligned_names(self.border_names, len(self.borders))

    def polygon_at(self, x: float, y: float) -> Optional[int]:
        """Index of the land polygon containing a point, if any."""
        for index, ring in enumerate(self.borders):
            if point_in_ring(x, y, ring):
                return index
        return None

    def to_row(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def point_in_ring(x: float, y: float, ring: Sequence[Sequence[float]]) -> bool:
    inside = False
    count = len(ring)
    for index in range(count):
        ax, ay = ring[index]
        bx, by = ring[(index + 1) % count]
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            inside = not inside
    return inside


def _segment_distance(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx, dy = bx - ax, by - ay
    length = dx * dx + dy * dy
    fraction = 0.0 if not length else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length))
    return math.hypot(px - (ax + fraction * dx), py - (ay + fraction * dy))


def distance_to_ring(x: float, y: float, ring: Sequence[Sequence[float]]) -> float:
    count = len(ring)
    return min(
        _segment_distance(x, y, ring[i][0], ring[i][1], ring[(i + 1) % count][0], ring[(i + 1) % count][1])
        for i in range(count)
    )


def ring_area(ring: Sequence[Sequence[float]]) -> float:
    total = 0.0
    for index, (ax, ay) in enumerate(ring):
        bx, by = ring[(index + 1) % len(ring)]
        total += ax * by - bx * ay
    return abs(total) / 2.0


def _segments_cross(a: Point, b: Point, c: Point, d: Point) -> bool:
    def orient(p: Point, q: Point, r: Point) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    d1, d2 = orient(a, b, c), orient(a, b, d)
    d3, d4 = orient(c, d, a), orient(c, d, b)
    return d1 * d2 < 0 and d3 * d4 < 0


def ring_self_intersects(ring: Sequence[Sequence[float]]) -> bool:
    count = len(ring)
    for i in range(count):
        a, b = tuple(ring[i]), tuple(ring[(i + 1) % count])
        for j in range(i + 1, count):
            if abs(i - j) <= 1 or (i == 0 and j == count - 1):
                continue
            if _segments_cross(a, b, tuple(ring[j]), tuple(ring[(j + 1) % count])):
                return True
    return False


def aligned_names(names: Any, count: int) -> List[str]:
    """Pad or trim a name list so it lines up with ``count`` polygons."""
    given = list(names) if isinstance(names, (list, tuple)) else []
    return [str(given[i]) if i < len(given) and given[i] is not None else "" for i in range(count)]


def clean_border_names(value: Any, count: int) -> List[str]:
    if value is None:
        return [""] * count
    if not isinstance(value, (list, tuple)) or any(not isinstance(v, str) for v in value):
        raise RegionError("Polygon names must be a list of text")
    if len(value) != count:
        raise RegionError("Give one name per polygon (%d polygons, %d names)" % (count, len(value)))
    names = [" ".join(v.split()) for v in value]
    if any(len(v) > MAX_POLYGON_NAME for v in names):
        raise RegionError("Polygon names are limited to %d characters" % MAX_POLYGON_NAME)
    lowered = [v.casefold() for v in names if v]
    if len(set(lowered)) != len(lowered):
        raise RegionError("Polygon names must be different within a region")
    return names


def clean_borders(value: Any) -> List[List[List[float]]]:
    """Validate a list of rings and return it as plain rounded floats."""
    if value is None:
        return []
    if not isinstance(value, (list, tuple)) or len(value) > MAX_RINGS:
        raise RegionError("Borders must be a list of at most %d polygons" % MAX_RINGS)
    rings: List[List[List[float]]] = []
    for number, raw in enumerate(value, 1):
        if not isinstance(raw, (list, tuple)) or not 3 <= len(raw) <= MAX_RING_POINTS:
            raise RegionError("Polygon %d needs between 3 and %d points" % (number, MAX_RING_POINTS))
        ring: List[List[float]] = []
        for point in raw:
            if (not isinstance(point, (list, tuple)) or len(point) != 2
                    or any(type(v) not in (int, float) or not math.isfinite(v) or abs(v) > MAX_COORDINATE
                           for v in point)):
                raise RegionError("Polygon %d has a point that is not two finite world-mile coordinates" % number)
            rounded = [round(float(point[0]), 2), round(float(point[1]), 2)]
            if not ring or rounded != ring[-1]:
                ring.append(rounded)
        if len(ring) > 1 and ring[0] == ring[-1]:
            ring.pop()
        if ring_self_intersects(ring):
            raise RegionError("Polygon %d crosses itself" % number)
        if len(ring) < 3 or ring_area(ring) <= 0:
            raise RegionError("Polygon %d encloses no area" % number)
        rings.append(ring)
    return rings


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

def regions_path():
    return STORE_DIR / "regions.json"


def _from_row(row: Dict[str, Any]) -> Region:
    known = {f.name for f in fields(Region)}
    return Region(**{key: value for key, value in row.items() if key in known})


def _stamp():
    path = regions_path()
    if not path.exists():
        return None
    info = path.stat()
    return (str(path), info.st_mtime_ns, info.st_size)


def load_regions() -> Tuple[int, List[Region]]:
    """The saved revision and regions, re-read only when the file changes."""
    stamp = _stamp()
    if stamp is None:
        _CACHE.update(stamp=None, revision=0, regions=[])
    elif stamp != _CACHE["stamp"]:
        payload = json.loads(regions_path().read_text(encoding="utf-8"))
        _CACHE.update(stamp=stamp, revision=int(payload.get("revision", 0)),
                      regions=[_from_row(row) for row in payload.get("regions", [])])
    return _CACHE["revision"], copy.deepcopy(_CACHE["regions"])


def regions_revision() -> int:
    return load_regions()[0]


def _write(revision: int, regions: Iterable[Region]) -> None:
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    path = regions_path()
    tmp = path.with_suffix(".json.tmp")
    payload = {"revision": revision, "regions": [region.to_row() for region in regions]}
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    tmp.replace(path)
    _CACHE["stamp"] = None


def find_region(key: str, regions: Optional[Sequence[Region]] = None) -> Optional[Region]:
    pool = load_regions()[1] if regions is None else regions
    wanted = key.strip().casefold()
    for region in pool:
        if region.id == wanted or region.name.casefold() == wanted:
            return region
    for region in pool:
        if region.matches_label(key.strip()):
            return region
    return None


def region_for_label(label: str) -> Optional[Region]:
    return find_region(label) if label else None


def region_at(x: float, y: float, regions: Optional[Sequence[Region]] = None) -> Optional[Region]:
    """The region whose border (plus sea margin) covers a point, land first."""
    pool = load_regions()[1] if regions is None else regions
    best: Optional[Tuple[Tuple[float, float, float], Region]] = None
    for region in pool:
        if not region.borders:
            continue
        distance = region.distance_to_territory(x, y)
        if distance > region.sea_margin_miles:
            continue
        rank = (distance, region.land_square_miles(), 0.0)
        if best is None or rank < best[0]:
            best = (rank, region)
    return best[1] if best else None


# ---------------------------------------------------------------------------
# Validation and editing
# ---------------------------------------------------------------------------

def _clean_fields(values: Dict[str, Any], commodities: Optional[Iterable[str]]) -> Dict[str, Any]:
    clean: Dict[str, Any] = {}
    for key in ("name", "summary", "ruler", "notes", "border_source"):
        if key in values and values[key] is not None:
            if not isinstance(values[key], str):
                raise RegionError("%s must be text" % key)
            clean[key] = values[key].strip()
    if "name" in clean and (not clean["name"] or len(clean["name"]) > 120):
        raise RegionError("A region needs a name of at most 120 characters")
    if "kind" in values and values["kind"] is not None:
        if values["kind"] not in REGION_KINDS:
            raise RegionError("kind must be one of: " + ", ".join(sorted(REGION_KINDS)))
        clean["kind"] = values["kind"]
    if "trade_dependence" in values and values["trade_dependence"] is not None:
        if values["trade_dependence"] not in TRADE_DEPENDENCE:
            raise RegionError("trade_dependence must be one of: " + ", ".join(sorted(TRADE_DEPENDENCE)))
        clean["trade_dependence"] = values["trade_dependence"]
    for key in ("landmasses", "aliases", "exports", "imports"):
        if key in values and values[key] is not None:
            if not isinstance(values[key], (list, tuple)) or not all(isinstance(v, str) and v.strip() for v in values[key]):
                raise RegionError("%s must be a list of non-empty text" % key)
            clean[key] = [v.strip() for v in values[key]]
    known = set(commodities) if commodities is not None else None
    if known is not None:
        for key in ("exports", "imports"):
            unknown = [v for v in clean.get(key, []) if v not in known]
            if unknown:
                raise RegionError("Unknown commodity ids in %s: %s" % (key, ", ".join(unknown)))
    if "industries" in values and values["industries"] is not None:
        industries = values["industries"]
        if not isinstance(industries, dict) or any(
                not isinstance(k, str) or type(v) not in (int, float) or not 0 <= v <= 5 for k, v in industries.items()):
            raise RegionError("industries must map tags to levels between 0 and 5")
        clean["industries"] = {k: float(v) for k, v in industries.items()}
    for key, low, high in (("wealth", 0.1, 5.0), ("tariff", 0.0, 1.0)):
        if key in values:
            value = values[key]
            if value is not None and (type(value) not in (int, float) or not low <= value <= high):
                raise RegionError("%s must be between %s and %s" % (key, low, high))
            clean[key] = None if value is None else float(value)
    if "sea_margin_miles" in values and values["sea_margin_miles"] is not None:
        margin = values["sea_margin_miles"]
        if type(margin) not in (int, float) or not 0 <= margin <= MAX_MARGIN_MILES:
            raise RegionError("sea_margin_miles must be between 0 and %d" % MAX_MARGIN_MILES)
        clean["sea_margin_miles"] = float(margin)
    if "borders" in values:
        clean["borders"] = clean_borders(values["borders"])
    return clean


def upsert_region(key: str, values: Dict[str, Any], *, commodities: Optional[Iterable[str]] = None,
                  revision: Optional[int] = None) -> Region:
    """Create or update one region; ``key`` is an id or a name.

    Only the fields present in ``values`` change.  Pass ``revision`` to refuse a
    save made against a stale copy of the file.
    """
    with _LOCK:
        current, regions = load_regions()
        if revision is not None and revision != current:
            raise RegionError("Regions changed elsewhere. Reload before saving.")
        clean = _clean_fields(values, commodities)
        existing = find_region(key, regions)
        if existing is None:
            name = clean.get("name") or key.strip()
            if not name:
                raise RegionError("A new region needs a name")
            region_id = slugify(name)
            if any(item.id == region_id for item in regions):
                raise RegionError("A region with that id already exists")
            kind = clean.get("kind", "other")
            region = Region(id=region_id, name=name, kind=kind)
            if kind == "island_nation" and "sea_margin_miles" not in clean:
                clean["sea_margin_miles"] = DEFAULT_ISLAND_MARGIN_MILES
            regions.append(region)
        else:
            region = existing
            if "name" in clean and any(item is not region and item.name.casefold() == clean["name"].casefold()
                                       for item in regions):
                raise RegionError("A region with that name already exists")
        final_borders = clean.get("borders", region.borders)
        if "border_names" in values and values["border_names"] is not None:
            clean["border_names"] = clean_border_names(values["border_names"], len(final_borders))
        elif "borders" in clean or len(region.border_names) != len(final_borders):
            clean["border_names"] = aligned_names(region.border_names, len(final_borders))
        for name, value in clean.items():
            setattr(region, name, value)
        _write(current + 1, regions)
        return region


def delete_region(key: str) -> bool:
    with _LOCK:
        current, regions = load_regions()
        region = find_region(key, regions)
        if region is None:
            return False
        _write(current + 1, [item for item in regions if item is not region])
        return True


def save_region_border(body: Dict[str, Any], labels: Iterable[str] = ()) -> Dict[str, Any]:
    """Map-editor save: replace one region's polygons and sea margin.

    A region without a profile yet can be given a border when its id is one of
    the settlement region ``labels``; the profile is created on the way.  With
    ``create`` set, a brand-new region named ``id`` (of the given ``kind``) is
    made even though no settlement carries its label.
    """
    if type(body.get("revision")) is not int:
        raise RegionError("A region save needs an integer revision")
    identifier = body.get("id")
    if not isinstance(identifier, str) or not identifier.strip():
        raise RegionError("Unknown region")
    values: Dict[str, Any] = {"borders": body.get("borders")}
    if body.get("create") is True:
        if find_region(identifier) is not None or identifier.strip().casefold() in {l.casefold() for l in labels}:
            raise RegionError("A region with that name already exists")
        values["name"] = identifier.strip()
        if "kind" in body:
            values["kind"] = body["kind"]
    elif find_region(identifier) is None and identifier.strip().casefold() not in {l.casefold() for l in labels}:
        raise RegionError("Unknown region")
    if "seaMarginMiles" in body:
        values["sea_margin_miles"] = body["seaMarginMiles"]
    if "borderNames" in body:
        values["border_names"] = body["borderNames"]
    values["border_source"] = "manual"
    upsert_region(identifier, values, revision=body["revision"])
    return map_region_payload()


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

_TERRITORY_CACHE: Dict[str, Any] = {"stamp": None, "value": {}}


def region_territories() -> Dict[str, List[List[List[float]]]]:
    """Smoothed territory outlines (land plus sea margin, split with neighbours).

    Computed from the saved borders and kept until the regions file changes.
    """
    from .territory import region_territories as compute

    _, regions = load_regions()
    stamp = _CACHE["stamp"]
    if stamp is None or stamp != _TERRITORY_CACHE["stamp"]:
        _TERRITORY_CACHE.update(stamp=stamp, value=compute(regions))
    return _TERRITORY_CACHE["value"]


def smooth_region_borders(body: Dict[str, Any]) -> Dict[str, Any]:
    """Map-editor helper: smooth a draft's polygons without saving anything."""
    from .territory import MAX_SMOOTH_MILES, smooth_borders, smooth_report

    strength = body.get("strengthMiles")
    if type(strength) not in (int, float) or not 0 < strength <= MAX_SMOOTH_MILES:
        raise RegionError("Smoothing must be between 0 and %d miles" % MAX_SMOOTH_MILES)
    before = clean_borders(body.get("borders"))
    after = smooth_borders(before, float(strength))
    return {"borders": after, "reports": [smooth_report(a, b) for a, b in zip(before, after)]}


def fit_region_borders(body: Dict[str, Any], origin: Tuple[float, float]) -> Dict[str, Any]:
    """Map-editor helper: fit a draft's polygons to the mapped coastline.

    ``bufferMiles`` pushes each outline out over the sea, kept clear of every
    other region's polygons (``regionId`` names the region being edited).
    """
    from .coast import DEFAULT_SNAP_MILES, MAX_BUFFER_MILES, MAX_SNAP_MILES, fit_borders_to_coast

    snap = body.get("snapMiles", DEFAULT_SNAP_MILES)
    if type(snap) not in (int, float) or not 0 <= snap <= MAX_SNAP_MILES:
        raise RegionError("Snap reach must be between 0 and %d miles" % MAX_SNAP_MILES)
    buffer = body.get("bufferMiles", 0)
    if type(buffer) not in (int, float) or not 0 <= buffer <= MAX_BUFFER_MILES:
        raise RegionError("Sea buffer must be between 0 and %d miles" % MAX_BUFFER_MILES)
    own = find_region(body["regionId"]) if isinstance(body.get("regionId"), str) else None
    avoid = [ring for region in load_regions()[1] if own is None or region.id != own.id for ring in region.borders]
    return fit_borders_to_coast(clean_borders(body.get("borders")), origin, float(snap), float(buffer), avoid)


def map_region_payload() -> Dict[str, Any]:
    revision, regions = load_regions()
    territories = region_territories()
    return {
        "regionRevision": revision,
        "regionBorders": [{
            "id": region.id, "name": region.name, "kind": region.kind,
            "summary": region.summary, "seaMarginMiles": region.sea_margin_miles,
            "borders": region.borders, "borderNames": region.polygon_names(),
            "territory": territories.get(region.id, []),
            "source": region.border_source,
        } for region in regions],
    }


def _members(world: Any, region: Region) -> Tuple[List[Any], List[Any]]:
    by_label = [s for s in world.settlements.values() if region.matches_label(s.region)]
    by_border = [s for s in world.settlements.values()
                 if region.borders and region.contains(float(s.x), float(s.y))]
    return by_label, by_border


def describe_region(world: Any, key: str) -> Dict[str, Any]:
    region = find_region(key)
    if region is None:
        raise KeyError("no region matching %r" % key)
    by_label, by_border = _members(world, region)
    label_ids = {s.id for s in by_label}
    border_ids = {s.id for s in by_border}
    row = region.to_row()
    row["land_square_miles"] = region.land_square_miles()
    row["territory_square_miles"] = round(sum(ring_area(ring) for ring in
                                              region_territories().get(region.id, [])), 1)
    row["has_border"] = bool(region.borders)
    row["border_names"] = region.polygon_names()
    row["polygons"] = [{"name": name, "square_miles": round(ring_area(ring), 1)}
                       for name, ring in zip(region.polygon_names(), region.borders)]
    row["markets"] = len(by_label)
    row["population"] = sum(s.population for s in by_label)
    row["settlements"] = sorted(s.name for s in by_label)
    row["inside_border_not_labelled"] = sorted(s.name for s in by_border if s.id not in label_ids)
    row["labelled_outside_border"] = (
        sorted(s.name for s in by_label if s.id not in border_ids) if region.borders else [])
    return row


def region_rows(world: Any) -> List[Dict[str, Any]]:
    """One row per region label: counts for every label, plus the saved profile."""
    saved = load_regions()[1]
    rows: List[Dict[str, Any]] = []
    claimed: set = set()
    for label in world.regions:
        members = [s for s in world.settlements.values() if s.region == label]
        region = next((item for item in saved if item.matches_label(label)), None)
        if region is not None:
            claimed.add(region.id)
        rows.append({
            "region": label,
            "markets": len(members),
            "population": sum(s.population for s in members),
            "settlements": sorted(s.name for s in members),
            "profile": None if region is None else {
                "id": region.id, "kind": region.kind, "summary": region.summary,
                "trade_dependence": region.trade_dependence, "exports": region.exports,
                "imports": region.imports, "has_border": bool(region.borders),
                "sea_margin_miles": region.sea_margin_miles,
            },
        })
    for region in saved:
        if region.id not in claimed:
            rows.append({"region": region.name, "markets": 0, "population": 0, "settlements": [],
                         "profile": {"id": region.id, "kind": region.kind, "summary": region.summary,
                                     "trade_dependence": region.trade_dependence,
                                     "exports": region.exports, "imports": region.imports,
                                     "has_border": bool(region.borders),
                                     "sea_margin_miles": region.sea_margin_miles}})
    return rows
