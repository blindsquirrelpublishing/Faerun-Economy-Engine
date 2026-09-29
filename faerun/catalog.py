"""Runtime CRUD for commodities, settlements, businesses and named routes.

Every mutation updates the live :class:`~faerun.world.World` singleton
immediately (so subsequent price/route/report calls in the same process see
it) and rewrites the affected JSON file under ``faerun/data/store/`` so the
change survives a restart. This is what backs the MCP server's write tools,
letting an assistant add or edit products, settlements, businesses and trade
routes and have every later query reflect the change.
"""
from __future__ import annotations

import importlib
from typing import Any, Dict, List, Optional

from . import data_store
from .models import Business, Commodity, Settlement, slugify
from .world import get_world


class CatalogError(ValueError):
    """A CRUD request was invalid (bad id, unknown reference, duplicate...)."""


def _world():
    return get_world()


def reload_from_disk() -> Dict[str, int]:
    """Pull the current faerun/data/store/ catalog into this process's world.

    Commodities, settlements and businesses are only copied into the World
    once at startup, so a long-running dashboard or a second MCP server
    process keeps whatever it had in memory even after another process edits
    the catalog. This re-runs each data module (so BOMs, harvest calendars,
    storage policies and map calibration are recomputed) and swaps the fresh
    result into the live world, then rebuilds the trade network. Named routes
    and sea lanes need no action here: add_route/remove_route already mutate
    the shared list in place, so every process sees those immediately.
    """
    world = _world()
    from .data import businesses as businesses_mod
    from .data import commodities as commodities_mod
    from .data import settlements as settlements_mod

    importlib.reload(commodities_mod)
    importlib.reload(settlements_mod)
    importlib.reload(businesses_mod)

    world.commodities = {c.id: c for c in commodities_mod.COMMODITIES}
    world.settlements = {s.id: s for s in settlements_mod.SETTLEMENTS}
    world.businesses = {
        b.id: b for b in businesses_mod.BUSINESSES
        if any(loc in world.settlements for loc in b.locations)
    }
    world.rebuild()
    return {
        "commodities": len(world.commodities),
        "settlements": len(world.settlements),
        "businesses": len(world.businesses),
    }


# ---------------------------------------------------------------------------
# Commodities / products
# ---------------------------------------------------------------------------

def create_commodity(
    name: str, category: str, base_price: float, *, id: Optional[str] = None,
    unit: str = "item", weight: float = 1.0, produced_by: Optional[List[str]] = None,
    required_skill: Optional[Dict[str, float]] = None,
    demand: float = 1.0, luxury: float = 0.0, perishable: float = 0.0,
    demand_traits: Optional[Dict[str, float]] = None, season: Optional[Dict[str, float]] = None,
    substitutes: Optional[List[str]] = None, requires: Optional[List[str]] = None,
    description: str = "", bom: Optional[Dict[str, float]] = None,
) -> Commodity:
    world = _world()
    cid = slugify(id or name)
    if not cid:
        raise CatalogError("A commodity needs a usable name or id")
    if cid in world.commodities:
        raise CatalogError(f"Commodity {cid!r} already exists; use update_commodity")
    commodity = Commodity(
        id=cid, name=name, category=category, base_price=float(base_price),
        unit=unit, weight=float(weight), produced_by=list(produced_by or []),
        required_skill={tag: float(level) for tag, level in (required_skill or {}).items()},
        demand=float(demand), luxury=float(luxury), perishable=float(perishable),
        demand_traits=dict(demand_traits or {}), season=dict(season or {}),
        substitutes=list(substitutes or []), requires=list(requires or []),
        description=description, bom=dict(bom or {}),
    )
    world.commodities[cid] = commodity
    world.revision += 1
    data_store.save_commodities(world.commodities.values())
    return commodity


def update_commodity(id: str, **fields: Any) -> Commodity:
    world = _world()
    cid = slugify(id)
    existing = world.commodities.get(cid)
    if existing is None:
        raise CatalogError(f"Unknown commodity: {id!r}")
    unknown = set(fields) - {
        "name", "category", "base_price", "unit", "weight", "produced_by",
        "required_skill",
        "demand", "luxury", "perishable", "demand_traits", "season",
        "substitutes", "requires", "description", "bom",
    }
    if unknown:
        raise CatalogError(f"Unknown commodity field(s): {sorted(unknown)}")
    for key, value in fields.items():
        if value is not None:
            setattr(existing, key, value)
    world.revision += 1
    data_store.save_commodities(world.commodities.values())
    return existing


def delete_commodity(id: str) -> bool:
    world = _world()
    cid = slugify(id)
    removed = world.commodities.pop(cid, None) is not None
    if removed:
        world.revision += 1
        data_store.save_commodities(world.commodities.values())
    return removed


# ---------------------------------------------------------------------------
# Settlements / locations
# ---------------------------------------------------------------------------

def create_settlement(
    name: str, region: str, zone: str, population: int, x: float, y: float, *,
    id: Optional[str] = None, wealth: float = 1.0, tax: float = 0.05,
    security: float = 0.75, port: Optional[str] = None, river: bool = False,
    terrain: str = "plains", landmass: str = "faerun", underdark: bool = False,
    traits: Optional[List[str]] = None, industries: Optional[Dict[str, float]] = None,
    specialties: Optional[Dict[str, float]] = None, shortages: Optional[List[str]] = None,
    ruler: str = "", description: str = "",
) -> Settlement:
    world = _world()
    sid = slugify(id or name)
    if not sid:
        raise CatalogError("A settlement needs a usable name or id")
    if sid in world.settlements:
        raise CatalogError(f"Settlement {sid!r} already exists; use update_settlement")
    settlement = Settlement(
        id=sid, name=name, region=region, zone=zone, population=int(population),
        x=float(x), y=float(y), wealth=float(wealth), tax=float(tax),
        security=float(security), port=port, river=bool(river), terrain=terrain,
        landmass=landmass, underdark=bool(underdark), traits=list(traits or []),
        industries=dict(industries or {}), specialties=dict(specialties or {}),
        shortages=list(shortages or []), ruler=ruler, description=description,
    )
    world.settlements[sid] = settlement
    world.rebuild()
    data_store.save_settlements(world.settlements.values())
    return settlement


def update_settlement(id: str, **fields: Any) -> Settlement:
    world = _world()
    sid = slugify(id)
    existing = world.settlements.get(sid)
    if existing is None:
        raise CatalogError(f"Unknown settlement: {id!r}")
    unknown = set(fields) - {
        "name", "region", "zone", "population", "x", "y", "wealth", "tax",
        "security", "port", "river", "terrain", "landmass", "underdark",
        "traits", "industries", "specialties", "shortages", "ruler", "description",
    }
    if unknown:
        raise CatalogError(f"Unknown settlement field(s): {sorted(unknown)}")
    geometry_changed = any(
        key in fields and fields[key] is not None
        for key in ("x", "y", "zone", "landmass", "underdark", "terrain", "port")
    )
    for key, value in fields.items():
        if value is not None:
            setattr(existing, key, value)
    if geometry_changed:
        world.rebuild()
    else:
        world.revision += 1
    data_store.save_settlements(world.settlements.values())
    return existing


def delete_settlement(id: str) -> bool:
    world = _world()
    sid = slugify(id)
    removed = world.settlements.pop(sid, None) is not None
    if not removed:
        return False
    stranded = [bid for bid, b in world.businesses.items()
                if not any(loc in world.settlements for loc in b.locations)]
    for bid in stranded:
        del world.businesses[bid]
    world.rebuild()
    data_store.save_settlements(world.settlements.values())
    if stranded:
        data_store.save_businesses(world.businesses.values())
    return True


# ---------------------------------------------------------------------------
# Businesses
# ---------------------------------------------------------------------------

def create_business(
    name: str, headquarters: str, locations: List[str], *, id: Optional[str] = None,
    specialties: Optional[List[str]] = None, offers: Optional[Dict[str, str]] = None,
    price_modifier: float = 1.0, description: str = "",
) -> Business:
    world = _world()
    bid = slugify(id or name)
    if not bid:
        raise CatalogError("A business needs a usable name or id")
    if bid in world.businesses:
        raise CatalogError(f"Business {bid!r} already exists; use update_business")
    hq = world.lookup_settlement(headquarters)
    if hq is None:
        raise CatalogError(f"Unknown headquarters settlement: {headquarters!r}")
    loc_ids: List[str] = []
    for loc in (locations or [headquarters]):
        settlement = world.lookup_settlement(loc)
        if settlement is None:
            raise CatalogError(f"Unknown location settlement: {loc!r}")
        if settlement.id not in loc_ids:
            loc_ids.append(settlement.id)
    if hq.id not in loc_ids:
        loc_ids.insert(0, hq.id)
    business = Business(
        id=bid, name=name, headquarters=hq.id, locations=loc_ids,
        specialties=list(specialties or []), offers=dict(offers or {}),
        price_modifier=float(price_modifier), description=description,
    )
    world.businesses[bid] = business
    world.revision += 1
    data_store.save_businesses(world.businesses.values())
    return business


def update_business(id: str, **fields: Any) -> Business:
    world = _world()
    bid = slugify(id)
    existing = world.businesses.get(bid)
    if existing is None:
        raise CatalogError(f"Unknown business: {id!r}")
    unknown = set(fields) - {
        "name", "headquarters", "locations", "specialties", "offers",
        "price_modifier", "description",
    }
    if unknown:
        raise CatalogError(f"Unknown business field(s): {sorted(unknown)}")
    if fields.get("headquarters") is not None:
        hq = world.lookup_settlement(fields["headquarters"])
        if hq is None:
            raise CatalogError(f"Unknown headquarters settlement: {fields['headquarters']!r}")
        fields["headquarters"] = hq.id
    if fields.get("locations") is not None:
        loc_ids = []
        for loc in fields["locations"]:
            settlement = world.lookup_settlement(loc)
            if settlement is None:
                raise CatalogError(f"Unknown location settlement: {loc!r}")
            if settlement.id not in loc_ids:
                loc_ids.append(settlement.id)
        fields["locations"] = loc_ids
    for key, value in fields.items():
        if value is not None:
            setattr(existing, key, value)
    if existing.headquarters not in existing.locations:
        existing.locations.insert(0, existing.headquarters)
    world.revision += 1
    data_store.save_businesses(world.businesses.values())
    return existing


def delete_business(id: str) -> bool:
    world = _world()
    bid = slugify(id)
    removed = world.businesses.pop(bid, None) is not None
    if removed:
        world.revision += 1
        data_store.save_businesses(world.businesses.values())
    return removed


# ---------------------------------------------------------------------------
# Named routes and sea lanes
# ---------------------------------------------------------------------------

def _resolved_stops(world, stops: List[str]) -> List[str]:
    if len(stops) < 2:
        raise CatalogError("A route needs at least two stops")
    ids = []
    for stop in stops:
        settlement = world.lookup_settlement(stop)
        if settlement is None:
            raise CatalogError(f"Unknown settlement: {stop!r}")
        ids.append(settlement.id)
    return ids


def add_route(name: str, stops: List[str], quality: float = 1.0, kind: str = "road") -> Dict[str, Any]:
    world = _world()
    stop_ids = _resolved_stops(world, stops)
    from .data.routes import NAMED_ROUTES
    NAMED_ROUTES[:] = [route for route in NAMED_ROUTES if route[0] != name]
    NAMED_ROUTES.append((name, stop_ids, float(quality), kind))
    data_store.save_routes(NAMED_ROUTES)
    world.rebuild()
    return {"name": name, "stops": stop_ids, "quality": quality, "kind": kind}


def remove_route(name: str) -> bool:
    world = _world()
    from .data.routes import NAMED_ROUTES
    before = len(NAMED_ROUTES)
    NAMED_ROUTES[:] = [route for route in NAMED_ROUTES if route[0] != name]
    removed = len(NAMED_ROUTES) != before
    if removed:
        data_store.save_routes(NAMED_ROUTES)
        world.rebuild()
    return removed


def add_sea_lane(name: str, stops: List[str], quality: float = 1.0,
                  kind: Optional[str] = None) -> Dict[str, Any]:
    world = _world()
    stop_ids = _resolved_stops(world, stops)
    from .data.routes import NAMED_SEA_LANES
    NAMED_SEA_LANES[:] = [lane for lane in NAMED_SEA_LANES if lane[0] != name]
    lane = (name, stop_ids, float(quality), kind) if kind else (name, stop_ids, float(quality))
    NAMED_SEA_LANES.append(lane)
    data_store.save_sea_lanes(NAMED_SEA_LANES)
    world.rebuild()
    return {"name": name, "stops": stop_ids, "quality": quality, "kind": kind}


def remove_sea_lane(name: str) -> bool:
    world = _world()
    from .data.routes import NAMED_SEA_LANES
    before = len(NAMED_SEA_LANES)
    NAMED_SEA_LANES[:] = [lane for lane in NAMED_SEA_LANES if lane[0] != name]
    removed = len(NAMED_SEA_LANES) != before
    if removed:
        data_store.save_sea_lanes(NAMED_SEA_LANES)
        world.rebuild()
    return removed
