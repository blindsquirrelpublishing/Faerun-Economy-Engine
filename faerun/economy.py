"""The price engine.

For each commodity the engine runs three passes over the whole world:

1. **Local balance** - how much of the good each settlement can make
   (industries, specialities, terrain, size) versus how much it wants
   (population, culture, wealth, season, events).
2. **Export pricing** - settlements in surplus set a producer price below
   the notional base price and add a merchant's margin.
3. **Landed cost** - a multi-source shortest-path search pushes goods out
   along roads, rivers, sea lanes and Underdark tunnels, accumulating
   freight, risk premiums and spoilage, so every market learns the cheapest
   price at which the good can reach it.

Local tariffs, market competition, seasonality, world events and a small
deterministic wobble finish the number.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict
from typing import Dict, Iterable, List, Optional, Sequence

from .calendar import season_of
from .living import daily_requirement, settlement_daily_requirements
from .models import Commodity, PriceQuote, Settlement, format_coin, price_terms
from .population import population_report
from .production import allocate_production
from .sourcing import allocate_supply
from .world import FREIGHT_RATE, World, get_world

# ---------------------------------------------------------------------------
# Industry classification
# ---------------------------------------------------------------------------

PRIMARY = {
    "farm", "orchard", "herd", "cattle", "horse", "fish", "whale", "hunt", "log",
    "quarry", "salt", "herb", "spice", "sugar", "ivory", "pearl", "amber", "oil",
    "mine_iron", "mine_copper", "mine_tin", "mine_silver", "mine_gold", "mine_gem",
    "mine_mithral", "mine_adamantine", "mine_coal",
}

EXTRACTIVE = {
    "salt", "quarry", "pearl", "amber", "ivory", "oil",
    "mine_iron", "mine_copper", "mine_tin", "mine_silver", "mine_gold",
    "mine_gem", "mine_mithral", "mine_adamantine", "mine_coal",
}

QUALITY_INDUSTRIES = {
    "craft", "smith", "armor", "weapon", "textile", "glass", "pottery",
    "paper", "alch", "brew", "vint", "distill", "ship", "tan", "rope",
}

QUALITY_TIERS = (
    ("basic", 0.70),
    ("standard", 1.00),
    ("fine", 1.75),
    ("masterwork", 4.00),
)

TERRAIN_MODS: Dict[str, Dict[str, float]] = {
    "plains": {"farm": 1.2, "herd": 1.1, "cattle": 1.15, "horse": 1.15, "log": 0.8},
    "hills": {"mine": 1.2, "quarry": 1.15, "herd": 1.2, "farm": 0.9},
    "mountains": {"mine": 1.35, "quarry": 1.3, "farm": 0.4, "log": 0.7, "herd": 0.8},
    "forest": {"log": 1.45, "hunt": 1.35, "herb": 1.2, "farm": 0.85},
    "taiga": {"log": 1.35, "hunt": 1.25, "farm": 0.4, "fish": 1.1},
    "coast": {"fish": 1.3, "ship": 1.2, "salt": 1.25, "pearl": 1.3, "farm": 0.95},
    "marsh": {"fish": 1.25, "farm": 0.7, "herb": 1.15, "log": 0.9},
    "desert": {"farm": 0.4, "herd": 0.8, "spice": 1.15, "quarry": 1.1, "log": 0.3},
    "tundra": {"farm": 0.2, "hunt": 1.3, "fish": 1.15, "herd": 0.6, "log": 0.3},
    "jungle": {"spice": 1.55, "log": 1.35, "orchard": 1.35, "hunt": 1.25, "ivory": 1.4,
               "farm": 0.8},
    "cavern": {"farm": 0.12, "orchard": 0.1, "mine": 1.35, "hunt": 0.3, "fish": 0.3,
               "herd": 0.2, "log": 0.1},
}

#: units of a staple a single citizen buys in a tenday
VOLUME_SCALE = 0.02

#: how many (commodity, month) market solutions to keep before dropping the lot
PRICE_CACHE_LIMIT = 2000


def _terrain_mod(terrain: str, tag: str) -> float:
    table = TERRAIN_MODS.get(terrain, {})
    if tag in table:
        return table[tag]
    if tag.startswith("mine_") and "mine" in table:
        return table["mine"]
    return 1.0


def _noise(world: World, settlement: Settlement, commodity: Commodity) -> float:
    key = (
        f"{settlement.id}|{commodity.id}|{world.date.absolute_day()}|"
        f"{world.config.seed}"
    )
    digest = hashlib.blake2b(key.encode(), digest_size=8).digest()
    unit = int.from_bytes(digest, "big") / float(1 << 64)
    return 1.0 + (unit * 2 - 1) * world.config.noise


def _size_norm(population: int) -> float:
    """0 for a thorp, 1 for Waterdeep-scale markets."""
    return max(0.0, min(1.0, (math.log(max(population, 20)) - math.log(50)) /
                        (math.log(150000) - math.log(50))))


# ---------------------------------------------------------------------------
# Supply and demand
# ---------------------------------------------------------------------------


def _region_allows(s: Settlement, c: Commodity) -> bool:
    """Region-locked goods (teak, camels, faerzress) only grow where they belong."""
    if not c.requires:
        return True
    return any(s.terrain == gate or s.has_trait(gate) for gate in c.requires)


def supply_index(world: World, s: Settlement, c: Commodity, *, include_events: bool = True) -> float:
    """How much of `c` the settlement makes, in units of its own demand."""
    raw = 0.0
    if _region_allows(s, c):
        for tag in c.produced_by:
            level = s.industry_level(tag)
            if level:
                raw += level * _terrain_mod(s.terrain, tag)
    primary = any(tag in PRIMARY for tag in c.produced_by)
    if primary:
        scale = 1.0 + max(0.0, 8.0 - math.log(max(s.population, 20))) * 0.14
    else:
        scale = 1.0 + max(0.0, math.log(max(s.population, 20)) - 7.0) * 0.11
    strength = 0.35 * raw * scale
    strength += 1.20 * s.specialties.get(c.id, 0.0)
    if c.bom and daily_requirement(c.id, s.wealth, settlement=s) is not None:
        if raw > 0 or c.id in {"bread", "flour"}:
            strength = max(strength, demand_index(world, s, c, include_events=False))
    if c.id in s.shortages:
        strength *= 0.12
    if include_events:
        for event in world.events_for(s):
            if event.supply != 1.0 and event.applies_to_commodity(c):
                strength *= event.supply
    return max(0.0, strength)


def demand_index(world: World, s: Settlement, c: Commodity, *, include_events: bool = True) -> float:
    """Per-capita appetite for `c`, relative to a balanced market (1.0)."""
    multiplier = 1.0
    for trait, factor in c.demand_traits.items():
        if s.has_trait(trait):
            multiplier *= factor
    multiplier = min(multiplier ** 0.7, 5.0)
    # A town needs far fewer bolts of spider silk than bushels of grain, so the
    # appetite for niche goods is scaled down against the staples.
    multiplier *= max(0.05, c.demand) ** 0.5
    multiplier *= s.wealth ** (0.6 + 1.8 * c.luxury)
    if c.id in s.shortages:
        multiplier *= 1.15
    if include_events:
        for event in world.events_for(s):
            if event.demand != 1.0 and event.applies_to_commodity(c):
                multiplier *= event.demand
    return max(0.05, multiplier)


def _daily_market_volume(s: Settlement, c: Commodity) -> float:
    """Baseline daily units before culture, events, and other demand pressure."""
    requirement = daily_requirement(c.id, s.wealth, settlement=s)
    if requirement is not None:
        return s.population * requirement
    return s.population * c.demand * VOLUME_SCALE / 10.0


def _quality_capability(s: Settlement, c: Commodity) -> float:
    specialty = s.specialties.get(c.id, 0.0)
    industry = max(
        (s.industry_level(tag) for tag in c.produced_by if tag in QUALITY_INDUSTRIES),
        default=0.0,
    )
    return max(specialty, industry * 0.75)


def _quality_availability(stock: int) -> str:
    if stock <= 0:
        return "unavailable"
    if stock == 1:
        return "rare"
    if stock <= 4:
        return "scarce"
    if stock <= 19:
        return "common"
    return "abundant"


def _quality_offers(price: float, buy_price: float, stock: int,
                    capability: float) -> List[Dict]:
    fine_stock = 0
    masterwork_stock = 0
    if capability >= 1.0 and stock >= 2:
        fine_stock = max(1, int(round(stock * min(0.22, 0.08 + capability * 0.04))))
    if capability >= 2.5 and stock >= 8:
        masterwork_stock = max(1, int(round(stock * min(0.06, capability * 0.018))))
    basic_stock = int(round(stock * 0.15)) if stock >= 3 else 0
    standard_stock = max(0, stock - basic_stock - fine_stock - masterwork_stock)
    stocks = {
        "basic": basic_stock,
        "standard": standard_stock,
        "fine": fine_stock,
        "masterwork": masterwork_stock,
    }
    offers = []
    for quality, factor in QUALITY_TIERS:
        ask = round(price * factor, 3)
        bid = round(buy_price * factor, 3)
        offers.append({
            "quality": quality,
            "price": ask,
            "buy_price": bid,
            "price_factor": factor,
            "stock": stocks[quality],
            "availability": _quality_availability(stocks[quality]),
        })
    return offers


# ---------------------------------------------------------------------------
# Whole-world pass for a single commodity
# ---------------------------------------------------------------------------


def _staple_recipes(world):
    return {commodity.id: commodity.bom for commodity in world.commodities.values()
            if commodity.id in {"flour", "bread"} and commodity.bom
            and all(component in world.commodities for component in commodity.bom)}


def _staple_markets(world, recipes):
    tracked = set(recipes).union(*(recipe.keys() for recipe in recipes.values()))
    capacity = {}
    household = {}
    quotes = {}
    baseline = {}
    baseline_household = {}
    hinterland_factors = {}
    for commodity_id in sorted(tracked):
        commodity = world.commodities[commodity_id]
        baseline[commodity_id] = {
            place: _daily_market_volume(settlement, commodity) * supply_index(world, settlement, commodity, include_events=False)
            for place, settlement in world.settlements.items()
        }
        baseline_household[commodity_id] = {
            place: _daily_market_volume(settlement, commodity) * demand_index(world, settlement, commodity, include_events=False)
            for place, settlement in world.settlements.items()
        }
        capacity[commodity_id] = {
            place: _daily_market_volume(settlement, commodity) * supply_index(world, settlement, commodity)
            for place, settlement in world.settlements.items()
        }
        household[commodity_id] = {
            place: _daily_market_volume(settlement, commodity) * demand_index(world, settlement, commodity)
            for place, settlement in world.settlements.items()
        }

    if "flour" in recipes and "bread" in recipes and "flour" in recipes["bread"]:
        for place, settlement in world.settlements.items():
            original = baseline["flour"][place]
            milling_need = baseline_household["flour"][place] + baseline["bread"][place] * recipes["bread"]["flour"]
            if "flour" not in settlement.shortages:
                baseline["flour"][place] = max(original, milling_need)
                disruption = capacity["flour"][place] / original if original else 0.0
                capacity["flour"][place] = baseline["flour"][place] * disruption

    reserve = world.config.staple_reserve_ratio
    if not math.isfinite(reserve) or reserve < 1.0:
        raise ValueError("Staple reserve ratio must be finite and at least one")
    for commodity_id in sorted(tracked - set(recipes)):
        needed = sum(baseline_household[commodity_id].values())
        needed += sum(sum(baseline[product].values()) * recipe.get(commodity_id, 0.0)
                      for product, recipe in recipes.items())
        existing = sum(baseline[commodity_id].values())
        factor = max(1.0, needed * reserve / existing) if existing else 1.0
        hinterland_factors[commodity_id] = factor
        capacity[commodity_id] = {place: amount * factor for place, amount in capacity[commodity_id].items()}

    def allocate(commodity_id, production, demand):
        costs = {place: 0.0 for place in world.settlements}
        for component, quantity in recipes.get(commodity_id, {}).items():
            for place, quote in quotes[component].items():
                supplied = sum(row["quantity_per_day"] for row in quote.sources)
                unit_cost = (sum(row["quantity_per_day"] * row["unit_cost"] for row in quote.sources) / supplied
                             if supplied else 0.0)
                costs[place] += quantity * unit_cost
        quotes[commodity_id] = _commodity_markets(
            world, world.commodities[commodity_id],
            _material={"production": production, "demand": demand, "unit_cost": costs},
        )
        return {place: {
            "local_per_day": quote.local_consumption_per_day,
            "imports": [row for row in quote.sources if row["supply_type"] == "import"],
            "backups": quote.backup_sources,
            "unmet_per_day": quote.unmet_demand_per_day,
            "exports_per_day": quote.exports_per_day,
        } for place, quote in quotes[commodity_id].items()}

    balances = allocate_production(capacity, household, recipes, allocate)
    for commodity_id, markets in quotes.items():
        commodity = world.commodities[commodity_id]
        for place, quote in markets.items():
            balance = balances[commodity_id][place]
            quote.production_capacity_per_day = balance["capacity_per_day"]
            quote.factors["hinterland_capacity_multiplier"] = hinterland_factors.get(commodity_id, 1.0)
            quote.household_demand_per_day = balance["household_demand_per_day"]
            quote.household_consumption_per_day = balance["household_consumption_per_day"]
            quote.processing_demand_per_day = balance["processing_demand_per_day"]
            quote.processing_consumption_per_day = balance["processing_consumption_per_day"]
            quote.material_closing_stock = balance["closing_stock"]
            quote.production_inputs = balance["inputs"]
            for ingredient in quote.production_inputs:
                ingredient["unit"] = world.commodities[ingredient["commodity"]].unit
            retail_daily = balance["household_consumption_per_day"] + balance["closing_stock"]
            stock_days = min(10.0, world.config.fresh_bread_days) if commodity_id == "bread" else 10.0
            quote.stock_horizon_days = stock_days
            quote.stock = max(0, round(retail_daily * stock_days))
            capability = max((_quality_capability(world.settlements[row["source_id"]], commodity)
                              for row in quote.sources), default=0.0)
            quote.quality_offers = _quality_offers(quote.price, quote.buy_price, quote.stock, capability)
            if quote.stock == 0 and quote.availability != "unavailable":
                quote.availability = "rare"
            if balance["inputs"]:
                quote.notes.append(
                    f"input-backed production: {balance['production_per_day']:.1f} of "
                    f"{balance['capacity_per_day']:.1f} {commodity.unit}/day capacity"
                )
    return quotes


def _delivery_candidates(world, commodity, sources, buyers):
    candidates = []
    for exporter, producer_price in sorted(sources.items()):
        if not buyers:
            break
        landed, _, haul = world.multi_source_freight(
            {exporter: producer_price}, commodity.weight, commodity.perishable, commodity.base_price,
            max_days=world.config.fresh_bread_days if commodity.id == "bread" else None,
        )
        for buyer in buyers:
            if buyer not in landed or buyer == exporter:
                continue
            miles, days = haul[buyer]
            candidate = {"source_id": exporter, "destination_id": buyer,
                         "source": world.settlements[exporter].name,
                         "unit_cost": landed[buyer], "producer_unit_cost": producer_price,
                         "distance": miles, "days": days}
            limit = world.config.delivery_limits.get((commodity.id, exporter, buyer))
            if limit is not None:
                if not math.isfinite(limit) or limit < 0:
                    raise ValueError("Delivery limits must be finite non-negative units per day")
                candidate["capacity_per_day"] = limit
            candidates.append(candidate)
    return candidates


def _commodity_markets(world: World, c: Commodity, *, _material=None) -> Dict[str, PriceQuote]:
    cfg = world.config
    if (not all(isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) for value in (cfg.spread_min, cfg.spread_max))
            or not 0 <= cfg.spread_min <= cfg.spread_max < 1):
        raise ValueError("Merchant spread bounds must satisfy 0 <= minimum <= maximum < 1")
    cache = getattr(world, "_price_cache", None)
    if cache is None:
        cache = {}
        setattr(world, "_price_cache", cache)

    key = (c.id,) + world.economy_state_key()
    cache_limit = len(world.commodities) * 2 if cfg.seasonal_inventory else PRICE_CACHE_LIMIT
    if _material is None and key in cache:
        return cache[key]
    if len(cache) > cache_limit:
        cache.clear()
    if _material is None and world.config.expanded_requirements:
        from .materials import requirements_markets

        markets = requirements_markets(world)
        for commodity_id, quotes in markets.items():
            cache[(commodity_id,) + key[1:]] = quotes
        return markets[c.id]
    recipes = _staple_recipes(world)
    tracked = set(recipes).union(*(recipe.keys() for recipe in recipes.values()))
    if _material is None and c.id in tracked:
        markets = _staple_markets(world, recipes)
        for commodity_id, quotes in markets.items():
            cache[(commodity_id,) + key[1:]] = quotes
        return markets[c.id]
    # Each entry holds a quote for every settlement, and scrubbing a timeline
    # walks dozens of months, so an unbounded cache would happily grow to a
    # million objects.  Nothing here is worth keeping across that many months.
    if len(cache) > cache_limit:
        cache.clear()

    if not math.isfinite(cfg.fresh_bread_days) or cfg.fresh_bread_days <= 0:
        raise ValueError("Bread freshness must be a finite positive number of days")
    season = season_of(world.date.month)
    inventory_mode = _material is not None and "allocations" in _material
    season_mult = 1.0 if inventory_mode else c.season_multiplier(season)

    balance: Dict[str, Dict[str, float]] = {}
    sources: Dict[str, float] = {}
    for sid, s in world.settlements.items():
        daily_volume = _daily_market_volume(s, c)
        input_cost = 0.0
        if _material is None:
            supply = supply_index(world, s, c)
            demand = demand_index(world, s, c)
        else:
            daily_volume = daily_volume or 1.0
            supply = _material["production"][sid] / daily_volume
            demand = _material["demand"][sid] / daily_volume
            input_cost = _material["unit_cost"][sid]
        ratio = supply / demand if demand else 0.0
        if math.isclose(ratio, 1.0, rel_tol=1e-9):
            ratio = 1.0
        balance[sid] = {"supply": supply, "demand": demand, "ratio": ratio, "volume": daily_volume}
        if ratio > 1.02 or (_material is not None and supply > demand + 1e-9):
            factor = max(cfg.surplus_floor, min(1.0, (1.0 / ratio) ** cfg.surplus_elasticity)) if ratio else cfg.surplus_floor
            producer_price = max(c.base_price * factor, input_cost)
            balance[sid]["producer_price"] = producer_price
            sources[sid] = producer_price * (1.0 + cfg.export_margin)

    production = {sid: info["volume"] * info["supply"]
                  for sid, info in balance.items()}
    demand_volume = {sid: info["volume"] * info["demand"]
                     for sid, info in balance.items()}
    if inventory_mode:
        allocations = _material["allocations"]
    else:
        buyers = [sid for sid in balance if demand_volume[sid] > production[sid]]
        candidates = _delivery_candidates(world, c, sources, buyers)
        allocations = allocate_supply(production, demand_volume, candidates)

    quotes: Dict[str, PriceQuote] = {}
    for sid, s in world.settlements.items():
        info = balance[sid]
        supply, demand, ratio = info["supply"], info["demand"], info["ratio"]
        notes: List[str] = []
        source_id: Optional[str] = None
        source_distance: Optional[float] = None
        source_days: Optional[float] = None
        allocation = allocations[sid]
        active_imports = allocation["imports"]
        imported = sum(row["quantity_per_day"] for row in active_imports)
        unmet = allocation["unmet_per_day"]
        reachable = imported > 0
        local_share = min(1.0, allocation["local_per_day"] / demand_volume[sid]) if demand_volume[sid] else 1.0

        if sid in sources:
            core = info["producer_price"]
            notes.append("local surplus is available for trade" if inventory_mode else
                         "local surplus: this market exports")
            local_share = 1.0
        elif ratio >= 1.0:
            core = max(c.base_price, _material["unit_cost"][sid] if _material is not None else 0.0)
            notes.append("local production and stored inventory meet local needs" if inventory_mode else
                         "local production meets local needs")
            local_share = 1.0
        elif reachable:
            import_cost = sum(row["quantity_per_day"] * row["unit_cost"] for row in active_imports)
            if demand_volume[sid] > 0:
                import_use = min(imported, max(0.0, demand_volume[sid] - allocation["local_per_day"]))
                local_cost = max(c.base_price, _material["unit_cost"][sid] if _material is not None else 0.0)
                core = (allocation["local_per_day"] * local_cost + import_cost * import_use / imported
                        + unmet * c.base_price * cfg.shortage_ceiling) / demand_volume[sid]
                core *= 1.0 + unmet / demand_volume[sid] * cfg.scarcity_elasticity * 0.4
                core = min(core, c.base_price * cfg.shortage_ceiling)
            else:
                core = import_cost / imported
            supplier_totals = {}
            for row in active_imports:
                supplier_totals[row["source_id"]] = supplier_totals.get(row["source_id"], 0.0) + row["quantity_per_day"]
            primary_source = max(active_imports, key=lambda row: supplier_totals[row["source_id"]])
            source_id = primary_source["source_id"]
            source_distance = round(primary_source["distance"], 1)
            source_days = round(primary_source["days"], 1)
            for row in active_imports:
                notes.append(
                    f"{row['quantity_per_day']:.1f} {c.unit}/day from {row['source']} "
                    f"({row['distance']:.0f} mi, {row['days']:.1f} days)"
                )
        else:
            scarcity = demand / max(supply, 0.02)
            core = c.base_price * min(cfg.shortage_ceiling,
                                      max(2.0, scarcity ** cfg.scarcity_elasticity * 4))
            local_share = max(0.0, min(1.0, ratio))
            notes.append("no eligible export capacity allocated to this market")

        if unmet > 1e-6:
            notes.append(f"unmet demand: {unmet:.1f} {c.unit}/day")

        size = _size_norm(s.population)
        markup = cfg.market_markup_small * (1.0 - size)
        markup *= max(0.4, 1.0 - 0.12 * s.industry_level("trade"))
        tax = 1.0 + s.tax
        event_price = 1.0
        for event in world.events_for(s):
            if event.price != 1.0 and event.applies_to_commodity(c):
                event_price *= event.price
                notes.append(f"event: {event.name}")
        wobble = _noise(world, s, c)

        inventory_pressure = _material["inventory_pressure"][sid] if inventory_mode else 1.0
        price = core * (1.0 + markup) * tax * season_mult * inventory_pressure * event_price * wobble
        price = max(price, c.base_price * 0.25)

        production_per_day = production[sid]
        demand_per_day = demand_volume[sid]
        available_daily = max(0.0, production_per_day - allocation["exports_per_day"] + imported)
        stock_days = min(10.0, cfg.fresh_bread_days) if c.id == "bread" else 10.0
        stock = max(0, int(round(available_daily * stock_days)))

        multiplier = price / c.base_price
        if not reachable and supply <= 0:
            availability = "unavailable"
        elif multiplier <= 0.8:
            availability = "abundant"
        elif ratio >= 1.0 and daily_requirement(c.id, s.wealth, settlement=s) is not None:
            availability = "common"
        elif multiplier <= 1.35:
            availability = "common"
        elif multiplier <= 2.5:
            availability = "scarce"
        else:
            availability = "rare"
        if stock <= 0 and availability not in ("unavailable",):
            availability = "rare"

        spread = 0.16 + 0.22 * min(2.0, ratio) - 0.10 * size
        if availability in ("rare", "unavailable"):
            spread -= 0.06
        spread = max(cfg.spread_min, min(cfg.spread_max, spread))

        source_settlement = world.settlements.get(source_id) if source_id else None
        capability = max(
            _quality_capability(s, c) if supply > 0 else 0.0,
            _quality_capability(source_settlement, c) if source_settlement else 0.0,
        )
        quality_offers = _quality_offers(price, price * (1.0 - spread), stock, capability)

        quotes[sid] = PriceQuote(
            settlement=s.name,
            commodity=c.id,
            commodity_name=c.name,
            category=c.category,
            production_type=c.production_type,
            unit=c.unit,
            base_price=round(c.base_price, 2),
            price=round(price, 3),
            buy_price=round(price * (1.0 - spread), 3),
            multiplier=round(multiplier, 3),
            availability=availability,
            stock=stock,
            stock_horizon_days=stock_days,
            producer_gate_price=(
                info.get("producer_price", max(c.base_price, _material["unit_cost"][sid] if _material is not None else 0.0))
                if production_per_day > 0 else None),
            guild_markup_rate=cfg.export_margin,
            supply_index=round(supply, 3),
            demand_index=round(demand, 3),
            production_per_day=round(production_per_day, 3),
            demand_per_day=round(demand_per_day, 3),
            scarcity=round(demand / max(supply, 0.02), 2),
            source=world.settlements[source_id].name if source_id and source_id != sid else None,
            source_distance=source_distance,
            source_days=source_days,
            factors={
                "local_share": round(local_share, 3),
                "core_price": round(core, 3),
                "market_markup": round(markup, 3),
                "tariff": round(s.tax, 3),
                "season": round(season_mult, 3),
                "inventory_pressure": round(inventory_pressure, 3),
                "event": round(event_price, 3),
                "wobble": round(wobble, 3),
                "spread": round(spread, 3),
            },
            notes=notes,
            quality_offers=quality_offers,
                        sources=([{"source_id": sid, "source": s.name, "supply_type": "local",
                                             "quantity_per_day": allocation["local_per_day"], "share": local_share,
                                             "unit_cost": info.get("producer_price", max(c.base_price, _material["unit_cost"][sid] if _material is not None else 0.0)), "distance": 0.0, "days": 0.0}]
                                         if allocation["local_per_day"] > 0 else []) +
                                        [{**row, "supply_type": "import"} for row in active_imports],
                        backup_sources=allocation["backups"],
                        imports_per_day=imported,
                        exports_per_day=allocation["exports_per_day"],
                        local_consumption_per_day=allocation["local_per_day"],
                        unmet_demand_per_day=unmet,
                        final_demand_per_day=demand_per_day,
                        final_consumption_per_day=min(available_daily, demand_per_day),
        )

    if _material is None:
        cache[key] = quotes
    if len(cache) > 4000:
        cache.clear()
        cache[key] = quotes
    return quotes


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def price_for(settlement, commodity, world: Optional[World] = None,
              quantity: int = 1, quality: str = "standard") -> PriceQuote:
    """Price one commodity in one market."""
    world = world or get_world()
    s = world.find_settlement(settlement)
    c = world.find_commodity(commodity)
    from .trading import tradable_quote
    quote = tradable_quote(world, _commodity_markets(world, c)[s.id])
    quality = str(quality).strip().lower()
    if quality not in {name for name, _factor in QUALITY_TIERS}:
        raise ValueError(
            f"unknown quality {quality!r}; choose basic, standard, fine, or masterwork"
        )
    if quality != "standard":
        offer = next(row for row in quote.quality_offers if row["quality"] == quality)
        data = asdict(quote)
        data.update({
            "quality": quality,
            "price": offer["price"],
            "buy_price": offer["buy_price"],
            "multiplier": round(offer["price"] / quote.base_price, 3),
            "availability": offer["availability"],
            "stock": offer["stock"],
            "stock_scope": quality,
            "producer_gate_price": (quote.producer_gate_price * offer["price_factor"]
                                    if quote.producer_gate_price is not None else None),
            "producer_price_factor": offer["price_factor"],
        })
        quote = PriceQuote(**data)
    if quantity and quantity > 1:
        quote = _apply_quantity(quote, quantity)
    return quote


def _apply_quantity(quote: PriceQuote, quantity: int) -> PriceQuote:
    """Large orders move the market: depth impact against available stock."""
    depth = max(1.0, float(quote.stock))
    pressure = 1.0 + 0.35 * math.log1p(max(0.0, quantity - 1) / depth)
    relief = 1.0 - 0.25 * math.log1p(max(0.0, quantity - 1) / depth)
    relief = max(0.5, relief)
    data = asdict(quote)
    data["price"] = round(quote.price * pressure, 3)
    data["buy_price"] = round(quote.buy_price * relief, 3)
    data["multiplier"] = round(data["price"] / quote.base_price, 3)
    data["factors"] = dict(quote.factors, quantity=quantity,
                           depth_impact=round(pressure, 3))
    notes = list(quote.notes)
    if pressure > 1.05:
        notes.append(
            f"buying {quantity:,} {quote.unit}s at once drives the price up "
            f"{(pressure - 1) * 100:.0f}%"
        )
    if quantity > quote.uncommitted_stock:
        if quote.inventory.get("enabled"):
            notes.append(
                f"requested quantity exceeds uncommitted closing inventory ({quote.uncommitted_stock:,} units); "
                "additional purchases could displace protected reserves or ingredient commitments; this quote is not a booking"
            )
        else:
            notes.append(
                f"requested quantity exceeds the uncommitted stock estimate "
                f"({quote.uncommitted_stock:,} units over {quote.stock_horizon_days:g} days); "
                "additional purchases could displace planned needs or exports; this quote is not a booking"
            )
    data["notes"] = notes
    return PriceQuote(**data)


def market_report(settlement, world: Optional[World] = None,
                  category: Optional[str] = None,
                  commodities: Optional[Sequence[str]] = None,
                  sort: str = "category") -> Dict:
    """Every price on offer in one market."""
    world = world or get_world()
    s = world.find_settlement(settlement)
    if commodities:
        goods = [world.find_commodity(x) for x in commodities]
    else:
        goods = [
            c for c in world.commodities.values()
            if category is None or c.category == category
        ]
    from .trading import claims_for, tradable_quote
    claims = claims_for(world)
    quotes = [tradable_quote(world, _commodity_markets(world, c)[s.id], claims) for c in goods]
    if sort == "price":
        quotes.sort(key=lambda q: -q.price)
    elif sort == "multiplier":
        quotes.sort(key=lambda q: -q.multiplier)
    else:
        quotes.sort(key=lambda q: (q.category, q.commodity_name))
    exports = sorted(
        (q for q in quotes if q.multiplier <= 0.9),
        key=lambda q: q.multiplier,
    )[:8]
    imports = sorted(
        (q for q in quotes if q.multiplier >= 1.4),
        key=lambda q: -q.multiplier,
    )[:8]
    living = settlement_daily_requirements(s.id, world=world)
    from .materials import economic_report

    accounts = economic_report(s.id, world)["accounts"]
    return {
        "settlement": s.name,
        "region": s.region,
        "size": s.size,
        "population": s.population,
        "population_model": population_report(s),
        "ruler": s.ruler,
        "tariff": s.tax,
        "wealth": s.wealth,
        "living_standard": living["living_standard"],
        "daily_requirements": living["requirements"],
        "accounts": accounts,
        "date": str(world.date),
        "season": world.date.season,
        "traits": s.traits,
        "description": s.description,
        "events": [e.name for e in world.events_for(s)],
        "cheap_here": [{"commodity": q.commodity_name, "price": q.price,
                        "unit": q.unit, "x_base": q.multiplier} for q in exports],
        "dear_here": [{"commodity": q.commodity_name, "price": q.price,
                       "unit": q.unit, "x_base": q.multiplier} for q in imports],
        "prices": [q.to_dict() for q in quotes],
    }


def compare_prices(commodity, world: Optional[World] = None,
                   settlements: Optional[Sequence[str]] = None,
                   region: Optional[str] = None,
                   limit: int = 20, cheapest_first: bool = True) -> Dict:
    """Where in the Realms is this good cheap, and where is it dear?"""
    world = world or get_world()
    c = world.find_commodity(commodity)
    markets = _commodity_markets(world, c)
    if settlements:
        ids = [world.find_settlement(x).id for x in settlements]
    elif region:
        low = region.lower()
        ids = [s.id for s in world.settlements.values()
               if low in s.region.lower() or low in s.zone.lower()]
    else:
        ids = list(world.settlements)
    from .trading import claims_for, tradable_quote
    claims = claims_for(world)
    rows = [tradable_quote(world, markets[i], claims) for i in ids if i in markets]
    rows.sort(key=lambda q: q.price, reverse=not cheapest_first)
    return {
        "commodity": c.name,
        "commodity_id": c.id,
        "unit": c.unit,
        "base_price": c.base_price,
        "date": str(world.date),
        "markets": [q.to_dict() for q in rows[:limit]],
    }


def commodity_sources(commodity, world: Optional[World] = None,
                      limit: int = 30) -> Dict:
    """Where a good is produced, exported, and made especially well."""
    world = world or get_world()
    c = world.find_commodity(commodity)
    recipes = _staple_recipes(world)
    tracked = set(recipes).union(*(recipe.keys() for recipe in recipes.values()))
    actual = _commodity_markets(world, c) if world.config.expanded_requirements or c.id in tracked else {}
    locations = []
    for settlement in world.settlements.values():
        quote = actual.get(settlement.id)
        supply = quote.supply_index if quote else supply_index(world, settlement, c)
        seasonal_capacity = quote.inventory.get("annual_capacity_per_day", 0.0) if quote else 0.0
        if (max(quote.production_per_day, seasonal_capacity) <= 0 if quote else supply <= 0):
            continue
        demand = quote.demand_index if quote else demand_index(world, settlement, c)
        daily_volume = _daily_market_volume(settlement, c)
        specialty = settlement.specialties.get(c.id, 0.0)
        quality_industry = max(
            (settlement.industry_level(tag) for tag in c.produced_by
             if tag in QUALITY_INDUSTRIES),
            default=0.0,
        )
        if specialty >= 2 or quality_industry >= 3:
            quality = "renowned"
        elif specialty >= 1 or quality_industry >= 2:
            quality = "notable"
        else:
            quality = "standard"
        locations.append({
            "id": settlement.id,
            "name": settlement.name,
            "region": settlement.region,
            "terrain": settlement.terrain,
            "producer": True,
            "exporter": (quote.exports_per_day > 1e-9 if quote and quote.inventory.get("enabled") else
                         quote.production_per_day > quote.demand_per_day + 1e-9
                         if quote else supply / max(demand, 0.02) > 1.02),
            "production_strength": round(supply, 3),
            "production_per_day": quote.production_per_day if quote else round(daily_volume * supply, 3),
            "demand_per_day": quote.demand_per_day if quote else round(daily_volume * demand, 3),
            "unit": c.unit,
            "inventory": quote.inventory if quote else {},
            "seasonality": quote.seasonality if quote else {},
            "quality": quality,
            "quality_basis": (
                "commodity specialty" if specialty
                else "established craft industry" if quality_industry >= 2
                else None
            ),
        })

    locations.sort(key=lambda row: (
        row["quality"] == "renowned",
        row["quality"] == "notable",
        row["exporter"],
        row["production_strength"],
    ), reverse=True)
    region_rows = []
    for region in sorted({row["region"] for row in locations}):
        members = [row for row in locations if row["region"] == region]
        region_rows.append({
            "region": region,
            "producers": len(members),
            "exporters": sum(row["exporter"] for row in members),
            "quality_sources": [
                row["name"] for row in members if row["quality"] != "standard"
            ],
        })
    region_rows.sort(key=lambda row: (
        bool(row["quality_sources"]), row["exporters"], row["producers"]
    ), reverse=True)

    tags = set(c.produced_by)
    if c.requires:
        scope = "restricted"
    elif tags & EXTRACTIVE:
        scope = "extractive"
    elif "farm" in tags or len(locations) >= max(8, len(world.settlements) // 4):
        scope = "widespread"
    else:
        scope = "specialized"
    return {
        "commodity": c.name,
        "commodity_id": c.id,
        "category": c.category,
        "source_scope": scope,
        "source_requirements": c.requires,
        "produced_by": c.produced_by,
        "producer_count": len(locations),
        "exporter_count": sum(row["exporter"] for row in locations),
        "regions": region_rows,
        "sources": locations[:max(0, limit)],
    }


def sourcing_catalog(world: Optional[World] = None,
                     category: Optional[str] = None,
                     search: Optional[str] = None,
                     limit: int = 200,
                     source_limit: int = 12) -> Dict:
    """List goods with their source scope, regions, and leading producers."""
    world = world or get_world()
    needle = (search or "").lower()
    goods = [
        commodity for commodity in world.commodities.values()
        if (category is None or commodity.category == category)
        and (not needle or needle in f"{commodity.id} {commodity.name}".lower())
    ]
    rows = [
        commodity_sources(commodity.id, world=world, limit=source_limit)
        for commodity in goods[:max(0, limit)]
    ]
    return {
        "count": len(rows),
        "categories": sorted({commodity.category for commodity in goods}),
        "commodities": rows,
    }


def _freight_map(world: World, origin_id: str) -> Dict[str, float]:
    """gp to carry one pound from `origin_id` to everywhere reachable."""
    weight = lambda e: e.freight_units(world.edge_risk(e)) * FREIGHT_RATE
    dist, _ = world._dijkstra(origin_id, weight)
    return dist


def _days_map(world: World, origin_id: str) -> Dict[str, float]:
    weight = lambda e: e.days * (1.0 + world.edge_risk(e) * 0.25)
    dist, _ = world._dijkstra(origin_id, weight)
    return dist


def find_arbitrage(origin, world: Optional[World] = None,
                   destinations: Optional[Sequence[str]] = None,
                   max_days: float = 45.0,
                   cargo_pounds: float = 2000.0,
                   category: Optional[str] = None,
                   limit: int = 15) -> Dict:
    """Profitable cargoes to carry out of a market.

    Profit is per wagonload (`cargo_pounds`): buy at the origin's asking
    price, pay freight and risk, sell at the destination merchant's bid.
    """
    world = world or get_world()
    a = world.find_settlement(origin)
    freight = _freight_map(world, a.id)
    days = _days_map(world, a.id)
    if destinations:
        targets = [world.find_settlement(d).id for d in destinations]
    else:
        targets = [sid for sid, d in days.items()
                   if sid != a.id and d <= max_days]

    goods = [c for c in world.commodities.values()
             if category is None or c.category == category]

    from .trading import claims_for, tradable_quote
    claims = claims_for(world)
    deals = []
    for c in goods:
        markets = _commodity_markets(world, c)
        here = tradable_quote(world, markets[a.id], claims)
        if here.availability in ("unavailable",) or here.uncommitted_stock <= 0:
            continue
        units = min(int(cargo_pounds // max(c.weight, 0.05)), here.uncommitted_stock)
        if units <= 0:
            continue
        buy_unit = here.price
        for sid in targets:
            if sid not in freight:
                continue
            there = markets[sid]
            if there.availability == "unavailable":
                continue
            travel_days = days.get(sid, 999)
            if travel_days > max_days:
                continue
            spoil = 1.0 - min(0.9, c.perishable * travel_days / 20.0)
            freight_unit = freight[sid] * c.weight
            sell_unit = there.buy_price * spoil
            profit_unit = sell_unit - buy_unit - freight_unit
            if profit_unit <= 0:
                continue
            total = profit_unit * units
            deals.append({
                "commodity": c.name,
                "commodity_id": c.id,
                "unit": c.unit,
                "destination": world.settlements[sid].name,
                "destination_id": sid,
                "buy_at_origin": round(buy_unit, 2),
                "sell_at_destination": round(sell_unit, 2),
                "freight_per_unit": round(freight_unit, 3),
                "profit_per_unit": round(profit_unit, 2),
                "units_per_load": units,
                "uncommitted_stock": here.uncommitted_stock,
                "uncommitted_supply_per_day": here.uncommitted_supply_per_day,
                "stock_horizon_days": here.stock_horizon_days,
                "profit_per_load": round(total, 2),
                "margin_pct": round(profit_unit / max(buy_unit, 0.001) * 100, 1),
                "travel_days": round(travel_days, 1),
                "gp_per_day": round(total / max(travel_days, 0.5), 2),
                "risk": round(1.0 - world.settlements[sid].security, 2),
            })
    deals.sort(key=lambda d: -d["gp_per_day"])
    return {
        "origin": a.name,
        "date": str(world.date),
        "cargo_pounds": cargo_pounds,
        "max_days": max_days,
        "deals": deals[:limit],
        "supply_basis": "Cargo is capped by uncommitted stock estimates after planned demand and allocated exports; alternatives share this pool and are not bookings.",
    }


def price_history(settlement, commodity, world: Optional[World] = None,
                  months: int = 12) -> Dict:
    """Roll the calendar forward and record the price each month."""
    world = world or get_world()
    s = world.find_settlement(settlement)
    c = world.find_commodity(commodity)
    original = world.date
    original_key = world.economy_state_key()
    original_markets = {}
    series = []
    from .trading import claims_for, tradable_quote
    claims = claims_for(world)
    try:
        for offset in range(months):
            world.date = original.advance(offset)
            quote = tradable_quote(world, _commodity_markets(world, c)[s.id], claims)
            if offset == 0 and world.config.seasonal_inventory:
                original_markets = {key: value for key, value in world._price_cache.items()
                                    if key[1:] == original_key}
            series.append({
                "date": str(world.date),
                "month": world.date.month_name,
                "season": world.date.season,
                "price": quote.price,
                "buy_price": quote.buy_price,
                **price_terms(quote.price, quote.buy_price),
                "uncommitted_supply_per_day": quote.uncommitted_supply_per_day,
                "uncommitted_stock": quote.uncommitted_stock,
                "stock_horizon_days": quote.stock_horizon_days,
                "x_base": quote.multiplier,
                "availability": quote.availability,
                "production_per_day": quote.production_per_day,
                "demand_per_day": quote.demand_per_day,
                "stock": quote.stock,
                "inventory": quote.inventory,
                "seasonality": quote.seasonality,
            })
    finally:
        world.date = original
        if original_markets:
            world._price_cache.update(original_markets)
    prices = [row["price"] for row in series]
    return {
        "settlement": s.name,
        "commodity": c.name,
        "unit": c.unit,
        "base_price": c.base_price,
        "low": min(prices),
        "high": max(prices),
        "average": round(sum(prices) / len(prices), 3),
        "series": series,
    }


def trade_summary(settlement, world: Optional[World] = None,
                  top: int = 10) -> Dict:
    """What a market sells cheaply to the world, and what it hungers for."""
    world = world or get_world()
    s = world.find_settlement(settlement)
    rows = []
    from .trading import claims_for, tradable_quote
    claims = claims_for(world)
    for c in world.commodities.values():
        q = tradable_quote(world, _commodity_markets(world, c)[s.id], claims)
        rows.append(q)
    exports = sorted(
        (q for q in rows if (q.exports_per_day > 0 or q.uncommitted_stock > 0
                            if q.inventory.get("enabled") else
                            not world.config.expanded_requirements or q.production_per_day > q.demand_per_day)),
        key=lambda q: q.multiplier,
    )[:top]
    imports = sorted(
        (q for q in rows if (q.imports_per_day > 0 or q.unmet_demand_per_day > 0
                            if q.inventory.get("enabled") else
                            not world.config.expanded_requirements or q.demand_per_day > q.production_per_day)),
        key=lambda q: -q.multiplier,
    )[:top]
    from .materials import economic_report

    return {
        "settlement": s.name,
        "region": s.region,
        "accounts": economic_report(s.id, world)["accounts"],
        "exports": [{"commodity": q.commodity_name, "price": q.price,
                     **price_terms(q.price, q.buy_price),
                     "unit": q.unit, "x_base": q.multiplier,
                     "stock_per_tenday": q.stock, "exports_per_day": q.exports_per_day,
                     "uncommitted_stock": q.uncommitted_stock,
                     "uncommitted_supply_per_day": q.uncommitted_supply_per_day,
                     "stock_horizon_days": q.stock_horizon_days,
                     "inventory": q.inventory,
                     "surplus_per_day": q.exportable_supply_per_day}
                    for q in exports],
        "imports": [{"commodity": q.commodity_name, "price": q.price,
                     **price_terms(q.price, q.buy_price),
                     "unit": q.unit, "x_base": q.multiplier,
                     "from": q.source, "availability": q.availability,
                     "imports_per_day": q.imports_per_day,
                     "import_need_per_day": q.import_need_per_day,
                     "unmet_demand_per_day": q.unmet_demand_per_day}
                    for q in imports],
    }


def coin(gp: float) -> str:
    return format_coin(gp)
