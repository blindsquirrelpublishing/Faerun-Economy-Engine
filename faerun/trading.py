"""Guild quotations and finite, dated planning pools. No external orders are sent."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
import hashlib
import json
import math
import re

from .calendar import FESTIVAL_MONTHS, HarptosDate
from .economy import QUALITY_TIERS


CENT = Decimal("0.01")
UNIT_PRECISION = Decimal("0.000001")
MINIMUM_ORDER_GP = Decimal("25")
QUALITIES = dict(QUALITY_TIERS)
FIELDS = {
    "origin", "destination", "commodity", "quantity", "quality", "supply_date",
    "delivery_date", "supply_mode", "purchase_channel", "delivery_terms",
    "transport_mode", "daily_gp", "fixed_gp", "contingency_pct", "return_trip",
    "customer_price_mode", "customer_unit_price", "tax_terms", "deposit_percent",
    "payment_terms", "acceptance_terms", "supplier_tax_exempt", "tax_exemption_reason",
}


class TradeError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def text(value, name, *, required=True, maximum=200):
    if not isinstance(value, str):
        raise TradeError(f"{name} must be text")
    value = value.strip()
    if (required and not value) or len(value) > maximum or "\0" in value:
        raise TradeError(f"{name} must contain 1 to {maximum} characters" if required else
                         f"{name} must contain at most {maximum} characters")
    return value


def number(value, name, *, minimum=0, maximum=1_000_000_000):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)) or str(value).strip() == "":
        raise TradeError(f"{name} must be a number, not an empty value")
    try:
        result = Decimal(str(value))
    except ArithmeticError as exc:
        raise TradeError(f"{name} must be a number") from exc
    if not result.is_finite() or not Decimal(str(minimum)) <= result <= Decimal(str(maximum)):
        raise TradeError(f"{name} must be finite and between {minimum} and {maximum}")
    return result


def integer(value, name, *, minimum=1, maximum=1_000_000):
    result = number(value, name, minimum=minimum, maximum=maximum)
    if result != result.to_integral_value():
        raise TradeError(f"{name} must be a whole number")
    return int(result)


def boolean(value, name):
    if not isinstance(value, bool):
        raise TradeError(f"{name} must be true or false")
    return value


def choice(params, key, default, options):
    value = params.get(key, default)
    if not isinstance(value, str) or value not in options:
        raise TradeError(f"{key} must be one of: {', '.join(options)}")
    return value


def money(value):
    result = Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
    if not result.is_finite() or abs(result) > Decimal("1000000000000"):
        raise TradeError("Invoice amount exceeds supported monetary bounds")
    return float(result)


def unit_money(value):
    return float(Decimal(str(value)).quantize(UNIT_PRECISION, rounding=ROUND_HALF_UP))


def iso(date):
    return f"{date.year:04d}-{date.month:02d}-{date.day:02d}"


def parse_date(value, name):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise TradeError(f"{name} must be a Harptos date in YYYY-MM-DD format")
    year, month, day = map(int, value.split("-"))
    if not 1 <= year <= 9000:
        raise TradeError(f"{name} year must be between 1 and 9000")
    try:
        return HarptosDate(year, month, day)
    except ValueError as exc:
        raise TradeError(f"{name}: {exc}") from exc


@contextmanager
def at_date(world, date):
    saved = world.date
    world.date = date
    try:
        yield
    finally:
        world.date = saved


def supply_window(date, horizon):
    if not math.isfinite(horizon) or not 0 < horizon <= 10:
        raise TradeError("Wholesale planning requires a stock horizon greater than zero and at most ten days")
    width = math.ceil(horizon)
    start = ((date.day - 1) // width) * width + 1
    last = 31 if date.month in FESTIVAL_MONTHS else 30
    end = min(last, start + width - 1)
    first, final = HarptosDate(date.year, date.month, start), HarptosDate(date.year, date.month, end)
    return {"start": iso(first), "end": iso(final),
            "start_day": first.absolute_day(), "end_day": final.absolute_day(),
            "capacity_days": min(horizon, end - start + 1)}


def contract_horizon(world, commodity, quote):
    if quote.inventory.get("enabled"):
        # A daily warehouse snapshot is not a one-day contracting period.
        return min(10.0, world.config.fresh_bread_days) if commodity.id == "bread" else 10.0
    return quote.stock_horizon_days


def apportion(total, weights):
    total = max(0, int(total))
    weight = sum(weights.values())
    shares = {key: total * value / weight if weight else 0.0 for key, value in weights.items()}
    counts = {key: math.floor(value) for key, value in shares.items()}
    for key in sorted(shares, key=lambda key: -(shares[key] - counts[key]))[:total - sum(counts.values())]:
        counts[key] += 1
    return counts


def supply_basis(source, source_id, destination_id, quality, mode, window, allocation=None,
                 purchase_channel="guild", *, period=None):
    days = window["capacity_days"]
    inventory = bool(source.inventory.get("enabled"))
    total_free = source._uncommitted_total()
    if not inventory:
        total_free = min(total_free, math.floor(source.uncommitted_supply_per_day * days + 1e-9))
    free_grades = apportion(total_free, {o["quality"]: o["stock"] for o in source.quality_offers})
    exportable = max(0.0, source.production_per_day + source.imports_per_day - source.demand_per_day)
    if inventory:
        snapshots = period["snapshots"] if period is not None else []
        weighted = [(row, min(1.0, max(0.0, days - index))) for index, row in enumerate(snapshots)]
        production = math.fsum(row["production"] * weight for row, weight in weighted)
        exports = math.fsum(row["exports"] * weight for row, weight in weighted)
        allocated = math.fsum(row["exports_by_destination"].get(destination_id, 0.0) * weight
                              for row, weight in weighted)
    else:
        production = source.production_per_day * days
        exports = source.exports_per_day * days
        allocated = allocation["quantity_per_day"] * days if allocation else 0.0
    export_capacity = math.floor(exports + 1e-9)
    production_capacity = math.floor(production + 1e-9)
    # Closing free stock already excludes modeled exports; these are disjoint pools.
    global_capacity = (total_free + export_capacity if inventory
                       else math.floor(exportable * days + 1e-9))
    if purchase_channel == "producer":
        global_capacity = min(global_capacity, production_capacity)
    return {
        "source_id": source_id, "destination_id": destination_id,
        "commodity": source.commodity, "quality": quality, "mode": mode,
        "start_day": window["start_day"], "end_day": window["end_day"],
        "uncommitted_by_quality": free_grades,
        "allocation_capacity": math.floor(allocated + 1e-9),
        "global_capacity": max(0, global_capacity),
        "purchase_channel": purchase_channel,
        "inventory_enabled": inventory,
        "export_capacity": export_capacity,
        "production_capacity": production_capacity,
        "flow_basis": ("daily inventory window" if period is not None else
                       "closing inventory snapshot" if inventory else "steady-state daily rate"),
    }


def remaining_supply(basis, claims):
    relevant = [
        row for row in claims
        if row["source_id"] == basis["source_id"] and row["commodity"] == basis["commodity"]
        and ((row["mode"] == "uncommitted"
              and (basis.get("inventory_enabled") or row.get("inventory_stock")))
             or (row["start_day"] <= basis["end_day"] and row["end_day"] >= basis["start_day"]))
    ]
    total_claimed = sum(row["quantity"] for row in relevant)
    headroom = max(0, basis["global_capacity"] - total_claimed)
    used = {grade: sum(row["quantity"] for row in relevant
                       if row["mode"] == "uncommitted" and row["quality"] == grade)
            for grade in QUALITIES}
    grade_capacities = dict(basis["uncommitted_by_quality"])
    stock_capacity = sum(grade_capacities.values())
    if basis.get("inventory_enabled"):
        # Protect already-booked later snapshots when reserving an earlier pickup.
        for row in relevant:
            if (row.get("inventory_stock") and row.get("status") == "reserved"
                    and row["end_day"] >= basis["end_day"]):
                committed = row["stock_capacities"]
                stock_capacity = min(stock_capacity, sum(committed.values()))
                grade_capacities = {grade: min(count, committed.get(grade, 0))
                                    for grade, count in grade_capacities.items()}
    available_grades = {grade: max(0, count - used.get(grade, 0))
                        for grade, count in grade_capacities.items()}
    if basis.get("inventory_enabled"):
        stock_headroom = max(0, stock_capacity - sum(used.values()))
        if sum(available_grades.values()) > stock_headroom:
            available_grades = apportion(stock_headroom, available_grades)
    if sum(available_grades.values()) > headroom:
        available_grades = apportion(headroom, available_grades)
    if basis["mode"] == "allocated_export":
        claimed = sum(row["quantity"] for row in relevant if row["mode"] == "allocated_export"
                      and row["destination_id"] == basis["destination_id"])
        capacity = basis["allocation_capacity"]
        available = min(headroom, max(0, capacity - claimed))
        if basis.get("inventory_enabled"):
            exports_claimed = sum(row["quantity"] for row in relevant if row["mode"] == "allocated_export")
            available = min(available, max(0, basis["export_capacity"] - exports_claimed))
    else:
        claimed = used.get(basis["quality"], 0)
        capacity = basis["uncommitted_by_quality"].get(basis["quality"], 0)
        available = available_grades.get(basis["quality"], 0)
    return {"capacity_units": capacity, "claimed_units": claimed, "available_units": available,
            "global_claimed_units": total_claimed, "global_headroom_units": headroom,
            "available_by_quality": available_grades}


def claims_for(world):
    store = getattr(world, "trade_store", None)
    return store.claims() if store is not None else []


def tradable_quote(world, quote, claims=None):
    if getattr(world, "trade_store", None) is None:
        return quote
    claims = claims_for(world) if claims is None else claims
    source_id = world.find_settlement(quote.settlement).id
    window = supply_window(world.date, contract_horizon(world, world.commodities[quote.commodity], quote))
    basis = supply_basis(quote, source_id, "", "standard", "uncommitted", window)
    if quote.inventory.get("enabled"):
        # Modeled exports have already left closing stock; only stock claims encumber it.
        claims = [row for row in claims if row["mode"] == "uncommitted"]
    available = remaining_supply(basis, claims)
    return replace(quote, order_available_by_quality=available["available_by_quality"],
                   order_claimed_stock=available["global_claimed_units"], order_supply_window=window)


def guild_prices(gate, quantity, commodity, export_margin):
    margin = number(export_margin, "export margin", maximum=10)
    minimum = max(1, int((MINIMUM_ORDER_GP / gate).to_integral_value(rounding=ROUND_CEILING)))
    if commodity.unit == "bottle":
        minimum = max(12, minimum)
    multiples = quantity / minimum
    discount = Decimal(".75") if multiples >= 100 else Decimal(".5") if multiples >= 20 else Decimal(".25") if multiples >= 5 else Decimal(0)
    retained = margin * (1 - discount)
    return gate * (1 + retained), minimum, float(discount * 100), float(retained * 100)


def transport_quote(world, origin, destination, pounds, params):
    from .transport import direct_path, plan_shipment, shipment_leg

    mode = params["transport_mode"]
    if mode == "own_caravan" and pounds > 4000:
        raise TradeError("This owned-caravan budget is for one 4,000-lb horse wagon; reduce quantity or use shared freight")
    if origin.id == destination.id:
        local_cost = Decimal(str(params["fixed_gp"])) * (1 + Decimal(str(params["contingency_pct"])) / 100)
        return {"mode": mode, "terms": params["delivery_terms"], "path": [origin.name],
                "one_way_days": 0.0, "cost_days": 0.0, "cost_gp": money(local_cost),
                "benchmark_freight_gp": 0.0, "cargo_lb": pounds, "capacity_lb": 4000 if mode == "own_caravan" else None,
                "carrier": "Local pickup", "basis": "Local transfer; no intersettlement freight."}
    if mode == "own_caravan":
        route = direct_path(world, origin.id, destination.id,
                            lambda edge: edge.days if edge.modes == ("road",) and not edge.inferred else math.inf)
        if route is None:
            raise TradeError("No established road-only route is available for this horse wagon")
        days, benchmark = 0.0, 0.0
        for edge in route:
            leg = shipment_leg(world, edge, pounds, world.edge_risk(edge), 0, {})
            carrier = next(row for row in leg["carrier_loads"] if row["name"] == "Horse freight wagon")
            if carrier["shipments_required"] != 1:
                raise TradeError("The cargo exceeds the owned wagon's capacity")
            days += carrier["travel_days"]
            benchmark += leg["line_haul_gp"]
        cost_days = days
        if params["return_trip"]:
            back = direct_path(world, destination.id, origin.id,
                               lambda edge: edge.days if edge.modes == ("road",) and not edge.inferred else math.inf)
            if back is None:
                raise TradeError("No road-only empty return route is available")
            for edge in back:
                leg = shipment_leg(world, edge, pounds, world.edge_risk(edge), 0, {})
                cost_days += next(row["travel_days"] for row in leg["carrier_loads"]
                                  if row["name"] == "Horse freight wagon")
        cost = (Decimal(str(math.ceil(cost_days))) * Decimal(str(params["daily_gp"]))
                + Decimal(str(params["fixed_gp"]))) * (1 + Decimal(str(params["contingency_pct"])) / 100)
        return {"mode": mode, "terms": params["delivery_terms"],
                "path": [origin.name] + [world.settlements[e.dst].name for e in route],
                "one_way_days": days, "cost_days": math.ceil(cost_days), "cost_gp": money(cost),
                "benchmark_freight_gp": benchmark, "cargo_lb": pounds, "capacity_lb": 4000,
                "carrier": "Horse freight wagon",
                "basis": "Owned-vehicle operating allowance, not a hired freight charge. Optional empty return is a cost allowance, not another shipment or a fleet reservation."}
    plan = plan_shipment(world, origin.id, destination.id, pounds=pounds,
                         fixed=params["fixed_gp"], contingency=params["contingency_pct"],
                         include_events=True, include_inferred=False, allow_special=False)
    if not plan["options"]:
        raise TradeError("No established transport route is available")
    option = min(plan["options"], key=lambda row: row["costs"]["total_gp"])
    return {"mode": mode, "terms": params["delivery_terms"], "path": option["path"],
            "one_way_days": option["travel_days"], "cost_days": option["travel_days"],
            "cost_gp": money(option["costs"]["total_gp"]),
            "benchmark_freight_gp": option["costs"]["line_haul_gp"],
            "cargo_lb": pounds, "capacity_lb": None, "carrier": "Shared freight",
            "basis": "Estimated shared-carrier freight, including route risk; not a booked carrier service."}


def build_quote(world, raw, claims=(), *, revalidate=False):
    from .economy import _commodity_markets

    if not isinstance(raw, dict) or set(raw) - FIELDS:
        raise TradeError("Quote contains unsupported fields")
    origin = world.find_settlement(text(raw.get("origin"), "origin"))
    destination = world.find_settlement(text(raw.get("destination"), "destination"))
    commodity = world.find_commodity(text(raw.get("commodity"), "commodity"))
    quantity = integer(raw.get("quantity"), "quantity")
    quality = choice(raw, "quality", "standard", QUALITIES)
    mode = choice(raw, "supply_mode", "uncommitted", ("uncommitted", "allocated_export"))
    channel = raw.get("purchase_channel", "guild")
    channel = "guild" if channel == "wholesale" else channel
    if channel not in ("producer", "guild"):
        raise TradeError("purchase_channel must be producer or guild")
    terms = choice(raw, "delivery_terms", "pickup", ("pickup", "delivered"))
    transport_mode = choice(raw, "transport_mode", "shared_freight", ("own_caravan", "shared_freight"))
    return_trip = boolean(raw.get("return_trip", False), "return_trip")
    if terms == "delivered" and transport_mode != "shared_freight":
        raise TradeError("Supplier-delivered orders use shared freight; owned-caravan costs belong to pickup orders")
    if return_trip and transport_mode != "own_caravan":
        raise TradeError("An empty return allowance only applies to an owned caravan")
    if mode == "allocated_export" and (quality != "standard" or origin.id == destination.id):
        raise TradeError("Existing export takeovers require different markets and standard grade; graded export inventory is not modeled")
    params = {
        "origin": origin.id, "destination": destination.id, "commodity": commodity.id,
        "quantity": quantity, "quality": quality, "supply_mode": mode,
        "purchase_channel": channel, "delivery_terms": terms, "transport_mode": transport_mode,
        "return_trip": return_trip,
        "daily_gp": float(number(raw.get("daily_gp", 5 if transport_mode == "own_caravan" else 0), "daily_gp")),
        "fixed_gp": float(number(raw.get("fixed_gp", 0), "fixed_gp")),
        "contingency_pct": float(number(raw.get("contingency_pct", 10), "contingency_pct", maximum=100)),
        "customer_price_mode": choice(raw, "customer_price_mode", "retail", ("retail", "wholesale", "agreed")),
        "tax_terms": choice(raw, "tax_terms", "included", ("included", "extra")),
        "deposit_percent": float(number(raw.get("deposit_percent", 0), "deposit_percent", maximum=100)),
        "payment_terms": choice(raw, "payment_terms", "on_delivery", ("on_delivery", "before_dispatch")),
        "acceptance_terms": text(raw.get("acceptance_terms", ""), "acceptance_terms", maximum=2000),
        "supplier_tax_exempt": boolean(raw.get("supplier_tax_exempt", False), "supplier_tax_exempt"),
        "tax_exemption_reason": text(raw.get("tax_exemption_reason", ""), "tax_exemption_reason", required=False, maximum=500),
    }
    if params["supplier_tax_exempt"] and not params["tax_exemption_reason"]:
        raise TradeError("Record the agreed supplier duty exemption; it is not assumed automatically")
    if transport_mode != "own_caravan" and params["daily_gp"] != 0:
        raise TradeError("Daily owned-caravan allowance must be zero for shared freight")
    date = parse_date(raw.get("supply_date", iso(world.date)), "supply_date")
    if ((not revalidate and date.absolute_day() < world.date.absolute_day())
            or date.absolute_day() > world.date.absolute_day() + 365):
        raise TradeError("Supply date must be today or within the next 365 modeled days")
    with at_date(world, date):
        initial = _commodity_markets(world, commodity)[origin.id]
        window = supply_window(date, contract_horizon(world, commodity, initial))
    pickup = parse_date(window["end"], "pickup_date")
    params["supply_date"] = iso(date)
    with at_date(world, pickup):
        markets = _commodity_markets(world, commodity)
        source, buyer = markets[origin.id], markets[destination.id]
        allocation = next((row for row in buyer.sources if row["supply_type"] == "import"
                           and row["source_id"] == origin.id), None) if mode == "allocated_export" else None
        period = None
        if source.inventory.get("enabled"):
            from .seasonal_economy import inventory_window

            period = inventory_window(origin.id, commodity.id,
                                      parse_date(window["start"], "window start"), pickup, world=world)
        basis = supply_basis(source, origin.id, destination.id, quality, mode, window, allocation, channel,
                             period=period)
        if mode == "allocated_export" and (basis["allocation_capacity"] <= 0 if period is not None
                                          else allocation is None):
            raise TradeError("No existing export allocation from this supplier to this destination")
        local = source.producer_gate_price
        if channel == "producer" and (local is None or basis["production_capacity"] <= 0):
            raise TradeError("No supported local producer for this item; select a producing market or guild stock")
        supplied = sum(row["quantity_per_day"] for row in source.sources)
        landed_floor = (sum(row["quantity_per_day"] * row["unit_cost"] for row in source.sources) / supplied
                        if supplied else local)
        if landed_floor is None:
            raise TradeError("No supported inventory cost is available for this guild quote")
        factor = Decimal(str(QUALITIES[quality]))
        gate = (Decimal(str(local if channel == "producer" else landed_floor)) * factor).quantize(
            UNIT_PRECISION, rounding=ROUND_CEILING)
        if gate <= 0:
            raise TradeError("A positive supplier cost floor is required")
        guild_floor = (Decimal(str(landed_floor)) * factor).quantize(UNIT_PRECISION, rounding=ROUND_CEILING)
        if guild_floor <= 0:
            raise TradeError("A positive supported guild inventory cost is required")
        guild, guild_minimum, discount, markup = guild_prices(
            guild_floor, quantity, commodity, world.config.export_margin)
        minimum = (guild_minimum if channel == "guild"
                   else guild_prices(gate, quantity, commodity, world.config.export_margin)[1])
        guild = guild.quantize(UNIT_PRECISION, rounding=ROUND_CEILING)
        if quantity < minimum:
            raise TradeError(f"Merchant guild/producer minimum is {minimum} {commodity.unit} units for this item and grade")
        available = remaining_supply(basis, claims)
        shipping = transport_quote(world, origin, destination, quantity * commodity.weight, params)
        shipping.update({key: params[key] for key in ("daily_gp", "fixed_gp", "contingency_pct", "return_trip")})
        wholesale_delivered = (Decimal(str(allocation["unit_cost"])) if allocation else
                               guild + Decimal(str(shipping["benchmark_freight_gp"])) / quantity)
    earliest = pickup.add_days(math.ceil(shipping["one_way_days"]))
    delivery = (parse_date(raw["delivery_date"], "delivery_date")
                if raw.get("delivery_date") not in (None, "") else earliest)
    if delivery.absolute_day() < earliest.absolute_day() or delivery.absolute_day() > pickup.absolute_day() + 180:
        raise TradeError(f"Delivery must be on or after {iso(earliest)} and within 180 days of pickup")
    params["delivery_date"] = iso(delivery)
    with at_date(world, delivery):
        retail_quote = _commodity_markets(world, commodity)[destination.id]
        offer = next(o for o in retail_quote.quality_offers if o["quality"] == quality)
    if params["customer_price_mode"] == "agreed":
        sale = number(raw.get("customer_unit_price"), "customer_unit_price")
        if sale != sale.quantize(UNIT_PRECISION):
            raise TradeError("Customer unit price supports at most six gp decimal places")
        params["customer_unit_price"] = float(sale)
    elif params["customer_price_mode"] == "wholesale":
        sale = wholesale_delivered
    else:
        sale = Decimal(str(offer["price"]))
    sale = sale.quantize(UNIT_PRECISION, rounding=ROUND_HALF_UP)
    customer_base = Decimal(str(money(sale * quantity)))
    destination_tax = number(destination.tax, "destination duty", maximum=1)
    if params["tax_terms"] == "included":
        customer_net = Decimal(str(money(customer_base / (1 + destination_tax))))
        customer_tax = customer_base - customer_net
        customer_total = customer_base
    else:
        customer_net = customer_base
        customer_tax = Decimal(str(money(customer_net * destination_tax)))
        customer_total = customer_net + customer_tax
    goods = Decimal(str(money((gate if channel == "producer" else guild) * quantity)))
    supplier_tax_rate = Decimal(0) if params["supplier_tax_exempt"] else number(origin.tax, "supplier duty", maximum=1)
    supplier_tax = Decimal(str(money(goods * supplier_tax_rate)))
    shipping_cost = Decimal(str(shipping["cost_gp"]))
    supplier_net = goods + (shipping_cost if terms == "delivered" else 0)
    supplier_total = supplier_net + supplier_tax
    separate_shipping = shipping_cost if terms == "pickup" else Decimal(0)
    estimated_cost = supplier_total + separate_shipping
    amounts = {
        "supplier_net_gp": money(supplier_net), "supplier_tax_gp": money(supplier_tax),
        "supplier_total_gp": money(supplier_total),
        "shipping_paid_separately_gp": money(separate_shipping),
        "customer_net_gp": money(customer_net), "customer_tax_gp": money(customer_tax),
        "customer_total_gp": money(customer_total),
        "customer_deposit_due_gp": money(customer_total * Decimal(str(params["deposit_percent"])) / 100),
        "estimated_cost_gp": money(estimated_cost),
        "estimated_profit_gp": money(customer_net - estimated_cost),
    }
    deposit_net = money(Decimal(str(amounts["customer_deposit_due_gp"])) / (1 + destination_tax))
    amounts["customer_deposit_usable_gp"] = deposit_net
    amounts["customer_deposit_tax_reserve_gp"] = money(
        Decimal(str(amounts["customer_deposit_due_gp"])) - Decimal(str(deposit_net)))
    shipping["earliest_delivery_date"] = iso(earliest)
    warnings = []
    if quantity > available["available_units"]:
        warnings.append("Requested quantity exceeds remaining dated supply; this quote cannot be reserved.")
    if amounts["estimated_profit_gp"] < 0:
        warnings.append("The stated customer price produces an estimated loss after procurement, duties and transport.")
    if guild > Decimal(str(offer["price"])):
        warnings.append("The cost-covering guild rate exceeds the destination's retail reference; wholesale is not guaranteed cheaper in a distorted market.")
    if source.inventory.get("enabled"):
        warnings.append("Free-stock POs use modeled uncommitted warehouse inventory, including stored winter supply. All uncancelled free-stock claims remain encumbered across dates, including after delivery; changing the day or contract window does not replenish stock. Export takeovers remain dated allocations.")
        warnings.append("Inventory lots and PO withdrawals are not replayed by the physical model. Carried-stock accounting therefore subtracts prior claims conservatively, without automatic aging or replenishment credits; it may understate availability after stock turnover.")
    if channel == "producer":
        assumptions_note = "Direct producer quantities are additionally capped by modeled local output; imported or untraced carried stock cannot be procured at an invented producer-gate price."
    else:
        assumptions_note = "Guild inventory costs are modeled weighted supplier costs, not verified invoices or merchant buyback prices."
    if mode == "allocated_export":
        warnings.append("This takes over an existing destination allocation, not additional demand or uncommitted stock. Authorization and a delivery schedule are required.")
    assumptions = [
        assumptions_note,
        "Merchant guild pricing is wholesale, not merchant buyback. Minimum invoice value is 25 gp; bottles have a 12-unit minimum. Catalogue trade units remain indivisible.",
        "Volume tiers reduce only the guild margin: 25% at five minimum lots, 50% at twenty, and 75% at one hundred. Prices never fall below the modeled supplier inventory/gate floor.",
        "Supply is a dated forecast quota, not verified on-hand inventory. Windows align to the contracting horizon (a tenday, or shorter for fresh bread, with daily inventory enabled), not the daily stock snapshot; pickup is at the window end.",
        "Seasonal export and producer limits sum actual daily flows; a fractional horizon prorates only its last day. Carried stock is one closing uncommitted balance, never a sum of daily stocks. Legacy mode retains steady-state rate estimates.",
        "Export takeovers reserve part of an existing modeled allocation to this destination. They must not be added again to demand or macroeconomic trade receipts.",
        "Source duty is budgeted on goods unless an agreed exemption is recorded. Customer included-tax prices are divided by 1 + the destination rate; tax is not profit. These rates are scenario assumptions, not verified tax law.",
        "A customer PO locks the agreed unit price; no spot quantity uplift or buyback discount is added. Deposits are manual cash records, not automatic income or an external charge.",
        "Route and operating costs are estimates. Owned-caravan cost days cover travel and the optional empty return; budget extra loading/trading days through the fixed allowance. Vehicle capacity is checked per order; fleet scheduling, verified physical inventory, financing and insurance are not simulated.",
    ]
    quote = {
        "origin": {"id": origin.id, "name": origin.name},
        "destination": {"id": destination.id, "name": destination.name},
        "commodity": {"id": commodity.id, "name": commodity.name, "unit": commodity.unit, "weight": commodity.weight},
        "quantity": quantity, "quality": quality, "pickup_date": iso(pickup), "delivery_date": iso(delivery),
        "prices": {"producer_gate_gp": float((Decimal(str(local)) * factor).quantize(UNIT_PRECISION, rounding=ROUND_CEILING)) if local is not None else None,
                   "guild_wholesale_gp": unit_money(guild), "delivered_wholesale_gp": unit_money(wholesale_delivered),
                   "retail_gp": offer["price"], "merchant_buyback_gp": offer["buy_price"],
                   "minimum_quantity": minimum, "lot_size": 1,
                   "margin_discount_pct": discount, "guild_markup_pct": markup},
        "supply": {"mode": mode, **available, "window": window,
                   "basis": ("Existing export takeover" if mode == "allocated_export" else
                             "Uncommitted carried inventory after protected reserves and modeled exports"
                             if basis["inventory_enabled"] else
                             "Uncommitted supply after planned local needs and exports"),
                   "claim_scope": ("carried_inventory" if basis["inventory_enabled"] and mode == "uncommitted"
                                   else "dated_flow"),
                   "flow_basis": basis["flow_basis"],
                   "takeover_requires_ack": mode == "allocated_export"},
        "shipping": shipping, "terms": {**{key: params[key] for key in (
            "purchase_channel", "customer_price_mode", "tax_terms", "deposit_percent", "payment_terms",
            "acceptance_terms", "supplier_tax_exempt", "tax_exemption_reason")},
            "customer_unit_price_gp": unit_money(sale)},
        "amounts": amounts, "assumptions": assumptions, "warnings": warnings,
        "reservable": quantity <= available["available_units"],
        "_params": params, "_basis": basis,
    }
    signature = {"prices": quote["prices"], "amounts": amounts, "shipping": shipping,
                 "terms": quote["terms"], "basis": basis, "params": params,
                 "config": world.economy_state_key()[2]}
    quote["_signature"] = hashlib.sha256(json.dumps(signature, sort_keys=True, allow_nan=False).encode()).hexdigest()
    return quote


def public_quote(quote):
    return {key: value for key, value in quote.items() if not key.startswith("_")}
