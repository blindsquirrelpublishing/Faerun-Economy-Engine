"""Deterministic daily stock ledgers, reconstructed from an explicit scenario epoch."""

from __future__ import annotations

import math
from collections import OrderedDict
from copy import copy, deepcopy
from dataclasses import replace

from .calendar import FESTIVAL_MONTHS, HarptosDate


def inventory_epoch(world):
    value = world.config.inventory_epoch
    if not isinstance(value, str) or len(value.split("-")) != 3:
        raise ValueError("inventory_epoch must be a YYYY-MM-DD Harptos date")
    parts = value.split("-")
    if not all(part.isdigit() for part in parts):
        raise ValueError("inventory_epoch must be a YYYY-MM-DD Harptos date")
    return HarptosDate(*(int(part) for part in parts))


def inventory_enabled(world):
    return (world.config.seasonal_inventory and world.config.expanded_requirements
            and world.date.absolute_day() >= inventory_epoch(world).absolute_day())


def _overrides(world, values, name):
    if not isinstance(values, dict):
        raise ValueError(f"{name} must map (settlement_id, commodity_id) to quantities")
    for key, amount in values.items():
        if not isinstance(key, tuple) or len(key) != 2:
            raise ValueError(f"{name} keys must be (settlement_id, commodity_id)")
        sid, cid = key
        if sid not in world.settlements or cid not in world.commodities:
            raise ValueError(f"Unknown location or commodity in {name}: {key}")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount < 0:
            raise ValueError(f"{name} quantities must be finite and non-negative")
    return values


def _cover_calendar(multipliers, demand_multipliers):
    daily = [value for month, value in enumerate(multipliers, 1)
             for _ in range(31 if month in FESTIVAL_MONTHS else 30)]
    demand = [value for month, value in enumerate(demand_multipliers, 1)
              for _ in range(31 if month in FESTIVAL_MONTHS else 30)]
    result = []
    # Maximum future cumulative deficit is the stock needed to bridge harvests.
    for start in range(365):
        deficit = peak = 0.0
        for offset in range(1, 366):
            index = (start + offset) % 365
            deficit += demand[index] - daily[index]
            peak = max(peak, deficit)
        result.append(peak)
    return result


def _consume_services(balances, sectors, services):
    from .accounts import service_consumption
    from .inventory import _quantity

    releases = {}
    for cid, places in balances.items():
        for sid, balance in places.items():
            demand = balance["household_demand_per_day"]
            fraction = balance["household_consumption_per_day"] / demand if demand else 0.0
            balance["consumption_sectors"] = {sector: amount * fraction
                                              for sector, amount in sectors[sid][cid].items()}
    for sid, plans in services.items():
        for plan in plans:
            _, allocated, consumed = service_consumption(
                plan, {cid: balances[cid][sid]["consumption_sectors"].get(plan["id"], 0.0)
                       for cid in plan["inputs_per_unit"]},
            )
            for cid in allocated:
                released = allocated[cid] - consumed[cid]
                balance = balances[cid][sid]
                balance["consumption_sectors"][plan["id"]] -= released
                releases.setdefault((cid, sid), []).append(released)
                closing = balance["closing_stock"] + released
                balance["closing_stock"] = min(balance["storage_capacity"], closing)
                balance["overflow"] += max(0.0, closing - balance["storage_capacity"])
    for (cid, sid), amounts in releases.items():
        balance = balances[cid][sid]
        allocated = balance["household_consumption_per_day"]
        released = math.fsum(amounts)
        consumed = allocated - released
        # Repeated subtraction and proportional sector shares can exceed an
        # exhausted budget by ulps. Material over-releases must still fail.
        if consumed < 0 and math.isclose(allocated, released, rel_tol=1e-12, abs_tol=0):
            consumed = 0.0
        balance["household_consumption_per_day"] = _quantity(consumed, "Service consumption")
        used = (consumed + balance["processing_consumption_per_day"]
                + balance["allocation"]["exports_per_day"])
        balance["stock_draw_per_day"] = min(balance["opening_stock"] - balance["spoilage"], used)


class InventoryHistory:
    def __init__(self, world, plan):
        from .seasonality import seasonal_profile

        self.epoch = inventory_epoch(world)
        self.world = copy(world)
        self.world.config = replace(world.config, seasonal_inventory=False)
        self.world.revision = world.inventory_revision
        self.world._date_revisions = 0
        self.world.follows_real_date = False
        for name in ("_price_cache", "_service_accounts_cache", "_requirements_plan",
                     "_freight_graph_stamp", "_inventory_history"):
            self.world.__dict__.pop(name, None)
        self.world._events_stamp = None
        self.plan = plan
        self.recipes = {cid: c.bom for cid, c in world.commodities.items() if c.bom}
        self.needs = {cid: {sid: sum(plan["sectors"][sid][cid].values())
                            for sid in world.settlements} for cid in plan["order"]}
        for product, recipe in self.recipes.items():
            for component, coefficient in recipe.items():
                for sid, capacity in plan["capacity"][product].items():
                    self.needs[component][sid] += capacity * coefficient
        self.profiles = {}
        self.covers = {}
        self.storage = {}
        self.losses = {}
        self.months = OrderedDict()
        self.routes = {}
        self.checkpoints = OrderedDict()
        self.last_day = None
        self.last_balances = None
        self.last_includes_backups = False
        self.windows = OrderedDict()
        initial = _overrides(world, world.config.initial_inventory, "initial_inventory")
        capacities = _overrides(world, world.config.storage_capacity, "storage_capacity")
        cover_cache = {}
        calendar_cache = {}
        opening = {}
        epoch_offset = self.epoch.absolute_day() - HarptosDate(self.epoch.year).absolute_day()
        for cid in plan["order"]:
            commodity = world.commodities[cid]
            values = (commodity.storage_days, commodity.storage_loss, commodity.reserve_days)
            if any(isinstance(v, bool) or not isinstance(v, (int, float))
                   or not math.isfinite(v) or v < 0 for v in values) or commodity.storage_loss > 1:
                raise ValueError(f"Invalid storage settings for {cid}")
            self.profiles[cid] = {}
            self.covers[cid] = {}
            self.storage[cid] = {}
            self.losses[cid] = {}
            opening[cid] = {}
            for sid, settlement in world.settlements.items():
                profile = seasonal_profile(commodity, settlement, self.epoch)
                curve = tuple(row["production_multiplier"] for row in profile["months"])
                demand_curve = tuple(row["demand_multiplier"] for row in profile["months"])
                key = (curve, demand_curve)
                if key not in cover_cache:
                    cover_cache[key] = _cover_calendar(curve, demand_curve)
                self.profiles[cid][sid] = calendar_cache.setdefault(key, key)
                self.covers[cid][sid] = cover_cache[key]
                throughput = max(self.needs[cid][sid], plan["capacity"][cid][sid])
                capacity = capacities.get((sid, cid), throughput * commodity.storage_days)
                self.storage[cid][sid] = capacity
                self.losses[cid][sid] = commodity.storage_loss
                reserve = self.needs[cid][sid] * max(commodity.reserve_days, cover_cache[key][epoch_offset])
                quantity = initial.get((sid, cid), min(capacity, reserve))
                if quantity > capacity:
                    raise ValueError(f"Initial inventory exceeds storage capacity for {sid}/{cid}")
                opening[cid][sid] = quantity
        self.checkpoints[self.epoch.absolute_day()] = opening
        self.store = None
        if world.config.inventory_cache_path:
            from .inventory_cache import InventoryCheckpointStore, scenario_key

            self.store = InventoryCheckpointStore(world.config.inventory_cache_path, scenario_key(world))

    def _allocator(self):
        from .economy import _delivery_candidates
        from .inventory import InventoryAllocator

        signature = tuple((event.id, event.risk) for event in self.world.active_events() if event.risk)
        if signature in self.routes:
            return self.routes[signature]
        candidates = {}
        cfg = self.world.config
        for cid, capacity in self.plan["capacity"].items():
            commodity = self.world.commodities[cid]
            sources = {}
            for sid, amount in capacity.items():
                need = self.needs[cid][sid]
                if amount <= need + 1e-9:
                    continue
                ratio = amount / need if need else math.inf
                factor = max(cfg.surplus_floor, min(1.0, (1.0 / ratio) ** cfg.surplus_elasticity))
                sources[sid] = commodity.base_price * factor * (1.0 + cfg.export_margin)
            buyers = [sid for sid, amount in self.needs[cid].items() if amount > 0]
            rows = _delivery_candidates(self.world, commodity, sources, buyers)
            candidates[cid] = sorted(rows, key=lambda r: (
                r["unit_cost"], r["days"], r["source_id"], r["destination_id"]))
        allocator = InventoryAllocator(self.recipes, candidates)
        self.routes[signature] = allocator
        # Old route states can be reconstructed when browsing backwards.
        if len(self.routes) > 1:
            self.routes.pop(next(iter(self.routes)))
        return allocator

    def _month(self, date):
        from .materials import _active_requirements

        key = (date.absolute_month(), bool(date.festival))
        self.world.date = date
        if key in self.months:
            self.months.move_to_end(key)
            return self.months[key]
        sectors, services, travel = _active_requirements(self.world, self.plan)
        capacity = {}
        final = {}
        for cid, commodity in self.world.commodities.items():
            capacity[cid] = {}
            final[cid] = {}
            for sid, settlement in self.world.settlements.items():
                production_curve, demand_curve = self.profiles[cid][sid]
                capacity[cid][sid] = self.plan["capacity"][cid][sid] * production_curve[date.month - 1]
                demand_factor = demand_curve[date.month - 1]
                for event in self.world.events_for(settlement):
                    if not math.isfinite(event.supply) or not math.isfinite(event.demand):
                        raise ValueError(f"Event {event.id} has non-finite supply or demand")
                    if event.applies_to_commodity(commodity):
                        capacity[cid][sid] *= max(0.0, event.supply)
                        demand_factor *= max(0.0, event.demand)
                        for service in services[sid]:
                            if cid in service["inputs_per_unit"]:
                                service["inputs_per_unit"][cid] *= max(0.0, event.demand)
                sectors[sid][cid] = {sector: amount * demand_factor
                                     for sector, amount in sectors[sid][cid].items()}
                final[cid][sid] = sum(sectors[sid][cid].values())
        result = (capacity, final, sectors, services, travel)
        self.months[key] = result
        while len(self.months) > 3:
            self.months.popitem(last=False)
        return result

    def at(self, date, *, include_backups=True):
        target = date.absolute_day()
        if self.last_day == target and (self.last_includes_backups or not include_backups):
            return self.last_balances, self._month(date)
        checkpoint = max(day for day in self.checkpoints if day <= target)
        opening = self.checkpoints[checkpoint]
        if self.store:
            saved = self.store.load(target, self.storage)
            if saved and saved[0] > checkpoint:
                checkpoint, opening = saved
                self.checkpoints[checkpoint] = opening
        balances = None
        monthly = None
        for absolute_day in range(checkpoint, target + 1):
            current = HarptosDate.from_absolute_day(absolute_day)
            monthly = self._month(current)
            capacity, final = monthly[:2]
            offset = absolute_day - HarptosDate(current.year).absolute_day()
            reserves = {
                cid: {sid: min(self.storage[cid][sid], self.needs[cid][sid]
                               * max(self.world.commodities[cid].reserve_days, days[offset]))
                      for sid, days in places.items()}
                for cid, places in self.covers.items()
            }
            try:
                balances = self._allocator().allocate(
                    capacity, final, opening, self.storage, reserves,
                    self.losses, include_backups=include_backups and absolute_day == target,
                )
            except ValueError as error:
                raise ValueError(f"Inventory replay on {current}: {error}") from error
            _consume_services(balances, monthly[2], monthly[3])
            opening = {cid: {sid: balance["closing_stock"] for sid, balance in places.items()}
                       for cid, places in balances.items()}
            tomorrow = current.add_days()
            if tomorrow.day == 1 or absolute_day == target:
                self.checkpoints[absolute_day + 1] = opening
                if self.store:
                    self.store.save(absolute_day + 1, opening)
                    if absolute_day == target:
                        self.store.save(absolute_day, {
                            cid: {sid: balance["opening_stock"] for sid, balance in places.items()}
                            for cid, places in balances.items()
                        })
                while len(self.checkpoints) > 38:
                    removable = next(day for day in self.checkpoints if day != self.epoch.absolute_day())
                    self.checkpoints.pop(removable)
        self.last_day = target
        self.last_balances = balances
        self.last_includes_backups = include_backups
        return balances, monthly


def _history_for(world, plan):
    settings = world.economy_state_key(month=0)[2]
    catalogue = repr([c.to_dict() for c in world.commodities.values()])
    signature = (world.inventory_revision, settings, catalogue)
    cached = getattr(world, "_inventory_history", None)
    if cached is None or cached[0] != signature:
        cached = (signature, InventoryHistory(world, plan))
        world._inventory_history = cached
    return cached[1]


def seasonal_balances(world, plan):
    history = _history_for(world, plan)
    balances, monthly = history.at(world.date)
    return history, balances, monthly


def inventory_window(settlement, commodity, start: HarptosDate, end: HarptosDate, *, world=None):
    """Exact daily physical allocations for an inclusive window of 1-31 days.

    Requires explicit seasonal inventory mode and dates on/after its epoch.
    Returns detached snapshots and summed flows, without changing the world's
    date, quoting prices, claiming stock, or enumerating backup suppliers.
    Opening/closing/free stocks are balances, never additive window supply.
    Existing exports describe modeled deliveries, not additional free stock.
    """
    from .materials import _baseline_plan
    from .world import get_world

    world = world or get_world()
    if not world.config.seasonal_inventory or not world.config.expanded_requirements:
        raise ValueError("Inventory windows require seasonal_inventory and expanded_requirements")
    if not isinstance(start, HarptosDate) or not isinstance(end, HarptosDate):
        raise ValueError("Inventory window dates must be HarptosDate instances")
    first, last = start.absolute_day(), end.absolute_day()
    if last < first or last - first >= 31:
        raise ValueError("Inventory windows must contain 1-31 inclusive days")
    if first < inventory_epoch(world).absolute_day():
        raise ValueError("Inventory windows cannot precede the configured inventory epoch")
    sid = world.find_settlement(settlement).id
    cid = world.find_commodity(commodity).id
    history = _history_for(world, _baseline_plan(world))
    key = (sid, cid, first, last)
    if key in history.windows:
        history.windows.move_to_end(key)
        return deepcopy(history.windows[key])
    snapshots = []
    flows = ("production", "imports", "exports", "final_demand", "processing_demand", "demand",
             "final_consumption", "processing_consumption", "spoilage", "overflow")
    for day in range(first, last + 1):
        current = HarptosDate.from_absolute_day(day)
        balances, _ = history.at(current, include_backups=False)
        places = balances[cid]
        balance = places[sid]
        allocation = balance["allocation"]
        destinations = {}
        for destination, market in places.items():
            amount = math.fsum(row["quantity_per_day"] for row in market["allocation"]["imports"]
                               if row["source_id"] == sid)
            if amount:
                destinations[destination] = amount
        final = balance["household_demand_per_day"]
        processing = balance["processing_demand_per_day"]
        snapshots.append({
            "date": f"{current.year:04d}-{current.month:02d}-{current.day:02d}",
            "production": balance["production_per_day"],
            "imports": math.fsum(row["quantity_per_day"] for row in allocation["imports"]),
            "exports": allocation["exports_per_day"],
            "exports_by_destination": destinations,
            "final_demand": final, "processing_demand": processing, "demand": final + processing,
            "final_consumption": balance["household_consumption_per_day"],
            "processing_consumption": balance["processing_consumption_per_day"],
            **{name: balance[name] for name in (
                "opening_stock", "closing_stock", "uncommitted_stock", "reserve_target",
                "storage_capacity", "stock_draw_per_day", "spoilage", "overflow")},
        })
    destinations = set().union(*(row["exports_by_destination"] for row in snapshots))
    result = {
        "settlement_id": sid, "commodity_id": cid, "unit": world.commodities[cid].unit,
        "start": snapshots[0]["date"], "end": snapshots[-1]["date"], "days": len(snapshots),
        "opening_stock": snapshots[0]["opening_stock"], "closing_stock": snapshots[-1]["closing_stock"],
        "totals": {name: math.fsum(row[name] for row in snapshots) for name in flows},
        "exports_by_destination": {
            destination: math.fsum(row["exports_by_destination"].get(destination, 0.0) for row in snapshots)
            for destination in sorted(destinations)},
        "snapshots": snapshots,
        "basis": "Exact daily modeled allocations; exports are existing deliveries, not free stock. "
                 "No PO claims or warehouse purchases are executed by this read.",
    }
    history.windows[key] = result
    while len(history.windows) > 64:
        history.windows.popitem(last=False)
    return deepcopy(result)


def inventory_quotes(world, plan):
    from .economy import _commodity_markets
    from .seasonality import seasonal_profile

    history, balances, monthly = seasonal_balances(world, plan)
    sectors, services, travel = monthly[2:]
    quotes = {}
    for cid in plan["order"]:
        commodity = world.commodities[cid]
        costs = {sid: 0.0 for sid in world.settlements}
        for component, coefficient in commodity.bom.items():
            for sid, quote in quotes[component].items():
                costs[sid] += quote.factors["core_price"] * quote.factors["inventory_pressure"] * coefficient
        markets = balances[cid]
        pressures = {}
        for sid, balance in markets.items():
            reserve = balance["reserve_target"]
            closing = balance["closing_stock"]
            pressures[sid] = (min(2.0, max(0.75, (reserve / max(closing, reserve / 16.0)) ** 0.25))
                              if reserve > 0 else 1.0)
        demand = {sid: b["household_demand_per_day"] + b["processing_demand_per_day"]
                  for sid, b in markets.items()}
        supply = {sid: min(
            b["production_per_day"] + b["opening_stock"] - b["spoilage"],
            demand[sid] + b["allocation"]["exports_per_day"] + b["uncommitted_stock"] + b["overflow"],
        ) for sid, b in markets.items()}
        allocations = {}
        for sid, balance in markets.items():
            deliveries = []
            for row in balance["allocation"]["imports"]:
                source = row["source_id"]
                ratio = supply[source] / demand[source] if demand[source] else math.inf
                factor = (max(world.config.surplus_floor, (1.0 / ratio) ** world.config.surplus_elasticity)
                          if ratio > 1.0 else 1.0)
                producer = max(commodity.base_price * factor, costs[source])
                producer *= (1.0 + world.config.export_margin) * pressures[source]
                deliveries.append({**row, "producer_unit_cost": producer,
                                   "unit_cost": producer + row["unit_cost"] - row["producer_unit_cost"]})
            allocations[sid] = {**balance["allocation"], "imports": deliveries}
        quotes[cid] = _commodity_markets(
            world, commodity, _material={
                "production": supply,
                "demand": demand,
                "unit_cost": costs,
                "allocations": allocations,
                "inventory_pressure": pressures,
            },
        )
        for sid, quote in quotes[cid].items():
            balance = markets[sid]
            if plan["capacity"][cid][sid] <= 0:
                quote.producer_gate_price = None
            quote.seasonality = seasonal_profile(commodity, world.settlements[sid], world.date)
            need = balance["household_demand_per_day"] + balance["processing_demand_per_day"]
            quote.inventory = {
                "enabled": True,
                **{key: balance[key] for key in (
                    "opening_stock", "closing_stock", "storage_capacity", "reserve_target",
                    "spoilage", "overflow", "stock_draw_per_day", "uncommitted_stock")},
                "days_of_cover": balance["closing_stock"] / need if need else None,
                "annual_capacity_per_day": plan["capacity"][cid][sid],
                "epoch": str(history.epoch),
                "checkpoint_storage": "local SQLite cache" if history.store else "memory",
                "stock_basis": "Closing on-hand inventory; daily replay from seeded opening reserves. "
                               "Imports are same-day steady-state deliveries, not scheduled shipments.",
            }
            quote.factors["production_season"] = quote.seasonality["production_multiplier"]
            quote.factors["demand_season"] = quote.seasonality["demand_multiplier"]
            quote.notes.append(f"Inventory replay from {history.epoch}; "
                               f"{balance['stock_draw_per_day']:.3f} {commodity.unit}/day drawn from stores")
    return quotes, balances, sectors, services, travel
