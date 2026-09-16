"""Finite daily stocks, recipe reservations, and same-day trade deliveries."""

import math
import heapq
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType


@dataclass(frozen=True)
class _PreparedRecipes(Mapping):
    _data: Mapping
    _signature: tuple

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


@dataclass(frozen=True)
class _PreparedCandidates(Mapping):
    _data: Mapping
    _places: frozenset
    _limits: Mapping
    _networks: Mapping

    def __getitem__(self, key):
        return tuple(MappingProxyType(row) for row in self._data[key])

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


@dataclass(frozen=True)
class _LaneNetwork:
    rows: tuple
    limits: tuple
    by_source: Mapping
    by_destination: Mapping


def _quantity(value, label, upper=None):
    try:
        valid = math.isfinite(value) and value >= 0 and (upper is None or value <= upper)
    except (TypeError, OverflowError):
        valid = False
    if not valid:
        suffix = f" and at most {upper}" if upper is not None else ""
        raise ValueError(f"{label} must be finite and non-negative{suffix}")
    return value


def _total(values):
    try:
        return _quantity(math.fsum(values), "Material total")
    except OverflowError as error:
        raise ValueError("Material total must be finite") from error


def _recipe_signature(recipes):
    signature = []
    for product, recipe in sorted(recipes.items()):
        items = tuple(sorted(recipe.items()))
        for _, coefficient in items:
            _quantity(coefficient, "Recipe coefficient")
            if coefficient == 0:
                raise ValueError("Recipe coefficients must be positive")
        signature.append((product, items))
    return tuple(signature)


@lru_cache(maxsize=1)
def _recipe_plan(signature, commodities):
    """Cache only immutable, value-keyed plans; mutable input edits cannot hide."""
    recipe_items = dict(signature)
    known = set(commodities)
    for product, recipe in signature:
        if product not in known:
            raise ValueError(f"Missing material balance for recipe product {product}")
        for component, _ in recipe:
            if component not in known:
                raise ValueError(f"Missing material balance for recipe input {component}")
    order, visited, visiting = [], set(), set()

    def visit(commodity):
        if commodity in visiting:
            raise ValueError("Inventory recipes must not contain cycles")
        if commodity in visited:
            return
        visiting.add(commodity)
        for component, _ in recipe_items.get(commodity, ()):
            visit(component)
        visiting.remove(commodity)
        visited.add(commodity)
        order.append(commodity)

    for commodity in commodities:
        visit(commodity)
    consumers = {commodity: [] for commodity in order}
    for product in order:
        for index, (component, _) in enumerate(recipe_items.get(product, ())):
            consumers[component].append((product, index))
    return (MappingProxyType(recipe_items), tuple(order),
            MappingProxyType({commodity: tuple(users) for commodity, users in consumers.items()}))


def _delivery_key(row):
    return row["unit_cost"], row["days"], row["source_id"], row["destination_id"]


def _validate_candidates(candidates):
    ordered, places = {}, set()
    for commodity, rows in candidates.items():
        previous, sorted_already = None, True
        for row in rows:
            if not all(key in row for key in ("source_id", "destination_id", "unit_cost", "days")):
                raise ValueError("Delivery lanes require source_id, destination_id, unit_cost, and days")
            places.update((row["source_id"], row["destination_id"]))
            _quantity(row["unit_cost"], "Delivery unit cost")
            _quantity(row["days"], "Delivery days")
            if "capacity_per_day" in row:
                _quantity(row["capacity_per_day"], "Delivery capacity")
            key = _delivery_key(row)
            if previous is not None and key < previous:
                sorted_already = False
            previous = key
        ordered[commodity] = rows if sorted_already else sorted(rows, key=_delivery_key)
    return ordered, places


def prepare_inventory_inputs(recipes, candidates):
    """Return reusable ``(recipes, candidates)`` for ``allocate_inventory_day``.

    Call once per immutable recipe/routing configuration (e.g. risk state),
    outside the replay loop. The returned mappings snapshot recipe quantities
    and lane dictionaries, validate them, and retain cheapest lane ordering.
    Mutating the original mappings or returned delivery rows cannot change
    the prepared plan. Extra lane metadata is shallow-copied, not interpreted.

    Preparation does not cache balances or trade budgets. Every allocation
    still validates all daily state values and checks that recipe materials
    and delivery commodities exist in that day's maps. Ordinary unprepared
    mappings remain supported and fully revalidated on every call.
    """
    if not isinstance(recipes, _PreparedRecipes):
        signature = _recipe_signature(recipes)
        materials = {product for product, _ in signature}
        materials.update(component for _, recipe in signature for component, _ in recipe)
        _recipe_plan(signature, tuple(sorted(materials)))
        data = MappingProxyType({product: MappingProxyType(dict(recipe))
                                 for product, recipe in signature})
        recipes = _PreparedRecipes(data, signature)
    if not isinstance(candidates, _PreparedCandidates):
        # Keep scalar-only lane dictionaries untracked by cyclic GC. Read-only
        # wrappers are needed only at the public boundary, not for millions of
        # private routing rows scanned on every replay day.
        snapshots = {commodity: tuple(dict(row) for row in rows)
                     for commodity, rows in candidates.items()}
        ordered, places = _validate_candidates(snapshots)
        data = MappingProxyType({commodity: tuple(rows) for commodity, rows in ordered.items()})
        limits = MappingProxyType({
            commodity: tuple(row.get("capacity_per_day", math.inf) for row in rows)
            for commodity, rows in data.items()
        })
        networks = {}
        for commodity, rows in data.items():
            by_source, by_destination = {}, {}
            for index, row in enumerate(rows):
                if row["source_id"] == row["destination_id"] or limits[commodity][index] == 0:
                    continue
                by_source.setdefault(row["source_id"], []).append(index)
                by_destination.setdefault(row["destination_id"], []).append(index)
            networks[commodity] = _LaneNetwork(
                rows, limits[commodity],
                MappingProxyType({place: tuple(indices) for place, indices in by_source.items()}),
                MappingProxyType({place: tuple(indices) for place, indices in by_destination.items()}),
            )
        candidates = _PreparedCandidates(data, frozenset(places), limits, MappingProxyType(networks))
    return recipes, candidates


class InventoryAllocator:
    """Prepared replay allocator retaining every eligible delivery lane.

    Construct once per route/risk signature, then call ``allocate`` with the
    six daily state maps. Sorted source/destination indexes are immutable;
    daily lane budgets are sparse and never leak into subsequent days.
    No global route cache retains older allocator instances.

    Replay omits diagnostic backup quotes by default, because enumerating
    unused alternatives can itself emit millions of rows every day. This
    does not remove any eligible route from either trade round. Pass
    ``include_backups=True`` when complete backup quote lists are required;
    that cost is necessarily proportional to the alternatives returned.
    """

    def __init__(self, recipes, candidates):
        self._recipes, self._candidates = prepare_inventory_inputs(recipes, candidates)

    def allocate(
        self, capacity, final_demand, opening_stock, storage_capacity,
        reserve_target, loss_rates, *, include_backups=False,
    ):
        return _allocate_inventory_day(
            capacity, final_demand, self._recipes, opening_stock,
            storage_capacity, reserve_target, loss_rates, self._candidates,
            include_backups=include_backups,
        )


def _reserve(requests, budget, demand):
    """Partition one physical input budget, never rounding a share above it."""
    if not requests or not demand or not budget:
        return
    if len(requests) == 1:
        requests[0]["reserved_per_day"] = min(requests[0]["required_per_day"], budget)
        return
    fraction = min(1.0, budget / demand)
    remaining = budget
    for index, request in enumerate(requests):
        required = request["required_per_day"]
        amount = min(required, remaining)
        if index != len(requests) - 1:
            amount = min(amount, required * fraction)
        request["reserved_per_day"] = amount
        remaining = max(0.0, remaining - amount)

    # Repeated subtraction can leave an ulp more than the original budget.
    excess = math.fsum(row["reserved_per_day"] for row in requests) - budget
    if excess > 0:
        for request in reversed(requests):
            amount = request["reserved_per_day"]
            if amount:
                reduced = max(0.0, amount - excess)
                request["reserved_per_day"] = min(reduced, math.nextafter(amount, 0.0))
                excess = math.fsum(row["reserved_per_day"] for row in requests) - budget
                if excess <= 0:
                    break


def _trade(ordered, lane_remaining, surplus, needs, balances, used, replenish=False):
    if not any(surplus.values()) or not any(needs.values()):
        return
    for index, row in enumerate(ordered):
        source, destination = row["source_id"], row["destination_id"]
        if source == destination:
            continue
        available, needed = surplus[source], needs[destination]
        if not available or not needed:
            continue
        quantity = min(available, needed, lane_remaining[index])
        if quantity <= 0:
            continue
        source_balance, destination_balance = balances[source], balances[destination]
        demand = (destination_balance["household_demand_per_day"]
                  + destination_balance["processing_demand_per_day"])
        destination_balance["allocation"]["imports"].append({
            **row,
            "quantity_per_day": quantity,
            "share": quantity / demand if demand and not replenish else 0.0,
            "purpose": "replenishment" if replenish else "demand",
        })
        surplus[source] = max(0.0, surplus[source] - quantity)
        needs[destination] = max(0.0, needs[destination] - quantity)
        lane_remaining[index] = max(0.0, lane_remaining[index] - quantity)
        source_balance["allocation"]["exports_per_day"] += quantity
        used.add((source, destination))
        if replenish:
            source_balance["closing_stock"] -= quantity
            destination_balance["closing_stock"] += quantity


def _next_eligible(network, indices, position, remaining, surplus, needs):
    while position < len(indices):
        index = indices[position]
        position += 1
        row = network.rows[index]
        source, destination = row["source_id"], row["destination_id"]
        if (source != destination and surplus[source] > 0 and needs[destination] > 0
                and remaining.get(index, network.limits[index]) > 0):
            return index, position
    return None


def _trade_indexed(network, remaining, surplus, needs, balances, used, replenish=False):
    """Merge only active lane groups in the original global cheapest order."""
    source_groups = {source: network.by_source[source] for source, amount in surplus.items()
                     if amount > 0 and source in network.by_source}
    destination_groups = {destination: network.by_destination[destination]
                          for destination, amount in needs.items()
                          if amount > 0 and destination in network.by_destination}
    if not source_groups or not destination_groups:
        return
    source_size = sum(map(len, source_groups.values()))
    destination_size = sum(map(len, destination_groups.values()))
    by_source = source_size <= destination_size
    groups = source_groups if by_source else destination_groups
    heap = []
    for place, indices in groups.items():
        next_lane = _next_eligible(network, indices, 0, remaining, surplus, needs)
        if next_lane is not None:
            index, position = next_lane
            heap.append((index, place, position))
    heapq.heapify(heap)
    active_sources, active_destinations = len(source_groups), len(destination_groups)
    while heap:
        index, place, position = heapq.heappop(heap)
        row = network.rows[index]
        source, destination = row["source_id"], row["destination_id"]
        available, needed = surplus[source], needs[destination]
        quantity = min(available, needed, remaining.get(index, network.limits[index]))
        if quantity > 0:
            source_balance, destination_balance = balances[source], balances[destination]
            demand = (destination_balance["household_demand_per_day"]
                      + destination_balance["processing_demand_per_day"])
            destination_balance["allocation"]["imports"].append({
                **row, "quantity_per_day": quantity,
                "share": quantity / demand if demand and not replenish else 0.0,
                "purpose": "replenishment" if replenish else "demand",
            })
            surplus[source] = max(0.0, available - quantity)
            needs[destination] = max(0.0, needed - quantity)
            remaining[index] = max(0.0, remaining.get(index, network.limits[index]) - quantity)
            source_balance["allocation"]["exports_per_day"] += quantity
            used.add((source, destination))
            if replenish:
                source_balance["closing_stock"] -= quantity
                destination_balance["closing_stock"] += quantity
            if surplus[source] == 0:
                active_sources -= 1
            if needs[destination] == 0:
                active_destinations -= 1
            if not active_sources or not active_destinations:
                break
        if (surplus[place] if by_source else needs[place]) > 0:
            next_lane = _next_eligible(
                network, groups[place], position, remaining, surplus, needs,
            )
            if next_lane is not None:
                index, position = next_lane
                heapq.heappush(heap, (index, place, position))


def allocate_inventory_day(
    capacity, final_demand, recipes, opening_stock, storage_capacity,
    reserve_target, loss_rates, candidates,
):
    """Allocate one day without mutating inputs or depending on world models.

    State maps are commodity -> settlement -> finite non-negative quantity;
    absent entries are zero, including storage capacity. Recipe coefficients
    must be positive. Recipe materials must occur in at least one state map.
    Loss rates apply to opening inventory only, before any use or delivery.

    Raw producers run at capacity. Workshops reduce their planned output by
    surviving product stock above their reserve target, then compete for
    unique, proportional ingredient reservations after households are served.
    The remaining planned output includes export orders, not just local use.

    Each candidate entry is a delivery lane. Its optional finite capacity and
    its source's exportable supply are shared by urgent and replenishment
    rounds. Replenishment runs after actual workshop use is known, cannot feed
    today's workshops, and has zero final-demand share. Travel days rank
    deliveries; there is no shipment-arrival lag.

    Reserves protect stock *after* planned local use, but urgent local use may
    draw them down. Unused workshop reservations remain protected for this
    day. Storage limits apply to closing inventory, not same-day throughput.
    Stock draw uses oldest inventory first and excludes all inventory losses.
    For replay, ``prepare_inventory_inputs`` can prevalidate and freeze the
    recipe/lane configuration without changing this call's arguments.
    """
    return _allocate_inventory_day(
        capacity, final_demand, recipes, opening_stock, storage_capacity,
        reserve_target, loss_rates, candidates, include_backups=True,
    )


def _allocate_inventory_day(
    capacity, final_demand, recipes, opening_stock, storage_capacity,
    reserve_target, loss_rates, candidates, *, include_backups,
):
    state_maps = (
        ("Capacity", capacity), ("Final demand", final_demand),
        ("Opening stock", opening_stock), ("Storage capacity", storage_capacity),
        ("Reserve target", reserve_target), ("Loss rate", loss_rates),
    )
    commodities, places = set(), set()
    for label, values in state_maps:
        commodities.update(values)
        for amounts in values.values():
            places.update(amounts)
            for amount in amounts.values():
                _quantity(amount, label, 1 if label == "Loss rate" else None)

    signature = (recipes._signature if isinstance(recipes, _PreparedRecipes)
                 else _recipe_signature(recipes))
    recipe_items, order, consumers = _recipe_plan(signature, tuple(sorted(commodities)))
    for commodity in candidates:
        if commodity not in commodities:
            raise ValueError(f"Missing material balance for delivery commodity {commodity}")
    if isinstance(candidates, _PreparedCandidates):
        ordered_candidates, lane_places = candidates._data, candidates._places
    else:
        ordered_candidates, lane_places = _validate_candidates(candidates)
    places.update(lane_places)
    places = sorted(places)

    result, surviving = {}, {}
    for commodity in order:
        balances, stocks = {}, {}
        limits = capacity.get(commodity, {})
        demands = final_demand.get(commodity, {})
        openings = opening_stock.get(commodity, {})
        stores = storage_capacity.get(commodity, {})
        targets = reserve_target.get(commodity, {})
        losses = loss_rates.get(commodity, {})
        recipe = recipe_items.get(commodity, ())
        for place in places:
            limit, opening = limits.get(place, 0.0), openings.get(place, 0.0)
            target = targets.get(place, 0.0)
            stock = opening * (1 - losses.get(place, 0.0))
            stocks[place] = stock
            scheduled = max(0.0, limit - max(0.0, stock - target)) if recipe else limit
            balances[place] = {
                "capacity_per_day": limit,
                "production_per_day": scheduled,
                "household_demand_per_day": demands.get(place, 0.0),
                "household_consumption_per_day": 0.0,
                "processing_demand_per_day": 0.0,
                "processing_consumption_per_day": 0.0,
                "opening_stock": opening,
                "spoilage": opening - stock,
                "overflow": 0.0,
                "storage_capacity": stores.get(place, 0.0),
                "reserve_target": target,
                "closing_stock": stock,
                "stock_draw_per_day": 0.0,
                "uncommitted_stock": 0.0,
                "inputs": [
                    {"commodity": component,
                     "required_per_day": _quantity(scheduled * coefficient, "Recipe requirement"),
                     "reserved_per_day": 0.0, "consumed_per_day": 0.0}
                    for component, coefficient in recipe
                ],
                "allocation": {
                    "local_per_day": 0.0, "imports": [], "backups": [],
                    "unmet_per_day": 0.0, "exports_per_day": 0.0,
                },
            }
        result[commodity], surviving[commodity] = balances, stocks

    for commodity in order:
        if not consumers[commodity]:
            continue
        for place, balance in result[commodity].items():
            if len(consumers[commodity]) == 1:
                product, index = consumers[commodity][0]
                demand = result[product][place]["inputs"][index]["required_per_day"]
            else:
                demand = _total(result[product][place]["inputs"][index]["required_per_day"]
                                for product, index in consumers[commodity])
            balance["processing_demand_per_day"] = demand

    markets = {}
    for commodity in order:
        balances = result[commodity]
        recipe = recipe_items.get(commodity, ())
        available, surplus, needs = {}, {}, {}
        for place, balance in balances.items():
            production = balance["production_per_day"]
            for (_, coefficient), request in zip(recipe, balance["inputs"]):
                reserved = request["reserved_per_day"]
                if production * coefficient > reserved:
                    production = min(production, reserved / coefficient)
                    # A rounded-up division must never spend an unreserved ulp.
                    while production * coefficient > reserved:
                        production = math.nextafter(production, 0.0)
            balance["production_per_day"] = production
            for (_, coefficient), request in zip(recipe, balance["inputs"]):
                request["consumed_per_day"] = production * coefficient
            supply = _quantity(surviving[commodity][place] + production, "Available supply")
            demand = _quantity(balance["household_demand_per_day"]
                               + balance["processing_demand_per_day"], "Total demand")
            local = min(supply, demand)
            balance["allocation"]["local_per_day"] = local
            available[place] = supply
            surplus[place] = max(0.0, supply - local - balance["reserve_target"])
            needs[place] = max(0.0, demand - local)

        # Reuse ordering, but always make fresh budgets for each day.
        ordered = ordered_candidates.get(commodity, ())
        network = (candidates._networks.get(commodity)
                   if isinstance(candidates, _PreparedCandidates) else None)
        lane_remaining = ({} if network is not None
                          else [row.get("capacity_per_day", math.inf) for row in ordered])
        used = set()
        if network is not None:
            _trade_indexed(network, lane_remaining, surplus, needs, balances, used)
        else:
            _trade(ordered, lane_remaining, surplus, needs, balances, used)
        markets[commodity] = ordered, lane_remaining, surplus, used, network
        for place, balance in balances.items():
            allocation = balance["allocation"]
            imported = (_total(row["quantity_per_day"] for row in allocation["imports"])
                        if allocation["imports"] else 0.0)
            delivered = available[place] + imported
            exported = allocation["exports_per_day"]
            supply = delivered - exported
            # Accumulated exports can round just above an exhausted float budget.
            if supply < 0 and math.isclose(delivered, exported, rel_tol=1e-12, abs_tol=0):
                supply = 0.0
            supply = _quantity(supply, "Delivered supply")
            household = min(supply, balance["household_demand_per_day"])
            balance["household_consumption_per_day"] = household
            balance["closing_stock"] = max(0.0, supply - household)
            allocation["unmet_per_day"] = needs[place]
            if consumers[commodity]:
                requests = [result[product][place]["inputs"][index]
                            for product, index in consumers[commodity]]
                processing = balance["processing_demand_per_day"]
                _reserve(requests, min(processing, balance["closing_stock"]), processing)

    for commodity in order:
        balances = result[commodity]
        ordered, lane_remaining, surplus, used, network = markets[commodity]
        unused, needs = {}, {}
        for place, balance in balances.items():
            users = consumers[commodity]
            consumed = unused[place] = 0.0
            if len(users) == 1:
                product, index = users[0]
                request = result[product][place]["inputs"][index]
                consumed = request["consumed_per_day"]
                unused[place] = request["reserved_per_day"] - consumed
            elif users:
                requests = [result[product][place]["inputs"][index] for product, index in users]
                consumed = _total(row["consumed_per_day"] for row in requests)
                unused[place] = _total(row["reserved_per_day"] - row["consumed_per_day"]
                                       for row in requests)
            balance["processing_consumption_per_day"] = consumed
            balance["closing_stock"] = max(0.0, balance["closing_stock"] - consumed)
            # Cancellation of workshop use is not another export opportunity.
            surplus[place] = min(surplus[place], balance["closing_stock"])
            target = min(balance["reserve_target"], balance["storage_capacity"])
            needs[place] = max(0.0, target - balance["closing_stock"])

        if network is not None:
            _trade_indexed(network, lane_remaining, surplus, needs, balances, used, replenish=True)
        else:
            _trade(ordered, lane_remaining, surplus, needs, balances, used, replenish=True)
        for place, balance in balances.items():
            closing = max(0.0, balance["closing_stock"])
            balance["overflow"] = max(0.0, closing - balance["storage_capacity"])
            balance["closing_stock"] = min(closing, balance["storage_capacity"])
            balance["uncommitted_stock"] = max(
                0.0, balance["closing_stock"] - balance["reserve_target"] - unused[place],
            )
            used_stock = (balance["household_consumption_per_day"]
                          + balance["processing_consumption_per_day"]
                          + balance["allocation"]["exports_per_day"])
            balance["stock_draw_per_day"] = min(surviving[commodity][place], used_stock)

        if not include_backups:
            continue
        backup_surplus = {place: min(surplus[place], balance["uncommitted_stock"])
                          for place, balance in balances.items()}
        if not any(backup_surplus.values()):
            continue
        indices = (heapq.merge(*(network.by_source.get(source, ())
                                 for source, amount in backup_surplus.items() if amount > 0))
                   if network is not None else range(len(ordered)))
        for index in indices:
            row = ordered[index]
            source, destination = row["source_id"], row["destination_id"]
            if source == destination or (source, destination) in used:
                continue
            lane_capacity = (lane_remaining.get(index, network.limits[index])
                             if network is not None else lane_remaining[index])
            available_stock = min(backup_surplus[source], lane_capacity)
            if available_stock > 0:
                balances[destination]["allocation"]["backups"].append({
                    **row, "available_per_day": available_stock,
                })
    return result
