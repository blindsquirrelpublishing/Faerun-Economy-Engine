"""MCP server exposing the Faerûn market engine over stdio.

Run it directly::

    python -m faerun.mcp_server

or wire it into an MCP client (Claude Desktop, VS Code, Copilot CLI)::

    {
      "mcpServers": {
        "faerun": {
          "command": "python",
          "args": ["-m", "faerun.mcp_server"]
        }
      }
    }
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .calendar import HarptosDate, MONTHS, parse_month
from .city import city_directory
from .buildinggen import generate_buildings as _generate_buildings
from .locationgen import generate_location as _generate_location, location_profiles as _location_profiles
from .economy import (
    commodity_sources as _commodity_sources,
    compare_prices as _compare_prices,
    find_arbitrage as _find_arbitrage,
    market_report as _market_report,
    price_for as _price_for,
    price_history as _price_history,
    sourcing_catalog as _sourcing_catalog,
    trade_summary as _trade_summary,
)
from .events import EVENT_TEMPLATES, make_event
from .population import population_report as _population_report
from .census import waterdeep_housing_report as _housing_report
from .mapsurvey import map_survey_report as _map_survey_report
from .settlement_analysis import settlement_analysis_report as _settlement_analysis_report
from .world import (
    MODES,
    MULTIMODAL_COST,
    MULTIMODAL_DELAY,
    MULTIMODAL_RISK,
    World,
    describe_modes,
    get_world,
    parse_modes,
)

mcp = FastMCP(
    "faerun-market",
    instructions=(
        "Commodity and product prices for every town and city in Faerûn. "
        "Prices are simulated from local industry, terrain, population, "
        "wealth, tariffs, trade-route distance, season and active world "
        "events, so the same good costs different amounts in different "
        "markets. Settlement and commodity arguments accept names, partial "
        "names or ids ('Waterdeep', 'bryn shander', 'mithral_ingot'). "
        "Prices are in gold pieces (gp) per unit."
    ),
)


def world() -> World:
    return get_world()


def _fail(exc: Exception) -> Dict[str, Any]:
    return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------


@mcp.tool()
def generate_city_buildings(
    ward: str = "Trades Ward", count: int = 20, seed: int = 1357,
    building_class: Optional[str] = None, footprint_sqft: float = 1000,
    scenario: str = "central",
) -> Dict[str, Any]:
    """Generate 1-100 repeatable Waterdeep building scenarios from City System.

    Counts only: no invented named people or lore affiliations. Source rules
    supply B/C/D class, stories, condition and use; occupant counts and the
    entered footprint are assumptions, not surveyed or canonical facts.
    Southern Ward rolls 3-4 remain unresolved unless a class is chosen.
    Class A institutions/City of the Dead require individual authoring.
    Never changes the census, active population, directory, prices or stock.
    """
    try:
        return _generate_buildings(
            ward, count=count, seed=seed, building_class=building_class,
            footprint_sqft=footprint_sqft, scenario=scenario,
        )
    except ValueError as exc:
        return _fail(exc)


@mcp.tool()
def get_location_generation_profiles() -> Dict[str, Any]:
    """List assumed village/town/city/port/fortress class mixes and modifiers."""
    return _location_profiles()


@mcp.tool()
def generate_location(
    location: str, profile: str = "town", count: int = 20, seed: int = 1357,
    footprint_sqft: float = 1000, scenario: str = "central",
    class_b_weight: Optional[int] = None, class_c_weight: Optional[int] = None,
    class_d_weight: Optional[int] = None, condition_modifier: Optional[int] = None,
) -> Dict[str, Any]:
    """Generate 1-100 repeatable building scenarios for ANY supplied place name.

    Profiles adapt City System urban rules using explicit assumed class mixes.
    Optional B/C/D integer percentages must all be supplied and sum to 100.
    Condition modifier is -1, 0 or 1. Footprint and occupants are assumptions.
    Counts only: no invented named people, inferred lore, map coordinates or
    population fitting. Fortress profiles exclude unique keeps and garrisons.
    Never creates a world location or changes population, markets or the survey.
    Returned parameters reproduce the scenario; export the result to retain it.
    """
    try:
        return _generate_location(
            location, profile=profile, count=count, seed=seed,
            footprint_sqft=footprint_sqft, scenario=scenario,
            class_b_weight=class_b_weight, class_c_weight=class_c_weight,
            class_d_weight=class_d_weight, condition_modifier=condition_modifier,
        )
    except ValueError as exc:
        return _fail(exc)


@mcp.tool()
def get_city_directory(
    settlement: str = "Waterdeep", search: str = "", ward: str = "",
    kind: str = "all", category: str = "",
) -> Dict[str, Any]:
    """Historical businesses and named people with Volo PDF page citations.

    Separate from live 1492 DR markets. Currently covers a curated Waterdeep
    selection only. kind: all, business, person. Ward/category accept names or
    underscore IDs. Search includes directly affiliated names and roles.
    """
    try:
        return city_directory(settlement, search=search, ward=ward,
                              kind=kind, category=category)
    except (KeyError, ValueError) as exc:
        return _fail(exc)


@mcp.tool()
def list_settlements(region: Optional[str] = None,
                     search: Optional[str] = None,
                     min_population: int = 0,
                     limit: int = 250,
                     verbose: bool = False) -> Dict[str, Any]:
    """List markets in the Realms, optionally filtered by region or name.

    Args:
        region: match against region or zone, e.g. "Sword Coast", "Amn".
        search: substring of the settlement name.
        min_population: only settlements at least this large.
        limit: maximum rows returned.
        verbose: include full settlement records (industries, traits, ...).
    """
    rows: List[Dict[str, Any]] = []
    for s in sorted(world().settlements.values(),
                    key=lambda x: (x.region, -x.population)):
        if region and region.lower() not in f"{s.region} {s.zone}".lower():
            continue
        if search and search.lower() not in s.name.lower():
            continue
        if s.population < min_population:
            continue
        if verbose:
            rows.append(s.to_dict())
        else:
            rows.append({
                "id": s.id, "name": s.name, "region": s.region,
                "zone": s.zone, "size": s.size, "population": s.population,
                "wealth": s.wealth, "tariff": s.tax, "terrain": s.terrain,
                "port": s.port, "underdark": s.underdark,
                "traits": s.traits,
            })
    return {"count": len(rows), "settlements": rows[:limit]}


@mcp.tool()
def get_settlement(settlement: str) -> Dict[str, Any]:
    """Full record for one market: industries, specialties, shortages, traits."""
    try:
        s = world().find_settlement(settlement)
    except KeyError as exc:
        return _fail(exc)
    data = s.to_dict()
    data["neighbours"] = [
        {"to": world().route_node(e.dst).name, "mode": e.kind,
         "modes": list(e.modes), "mode_label": describe_modes(e.kind),
         "multimodal": e.multimodal,
         "miles": round(e.distance, 1), "days": round(e.days, 1),
         "via": e.name or "local track"}
        for e in world().edges_from(s.id)
    ]
    return data


@mcp.tool()
def list_commodities(category: Optional[str] = None,
                     search: Optional[str] = None,
                     verbose: bool = False) -> Dict[str, Any]:
    """List tradeable goods. Categories include food, metal, cloth, arms,
    tool, luxury, gem, arcane, drink, livestock, exotic and more."""
    rows: List[Dict[str, Any]] = []
    for c in world().commodities.values():
        if category and c.category != category:
            continue
        if search and search.lower() not in f"{c.id} {c.name}".lower():
            continue
        rows.append(c.to_dict() if verbose else {
            "id": c.id, "name": c.name, "category": c.category,
            "base_price": c.base_price, "unit": c.unit, "weight_lb": c.weight,
            "produced_by": c.produced_by,
        })
    return {
        "count": len(rows),
        "categories": sorted({c.category for c in world().commodities.values()}),
        "commodities": rows,
    }


@mcp.tool()
def get_commodity(commodity: str) -> Dict[str, Any]:
    """Full record for one good, including who can produce it and its
    seasonal and cultural demand modifiers."""
    try:
        return world().find_commodity(commodity).to_dict()
    except KeyError as exc:
        return _fail(exc)


@mcp.tool()
def list_commodity_sources(category: Optional[str] = None,
                           search: Optional[str] = None,
                           limit: int = 200,
                           source_limit: int = 12) -> Dict[str, Any]:
    """List commodities and where they originate.

    Each good is classified as widespread, restricted, extractive, or
    specialized. Results identify producing regions, active exporters, and
    locations with notable or renowned quality based on local specialties
    and established craft industries.

    Args:
        category: restrict to one commodity category, such as food or metal.
        search: substring of the commodity name or id.
        limit: maximum commodities returned.
        source_limit: maximum leading source locations returned per commodity.
    """
    return _sourcing_catalog(
        world=world(), category=category, search=search,
        limit=max(0, min(limit, 500)),
        source_limit=max(0, min(source_limit, 100)),
    )


@mcp.tool()
def get_commodity_sources(commodity: str, limit: int = 30) -> Dict[str, Any]:
    """Source regions, producers, exporters, and quality centers for one good."""
    try:
        return _commodity_sources(commodity, world=world(),
                                  limit=max(0, min(limit, 250)))
    except KeyError as exc:
        return _fail(exc)


@mcp.tool()
def list_regions() -> Dict[str, Any]:
    """Regions of the Realms covered by the engine, with market counts."""
    out = []
    for region in world().regions:
        members = [s for s in world().settlements.values() if s.region == region]
        out.append({
            "region": region,
            "markets": len(members),
            "population": sum(s.population for s in members),
            "settlements": sorted(s.name for s in members),
        })
    return {"count": len(out), "regions": out}


# ---------------------------------------------------------------------------
# Prices
# ---------------------------------------------------------------------------


@mcp.tool()
def get_price(settlement: str, commodity: str, quantity: int = 1,
              quality: str = "standard") -> Dict[str, Any]:
    """Price one good in one market.

    Returns the asking price, the local merchant's buy-back bid, the
    multiplier against the book price, availability, the tenday stock, and
    the factors (supply, demand, freight, tariff, season, events) behind it.
    Quality may be basic, standard, fine, or masterwork. Large quantities
    move the market.
    """
    try:
        quote = _price_for(
            settlement, commodity, world=world(), quantity=quantity, quality=quality
        )
    except (KeyError, ValueError) as exc:
        return _fail(exc)
    data = quote.to_dict()
    data["quantity"] = quantity
    data["total_price"] = round(quote.price * max(1, quantity), 2)
    data["date"] = str(world().date)
    data["season"] = world().date.season
    return data


@mcp.tool()
def refresh_price_snapshot(mode: str = "both") -> Dict[str, Any]:
    """Recompute and persist the full settlement x commodity price grid.

    `mode` is "standard", "seasonal" or "both" (default). Precomputing lets
    fast readers (get_cached_price, the web app) skip live recalculation;
    call this again after adding/editing commodities, settlements, routes or
    events, or whenever the date moves on and you want the cache to catch up.
    Rebuilding the whole gazetteer takes tens of seconds per mode; seasonal
    mode costs more because it replays daily inventory.
    """
    from .price_snapshot import refresh_price_snapshot as _refresh

    try:
        return _refresh(mode, world=world())
    except ValueError as exc:
        return _fail(exc)


@mcp.tool()
def get_price_snapshot_status() -> Dict[str, Any]:
    """Whether standard/seasonal price snapshots exist and are current.

    `stale: true` means the world has changed (catalog edit, date, event...)
    since that snapshot was last built with refresh_price_snapshot.
    """
    from .price_snapshot import price_snapshot_status

    return price_snapshot_status(world())


@mcp.tool()
def reload_catalog() -> Dict[str, Any]:
    """Reload commodities, settlements and businesses into this MCP server.

    Only useful if something else (another process, or a hand-edited JSON
    file under faerun/data/store/) changed the catalog since this server
    started; catalog tools in this same process already update its world
    immediately. Named routes and sea lanes need no action here since
    add_trade_route/add_sea_lane already keep every process in sync.
    """
    from .catalog import reload_from_disk

    try:
        return {"reloaded": reload_from_disk()}
    except Exception as exc:  # noqa: BLE001 - surfaced to the caller, not raised
        return _fail(exc)


@mcp.tool()
def restart_market_server(host: str = "127.0.0.1", port: int = 8883,
                          seasonal_inventory: bool = True,
                          category: str = "") -> Dict[str, Any]:
    """Restart the standalone market-board web dashboard so it picks up recent changes.

    The dashboard (`faerun.cli ... serve`) runs as its own long-lived process
    with its own copy of the world, so adding or editing commodities,
    settlements, businesses or routes through this MCP server does not
    reach an already-running dashboard. Call this after such a change (or
    whenever the browser looks stale) to stop the old server, if this tool
    started it, and launch a fresh one that reads the current catalog.
    `category` optionally opens the location page filtered to one category.
    """
    from .market_server import restart_market_server as _restart

    try:
        return _restart(host=host, port=port,
                        seasonal_inventory=seasonal_inventory, category=category)
    except OSError as exc:
        return _fail(exc)


@mcp.tool()
def get_cached_price(settlement: str, commodity: str, mode: str = "standard") -> Dict[str, Any]:
    """A previously precomputed quote, without recalculating it live.

    Returns an error if no snapshot has been built yet (see
    refresh_price_snapshot) or if the settlement/commodity is unknown.
    """
    from .price_snapshot import get_cached_price as _get_cached

    w = world()
    try:
        s = w.find_settlement(settlement)
        c = w.find_commodity(commodity)
    except KeyError as exc:
        return _fail(exc)
    cached = _get_cached(s.id, c.id, mode)
    if cached is None:
        return _fail(ValueError(
            f"no cached {mode} price for {s.name}/{c.name}; call refresh_price_snapshot first"
        ))
    return cached


@mcp.tool()
def get_population_report(settlement: str) -> Dict[str, Any]:
    """Resident scenario, comparison baseline and sources; not a census.

    Separates the city from territorial totals and unknown external visitors.
    Does not calculate prices or simulate historical population growth.
    """
    current = world()
    try:
        report = _population_report(current.find_settlement(settlement))
    except (KeyError, ValueError) as exc:
        return _fail(exc)
    return {"date": str(current.date), **report}


@mcp.tool()
def get_housing_census(settlement: str = "Waterdeep") -> Dict[str, Any]:
    """Audited building evidence, occupancy scenarios, and explicit census blockers.

    Read-only. Incomplete/uncalibrated map surveys do not produce city totals or
    change the active population. No PDF or image dependencies are used at runtime.
    """
    current = world()
    try:
        market = current.find_settlement(settlement)
        report = _housing_report(market.id)
    except (KeyError, ValueError, OSError) as exc:
        return _fail(exc)
    return {
        "date": str(current.date), "active_resident_population": market.population,
        "active_population_unchanged": True, **report,
    }


@mcp.tool()
def get_city_map_survey(
    layer: str = "streets", settlement: str = "Waterdeep", search: str = "",
    offset: int = 0, limit: int = 100, include_features: bool = False,
) -> Dict[str, Any]:
    """Street or roof map evidence, coverage and uncertainty; not a resident census.

    Use layer='streets' or 'roofs'. Metadata is returned by default. Set
    include_features=True for original-image pixel geometry, paged with offset
    and limit. Search matches a name or stable feature ID. Unknown names and
    unreviewed candidates are not promoted to verified streets or buildings.
    """
    current = world()
    try:
        market = current.find_settlement(settlement)
        report = _map_survey_report(
            layer, market.id, search=search, offset=offset, limit=limit,
            include_features=include_features,
        )
    except (KeyError, ValueError, OSError) as exc:
        return _fail(exc)
    return {
        "date": str(current.date), "active_resident_population": market.population,
        "active_population_unchanged": True, **report,
    }


@mcp.tool()
def get_settlement_analysis(settlement: str = "Daggerford") -> Dict[str, Any]:
    """Daggerford population evidence, indexed roof groups and named street traces.

    Includes source dates, scope, map-scale ambiguity and illustrative occupancy
    components. Read-only: never replaces the active resident population.
    """
    current = world()
    try:
        market = current.find_settlement(settlement)
        report = _settlement_analysis_report(market)
    except (KeyError, ValueError, OSError) as exc:
        return _fail(exc)
    return {"date": str(current.date), "active_population_unchanged": True, **report}


@mcp.tool()
def get_market_report(settlement: str, category: Optional[str] = None,
                      sort: str = "category", limit: int = 200) -> Dict[str, Any]:
    """Every price on offer in one settlement, plus what is cheap and dear there.

    Args:
        settlement: market name or id.
        category: restrict to one commodity category.
        sort: "category", "price" or "multiplier".
        limit: maximum price rows returned.
    """
    if sort not in ("category", "price", "multiplier"):
        sort = "category"
    try:
        report = _market_report(settlement, world=world(), category=category,
                                sort=sort)
    except KeyError as exc:
        return _fail(exc)
    report["price_count"] = len(report["prices"])
    report["prices"] = report["prices"][:limit]
    return report


@mcp.tool()
def compare_prices(commodity: str, region: Optional[str] = None,
                   settlements: Optional[List[str]] = None,
                   limit: int = 20,
                   cheapest_first: bool = True) -> Dict[str, Any]:
    """Compare one good across many markets: where it is cheap, where it is dear."""
    try:
        return _compare_prices(commodity, world=world(), settlements=settlements,
                               region=region, limit=limit,
                               cheapest_first=cheapest_first)
    except KeyError as exc:
        return _fail(exc)


@mcp.tool()
def get_price_history(settlement: str, commodity: str,
                      months: int = 12) -> Dict[str, Any]:
    """Roll the Calendar of Harptos forward and report the price each month."""
    try:
        return _price_history(settlement, commodity, world=world(),
                              months=max(1, min(months, 60)))
    except KeyError as exc:
        return _fail(exc)


@mcp.tool()
def get_trade_summary(settlement: str, top: int = 10) -> Dict[str, Any]:
    """What a market exports cheaply and what it pays dearly to import."""
    try:
        return _trade_summary(settlement, world=world(), top=top)
    except KeyError as exc:
        return _fail(exc)


# ---------------------------------------------------------------------------
# Trade and travel
# ---------------------------------------------------------------------------


@mcp.tool()
def get_trade_route(origin: str, destination: str,
                    optimise: str = "days") -> Dict[str, Any]:
    """Best trade road, river or sea lane between two markets.

    Args:
        optimise: "days" for the fastest route, "cost" for the cheapest freight.
    """
    try:
        return world().route(origin, destination,
                             optimise="cost" if optimise == "cost" else "days")
    except KeyError as exc:
        return _fail(exc)


@mcp.tool()
def find_arbitrage(origin: str, max_days: float = 45.0,
                   cargo_pounds: float = 2000.0,
                   category: Optional[str] = None,
                   destinations: Optional[List[str]] = None,
                   limit: int = 15) -> Dict[str, Any]:
    """Profitable cargoes to carry out of a market.

    Buys at the origin's asking price, pays freight, risk and spoilage, and
    sells at the destination merchant's bid. Results are ranked by gp per
    day of travel.
    """
    try:
        return _find_arbitrage(origin, world=world(), destinations=destinations,
                               max_days=max_days, cargo_pounds=cargo_pounds,
                               category=category, limit=limit)
    except KeyError as exc:
        return _fail(exc)


@mcp.tool()
def list_named_routes() -> Dict[str, Any]:
    """The great named trade roads and sea lanes of the Realms."""
    w = world()
    routes = []
    for name, stops, quality, kind in w.named_routes:
        routes.append({
            "name": name,
            "mode": kind,
            "modes": list(parse_modes(kind)),
            "mode_label": describe_modes(kind),
            "multimodal": len(parse_modes(kind)) > 1,
            "quality": quality,
            "stops": [w.route_node(sid).name if sid in getattr(w, "route_nodes", w.settlements) else sid
                      for sid in stops],
        })
    return {"count": len(routes), "routes": routes}


@mcp.tool()
def list_travel_modes() -> Dict[str, Any]:
    """Every way freight moves in the Realms, with its cost, pace and danger.

    A route may combine modes (spelled `river+portage`), which means the cargo
    must change carrier along the way: such a leg pays a transhipment
    surcharge, loses time to handling, and inherits risk from every mode.
    """
    return {
        "count": len(MODES),
        "modes": [
            {
                "mode": name,
                "label": describe_modes(name),
                "freight_factor": freight,
                "speed_miles_per_day": speed,
                "hazard_factor": hazard,
            }
            for name, (freight, speed, hazard) in MODES.items()
        ],
        "multimodal": {
            "syntax": "join modes with '+', most prominent first",
            "cost_surcharge_per_extra_mode": MULTIMODAL_COST,
            "speed_penalty_per_extra_mode": MULTIMODAL_DELAY,
            "risk_carried_from_each_extra_mode": MULTIMODAL_RISK,
        },
    }


# ---------------------------------------------------------------------------
# World state: date, seed and events
# ---------------------------------------------------------------------------


@mcp.tool()
def get_map_alignment(apply: bool = False) -> Dict[str, Any]:
    """Check - or perform - the realignment of every market to a poster map.

    If a surveyed index of a published map is present (maps/locations.json),
    this reports where each market would move to and which ones the survey has
    never heard of.  Pass apply=True to commit it, which moves the markets,
    rebuilds every caravan route, and therefore changes prices everywhere,
    because freight distance is a cost.
    """
    from . import atlas as atlas_mod
    from .calibration import apply_calibration, save_control_points

    w = world()
    settlements = list(w.settlements.values())
    info = atlas_mod.atlas_info()
    if not info.get("available"):
        return {"available": False, "applied": False,
                "error": info.get("error", ""),
                "searched": info.get("searched", []),
                "hint": "drop a surveyed location index into the maps folder"}

    try:
        report = atlas_mod.align(settlements)
    except atlas_mod.AtlasError as exc:
        return {"available": False, "applied": False, "error": str(exc),
                "searched": info.get("searched", [])}

    from .mapdata import terrain_alignment

    points = [{"id": m["id"], "x": m["x"], "y": m["y"]}
              for m in report["matched"]]
    terrain = terrain_alignment(settlements, points)

    applied = 0
    if apply and report["matched"]:
        save_control_points(points)
        applied = apply_calibration(settlements, points)
        w.rebuild()

    return {
        "available": True,
        "applied": bool(apply and applied),
        "control_points": applied,
        "survey": report["path"],
        "image": info.get("image", ""),
        "anchor": report["anchor"],
        "matched": report["count"],
        "surveyed_places": report["surveyed"],
        "missing": report["missing"],
        "moves": sorted(report["matched"], key=lambda m: -m["moved"])[:25],
        # The scenery is realigned too, so the coastline and the mountains
        # follow the towns they were drawn around.
        "terrain": terrain,
        # Where the poster image itself belongs, and how many surveyed towns
        # not present in the supplied world (normally zero after enrichment).
        "poster": atlas_mod.underlay_placement(settlements),
        "unmodelled_towns": len(report["unused"]),
        "inferred_markets": sum(
            1 for s in settlements if s.has_trait("surveyed_market")
        ),
        "revision": w.revision,
    }


@mcp.tool()
def get_world_state() -> Dict[str, Any]:
    """Current date, season, market seed, and the events now in play."""
    w = world()
    return {
        "date": str(w.date),
        "year": w.date.year,
        "month": w.date.month,
        "day": w.date.day,
        "month_name": w.date.month_name,
        "month_common_name": w.date.month_common_name,
        "season": w.date.season,
        "festival": w.date.festival,
        "follows_real_date": w.follows_real_date,
        "seed": w.config.seed,
        "revision": w.revision,
        "settlements": len(w.settlements),
        "commodities": len(w.commodities),
        "active_events": [e.to_dict() for e in w.active_events()],
        "months": [{"number": i + 1, "name": m[0], "common": m[1],
                    "season": m[2]} for i, m in enumerate(MONTHS)],
    }


@mcp.tool()
def set_world_date(year: Optional[int] = None, month: Optional[str] = None,
                   day: Optional[int] = None) -> Dict[str, Any]:
    """Move the calendar. `month` accepts a number or a Harptos name
    ("Flamerule", "Nightal") or common name ("Summertide")."""
    w = world()
    current = w.date
    try:
        m = parse_month(month) if month is not None else current.month
    except ValueError as exc:
        return _fail(exc)
    w.set_date(HarptosDate(
        year=year if year is not None else current.year,
        month=m,
        day=day if day is not None else current.day,
    ))
    return {"date": str(w.date), "season": w.date.season,
            "festival": w.date.festival}


@mcp.tool()
def set_market_seed(seed: int) -> Dict[str, Any]:
    """Reroll the small random wobble every market applies to its prices."""
    w = world()
    w.config.seed = int(seed)
    w.revision += 1
    return {"seed": w.config.seed, "revision": w.revision}


@mcp.tool()
def list_event_templates() -> Dict[str, Any]:
    """Ready-made event templates (siege, drought, festival, gold_rush, ...)."""
    return {
        "templates": {
            name: {
                "kind": spec.get("kind", "generic"),
                "supply_x": spec.get("supply", 1.0),
                "demand_x": spec.get("demand", 1.0),
                "price_x": spec.get("price", 1.0),
                "added_risk": spec.get("risk", 0.0),
                "categories": spec.get("categories", []),
                "description": spec.get("description", ""),
            }
            for name, spec in sorted(EVENT_TEMPLATES.items())
        }
    }


@mcp.tool()
def add_event(template: Optional[str] = None,
              name: Optional[str] = None,
              settlements: Optional[List[str]] = None,
              regions: Optional[List[str]] = None,
              zones: Optional[List[str]] = None,
              commodities: Optional[List[str]] = None,
              categories: Optional[List[str]] = None,
              supply: Optional[float] = None,
              demand: Optional[float] = None,
              price: Optional[float] = None,
              risk: Optional[float] = None,
              duration_months: Optional[int] = None,
              description: Optional[str] = None) -> Dict[str, Any]:
    """Add a world event that distorts prices until it is removed.

    Use a `template` (see list_event_templates) and/or supply explicit
    multipliers. Scope it with `settlements`, `regions` or `zones` (all
    empty means the whole of Faerûn) and with `commodities` or
    `categories` (empty means every good). Multipliers below 1.0 on supply
    make goods scarce and dear; above 1.0 makes them plentiful and cheap.
    """
    if template and template not in EVENT_TEMPLATES:
        return {"error": f"unknown template {template!r}",
                "known": sorted(EVENT_TEMPLATES)}
    w = world()
    try:
        event = make_event(
            template=template, name=name, settlements=settlements,
            zones=zones, regions=regions, commodities=commodities,
            categories=categories, supply=supply, demand=demand, price=price,
            risk=risk, duration_months=duration_months,
            start_month=w.date.absolute_month() if duration_months else None,
            description=description, world=w,
        )
    except (KeyError, ValueError) as exc:
        return _fail(exc)
    w.add_event(event)
    return {"added": event.to_dict(),
            "active_events": [e.id for e in w.active_events()]}


@mcp.tool()
def list_events() -> Dict[str, Any]:
    """Every event registered on the world, and which are active right now."""
    w = world()
    active = {e.id for e in w.active_events()}
    return {
        "date": str(w.date),
        "events": [dict(e.to_dict(), active=e.id in active)
                   for e in w.events.values()],
    }


@mcp.tool()
def remove_event(event_id: str) -> Dict[str, Any]:
    """Remove one event by its id."""
    return {"removed": world().remove_event(event_id), "event_id": event_id}


@mcp.tool()
def clear_events() -> Dict[str, Any]:
    """Remove every event and return the world to its baseline."""
    world().clear_events()
    return {"cleared": True, "active_events": []}


# ---------------------------------------------------------------------------
# The standing history
# ---------------------------------------------------------------------------


@mcp.tool()
def get_chronicle_summary() -> Dict[str, Any]:
    """How much standing history the world carries, and of what kind.

    The chronicle is installed by default and spans three years either side of
    1492 DR, so every price the engine quotes is already a price in a
    particular month of a particular history.
    """
    from .chronicle import chronicle_summary

    try:
        return chronicle_summary(world())
    except Exception as exc:
        return _fail(exc)


@mcp.tool()
def get_settlement_history(settlement: str) -> Dict[str, Any]:
    """Every recorded event touching one settlement, past and future.

    Includes regional and world events as well as local ones, with the exact
    months each runs between.
    """
    from .chronicle import settlement_timeline

    try:
        return settlement_timeline(settlement, world=world())
    except Exception as exc:
        return _fail(exc)


@mcp.tool()
def get_settlement_timeline(settlement: str,
                            commodity: Optional[List[str]] = None,
                            basket_size: int = 6) -> Dict[str, Any]:
    """Price a basket of goods in one settlement in every month of history.

    Returns the month-by-month series, the events behind it, and an analysis
    naming the dearest and cheapest months and what each event cost the town.
    Pass `commodity` to choose the goods; otherwise a staple basket is used.
    """
    from .location import location_timeline

    try:
        return location_timeline(settlement, world=world(),
                                 commodities=commodity or None,
                                 size=max(1, min(12, int(basket_size))))
    except Exception as exc:
        return _fail(exc)


@mcp.tool()
def get_location_detail(settlement: str, year: Optional[int] = None,
                        month: Optional[str] = None,
                        category: Optional[str] = None) -> Dict[str, Any]:
    """One settlement's whole market at one month, with a quiet-world control.

    Prices the market twice - as history has it, and again with every event
    lifted - so the answer says what the running troubles are actually costing
    rather than only what things cost.
    """
    from .location import location_detail

    try:
        w = world()
        stamp = w.date.absolute_month()
        if year is not None or month is not None:
            resolved = parse_month(month) if month else w.date.month
            stamp = (year if year is not None else w.date.year) * 12 + resolved
        return location_detail(settlement, world=w, month=stamp,
                               category=category)
    except Exception as exc:
        return _fail(exc)


@mcp.tool()
def reset_chronicle(install: bool = True) -> Dict[str, Any]:
    """Regenerate the standing history, or strip it out entirely.

    Hand-placed events added with `add_event` are left alone either way.
    """
    from .chronicle import clear_chronicle, install_chronicle

    try:
        w = world()
        removed = clear_chronicle(w)
        added = install_chronicle(w, replace=False) if install else 0
        w.revision += 1
        return {"removed": removed, "installed": added,
                "events": len(w.events)}
    except Exception as exc:
        return _fail(exc)


# ---------------------------------------------------------------------------
# Catalog CRUD: products, settlements, businesses, trade routes
# ---------------------------------------------------------------------------
# Every tool below edits the live world immediately and rewrites the matching
# JSON file under faerun/data/store/, so the change is still there next time
# the server (or the CLI, or the web app) starts.


@mcp.tool()
def list_wages() -> Dict[str, Any]:
    """List baseline daily wages used by the labor and service models.

    Values are gp per productive worker-day before the local settlement
    modifier is applied. They are scenario assumptions, not canon or survey
    data.
    """
    from .wages import list_wages as _list

    return {"wages": _list()}


@mcp.tool()
def get_wage(occupation_id: str) -> Dict[str, Any]:
    """Read one baseline wage by occupation id."""
    from .wages import list_wages as _list

    row = next((item for item in _list() if item["id"] == occupation_id), None)
    return {"wage": row} if row else _fail(ValueError(f"Unknown wage occupation: {occupation_id!r}"))


@mcp.tool()
def create_wage(occupation_id: str, daily_wage_gp: float) -> Dict[str, Any]:
    """Create a baseline wage record in gp per productive worker-day."""
    from .wages import create_wage as _create

    try:
        row = _create(occupation_id, daily_wage_gp)
        world().revision += 1
        return {"created": row}
    except ValueError as exc:
        return _fail(exc)


@mcp.tool()
def update_wage(occupation_id: str, daily_wage_gp: float) -> Dict[str, Any]:
    """Change an existing baseline wage; location modifiers remain automatic."""
    from .wages import update_wage as _update

    try:
        row = _update(occupation_id, daily_wage_gp)
        world().revision += 1
        return {"updated": row}
    except ValueError as exc:
        return _fail(exc)


@mcp.tool()
def delete_wage(occupation_id: str) -> Dict[str, Any]:
    """Remove a baseline wage record; unknown occupations use general labor pay."""
    from .wages import delete_wage as _delete

    removed = _delete(occupation_id)
    if removed:
        world().revision += 1
    return {"removed": removed, "id": occupation_id}


@mcp.tool()
def create_commodity(
    name: str, category: str, base_price: float, id: Optional[str] = None,
    unit: str = "item", weight: float = 1.0, produced_by: Optional[List[str]] = None,
    required_skill: Optional[Dict[str, float]] = None,
    demand: float = 1.0, luxury: float = 0.0, perishable: float = 0.0,
    demand_traits: Optional[Dict[str, float]] = None, season: Optional[Dict[str, float]] = None,
    substitutes: Optional[List[str]] = None, requires: Optional[List[str]] = None,
    description: str = "", bom: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Add a new tradeable product or raw commodity.

    `id` defaults to a slug of `name`. `category` groups it for listings
    (food, metal, cloth, arms, tool, luxury, gem, arcane, drink, livestock,
    exotic, ...). `base_price` is gp per `unit` in an average market.
    `produced_by` lists industry tags a settlement needs to make it locally
    (see a settlement's `industries`). `demand` is per-capita consumption
    (1.0 = staple); `luxury` is wealth elasticity (0 necessity, 1 pure
    luxury); `perishable` drives spoilage in transit (0-1). `bom` names
    input commodity ids and the units of each needed to make one unit of
    this good, letting its price follow its ingredients.
    """
    from .catalog import CatalogError, create_commodity as _create

    try:
        commodity = _create(
            name, category, base_price, id=id, unit=unit, weight=weight,
            produced_by=produced_by, demand=demand, luxury=luxury,
            required_skill=required_skill,
            perishable=perishable, demand_traits=demand_traits, season=season,
            substitutes=substitutes, requires=requires, description=description,
            bom=bom,
        )
    except CatalogError as exc:
        return _fail(exc)
    return {"created": commodity.to_dict()}


@mcp.tool()
def update_commodity(
    id: str, name: Optional[str] = None, category: Optional[str] = None,
    base_price: Optional[float] = None, unit: Optional[str] = None,
    weight: Optional[float] = None, produced_by: Optional[List[str]] = None,
    required_skill: Optional[Dict[str, float]] = None,
    demand: Optional[float] = None, luxury: Optional[float] = None,
    perishable: Optional[float] = None, demand_traits: Optional[Dict[str, float]] = None,
    season: Optional[Dict[str, float]] = None, substitutes: Optional[List[str]] = None,
    requires: Optional[List[str]] = None, description: Optional[str] = None,
    bom: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Change one or more fields of an existing product. Omitted fields are unchanged."""
    from .catalog import CatalogError, update_commodity as _update

    try:
        commodity = _update(
            id, name=name, category=category, base_price=base_price, unit=unit,
            weight=weight, produced_by=produced_by, demand=demand, luxury=luxury,
            required_skill=required_skill,
            perishable=perishable, demand_traits=demand_traits, season=season,
            substitutes=substitutes, requires=requires, description=description,
            bom=bom,
        )
    except CatalogError as exc:
        return _fail(exc)
    return {"updated": commodity.to_dict()}


@mcp.tool()
def delete_commodity(id: str) -> Dict[str, Any]:
    """Remove a product from the catalogue. Existing price history is unaffected."""
    from .catalog import delete_commodity as _delete

    return {"removed": _delete(id), "id": id}


@mcp.tool()
def create_settlement(
    name: str, region: str, zone: str, population: int, x: float, y: float,
    id: Optional[str] = None, wealth: float = 1.0, tax: float = 0.05,
    security: float = 0.75, port: Optional[str] = None, river: bool = False,
    terrain: str = "plains", landmass: str = "faerun", underdark: bool = False,
    traits: Optional[List[str]] = None, industries: Optional[Dict[str, float]] = None,
    specialties: Optional[Dict[str, float]] = None, shortages: Optional[List[str]] = None,
    ruler: str = "", description: str = "",
) -> Dict[str, Any]:
    """Add a new market: a town, city, citadel, port or Underdark enclave.

    `x`/`y` are map miles (x east from the Trackless Sea, y south from the
    Sea of Moving Ice); nearby settlements get automatic caravan tracks once
    `zone` matches or borders theirs. `port` names a sea basin ("Sea of
    Swords", "Sea of Fallen Stars", "Moonsea", "Lake of Steam", ...) to make
    it eligible for sea lanes. `industries` and `specialties` are tag ->
    level dicts (e.g. {"farm": 2, "smith": 1}) that drive local production
    and price bonuses; `shortages` lists commodity ids the town cannot supply.
    """
    from .catalog import CatalogError, create_settlement as _create

    try:
        settlement = _create(
            name, region, zone, population, x, y, id=id, wealth=wealth, tax=tax,
            security=security, port=port, river=river, terrain=terrain,
            landmass=landmass, underdark=underdark, traits=traits,
            industries=industries, specialties=specialties, shortages=shortages,
            ruler=ruler, description=description,
        )
    except CatalogError as exc:
        return _fail(exc)
    return {"created": settlement.to_dict()}


@mcp.tool()
def update_settlement(
    id: str, name: Optional[str] = None, region: Optional[str] = None,
    zone: Optional[str] = None, population: Optional[int] = None,
    x: Optional[float] = None, y: Optional[float] = None, wealth: Optional[float] = None,
    tax: Optional[float] = None, security: Optional[float] = None,
    port: Optional[str] = None, river: Optional[bool] = None, terrain: Optional[str] = None,
    landmass: Optional[str] = None, underdark: Optional[bool] = None,
    traits: Optional[List[str]] = None, industries: Optional[Dict[str, float]] = None,
    specialties: Optional[Dict[str, float]] = None, shortages: Optional[List[str]] = None,
    ruler: Optional[str] = None, description: Optional[str] = None,
) -> Dict[str, Any]:
    """Change one or more fields of an existing settlement. Omitted fields are unchanged.

    Moving `x`/`y` or changing `zone`, `terrain`, `landmass`, `underdark` or
    `port` rebuilds the trade network, which can add, drop or re-cost routes.
    """
    from .catalog import CatalogError, update_settlement as _update

    try:
        settlement = _update(
            id, name=name, region=region, zone=zone, population=population, x=x,
            y=y, wealth=wealth, tax=tax, security=security, port=port, river=river,
            terrain=terrain, landmass=landmass, underdark=underdark, traits=traits,
            industries=industries, specialties=specialties, shortages=shortages,
            ruler=ruler, description=description,
        )
    except CatalogError as exc:
        return _fail(exc)
    return {"updated": settlement.to_dict()}


@mcp.tool()
def delete_settlement(id: str) -> Dict[str, Any]:
    """Remove a settlement and rebuild the trade network around the gap.

    Businesses left with no remaining valid location are removed too.
    """
    from .catalog import delete_settlement as _delete

    return {"removed": _delete(id), "id": id}


@mcp.tool()
def create_business(
    name: str, headquarters: str, locations: List[str], id: Optional[str] = None,
    specialties: Optional[List[str]] = None, offers: Optional[Dict[str, str]] = None,
    price_modifier: float = 1.0, description: str = "",
) -> Dict[str, Any]:
    """Add a merchant house or workshop operating in one or more settlements.

    `headquarters` and every entry in `locations` must be existing
    settlements (name or id). `offers` maps a commodity id to the quality
    it stocks there ("basic", "standard", "fine" or "masterwork").
    `price_modifier` scales its prices versus the local market (1.0 = par).
    """
    from .catalog import CatalogError, create_business as _create

    try:
        business = _create(
            name, headquarters, locations, id=id, specialties=specialties,
            offers=offers, price_modifier=price_modifier, description=description,
        )
    except CatalogError as exc:
        return _fail(exc)
    return {"created": business.to_dict()}


@mcp.tool()
def update_business(
    id: str, name: Optional[str] = None, headquarters: Optional[str] = None,
    locations: Optional[List[str]] = None, specialties: Optional[List[str]] = None,
    offers: Optional[Dict[str, str]] = None, price_modifier: Optional[float] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Change one or more fields of an existing business. Omitted fields are unchanged."""
    from .catalog import CatalogError, update_business as _update

    try:
        business = _update(
            id, name=name, headquarters=headquarters, locations=locations,
            specialties=specialties, offers=offers, price_modifier=price_modifier,
            description=description,
        )
    except CatalogError as exc:
        return _fail(exc)
    return {"updated": business.to_dict()}


@mcp.tool()
def delete_business(id: str) -> Dict[str, Any]:
    """Remove a business from the world."""
    from .catalog import delete_business as _delete

    return {"removed": _delete(id), "id": id}


@mcp.tool()
def add_trade_route(name: str, stops: List[str], quality: float = 1.0,
                     kind: str = "road") -> Dict[str, Any]:
    """Add a named overland/river/tunnel trade artery linking settlements in order.

    `stops` are settlement names or ids visited in order (at least two).
    `quality` scales freight cost and speed (1.0 ordinary road; see
    list_travel_modes for the vocabulary). `kind` is one of road, trail,
    track, river, barge, portage, tunnel, air or teleport, or several
    joined with "+" (e.g. "river+portage") for a route that changes carrier
    partway. Re-adding a name already in use replaces that route.
    """
    from .catalog import CatalogError, add_route as _add

    try:
        return {"added": _add(name, stops, quality, kind)}
    except CatalogError as exc:
        return _fail(exc)


@mcp.tool()
def remove_trade_route(name: str) -> Dict[str, Any]:
    """Remove a named route added with add_trade_route, by its exact name."""
    from .catalog import remove_route as _remove

    return {"removed": _remove(name), "name": name}


@mcp.tool()
def add_sea_lane(name: str, stops: List[str], quality: float = 1.0,
                  kind: Optional[str] = None) -> Dict[str, Any]:
    """Add a named sea lane between ports, regardless of distance heuristics.

    `stops` are port settlement names or ids in order (at least two).
    `kind` defaults to plain sea; use "sea+ferry" or "sea+air" for a lane
    that changes carrier partway. Re-adding a name already in use replaces
    that lane.
    """
    from .catalog import CatalogError, add_sea_lane as _add

    try:
        return {"added": _add(name, stops, quality, kind)}
    except CatalogError as exc:
        return _fail(exc)


@mcp.tool()
def remove_sea_lane(name: str) -> Dict[str, Any]:
    """Remove a named sea lane added with add_sea_lane, by its exact name."""
    from .catalog import remove_sea_lane as _remove

    return {"removed": _remove(name), "name": name}


# ---------------------------------------------------------------------------
# Commodity request board
# ---------------------------------------------------------------------------


def _board():
    from .orders import TradeStore, default_ledger_path

    current = world()
    if current.trade_store is None:
        current.trade_store = TradeStore(default_ledger_path())
    return current.trade_store


@mcp.tool()
def list_commodity_requests(status: Optional[str] = "open", offset: int = 0,
                             limit: int = 50) -> Dict[str, Any]:
    """List commodity requests posted to the public request/bid market board.

    `status` filters to "open", "accepted" or "cancelled"; pass None for
    every request. This is the same board the web request-board page reads.
    """
    from .trading import TradeError

    try:
        return _board().list_requests(world(), status=status, offset=offset, limit=limit)
    except TradeError as exc:
        return _fail(exc)


@mcp.tool()
def get_commodity_request(request_id: str) -> Dict[str, Any]:
    """Read one commodity request with its bids and audit history."""
    from .trading import TradeError

    try:
        return {"request": _board().request(world(), request_id)}
    except TradeError as exc:
        return _fail(exc)


@mcp.tool()
def post_commodity_request(
    requester_name: str, commodity: str, quantity: int, quality: str,
    settlement_id: str, needed_by: str, notes: str = "",
    max_price_gp: Optional[float] = None,
) -> Dict[str, Any]:
    """Post a commodity request other parties can bid on.

    `commodity` and `settlement_id` must be known catalog ids. `quality` is
    one of basic, standard, fine or masterwork. `needed_by` is a Harptos
    YYYY-MM-DD date on or after the current world date. `max_price_gp` is an
    optional ceiling per unit; omit it to accept any price.
    """
    from .trading import TradeError

    try:
        request = _board().post_request(
            world(), requester_name=requester_name, commodity=commodity,
            quantity=quantity, quality=quality, settlement_id=settlement_id,
            needed_by=needed_by, notes=notes, max_price_gp=max_price_gp,
        )
        return {"created": request}
    except TradeError as exc:
        return _fail(exc)


@mcp.tool()
def cancel_commodity_request(request_id: str, version: int) -> Dict[str, Any]:
    """Cancel an open commodity request. `version` must match its current version."""
    from .trading import TradeError

    try:
        return {"request": _board().cancel_request(world(), request_id=request_id, version=version)}
    except TradeError as exc:
        return _fail(exc)


@mcp.tool()
def place_commodity_bid(
    request_id: str, bidder_name: str, price_gp: float, quantity: int,
    delivery_by: str, notes: str = "",
) -> Dict[str, Any]:
    """Bid to fulfil an open commodity request.

    `quantity` cannot exceed the request's remaining quantity, and
    `delivery_by` must fall on or before the request's needed_by date.
    """
    from .trading import TradeError

    try:
        request = _board().bid(
            world(), request_id=request_id, bidder_name=bidder_name,
            price_gp=price_gp, quantity=quantity, delivery_by=delivery_by, notes=notes,
        )
        return {"request": request}
    except TradeError as exc:
        return _fail(exc)


@mcp.tool()
def withdraw_commodity_bid(request_id: str, bid_id: str) -> Dict[str, Any]:
    """Withdraw a pending bid from a commodity request."""
    from .trading import TradeError

    try:
        return {"request": _board().withdraw_bid(world(), request_id=request_id, bid_id=bid_id)}
    except TradeError as exc:
        return _fail(exc)


@mcp.tool()
def accept_commodity_bid(request_id: str, bid_id: str, version: int) -> Dict[str, Any]:
    """Accept a pending bid, closing the request and rejecting its other bids.

    `version` must match the request's current version.
    """
    from .trading import TradeError

    try:
        return {"request": _board().accept_bid(world(), request_id=request_id, bid_id=bid_id, version=version)}
    except TradeError as exc:
        return _fail(exc)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
