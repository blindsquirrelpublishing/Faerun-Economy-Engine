"""A small stdlib-only web UI for browsing Faerun market prices.

Run it with:

    python -m faerun.web

then open http://127.0.0.1:8765 in a browser. No third-party packages are
needed - this uses `http.server` and serves the engine's live output as JSON
to a single-page commodity board. The page itself lives in `webassets.py` so
the whole UI ships as importable Python with no package-data to install.
"""

from __future__ import annotations

import argparse
import copy
from contextlib import contextmanager
import html
import ipaddress
import json
import math
import re
import threading
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .calendar import MONTHS, HarptosDate, parse_month
from .city import city_directory
from .buildinggen import generate_buildings
from .locationgen import generate_location, location_profiles
from .calibration import (
    apply_calibration,
    base_coordinates,
    load_control_points,
    save_control_points,
)
from .economy import (
    commodity_sources,
    compare_prices,
    find_arbitrage,
    market_report,
    price_for,
    price_history,
    special_order_quote,
    trade_summary,
)
from .chronicle import chronicle_summary, month_labels
from .events import EVENT_TEMPLATES, apply_event
from .location import location_detail, location_timeline
from .locationassets import LOCATION_ASSETS
from .detailassets import DETAIL_ASSETS
from .plannerassets import PLANNER_ASSETS
from .transport import plan_shipment
from .mapassets import MAP_ASSETS
from .mobile import mobile_location_summary
from .mobile_economy import mobile_economic_report
from .mobileassets import MOBILE_ASSETS
from .mapdata import map_payload, save_terrain_override, terrain_detail, planar_terrain_tile
from .locationedits import apply_location_edits, save_location_edit
from .routegeometry import load_route_edits, save_route_leg, save_road_junction
from .underlay import set_override, underlay_bytes, underlay_info
from .webassets import ASSETS
from .world import MODES, World, get_world
from .models import price_terms
from .population import land_area_report, population_report
from .census import waterdeep_housing_report
from .mapsurvey import map_survey_report
from .settlement_analysis import DAGGERFORD_PREVIEW, settlement_analysis_report
from .daggerfordassets import DAGGERFORD_ASSETS
from .tradeapi import GET_TRADE_ROUTES, POST_TRADE_ROUTES
from .tradeassets import TRADE_ASSETS
from .trading import TradeError
from .marketboardapi import GET_BOARD_ROUTES, POST_BOARD_ROUTES
from .marketboardassets import BOARD_ASSETS
from .eventsassets import EVENTS_ASSETS
from .waterdeepassets import WATERDEEP_ASSETS
from .loreassets import LORE_ASSETS
from .loredesk import read_desk, post_desk

# Static files are served from a single flat lookup keyed by bare filename.
STATIC: Dict[str, Tuple[str, str]] = dict(ASSETS)
STATIC.update(MAP_ASSETS)
STATIC.update(LOCATION_ASSETS)
STATIC.update(DETAIL_ASSETS)
STATIC.update(PLANNER_ASSETS)
STATIC.update(TRADE_ASSETS)
STATIC.update(BOARD_ASSETS)
STATIC.update(EVENTS_ASSETS)
STATIC.update(WATERDEEP_ASSETS)
STATIC.update(DAGGERFORD_ASSETS)
STATIC.update(MOBILE_ASSETS)
STATIC.update(LORE_ASSETS)

BINARY_STATIC: Dict[str, Tuple[Path, str]] = {
    "daggerford-map.jpg": (DAGGERFORD_PREVIEW, "image/jpeg"),
    "waterdeep-map.jpg": (
        Path(__file__).resolve().parent.parent / "maps" / "waterdeep-map.jpg",
        "image/jpeg",
    ),
    "waterdeep-map-hires.jpg": (
        Path(__file__).resolve().parent.parent / "maps" / "waterdeep-map-hires.jpg",
        "image/jpeg",
    ),
    "waterdeep-map-hires.jpg": (
        Path(__file__).resolve().parent.parent / "maps" / "waterdeep-map-hires.jpg",
        "image/jpeg",
    ),
}

# The price engine caches on the world instance and is not thread-safe, so all
# engine access is serialised. Requests are cheap once the cache is warm.
_LOCK = threading.Lock()
_PROGRESS_LOCK = threading.Lock()
_PROGRESS: Dict[str, Dict[str, Any]] = {}
_PROGRESS_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
_WARMUP_LOCK = threading.Lock()
_SEASONAL_WARMUPS: set[int] = set()

# A browser that navigates away mid-request kills the socket. That is routine,
# not a fault, and must not be reported as a server error - there is nothing
# left to write the response to.
CONNECTION_LOST = (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)


def _finite(value: Any) -> Any:
    """Replace inf/NaN with None so the payload is valid JSON.

    Unreachable routes legitimately produce infinite distances, and
    `JSON.parse` in the browser rejects the `Infinity` literal that
    `json.dumps` would otherwise emit.
    """
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: _finite(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_finite(v) for v in value]
    return value


def _progress_id(raw: Optional[str]) -> str:
    value = str(raw or "").strip()
    return value if _PROGRESS_ID.fullmatch(value) else ""


def _set_progress(progress_id: str, **values: Any) -> None:
    if not progress_id:
        return
    with _PROGRESS_LOCK:
        current = dict(_PROGRESS.get(progress_id, {}))
        current.update(values)
        _PROGRESS[progress_id] = current


def _seasonal_warmup_running(world: World) -> bool:
    with _WARMUP_LOCK:
        return id(world) in _SEASONAL_WARMUPS


def _start_seasonal_warmup(world: World) -> None:
    key = id(world)
    with _WARMUP_LOCK:
        if key in _SEASONAL_WARMUPS:
            return
        _SEASONAL_WARMUPS.add(key)

    def warm() -> None:
        try:
            snapshot = copy.copy(world)
            snapshot.config = replace(world.config, seasonal_inventory=True)
            snapshot._price_cache = {}
            for name in ("_requirements_plan", "_service_accounts_cache", "_resource_plan"):
                snapshot.__dict__.pop(name, None)
            settlement = next(iter(snapshot.settlements), None)
            if settlement is None:
                return
            market_report(settlement, world=snapshot)
            with _LOCK:
                if world.config.seasonal_inventory and world.economy_state_key() == snapshot.economy_state_key():
                    world._price_cache = getattr(world, "_price_cache", {})
                    world._price_cache.update(snapshot._price_cache)
        finally:
            with _WARMUP_LOCK:
                _SEASONAL_WARMUPS.discard(key)

    threading.Thread(target=warm, name="seasonal-price-warmup", daemon=True).start()


@contextmanager
def _simple_market_mode(world: World, enabled: bool):
    if not enabled:
        yield
        return
    original = world.config
    original_cache = getattr(world, "_price_cache", None)
    world.config = replace(original, expanded_requirements=False, seasonal_inventory=False)
    world.revision += 1
    try:
        yield
    finally:
        world.config = original
        world.revision += 1
        if original_cache is None:
            world.__dict__.pop("_price_cache", None)
        else:
            world._price_cache = original_cache


class ApiError(Exception):
    """A bad request that should become a 400 rather than a 500."""

    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.status = status


# ---------------------------------------------------------------------------
# Query-parameter helpers
# ---------------------------------------------------------------------------


def _one(params: Dict[str, list], key: str, default: Optional[str] = None) -> Optional[str]:
    values = params.get(key)
    if not values:
        return default
    value = values[0].strip()
    return value or default


def _int(params: Dict[str, list], key: str, default: int) -> int:
    raw = _one(params, key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ApiError(f"{key} must be a whole number, got {raw!r}")


def _float(params: Dict[str, list], key: str, default: float) -> float:
    raw = _one(params, key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        raise ApiError(f"{key} must be a number, got {raw!r}")


def _required(params: Dict[str, list], key: str) -> str:
    value = _one(params, key)
    if value is None:
        raise ApiError(f"missing required parameter: {key}")
    return value


# ---------------------------------------------------------------------------
# API handlers
# ---------------------------------------------------------------------------


def api_bootstrap(world: World, params) -> Dict[str, Any]:
    """Everything the page needs to draw itself once."""
    settlements = sorted(
        (
            {
                "id": s.id,
                "name": s.name,
                "region": s.region,
                "zone": s.zone,
                "size": s.size,
                "population": s.population,
                "port": bool(s.is_port),
                "underdark": bool(s.underdark),
                "terrain": s.terrain,
                "landmass": s.landmass,
                "river": bool(s.river),
                "x": s.x,
                "y": s.y,
                "wealth": s.wealth,
                "tariff": s.tax,
                "surveyed": s.has_trait("surveyed_market"),
            }
            for s in world.settlements.values()
        ),
        key=lambda s: (s["region"], s["name"]),
    )
    commodities = sorted(
        (
            {
                "id": c.id,
                "name": c.name,
                "category": c.category,
                "production_type": c.production_type,
                "unit": c.unit,
                "base_price": c.base_price,
                "bom": c.bom,
                "production_profile": getattr(c, "production_profile", []),
                "demand_profile": getattr(c, "demand_profile", []),
                "regional_production_profiles": getattr(c, "regional_production_profiles", {}),
                "storage_days": getattr(c, "storage_days", 0),
                "storage_loss": getattr(c, "storage_loss", 0),
                "reserve_days": getattr(c, "reserve_days", 0),
            }
            for c in world.commodities.values()
        ),
        key=lambda c: (c["category"], c["name"]),
    )
    mobile_locations = sorted(
        (
            mobile_location_summary(location, world)
            for location in world.mobile_locations.values()
        ),
        key=lambda location: location["name"],
    )
    return {
        "date": str(world.date),
        "year": world.date.year,
        "month": world.date.month,
        "day": world.date.day,
        "month_name": world.date.month_name,
        "season": world.date.season,
        "moon_phase": world.date.moon_phase,
        "festival": world.date.festival,
        "follows_real_date": world.follows_real_date,
        "seed": world.config.seed,
        "seasonal_inventory": bool(getattr(world.config, "seasonal_inventory", False)),
        "inventory_epoch": getattr(world.config, "inventory_epoch", "1492-01-01"),
        "months": [
            {"number": i + 1, "name": name, "common": common, "season": season}
            for i, (name, common, season) in enumerate(MONTHS)
        ],
        "regions": world.regions,
        "categories": sorted({c["category"] for c in commodities}),
        "settlements": settlements,
        "mobile_locations": mobile_locations,
        "commodities": commodities,
        "businesses": [business.to_dict() for business in world.businesses.values()],
        "event_templates": sorted(EVENT_TEMPLATES),
        "events": [e.to_dict() for e in world.active_events()],
    }


def api_market(world: World, params) -> Dict[str, Any]:
    progress_id = _progress_id(_one(params, "progress"))
    simple = _one(params, "simple", "") in {"1", "true", "yes", "on"}

    def progress(done: int, total: int, label: str) -> None:
        _set_progress(progress_id, done=done, total=total, label=label,
                      status="running")

    _set_progress(progress_id, done=0, total=0, label="Starting", status="running")
    warming = world.config.seasonal_inventory and _seasonal_warmup_running(world)
    try:
        with _simple_market_mode(world, simple or warming):
            report = market_report(
                _required(params, "settlement"),
                world=world,
                category=_one(params, "category"),
                sort="category",
                progress=progress if progress_id else None,
            )
    except Exception:
        _set_progress(progress_id, status="failed")
        raise
    if simple:
        report["simple_price_mode"] = True
    _set_progress(progress_id, done=len(report["prices"]), total=len(report["prices"]),
                  label="Complete", status="complete")
    return report


def api_progress(world: World, params) -> Dict[str, Any]:
    progress_id = _progress_id(_required(params, "id"))
    with _PROGRESS_LOCK:
        progress = dict(_PROGRESS.get(progress_id, {}))
    if not progress:
        return {"id": progress_id, "status": "unknown", "done": 0, "total": 0, "label": ""}
    return {"id": progress_id, **progress}


def api_population(world: World, params) -> Dict[str, Any]:
    settlement = world.find_settlement(_required(params, "settlement"))
    report = population_report(settlement)
    defaults = report["land_area"]["inputs"]
    if any(name in params for name in defaults):
        try:
            report["land_area"] = land_area_report(
                settlement, **{name: _float(params, name, value) for name, value in defaults.items()},
            )
        except ValueError as exc:
            raise ApiError(str(exc)) from exc
    return {"date": str(world.date), **report}


def api_census(world: World, params) -> Dict[str, Any]:
    settlement = world.find_settlement(_required(params, "settlement"))
    report = waterdeep_housing_report(settlement.id)
    return {
        "date": str(world.date),
        "active_resident_population": settlement.population,
        "active_population_unchanged": True,
        **report,
    }


def _api_map_survey(world: World, params, layer: str) -> Dict[str, Any]:
    settlement = world.find_settlement(_required(params, "settlement"))
    report = map_survey_report(
        layer, settlement.id, search=_one(params, "search", ""),
        offset=_int(params, "offset", 0),
        limit=_int(params, "limit", 100) if _one(params, "limit") is not None else None,
    )
    return {
        "date": str(world.date),
        "active_resident_population": settlement.population,
        "active_population_unchanged": True,
        **report,
    }


def api_streets(world: World, params) -> Dict[str, Any]:
    return _api_map_survey(world, params, "streets")


def api_hires_census(world: World, params) -> Dict[str, Any]:
    return _api_map_survey(world, params, "roofs")


def api_settlement_analysis(world: World, params) -> Dict[str, Any]:
    settlement = world.find_settlement(_required(params, "settlement"))
    return {
        "date": str(world.date),
        "active_population_unchanged": True,
        **settlement_analysis_report(settlement),
    }


def api_mobile_locations(world: World, params) -> Dict[str, Any]:
    return {
        "date": str(world.date),
        "mobile_locations": [
            mobile_location_summary(location, world)
            for location in sorted(
                world.mobile_locations.values(), key=lambda item: item.name
            )
        ],
    }


def api_mobile_location(world: World, params) -> Dict[str, Any]:
    key = _required(params, "id")
    try:
        location = world.find_mobile_location(key)
    except KeyError as exc:
        raise ApiError(str(exc)) from exc
    return location.profile(world)


def api_mobile_economy(world: World, params) -> Dict[str, Any]:
    key = _required(params, "id")
    try:
        location = world.find_mobile_location(key)
    except KeyError as exc:
        raise ApiError(str(exc)) from exc
    return mobile_economic_report(location, world)


def api_compare(world: World, params) -> Dict[str, Any]:
    return compare_prices(
        _required(params, "commodity"),
        world=world,
        region=_one(params, "region"),
        limit=_int(params, "limit", 25),
        cheapest_first=_one(params, "order", "cheap") != "dear",
    )


def api_product(world: World, params) -> Dict[str, Any]:
    commodity = world.find_commodity(_required(params, "commodity"))
    components = {
        component_id: {
            "name": world.commodities[component_id].name,
            "unit": world.commodities[component_id].unit,
            "base_price": world.commodities[component_id].base_price,
        }
        for component_id in commodity.bom
    }
    result = {
        "commodity": commodity.to_dict(),
        "components": components,
        "sourcing": commodity_sources(commodity.id, world=world, limit=50),
        "seasonal_inventory": bool(getattr(world.config, "seasonal_inventory", False)),
        "seasonality": {},
    }
    market = _one(params, "settlement")
    if market:
        from .seasonality import seasonal_profile
        settlement = world.find_settlement(market)
        result["settlement"] = settlement.name
        result["settlement_id"] = settlement.id
        result["seasonality"] = seasonal_profile(commodity, settlement, world.date)
        result["special_order"] = special_order_quote(settlement.id, commodity.id, world=world)
    return result


def api_generated_buildings(world: World, params) -> Dict[str, Any]:
    return generate_buildings(
        _one(params, "ward") or "Trades Ward",
        count=_int(params, "count", 20),
        seed=_int(params, "seed", 1357),
        building_class=_one(params, "building_class"),
        footprint_sqft=_float(params, "footprint_sqft", 1000),
        scenario=_one(params, "scenario") or "central",
    )


def api_location_profiles(world: World, params) -> Dict[str, Any]:
    return location_profiles()


def api_generated_location(world: World, params) -> Dict[str, Any]:
    return generate_location(
        _required(params, "location"),
        profile=_one(params, "profile") or "town",
        count=_int(params, "count", 20), seed=_int(params, "seed", 1357),
        footprint_sqft=_float(params, "footprint_sqft", 1000),
        scenario=_one(params, "scenario") or "central",
        class_b_weight=_int(params, "class_b_weight", 0) if _one(params, "class_b_weight") is not None else None,
        class_c_weight=_int(params, "class_c_weight", 0) if _one(params, "class_c_weight") is not None else None,
        class_d_weight=_int(params, "class_d_weight", 0) if _one(params, "class_d_weight") is not None else None,
        condition_modifier=_int(params, "condition_modifier", 0) if _one(params, "condition_modifier") is not None else None,
    )


def api_city_directory(world: World, params) -> Dict[str, Any]:
    return city_directory(
        _one(params, "settlement") or "Waterdeep",
        search=_one(params, "search") or "",
        ward=_one(params, "ward") or "",
        kind=_one(params, "kind") or "all",
        category=_one(params, "category") or "",
    )


def api_businesses(world: World, params) -> Dict[str, Any]:
    settlement = world.find_settlement(_required(params, "settlement"))
    quality_order = ("basic", "standard", "fine", "masterwork")
    businesses = []
    for business in world.businesses.values():
        if settlement.id not in business.locations:
            continue
        if not math.isfinite(business.price_modifier) or business.price_modifier <= 0:
            raise ValueError(f"Price modifier must be finite and positive for {business.name}")
        offers = []
        for commodity_id, ceiling in business.offers.items():
            if commodity_id not in world.commodities:
                continue
            quote = price_for(settlement, commodity_id, world=world)
            quote_data = quote.to_dict()
            for offer in quote_data["quality_offers"]:
                if (quality_order.index(offer["quality"]) > quality_order.index(ceiling)
                        or offer["stock"] <= 0):
                    continue
                ask = round(offer["price"] * business.price_modifier, 3)
                bid = round(offer["buy_price"] * business.price_modifier, 3)
                stock = max(1, int(round(offer["stock"] * 0.35)))
                eligible = sorted(
                    trader.id for trader in world.businesses.values()
                    if settlement.id in trader.locations and commodity_id in trader.offers
                    and quality_order.index(offer["quality"]) <= quality_order.index(trader.offers[commodity_id])
                )
                free, remainder = divmod(offer["uncommitted_stock"], len(eligible))
                free += eligible.index(business.id) < remainder
                offers.append({
                    **offer,
                    "commodity": commodity_id,
                    "commodity_name": quote.commodity_name,
                    "unit": quote.unit,
                    "price": ask,
                    "buy_price": bid,
                    **price_terms(ask, bid),
                    "stock": stock,
                    "uncommitted_stock": min(stock, free),
                    "uncommitted_basis": (
                        "Share of the common market's uncommitted grade stock after protected storage reserves; not a booking."
                        if (quote_data.get("inventory") or {}).get("enabled")
                        else "Share of the common market's uncommitted grade stock; a forecast, not a booking."
                    ),
                })
        data = business.to_dict()
        headquarters = world.settlements.get(business.headquarters)
        data["is_headquarters"] = settlement.id == business.headquarters
        data["headquarters_name"] = headquarters.name if headquarters else business.headquarters
        data["location_names"] = [
            world.settlements[location].name
            for location in business.locations if location in world.settlements
        ]
        data["offers"] = offers
        businesses.append(data)
    return {
        "settlement": settlement.name,
        "settlement_id": settlement.id,
        "businesses": businesses,
        "count": len(businesses),
    }


def api_business_detail(world: World, params) -> Dict[str, Any]:
    business_id = _required(params, "business")
    business = world.businesses.get(business_id)
    if business is None:
        matches = [b for b in world.businesses.values()
                   if b.name.casefold() == business_id.casefold()]
        business = matches[0] if matches else None
    if business is None:
        raise ApiError(f"unknown business: {business_id}")

    data = business.to_dict()
    data["headquarters_name"] = (
        world.settlements[business.headquarters].name
        if business.headquarters in world.settlements else business.headquarters
    )
    data["locations_detail"] = [
        {
            "id": location,
            "name": world.settlements[location].name,
            "inventory": business.inventory.get(location, {}),
            "address": business.location_addresses[location],
        }
        for location in business.locations if location in world.settlements
    ]
    settlement_value = _one(params, "settlement") or business.headquarters
    try:
        settlement = world.find_settlement(settlement_value).id
    except (KeyError, ValueError):
        settlement = business.headquarters
    market = api_businesses(world, {"settlement": [settlement]})
    data["market_settlement"] = market["settlement"]
    data["market_settlement_id"] = market["settlement_id"]
    data["offers"] = next(
        (entry["offers"] for entry in market["businesses"] if entry["id"] == business.id),
        [],
    )
    return {"business": data}


def api_carriers(world: World, params) -> Dict[str, Any]:
    carriers = []
    for business in world.businesses.values():
        if not business.carrier_service_id:
            continue
        carriers.append({
            "id": business.id,
            "service_id": business.carrier_service_id,
            "name": business.name,
            "headquarters": business.headquarters,
            "locations": list(business.locations),
            "modes": list(business.carrier_modes),
            "capacity_lb": business.capacity_lb,
            "capacity_ft3": business.capacity_ft3,
            "equipment": dict(business.transport_equipment),
            "employees": business.employee_total,
            "itinerary": list(business.itinerary),
        })
    return {"carriers": carriers, "count": len(carriers)}


def api_history(world: World, params) -> Dict[str, Any]:
    return price_history(
        _required(params, "settlement"),
        _required(params, "commodity"),
        world=world,
        months=max(2, min(_int(params, "months", 12), 48)),
    )


def api_trade(world: World, params) -> Dict[str, Any]:
    return trade_summary(
        _required(params, "settlement"), world=world, top=_int(params, "top", 10)
    )


def api_route(world: World, params) -> Dict[str, Any]:
    route_types = []
    for value in params.get("route_type", []):
        route_types.extend(part.strip() for part in value.split(",") if part.strip())
    return world.route(
        _required(params, "origin"),
        _required(params, "destination"),
        optimise=_one(params, "optimise", "days"),
        include_inferred=_one(params, "include_inferred", "1") in {"1", "true", "yes", "on"},
        route_types=route_types,
    )


def api_transport_plan(world: World, params) -> Dict[str, Any]:
    amounts = {key: _float(params, key, default) for key, default in (
        ("pounds", 100), ("minimum", 0), ("handling", 0), ("daily", 0), ("fixed", 0), ("contingency", 0))}
    if _one(params, "purchase_per_lb", "").strip():
        amounts["purchase_per_lb"] = _float(params, "purchase_per_lb", 0)
    purchase_basis = "manual" if "purchase_per_lb" in amounts else "not supplied"
    if "purchase_per_lb" not in amounts and _one(params, "cargo", "").strip():
        try:
            commodity = world.find_commodity(_one(params, "cargo"))
            origin = world.find_settlement(_required(params, "origin"))
            if commodity.weight > 0:
                quote = price_for(origin, commodity.id, world=world, quality="standard")
                amounts["purchase_per_lb"] = round(quote.price / commodity.weight, 6)
                purchase_basis = f"origin standard market price in {origin.name}"
        except (KeyError, ValueError, AttributeError, TypeError):
            pass
    flags = {}
    for key in ("include_inferred", "include_events", "allow_special", "prefer_land"):
        raw = _one(params, key, "0")
        if raw not in ("0", "1"):
            raise ApiError(f"{key} must be 0 or 1")
        flags[key] = raw == "1"
    route_types = [part.strip() for part in _one(params, "route_types", "").split(",") if part.strip()]
    freight_mode = _one(params, "freight_mode", "shared_freight")
    try:
        carrier_choices = json.loads(_one(params, "carrier_choices", "{}"))
        selected_leg_ids = json.loads(_one(params, "selected_legs", "[]"))
        result = plan_shipment(world, _required(params, "origin"), _required(params, "destination"),
                             **amounts, **flags, carrier_choices=carrier_choices,
                             selected_leg_ids=selected_leg_ids,
                             route_types=route_types, freight_mode=freight_mode)
        cargo_name = _one(params, "cargo", "").strip()
        if cargo_name:
            try:
                commodity = world.find_commodity(cargo_name)
                units = amounts["pounds"] / commodity.weight if commodity.weight > 0 else 0
                result["cargo_unit"] = commodity.unit
                result["cargo_weight_lb"] = amounts["pounds"]
                result["cargo_weight_per_unit_lb"] = commodity.weight
                result["cargo_units"] = units
                density_by_category = {
                    "metal": 450, "stone": 140, "material": 45, "food": 35,
                    "drink": 55, "textile": 12, "luxury": 18, "gem": 180,
                    "livestock": 45, "arms": 55, "product": 30, "arcane": 25,
                    "exotic": 20,
                }
                density = density_by_category.get(commodity.category, 30)
                volume_per_unit = commodity.weight / density
                result["cargo_volume_per_unit_ft3"] = round(volume_per_unit, 6)
                result["cargo_volume_ft3"] = round(units * volume_per_unit, 3)
                result["cargo_volume_basis"] = f"modeled {density:g} lb/ft3 density for {commodity.category} goods"
                if units > 0:
                    for option in result["options"]:
                        total = option["costs"].get("landed_total_gp")
                        option["costs"]["landed_gp_per_unit"] = None if total is None else total / units
            except (KeyError, ValueError, AttributeError, TypeError, ZeroDivisionError):
                pass
        result["purchase_price_basis"] = purchase_basis
        return result
    except (ValueError, KeyError) as error:
        raise ApiError(str(error)) from error


def api_supply_chain(world: World, params) -> Dict[str, Any]:
    destination = world.find_settlement(_required(params, "settlement"))
    root = world.find_commodity(_required(params, "commodity"))

    def trace(commodity, market, quantity, ancestors):
        quote = price_for(market.id, commodity.id, world=world)
        source = world.find_settlement(quote.source) if quote.source else market
        route = None if source.id == market.id else world.route(
            source.id, market.id, optimise="cost"
        )
        node = {
            "commodity": commodity.id,
            "name": commodity.name,
            "quantity": round(quantity, 6),
            "unit": commodity.unit,
            "production_type": commodity.production_type,
            "market": market.name,
            "source": source.name,
            "local": source.id == market.id,
            "route": route,
            "inputs": [],
        }
        if commodity.id in ancestors:
            return node
        next_ancestors = ancestors | {commodity.id}
        node["inputs"] = [
            trace(
                world.commodities[input_id],
                source,
                quantity * input_quantity,
                next_ancestors,
            )
            for input_id, input_quantity in commodity.bom.items()
        ]
        return node

    return {
        "settlement": destination.name,
        "settlement_id": destination.id,
        "commodity": root.id,
        "commodity_name": root.name,
        "chain": trace(root, destination, 1.0, set()),
    }


def api_arbitrage(world: World, params) -> Dict[str, Any]:
    return find_arbitrage(
        _required(params, "origin"),
        world=world,
        max_days=_float(params, "max_days", 45.0),
        cargo_pounds=_float(params, "cargo", 2000.0),
        category=_one(params, "category"),
        limit=_int(params, "limit", 20),
    )


def api_special_order(world: World, params) -> Dict[str, Any]:
    return special_order_quote(
        _required(params, "settlement"),
        _required(params, "commodity"),
        world=world,
        quantity=_int(params, "quantity", 1),
        quality=_one(params, "quality") or "standard",
        max_days=_float(params, "max_days", 90.0),
    )


def api_map_revision(world: World, params) -> Dict[str, Any]:
    from .locationedits import location_edits_path
    from .routegeometry import route_edits_path
    from .atlas import project_root

    paths = [location_edits_path(), route_edits_path(), project_root() / "maps" / "terrain-overrides.json",
             project_root() / "maps" / "terrain-1-mile.json",
             project_root() / "maps" / "high-forest-regions.json",
             project_root() / "maps" / "high-forest-source-boundaries.json",
             project_root() / "maps" / "goldenfields-regions.json"]
    versions = []
    for path in paths:
        info = path.stat() if path.exists() else None
        versions.append([info.st_mtime_ns, info.st_size] if info else None)
    return {"version": json.dumps(versions)}


def map_boundary_regions():
    from .atlas import project_root

    regions = []
    for name in ("high-forest-regions.json", "goldenfields-regions.json"):
        path = project_root() / "maps" / name
        if path.is_file():
            regions.extend(json.loads(path.read_text(encoding="utf-8"))["regions"])
    return regions


def map_source_boundaries():
    from .atlas import project_root

    path = project_root() / "maps" / "high-forest-source-boundaries.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def api_map(world: World, params) -> Dict[str, Any]:
    """Terrain heightfield, settlement pins and trade routes for the 3D map.

    The raster is built once and cached in `mapdata`, so only the first
    request pays for it.
    """
    return {**apply_location_edits(map_payload(world)), "sourceBoundaries": map_source_boundaries(), "boundaryRegions": map_boundary_regions(), "mapVersion": api_map_revision(world, {})["version"], "travelMilesPerDay": {
        kind: values[1] for kind, values in MODES.items() if kind != "teleport"
    }}


def api_planar_terrain(world: World, params) -> Dict[str, Any]:
    return planar_terrain_tile(int(_required(params, "column")), int(_required(params, "row")))


def api_terrain_detail(world: World, params) -> Dict[str, Any]:
    return terrain_detail(
        world,
        _required(params, "settlement"),
        radius=_float(params, "radius", 250.0),
    )


def api_timeline(world: World, params) -> Dict[str, Any]:
    """The basket price series and event history for one settlement.

    This walks every month in the chronicle window, so it is the most expensive
    endpoint here; the basket is deliberately small to keep it servable.
    """
    settlement = _required(params, "settlement")
    goods = params.get("commodity") or None
    size = _int(params, "size", 6)
    return location_timeline(settlement, world=world, commodities=goods,
                             size=max(1, min(12, size)))


def api_location(world: World, params) -> Dict[str, Any]:
    """One settlement's whole market at one month of the chronicle."""
    settlement = _required(params, "settlement")
    month = _int(params, "month", 0) or None
    category = _one(params, "category") or None
    return location_detail(settlement, world=world, month=month,
                           category=category)


def api_chronicle(world: World, params) -> Dict[str, Any]:
    """The shape of the world's history, and labels for the scrubber."""
    payload = chronicle_summary(world)
    payload["labels"] = month_labels()
    payload["today"] = world.date.absolute_month()
    return payload


def api_underlay(world: World, params) -> Dict[str, Any]:
    """Whether a user-supplied poster map is available to overlay.

    Takes `world` only to match the route signature - the answer depends on the
    filesystem, not on the economy. Looked up fresh on every call so dropping
    the image in place is picked up without restarting the server (unlike the
    page assets, which are frozen at import).
    """
    info = underlay_info(params.get("source", ["default"])[0])
    # If the poster has been surveyed we know exactly where it belongs in world
    # miles, so the browser can lay it down instead of asking for it to be
    # nudged into place by hand.
    from . import atlas as atlas_mod

    try:
        placement = atlas_mod.underlay_placement(list(world.settlements.values()))
    except Exception as exc:  # noqa: BLE001 - an overlay must never 500
        placement = {"available": False, "error": str(exc)}
    info["survey"] = placement
    return info


def api_calibration(world: World, params) -> Dict[str, Any]:
    """The saved control points, plus where each one started life.

    The browser needs the shipped position too: that is the point it has to
    drag *from*, and it is no longer readable off the settlement once a
    calibration has been applied.
    """
    settlements = list(world.settlements.values())
    base = base_coordinates(settlements)
    points = []
    for item in load_control_points():
        src = base.get(item["id"])
        if src is None:
            continue
        s = world.settlements[item["id"]]
        points.append({
            "id": item["id"],
            "name": s.name,
            "x": item["x"],
            "y": item["y"],
            "baseX": src[0],
            "baseY": src[1],
        })
    return {"points": points, "count": len(points)}


def api_atlas(world: World, params) -> Dict[str, Any]:
    """What a surveyed poster index would do to the map, without doing it.

    This is the preview behind the one-click realignment: it reports which
    markets the survey knows, how far each would travel, and which ones it has
    never heard of and would therefore be left where they are.
    """
    from . import atlas as atlas_mod

    def nothing(error: str) -> Dict[str, Any]:
        return {"available": False, "error": error,
                "searched": info.get("searched", []), "matched": [],
                "missing": [], "unused": [], "count": 0, "surveyed": 0,
                "anchor": "", "path": "",
                "terrain": {"landmarks": 0, "anchored": 0,
                            "rejected": [], "unsurveyed": []}}

    info = atlas_mod.atlas_info()
    if not info.get("available"):
        return nothing(info.get("error", ""))

    settlements = list(world.settlements.values())
    try:
        report = atlas_mod.align(settlements)
    except atlas_mod.AtlasError as exc:
        return nothing(str(exc))

    from .mapdata import terrain_alignment

    points = [{"id": m["id"], "x": m["x"], "y": m["y"]}
              for m in report["matched"]]
    terrain = terrain_alignment(settlements, points)
    # The raw feature index is hundreds of entries the browser has no use for;
    # what it wants is the count of scenery that would be pinned.
    report.pop("features", None)
    report["terrain"] = {
        "landmarks": terrain.get("landmarks", 0),
        "anchored": len(terrain.get("anchored", [])),
        "rejected": [r["name"] for r in terrain.get("rejected", [])],
        "unsurveyed": terrain.get("unsurveyed", []),
    }
    report["image"] = info.get("image", "")
    report["milesPerPixel"] = info.get("miles_per_pixel", 0.0)
    report["searched"] = info.get("searched", [])
    report["error"] = ""
    return report


GET_ROUTES: Dict[str, Callable[[World, Dict[str, list]], Dict[str, Any]]] = {
    "/api/lore-desk": read_desk,
    **GET_TRADE_ROUTES,
    **GET_BOARD_ROUTES,
    "/api/bootstrap": api_bootstrap,
    "/api/mobile-locations": api_mobile_locations,
    "/api/mobile-location": api_mobile_location,
    "/api/mobile-economy": api_mobile_economy,
    "/api/underlay": api_underlay,
    "/api/calibration": api_calibration,
    "/api/atlas": api_atlas,
    "/api/map": api_map,
    "/api/terrain-detail": api_terrain_detail,
    "/api/planar-terrain": api_planar_terrain,
    "/api/timeline": api_timeline,
    "/api/location": api_location,
    "/api/chronicle": api_chronicle,
    "/api/market": api_market,
    "/api/progress": api_progress,
    "/api/population": api_population,
    "/api/census": api_census,
    "/api/census/hires": api_hires_census,
    "/api/streets": api_streets,
    "/api/settlement-analysis": api_settlement_analysis,
    "/api/compare": api_compare,
    "/api/product": api_product,
    "/api/businesses": api_businesses,
    "/api/business": api_business_detail,
    "/api/carriers": api_carriers,
    "/api/city-directory": api_city_directory,
    "/api/generated-buildings": api_generated_buildings,
    "/api/location-profiles": api_location_profiles,
    "/api/generated-location": api_generated_location,
    "/api/history": api_history,
    "/api/trade": api_trade,
    "/api/route": api_route,
    "/api/transport-plan": api_transport_plan,
    "/api/supply-chain": api_supply_chain,
    "/api/arbitrage": api_arbitrage,
    "/api/special-order": api_special_order,
}


# ---------------------------------------------------------------------------
# Mutating handlers
# ---------------------------------------------------------------------------


def post_world(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    """Set the date, wobble seed and run mode."""
    date = world.date
    year = body.get("year")
    month = body.get("month")
    if year is not None or month is not None:
        # JSON numbers arrive as floats when the browser sends 6.0, and
        # parse_month only treats real ints as month numbers.
        if month is None:
            new_month = date.month
        elif isinstance(month, (int, float)):
            new_month = parse_month(int(month))
        else:
            new_month = parse_month(month)
        new_year = int(year) if year is not None else date.year
        world.set_date(HarptosDate(year=new_year, month=new_month, day=date.day))
    seed = body.get("seed")
    if seed is not None and int(seed) != world.config.seed:
        world.config.seed = int(seed)
        world.revision += 1
    seasonal = body.get("seasonal_inventory")
    if seasonal is not None:
        enabled = bool(seasonal)
        if enabled != world.config.seasonal_inventory:
            world.config.seasonal_inventory = enabled
            world.revision += 1
    payload = api_bootstrap(world, {})
    if world.config.seasonal_inventory:
        _start_seasonal_warmup(world)
    return payload


def post_event(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    template = str(body.get("template") or "").strip()
    if template not in EVENT_TEMPLATES:
        raise ApiError(
            f"unknown event template {template!r}; try one of: "
            f"{', '.join(sorted(EVENT_TEMPLATES))}"
        )
    kwargs: Dict[str, Any] = {"template": template, "world": world}
    description = str(body.get("description") or "").strip()
    if description:
        kwargs["description"] = description
    scope = str(body.get("scope") or "settlement").strip().lower()
    target = str(body.get("target") or "").strip()
    if not target:
        raise ApiError("an event needs a target settlement, region or zone")
    if scope == "region":
        kwargs["regions"] = [target]
    elif scope == "zone":
        kwargs["zones"] = [target]
    else:
        kwargs["settlements"] = [target]
    apply_event(**kwargs)
    return api_bootstrap(world, {})


def post_clear_events(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    event_id = body.get("id")
    if event_id:
        world.remove_event(str(event_id))
    else:
        world.clear_events()
    return api_bootstrap(world, {})


def post_atlas_apply(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    """Realign every market from the survey in one step."""
    from . import atlas as atlas_mod

    settlements = list(world.settlements.values())
    try:
        points = atlas_mod.control_points(settlements)
    except atlas_mod.AtlasError as exc:
        raise ApiError(str(exc))
    if not points:
        raise ApiError("no market names matched the survey, so there is "
                       "nothing to align to")

    save_control_points(points)
    used = apply_calibration(settlements, points)
    world.rebuild()
    payload = api_bootstrap(world, {})
    payload["calibration"] = {"count": used, "source": "atlas"}
    return payload


def post_calibrate(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    """Re-survey the gazetteer from a set of map control points.

    Sending an empty list clears the calibration and restores the shipped
    coordinates, so this is both the save and the reset path.
    """
    raw = body.get("points")
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        raise ApiError("calibration expects a list of control points")

    settlements = list(world.settlements.values())
    known = base_coordinates(settlements)
    clean = []
    for item in raw:
        if not isinstance(item, dict):
            raise ApiError("each control point must be an object")
        sid = str(item.get("id") or "").strip()
        if sid not in known:
            raise ApiError(f"unknown settlement {sid!r} in calibration")
        try:
            clean.append({"id": sid, "x": float(item["x"]), "y": float(item["y"])})
        except (KeyError, TypeError, ValueError):
            raise ApiError(f"control point for {sid!r} needs numeric x and y")

    save_control_points(clean)
    used = apply_calibration(settlements, clean)

    # Coordinates feed trade-route distances, so the graph and every cached
    # price derived from it are now wrong. Rebuilding the network is what makes
    # a calibration actually change the economy rather than just the picture.
    world.rebuild()
    payload = api_bootstrap(world, {})
    payload["calibration"] = {"count": used}
    return payload


def post_terrain_cell(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    """Persist one manual correction to the rendered world terrain grid."""
    try:
        column = int(body["column"])
        row = int(body["row"])
    except (KeyError, TypeError, ValueError):
        raise ApiError("terrain correction needs integer column and row")
    terrain = str(body.get("terrain") or "").strip()
    try:
        count = save_terrain_override(column, row, terrain)
    except (OSError, UnicodeError, ValueError, AtlasError) as exc:
        raise ApiError(str(exc)) from exc
    payload = api_map(world, {})
    payload["terrainOverrideCount"] = count
    return payload


def post_rebuild(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    """Reload commodities/settlements/businesses from disk into this server.

    Picks up anything added or edited through the MCP catalog tools since
    this process started, without a restart.
    """
    from .catalog import reload_from_disk

    counts = reload_from_disk()
    payload = api_bootstrap(world, {})
    payload["reloaded"] = counts
    return payload


def post_map_route_leg(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    try:
        result = save_route_leg(body)
        world.sync_route_edits()
        return result
    except (OSError, ValueError) as exc:
        raise ApiError(str(exc)) from exc


GET_ROUTES["/api/map-route-legs"] = lambda world, params: load_route_edits()
GET_ROUTES["/api/map-revision"] = api_map_revision


def post_map_junction(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    try:
        result = save_road_junction(body)
        world.sync_route_edits()
        return result
    except (OSError, ValueError) as exc:
        raise ApiError(str(exc)) from exc


def post_map_location(world: World, body: Dict[str, Any]) -> Dict[str, Any]:
    try:
        payload = map_payload(world)
        result = save_location_edit(body, {"settlements": payload["settlements"], "places": payload.get("places", [])})
        if world is not None:
            world.sync_route_edits()
        return result
    except (OSError, ValueError) as exc:
        raise ApiError(str(exc)) from exc


POST_ROUTES: Dict[str, Callable[[World, Dict[str, Any]], Dict[str, Any]]] = {
    "/api/lore-desk": post_desk,
    **POST_TRADE_ROUTES,
    **POST_BOARD_ROUTES,
    "/api/world": post_world,
    "/api/calibrate": post_calibrate,
    "/api/terrain-cell": post_terrain_cell,
    "/api/map-route-leg": post_map_route_leg,
    "/api/map-junction": post_map_junction,
    "/api/map-location": post_map_location,
    "/api/atlas/apply": post_atlas_apply,
    "/api/event": post_event,
    "/api/events/clear": post_clear_events,
    "/api/rebuild": post_rebuild,
}

UNLOCKED_GET_ROUTES = {"/api/bootstrap", "/api/progress", "/api/map", "/api/underlay", "/api/map-route-legs"}


# ---------------------------------------------------------------------------
# HTTP plumbing
# ---------------------------------------------------------------------------


class Handler(BaseHTTPRequestHandler):
    server_version = "FaerunMarket/0.1"

    def log_message(self, fmt: str, *args) -> None:  # quieter console
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    # -- responses ----------------------------------------------------------
    def _send_json(self, payload: Any, status: int = 200) -> None:
        raw = json.dumps(_finite(payload), ensure_ascii=False,
                         allow_nan=False).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)
        except CONNECTION_LOST:
            return

    def _send_bytes(self, raw: bytes, content_type: str, status: int = 200) -> None:
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)
        except CONNECTION_LOST:
            return

    def _send_error(self, exc: BaseException) -> None:
        """Turn an unexpected exception into a readable 500.

        Without this the exception escapes `do_GET`, the socket is closed with
        no response at all, and the browser reports a JSON parse failure - which
        hides the actual bug. Printing the traceback here means the terminal
        running the server always shows the real cause.
        """
        traceback.print_exc()
        try:
            self._send_json(
                {"error": f"{type(exc).__name__}: {exc}",
                 "traceback": traceback.format_exc().splitlines()[-12:]},
                500,
            )
        except CONNECTION_LOST:
            pass

    def _send_static(self, path: str) -> None:
        name = path.lstrip("/") or "index.html"
        binary = BINARY_STATIC.get(name)
        if binary is not None:
            image_path, content_type = binary
            try:
                self._send_bytes(image_path.read_bytes(), content_type)
            except OSError as exc:
                self._send_bytes(
                    f"Waterdeep map image is unavailable: {exc}".encode("utf-8"),
                    "text/plain; charset=utf-8",
                    404,
                )
            return
        asset = STATIC.get(name)
        if asset is None:
            # The page set is baked into STATIC when this module is imported,
            # so a long-running server started before a page existed will miss
            # it forever. Say so, rather than a bare "not found" that reads
            # like the page is broken.
            pages = "".join(
                f'<li><a href="/{n}">{n}</a></li>'
                for n in sorted(STATIC) if n.endswith(".html")
            )
            body = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                "<title>Not found</title></head><body "
                "style='font:15px/1.6 system-ui,sans-serif;margin:3rem auto;"
                "max-width:34rem;color:#111'>"
                f"<h1>No page called <code>{html.escape(name)}</code></h1>"
                "<p>This server is serving these pages:</p>"
                f"<ul>{pages}</ul>"
                "<p>If you expected the page you asked for, this server was "
                "started before that page existed. Close the server window and "
                "run <code>run.ps1</code> again.</p>"
                "</body></html>"
            )
            self._send_bytes(body.encode("utf-8"), "text/html; charset=utf-8", 404)
            return
        body, ctype = asset
        self._send_bytes(body.encode("utf-8"), ctype)

    def _send_underlay(self, source: str = "default") -> None:
        """Stream the user's own poster map straight off their disk.

        Nothing is copied into the project and nothing is redistributed: the
        bytes are read from wherever the file already lives and handed to the
        one browser that asked for them.
        """
        found = underlay_bytes(source)
        if found is None:
            self._send_json(
            {"error": "no underlay image found", **underlay_info(source)}, 404
            )
            return
        self._send_bytes(found["raw"], found["mime"])

    # -- verbs --------------------------------------------------------------
    def _discard_rejected_trade_body(self):
        # Drain bounded rejected bodies so Windows can deliver the error before
        # closing the socket, rather than resetting an unread connection.
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return
        if 0 < length <= 65536:
            self.connection.settimeout(0.1)
            try:
                self.rfile.read(length)
            except (*CONNECTION_LOST, TimeoutError):
                return

    def _guard_trade_request(self, mutation=False):
        client_ip = ipaddress.ip_address(self.client_address[0])
        if not (client_ip.is_loopback or client_ip.is_private):
            raise ApiError("Trade records are accessible only from this machine or your local network", 403)
        host = urlparse("http://" + (self.headers.get("Host") or ""))
        if host.username or host.password or host.path or host.query or host.fragment or (
                host.port or 80) != self.server.server_address[1]:
            raise ApiError("Trade requests require the local server address", 403)
        if host.hostname not in ("localhost", "127.0.0.1", "::1"):
            try:
                host_ip = ipaddress.ip_address(host.hostname)
            except (ValueError, TypeError):
                raise ApiError("Trade requests require the local server address", 403)
            if not (host_ip.is_loopback or host_ip.is_private):
                raise ApiError("Trade requests require the local server address", 403)
        origin = self.headers.get("Origin")
        if origin is not None and origin != f"http://{host.netloc}":
            raise ApiError("Cross-origin trade requests are not allowed", 403)
        if mutation:
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                raise ApiError("Trade mutations require application/json", 415)
            if self.headers.get("Transfer-Encoding") or len(self.headers.get_all("Content-Length", [])) != 1:
                raise ApiError("Provide one Content-Length for the JSON request")
            try:
                length = int(self.headers["Content-Length"])
            except ValueError as exc:
                raise ApiError("Invalid Content-Length") from exc
            if not 0 < length <= 65536:
                raise ApiError("Trade JSON body must contain 1 to 65,536 bytes", 413)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        if parsed.path == "/underlay.img":
            try:
                self._send_underlay(parse_qs(parsed.query).get("source", ["default"])[0])
            except CONNECTION_LOST:
                pass
            except Exception as exc:  # noqa: BLE001 - deliberate catch-all
                self._send_error(exc)
            return
        route = GET_ROUTES.get(parsed.path)
        if route is None:
            self._send_static(parsed.path)
            return
        params = parse_qs(parsed.query)
        try:
            if parsed.path in GET_TRADE_ROUTES or parsed.path in GET_BOARD_ROUTES or parsed.path == "/api/lore-desk":
                self._guard_trade_request()
            if parsed.path in UNLOCKED_GET_ROUTES:
                payload = route(get_world(), params)
            else:
                with _LOCK:
                    payload = route(get_world(), params)
        except (ApiError, TradeError) as exc:
            self._send_json({"error": str(exc)}, exc.status)
        except KeyError as exc:
            self._send_json({"error": f"not found: {exc}"}, 404)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, 400)
        except CONNECTION_LOST:
            return
        except Exception as exc:  # noqa: BLE001 - deliberate catch-all
            self._send_error(exc)
        else:
            self._send_json(payload)

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        parsed = urlparse(self.path)
        route = POST_ROUTES.get(parsed.path)
        if route is None:
            self._send_json({"error": "no such endpoint"}, 404)
            return
        if (parsed.path in POST_TRADE_ROUTES or parsed.path in POST_BOARD_ROUTES
                or parsed.path in {"/api/map-route-leg", "/api/map-junction", "/api/map-location", "/api/lore-desk"}):
            try:
                self._guard_trade_request(mutation=True)
            except (ApiError, ValueError) as exc:
                self.close_connection = True
                self._send_json({"error": str(exc)}, exc.status if isinstance(exc, ApiError) else 400)
                self._discard_rejected_trade_body()
                return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
            if not isinstance(body, dict):
                raise ApiError("request body must be a JSON object")
            with _LOCK:
                payload = route(get_world(), body)
        except json.JSONDecodeError:
            self._send_json({"error": "request body was not valid JSON"}, 400)
        except (ApiError, TradeError) as exc:
            self._send_json({"error": str(exc)}, exc.status)
        except KeyError as exc:
            self._send_json({"error": f"not found: {exc}"}, 404)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, 400)
        except CONNECTION_LOST:
            return
        except Exception as exc:  # noqa: BLE001 - deliberate catch-all
            self._send_error(exc)
        else:
            self._send_json(payload)


def serve(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True,
          verbose: bool = False, page: str = "") -> None:
    from .orders import TradeStore, default_ledger_path
    world = get_world()
    if world.trade_store is None:
        world.trade_store = TradeStore(default_ledger_path())
    try:
        httpd = ThreadingHTTPServer((host, port), Handler)
    except OSError as exc:
        # Almost always an older copy of this server still holding the port.
        # That copy serves whatever pages existed when *it* started, which is
        # the usual reason a newly added page appears to be missing.
        print(f"Could not listen on {host}:{port} - {exc}")
        print("Something is already using that port, most likely an older copy")
        print("of this server. Close that window (Ctrl+C in it), or start this")
        print(f"one on a free port with:  run.ps1 -Port {port + 1}")
        raise SystemExit(1) from None
    httpd.verbose = verbose  # type: ignore[attr-defined]
    actual = httpd.server_address[1]
    # 0.0.0.0 is a bind address, not something a browser can open.
    shown = "127.0.0.1" if host in ("", "0.0.0.0", "::") else host
    url = f"http://{shown}:{actual}"
    print(f"Faerun market board serving at {url}")
    print(f"  commodity board  {url}/")
    print(f"  3D world map     {url}/map.html")
    print(f"  location history {url}/location.html")
    print(f"  merchant guild   {url}/trade.html")
    print(f"  request board    {url}/board.html")
    info = underlay_info()
    if info["available"]:
        print(f"  poster overlay   {info['name']}  ({info['path']})")
    else:
        print("  poster overlay   none found - drop a Faerun map image named")
        print(f"                   underlay.jpg in {info['searched'][0]}")
    if world.config.seasonal_inventory:
        print("Warming seasonal prices in the background; standard quotes remain available.")
        _start_seasonal_warmup(world)
    else:
        print("Standard prices are generated on demand; seasonal inventory is opt-in.")
    if open_browser:
        target = url + "/" + (page or "").lstrip("/")
        threading.Timer(0.5, lambda: webbrowser.open(target)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        httpd.server_close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="faerun-web",
        description="Browse Faerun commodity prices in a web UI.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765,
                        help="port to listen on (0 picks a free one)")
    parser.add_argument("--no-browser", action="store_true",
                        help="do not open a browser window")
    parser.add_argument("--verbose", action="store_true",
                        help="log every request")
    parser.add_argument("--map", action="store_true",
                        help="open the 3D world map instead of the board")
    parser.add_argument("--underlay", default="", metavar="PATH",
                        help="your own copy of a Faerun poster map to overlay "
                             "on the 3D world map (jpg/png/webp)")
    args = parser.parse_args(argv)
    if args.underlay:
        set_override(args.underlay)
    serve(args.host, args.port, not args.no_browser, args.verbose,
          "map.html" if args.map else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
