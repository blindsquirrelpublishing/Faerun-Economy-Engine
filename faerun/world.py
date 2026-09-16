"""World assembly: settlements, commodities and the trade network graph."""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field, fields
from functools import lru_cache
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .calendar import HarptosDate
from .atlas import AtlasError
from .data.commodities import COMMODITIES
from .data.businesses import BUSINESSES
from .data.mobile_locations import MOBILE_LOCATIONS
from .data.routes import NAMED_ROUTES, NAMED_SEA_LANES
from .data.settlements import SETTLEMENTS, ZONE_ADJACENCY
from .mobile import MobileLocation
from .models import Business, Commodity, Event, Settlement, slugify

SURVEYED_MARKET_TRAIT = "surveyed_market"
SURVEYED_MARKET_PORTS = {
    "delselar": "Sea of Swords",
    "halagard": "Sea of Swords",
    "samargol": "Sea of Swords",
    "thindar": "Sea of Swords",
    "urbreth": "Sea of Swords",
}
SURVEYED_FERRY_MARKETS = {
    "anchoril", "iron_keep", "irphong", "llewellyn", "nemesser",
    "sambar", "sundrah",
}
SURVEYED_SEA_LANES = [
    ("Halruaan Harbor Passage", ["halarahh", "halagard"], 0.95),
    ("Halruaa-Chult Coastal Run",
        ["halarahh", "halagard", "delselar", "thindar", "samargol",
         "port_nyanzaru"], 1.05),
    ("Chult-Tashalar Coastal Run",
        ["port_nyanzaru", "tashluta", "almraiven", "suldolphor"], 1.05),
    ("Calimshan-Lantan Coastal Run",
        ["suldolphor", "urbreth", "lantan", "calimport"], 1.05),
]
SURVEYED_FERRY_ROUTES = [
    ("Port Ghaast Ferry", "port_ghaast", "khalab", 0.75),
]
SURVEYED_ROADS = [
    ("The Shining Plains Road",
        ["riatavin", "lheshayl", "ormath", "hlondeth"], 1.0),
]
SURVEYED_MAGIC_ROUTES = [
    ("The Winterkeep Circle", ["winterkeep", "eltabbar"], 1.0, "teleport"),
    ("The Winterkeep-Bezantur Circle",
        ["winterkeep", "bezantur"], 0.95, "teleport"),
    ("The Halruaan Concordance",
        ["winterkeep", "halarahh"], 0.85, "teleport"),
    ("The Nimbral Accord",
        ["winterkeep", "nimbral"], 0.75, "teleport"),
    ("The Sshamath Gate",
        ["winterkeep", "sshamath"], 0.65, "teleport"),
]
MAX_COASTING_LEG_MILES = 650.0
BLOCKED_COASTING_LEGS = {
    frozenset(("tashluta", "thindar")),
    frozenset(("urmlaspyr", "westgate")),
}


def _surveyed_markets(established: Sequence[Settlement]) -> List[Settlement]:
    """Infer small import markets for surveyed towns absent from the gazetteer.

    The survey supplies names and coordinates, not populations or industries.
    Each new market therefore inherits geographic and civic context from its
    nearest established market, but no authored industries or specialties.
    Expanded requirements infer basic local resources separately; imports and
    any modeled exports still travel through that hub.
    """
    if not established:
        return []
    try:
        from .mapdata import surveyed_places

        current = surveyed_places(established)
    except (AtlasError, OSError, ValueError, TypeError, KeyError):
        # Baseline recovery can fail independently of the survey itself. Use
        # the survey's aligned coordinates rather than dropping every market.
        try:
            from .atlas import surveyed_places as atlas_places

            current = atlas_places(established)
        except (AtlasError, OSError, ValueError, TypeError, KeyError):
            # Survey enrichment is optional; malformed user data must not
            # prevent the built-in economy from starting.
            return []

    # Stable shipped coordinates improve calibration resets, but they are not
    # required to create a market. A bad baseline must not discard every valid
    # surveyed town and leave it as an unpriced map label.
    base_by_id = {}
    try:
        from .mapdata import surveyed_places_base

        base_by_id = {
            slugify(str(p["name"])): p
            for p in surveyed_places_base(established)
        }
    except (AtlasError, OSError, ValueError, TypeError, KeyError):
        pass
    known = {s.id for s in established}
    inferred: List[Settlement] = []
    for place in current:
        name = str(place.get("name") or "").strip()
        sid = slugify(name)
        if not sid or sid in known:
            continue
        try:
            x, y = float(place["x"]), float(place["y"])
        except (KeyError, TypeError, ValueError):
            continue
        surface = [s for s in established if not s.underdark] or list(established)
        nearest = min(
            surface,
            key=lambda s: math.dist((x, y), (s.x, s.y)),
        )
        population = max(80, min(2000, nearest.population // 25))
        traits = list(dict.fromkeys(list(nearest.traits) + [SURVEYED_MARKET_TRAIT]))
        market = Settlement(
            id=sid,
            name=name,
            region=nearest.region,
            zone=nearest.zone,
            population=population,
            x=x,
            y=y,
            wealth=nearest.wealth,
            tax=nearest.tax,
            security=nearest.security,
            terrain=nearest.terrain,
            landmass=nearest.landmass,
            port=SURVEYED_MARKET_PORTS.get(sid),
            traits=traits,
            description=(
                "A surveyed local market. Its regional profile is inferred "
                f"from {nearest.name}; goods arrive through that trade hub."
            ),
        )
        shipped = base_by_id.get(sid)
        if shipped is not None:
            setattr(market, "_base_xy",
                    (float(shipped["x"]), float(shipped["y"])))
        inferred.append(market)
        known.add(sid)
    return inferred

# ---------------------------------------------------------------------------
# Travel modes
# ---------------------------------------------------------------------------

#: mode -> (freight factor, base speed in miles/day, hazard factor)
#:
#: The freight factor is the cost of a pound-mile relative to an ordinary road,
#: the speed is the mode's unloaded pace, and the hazard factor scales how
#: badly poor security bites on that kind of going.  Water is cheap and fast,
#: the Underdark is neither, and skyships buy speed at a ruinous price.
MODES = {
    "teleport": (8.00, 5000.0, 0.20),  # licensed permanent portal circles
    "air": (3.20, 110.0, 0.85),    # Halruaan skyships, Netherese relics
    "sea": (0.30, 72.0, 0.90),     # deep-water hulls
    "river": (0.55, 40.0, 0.70),   # downstream-capable river craft
    "ferry": (0.70, 30.0, 0.80),   # short crossings, lake and estuary hops
    "barge": (0.45, 28.0, 0.60),   # slow bulk haulage on still water
    "road": (1.00, 24.0, 1.00),    # a maintained, drained highway
    "trail": (1.30, 19.0, 1.30),   # unpaved but established
    "track": (1.45, 18.0, 1.40),   # wilderness caravan going
    "tunnel": (1.90, 12.0, 2.20),  # Underdark passages
    "portage": (2.20, 10.0, 1.60),  # hauling cargo overland between waters
}

#: Human-readable names, used by the CLI, the MCP server and the map legend.
MODE_LABELS = {
    "teleport": "teleportation circle",
    "air": "skyship",
    "sea": "sea lane",
    "river": "river",
    "ferry": "ferry",
    "barge": "barge",
    "road": "road",
    "trail": "trail",
    "track": "wilderness track",
    "tunnel": "Underdark tunnel",
    "portage": "portage",
}

# --- multimodal legs -------------------------------------------------------
#
# Some arteries are not one thing.  A smugglers' run may be tunnel *and* trail;
# a grain route may be barge *and* portage; the Sword Coast timber run is river
# then sea.  A leg carrying several modes has to be transhipped, and every
# transfer costs money, wastes days and offers thieves another chance.  These
# three constants price that penalty; each is charged per *extra* mode.

#: surcharge on freight for each mode beyond the first (handling, wharfage)
MULTIMODAL_COST = 0.18
#: loss of effective speed for each extra mode (loading, waiting on the tide)
MULTIMODAL_DELAY = 0.12
#: share of a secondary mode's hazard that carries over to the whole leg
MULTIMODAL_RISK = 0.35


def parse_modes(kind) -> Tuple[str, ...]:
    """Normalise a route ``kind`` into an ordered tuple of known modes.

    Accepts ``"road"``, a ``"+"``-joined string such as ``"river+portage"``, or
    any sequence of mode names.  Unknown names are dropped rather than raising,
    so a typo in the gazetteer degrades to a plain road instead of breaking
    world construction; :mod:`verify` checks for that case explicitly.
    """
    if isinstance(kind, (list, tuple)):
        parts: Sequence[str] = list(kind)
    else:
        parts = str(kind).split("+")
    out: List[str] = []
    for part in parts:
        name = str(part).strip().lower()
        if name in MODES and name not in out:
            out.append(name)
    return tuple(out) or ("road",)


def canonical_kind(kind) -> str:
    """The stable ``"+"``-joined spelling of a (possibly composite) kind."""
    return "+".join(parse_modes(kind))


@lru_cache(maxsize=None)
def mode_profile(modes: Tuple[str, ...]) -> Tuple[float, float, float]:
    """(freight factor, speed, hazard) for a leg served by several modes.

    Cost is the mean of the members plus a transhipment surcharge: the cargo
    covers part of the distance by each mode, so a river-and-portage haul lands
    between the two rather than at either extreme.  Time uses the harmonic mean
    for the same reason -- distance splits, so *durations* add -- and is then
    slowed further by handling.  Risk takes the worst mode in full and a share
    of every other, because a chain is exposed everywhere it is handled.
    """
    if len(modes) == 1:
        return MODES[modes[0]]
    n = len(modes)
    extra = n - 1
    freight = sum(MODES[m][0] for m in modes) / n
    freight *= 1.0 + MULTIMODAL_COST * extra
    speed = n / sum(1.0 / MODES[m][1] for m in modes)
    speed *= max(0.35, 1.0 - MULTIMODAL_DELAY * extra)
    ranked = sorted((MODES[m][2] for m in modes), reverse=True)
    hazard = ranked[0] + MULTIMODAL_RISK * sum(ranked[1:])
    return (freight, speed, hazard)


def describe_modes(kind) -> str:
    """``"river+portage"`` -> ``"river and portage"`` for display."""
    names = [MODE_LABELS.get(m, m) for m in parse_modes(kind)]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


@lru_cache(maxsize=None)
def _profile_for_kind(kind: str) -> Tuple[float, float, float]:
    """Cached profile for an edge's canonical kind string.

    Edges resolve this on every relaxation inside Dijkstra, so the parse and
    the blend are memoised on the small set of kinds actually in play.
    """
    return mode_profile(parse_modes(kind))


#: gp to move one pound one mile along an ordinary road in peaceful country
FREIGHT_RATE = 0.00006

#: carrier -> (name, maximum load in pounds, relative cost, relative speed)
CARRIERS = {
    "teleport": (
        ("Licensed portal transfer", 2000, 1.00, 1.00),
        ("Priority circle transfer", 500, 1.35, 1.15),
    ),
    "road": (
        ("Ox freight wagon", 6000, 0.82, 0.72),
        ("Horse freight wagon", 4000, 1.00, 1.00),
        ("Mule cart", 2000, 0.88, 0.90),
    ),
    "trail": (
        ("Pack pony string", 1200, 0.95, 1.05),
        ("Mule train", 2400, 0.90, 1.00),
        ("Porter company", 1000, 1.20, 0.78),
    ),
    "track": (
        ("Camel caravan", 3000, 0.90, 1.15),
        ("Mule caravan", 2400, 1.00, 1.00),
        ("Ox caravan", 5000, 0.82, 0.70),
    ),
    "sea": (
        ("Coasting cog", 100000, 1.08, 0.88),
        ("Merchant caravel", 180000, 1.00, 1.05),
        ("Deep-water galleon", 400000, 0.86, 0.95),
    ),
    "river": (
        ("Keelboat", 30000, 1.00, 1.05),
        ("River barge", 80000, 0.82, 0.72),
        ("Shallow-draft wherry", 12000, 1.15, 1.18),
    ),
    "barge": (
        ("Canal barge", 100000, 0.78, 0.78),
        ("Horse-drawn barge", 70000, 0.90, 1.00),
    ),
    "ferry": (
        ("Cargo ferry", 30000, 0.95, 0.90),
        ("Fast packet", 8000, 1.30, 1.25),
    ),
    "portage": (
        ("Mule portage train", 2000, 0.95, 1.00),
        ("Ox haulage team", 5000, 0.82, 0.70),
        ("Porter company", 1000, 1.15, 0.85),
    ),
    "tunnel": (
        ("Rothe caravan", 4000, 0.85, 0.82),
        ("Deep mule train", 1800, 1.00, 1.00),
        ("Porter company", 900, 1.20, 0.80),
    ),
    "air": (
        ("Gryphon flight", 600, 0.95, 1.00),
        ("Hippogriff flight", 450, 0.82, 0.88),
        ("Giant eagle flight", 300, 1.08, 1.18),
        ("Pegasus courier", 200, 1.35, 1.32),
        ("Halruaan skyship", 20000, 0.74, 0.82),
    ),
}

MULTILEG_CARRIER_SERVICES = {
    "The Vilhon Road": {
        "carrier": "Ox freight wagon",
        "name": "Vilhon Reach Milk Run",
        "service_id": "vilhon-reach-milk-run",
        "service_class": "ground",
    },
    "Halruaa-Chult Coastal Run": {
        "carrier": "Coasting cog",
        "name": "Sword Coast Coasters",
        "service_id": "halruaa-chult-coastal-run",
    },
    "Chult-Tashalar Coastal Run": {
        "carrier": "Coasting cog",
        "name": "Sword Coast Coasters",
        "service_id": "chult-tashalar-coastal-run",
    },
    "Calimshan-Lantan Coastal Run": {
        "carrier": "Coasting cog",
        "name": "Sword Coast Coasters",
        "service_id": "calimshan-lantan-coastal-run",
    },
}


@dataclass
class Edge:
    """A leg of the trade network."""

    src: str
    dst: str
    distance: float
    quality: float
    kind: str
    name: str = ""
    inferred: bool = False

    @property
    def modes(self) -> Tuple[str, ...]:
        """Every mode this leg is served by, in order of prominence."""
        return parse_modes(self.kind)

    @property
    def primary(self) -> str:
        """The dominant mode, used for map styling and one-word labels."""
        return parse_modes(self.kind)[0]

    @property
    def multimodal(self) -> bool:
        return len(parse_modes(self.kind)) > 1

    @property
    def speed(self) -> float:
        base = _profile_for_kind(self.kind)[1]
        return base * max(0.5, min(1.35, self.quality))

    @property
    def days(self) -> float:
        return self.distance / max(1.0, self.speed)

    def freight_units(self, risk: float) -> float:
        """Pound-miles of effective freight, including a risk premium."""
        factor = _profile_for_kind(self.kind)[0] / max(0.4, min(1.35, self.quality))
        return self.distance * factor * (1.0 + risk)

    def hazard(self, security: float) -> float:
        """0 (safe) .. ~1 (very dangerous) for this leg."""
        return max(0.0, (1.0 - security)) * _profile_for_kind(self.kind)[2]

    def carrier_options(self) -> List[Dict[str, object]]:
        """Available carriers with full-load prices for this particular leg."""
        quality = max(0.4, min(1.35, self.quality))
        service = MULTILEG_CARRIER_SERVICES.get(self.name)
        options: List[Dict[str, object]] = []
        for mode in self.modes:
            freight_factor, base_speed, _hazard = MODES[mode]
            for name, max_load, cost_factor, speed_factor in CARRIERS[mode]:
                rate = FREIGHT_RATE * freight_factor * cost_factor / quality
                speed = base_speed * speed_factor * quality
                option = {
                    "mode": mode,
                    "name": name,
                    "max_load_lb": max_load,
                    "cost_gp": round(rate * max_load * self.distance, 2),
                    "cost_gp_per_ton_mile": round(rate * 2000, 3),
                    "speed_miles_per_day": round(speed, 1),
                    "days": round(self.distance / max(1.0, speed), 2),
                }
                if service and service["carrier"] == name:
                    option.update({
                        "name": service["name"],
                        "service_id": service["service_id"],
                        "service_class": service.get("service_class", "water"),
                        "multileg": True,
                    })
                options.append(option)
        return options


@dataclass
class EconomyConfig:
    """Tunable knobs for the price model."""

    scarcity_elasticity: float = 0.45   # how hard shortages bite
    surplus_elasticity: float = 0.30    # how far gluts push prices down
    surplus_floor: float = 0.45         # cheapest a glut can get (x base)
    shortage_ceiling: float = 18.0      # dearest an unreachable good can get
    export_margin: float = 0.12         # merchant margin taken at the source
    market_markup_small: float = 0.45   # markup in a thorp with no competition
    noise: float = 0.07                 # deterministic pseudo-random wobble
    spread_min: float = 0.12            # merchant buy/sell spread floor
    spread_max: float = 0.55
    seed: int = 1492
    delivery_limits: Dict[Tuple[str, str, str], float] = field(default_factory=dict)
    fresh_bread_days: float = 3.0
    staple_reserve_ratio: float = 1.15
    expanded_requirements: bool = True
    resource_reserve_ratio: float = 1.10
    calibrate_source_districts: bool = True
    service_economy: bool = True
    visitor_economy: bool = True
    visitor_scale: float = 1.0
    visitor_max_days: float = 14.0
    water_overrides: Dict[str, Dict[str, float]] = field(default_factory=dict)
    seasonal_inventory: bool = False
    inventory_epoch: str = "1492-01-01"
    initial_inventory: Dict[Tuple[str, str], float] = field(default_factory=dict)
    storage_capacity: Dict[Tuple[str, str], float] = field(default_factory=dict)
    inventory_cache_path: Optional[str] = None


class World:
    """The Realms as a market: settlements, goods, routes, events and a date."""

    @property
    def inventory_revision(self) -> int:
        return self.revision - getattr(self, "_date_revisions", 0)

    def economy_state_key(self, month: Optional[int] = None) -> tuple:
        def freeze(value):
            if isinstance(value, dict):
                return tuple(sorted((key, freeze(item)) for key, item in value.items()))
            if isinstance(value, (list, tuple)):
                return tuple(freeze(item) for item in value)
            return value

        settings = tuple(
            (item.name, freeze(value))
            for item in fields(self.config)
            for value in (getattr(self.config, item.name),)
        )
        date_key = (
            ("day", self.date.absolute_day())
            if month is None
            else ("month", month)
        )
        revision = self.inventory_revision if self.config.seasonal_inventory else self.revision
        return (revision, date_key, settings)

    def __init__(
        self,
        settlements: Optional[Sequence[Settlement]] = None,
        commodities: Optional[Sequence[Commodity]] = None,
        businesses: Optional[Sequence[Business]] = None,
        mobile_locations: Optional[Sequence[MobileLocation]] = None,
        date: Optional[HarptosDate] = None,
        config: Optional[EconomyConfig] = None,
        trade_store=None,
    ) -> None:
        source = list(settlements or SETTLEMENTS)
        if not settlements:
            source.extend(_surveyed_markets(source))
        self.settlements: Dict[str, Settlement] = {
            s.id: s for s in source
        }
        self.commodities: Dict[str, Commodity] = {
            c.id: c for c in (commodities or COMMODITIES)
        }
        business_source = list(BUSINESSES if businesses is None else businesses)
        self.businesses: Dict[str, Business] = {
            business.id: business for business in business_source
            if any(location in self.settlements for location in business.locations)
        }
        mobile_source = (
            MOBILE_LOCATIONS
            if settlements is None and mobile_locations is None
            else (mobile_locations or ())
        )
        self.mobile_locations: Dict[str, MobileLocation] = {
            location.id: location for location in mobile_source
        }
        self.follows_real_date = date is None
        self.date = date or HarptosDate.today()
        self.config = config or EconomyConfig()
        self.trade_store = trade_store
        self.events: Dict[str, Event] = {}
        self.revision = 0          # bumped whenever state changes; busts caches
        self._date_revisions = 0  # dates select a ledger snapshot, not a new scenario
        # The chronicle registers several hundred dated events, and the pricing
        # pass asks "what is happening here?" once per settlement per commodity.
        # Re-filtering the whole event list every time would dominate the run,
        # so the answer is memoised per (revision, month) and then indexed by
        # settlement.  Both caches are dropped whenever either input changes.
        self._events_stamp: Optional[Tuple[int, int]] = None
        self._events_active: List[Event] = []
        self._events_by_settlement: Dict[str, List[Event]] = {}
        self._edges: Dict[str, List[Edge]] = {}
        self._named: List[Tuple[str, List[str], float, str]] = []
        self._build_graph()

    # -- lookup ------------------------------------------------------------
    def find_settlement(self, key: str) -> Settlement:
        s = self.lookup_settlement(key)
        if s is None:
            raise KeyError(f"Unknown settlement: {key!r}")
        return s

    def lookup_settlement(self, key: str) -> Optional[Settlement]:
        if isinstance(key, Settlement):
            return key
        slug = slugify(key)
        if slug in self.settlements:
            return self.settlements[slug]
        matches = [s for s in self.settlements.values() if slug in s.id]
        if not matches:
            low = str(key).lower()
            matches = [s for s in self.settlements.values() if low in s.name.lower()]
        if len(matches) == 1:
            return matches[0]
        if matches:
            matches.sort(key=lambda s: (len(s.id), -s.population))
            return matches[0]
        return None

    def find_commodity(self, key: str) -> Commodity:
        c = self.lookup_commodity(key)
        if c is None:
            raise KeyError(f"Unknown commodity: {key!r}")
        return c

    def find_mobile_location(self, key: str) -> MobileLocation:
        location = self.lookup_mobile_location(key)
        if location is None:
            raise KeyError(f"Unknown mobile location: {key!r}")
        return location

    def lookup_mobile_location(self, key: str) -> Optional[MobileLocation]:
        if isinstance(key, MobileLocation):
            return key
        slug = slugify(key)
        if slug in self.mobile_locations:
            return self.mobile_locations[slug]
        matches = [
            location for location in self.mobile_locations.values()
            if slug in location.id or str(key).lower() in location.name.lower()
        ]
        return matches[0] if len(matches) == 1 else None

    def lookup_commodity(self, key: str) -> Optional[Commodity]:
        if isinstance(key, Commodity):
            return key
        slug = slugify(key)
        if slug in self.commodities:
            return self.commodities[slug]
        low = str(key).lower()
        matches = [
            c for c in self.commodities.values()
            if slug in c.id or low in c.name.lower()
        ]
        if not matches:
            matches = [
                c for c in self.commodities.values()
                if any(tok and tok in c.name.lower() for tok in low.split())
            ]
        if len(matches) == 1:
            return matches[0]
        if matches:
            matches.sort(key=lambda c: (len(c.id), c.base_price))
            return matches[0]
        return None

    @property
    def regions(self) -> List[str]:
        return sorted({s.region for s in self.settlements.values()})

    # -- graph construction -------------------------------------------------
    def _add_edge(self, a: str, b: str, quality: float, kind: str, name: str = "", *, inferred: bool = False) -> None:
        if a == b or a not in self.settlements or b not in self.settlements:
            return
        sa, sb = self.settlements[a], self.settlements[b]
        distance = math.dist((sa.x, sa.y), (sb.x, sb.y))
        distance = max(8.0, distance)
        kind = canonical_kind(kind)
        existing = None
        for edge in self._edges.setdefault(a, []):
            if edge.dst == b:
                existing = edge
                break
        if existing is not None:
            # Two *separate* arteries between the same pair are alternatives,
            # not a multimodal leg: a town on both a road and a river lets a
            # trader pick the cheaper, so the better one wins outright. A leg
            # is only multimodal when a single named route declares it so,
            # meaning the cargo genuinely has to change carrier en route.
            better = (_profile_for_kind(kind)[0] / quality
                      < _profile_for_kind(existing.kind)[0] / existing.quality)
            if not better:
                return
            self._edges[a] = [e for e in self._edges[a] if e.dst != b]
            self._edges[b] = [e for e in self._edges.get(b, []) if e.dst != a]
        self._edges.setdefault(a, []).append(Edge(a, b, distance, quality, kind, name, inferred))
        self._edges.setdefault(b, []).append(Edge(b, a, distance, quality, kind, name, inferred))

    def _add_sea_edge(self, a: str, b: str, quality: float, kind: str,
                      name: str = "") -> None:
        """Split a sea lane at harbours lying close to and between its ends."""
        if a not in self.settlements or b not in self.settlements:
            return
        start, end = self.settlements[a], self.settlements[b]
        dx, dy = end.x - start.x, end.y - start.y
        length_squared = dx * dx + dy * dy
        if length_squared <= 0:
            return
        length = math.sqrt(length_squared)
        corridor = min(80.0, max(30.0, length * 0.06))
        basins = {port for port in (start.port, end.port) if port}
        calls: List[Tuple[float, str]] = []
        for harbour in self.settlements.values():
            if harbour.id in (a, b) or not harbour.port:
                continue
            if basins and harbour.port not in basins:
                continue
            along = ((harbour.x - start.x) * dx + (harbour.y - start.y) * dy) / length_squared
            if along <= 0.05 or along >= 0.95:
                continue
            closest = (start.x + along * dx, start.y + along * dy)
            if math.dist((harbour.x, harbour.y), closest) <= corridor:
                calls.append((along, harbour.id))
        stops = [a] + [sid for _along, sid in sorted(calls)] + [b]
        for src, dst in zip(stops, stops[1:]):
            if (name.endswith("coasting run")
                    and frozenset((src, dst)) in BLOCKED_COASTING_LEGS):
                continue
            self._add_edge(src, dst, quality, kind, name)

    def _build_graph(self) -> None:
        self._edges = {sid: [] for sid in self.settlements}

        # 1. Named roads, trails, rivers, tunnels and skyways. A kind may name
        #    several modes at once, joined with "+", for arteries that have to
        #    change carrier along the way.
        for name, stops, quality, kind in NAMED_ROUTES:
            kind = canonical_kind(kind)
            self._named.append((name, list(stops), quality, kind))
            for a, b in zip(stops, stops[1:]):
                self._add_edge(a, b, quality, kind, name, inferred="tunnel" in kind.split("+"))

        for name, stops, quality in SURVEYED_ROADS:
            if not all(stop in self.settlements for stop in stops):
                continue
            self._named.append((name, list(stops), quality, "road"))
            for a, b in zip(stops, stops[1:]):
                self._add_edge(a, b, quality, "road", name)

        for name, stops, quality, kind in SURVEYED_MAGIC_ROUTES:
            if not all(stop in self.settlements for stop in stops):
                continue
            kind = canonical_kind(kind)
            self._named.append((name, list(stops), quality, kind))
            for a, b in zip(stops, stops[1:]):
                self._add_edge(a, b, quality, kind, name)

        # 2. Named sea lanes. These default to plain "sea", but a lane may
        #    carry an explicit kind as a fourth element when it is more than
        #    that -- a lane that ends in a river mouth, say.
        for lane in NAMED_SEA_LANES:
            name, stops, quality = lane[0], lane[1], lane[2]
            kind = canonical_kind(lane[3]) if len(lane) > 3 else "sea"
            self._named.append((name, list(stops), quality, kind))
            for a, b in zip(stops, stops[1:]):
                self._add_sea_edge(a, b, quality, kind, name)

        # Survey-promoted harbours can define short passages without becoming
        # permanent entries in the built-in settlement catalogue.
        for name, stops, quality in SURVEYED_SEA_LANES:
            if not all(stop in self.settlements for stop in stops):
                continue
            self._named.append((name, list(stops), quality, "sea"))
            for a, b in zip(stops, stops[1:]):
                self._add_edge(a, b, quality, "sea", name)

        for name, start, end, quality in SURVEYED_FERRY_ROUTES:
            self._add_edge(start, end, quality, "ferry", name)

        # 3. Local caravan tracks: link each settlement to its nearest
        #    neighbours in the same or an adjacent zone.
        nodes = list(self.settlements.values())
        established = [
            s for s in nodes if not s.has_trait(SURVEYED_MARKET_TRAIT)
        ]
        for s in established:
            allowed = {s.zone} | ZONE_ADJACENCY.get(s.zone, set())
            candidates = []
            for other in established:
                if other.id == s.id or other.landmass != s.landmass:
                    continue
                if other.underdark != s.underdark:
                    continue
                if other.zone not in allowed:
                    continue
                d = math.dist((s.x, s.y), (other.x, other.y))
                limit = 260.0 if other.zone == s.zone else 200.0
                if d <= limit:
                    candidates.append((d, other))
            candidates.sort(key=lambda pair: pair[0])
            for d, other in candidates[:4]:
                rough = s.terrain in ("mountains", "marsh", "jungle", "desert", "tundra")
                quality = 0.85 if other.zone == s.zone else 0.7
                if rough:
                    quality -= 0.15
                label = "caravan track"
                if s.underdark:
                    kind = "tunnel"
                    label = "Underdark passage"
                elif s.terrain == "marsh":
                    # A fen has to be worked across: part track, part hauling
                    # the load bodily over ground that will not take a waggon.
                    # Deliberately portage rather than ferry -- boats would
                    # make the crossing come out cheaper than dry going, which
                    # is precisely backwards for a marsh.
                    kind = "track+portage"
                    label = "fen portage"
                else:
                    kind = "track"
                self._add_edge(s.id, other.id, max(0.35, quality), kind, label, inferred=True)

        # 4. Coastal shipping between ports in the same basin.
        ports: Dict[str, List[Settlement]] = {}
        for s in nodes:
            if s.port:
                ports.setdefault(s.port, []).append(s)
        for basin, group in ports.items():
            for s in group:
                near = sorted(
                    ((math.dist((s.x, s.y), (o.x, o.y)), o) for o in group if o.id != s.id),
                    key=lambda pair: pair[0],
                )
                for d, other in near[:4]:
                    if d > MAX_COASTING_LEG_MILES:
                        continue
                    if frozenset((s.id, other.id)) in BLOCKED_COASTING_LEGS:
                        continue
                    self._add_sea_edge(
                        s.id, other.id, 0.95, "sea", f"{basin} coasting run"
                    )

        # 5. Nothing may be stranded: connect isolated nodes to the closest
        #    reachable settlement on the same landmass.
        for s in established:
            if self._edges.get(s.id):
                continue
            near = sorted(
                (
                    (math.dist((s.x, s.y), (o.x, o.y)), o)
                    for o in established
                    if o.id != s.id and o.landmass == s.landmass
                ),
                key=lambda pair: pair[0],
            )
            if near:
                self._add_edge(s.id, near[0][1].id, 0.4, "track", "wilderness trail")

        # 6. Settlements close to a traced map road become stops on that road.
        #    This lets survey-only markets use an existing connector instead
        #    of receiving a redundant long-distance local trail.
        try:
            from .mapdata import road_connections

            traced_connections = road_connections(nodes, include_spanning=True)
        except (AtlasError, OSError, ValueError, TypeError, KeyError):
            traced_connections = []
        for connection in traced_connections:
            if not connection["consecutive"]:
                continue
            kind = connection["kind"]
            quality = 0.85 if kind == "road" else 0.7
            self._add_edge(
                connection["a"], connection["b"], quality, kind,
                connection["name"],
            )

        measured_distances = {}
        for connection in traced_connections:
            key = (frozenset((connection["a"], connection["b"])), connection["kind"])
            distance = float(connection["distance"])
            measured_distances[key] = min(measured_distances.get(key, float("inf")), distance)
        for edges in self._edges.values():
            for edge in edges:
                key = (frozenset((edge.src, edge.dst)), edge.kind)
                if key in measured_distances:
                    edge.distance = max(8.0, measured_distances[key])

        # 7. Remaining survey-only markets form local feeder trees rooted at their
        # nearest established hub. A minimum spanning tree keeps each leg
        # local instead of drawing every small market straight to a distant
        # regional centre; separate roots never become shortcuts between hubs.
        feeder_groups: Dict[str, List[Settlement]] = {}
        for s in nodes:
            if not s.has_trait(SURVEYED_MARKET_TRAIT):
                continue
            if self._edges.get(s.id):
                continue
            near = sorted(
                (
                    (math.dist((s.x, s.y), (o.x, o.y)), o)
                    for o in established
                    if o.landmass == s.landmass and o.underdark == s.underdark
                ),
                key=lambda pair: pair[0],
            )
            if near:
                feeder_groups.setdefault(near[0][1].id, []).append(s)

        for root_id, markets in feeder_groups.items():
            connected = [self.settlements[root_id]]
            remaining = {market.id: market for market in markets}
            while remaining:
                _distance, market_id, _parent_id, market, parent = min(
                    (
                        math.dist((market.x, market.y), (parent.x, parent.y)),
                        market.id,
                        parent.id,
                        market,
                        parent,
                    )
                    for market in remaining.values()
                    for parent in connected
                )
                crosses_water = market.id in SURVEYED_FERRY_MARKETS
                self._add_edge(
                    market.id,
                    parent.id,
                    0.65,
                    "ferry" if crosses_water else "trail",
                    "local market ferry" if crosses_water
                    else "local market trail",
                    inferred=True,
                )
                connected.append(market)
                del remaining[market_id]

    def edges_from(self, settlement_id: str) -> List[Edge]:
        return self._edges.get(settlement_id, [])

    @property
    def named_routes(self) -> List[Tuple[str, List[str], float, str]]:
        return self._named

    # -- risk ---------------------------------------------------------------
    def edge_risk(self, edge: Edge) -> float:
        """Freight risk premium for a leg, including event-driven danger."""
        a, b = self.settlements[edge.src], self.settlements[edge.dst]
        security = (a.security + b.security) / 2.0
        risk = edge.hazard(security) * 0.6
        # Every relaxation in Dijkstra lands here, so use the per-settlement
        # index rather than re-scanning the whole chronicle.  An event covering
        # both ends -- a regional war, say -- must still only be charged once.
        near = self.events_for(a)
        far = self.events_for(b)
        if far and far is not near:
            already = {e.id for e in near}
            near = list(near) + [e for e in far if e.id not in already]
        for event in near:
            if event.risk:
                risk += event.risk
        return max(0.0, risk)

    # -- events -------------------------------------------------------------
    def add_event(self, event: Event) -> Event:
        self.events[event.id] = event
        self.revision += 1
        return event

    def remove_event(self, event_id: str) -> bool:
        removed = self.events.pop(event_id, None) is not None
        if removed:
            self.revision += 1
        return removed

    def clear_events(self) -> None:
        self.events.clear()
        self.revision += 1

    def active_events(self) -> List[Event]:
        """Every registered event whose window covers the current month."""
        stamp = (self.revision, self.date.absolute_month())
        if self._events_stamp != stamp:
            self._events_stamp = stamp
            self._events_active = [
                e for e in self.events.values() if e.active_on(stamp[1])
            ]
            self._events_by_settlement = {}
        return self._events_active

    def events_for(self, settlement: Settlement) -> List[Event]:
        """Active events that touch one settlement, by id, zone or region.

        The pricing pass calls this for every commodity in a market, so the
        per-settlement answer is cached alongside the active list and thrown
        away with it.
        """
        active = self.active_events()
        found = self._events_by_settlement.get(settlement.id)
        if found is None:
            found = [e for e in active if e.applies_to_settlement(settlement)]
            self._events_by_settlement[settlement.id] = found
        return found

    def set_date(self, date: HarptosDate, *, follow_real_date: bool = False) -> None:
        self.date = date
        self.follows_real_date = follow_real_date
        self.revision += 1
        self._date_revisions += 1

    def sync_real_date(self) -> bool:
        """Advance a live world when the current UTC civil date changes."""
        if not self.follows_real_date:
            return False
        current = HarptosDate.today()
        if current == self.date:
            return False
        self.date = current
        self.revision += 1
        self._date_revisions += 1
        return True

    def rebuild(self) -> None:
        """Rebuild the trade network after settlement coordinates change.

        Calibrating the map against a published poster moves cities, and every
        caravan distance - and therefore every freight cost, travel time and
        landed price - is derived from those coordinates.  Bumping the revision
        drops the price caches that were computed against the old geography.
        """
        self._edges = {}
        self._named = []
        self._events_stamp = None
        self._events_active = []
        self._events_by_settlement = {}
        self._build_graph()
        self.revision += 1

    # -- pathfinding --------------------------------------------------------
    def _dijkstra(self, start: str, weight):
        """Generic single-source shortest path. `weight(edge) -> float`."""
        dist = {start: 0.0}
        prev: Dict[str, Optional[Edge]] = {start: None}
        queue = [(0.0, start)]
        seen = set()
        while queue:
            d, node = heapq.heappop(queue)
            if node in seen:
                continue
            seen.add(node)
            for edge in self._edges.get(node, []):
                nd = d + weight(edge)
                if nd < dist.get(edge.dst, math.inf):
                    dist[edge.dst] = nd
                    prev[edge.dst] = edge
                    heapq.heappush(queue, (nd, edge.dst))
        return dist, prev

    def _weighted_freight_graph(self, pounds, perishable, base_price):
        stamp = (getattr(self, "revision", 0), self.date.absolute_month() if hasattr(self, "date") else None,
                 pounds, perishable, base_price)
        if getattr(self, "_freight_graph_stamp", None) != stamp:
            spoil_rate = perishable * base_price / 14.0
            self._freight_graph = {
                node: [(edge, edge.freight_units(self.edge_risk(edge)) * FREIGHT_RATE * pounds
                         + spoil_rate * edge.days) for edge in edges]
                for node, edges in self._edges.items()
            }
            self._freight_graph_stamp = stamp
        return self._freight_graph

    def multi_source_freight(
        self, sources: Dict[str, float], pounds: float, perishable: float,
        base_price: float, *, max_days: Optional[float] = None,
    ) -> Tuple[Dict[str, float], Dict[str, str], Dict[str, Tuple[float, float]]]:
        """Cheapest landed cost for a good, given `sources` -> price at source.

        Returns (landed cost, origin settlement id, (miles, days) hauled) per
        settlement id.  Distance and time are accumulated along the winning
        path so callers never need a second search.
        """
        if max_days is not None:
            return self._fresh_freight(sources, pounds, perishable, base_price, max_days)
        if (len(sources) == 1 and perishable == 0 and math.isfinite(base_price)
                and math.isfinite(pounds) and pounds > 0):
            source, price = next(iter(sources.items()))
            if source in self.settlements and math.isfinite(price) and price >= 0:
                costs, distances = self._durable_freight(source)
                landed = {sid: value for sid, cost in costs.items()
                          if math.isfinite(value := price + cost * pounds)}
                return (landed, {sid: source for sid in landed},
                        {sid: distances[sid] for sid in landed})
        dist: Dict[str, float] = dict(sources)
        origin: Dict[str, str] = {sid: sid for sid in sources}
        haul: Dict[str, Tuple[float, float]] = {sid: (0.0, 0.0) for sid in sources}
        queue = [(cost, sid) for sid, cost in sources.items()]
        heapq.heapify(queue)
        seen = set()
        graph = self._weighted_freight_graph(pounds, perishable, base_price)
        while queue:
            cost, node = heapq.heappop(queue)
            if node in seen:
                continue
            seen.add(node)
            miles, days = haul[node]
            for edge, leg in graph.get(node, []):
                nd = cost + leg
                if nd < dist.get(edge.dst, math.inf):
                    dist[edge.dst] = nd
                    origin[edge.dst] = origin[node]
                    haul[edge.dst] = (miles + edge.distance, days + edge.days)
                    heapq.heappush(queue, (nd, edge.dst))
        return dist, origin, haul

    def _durable_freight(self, source):
        # Without spoilage, source price is additive and weight scales every
        # edge equally. Reuse the same routes across durable commodities.
        stamp = (self.revision, self.date.absolute_month())
        if getattr(self, "_durable_freight_stamp", None) != stamp:
            self._durable_freight_stamp = stamp
            self._durable_freight_cache = {}
        cache = self._durable_freight_cache
        if source not in cache:
            graph = self._weighted_freight_graph(1.0, 0.0, 0.0)
            costs = {source: 0.0}
            distances = {source: (0.0, 0.0)}
            queue = [(0.0, source)]
            seen = set()
            while queue:
                cost, node = heapq.heappop(queue)
                if node in seen:
                    continue
                seen.add(node)
                miles, days = distances[node]
                for edge, leg in graph.get(node, ()):
                    total = cost + leg
                    if total < costs.get(edge.dst, math.inf):
                        costs[edge.dst] = total
                        distances[edge.dst] = (miles + edge.distance, days + edge.days)
                        heapq.heappush(queue, (total, edge.dst))
            cache[source] = costs, distances
        return cache[source]

    def _fresh_freight(self, sources, pounds, perishable, base_price, max_days):
        labels = {sid: [(cost, 0.0)] for sid, cost in sources.items()}
        queue = [(cost, 0.0, sid, sid, 0.0) for sid, cost in sources.items()]
        heapq.heapify(queue)
        landed, origins, hauls = {}, {}, {}
        graph = self._weighted_freight_graph(pounds, perishable, base_price)
        while queue:
            cost, days, node, origin, miles = heapq.heappop(queue)
            if (cost, days) not in labels[node]:
                continue
            if cost < landed.get(node, math.inf):
                landed[node], origins[node], hauls[node] = cost, origin, (miles, days)
            for edge, leg in graph.get(node, []):
                arrival = days + edge.days
                if arrival > max_days:
                    continue
                delivered = cost + leg
                existing = labels.setdefault(edge.dst, [])
                if any(price <= delivered and elapsed <= arrival for price, elapsed in existing):
                    continue
                labels[edge.dst] = [(price, elapsed) for price, elapsed in existing
                                    if not (delivered <= price and arrival <= elapsed)]
                labels[edge.dst].append((delivered, arrival))
                heapq.heappush(queue, (delivered, arrival, edge.dst, origin, miles + edge.distance))
        return landed, origins, hauls

    def route(self, start: str, end: str, optimise: str = "days") -> Dict:
        """Best path between two markets, optimising 'days' or 'cost'."""
        a = self.find_settlement(start)
        b = self.find_settlement(end)
        if optimise == "cost":
            weight = lambda e: e.freight_units(self.edge_risk(e)) * FREIGHT_RATE * 100
        else:
            weight = lambda e: e.days * (1.0 + self.edge_risk(e) * 0.25)
        dist, prev = self._dijkstra(a.id, weight)
        if b.id not in dist:
            return {
                "origin": a.name, "destination": b.name, "reachable": False,
                "legs": [], "days": None, "distance": None,
            }
        legs: List[Edge] = []
        node = b.id
        while node != a.id:
            edge = prev[node]
            if edge is None:
                break
            legs.append(edge)
            node = edge.src
        legs.reverse()
        total_days = sum(e.days for e in legs)
        total_distance = sum(e.distance for e in legs)
        hazard = 0.0
        for e in legs:
            hazard = max(hazard, self.edge_risk(e))
        return {
            "origin": a.name,
            "destination": b.name,
            "reachable": True,
            "distance": round(total_distance, 1),
            "days": round(total_days, 1),
            "caravan_days": round(total_distance / 24.0, 1),
            "hazard": round(hazard, 2),
            "modes": sorted({m for e in legs for m in e.modes}),
            # every extra mode on a leg is one more time the cargo is unloaded
            "transfers": sum(len(e.modes) - 1 for e in legs),
            "freight_gp_per_100lb": round(
                sum(e.freight_units(self.edge_risk(e)) for e in legs) * FREIGHT_RATE * 100,
                2,
            ),
            "legs": [
                {
                    "from": self.settlements[e.src].name,
                    "to": self.settlements[e.dst].name,
                    "via": e.name or "local track",
                    "mode": e.kind,
                    "modes": list(e.modes),
                    "mode_label": describe_modes(e.kind),
                    "multimodal": e.multimodal,
                    "miles": round(e.distance, 1),
                    "days": round(e.days, 1),
                    "hazard": round(self.edge_risk(e), 2),
                }
                for e in legs
            ],
            "path": [a.name] + [self.settlements[e.dst].name for e in legs],
        }

    def travel_days(self, start: str, end: str) -> Optional[float]:
        return self.route(start, end).get("days")


_WORLD: Optional[World] = None


#: Whether the singleton world is born with a history.  The chronicle gives
#: every settlement seven years of droughts, bandits, famines and booms, and
#: those shocks are folded into every price the engine quotes.  Set this to
#: False before the first `get_world()` call for a bare, event-free world.
USE_CHRONICLE = True


def _new_world() -> World:
    from .inventory_cache import default_inventory_cache_path

    world = World(config=EconomyConfig(
        inventory_cache_path=str(default_inventory_cache_path())))
    if USE_CHRONICLE:
        # Imported here rather than at module scope because `chronicle` imports
        # `events`, which imports this module.
        from .chronicle import install_chronicle
        install_chronicle(world)
    return world


def get_world() -> World:
    """Process-wide singleton world (used by the CLI and MCP server)."""
    global _WORLD
    if _WORLD is None:
        _WORLD = _new_world()
    else:
        _WORLD.sync_real_date()
    return _WORLD


def reset_world() -> World:
    global _WORLD
    _WORLD = _new_world()
    return _WORLD
