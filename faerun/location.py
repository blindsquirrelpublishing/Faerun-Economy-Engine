"""Everything the location detail screen needs: a timeline and an analysis.

The commodity board answers "what does this cost *now*".  This module answers
the more interesting question: "what has been happening to this town, and what
is it doing to the prices".  It walks the chronicle window month by month,
prices a small representative basket in each one, and then reads the resulting
series back as history -- which months were dear, which events bit hardest, and
what the running shocks are costing the townsfolk right now.

Two costs are worth knowing about:

* Pricing the whole 130-good catalogue in all 84 months would mean ~11,000
  market solutions.  The timeline therefore prices a **basket** of a half-dozen
  goods chosen for the settlement, which is enough to draw a cost-of-living
  line and cheap enough to serve from a web request.
* The "what are the events costing" figure needs a counterfactual, so
  `location_detail` prices the market twice: once as history has it, and once
  with the events lifted.  That is two full market passes -- the same cost as
  loading the board twice.  Two things take the sting out of it: a month with
  no events running anywhere skips the second pass entirely (it provably cannot
  differ), and finished payloads are memoised per world, so scrubbing
  back over a month already visited costs nothing.
"""

from __future__ import annotations

from collections import OrderedDict
from contextlib import contextmanager
from typing import Dict, Iterator, List, Optional, Sequence

from .chronicle import (
    chronicle_window,
    event_span,
    event_to_dict,
    _from_absolute,
    month_labels,
)
from .economy import _commodity_markets, market_report
from .lore import location_lore
from .models import Commodity, Settlement
from .world import World, get_world

#: Goods that nearly every market in the Realms trades, so a basket built from
#: them is comparable between settlements.  Ordered by how much a household
#: actually spends on them.
BASKET_STAPLES = (
    "grain", "bread", "ale", "salt", "cheese", "charcoal",
    "linen", "wool", "iron_ingot", "rope",
)

#: how many goods the timeline prices by default
BASKET_SIZE = 6


def _first_existing(world: World, ids: Sequence[str]) -> List[Commodity]:
    out = []
    for cid in ids:
        c = world.commodities.get(cid)
        if c is not None:
            out.append(c)
    return out


def basket_for(world: World, s: Settlement, size: int = BASKET_SIZE) -> List[Commodity]:
    """A representative shopping basket for one settlement.

    Staples first, so the cost-of-living line means the same thing everywhere,
    then whatever this town is short of -- because that is where its history
    shows up most sharply.
    """
    chosen: List[Commodity] = []
    seen = set()
    for c in _first_existing(world, BASKET_STAPLES):
        if len(chosen) >= max(1, size - 2):
            break
        chosen.append(c)
        seen.add(c.id)
    for cid in list(s.shortages) + list(s.specialties):
        if len(chosen) >= size:
            break
        c = world.commodities.get(cid)
        if c is not None and c.id not in seen:
            chosen.append(c)
            seen.add(c.id)
    if not chosen:
        chosen = list(world.commodities.values())[:size]
    return chosen[:size]


@contextmanager
def _at_month(world: World, stamp: int, day: int = 1) -> Iterator[None]:
    """Price as of an absolute month, then put the calendar back."""
    original = world.date
    world.date = _from_absolute(stamp).add_days(day - 1)
    try:
        yield
    finally:
        world.date = original


@contextmanager
def _without_events(world: World) -> Iterator[None]:
    """Lift every event, for a counterfactual "quiet world" price.

    The revision counter keys the price cache, so the quiet world needs a
    revision of its own or the cache would serve a haunted answer for a quiet
    world, or the reverse.  Two things matter here:

    * It must be *restored* on the way out, not bumped again.  Bumping would
      hand back a revision the cache has never seen, throwing away every entry
      the board and the timeline just paid for, on every single request.
    * It must be a number an ordinary mutation can never produce.  Revisions
      only ever count upwards from zero, so the mirror-image negative is free
      real estate: it can never collide, and it is the same number every time
      for a given state, so quiet prices stay cached between requests.
    """
    saved_events = world.events
    saved_revision = world.revision
    saved_inventory = getattr(world, "_inventory_history", None)
    world.events = {}
    world.revision = -(saved_revision + 1)
    try:
        yield
    finally:
        world.events = saved_events
        world.revision = saved_revision
        # The counterfactual has a separate stock ledger, not the active world's
        # next day. Keep its checkpoints on disk without evicting the live replay.
        if saved_inventory is None:
            world.__dict__.pop("_inventory_history", None)
        else:
            world._inventory_history = saved_inventory


# ---------------------------------------------------------------------------
# The timeline
# ---------------------------------------------------------------------------

def location_timeline(settlement, world: Optional[World] = None,
                      commodities: Optional[Sequence[str]] = None,
                      size: int = BASKET_SIZE) -> Dict:
    """Price a basket in every month of the chronicle window."""
    world = world or get_world()
    s = world.find_settlement(settlement)
    first, last = chronicle_window()

    if commodities:
        basket = [world.find_commodity(x) for x in commodities]
    else:
        basket = basket_for(world, s, size)

    # The index is a weighted average of each good's price relative to its own
    # base price, so goods of wildly different value contribute comparably.
    base_total = sum(c.base_price for c in basket) or 1.0

    rows: List[Dict] = []
    original = world.date
    try:
        for stamp in range(first, last + 1):
            world.date = _from_absolute(stamp)
            prices: Dict[str, float] = {}
            spend = 0.0
            for c in basket:
                quote = _commodity_markets(world, c)[s.id]
                prices[c.id] = quote.price
                spend += quote.price
            rows.append({
                "month": stamp,
                "prices": prices,
                "index": round(spend / base_total, 4),
                "basket_cost": round(spend, 2),
                "events": [e.id for e in world.events_for(s)],
            })
    finally:
        world.date = original

    labels = {row["month"]: row for row in month_labels()}
    for row in rows:
        label = labels.get(row["month"], {})
        row["label"] = label.get("label", str(row["month"]))
        row["short"] = label.get("short", str(row["month"]))
        row["year"] = label.get("year")
        row["season"] = label.get("season")

    events = [
        event_to_dict(e) for e in world.events.values()
        if e.applies_to_settlement(s) and _overlaps(e, first, last)
    ]
    events.sort(key=lambda r: (r["start_month"] is None, r["start_month"] or 0))

    return {
        "settlement": s.name,
        "settlement_id": s.id,
        "region": s.region,
        "first_month": first,
        "last_month": last,
        "basket": [{"id": c.id, "name": c.name, "unit": c.unit,
                    "base_price": c.base_price} for c in basket],
        "series": rows,
        "events": events,
        "analysis": analyse_timeline(rows, events),
    }


def _overlaps(event, first: int, last: int) -> bool:
    start, end = event_span(event)
    if start is not None and start > last:
        return False
    if end is not None and end < first:
        return False
    return True


# ---------------------------------------------------------------------------
# Reading the series back as history
# ---------------------------------------------------------------------------

def analyse_timeline(rows: Sequence[Dict], events: Sequence[Dict]) -> Dict:
    """Turn a month-by-month series into statements about the place."""
    if not rows:
        return {}

    values = [row["index"] for row in rows]
    mean = sum(values) / len(values)
    spread = max(values) - min(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)

    dearest = max(rows, key=lambda r: r["index"])
    cheapest = min(rows, key=lambda r: r["index"])

    # The sharpest month-on-month move, which is usually an event starting.
    jump = {"month": None, "change": 0.0}
    for previous, current in zip(rows, rows[1:]):
        if not previous["index"]:
            continue
        change = current["index"] / previous["index"] - 1.0
        if abs(change) > abs(jump["change"]):
            jump = {"month": current["month"], "label": current["label"],
                    "change": round(change, 4)}

    # What each event did to the basket, measured against the three quiet-ish
    # months before it began.  Events that start before the window has any
    # run-up are skipped rather than compared against nothing.
    by_month = {row["month"]: row for row in rows}
    impacts = []
    for event in events:
        start = event.get("start_month")
        end = event.get("end_month")
        if start is None:
            continue
        before = [by_month[m]["index"] for m in range(start - 3, start)
                  if m in by_month]
        during_last = end if end is not None else rows[-1]["month"]
        during = [by_month[m]["index"] for m in range(start, during_last + 1)
                  if m in by_month]
        if not before or not during:
            continue
        base = sum(before) / len(before)
        peak = sum(during) / len(during)
        if base <= 0:
            continue
        impacts.append({
            "id": event["id"],
            "name": event["name"],
            "kind": event["kind"],
            "start": event.get("start"),
            "change": round(peak / base - 1.0, 4),
        })
    impacts.sort(key=lambda r: -abs(r["change"]))

    return {
        "months": len(rows),
        "mean_index": round(mean, 4),
        "spread": round(spread, 4),
        "volatility": round(variance ** 0.5, 4),
        "dearest": {"month": dearest["month"], "label": dearest["label"],
                    "index": dearest["index"]},
        "cheapest": {"month": cheapest["month"], "label": cheapest["label"],
                     "index": cheapest["index"]},
        "sharpest_move": jump if jump["month"] is not None else None,
        "event_impact": impacts[:8],
        "quiet_months": sum(1 for row in rows if not row["events"]),
        "troubled_months": sum(1 for row in rows if row["events"]),
    }


# ---------------------------------------------------------------------------
# One month, in full
# ---------------------------------------------------------------------------

#: Finished `location_detail` payloads, keyed by everything that can change one.
#:
#: Roughly a year and a half of scrubbing held at once.  Each entry is small.
DETAIL_CACHE_LIMIT = 160


def _detail_cache(world: World) -> "OrderedDict[tuple, Dict]":
    """The memoised `location_detail` payloads belonging to one world.

    Scrubbing the timeline is the one place in the engine where a *human* drives
    the month, so the same handful of months get asked for over and over.  A
    detail payload costs two full market passes to build (~260 commodity solves)
    but is only a few hundred small dicts to keep, so caching the finished
    answer is far better value than leaning on the commodity cache underneath --
    that one is capped at 2,000 entries, which is barely seven months of detail
    views before it flushes itself and every month goes cold again.

    It hangs off the world rather than sitting in a module global, exactly as
    `_price_cache` does.  A global would have to key on the revision and the
    seed, and two separate worlds that merely *agree* on both would then read
    each other's answers -- which is easy to arrange by accident and miserable
    to debug.
    """
    cache = getattr(world, "_detail_cache", None)
    if cache is None:
        cache = OrderedDict()
        setattr(world, "_detail_cache", cache)
    return cache


def clear_detail_cache(world: Optional[World] = None) -> None:
    """Forget every memoised detail payload.  Exposed mostly for the tests."""
    _detail_cache(world or get_world()).clear()


def location_detail(settlement, world: Optional[World] = None,
                    month: Optional[int] = None,
                    category: Optional[str] = None,
                    movers: int = 12) -> Dict:
    """The full market at one month, and what the events are doing to it."""
    world = world or get_world()
    s = world.find_settlement(settlement)
    stamp = int(month) if month is not None else world.date.absolute_month()
    day = world.date.day if stamp == world.date.absolute_month() else 1

    # `revision` covers any event edit; `seed` covers a re-rolled world.  The
    # month is explicit, so a cache hit here is exact rather than approximate.
    cache = _detail_cache(world)
    trade_revision = ((str(world.trade_store.path), world.trade_store.revision)
                      if world.trade_store is not None else None)
    key = (s.id, stamp, day, category, movers, trade_revision) + world.economy_state_key(stamp)
    hit = cache.get(key)
    if hit is not None:
        cache.move_to_end(key)
        return hit

    with _at_month(world, stamp, day):
        report = market_report(s.id, world=world, category=category)
        from .materials import location_requirements

        requirements = location_requirements(s.id, world)
        active = [event_to_dict(e) for e in world.events_for(s)]
        if world.active_events():
            with _without_events(world):
                quiet_report = market_report(s.id, world=world,
                                             category=category)
        else:
            # Nothing is running anywhere in the Realms this month, so lifting
            # the events cannot change a single number -- not even through a
            # distant supplier.  Skipping the second pass halves the cost of a
            # quiet month outright.
            quiet_report = report

    # PriceQuote.commodity holds the id; commodity_name holds the display name.
    quiet = {q["commodity"]: q["price"] for q in quiet_report["prices"]}

    moves = []
    for row in report["prices"]:
        was = quiet.get(row["commodity"])
        if not was:
            continue
        change = row["price"] / was - 1.0
        if abs(change) < 0.005:
            continue
        moves.append({
            "commodity": row["commodity_name"],
            "commodity_id": row["commodity"],
            "unit": row["unit"],
            "price": row["price"],
            "quiet_price": round(was, 2),
            "change": round(change, 4),
        })
    moves.sort(key=lambda r: -abs(r["change"]))

    date = _from_absolute(stamp).add_days(day - 1)
    total_now = sum(q["price"] for q in report["prices"])
    total_quiet = sum(quiet.get(q["commodity"], q["price"])
                      for q in report["prices"]) or 1.0

    payload = {
        "month": stamp,
        "date": str(date),
        "label": f"{date.month_name} {date.year}",
        "season": date.season,
        "market": report,
        "requirements": requirements,
        "lore": location_lore(s),
        "events": active,
        # The quiet-world price of every good on the report, so the screen can
        # show a counterfactual column on each row rather than only the movers.
        "quiet": {cid: round(price, 2) for cid, price in quiet.items()},
        "movers": moves[:movers],
        "event_cost": round(total_now / total_quiet - 1.0, 4),
        "goods_moved": len(moves),
    }

    cache[key] = payload
    while len(cache) > DETAIL_CACHE_LIMIT:
        cache.popitem(last=False)
    return payload
