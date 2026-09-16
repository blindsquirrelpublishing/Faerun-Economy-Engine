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
        {"to": world().settlements[e.dst].name, "mode": e.kind,
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
            "stops": [w.settlements[sid].name if sid in w.settlements else sid
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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
