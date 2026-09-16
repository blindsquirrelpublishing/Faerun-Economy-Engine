"""One-shot smoke test: run `python verify.py` from the project root.

Exercises every public entry point (imports, engine API, CLI subcommands and
the MCP tool surface) and prints a pass/fail line for each. Exits non-zero if
anything failed, so it also works as a CI gate.
"""

from __future__ import annotations

import io
import sys
import traceback
from contextlib import redirect_stdout

RESULTS: list[tuple[str, bool, str]] = []


def check(label):
    def wrap(fn):
        try:
            with redirect_stdout(io.StringIO()):
                fn()
            RESULTS.append((label, True, ""))
        # SystemExit is caught deliberately: argparse calls sys.exit() on a bad
        # command line, and without this one malformed invocation would kill the
        # whole run instead of failing a single check and printing the report.
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - reporting layer
            detail = "".join(traceback.format_exception_only(type(exc), exc)).strip()
            RESULTS.append((label, False, detail))
        return fn

    return wrap


# --------------------------------------------------------------------------
# imports
# --------------------------------------------------------------------------


@check("import faerun")
def _imports():
    import faerun  # noqa: F401
    import faerun.cli  # noqa: F401
    import faerun.economy  # noqa: F401
    import faerun.events  # noqa: F401
    import faerun.world  # noqa: F401


@check("world loads")
def _world():
    from faerun import get_world

    w = get_world()
    assert len(w.settlements) > 100, len(w.settlements)
    assert len(w.commodities) > 100, len(w.commodities)


@check("settlement goods reference real commodities")
def _settlement_goods():
    from faerun import get_world

    w = get_world()
    bad = []
    for s in w.settlements.values():
        for cid in list(s.specialties) + list(s.shortages):
            if cid not in w.commodities:
                bad.append(f"{s.name} -> {cid!r}")
    assert not bad, "unknown goods: " + ", ".join(bad)


@check("trade routes name real travel modes")
def _route_modes():
    """A typo in a route `kind` would silently degrade the leg to a road.

    `parse_modes` drops names it does not recognise rather than raising, so
    world construction survives a bad gazetteer entry -- which means nothing
    else will ever tell us about it. This is that check.
    """
    from faerun.data.routes import NAMED_ROUTES, NAMED_SEA_LANES
    from faerun.world import MODES

    bad = []

    def _inspect(label, kind):
        for part in str(kind).split("+"):
            if part.strip().lower() not in MODES:
                bad.append(f"{label} -> {kind!r}")

    for name, _stops, _quality, kind in NAMED_ROUTES:
        _inspect(name, kind)
    for lane in NAMED_SEA_LANES:
        if len(lane) > 3:
            _inspect(lane[0], lane[3])
    assert not bad, "unknown travel modes: " + ", ".join(bad)


@check("multimodal routes cost and risk more")
def _multimodal_penalty():
    from faerun.world import MODES, mode_profile

    freight, speed, hazard = mode_profile(("river", "portage"))
    assert freight > (MODES["river"][0] + MODES["portage"][0]) / 2
    assert speed < MODES["river"][1]
    assert hazard > MODES["portage"][2]


# --------------------------------------------------------------------------
# engine API
# --------------------------------------------------------------------------


@check("price_for")
def _price_for():
    from faerun import get_world, price_for

    w = get_world()
    q = price_for("Waterdeep", "grain", world=w)
    assert q.price > 0
    assert q.buy_price <= q.price
    bulk = price_for("Waterdeep", "grain", world=w, quantity=500)
    assert bulk.price > 0


@check("market_report")
def _market_report():
    from faerun import get_world, market_report

    r = market_report("Baldur's Gate", world=get_world())
    assert r["prices"], "no prices returned"
    assert r["settlement"] == "Baldur's Gate"


@check("compare_prices")
def _compare():
    from faerun import compare_prices, get_world

    r = compare_prices("mithral_ingot", world=get_world(), limit=5)
    assert len(r["markets"]) == 5


@check("find_arbitrage")
def _arb():
    from faerun import find_arbitrage, get_world

    r = find_arbitrage("Waterdeep", world=get_world(), max_days=30, limit=5)
    assert "deals" in r


@check("price_history")
def _history():
    from faerun import get_world, price_history

    w = get_world()
    before = str(w.date)
    r = price_history("Bryn Shander", "grain", world=w, months=12)
    assert len(r["series"]) == 12
    assert str(w.date) == before, "price_history leaked the world date"


@check("trade_summary")
def _trade():
    from faerun import get_world, trade_summary

    r = trade_summary("Calimport", world=get_world(), top=5)
    assert len(r["exports"]) == 5 and len(r["imports"]) == 5


@check("routing")
def _route():
    from faerun import get_world

    r = get_world().route("Waterdeep", "Calimport")
    assert r["reachable"] and r["legs"], r
    assert r["freight_gp_per_100lb"] > 0


@check("events shift prices")
def _events():
    from faerun import World, apply_event, price_for

    w = World()
    before = price_for("Neverwinter", "grain", world=w).price
    apply_event(world=w, template="siege", settlements=["Neverwinter"])
    after = price_for("Neverwinter", "grain", world=w).price
    assert after > before, f"{before} -> {after}"


@check("the chronicle is installed by default")
def _chronicle():
    from faerun import World, get_world
    from faerun.chronicle import (
        chronicle_months,
        chronicle_summary,
        chronicle_window,
        is_chronicle_event,
        settlement_timeline,
    )

    w = get_world()
    summary = chronicle_summary(w)
    assert summary["events"] > 100, f"only {summary['events']} events of history"
    assert summary["months"] == chronicle_months() == 84, summary["months"]

    first, last = chronicle_window()
    for event in w.events.values():
        if not is_chronicle_event(event) or event.start_month is None:
            continue
        assert first <= event.start_month <= last, f"{event.id} starts outside the window"

    story = settlement_timeline("Waterdeep", world=w)
    assert story["events"], "Waterdeep has no history at all"

    # A bare World() must stay clean, so the existing test suite is unaffected.
    assert not any(is_chronicle_event(e) for e in World().events.values())


@check("the timeline and detail read back")
def _location():
    from faerun import get_world
    from faerun.chronicle import chronicle_months
    from faerun.location import location_detail, location_timeline

    w = get_world()
    before = w.date
    data = location_timeline("Neverwinter", world=w, commodities=["grain"])
    assert len(data["series"]) == chronicle_months(), len(data["series"])
    assert w.date == before, "the timeline left the calendar moved"
    assert data["analysis"]["dearest"]["index"] >= data["analysis"]["cheapest"]["index"]

    detail = location_detail("Neverwinter", world=w)
    assert detail["market"]["prices"], "no prices at all"
    assert detail["quiet"], "no quiet-world control prices"
    assert w.date == before, "the detail left the calendar moved"

    # The scrubber is worthless if the month does not reach the prices.
    first, last = data["series"][0]["month"], data["series"][-1]["month"]
    category = w.find_commodity("grain").category
    early = location_detail("Neverwinter", world=w, month=first,
                            category=category)
    late = location_detail("Neverwinter", world=w, month=last,
                           category=category)
    assert early["label"] != late["label"], "the month did not reach the label"
    was = {q["commodity"]: q["price"] for q in early["market"]["prices"]}
    now = {q["commodity"]: q["price"] for q in late["market"]["prices"]}
    moved = sum(1 for cid, price in now.items() if was.get(cid) != price)
    assert moved > len(was) / 2, f"only {moved} of {len(was)} goods moved"

    # ...and scrubbing back has to be free, or the table lags the slider.
    assert location_detail("Neverwinter", world=w, month=first,
                           category=category) is early, "detail cache missed"


@check("the poster-map overlay")
def _underlay():
    from faerun.mapassets import MAP_ASSETS
    from faerun.underlay import underlay_info
    from faerun.web import GET_ROUTES, api_underlay

    assert GET_ROUTES.get("/api/underlay") is api_underlay, "route not wired"

    info = underlay_info()
    # Whether an image is actually on this machine is the user's business; the
    # shape of the answer is not, because the page reads it either way.
    for key in ("available", "url", "name", "path", "mime", "bytes",
                "searched", "env_var"):
        assert key in info, key
    assert info["searched"], "no search folders reported"
    if info["available"]:
        print(f"      found a poster map: {info['name']}")
    else:
        print("      no poster map found (the overlay control stays hidden)")

    js = MAP_ASSETS["map.js"][0]
    for marker in ("drawUnderlay", "loadUnderlay", "/api/underlay"):
        assert marker in js, marker
    assert js.index("drawUnderlay();") < js.index("drawPins();"), \
        "the poster would cover the settlement dots"

    for name in ("map.html", "map.css", "map.js"):
        body = MAP_ASSETS[name][0]
        assert body.isascii(), f"{name} is no longer plain ASCII"
        assert "\\" not in body, f"{name} grew a backslash"


@check("map realignment")
def _calibration():
    from faerun.calibration import (
        apply_calibration,
        base_coordinates,
        build_warp,
        load_control_points,
    )
    from faerun.mapassets import MAP_ASSETS
    from faerun.web import GET_ROUTES, POST_ROUTES, api_calibration, post_calibrate

    assert GET_ROUTES.get("/api/calibration") is api_calibration, "read route not wired"
    assert POST_ROUTES.get("/api/calibrate") is post_calibrate, "save route not wired"

    # The warp has to land exactly on the points the user placed, or the dot
    # will not go where they clicked and the tool feels broken.
    pairs = [((0.0, 0.0), (5.0, -5.0)), ((100.0, 0.0), (140.0, 10.0)),
             ((0.0, 100.0), (-20.0, 90.0)), ((100.0, 100.0), (130.0, 160.0))]
    warp = build_warp(pairs)
    for src, dst in pairs:
        got = warp(*src)
        assert abs(got[0] - dst[0]) < 1e-5 and abs(got[1] - dst[1]) < 1e-5, src

    class _T:
        def __init__(self, sid, x, y):
            self.id, self.x, self.y = sid, x, y

    towns = [_T("a", 0.0, 0.0), _T("b", 100.0, 0.0), _T("c", 0.0, 100.0)]
    shipped = base_coordinates(towns)
    apply_calibration(towns, [{"id": "b", "x": 300.0, "y": 0.0}])
    assert towns[1].x == 300.0, "control point did not move"
    apply_calibration(towns, [])
    assert all(shipped[t.id] == (t.x, t.y) for t in towns), \
        "clearing the calibration did not restore the shipped coordinates"

    saved = load_control_points()
    if saved:
        print(f"      calibrated against {len(saved)} hand-placed markets")
    else:
        print("      no saved calibration (markets sit where they shipped)")

    js = MAP_ASSETS["map.js"][0]
    for marker in ("applyCalibration", "groundPoint", "rebuildRouteGeometry",
                   "updateCalibHud", "wireCalibration", "/api/calibrate"):
        assert marker in js, marker


@check("survey-driven realignment")
def _atlas():
    from faerun import atlas
    from faerun.data.settlements import SETTLEMENTS
    from faerun.mapassets import MAP_ASSETS
    from faerun.web import GET_ROUTES, POST_ROUTES, api_atlas, post_atlas_apply

    assert GET_ROUTES.get("/api/atlas") is api_atlas, "preview route not wired"
    assert POST_ROUTES.get("/api/atlas/apply") is post_atlas_apply, \
        "apply route not wired"

    info = atlas.atlas_info()
    for key in ("available", "error", "searched"):
        assert key in info, key
    assert info["searched"], "no search folders reported"

    if not info["available"]:
        print("      no survey file found (the Align control stays hidden)")
    else:
        report = atlas.align(list(SETTLEMENTS))
        print(f"      {report['count']} of {len(SETTLEMENTS)} markets found in "
              f"{info['count']} surveyed places")
        assert report["count"] > 0, "the survey matched no markets at all"
        # The anchor is the one town whose position is taken on trust; if it
        # moved, every other distance would be measured from the wrong place.
        anchor = next((m for m in report["matched"]
                       if m["name"] == report["anchor"]), None)
        assert anchor is not None, \
            f"the anchor {report['anchor']!r} is not among the matched markets"
        assert anchor["moved"] < 0.05, "the anchor town drifted"
        if report["missing"]:
            print(f"      {len(report['missing'])} not surveyed, left in place")

    js = MAP_ASSETS["map.js"][0]
    for marker in ("loadAtlas", "applyAtlas", "/api/atlas"):
        assert marker in js, marker


@check("the map frame grows to fit the poster and a realignment")
def _frame():
    from faerun import mapdata
    from faerun.data.settlements import SETTLEMENTS

    class _T:
        def __init__(self, x, y):
            self.x, self.y = x, y

    towns = list(SETTLEMENTS)
    poster = mapdata.poster_frame(towns)

    # Uncalibrated the markets never move the frame, so what is left is the
    # poster - or, without one, exactly the frame the terrain was drawn for.
    mapdata._resolve_frame(towns, False)
    if poster is None:
        print("      no poster surveyed (the frame stays as shipped)")
        assert mapdata.BOUNDS == mapdata.SHIPPED_BOUNDS, "shipped frame changed"
        assert (mapdata.GRID_W, mapdata.GRID_H) == \
            (mapdata.SHIPPED_GRID_W, mapdata.SHIPPED_GRID_H)
    else:
        # The poster's whole footprint has to have ground under it, or three
        # quarters of the image hangs off the eastern edge over nothing.
        west, north, east, south = mapdata.BOUNDS
        assert west <= poster[0] and north <= poster[1], "frame misses the poster"
        assert east >= poster[2] and south >= poster[3], "frame misses the poster"
        assert west <= mapdata.SHIPPED_BOUNDS[0], "frame shrank west"
        assert south >= mapdata.SHIPPED_BOUNDS[3], "frame shrank south"
        cw = (east - west) / mapdata.GRID_W
        ch = (south - north) / mapdata.GRID_H
        print(f"      frame {east - west:.0f} x {south - north:.0f} miles "
              f"in {mapdata.GRID_W} x {mapdata.GRID_H} cells "
              f"of {cw:.1f} x {ch:.1f} miles")
        # Oblong cells smear the coastline in one direction only, which is
        # exactly what capping each axis on its own used to cause.
        assert abs(cw - ch) < 0.1 * max(cw, ch), "grid cells went oblong"
        assert mapdata.GRID_W * mapdata.GRID_H <= mapdata.MAX_CELLS, \
            "the heightfield ran away"

    # A survey reaches far further east than the hand-placed gazetteer did, so
    # the frame has to grow or those markets fall off the map.
    mapdata._resolve_frame([_T(4200.0, 1200.0)], True)
    assert mapdata.BOUNDS[2] >= 4200.0 + mapdata.FRAME_MARGIN, "frame too narrow"
    assert mapdata.BOUNDS[0] <= mapdata.SHIPPED_BOUNDS[0], "frame shrank west"
    assert mapdata.GRID_W > mapdata.SHIPPED_GRID_W, "grid did not follow"
    assert mapdata.GRID_W <= mapdata.MAX_GRID_W, "grid ran away"

    # Leave the module in the state a page load would put it in.
    mapdata._resolve_frame(towns, False)


@check("every surveyed town has commodity prices")
def _surveyed_prices():
    from faerun import atlas, get_world
    from faerun.data.settlements import SETTLEMENTS
    from faerun.economy import _commodity_markets
    from faerun.models import slugify
    from faerun.world import SURVEYED_MARKET_TRAIT

    surveyed = atlas.surveyed_places(list(SETTLEMENTS))
    if not surveyed:
        print("      no additional surveyed towns to enrich")
        return

    world = get_world()
    expected = {slugify(str(place["name"])) for place in surveyed}
    missing = expected - set(world.settlements)
    assert not missing, "surveyed markets missing: " + ", ".join(sorted(missing))

    good = next(iter(world.commodities.values()))
    quotes = _commodity_markets(world, good)
    unpriced = [sid for sid in expected if sid not in quotes]
    assert not unpriced, "surveyed markets without prices: " + \
        ", ".join(sorted(unpriced))
    assert all(world.settlements[sid].has_trait(SURVEYED_MARKET_TRAIT)
               for sid in expected), "surveyed market marker missing"
    print(f"      {len(expected)} surveyed local markets price "
          f"{len(world.commodities)} commodities each")


@check("the map rebuilds its terrain from the survey")
def _terrain():
    from faerun import mapdata
    from faerun.calibration import build_warp
    from faerun.data.settlements import SETTLEMENTS

    marks = mapdata.terrain_landmarks()
    assert marks, "the map has no named terrain to pin"
    names = [n for n, _p in marks]
    assert "Faerun" not in names, "the continent is not a landmark"

    # Pinning the scenery must never nudge a market: prices are computed from
    # the distances between them, so a town that drifts is a price that drifts.
    towns = list(SETTLEMENTS)[:12]
    pairs = [((t.x, t.y), (t.x + 40.0, t.y - 25.0)) for t in towns]
    # A landmark sitting exactly on a town would be the same control point
    # pulled two ways, which is a contrived clash rather than a real failure.
    far = [p for _n, p in marks
           if all(abs(p[0] - t.x) + abs(p[1] - t.y) > 5.0 for t in towns)]
    scenery = [(p, (p[0] + 90.0, p[1] + 30.0)) for p in far[:4]]
    warp = build_warp(pairs + scenery)
    for t in towns:
        x, y = warp(t.x, t.y)
        assert abs(x - (t.x + 40.0)) < 0.5 and abs(y - (t.y - 25.0)) < 0.5, \
            f"{t.name} moved when the scenery was pinned"

    # The report is what the CLI and the map screen both read, so it has to
    # come back whole even when there is no survey to read.
    report = mapdata.terrain_alignment(list(SETTLEMENTS))
    assert "error" not in report, report.get("error")
    for key in ("landmarks", "anchored", "rejected", "unsurveyed", "limit"):
        assert key in report, f"terrain report is missing {key}"
    seen = (len(report["anchored"]) + len(report["rejected"])
            + len(report["unsurveyed"]))
    assert seen == report["landmarks"], \
        "every landmark should be pinned, rejected or unsurveyed"


@check("the poster is placed from the survey, and its towns are drawn")
def _poster():
    from faerun import atlas, mapdata
    from faerun.data.settlements import SETTLEMENTS
    from faerun.mapassets import MAP_ASSETS

    towns = list(SETTLEMENTS)

    # The overlay must answer in a fixed shape whether or not a survey exists,
    # because the map screen reads it unconditionally and a missing key there
    # is a blank page rather than a missing overlay.
    fit = atlas.underlay_placement(towns)
    for key in ("available", "error"):
        assert key in fit, f"underlay placement is missing {key}"
    if fit["available"]:
        for key in ("x", "y", "widthMiles", "heightMiles", "anchor"):
            assert key in fit, f"underlay placement is missing {key}"
        assert fit["widthMiles"] > 0 and fit["heightMiles"] > 0, \
            "the poster was placed with no size"
        # The anchor pixel has to land on the anchor town or nothing else will.
        mpp_x = fit["widthMiles"] / fit["imageWidth"]
        mpp_y = fit["heightMiles"] / fit["imageHeight"]
        anchor = next((t for t in towns if t.name == fit["anchor"]), None)
        assert anchor is not None, "the placement named an unknown anchor"
        px, py = atlas.load_atlas()["origin_px"]
        ax = fit["x"] + px * mpp_x
        ay = fit["y"] + py * mpp_y
        base = getattr(anchor, "_base_xy", (anchor.x, anchor.y))
        assert abs(ax - base[0]) < 2.0 and abs(ay - base[1]) < 2.0, \
            f"the poster's {fit['anchor']} lands at ({ax:.0f}, {ay:.0f})"

    # The surveyed towns must never shadow a market that has real prices.
    extra = mapdata.surveyed_places(towns)
    known = {t.name for t in towns}
    for p in extra:
        assert p["name"] not in known, f"{p['name']} is already a market"

    js = MAP_ASSETS["map.js"][0]
    for marker in ("surveyUnderlayFit", "buildPlaces", "drawPlaces",
                   "opt-places"):
        assert marker in js, marker


@check("every good priced in every market")
def _coverage():
    from faerun import get_world
    from faerun.economy import _commodity_markets

    w = get_world()
    missing = 0
    for c in w.commodities.values():
        markets = _commodity_markets(w, c)
        missing += sum(1 for q in markets.values() if q.price <= 0)
    assert missing == 0, f"{missing} unpriced entries"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


@check("CLI subcommands")
def _cli():
    from faerun.cli import main

    invocations = [
        ["market", "Waterdeep"],
        # --json, --year, --month, --seed and --event belong to the top-level
        # parser, so they go before the subcommand, not after it.
        ["--json", "market", "Waterdeep"],
        ["price", "Baldur's Gate", "iron_ingot"],
        ["compare", "grain", "--limit", "5"],
        ["route", "Waterdeep", "Calimport"],
        # also as JSON, so the mode fields go through the serialiser
        ["--json", "route", "Waterdeep", "Calimport"],
        ["arbitrage", "Waterdeep", "--max-days", "30", "--limit", "5"],
        ["history", "Bryn Shander", "grain", "--months", "6"],
        ["trade", "Calimport"],
        ["settlements", "--region", "Sword Coast"],
        ["commodities", "--search", "iron"],
        ["regions"],
        ["events"],
        ["chronicle"],
        ["chronicle", "Waterdeep"],
        ["--json", "chronicle", "Waterdeep"],
        ["timeline", "Neverwinter", "--commodity", "grain",
         "--only-year", "1492"],
        ["calendar"],
        # Preview only: without --apply this must not touch the gazetteer.
        ["atlas", "--limit", "5"],
        ["--json", "atlas"],
        ["--month", "Flamerule", "--seed", "7777", "market", "Silverymoon"],
        ["--event", "siege@Neverwinter", "market", "Neverwinter"],
    ]
    for argv in invocations:
        rc = main(argv)
        assert rc in (0, None), f"{argv} returned {rc}"


@check("CLI rejects bad input")
def _cli_errors():
    from faerun.cli import main

    for argv in (["price", "Waterdeep", "no_such_good"], ["market", "Nowhere Town"]):
        try:
            rc = main(argv)
        except SystemExit as exc:
            rc = exc.code
        assert rc not in (0, None), f"{argv} should have failed, got {rc}"


@check("CLI server subcommands parse")
def _cli_serve_parsing():
    """`serve` and `map` cannot be executed here - they block on a socket -
    so check the parser wiring instead, which is what actually breaks."""
    from faerun.cli import build_parser, cmd_serve, cmd_map, cmd_location

    parser = build_parser()
    for name, func, page in (("serve", cmd_serve, ""),
                             ("map", cmd_map, "map.html"),
                             ("location", cmd_location, "location.html")):
        args = parser.parse_args([name, "--port", "0", "--no-browser"])
        assert args.func is func, f"{name} dispatches to {args.func}"
        assert args.page == page, f"{name} page is {args.page!r}, expected {page!r}"
        assert args.port == 0 and args.no_browser is True
        assert args.host == "127.0.0.1"
        assert args.verbose is False

    # serve() must accept everything cmd_serve hands it, by keyword.
    import inspect

    from faerun.web import serve

    params = inspect.signature(serve).parameters
    for needed in ("host", "port", "open_browser", "verbose", "page"):
        assert needed in params, f"web.serve is missing {needed}"


# --------------------------------------------------------------------------
# MCP
# --------------------------------------------------------------------------


@check("MCP tools")
def _mcp():
    import asyncio

    try:
        from faerun.mcp_server import mcp
    except ModuleNotFoundError as exc:
        if "mcp" in str(exc):
            raise AssertionError(
                "the 'mcp' package is not installed - run: pip install \"mcp>=1.2\""
            ) from exc
        raise

    tools = asyncio.run(mcp.list_tools())
    names = {t.name for t in tools}
    assert len(names) == len(tools), "duplicate MCP tool names"
    for expected in ("get_price", "get_market_report", "compare_prices",
                     "get_trade_route",
                     "get_chronicle_summary", "get_settlement_history",
                     "get_settlement_timeline", "get_location_detail"):
        assert expected in names, f"missing tool {expected}; have {sorted(names)}"
    asyncio.run(mcp.call_tool("get_price", {"settlement": "Waterdeep", "commodity": "grain"}))


@check("web UI server")
def _web():
    import json as _json
    import threading
    import urllib.error
    import urllib.request
    from http.server import ThreadingHTTPServer

    from faerun.web import STATIC, Handler

    for name in ("index.html", "app.css", "app.js", "map.html", "map.css",
                 "map.js", "location.html", "location.css", "location.js"):
        assert name in STATIC, f"missing asset {name}"

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    httpd.verbose = False
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{port}"

        with urllib.request.urlopen(base + "/") as resp:
            assert resp.status == 200
            assert b"Faer" in resp.read()

        with urllib.request.urlopen(base + "/api/bootstrap") as resp:
            boot = _json.loads(resp.read())
        assert len(boot["settlements"]) > 100
        assert len(boot["commodities"]) > 100
        assert len(boot["months"]) == 12
        for s in boot["settlements"]:
            assert isinstance(s["x"], (int, float)), f"{s['id']} has no map x"
            assert isinstance(s["y"], (int, float)), f"{s['id']} has no map y"

        for name in ("/location.html", "/location.css", "/location.js"):
            with urllib.request.urlopen(base + name) as resp:
                assert resp.status == 200, name
                assert resp.read(), f"{name} served empty"

        with urllib.request.urlopen(base + "/api/chronicle") as resp:
            chron = _json.loads(resp.read())
        assert chron["events"] > 0, "the served world has no history"
        assert len(chron["labels"]) == chron["months"], "label/month mismatch"
        assert chron["labels"][0]["month"] <= chron["today"] <= chron["labels"][-1]["month"]

        with urllib.request.urlopen(
                base + "/api/location?settlement=waterdeep") as resp:
            detail = _json.loads(resp.read())
        assert detail["market"]["prices"], "no prices in the location detail"
        assert detail["quiet"], "no counterfactual prices"

        for name in ("/map.html", "/map.css", "/map.js"):
            with urllib.request.urlopen(base + name) as resp:
                assert resp.status == 200, name
                assert resp.read(), f"{name} served empty"

        with urllib.request.urlopen(base + "/api/map") as resp:
            payload = _json.loads(resp.read())
        gw, gh = payload["grid"]
        assert len(payload["terrain"]) == gw * gh, "terrain string is the wrong size"
        assert len(payload["height"]) == gw * gh, "height array is the wrong size"
        assert set(payload["terrain"]) <= set(payload["legend"]), "unknown terrain code"
        assert len(payload["settlements"]) == len(boot["settlements"])
        ids = {s["id"] for s in payload["settlements"]}
        for pin in payload["settlements"]:
            for field in ("x", "y", "z"):
                assert isinstance(pin[field], (int, float)), f"{pin['id']}.{field}"
            assert pin["z"] >= 0.0, f"{pin['id']} sits below sea level"
        assert payload["routes"], "no trade routes in the map payload"
        for leg in payload["routes"]:
            assert leg["a"] in ids and leg["b"] in ids, leg

        with urllib.request.urlopen(base + "/api/market?settlement=waterdeep") as resp:
            report = _json.loads(resp.read())
        assert report["prices"], "no prices in market report"

        req = urllib.request.Request(
            base + "/api/world",
            data=_json.dumps({"month": 1}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            assert _json.loads(resp.read())["month"] == 1

        # a bad settlement should be a clean 404, not a traceback
        try:
            urllib.request.urlopen(base + "/api/market?settlement=Nowhere+Town")
            raise AssertionError("expected 404 for unknown settlement")
        except urllib.error.HTTPError as exc:
            assert exc.code == 404, exc.code
    finally:
        httpd.shutdown()
        httpd.server_close()


def main() -> int:
    width = max(len(label) for label, _, _ in RESULTS)
    failures = 0
    for label, ok, detail in RESULTS:
        print(f"{label.ljust(width)}  {'ok' if ok else 'FAIL'}")
        if not ok:
            failures += 1
            print(f"{' ' * width}    {detail}")
    print()
    print(f"{len(RESULTS) - failures}/{len(RESULTS)} checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
