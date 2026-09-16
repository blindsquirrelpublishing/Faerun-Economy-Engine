"""Command line browser for the Faerûn market engine.

    python -m faerun.cli market "Waterdeep"
    python -m faerun.cli price "Bryn Shander" grain --quantity 20
    python -m faerun.cli compare mithral_ingot --dearest
    python -m faerun.cli route Waterdeep "Baldur's Gate"
    python -m faerun.cli arbitrage Waterdeep --category metal
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List, Optional, Sequence
from urllib.parse import quote

from .calendar import HarptosDate, MONTHS, parse_month
from .city import city_directory
from .buildinggen import generate_buildings
from .locationgen import generate_location, location_profiles
from .economy import (
    compare_prices,
    find_arbitrage,
    market_report,
    price_for,
    price_history,
    trade_summary,
)
from .events import EVENT_TEMPLATES, apply_event
from .models import format_coin
from .world import World, get_world

# ---------------------------------------------------------------------------
# Plain text table rendering
# ---------------------------------------------------------------------------


def table(rows: Sequence[Sequence[object]], headers: Sequence[str],
          aligns: Optional[str] = None) -> str:
    """Render a small fixed-width table with no third-party dependencies."""
    data = [[("" if v is None else str(v)) for v in row] for row in rows]
    heads = [str(h) for h in headers]
    widths = [len(h) for h in heads]
    for row in data:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    aligns = aligns or "l" * len(heads)

    def fmt(cells: Sequence[str]) -> str:
        out = []
        for i, cell in enumerate(cells):
            if aligns[i] == "r":
                out.append(cell.rjust(widths[i]))
            else:
                out.append(cell.ljust(widths[i]))
        return "  ".join(out).rstrip()

    lines = [fmt(heads), "  ".join("-" * w for w in widths)]
    lines.extend(fmt(row) for row in data)
    return "\n".join(lines)


def heading(text: str) -> str:
    return f"\n{text}\n{'=' * len(text)}"


def emit(payload: Dict, text: str, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(text)


# ---------------------------------------------------------------------------
# World setup from global flags
# ---------------------------------------------------------------------------


def build_world(args: argparse.Namespace) -> World:
    world = get_world()
    seasonal_inventory = getattr(args, "seasonal_inventory", None)
    if seasonal_inventory is not None:
        world.config.seasonal_inventory = seasonal_inventory
    if world.trade_store is None:
        from .orders import TradeStore, default_ledger_path
        world.trade_store = TradeStore(default_ledger_path())
    date = world.date
    if args.year is not None or args.month is not None:
        month = parse_month(args.month) if args.month else date.month
        year = args.year if args.year is not None else date.year
        date = HarptosDate(year=year, month=month, day=date.day)
        world.set_date(date)
    if args.seed is not None and args.seed != world.config.seed:
        world.config.seed = args.seed
        world.revision += 1
    for spec in args.event or []:
        _apply_event_spec(world, spec)
    return world


def _apply_event_spec(world: World, spec: str) -> None:
    """--event siege@Baldur's Gate  or  --event drought@region:Amn"""
    if "@" not in spec:
        raise SystemExit(f"bad --event {spec!r}; expected template@place")
    template, place = spec.split("@", 1)
    template = template.strip()
    place = place.strip()
    if template not in EVENT_TEMPLATES:
        raise SystemExit(f"unknown event template {template!r}; "
                         f"try one of: {', '.join(sorted(EVENT_TEMPLATES))}")
    kwargs: Dict[str, object] = {"template": template, "world": world}
    if place.lower().startswith("region:"):
        kwargs["regions"] = [place.split(":", 1)[1]]
    elif place.lower().startswith("zone:"):
        kwargs["zones"] = [place.split(":", 1)[1]]
    else:
        kwargs["settlements"] = [place]
    apply_event(**kwargs)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def _markup_percent(value: float | None) -> str:
    return "-" if value is None else f"{value:.1f}%"


def _seasonal_lines(payload: Dict) -> List[str]:
    profile = payload.get("seasonality") or {}
    inventory = payload.get("inventory") or {}
    unit = payload.get("unit", "trade units")
    lines = []
    if inventory.get("enabled") is False and inventory.get("reason"):
        lines.append("inventory disabled: " + inventory["reason"])
        if inventory.get("epoch"):
            lines.append(f"replay epoch      {inventory['epoch']} (earlier dates use steady-state quotes)")
        if profile.get("months"):
            lines.append("Configured seasonal curves below do not imply a physical ledger for this historical quote.")
    if profile.get("months"):
        lines.extend([
            f"local climate {profile.get('climate', 'unspecified')} (modeled, not canonical agronomy)",
            f"seasonal production x{profile.get('production_multiplier', 1):g}"
            f" | demand x{profile.get('demand_multiplier', 1):g}",
            "Production multipliers describe potential; recipe output still requires inputs.",
            table([
                [row["name"], f"x{row['production_multiplier']:g}", f"x{row['demand_multiplier']:g}"]
                for row in profile["months"]
            ], ["Month", "Production potential", "Demand"], aligns="lrr"),
        ])
    if inventory.get("enabled"):
        lines.extend([
            f"local storage     opening {inventory['opening_stock']:,.3f};"
            f" closing {inventory['closing_stock']:,.3f} {unit}",
            "free local stock  "
            + (f"{inventory['uncommitted_stock']:,.3f}" if inventory.get("uncommitted_stock") is not None else "-")
            + f" {unit} (physical-model pool, before dated PO planning claims)",
            f"storage capacity  {inventory['storage_capacity']:,.3f} {unit};"
            f" protected reserve {inventory['reserve_target']:,.3f} {unit}",
            f"storage losses    spoilage {inventory['spoilage']:,.3f};"
            f" overflow {inventory['overflow']:,.3f} {unit}",
            f"stock draw        {inventory['stock_draw_per_day']:,.3f} {unit}/day",
            "days of cover     " + (
                "not applicable (no demand)" if inventory.get("days_of_cover") is None
                else f"{inventory['days_of_cover']:,.3f}"
            ),
            f"replay epoch      {inventory.get('epoch', 'not supplied')}",
            "stock basis       " + inventory.get(
                "stock_basis", "Modeled local carryover, not a ten-day stock-window estimate."
            ),
            "replay model      " + (
                "versioned local SQLite checkpoints shared across restarts."
                if inventory.get("checkpoint_storage") == "local SQLite cache"
                else "in-memory month checkpoints; same config/events reconstruct balances after restart."),
            "initial stocks    reserve-target seed assumes prior harvest; location/product overrides are configurable.",
            "limits            ingredients and finished goods tracked; player purchases do not execute against inventory.",
            "trade timing      same-day steady-state deliveries, not scheduled shipment arrivals.",
        ])
        if "storage_days" in profile:
            lines.append(
                f"storage policy    {profile['storage_days']:g} baseline days capacity;"
                f" {profile.get('reserve_days', 0):g} baseline days reserve;"
                f" {profile.get('storage_loss', 0) * 100:g}% storage loss/day"
            )
    return lines


def cmd_market(args: argparse.Namespace, world: World) -> None:
    report = market_report(args.settlement, world=world, category=args.category,
                           sort=args.sort)
    rows = []
    for p in report["prices"]:
        rows.append([
            p["commodity_name"], p["category"], format_coin(p["price"]),
            format_coin(p["buy_price"]), _markup_percent(p["merchant_markup_pct"]),
            f"/{p['unit']}", f"x{p['multiplier']:.2f}", p["availability"],
            p["stock"], p["uncommitted_stock"], p["source"] or "local",
        ])
    text = (
        heading(f"{report['settlement']} - {report['region']}")
        + f"\n{report['size']}, population {report['population']:,}"
        f" | ruler: {report['ruler'] or 'unknown'}"
        f"\ntariff {report['tariff'] * 100:.0f}% | wealth x{report['wealth']}"
        f" | {report['date']} ({report['season']})"
        + (f"\n{report['description']}" if report.get("description") else "")
        + (f"\nPopulation basis: {report['population_model']['rationale']}"
           if report["population_model"].get("rationale") else "")
        + (f"\nEvents: {', '.join(report['events'])}"
           if report.get("events") else "")
        + "\n\n"
        + table(rows,
                ["Commodity", "Category", "Buy from merchant", "Sell to merchant", "Markup", "Unit", "vs base",
                 "Availability", "Modeled stock", "Uncommitted", "Source"],
                aligns="llrrrlrlrrl")
        + "\n\nCheapest here: "
        + (", ".join(f"{r['commodity']} (x{r['x_base']:.2f})"
                     for r in report["cheap_here"]) or "nothing notable")
        + "\nDearest here:  "
        + (", ".join(f"{r['commodity']} (x{r['x_base']:.2f})"
                     for r in report["dear_here"]) or "nothing notable")
    )
    if any((row.get("inventory") or {}).get("enabled") for row in report["prices"]):
        text += (
            "\nSeasonal stocks carry forward with storage losses and protected reserves; "
            "these modeled quantities are not bookings. Use price for local curves and storage details."
        )
    else:
        reasons = sorted({
            row["inventory"]["reason"] for row in report["prices"]
            if (row.get("inventory") or {}).get("enabled") is False
            and (row.get("inventory") or {}).get("reason")
        })
        if reasons:
            text += "\nInventory disabled: " + "; ".join(reasons)
    emit(report, text, args.json)


def cmd_price(args: argparse.Namespace, world: World) -> None:
    quote = price_for(args.settlement, args.commodity, world=world,
                      quantity=args.quantity)
    d = quote.to_dict()
    inventory = d.get("inventory") or {}
    persistent = bool(inventory.get("enabled"))
    lines = [
        heading(f"{quote.commodity_name} in {quote.settlement}"),
        f"buy from merchant {format_coin(quote.price)} per {quote.unit}"
        + (f"  (x{args.quantity} = {format_coin(quote.price * args.quantity)})"
           if args.quantity != 1 else ""),
        f"sell to merchant  {format_coin(quote.buy_price)} per {quote.unit}"
        + (f"  (x{args.quantity} = {format_coin(quote.buy_price * args.quantity)})"
           if args.quantity != 1 else ""),
        f"merchant markup   {_markup_percent(quote.merchant_markup_pct)} before costs and losses",
        f"uncommitted       {quote.uncommitted_stock:,} {quote.unit}s"
        + (" after protected reserves" if persistent else f" over {quote.stock_horizon_days:g} modeled days")
        + f"; {quote.uncommitted_supply_per_day:,.3f}/day",
        f"base price   {format_coin(quote.base_price)}  ->  x{quote.multiplier:.2f}",
        f"availability {quote.availability} (about {quote.stock:,} {quote.unit}s"
        + (" modeled local stock, including protected reserves)"
           if persistent else f" over {quote.stock_horizon_days:g} modeled days, including local reservations)"),
          f"daily demand {quote.demand_per_day:,.2f} {quote.unit}s"
          + (f"; local production {quote.production_per_day:,.2f} {quote.unit}s"
              if quote.production_per_day > 0 else ""),
        f"supply {quote.supply_index:.2f} vs demand {quote.demand_index:.2f}"
        f"  (scarcity {quote.scarcity:.2f})",
    ]
    if persistent and d.get("uncommitted_basis"):
        lines.append("uncommitted basis " + d["uncommitted_basis"])
    lines.extend(_seasonal_lines(d))
    if quote.source:
        lines.append(f"imported from {quote.source}"
                     + (f" - {quote.source_distance:,.0f} miles, "
                        f"{quote.source_days:.0f} days"
                        if quote.source_distance and quote.source_days else ""))
    lines.append("")
    lines.append(table(
        [[k.replace("_", " "), f"{v}"] for k, v in quote.factors.items()],
        ["Factor", "Value"], aligns="lr"))
    if quote.notes:
        lines.append("")
        lines.extend(f"* {n}" for n in quote.notes)
    emit(d, "\n".join(lines), args.json)


def cmd_compare(args: argparse.Namespace, world: World) -> None:
    result = compare_prices(args.commodity, world=world, region=args.region,
                            limit=args.limit, cheapest_first=not args.dearest)
    rows = [[m["settlement"], format_coin(m["price"]), format_coin(m["buy_price"]),
             _markup_percent(m["merchant_markup_pct"]), f"x{m['multiplier']:.2f}",
             m["availability"], m["stock"], m["uncommitted_stock"], m["source"] or "local"]
            for m in result["markets"]]
    text = (
        heading(f"{result['commodity']} ({format_coin(result['base_price'])}"
                f" per {result['unit']} base) - {result['date']}")
        + "\n"
        + table(rows, ["Market", "Buy from merchant", "Sell to merchant", "Markup", "vs base",
                       "Availability", "Stock estimate", "Uncommitted", "Source"], aligns="lrrrrlrrl")
    )
    emit(result, text, args.json)


def cmd_route(args: argparse.Namespace, world: World) -> None:
    result = world.route(args.origin, args.destination, optimise=args.optimise)
    if not result.get("reachable", True):
        emit(result, f"No route from {result['origin']} to {result['destination']}.",
             args.json)
        return
    rows = [[leg["from"], leg["to"], leg.get("mode_label") or leg["mode"],
             f"{leg['miles']:,.0f}",
             f"{leg['days']:.1f}", f"{leg['hazard']:.2f}", leg["via"]]
            for leg in result["legs"]]
    text = (
        heading(f"{result['origin']} -> {result['destination']}")
        + f"\n{result['distance']:,.0f} miles, {result['days']:.1f} days"
        f" ({result['caravan_days']:.1f} by ox-cart),"
        f" worst leg hazard {result['hazard']:.2f}"
        + (f", {result['transfers']} cargo transfer"
           + ("s" if result.get("transfers", 0) != 1 else "")
           if result.get("transfers") else "")
        + f"\nfreight about {format_coin(result['freight_gp_per_100lb'])}"
        " per 100 lb\n\n"
        + table(rows, ["From", "To", "Mode", "Miles", "Days", "Hazard", "Via"],
                aligns="llrrrrl")
    )
    emit(result, text, args.json)


def cmd_arbitrage(args: argparse.Namespace, world: World) -> None:
    result = find_arbitrage(args.origin, world=world, max_days=args.max_days,
                            cargo_pounds=args.cargo, category=args.category,
                            limit=args.limit)
    rows = [[d["commodity"], d["destination"], format_coin(d["buy_at_origin"]),
             format_coin(d["sell_at_destination"]), f"{d['margin_pct']:.0f}%",
             f"{d['profit_per_load']:,.0f}", f"{d['travel_days']:.1f}",
             f"{d['risk']:.2f}"]
            for d in result["deals"]]
    text = (
        heading(f"Cargoes out of {result['origin']} - {result['date']}")
        + f"\n{result['cargo_pounds']:,.0f} lb load, up to "
        f"{result['max_days']:.0f} days travel\n\n"
        + table(rows, ["Commodity", "Sell in", "Buy", "Sell", "Margin",
                       "Profit/load gp", "Days", "Risk"], aligns="llrrrrrr")
    )
    emit(result, text, args.json)


def cmd_history(args: argparse.Namespace, world: World) -> None:
    result = price_history(args.settlement, args.commodity, world=world,
                           months=args.months)
    span = max(result["high"] - result["low"], 1e-9)
    rows = []
    for point in result["series"]:
        bar = "#" * int(round(1 + 28 * (point["price"] - result["low"]) / span))
        rows.append([point["month"], point["season"],
                     format_coin(point["price"]), bar])
    text = (
        heading(f"{result['commodity']} in {result['settlement']}")
        + f"\nlow {format_coin(result['low'])} | average "
        f"{format_coin(result['average'])} | high {format_coin(result['high'])}\n\n"
        + table(rows, ["Month", "Season", "Price", ""], aligns="llrl")
    )
    emit(result, text, args.json)


def cmd_trade(args: argparse.Namespace, world: World) -> None:
    result = trade_summary(args.settlement, world=world, top=args.top)
    text = (
        heading(f"{result['settlement']} - {result['region']}")
        + "\n\nExports (cheap here)\n"
        + table([[e["commodity"], format_coin(e["consumer_buy_price"]),
                  format_coin(e["consumer_sell_price"]), f"x{e['x_base']:.2f}",
                  e["stock_per_tenday"], e["uncommitted_stock"]] for e in result["exports"]],
                ["Commodity", "Buy from merchant", "Sell to merchant", "vs base", "Stock estimate", "Uncommitted"], aligns="lrrrrr")
        + "\n\nImports (dear here)\n"
        + table([[i["commodity"], format_coin(i["consumer_buy_price"]),
                   format_coin(i["consumer_sell_price"]), f"x{i['x_base']:.2f}",
                  i["from"] or "-", i["availability"]] for i in result["imports"]],
                ["Commodity", "Buy from merchant", "Sell to merchant", "vs base", "From", "Availability"],
                aligns="lrrrll")
    )
    emit(result, text, args.json)


def cmd_settlements(args: argparse.Namespace, world: World) -> None:
    rows = []
    payload = []
    for s in sorted(world.settlements.values(), key=lambda x: (x.region, -x.population)):
        if args.region and args.region.lower() not in (s.region + " " + s.zone).lower():
            continue
        if args.search and args.search.lower() not in s.name.lower():
            continue
        rows.append([s.name, s.region, s.size, f"{s.population:,}",
                     f"x{s.wealth:.2f}", f"{s.tax * 100:.0f}%", s.terrain,
                     " ".join(s.traits[:4])])
        payload.append(s.to_dict())
    text = (heading(f"{len(rows)} markets")
            + "\n" + table(rows, ["Name", "Region", "Size", "Population",
                                  "Wealth", "Tariff", "Terrain", "Traits"],
                           aligns="lllrrrll"))
    emit({"settlements": payload}, text, args.json)


def cmd_commodities(args: argparse.Namespace, world: World) -> None:
    rows = []
    payload = []
    for c in world.commodities.values():
        if args.category and c.category != args.category:
            continue
        if args.search and args.search.lower() not in c.name.lower():
            continue
        rows.append([c.id, c.name, c.category, format_coin(c.base_price),
                     c.unit, f"{c.weight:g}", " ".join(c.produced_by[:3])])
        payload.append(c.to_dict())
    text = (heading(f"{len(rows)} goods")
            + "\n" + table(rows, ["Id", "Name", "Category", "Base", "Unit",
                                  "Lb", "Made by"], aligns="lllrlrl"))
    emit({"commodities": payload}, text, args.json)


def cmd_regions(args: argparse.Namespace, world: World) -> None:
    payload = []
    for region in world.regions:
        members = [s for s in world.settlements.values() if s.region == region]
        payload.append({
            "region": region,
            "markets": len(members),
            "population": sum(s.population for s in members),
            "settlements": sorted(s.name for s in members),
        })
    rows = [[r["region"], r["markets"], f"{r['population']:,}"] for r in payload]
    emit({"regions": payload},
         heading("Regions") + "\n" + table(rows, ["Region", "Markets", "Population"],
                                           aligns="lrr"),
         args.json)


def cmd_events(args: argparse.Namespace, world: World) -> None:
    if args.clear:
        world.clear_events()
    events = [e.to_dict() for e in world.active_events()]
    rows = [[e["id"], e["name"], e["kind"],
             ", ".join(e["settlements"] or e["regions"] or e["zones"]) or "everywhere",
             ", ".join(e["categories"] or e["commodities"]) or "all goods",
             f"x{e['supply']:.2f}", f"x{e['demand']:.2f}", f"{e['risk']:.2f}"]
            for e in events]
    text = (heading("Active events")
            + "\n" + (table(rows, ["Id", "Name", "Kind", "Where", "What",
                                   "Supply", "Demand", "Risk"],
                            aligns="lllllrrr") if rows else "none")
            + "\n\nTemplates: " + ", ".join(sorted(EVENT_TEMPLATES)))
    emit({"events": events, "templates": sorted(EVENT_TEMPLATES)}, text, args.json)


def cmd_chronicle(args: argparse.Namespace, world: World) -> None:
    """The standing history: everything the world remembers about a place."""
    from .chronicle import chronicle_summary, settlement_timeline

    if not args.settlement:
        summary = chronicle_summary(world)
        rows = [[kind, str(count)] for kind, count in summary["by_kind"].items()]
        text = (heading(f"Chronicle {summary['first_year']}-{summary['last_year']} DR")
                + f"\n{summary['events']} events over {summary['months']} months\n\n"
                + (table(rows, ["Kind", "Events"], aligns="lr") if rows else "none"))
        emit(summary, text, args.json)
        return

    data = settlement_timeline(args.settlement, world=world)
    rows = [[e["start"] or "always", e["end"] or "-", e["name"], e["kind"],
             f"x{e['supply']:.2f}", f"x{e['demand']:.2f}", f"{e['risk']:.2f}"]
            for e in data["events"]]
    text = (heading(f"The chronicle of {data['settlement']}")
            + f"\n{data['region']}\n\n"
            + (table(rows, ["From", "To", "Event", "Kind", "Supply", "Demand",
                            "Risk"], aligns="llllrrr") if rows
               else "nothing recorded"))
    emit(data, text, args.json)


def cmd_timeline(args: argparse.Namespace, world: World) -> None:
    """Walk a basket of goods through the whole chronicle window."""
    from .location import location_timeline

    data = location_timeline(args.settlement, world=world,
                             commodities=args.commodity or None,
                             size=args.size)
    rows = []
    for row in data["series"]:
        if args.only_year and row["year"] != args.only_year:
            continue
        rows.append([row["label"], f"{row['basket_cost']:.2f}",
                     f"{row['index']:.3f}",
                     str(len(row["events"])) if row["events"] else ""])
    a = data["analysis"]
    lines = [
        f"Basket: {', '.join(c['name'] for c in data['basket'])}",
        f"Average index {a['mean_index']:.3f}, volatility {a['volatility']:.3f}",
        f"Dearest {a['dearest']['label']} ({a['dearest']['index']:.3f}), "
        f"cheapest {a['cheapest']['label']} ({a['cheapest']['index']:.3f})",
        f"{a['troubled_months']} months under an event, {a['quiet_months']} quiet",
    ]
    if a["event_impact"]:
        lines.append("")
        lines.append("What each event did to the basket:")
        for row in a["event_impact"]:
            lines.append(f"  {row['change']*100:+6.1f}%  {row['name']}")
    text = (heading(f"{data['settlement']} through the chronicle")
            + "\n" + "\n".join(lines) + "\n\n"
            + table(rows, ["Month", "Basket", "Index", "Events"],
                    aligns="lrrr"))
    emit(data, text, args.json)


def cmd_serve(args: argparse.Namespace, world: World) -> None:
    from .underlay import set_override
    from .web import serve

    # Pin the poster map before the server starts so the startup banner can
    # report whether the overlay will be available.
    if getattr(args, "underlay", ""):
        set_override(args.underlay)
    serve(host=args.host, port=args.port, open_browser=not args.no_browser,
          verbose=getattr(args, "verbose", False),
          page=getattr(args, "page", ""))


def cmd_map(args: argparse.Namespace, world: World) -> None:
    """Same server as `serve`, but the browser lands on the 3D map."""
    args.page = "map.html"
    cmd_serve(args, world)


def cmd_location(args: argparse.Namespace, world: World) -> None:
    """Same server again, landing on one settlement's history."""
    page = "location.html"
    if args.settlement:
        # Resolve here so a typo fails at the prompt rather than in the browser.
        s = world.find_settlement(args.settlement)
        page += "?settlement=" + quote(s.id)
    args.page = page
    cmd_serve(args, world)


def cmd_atlas(args: argparse.Namespace, world: World) -> None:
    """Realign every market from a surveyed index of a published poster map.

    The click-to-place calibration screen exists because nobody can read pixel
    positions off an image by hand at scale.  A survey file does exactly that
    job offline and far more accurately, so if one is present this is the fast
    path: match it by name, and place every market at its true distance from
    the survey's origin town.
    """
    from . import atlas as atlas_mod
    from .calibration import apply_calibration, save_control_points
    from .mapdata import terrain_alignment

    settlements = list(world.settlements.values())
    try:
        survey = atlas_mod.load_atlas(args.file)
        if not survey:
            searched = atlas_mod.atlas_info(args.file)["searched"]
            emit({"available": False, "error": "", "searched": searched,
                  "matched": [], "count": 0},
                 "No survey file found. Looked for "
                 + ", ".join(atlas_mod.ATLAS_NAMES) + " in:\n  "
                 + "\n  ".join(searched), args.json)
            return
        report = atlas_mod.align(settlements, atlas=survey, anchor=args.anchor)
    except atlas_mod.AtlasError as exc:
        emit({"available": False, "error": str(exc), "matched": [],
              "count": 0},
             f"Survey unusable: {exc}", args.json)
        return

    moved = [m for m in report["matched"] if m["moved"] >= 1.0]
    moved.sort(key=lambda m: -m["moved"])

    lines = [heading(f"Survey alignment - {report['path']}")]
    lines.append(
        f"anchored on {report['anchor']}, {report['count']} of "
        f"{len(settlements)} markets matched against {report['surveyed']} "
        "surveyed places"
    )
    if moved:
        rows = [[m["name"], m["fromX"], m["fromY"], m["x"], m["y"], m["moved"]]
                for m in moved[:args.limit]]
        lines.append(table(rows, ["Market", "From x", "From y", "To x",
                                  "To y", "Miles"], aligns="lrrrrr"))
        if len(moved) > args.limit:
            lines.append(f"... and {len(moved) - args.limit} more")
    else:
        lines.append("Every matched market is already in place.")

    if report["missing"]:
        lines.append("\nNot in the survey (left where they are): "
                     + ", ".join(report["missing"]))

    # Rebuilding the map moves the scenery as well as the markets, so say what
    # the coastline and the mountains are being pinned to.
    points = [{"id": m["id"], "x": m["x"], "y": m["y"]}
              for m in report["matched"]]
    terrain = terrain_alignment(settlements, points)
    anchored = terrain["anchored"]
    lines.append(
        f"\nTerrain: {len(anchored)} of {terrain['landmarks']} named features "
        f"pinned to the survey, {len(terrain['rejected'])} rejected as too far "
        f"out, {len(terrain['unsurveyed'])} not in the survey"
    )
    if anchored:
        lines.append(table(
            [[a["name"], a["survey"], a["drift"]] for a in
             sorted(anchored, key=lambda a: -a["drift"])[:args.limit]],
            ["Feature", "Survey name", "Shifted"], aligns="llr"))
    if terrain["rejected"]:
        lines.append("Rejected (kept where they were): "
                     + ", ".join(r["name"] for r in terrain["rejected"]))

    if args.apply:
        save_control_points(points)
        # Re-apply against the live gazetteer so this process agrees with the
        # next one; the map and prices both read these coordinates.
        applied = apply_calibration(settlements)
        world.rebuild()
        lines.append(f"\nSaved {applied} control points and rebuilt the world. "
                     "Restart any running server to pick them up.")
    else:
        lines.append("\nNothing was changed. Re-run with --apply to move the "
                     "markets.")

    emit({
        "available": True,
        "path": report["path"],
        "anchor": report["anchor"],
        "matched": report["matched"],
        "missing": report["missing"],
        "unused": report["unused"],
        "count": report["count"],
        "surveyed": report["surveyed"],
        "terrain": terrain,
        "applied": bool(args.apply),
    }, "\n".join(lines), args.json)


def cmd_generate_buildings(args: argparse.Namespace) -> None:
    payload = generate_buildings(
        args.ward, count=args.count, seed=args.seed if args.seed is not None else 1357,
        building_class=args.building_class, footprint_sqft=args.footprint_sqft,
        scenario=args.scenario,
    )
    _emit_generated_buildings(args, payload, "Generated Waterdeep buildings - not surveyed or canonical")


def cmd_generate_location(args: argparse.Namespace) -> None:
    payload = generate_location(
        args.location, profile=args.profile, count=args.count,
        seed=args.seed if args.seed is not None else 1357,
        footprint_sqft=args.footprint_sqft, scenario=args.scenario,
        class_b_weight=args.class_b_weight, class_c_weight=args.class_c_weight,
        class_d_weight=args.class_d_weight, condition_modifier=args.condition_modifier,
    )
    _emit_generated_buildings(
        args, payload, f"Generated {payload['location']['name']} ({payload['profile']['name']}) - not surveyed or canonical",
    )


def _emit_generated_buildings(args: argparse.Namespace, payload: dict, title: str) -> None:
    rows = []
    for row in payload["buildings"]:
        occupants = row["occupants"]
        rows.append([
            row["label"], row["building_class"] or "?",
            row["structure"]["stories"] if row["structure"] else "?",
            row["condition"] or "Unresolved", row["use"]["label"] if row["use"] else "?",
            occupants["residents"] if occupants else "?",
            occupants["lodging_guests"] if occupants else "?",
            occupants["staff"] if occupants else "?",
        ])
    text = "\n".join([
        heading(title),
        payload["source"]["era_note"],
        *([f"Assumed profile: {payload['profile']['class_weights']}; condition modifier "
           f"{payload['profile']['condition_modifier']:+d}."] if "profile" in payload else []),
        table(rows, ["Building", "Class", "Stories", "Condition", "Use", "Residents", "Guests", "Staff"]),
        "Residents/guests/staff are assumptions; staff may also be residents.",
        "No names, measured coordinates or population changes. Source: printed pp. 10-11 / PDF pp. 11-12.",
        *payload["assumptions"],
    ])
    emit(payload, text, args.json)


def cmd_city_directory(args: argparse.Namespace) -> None:
    payload = city_directory(
        args.settlement, search=args.search, ward=args.ward,
        kind=args.kind, category=args.category,
    )
    rows = [
        [b["name"], b["ward"], b["category"],
         "; ".join(f'{p["name"]} ({p["role"]})' for p in b["people"]),
         ", ".join(f'{c["printed_page"]} (PDF {c["pdf_page"]})' for c in b["citations"])]
        for b in payload["businesses"]
    ]
    rows.extend([
        p["name"], ", ".join(p["wards"]), "person",
        "; ".join(f'{a["business_name"]} ({a["role"]})' for a in p["affiliations"]),
        ", ".join(f'{c["printed_page"]} (PDF {c["pdf_page"]})' for c in p["citations"]),
    ] for p in payload["people"])
    text = "\n".join([
        heading(payload["name"]), payload["source"]["era_note"],
        payload["scope_note"],
        table(rows, ["Name", "Ward / affiliation", "Type", "People / businesses", "Pages"]),
        f'{payload["counts"]["businesses"]} businesses; {payload["counts"]["people"]} people',
    ])
    emit(payload, text, args.json)


def cmd_calendar(args: argparse.Namespace, world: World) -> None:
    rows = [[i + 1, m[0], m[1], m[2]] for i, m in enumerate(MONTHS)]
    text = (heading(f"Calendar of Harptos - today is {world.date}")
            + "\n" + table(rows, ["#", "Month", "Common name", "Season"],
                           aligns="rlll"))
    emit({"date": str(world.date), "season": world.date.season,
          "months": [{"number": i + 1, "name": m[0], "common": m[1],
                      "season": m[2]} for i, m in enumerate(MONTHS)]},
         text, args.json)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="faerun",
        description="Commodity prices across the Forgotten Realms, "
                    "adjusted for supply, demand, distance, tariffs, "
                    "season and world events.",
    )
    p.add_argument("--json", action="store_true", help="emit raw JSON")
    p.add_argument("--year", type=int, help="Dale Reckoning year (default 1492)")
    p.add_argument("--month", help="Harptos month name or number")
    p.add_argument("--seed", type=int, help="reroll the market wobble")
    p.add_argument("--seasonal-inventory", action=argparse.BooleanOptionalAction, default=None,
                   help="opt into daily stored-inventory replay (cold history can take many minutes)")
    p.add_argument("--event", action="append", metavar="TEMPLATE@PLACE",
                   help="apply an event, e.g. siege@Baldur's Gate or "
                        "drought@region:Amn (repeatable)")
    sub = p.add_subparsers(dest="command", required=True)

    generated = sub.add_parser("generate-buildings", help="generate noncanonical City System building scenarios")
    generated.add_argument("--ward", default="Trades Ward")
    generated.add_argument("--count", type=int, default=20)
    generated.add_argument("--building-class", choices=["B", "C", "D"])
    generated.add_argument("--footprint-sqft", type=float, default=1000)
    generated.add_argument("--scenario", choices=["low", "central", "high"], default="central")
    generated.set_defaults(func=cmd_generate_buildings)

    location_gen = sub.add_parser("generate-location", help="generate noncanonical buildings for any named location")
    location_gen.add_argument("location")
    location_gen.add_argument("--profile", choices=[p["id"] for p in location_profiles()["profiles"]], default="town")
    location_gen.add_argument("--count", type=int, default=20)
    location_gen.add_argument("--footprint-sqft", type=float, default=1000)
    location_gen.add_argument("--scenario", choices=["low", "central", "high"], default="central")
    location_gen.add_argument("--class-b-weight", type=int, help="optional B percentage; supply B, C and D together, summing to 100")
    location_gen.add_argument("--class-c-weight", type=int)
    location_gen.add_argument("--class-d-weight", type=int)
    location_gen.add_argument("--condition-modifier", type=int, choices=[-1, 0, 1])
    location_gen.set_defaults(func=cmd_generate_location)

    directory = sub.add_parser("city-directory", help="source-linked historical businesses and people")
    directory.add_argument("settlement", nargs="?", default="Waterdeep")
    directory.add_argument("--search", default="")
    directory.add_argument("--ward", default="")
    directory.add_argument("--kind", choices=["all", "business", "person"], default="all")
    directory.add_argument("--category", default="")
    directory.set_defaults(func=cmd_city_directory)

    m = sub.add_parser("market", help="every price in one settlement")
    m.add_argument("settlement")
    m.add_argument("--category")
    m.add_argument("--sort", default="category",
                   choices=["category", "price", "multiplier"])
    m.set_defaults(func=cmd_market)

    q = sub.add_parser("price", help="one good in one settlement")
    q.add_argument("settlement")
    q.add_argument("commodity")
    q.add_argument("--quantity", type=int, default=1)
    q.set_defaults(func=cmd_price)

    c = sub.add_parser("compare", help="one good across many markets")
    c.add_argument("commodity")
    c.add_argument("--region")
    c.add_argument("--limit", type=int, default=20)
    c.add_argument("--dearest", action="store_true",
                   help="list the most expensive markets first")
    c.set_defaults(func=cmd_compare)

    r = sub.add_parser("route", help="trade road between two markets")
    r.add_argument("origin")
    r.add_argument("destination")
    r.add_argument("--optimise", default="days", choices=["days", "cost"])
    r.set_defaults(func=cmd_route)

    a = sub.add_parser("arbitrage", help="what to buy here and sell elsewhere")
    a.add_argument("origin")
    a.add_argument("--max-days", type=float, default=45.0)
    a.add_argument("--cargo", type=float, default=2000.0,
                   help="load size in pounds")
    a.add_argument("--category")
    a.add_argument("--limit", type=int, default=15)
    a.set_defaults(func=cmd_arbitrage)

    h = sub.add_parser("history", help="a year of prices, month by month")
    h.add_argument("settlement")
    h.add_argument("commodity")
    h.add_argument("--months", type=int, default=12)
    h.set_defaults(func=cmd_history)

    t = sub.add_parser("trade", help="what a market exports and imports")
    t.add_argument("settlement")
    t.add_argument("--top", type=int, default=10)
    t.set_defaults(func=cmd_trade)

    s = sub.add_parser("settlements", help="list markets")
    s.add_argument("--region")
    s.add_argument("--search")
    s.set_defaults(func=cmd_settlements)

    g = sub.add_parser("commodities", help="list goods")
    g.add_argument("--category")
    g.add_argument("--search")
    g.set_defaults(func=cmd_commodities)

    sub.add_parser("regions", help="list regions").set_defaults(func=cmd_regions)

    e = sub.add_parser("events", help="show or clear world events")
    e.add_argument("--clear", action="store_true")
    e.set_defaults(func=cmd_events)

    n = sub.add_parser("chronicle",
                       help="the standing history, in full or for one place")
    n.add_argument("settlement", nargs="?", help="omit for a world summary")
    n.set_defaults(func=cmd_chronicle)

    tl = sub.add_parser("timeline",
                        help="a basket of goods priced through the chronicle")
    tl.add_argument("settlement")
    tl.add_argument("--commodity", action="append",
                    help="price this good instead of the default basket")
    tl.add_argument("--size", type=int, default=6,
                    help="how many goods in the default basket")
    # Deliberately not "--year": a subparser option of that name would be
    # merged back over the top-level --year and silently reset the world date.
    tl.add_argument("--only-year", type=int, dest="only_year",
                    help="show only this year of the window")
    tl.set_defaults(func=cmd_timeline)

    at = sub.add_parser("atlas",
                        help="realign markets from a surveyed poster map")
    at.add_argument("--file", default=None,
                    help="path to the survey (default: maps/locations.json)")
    at.add_argument("--anchor", default=None,
                    help="town the survey measures from (default: its own)")
    at.add_argument("--apply", action="store_true",
                    help="write the alignment instead of only previewing it")
    at.add_argument("--limit", type=int, default=30,
                    help="how many moves to list (default: 30)")
    at.set_defaults(func=cmd_atlas)

    sub.add_parser("calendar", help="the Calendar of Harptos").set_defaults(
        func=cmd_calendar)

    v = sub.add_parser("serve", help="browse the market board in a web UI")
    v.add_argument("--host", default="127.0.0.1")
    v.add_argument("--port", type=int, default=8765,
                   help="port to listen on (0 picks a free one)")
    v.add_argument("--no-browser", action="store_true",
                   help="do not open a browser window")
    v.add_argument("--verbose", action="store_true",
                   help="log every request")
    v.add_argument("--underlay", default="", metavar="PATH",
                   help="your own poster map image to overlay on the world map")
    v.set_defaults(func=cmd_serve, page="")

    loc = sub.add_parser("location",
                         help="open the location detail screen in a web UI")
    loc.add_argument("settlement", nargs="?")
    loc.add_argument("--host", default="127.0.0.1")
    loc.add_argument("--port", type=int, default=8765,
                     help="port to listen on (0 picks a free one)")
    loc.add_argument("--no-browser", action="store_true",
                     help="do not open a browser window")
    loc.add_argument("--verbose", action="store_true",
                     help="log every request")
    loc.add_argument("--underlay", default="", metavar="PATH",
                     help="your own poster map image to overlay on the world map")
    loc.set_defaults(func=cmd_location, page="location.html")

    w = sub.add_parser("map", help="open the 3D world map in a web UI")
    w.add_argument("--host", default="127.0.0.1")
    w.add_argument("--port", type=int, default=8765,
                   help="port to listen on (0 picks a free one)")
    w.add_argument("--no-browser", action="store_true",
                   help="do not open a browser window")
    w.add_argument("--verbose", action="store_true",
                   help="log every request")
    w.add_argument("--underlay", default="", metavar="PATH",
                   help="your own poster map image to overlay on the world map")
    w.set_defaults(func=cmd_map, page="map.html")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command in {"city-directory", "generate-buildings", "generate-location"}:
            args.func(args)
        else:
            world = build_world(args)
            args.func(args, world)
    except KeyError as exc:
        print(f"not found: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
