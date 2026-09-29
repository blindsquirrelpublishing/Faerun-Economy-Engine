"""Precomputed price snapshots for the seasonal and standard economy modes.

Pricing every settlement against every commodity is cheap per call but adds
up across the whole gazetteer, so pages that just want "today's prices"
should not recompute the full grid on every request. ``refresh_price_snapshot``
builds it once per mode (standard and seasonal-inventory) and writes it to
JSON under ``faerun/data/store/``; ``load_price_snapshot``/``get_cached_price``
then just read that file. Call refresh again (via the MCP tool or CLI) after
editing the catalog through :mod:`faerun.catalog`, or whenever the date or
active events move on and you want the cache to catch up.

Only a compact subset of each ``PriceQuote`` is kept (the full quote carries
verbose notes, sourcing breakdowns and inventory detail meant for a single
lookup, not for 51,000 of them at once); call ``get_price`` for the full
picture of one settlement/commodity.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from .world import World, get_world

STORE_DIR = Path(__file__).resolve().parent / "data" / "store"
MODES = ("standard", "seasonal")


def _snapshot_path(mode: str) -> Path:
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    return STORE_DIR / f"price_snapshot_{mode}.json"


def _compact(quote) -> Dict[str, Any]:
    """Just enough of a PriceQuote for a fast lookup; see get_price for the rest."""
    return {
        "commodity_name": quote.commodity_name,
        "category": quote.category,
        "unit": quote.unit,
        "base_price": quote.base_price,
        "price": quote.price,
        "buy_price": quote.buy_price,
        "multiplier": quote.multiplier,
        "availability": quote.availability,
        "stock": quote.stock,
        "scarcity": quote.scarcity,
        "source": quote.source,
        "source_distance": quote.source_distance,
        "source_days": quote.source_days,
        "quality_offers": [
            {"quality": offer["quality"], "price": offer["price"],
             "buy_price": offer["buy_price"], "availability": offer["availability"],
             "stock": offer["stock"]}
            for offer in quote.quality_offers
        ],
    }


def _build_one(world: World, mode: str) -> Dict[str, Any]:
    from .economy import _commodity_markets
    from .trading import claims_for, tradable_quote

    original = world.config.seasonal_inventory
    world.config.seasonal_inventory = (mode == "seasonal")
    try:
        claims = claims_for(world)
        prices: Dict[str, Dict[str, Any]] = {}
        for cid, commodity in world.commodities.items():
            for sid, quote in _commodity_markets(world, commodity).items():
                quote = tradable_quote(world, quote, claims)
                prices.setdefault(sid, {})[cid] = _compact(quote)
    finally:
        world.config.seasonal_inventory = original
    return {
        "mode": mode,
        "generated_at": time.time(),
        "date": str(world.date),
        "season": world.date.season,
        "revision": world.revision,
        "settlements": len(world.settlements),
        "commodities": len(world.commodities),
        "prices": prices,
    }


def refresh_price_snapshot(mode: str = "both", world: Optional[World] = None) -> Dict[str, Any]:
    """(Re)build and persist the full price grid for one or both modes."""
    world = world or get_world()
    modes = MODES if mode == "both" else (mode,)
    if any(m not in MODES for m in modes):
        raise ValueError(f"mode must be one of {MODES} or 'both'")
    results: Dict[str, Any] = {}
    for m in modes:
        started = time.monotonic()
        snapshot = _build_one(world, m)
        elapsed = time.monotonic() - started
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        path = _snapshot_path(m)
        tmp = path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(snapshot, fh, separators=(",", ":"), ensure_ascii=False)
        tmp.replace(path)
        results[m] = {
            "generated_at": snapshot["generated_at"], "date": snapshot["date"],
            "revision": snapshot["revision"], "settlements": snapshot["settlements"],
            "commodities": snapshot["commodities"], "seconds": round(elapsed, 2),
            "path": str(path),
        }
    return results


def load_price_snapshot(mode: str) -> Optional[Dict[str, Any]]:
    path = _snapshot_path(mode)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def price_snapshot_status(world: Optional[World] = None) -> Dict[str, Any]:
    """Whether each mode's snapshot exists, and whether the world has moved on since."""
    world = world or get_world()
    status: Dict[str, Any] = {}
    for m in MODES:
        snapshot = load_price_snapshot(m)
        if snapshot is None:
            status[m] = {"exists": False}
            continue
        status[m] = {
            "exists": True,
            "generated_at": snapshot.get("generated_at"),
            "date": snapshot.get("date"),
            "revision": snapshot.get("revision"),
            "current_revision": world.revision,
            "stale": snapshot.get("revision") != world.revision,
        }
    return status


def get_cached_price(settlement_id: str, commodity_id: str,
                      mode: str = "standard") -> Optional[Dict[str, Any]]:
    """A single quote from the last refresh, or None if uncached or unknown."""
    snapshot = load_price_snapshot(mode)
    if snapshot is None:
        return None
    return snapshot.get("prices", {}).get(settlement_id, {}).get(commodity_id)
