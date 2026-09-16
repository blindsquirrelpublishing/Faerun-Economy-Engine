"""A standing history of the Realms: three years behind, three years ahead.

Without this module the world is static -- every market sits at its structural
price forever, and the only way to see a shock is to hand-place one.  The
chronicle fills the calendar in: droughts in the Amnian grainlands, bandits on
the Trade Way, a hard winter that shuts the passes above Silverymoon, a famine
that follows a failed harvest two seasons later.  It is installed by default,
so every price the engine quotes is already a price *in a particular month of a
particular history*.

Three properties matter more than the fiction:

* **Deterministic.**  The same settlement always gets the same history, on every
  machine and every run, because the generator is seeded from `blake2b` over a
  stable key rather than from `random` or the salted builtin `hash`.
* **Plausible.**  Templates are drawn from pools built out of a settlement's own
  terrain, industries, port status and security, and seasonal events are snapped
  to the season they belong in.  Deserts do not flood; the Underdark has no
  drought.
* **Sparse.**  Local episodes never overlap each other, so a market cannot stack
  four disasters at once.  Regional events sit on a second layer and *may*
  overlap them, which is where the interesting compound shocks come from.

The window is anchored on 1492 DR (the engine's default "today"), so it does not
slide when you change the world date -- scrubbing the timeline moves you through
a fixed history rather than regenerating one underneath you.
"""

from __future__ import annotations

import hashlib
from typing import Dict, List, Optional, Sequence, Tuple

from .calendar import HarptosDate, season_of
from .events import EVENT_TEMPLATES, make_event
from .models import Event, Settlement
from .world import World

#: the year the chronicle is centred on -- the engine's default "today"
CHRONICLE_ANCHOR_YEAR = 1492
CHRONICLE_BACK_YEARS = 3
CHRONICLE_FORWARD_YEARS = 3

CHRONICLE_FIRST_YEAR = CHRONICLE_ANCHOR_YEAR - CHRONICLE_BACK_YEARS
CHRONICLE_LAST_YEAR = CHRONICLE_ANCHOR_YEAR + CHRONICLE_FORWARD_YEARS

#: every chronicle event id starts with this, so the chronicle can be removed
#: again without disturbing events a DM added by hand
CHRONICLE_PREFIX = "chron"

_SEED = "faerun-chronicle-v1"


# ---------------------------------------------------------------------------
# Deterministic number stream
# ---------------------------------------------------------------------------

class _Stream:
    """A repeatable stream of unit floats derived from a text key.

    `random.Random` would do, but its output is only guaranteed stable for the
    methods whose algorithms never change; hashing each draw explicitly is
    immune to that and matches the `blake2b` convention used by the price
    engine's noise term.
    """

    __slots__ = ("_key", "_n")

    def __init__(self, *parts) -> None:
        self._key = "|".join(str(p) for p in parts)
        self._n = 0

    def unit(self) -> float:
        """The next value in [0, 1)."""
        self._n += 1
        digest = hashlib.blake2b(
            f"{_SEED}|{self._key}#{self._n}".encode("utf-8"), digest_size=8
        ).digest()
        return int.from_bytes(digest, "big") / 18446744073709551616.0

    def chance(self, probability: float) -> bool:
        return self.unit() < probability

    def between(self, low: int, high: int) -> int:
        """An integer in [low, high], inclusive."""
        if high <= low:
            return low
        return low + int(self.unit() * (high - low + 1))

    def span(self, low: float, high: float) -> float:
        return low + self.unit() * (high - low)

    def weighted(self, pool: Sequence[Tuple[str, float]]) -> str:
        """Pick a template name from (name, weight) pairs."""
        total = sum(weight for _, weight in pool)
        if total <= 0:
            return pool[0][0]
        target = self.unit() * total
        running = 0.0
        for name, weight in pool:
            running += weight
            if target < running:
                return name
        return pool[-1][0]


# ---------------------------------------------------------------------------
# Calendar helpers
# ---------------------------------------------------------------------------

def _absolute(year: int, month: int) -> int:
    """Absolute month counter, matching `HarptosDate.absolute_month`."""
    return year * 12 + month


def _from_absolute(stamp: int) -> HarptosDate:
    """Invert `_absolute`.  Note this is *not* the arithmetic `advance` uses."""
    year = (stamp - 1) // 12
    return HarptosDate(year, stamp - year * 12, 1)


def chronicle_window() -> Tuple[int, int]:
    """Inclusive (first, last) absolute months covered by the chronicle."""
    return (
        _absolute(CHRONICLE_FIRST_YEAR, 1),
        _absolute(CHRONICLE_LAST_YEAR, 12),
    )


def chronicle_months() -> int:
    first, last = chronicle_window()
    return last - first + 1


def month_of(stamp: int) -> int:
    """Month-of-year (1-12) for an absolute month counter."""
    return stamp - ((stamp - 1) // 12) * 12


# ---------------------------------------------------------------------------
# What can happen where
# ---------------------------------------------------------------------------

#: typical run length in months: (shortest, longest)
DURATIONS: Dict[str, Tuple[int, int]] = {
    "siege": (2, 6),
    "war": (6, 20),
    "blockade": (3, 9),
    "drought": (4, 8),
    "blight": (3, 7),
    "famine": (4, 10),
    "hard_winter": (3, 5),
    "flood": (2, 4),
    "plague": (4, 11),
    "bumper_harvest": (3, 6),
    "gold_rush": (6, 18),
    "festival": (1, 2),
    "bandits": (3, 10),
    "pirates": (4, 12),
    "monster": (2, 6),
    "dragon": (2, 5),
    "boom": (8, 24),
    "caravan_boom": (4, 10),
    "trade_embargo": (5, 16),
    "refugees": (4, 12),
    "magical_surge": (2, 6),
}

#: events that only make sense at a certain time of year, as months-of-year
SEASONAL: Dict[str, Tuple[int, ...]] = {
    "hard_winter": (11, 12, 1),      # Uktar, Nightal, Hammer
    "drought": (5, 6, 7),            # Mirtul through Flamerule
    "flood": (3, 4, 5),              # the spring melt
    "bumper_harvest": (8, 9),        # Eleasis, Eleint
    "blight": (5, 6, 7, 8),
    "famine": (10, 11, 12, 1, 2),    # the winter after a failed harvest
}

#: a shortage begets a hunger: template -> what may follow it
CONSEQUENCES: Dict[str, Tuple[str, float]] = {
    "drought": ("famine", 0.40),
    "blight": ("famine", 0.35),
    "hard_winter": ("famine", 0.25),
    "flood": ("plague", 0.25),
    "siege": ("famine", 0.45),
    "war": ("refugees", 0.40),
    "plague": ("refugees", 0.20),
    "gold_rush": ("bandits", 0.35),
    "bumper_harvest": ("festival", 0.45),
    "boom": ("caravan_boom", 0.30),
}

#: terrains where crops matter enough for an agricultural disaster to register
FARMING_TERRAIN = {"plains", "hills", "coast", "forest", "marsh", "jungle"}
#: terrains that can freeze hard enough to shut the roads
COLD_TERRAIN = {"tundra", "taiga", "mountains", "hills", "forest", "plains"}

#: Map y grows *southward* (Bryn Shander sits near 240, Calimport near 2600),
#: so "cold" means a low y.  The line is taken as this fraction of the way down
#: the inhabited world rather than a hard-coded number, so adding settlements
#: further north or south does not silently move everyone's climate.
COLD_LINE_FRACTION = 0.35


def _cold_line(world: World) -> float:
    ys = [s.y for s in world.settlements.values()]
    if not ys:
        return 0.0
    low, high = min(ys), max(ys)
    return low + (high - low) * COLD_LINE_FRACTION


def _pool(s: Settlement, cold_line: float) -> List[Tuple[str, float]]:
    """Build the weighted template pool for one settlement.

    The weights are deliberately coarse: what matters is that a desert oasis
    cannot flood and a drow enclave cannot suffer a drought, not that the
    relative odds of piracy versus banditry are finely tuned.
    """
    pool: List[Tuple[str, float]] = [
        ("festival", 1.1),
        ("boom", 0.7),
        ("plague", 0.5),
        ("monster", 0.5),
        ("caravan_boom", 0.6),
    ]

    # Lawlessness draws predators.  security runs 0 (lawless) to 1 (safe).
    lawless = max(0.0, 1.0 - s.security)
    pool.append(("bandits", 0.5 + lawless * 3.0))
    pool.append(("refugees", 0.3 + lawless * 1.2))

    if s.underdark:
        # No sky, no weather: the Underdark's troubles are all political,
        # geological or predatory.
        pool.extend([
            ("magical_surge", 1.2),
            ("war", 0.9),
            ("siege", 0.6),
            ("trade_embargo", 0.9),
            ("monster", 1.4),
        ])
        pool = [(name, weight) for name, weight in pool if name != "festival"]
    else:
        if s.terrain in FARMING_TERRAIN:
            farming = 1.0 + s.industry_level("farm") + s.industry_level("herd")
            pool.append(("drought", 0.9 * farming))
            pool.append(("blight", 0.8 * farming))
            pool.append(("bumper_harvest", 1.0 * farming))
        if s.terrain == "desert":
            pool.append(("drought", 1.4))
        if s.terrain in COLD_TERRAIN and s.y <= cold_line:
            pool.append(("hard_winter", 1.6))
        if s.river or s.terrain == "marsh":
            pool.append(("flood", 1.1))

    if s.is_port:
        pool.append(("pirates", 1.5))
        pool.append(("blockade", 0.8))
    if s.population >= 25000:
        pool.append(("trade_embargo", 0.8))
        pool.append(("siege", 0.4))
    if any(tag.startswith("mine") for tag in s.industries):
        pool.append(("gold_rush", 1.0))
    if s.has_trait("arcane") or s.industry_level("arcane") > 0:
        pool.append(("magical_surge", 1.2))
    if s.has_trait("frontier") or s.has_trait("wild"):
        pool.append(("monster", 1.2))
        pool.append(("dragon", 0.35))
    if s.terrain in ("mountains", "hills") and not s.underdark:
        pool.append(("dragon", 0.3))

    return pool


def _snap_to_season(stamp: int, template: str, last: int) -> int:
    """Move a start month forward to the next month the event makes sense in."""
    allowed = SEASONAL.get(template)
    if not allowed:
        return stamp
    for offset in range(12):
        if month_of(stamp + offset) in allowed:
            candidate = stamp + offset
            return candidate if candidate <= last else stamp
    return stamp


def _severity(stream: _Stream) -> float:
    """A 0.7-1.35 multiplier on how far an event bends the market."""
    return round(stream.span(0.7, 1.35), 3)


def _bend(value: float, severity: float) -> float:
    """Scale a multiplier's *deviation* from 1.0, never its sign."""
    return round(1.0 + (float(value) - 1.0) * severity, 4)


def _title(template: str, s: Optional[Settlement], stamp: int) -> str:
    label = template.replace("_", " ").title()
    where = s.name if s is not None else "the Realms"
    date = _from_absolute(stamp)
    return f"{label} in {where}, {date.year} DR"


# ---------------------------------------------------------------------------
# Curated history
# ---------------------------------------------------------------------------

#: A handful of hand-written regional events, so the chronicle has recognisable
#: landmarks rather than being uniformly procedural.  These are this engine's
#: own fiction, not canon.  (template, name, regions, year, month, duration)
CURATED: Tuple[Tuple[str, str, Tuple[str, ...], int, int, int], ...] = (
    ("trade_embargo", "The Amnian Grain Tariff", ("Amn",), 1490, 3, 14),
    ("bandits", "The Trade Way Caravan Wars", ("Sword Coast North",), 1491, 5, 11),
    ("hard_winter", "The Long Winter of 1491",
     ("Silver Marches", "Icewind Dale", "Sword Coast North"), 1491, 11, 5),
    ("pirates", "The Nelanther Corsair Season", ("Sword Coast", "Amn"), 1492, 4, 8),
    ("gold_rush", "The Sword Mountains Silver Strike", ("Sword Coast North",),
     1492, 9, 15),
    ("magical_surge", "The Weave Tremors",
     ("Sword Coast", "Silver Marches"), 1493, 2, 6),
    ("war", "The Border Wars of 1494", ("Cormyr", "Sembia"), 1494, 3, 16),
    ("bumper_harvest", "The Great Harvest of 1495", ("Cormyr", "Dalelands",
                                                     "Sembia"), 1495, 8, 5),
)


def _curated_events(world: World) -> List[Event]:
    """Build the hand-written events, skipping regions this world lacks."""
    known = {s.region for s in world.settlements.values()}
    out: List[Event] = []
    for index, (template, name, regions, year, month, duration) in enumerate(CURATED):
        live = [r for r in regions if r in known]
        if not live:
            continue
        out.append(make_event(
            template=template,
            name=name,
            regions=live,
            start_month=_absolute(year, month),
            duration_months=duration,
            world=world,
            event_id=f"{CHRONICLE_PREFIX}-lore-{index:02d}",
        ))
    return out


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def _settlement_events(world: World, s: Settlement,
                       cold_line: float) -> List[Event]:
    """The full run of local episodes for one settlement across the window."""
    first, last = chronicle_window()
    stream = _Stream("settlement", s.id)
    pool = _pool(s, cold_line)
    events: List[Event] = []
    index = 0

    # Start somewhere inside the first year so histories are not all in step.
    stamp = first + stream.between(0, 11)
    pending: Optional[str] = None

    while stamp <= last and index < 24:
        template = pending or stream.weighted(pool)
        pending = None
        if template not in EVENT_TEMPLATES:
            template = "bandits"

        stamp = _snap_to_season(stamp, template, last)
        if stamp > last:
            break

        low, high = DURATIONS.get(template, (3, 8))
        duration = stream.between(low, high)
        # Let events run past the edge of the window rather than truncating
        # them: a war that is still going in 1495 should look unfinished.
        severity = _severity(stream)
        base = EVENT_TEMPLATES[template]
        events.append(make_event(
            template=template,
            name=_title(template, s, stamp),
            settlements=[s.id],
            supply=_bend(base.get("supply", 1.0), severity),
            demand=_bend(base.get("demand", 1.0), severity),
            price=_bend(base.get("price", 1.0), severity),
            risk=round(float(base.get("risk", 0.0)) * severity, 3),
            start_month=stamp,
            duration_months=duration,
            world=world,
            event_id=f"{CHRONICLE_PREFIX}-{s.id}-{index:02d}",
        ))
        index += 1

        follow = CONSEQUENCES.get(template)
        if follow and stream.chance(follow[1]):
            # A consequence treads on the heels of its cause.
            pending = follow[0]
            stamp += duration + stream.between(0, 2)
        else:
            stamp += duration + stream.between(4, 15)

    return events


def build_chronicle(world: World) -> List[Event]:
    """Generate the whole history without registering any of it."""
    events: List[Event] = []
    cold_line = _cold_line(world)
    for s in sorted(world.settlements.values(), key=lambda x: x.id):
        events.extend(_settlement_events(world, s, cold_line))
    events.extend(_curated_events(world))
    return events


def install_chronicle(world: World, replace: bool = True) -> int:
    """Register the chronicle with a world.  Returns the number of events.

    Existing chronicle events are cleared first so this is idempotent; events a
    DM added by hand are left alone.
    """
    if replace:
        clear_chronicle(world)
    events = build_chronicle(world)
    for event in events:
        world.add_event(event)
    return len(events)


def clear_chronicle(world: World) -> int:
    """Remove every chronicle event, leaving hand-placed ones in place."""
    doomed = [eid for eid in world.events if eid.startswith(CHRONICLE_PREFIX + "-")]
    for eid in doomed:
        world.remove_event(eid)
    return len(doomed)


def is_chronicle_event(event: Event) -> bool:
    return str(event.id).startswith(CHRONICLE_PREFIX + "-")


# ---------------------------------------------------------------------------
# Reading the history back
# ---------------------------------------------------------------------------

def event_span(event: Event) -> Tuple[Optional[int], Optional[int]]:
    """Inclusive (first, last) active month, or Nones for an open window."""
    if event.start_month is None:
        return (None, None)
    if event.duration_months is None:
        return (event.start_month, None)
    return (event.start_month, event.start_month + int(event.duration_months) - 1)


def event_to_dict(event: Event) -> Dict:
    """A JSON-friendly view of one event, with dates spelled out."""
    start, end = event_span(event)
    return {
        "id": event.id,
        "name": event.name,
        "kind": event.kind,
        "description": event.description,
        "supply": round(event.supply, 4),
        "demand": round(event.demand, 4),
        "price": round(event.price, 4),
        "risk": round(event.risk, 4),
        "categories": list(event.categories),
        "commodities": list(event.commodities),
        "regions": list(event.regions),
        "scope": ("settlement" if event.settlements else
                  "region" if event.regions else
                  "zone" if event.zones else "world"),
        "start_month": start,
        "end_month": end,
        "start": str(_from_absolute(start)) if start is not None else None,
        "end": str(_from_absolute(end)) if end is not None else None,
        "duration_months": event.duration_months,
        "chronicle": is_chronicle_event(event),
    }


def settlement_timeline(settlement, world: Optional[World] = None) -> Dict:
    """Every event touching one settlement, in order, across the window."""
    from .world import get_world

    world = world or get_world()
    s = world.find_settlement(settlement)
    first, last = chronicle_window()
    rows = []
    for event in world.events.values():
        if not event.applies_to_settlement(s):
            continue
        start, end = event_span(event)
        # Keep open-ended and undated events: they are always in view.
        if start is not None and start > last:
            continue
        if end is not None and end < first:
            continue
        rows.append(event_to_dict(event))
    rows.sort(key=lambda r: (r["start_month"] is None, r["start_month"] or 0, r["id"]))
    return {
        "settlement": s.name,
        "settlement_id": s.id,
        "region": s.region,
        "first_month": first,
        "last_month": last,
        "months": chronicle_months(),
        "anchor_month": _absolute(CHRONICLE_ANCHOR_YEAR, 6),
        "events": rows,
    }


def month_labels() -> List[Dict]:
    """One label per month in the window, for driving a timeline scrubber."""
    first, last = chronicle_window()
    out = []
    for stamp in range(first, last + 1):
        date = _from_absolute(stamp)
        out.append({
            "month": stamp,
            "year": date.year,
            "month_of_year": date.month,
            "label": f"{date.month_name} {date.year}",
            "short": f"{date.month_name[:3]} {date.year}",
            "season": season_of(date.month),
        })
    return out


def chronicle_summary(world: Optional[World] = None) -> Dict:
    """How much history there is, and of what kind."""
    from .world import get_world

    world = world or get_world()
    kinds: Dict[str, int] = {}
    total = 0
    for event in world.events.values():
        if not is_chronicle_event(event):
            continue
        total += 1
        kinds[event.kind] = kinds.get(event.kind, 0) + 1
    first, last = chronicle_window()
    return {
        "events": total,
        "by_kind": dict(sorted(kinds.items())),
        "first_year": CHRONICLE_FIRST_YEAR,
        "last_year": CHRONICLE_LAST_YEAR,
        "first_month": first,
        "last_month": last,
        "months": chronicle_months(),
    }
