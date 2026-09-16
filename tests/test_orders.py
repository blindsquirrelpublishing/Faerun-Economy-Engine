"""Deterministic guild quotes and isolated, persistent purchase-order ledgers."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import math
import sqlite3
from threading import Barrier, Event
from types import SimpleNamespace

import pytest

from faerun import economy, orders, seasonal_economy, trading
from faerun.calendar import HarptosDate
from faerun.models import C, PriceQuote, S
from faerun.orders import APPLICATION_ID, TradeStore
from faerun.trading import TradeError, build_quote, guild_prices, parse_date, remaining_supply
from faerun.world import EconomyConfig, Edge, World


def parameters(**changes):
    return {
        "origin": "source", "destination": "buyer", "commodity": "wine",
        "quantity": 120, "quality": "standard", "supply_date": "1492-06-11",
        "acceptance_terms": "Inspect bottle count and agreed grade on arrival.",
        "contingency_pct": 0, **changes,
    }


def market(name):
    return PriceQuote(
        settlement=name, commodity="wine", commodity_name="Wine",
        category="drink", production_type="vint", unit="bottle",
        base_price=3, price=10, buy_price=6, multiplier=10 / 3,
        availability="plentiful", stock=10000, supply_index=1, demand_index=1,
        production_per_day=1000, demand_per_day=100, scarcity=1,
        exports_per_day=100, stock_horizon_days=10, producer_gate_price=3,
        quality_offers=[
            {"quality": grade, "price_factor": factor, "price": 10 * factor,
             "buy_price": 6 * factor, "stock": stock}
            for grade, factor, stock in [
                ("basic", .7, 0), ("standard", 1, 7500),
                ("fine", 1.75, 2500), ("masterwork", 4, 0),
            ]
        ],
        sources=[{"supply_type": "local", "source_id": name.lower(),
                  "quantity_per_day": 1000, "unit_cost": 3}],
    )


def make_world(store):
    world = World(
        settlements=[S("Source", "Test", "test", 100, 0, 0, tax=.05),
                     S("Buyer", "Test", "test", 100, 1, 0, tax=.10)],
        commodities=[C("wine", "Wine", "drink", 3, unit="bottle", weight=2,
                       produced_by="vint")],
        businesses=[], date=HarptosDate(1492, 6, 11),
        config=EconomyConfig(noise=0, expanded_requirements=False,
                             seasonal_inventory=False),
        trade_store=store,
    )
    world._edges = {
        "source": [Edge("source", "buyer", 48, 1, "road")],
        "buyer": [Edge("buyer", "source", 48, 1, "road")],
    }
    return world


def flow_period(production, exports, destination="buyer"):
    return {
        "days": len(production),
        "totals": {"production": math.fsum(production), "exports": math.fsum(exports)},
        "exports_by_destination": {destination: math.fsum(exports)},
        "snapshots": [
            {"production": made, "exports": shipped,
             "exports_by_destination": {destination: shipped}}
            for made, shipped in zip(production, exports, strict=True)
        ],
    }


@pytest.fixture
def desk(tmp_path, monkeypatch):
    quotes = {"source": market("Source"), "buyer": market("Buyer")}
    quotes["buyer"].sources = [
        {"supply_type": "import", "source_id": "source",
         "quantity_per_day": 100, "unit_cost": 4},
    ]
    store = TradeStore(tmp_path / "ledger.sqlite3")
    world = make_world(store)
    # Bypass the large economy/inventory engines; only PO behavior is under test.
    monkeypatch.setattr(economy, "_commodity_markets", lambda *args, **kwargs: quotes)

    def window(origin, commodity, start, end, *, world):
        source = quotes[origin]
        days = end.absolute_day() - start.absolute_day() + 1
        return flow_period([source.production_per_day] * days, [source.exports_per_day] * days)

    monkeypatch.setattr(seasonal_economy, "inventory_window", window)

    def shipping(world, origin, destination, pounds, params):
        return {
            "mode": params["transport_mode"], "terms": params["delivery_terms"],
            "path": [origin.name, destination.name], "one_way_days": 2.2,
            "cost_days": 3, "cost_gp": 17.25, "benchmark_freight_gp": 8.5,
            "cargo_lb": pounds, "capacity_lb": None, "carrier": "Test wagon",
            "basis": "Deterministic test allowance",
        }

    monkeypatch.setattr(trading, "transport_quote", shipping)
    return SimpleNamespace(world=world, store=store, quotes=quotes, window=window,
                           real_transport=REAL_TRANSPORT)


REAL_TRANSPORT = trading.transport_quote


def test_producer_contract_cannot_claim_imported_inventory_as_local_output(desk):
    source = desk.quotes["source"]
    source.production_per_day = 1
    source.imports_per_day = 2000
    quote = build_quote(desk.world, parameters(purchase_channel="producer"))
    assert quote["supply"]["global_headroom_units"] == 10
    assert quote["supply"]["available_units"] <= 10
    assert not quote["reservable"]


def test_guild_can_take_over_existing_warehouse_exports_without_new_production(desk):
    source = desk.quotes["source"]
    source.production_per_day = 0
    source.inventory = {"enabled": True, "uncommitted_stock": 5000}
    quote = build_quote(desk.world, parameters(supply_mode="allocated_export", purchase_channel="guild"))
    assert quote["supply"]["global_headroom_units"] == 6000
    assert quote["supply"]["available_units"] == 1000
    assert quote["reservable"]
    reserved = reserve(desk, supply_mode="allocated_export", purchase_channel="guild")
    again = desk.store.quote(desk.world, parameters(supply_mode="allocated_export", purchase_channel="guild"))
    assert again["supply"]["available_units"] == 1000 - reserved["quote"]["quantity"]


def test_daily_inventory_snapshot_keeps_a_tenday_contract_window(desk):
    source = desk.quotes["source"]
    source.stock_horizon_days = 1
    source.inventory = {"enabled": True, "uncommitted_stock": 5000}
    quote = build_quote(desk.world, parameters(quantity=1000, supply_mode="allocated_export",
                                              purchase_channel="guild"))
    assert quote["pickup_date"] == "1492-06-20"
    assert quote["supply"]["window"]["capacity_days"] == 10
    assert quote["supply"]["capacity_units"] == 1000
    assert quote["reservable"]


def warehouse(desk, quantity=200):
    source = desk.quotes["source"]
    source.production_per_day = 0
    source.imports_per_day = 0
    source.exports_per_day = 0
    source.stock = quantity
    source.stock_horizon_days = 1
    source.inventory = {"enabled": True, "uncommitted_stock": quantity}
    for offer in source.quality_offers:
        offer["stock"] = quantity if offer["quality"] == "standard" else 0
    return source


def test_winter_guild_stock_does_not_require_daily_production_surplus(desk):
    warehouse(desk)
    quote = build_quote(desk.world, parameters(purchase_channel="guild"))
    assert quote["supply"]["available_units"] == 200
    assert quote["reservable"]
    with pytest.raises(TradeError, match="No supported local producer"):
        build_quote(desk.world, parameters(purchase_channel="producer"))


def test_warehouse_claim_survives_day_window_and_database_restart(desk):
    warehouse(desk)
    reserve(desk, purchase_channel="guild")
    desk.world.trade_store = TradeStore(desk.store.path)
    for day in (12, 21):
        quote = desk.world.trade_store.quote(
            desk.world, parameters(supply_date=f"1492-06-{day}", purchase_channel="guild"))
        assert quote["supply"]["available_units"] == 80
        assert not quote["reservable"]
        desk.world.date = HarptosDate(1492, 6, day)
        public = trading.tradable_quote(desk.world, desk.quotes["source"])
        assert public.uncommitted_stock == 80
        assert desk.quotes["source"].inventory["uncommitted_stock"] == 200


def test_warehouse_cancellation_releases_cross_window_claim(desk):
    warehouse(desk)
    order = reserve(desk, purchase_channel="guild")
    transition(desk, order, "cancel")
    quote = desk.store.quote(desk.world, parameters(supply_date="1492-06-21"))
    assert quote["supply"]["available_units"] == 200


def test_warehouse_delivered_stock_is_not_resold_in_later_window(desk):
    warehouse(desk)
    order = reserve(desk, purchase_channel="guild")
    desk.world.date = parse_date(order["quote"]["pickup_date"], "pickup")
    order = pay(desk, order, "supplier_payment", order["quote"]["amounts"]["supplier_total_gp"])
    order = transition(desk, order, "dispatch")
    desk.world.date = desk.world.date.add_days(3)
    transition(desk, order, "deliver", accepted=True)
    quote = desk.store.quote(desk.world, parameters(supply_date="1492-07-01"))
    assert quote["supply"]["available_units"] == 80


def test_warehouse_future_reservation_protects_its_smaller_stock_forecast(desk):
    source = warehouse(desk)
    reserve(desk, quantity=150, supply_date="1492-06-21")
    # Earlier inventory can be larger than the already-promised later snapshot.
    source.inventory["uncommitted_stock"] = source.stock = 1000
    source.quality_offers[1]["stock"] = 1000
    quote = desk.store.quote(desk.world, parameters(quantity=100))
    assert quote["supply"]["available_units"] == 50
    assert not quote["reservable"]


def test_warehouse_later_stock_growth_does_not_reset_consumed_claims(desk):
    source = warehouse(desk)
    reserve(desk, quantity=150)
    source.inventory["uncommitted_stock"] = source.stock = 300
    source.quality_offers[1]["stock"] = 300
    quote = desk.store.quote(desk.world, parameters(supply_date="1492-06-21"))
    assert quote["supply"]["available_units"] == 150


def test_warehouse_future_grade_budget_cannot_be_reclassified(desk):
    source = warehouse(desk)
    source.quality_offers[1]["stock"] = source.quality_offers[2]["stock"] = 100
    reserve(desk, quantity=80, quality="fine", supply_date="1492-06-21")
    source.inventory["uncommitted_stock"] = source.stock = 1000
    source.quality_offers[1]["stock"] = 900
    quote = desk.store.quote(desk.world, parameters(quantity=120))
    assert quote["supply"]["available_units"] == 100
    assert not quote["reservable"]


def test_warehouse_exports_and_closing_free_stock_are_separate_pools(desk):
    source = warehouse(desk)
    source.exports_per_day = 100
    reserve(desk, supply_mode="allocated_export")
    free = desk.store.quote(desk.world, parameters())
    assert free["supply"]["available_units"] == 200
    assert free["supply"]["claim_scope"] == "carried_inventory"
    later = desk.store.quote(desk.world, parameters(
        supply_mode="allocated_export", supply_date="1492-06-21"))
    assert later["supply"]["available_units"] == 1000
    assert later["supply"]["claim_scope"] == "dated_flow"


def test_seasonal_export_takeover_sums_actual_days_not_pickup_rate(desk, monkeypatch):
    source = warehouse(desk, 0)
    source.exports_per_day = 100
    period = flow_period([0] * 10, [0] * 9 + [100])
    monkeypatch.setattr(seasonal_economy, "inventory_window", lambda *args, **kwargs: period)
    quote = build_quote(desk.world, parameters(quantity=120, supply_mode="allocated_export"))
    assert quote["supply"]["capacity_units"] == 100
    assert quote["supply"]["global_headroom_units"] == 100
    assert not quote["reservable"]


def test_seasonal_takeover_can_use_earlier_exports_when_pickup_day_has_none(desk, monkeypatch):
    warehouse(desk, 0)
    desk.quotes["buyer"].sources = []
    period = flow_period([0] * 10, [25] * 9 + [0])
    monkeypatch.setattr(seasonal_economy, "inventory_window", lambda *args, **kwargs: period)
    quote = build_quote(desk.world, parameters(supply_mode="allocated_export"))
    assert quote["supply"]["capacity_units"] == 225
    assert quote["reservable"]


def test_producer_contract_uses_actual_window_production(desk, monkeypatch):
    source = warehouse(desk)
    source.production_per_day = 100
    period = flow_period([0] * 9 + [100], [0] * 10)
    monkeypatch.setattr(seasonal_economy, "inventory_window", lambda *args, **kwargs: period)
    quote = build_quote(desk.world, parameters(purchase_channel="producer"))
    assert quote["supply"]["global_headroom_units"] == 100
    assert not quote["reservable"]
    source.production_per_day = 0
    period = flow_period([20] * 9 + [0], [0] * 10)
    quote = build_quote(desk.world, parameters(purchase_channel="producer"))
    assert quote["supply"]["global_headroom_units"] == 180
    assert quote["reservable"]


def test_reserve_replenishment_imports_do_not_become_free_contract_stock(desk):
    source = warehouse(desk, 0)
    source.imports_per_day = 1000
    source.inventory.update(closing_stock=1000, reserve_target=1000)
    quote = build_quote(desk.world, parameters())
    assert quote["supply"]["available_units"] == 0
    assert not quote["reservable"]


def test_public_carried_stock_view_does_not_replay_windows_or_deduct_exports(desk, monkeypatch):
    source = warehouse(desk)
    source.exports_per_day = 100
    reserve(desk, supply_mode="allocated_export")

    def unexpected_window(*args, **kwargs):
        pytest.fail("Public closing-stock views must not replay a window for every material")

    monkeypatch.setattr(seasonal_economy, "inventory_window", unexpected_window)
    public = trading.tradable_quote(desk.world, source)
    assert public.uncommitted_stock == 200
    assert public.order_claimed_stock == 0


def test_fractional_contract_horizon_weights_only_the_partial_last_day(desk):
    source = warehouse(desk)
    window = trading.supply_window(HarptosDate(1492, 6, 1), 2.5)
    basis = trading.supply_basis(
        source, "source", "buyer", "standard", "allocated_export", window,
        period=flow_period([0, 0, 100], [0, 0, 40]),
    )
    assert basis["production_capacity"] == 50
    assert basis["export_capacity"] == basis["allocation_capacity"] == 20


def test_guild_reference_uses_its_own_inventory_floor_for_producer_purchase(desk):
    desk.quotes["source"].sources = [
        {"supply_type": "local", "source_id": "source", "quantity_per_day": 500, "unit_cost": 3},
        {"supply_type": "import", "source_id": "buyer", "quantity_per_day": 500, "unit_cost": 9},
    ]
    producer = build_quote(desk.world, parameters(purchase_channel="producer"))
    guild = build_quote(desk.world, parameters(purchase_channel="guild"))
    assert producer["prices"]["guild_wholesale_gp"] == guild["prices"]["guild_wholesale_gp"]
    assert producer["prices"]["guild_wholesale_gp"] >= 6
    assert producer["amounts"]["supplier_net_gp"] == 360
    assert producer["terms"]["purchase_channel"] == "producer"


def reserve(desk, *, reference="PO-1", quote=None, **changes):
    quote = quote or desk.store.quote(desk.world, parameters(**changes))
    return desk.store.reserve(
        desk.world, quote_id=quote["id"], customer_name="Example Guild",
        po_reference=reference, terms_accepted=True,
        allocation_authorized=quote["supply"]["mode"] == "allocated_export",
    )


def pay(desk, order, kind, amount, reference=None):
    return desk.store.payment(
        desk.world, order_id=order["id"], kind=kind, amount_gp=amount,
        reference=reference or kind,
    )


def transition(desk, order, action, **kwargs):
    return desk.store.transition(
        desk.world, order_id=order["id"], action=action,
        version=order["version"], **kwargs,
    )


def fund(desk, order):
    order = pay(desk, order, "supplier_payment", order["quote"]["amounts"]["supplier_total_gp"])
    deposit = order["quote"]["amounts"]["customer_deposit_due_gp"]
    if deposit:
        order = pay(desk, order, "customer_payment", deposit)
    return order


def small_pool(desk, total=120):
    source = desk.quotes["source"]
    source.production_per_day = total / 10
    source.demand_per_day = source.exports_per_day = 0
    source.stock = total
    for offer in source.quality_offers:
        offer["stock"] = total if offer["quality"] == "standard" else 0


@pytest.mark.parametrize("quantity,discount,rate", [
    (12, 0, "3.36"), (60, 25, "3.2700"), (240, 50, "3.180"),
    (1200, 75, "3.0900"),
])
def test_guild_volume_tiers_discount_only_margin(desk, quantity, discount, rate):
    price, minimum, actual_discount, markup = guild_prices(
        Decimal("3"), quantity, desk.world.commodities["wine"], .12)
    assert minimum == 12
    assert actual_discount == discount
    assert price == Decimal(rate) >= Decimal("3")
    assert markup == pytest.approx(12 * (1 - discount / 100))


def test_supplier_floor_and_bottle_minimum_are_not_pack_multiples(desk):
    with pytest.raises(TradeError, match="minimum is 12"):
        build_quote(desk.world, parameters(quantity=11))
    quote = desk.store.quote(desk.world, parameters(quantity=1000))
    assert quote["prices"]["minimum_quantity"] == 12
    assert quote["prices"]["lot_size"] == 1
    assert quote["quantity"] == 1000 and quote["reservable"]
    assert reserve(desk, quote=quote)["quote"]["quantity"] == 1000


def test_twenty_five_gp_floor_raises_minimum_for_cheap_units(desk):
    source = desk.quotes["source"]
    source.producer_gate_price = .2
    source.sources[0]["unit_cost"] = .2
    with pytest.raises(TradeError, match="minimum is 125"):
        build_quote(desk.world, parameters(quantity=124))
    quote = build_quote(desk.world, parameters(quantity=125))
    assert quote["prices"]["minimum_quantity"] == 125
    assert quote["amounts"]["supplier_net_gp"] >= 25


def test_imported_guild_floor_and_grade_are_distinct_from_producer_gate(desk):
    source = desk.quotes["source"]
    source.sources = [
        {"quantity_per_day": 100, "unit_cost": 3},
        {"quantity_per_day": 300, "unit_cost": 7},
    ]
    guild = build_quote(desk.world, parameters(quality="fine"))
    producer = build_quote(desk.world, parameters(quality="fine", purchase_channel="producer"))
    assert guild["prices"]["producer_gate_gp"] == 5.25
    assert guild["prices"]["guild_wholesale_gp"] >= 6 * 1.75
    assert producer["amounts"]["supplier_net_gp"] == 120 * 5.25
    assert guild["amounts"]["supplier_net_gp"] > producer["amounts"]["supplier_net_gp"]


@pytest.mark.parametrize("value", [
    "1492-13-01", "1492-00-01", "1492-06-31", "1492-01-32",
    "1492-6-11", "11 Kythorn 1492", "0000-01-01", "9001-01-01", None,
], ids=["month13", "month0", "nonfestival31", "day32", "unpadded", "name",
        "year0", "year9001", "null"])
def test_dates_reject_lenient_or_invalid_harptos_inputs(value):
    with pytest.raises(TradeError):
        parse_date(value, "supply_date")


def test_festival_window_is_one_day_and_world_date_is_restored(desk):
    original = desk.world.date
    quote = build_quote(desk.world, parameters(supply_date="1492-07-31"))
    assert parse_date("1492-07-31", "festival").festival
    assert quote["supply"]["window"]["start"] == "1492-07-31"
    assert quote["supply"]["window"]["end"] == "1492-07-31"
    assert quote["supply"]["window"]["capacity_days"] == 1
    assert quote["pickup_date"] == "1492-07-31"
    assert quote["delivery_date"] == "1492-08-03"
    assert desk.world.date is original


def test_quote_prices_at_pickup_and_delivery_not_current_date(desk, monkeypatch):
    seen = []
    original = desk.world.date

    def markets(world, commodity):
        seen.append(world.date)
        return desk.quotes

    monkeypatch.setattr(economy, "_commodity_markets", markets)
    quote = build_quote(desk.world, parameters(delivery_date="1492-07-04"))
    assert seen == [HarptosDate(1492, 6, 11), HarptosDate(1492, 6, 20),
                    HarptosDate(1492, 7, 4)]
    assert quote["shipping"]["earliest_delivery_date"] == "1492-06-23"
    assert desk.world.date is original


@pytest.mark.parametrize("stage", ["market", "transport"])
def test_quote_restores_world_date_when_calculation_raises(desk, monkeypatch, stage):
    original = desk.world.date

    def fail(*args, **kwargs):
        assert desk.world.date != original
        raise RuntimeError("test calculation failure")

    if stage == "market":
        monkeypatch.setattr(economy, "_commodity_markets", fail)
    else:
        monkeypatch.setattr(trading, "transport_quote", fail)
    with pytest.raises(RuntimeError, match="test calculation"):
        build_quote(desk.world, parameters(supply_date="1492-07-01"))
    assert desk.world.date is original


def test_past_and_distant_dates_and_early_delivery_are_rejected(desk):
    for changes in [
        {"supply_date": "1492-06-10"},
        {"supply_date": trading.iso(desk.world.date.add_days(366))},
        {"delivery_date": "1492-06-22"}, {"delivery_date": "1493-06-01"},
    ]:
        with pytest.raises(TradeError):
            build_quote(desk.world, parameters(**changes))
    desk.world.date = HarptosDate(1492, 6, 20)
    assert build_quote(desk.world, parameters(), revalidate=True)["pickup_date"] == "1492-06-20"


@pytest.mark.parametrize("terms,net,tax,total", [
    ("included", 1200, 120, 1320), ("extra", 1320, 132, 1452),
])
def test_customer_tax_and_deposit_are_reconciled(desk, terms, net, tax, total):
    quote = build_quote(desk.world, parameters(
        customer_price_mode="agreed", customer_unit_price=11,
        tax_terms=terms, deposit_percent=50))
    amounts = quote["amounts"]
    assert amounts["customer_net_gp"] == net
    assert amounts["customer_tax_gp"] == tax
    assert amounts["customer_total_gp"] == total
    assert amounts["customer_deposit_due_gp"] == total / 2
    assert amounts["customer_deposit_usable_gp"] == net / 2
    assert amounts["customer_deposit_tax_reserve_gp"] == tax / 2
    assert amounts["estimated_profit_gp"] == pytest.approx(net - amounts["estimated_cost_gp"])


def test_supplier_tax_exemption_must_be_explicit_and_documented(desk):
    with pytest.raises(TradeError, match="exemption"):
        build_quote(desk.world, parameters(supplier_tax_exempt=True))
    regular = build_quote(desk.world, parameters())
    exempt = build_quote(desk.world, parameters(
        supplier_tax_exempt=True, tax_exemption_reason="Supplier confirmed resale exemption"))
    assert regular["amounts"]["supplier_tax_gp"] > 0
    assert exempt["amounts"]["supplier_tax_gp"] == 0
    assert exempt["amounts"]["supplier_total_gp"] == regular["amounts"]["supplier_net_gp"]
    assert exempt["amounts"]["customer_tax_gp"] == regular["amounts"]["customer_tax_gp"]


@pytest.mark.parametrize("terms,mode", [
    ("pickup", "own_caravan"), ("pickup", "shared_freight"),
    ("delivered", "shared_freight"),
])
def test_shipping_is_counted_exactly_once(desk, terms, mode):
    quote = build_quote(desk.world, parameters(delivery_terms=terms, transport_mode=mode))
    amount = quote["amounts"]
    goods = Decimal(str(quote["prices"]["guild_wholesale_gp"])) * 120
    goods = goods.quantize(Decimal(".01"))
    tax = (goods * Decimal(".05")).quantize(Decimal(".01"))
    assert amount["estimated_cost_gp"] == float(goods + tax + Decimal("17.25"))
    assert amount["shipping_paid_separately_gp"] == (17.25 if terms == "pickup" else 0)
    assert amount["supplier_net_gp"] == float(goods + (Decimal("17.25") if terms == "delivered" else 0))


def test_real_owned_wagon_round_trip_is_operating_cost_not_hired_freight(desk, monkeypatch):
    monkeypatch.setattr(trading, "transport_quote", desk.real_transport)
    monkeypatch.setattr(desk.world, "edge_risk", lambda edge: 0)
    quote = build_quote(desk.world, parameters(
        transport_mode="own_caravan", daily_gp=5, fixed_gp=2,
        contingency_pct=10, return_trip=True))
    shipping = quote["shipping"]
    assert shipping["one_way_days"] == 2
    assert shipping["cost_days"] == 4
    assert shipping["cost_gp"] == 24.2
    assert shipping["benchmark_freight_gp"] > 0
    assert quote["amounts"]["shipping_paid_separately_gp"] == 24.2
    assert quote["amounts"]["estimated_cost_gp"] == pytest.approx(
        quote["amounts"]["supplier_total_gp"] + 24.2)
    with pytest.raises(TradeError, match="4,000"):
        build_quote(desk.world, parameters(quantity=2001, transport_mode="own_caravan"))


def test_real_shared_freight_and_missing_established_route(desk, monkeypatch):
    monkeypatch.setattr(trading, "transport_quote", desk.real_transport)
    monkeypatch.setattr(desk.world, "edge_risk", lambda edge: 0)
    quote = build_quote(desk.world, parameters(fixed_gp=2))
    shipping = quote["shipping"]
    assert shipping["carrier"] == "Shared freight"
    assert shipping["one_way_days"] == 2
    assert shipping["cost_gp"] == trading.money(shipping["benchmark_freight_gp"] + 2)
    desk.world._edges = {}
    with pytest.raises(TradeError, match="route"):
        build_quote(desk.world, parameters())


@pytest.mark.parametrize("field,value", [
    ("quantity", True), ("quantity", 0), ("quantity", -1),
    ("quantity", 12.5), ("quantity", ""), ("quantity", None),
    ("quantity", "NaN"), ("quantity", "Infinity"), ("quantity", 1000001),
    ("daily_gp", -1), ("daily_gp", "NaN"), ("fixed_gp", float("inf")),
    ("contingency_pct", 101), ("deposit_percent", -1), ("deposit_percent", 101),
    ("supplier_tax_exempt", "false"), ("return_trip", 1),
], ids=["bool", "zero", "negative", "fraction", "empty", "null", "nan", "inf",
        "huge", "daily-negative", "daily-nan", "fixed-inf", "contingency",
        "deposit-negative", "deposit-high", "exempt-text", "return-number"])
def test_quote_rejects_invalid_numeric_and_boolean_values(desk, field, value):
    with pytest.raises(TradeError):
        build_quote(desk.world, parameters(**{field: value}))


@pytest.mark.parametrize("changes", [
    {"delivery_terms": "delivered", "transport_mode": "own_caravan"},
    {"return_trip": True}, {"daily_gp": 3},
    {"customer_price_mode": "agreed", "customer_unit_price": .1234567},
    {"supplier_total_gp": 1}, {"quality": "legendary"}, {"acceptance_terms": ""},
], ids=["delivered-own", "shared-return", "shared-daily", "unit-precision",
        "untrusted-total", "unknown-grade", "missing-acceptance"])
def test_quote_rejects_incompatible_or_untrusted_terms(desk, changes):
    with pytest.raises(TradeError):
        build_quote(desk.world, parameters(**changes))


def test_public_quote_copper_totals_and_unit_prices_reconcile(desk):
    quote = desk.store.quote(desk.world, parameters(
        quantity=127, customer_price_mode="agreed", customer_unit_price=.333333,
        deposit_percent=33, tax_terms="extra"))
    assert not any(key.startswith("_") for key in quote)
    for value in quote["amounts"].values():
        assert Decimal(str(value)) == Decimal(str(value)).quantize(Decimal(".01"))
    amounts = {key: Decimal(str(value)) for key, value in quote["amounts"].items()}
    assert amounts["customer_net_gp"] == Decimal("42.33")
    assert amounts["customer_total_gp"] == amounts["customer_net_gp"] + amounts["customer_tax_gp"]
    assert amounts["supplier_total_gp"] == amounts["supplier_net_gp"] + amounts["supplier_tax_gp"]
    assert amounts["customer_deposit_due_gp"] == amounts["customer_deposit_usable_gp"] + amounts["customer_deposit_tax_reserve_gp"]
    assert amounts["estimated_cost_gp"] == amounts["supplier_total_gp"] + amounts["shipping_paid_separately_gp"]


@pytest.mark.parametrize("channel,price_key,locked_price", [
    ("producer", "producer_gate_gp", "1.000001"),
    ("guild", "guild_wholesale_gp", "1.030002"),
])
def test_supplier_floor_rounds_up_before_locked_unit_invoice_multiplication(
        desk, channel, price_key, locked_price):
    small_pool(desk, 100000)
    desk.quotes["source"].producer_gate_price = 1.00000001
    desk.quotes["source"].sources[0]["unit_cost"] = 1.00000001
    quote = desk.store.quote(desk.world, parameters(quantity=100000, purchase_channel=channel))
    assert Decimal(str(quote["prices"][price_key])) == Decimal(locked_price)
    expected = Decimal(locked_price) * 100000
    assert Decimal(str(quote["amounts"]["supplier_net_gp"])) == expected
    assert reserve(desk, quote=quote)["quote"]["amounts"] == quote["amounts"]


@pytest.mark.parametrize("mode,locked_price", [
    ("retail", "1.123456"), ("wholesale", "3.090123"),
])
def test_automatic_customer_invoice_uses_six_decimal_locked_price(
        desk, monkeypatch, mode, locked_price):
    small_pool(desk, 100000)
    for offer in desk.quotes["buyer"].quality_offers:
        offer["price"] = 1.12345649
    original = trading.transport_quote

    def shipping(*args, **kwargs):
        return {**original(*args, **kwargs), "benchmark_freight_gp": 12.34567}

    monkeypatch.setattr(trading, "transport_quote", shipping)
    quote = desk.store.quote(desk.world, parameters(
        quantity=100000, customer_price_mode=mode, tax_terms="extra"))
    assert Decimal(str(quote["terms"]["customer_unit_price_gp"])) == Decimal(locked_price)
    assert Decimal(str(quote["amounts"]["customer_net_gp"])) == Decimal(locked_price) * 100000
    assert reserve(desk, quote=quote)["quote"] == quote


def test_claims_change_availability_but_not_pricing_signature(desk):
    small_pool(desk)
    before = build_quote(desk.world, parameters(quantity=80))
    reserve(desk, quantity=80)
    after = build_quote(desk.world, parameters(quantity=80), desk.store.claims())
    assert before["_signature"] == after["_signature"]
    assert before["amounts"] == after["amounts"]
    assert before["supply"]["available_units"] == 120
    assert after["supply"]["available_units"] == 40
    assert not after["reservable"]


@pytest.mark.parametrize("inventory", [False, True], ids=["dated-flow", "carried-stock"])
def test_competing_connections_atomically_reserve_only_available_supply(desk, monkeypatch, inventory):
    if inventory:
        warehouse(desk, 120)
    else:
        small_pool(desk)
    dates = ("1492-06-11", "1492-06-21" if inventory else "1492-06-11")
    quotes = [desk.store.quote(desk.world, parameters(quantity=80, supply_date=date)) for date in dates]
    stores = [TradeStore(desk.store.path), TradeStore(desk.store.path)]
    worlds = [make_world(store) for store in stores]
    barrier = Barrier(2)
    original = orders.build_quote

    def simultaneous_validation(*args, **kwargs):
        result = original(*args, **kwargs)
        barrier.wait(timeout=10)
        return result

    monkeypatch.setattr(orders, "build_quote", simultaneous_validation)

    def attempt(index):
        try:
            return stores[index].reserve(
                worlds[index], quote_id=quotes[index]["id"],
                customer_name="Competing customer", po_reference=f"PO-{index}",
                terms_accepted=True)
        except TradeError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, range(2)))
    successful = [result for result in results if isinstance(result, dict)]
    rejected = [result for result in results if isinstance(result, TradeError)]
    assert len(successful) == len(rejected) == 1
    assert rejected[0].status == 409
    assert "Only 40 units remain" in str(rejected[0])
    assert sum(row["quantity"] for row in desk.store.claims()) == 80
    assert desk.store.list_orders(desk.world)["total"] == 1


def test_expired_quote_does_not_write_an_order(desk):
    quote = desk.store.quote(desk.world, parameters())
    with desk.store.connection(write=True) as db:
        snapshot = desk.store._quote(db, quote["id"])
        snapshot["expires_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        db.execute("UPDATE trade_quotes SET snapshot=?,expires_at=? WHERE id=?",
                   (json.dumps(snapshot), snapshot["expires_at"], quote["id"]))
    with pytest.raises(TradeError, match="expired"):
        reserve(desk, quote=quote)
    assert desk.store.list_orders(desk.world)["total"] == 0
    assert desk.store.claims() == []


@pytest.mark.parametrize("change", ["price", "capacity", "config", "past-pickup"])
def test_stale_quote_rejected_without_claims(desk, change):
    quote = desk.store.quote(desk.world, parameters())
    if change == "price":
        desk.quotes["source"].sources[0]["unit_cost"] = 4
    elif change == "capacity":
        desk.quotes["source"].production_per_day -= 1
    elif change == "config":
        desk.world.config.export_margin = .2
    else:
        desk.world.date = HarptosDate(1492, 6, 21)
    with pytest.raises(TradeError) as error:
        reserve(desk, quote=quote)
    assert error.value.status == 409
    assert desk.store.claims() == []


def test_reservation_terms_authorization_and_po_reference_idempotency(desk):
    quote = desk.store.quote(desk.world, parameters(supply_mode="allocated_export"))
    kwargs = dict(quote_id=quote["id"], customer_name=" Example Guild ", po_reference=" PO-1 ")
    with pytest.raises(TradeError, match="terms"):
        desk.store.reserve(desk.world, **kwargs)
    with pytest.raises(TradeError, match="authorization"):
        desk.store.reserve(desk.world, **kwargs, terms_accepted=True)
    order = desk.store.reserve(desk.world, **kwargs, terms_accepted=True, allocation_authorized=True)
    duplicate = desk.store.reserve(
        desk.world, quote_id=quote["id"], customer_name="example guild",
        po_reference="po-1", terms_accepted=True)
    assert duplicate["id"] == order["id"]
    assert duplicate["version"] == order["version"]
    assert len(duplicate["audit"]) == 1
    with pytest.raises(TradeError, match="different PO"):
        reserve(desk, quote=quote, reference="OTHER")
    with pytest.raises(TradeError, match="reference is already"):
        reserve(desk, reference="po-1")
    assert desk.store.list_orders(desk.world)["total"] == 1


def test_grade_pool_does_not_borrow_from_other_grades(desk):
    source = desk.quotes["source"]
    source.production_per_day = 20
    source.exports_per_day = source.demand_per_day = 0
    source.stock = 200
    for offer in source.quality_offers:
        offer["stock"] = 100 if offer["quality"] in ("standard", "fine") else 0
    standard = reserve(desk, quantity=100)
    assert standard["quote"]["supply"]["capacity_units"] == 100
    quote = desk.store.quote(desk.world, parameters(quantity=12))
    assert quote["supply"]["available_units"] == 0 and not quote["reservable"]
    fine = reserve(desk, reference="FINE", quantity=100, quality="fine")
    assert fine["quote"]["supply"]["available_units"] == 100
    assert sum(row["quantity"] for row in desk.store.claims()) == 200


def test_overlapping_windows_and_allocations_share_global_capacity():
    basis = {
        "source_id": "source", "destination_id": "buyer", "commodity": "wine",
        "quality": "standard", "mode": "uncommitted", "start_day": 11, "end_day": 20,
        "uncommitted_by_quality": {"standard": 80, "fine": 20},
        "allocation_capacity": 100, "global_capacity": 120,
    }
    claim = dict(source_id="source", destination_id="buyer", commodity="wine",
                 quality="standard", mode="allocated_export", start_day=20,
                 end_day=25, quantity=60)
    free = remaining_supply(basis, [claim])
    assert free["global_headroom_units"] == 60
    assert free["available_by_quality"] == {"standard": 48, "fine": 12}
    allocated = remaining_supply({**basis, "mode": "allocated_export"}, [claim])
    assert allocated["available_units"] == 40
    assert remaining_supply({**basis, "mode": "allocated_export", "destination_id": "other"}, [claim])["available_units"] == 60
    for change in [{"start_day": 21}, {"end_day": 10, "start_day": 1},
                   {"commodity": "other"}, {"source_id": "other"}]:
        ignored = remaining_supply(basis, [{**claim, **change}])
        assert ignored["available_units"] == 80
        assert ignored["global_claimed_units"] == 0


def test_allocated_and_free_orders_cannot_exceed_total_exportable_supply(desk):
    small_pool(desk, 200)
    desk.quotes["source"].exports_per_day = 10
    desk.quotes["buyer"].sources[0]["quantity_per_day"] = 10
    free_quote = desk.store.quote(desk.world, parameters(quantity=100))
    allocation_quote = desk.store.quote(desk.world, parameters(quantity=100, supply_mode="allocated_export"))
    reserve(desk, quote=free_quote)
    reserve(desk, reference="ALLOCATED", quote=allocation_quote)
    assert sum(row["quantity"] for row in desk.store.claims()) == 200
    for mode in ("uncommitted", "allocated_export"):
        quote = desk.store.quote(desk.world, parameters(quantity=12, supply_mode=mode))
        assert quote["supply"]["global_headroom_units"] == 0
        assert quote["supply"]["available_units"] == 0
        assert not quote["reservable"]


def test_later_nonoverlapping_window_has_independent_supply(desk):
    small_pool(desk)
    reserve(desk, quantity=120)
    quote = desk.store.quote(desk.world, parameters(quantity=120, supply_date="1492-06-21"))
    assert quote["supply"]["available_units"] == 120
    reserve(desk, quote=quote, reference="NEXT-WINDOW")
    assert sum(row["quantity"] for row in desk.store.claims()) == 240


def test_cancel_requires_refunds_then_releases_claim_across_connections(desk):
    small_pool(desk)
    peer = TradeStore(desk.store.path)
    assert peer.claims() == []
    order = reserve(desk, quantity=120, deposit_percent=50)
    assert len(peer.claims()) == 1
    order = fund(desk, order)
    with pytest.raises(TradeError, match="refunds"):
        transition(desk, order, "cancel")
    order = pay(desk, order, "customer_refund", order["balance"]["customer_paid_gp"])
    with pytest.raises(TradeError, match="refunds"):
        transition(desk, order, "cancel")
    order = pay(desk, order, "supplier_refund", order["balance"]["supplier_paid_gp"])
    cancelled = transition(desk, order, "cancel")
    assert cancelled["status"] == "cancelled"
    assert cancelled["balance"]["customer_due_gp"] == cancelled["balance"]["supplier_due_gp"] == 0
    assert cancelled["audit"][-1]["details"]["claims_released"]
    assert desk.store.claims() == peer.claims() == []
    assert reserve(desk, quantity=120, reference="REPLACEMENT")["status"] == "reserved"
    with pytest.raises(TradeError, match="Cancelled"):
        pay(desk, cancelled, "customer_payment", 1, "new-payment")


def test_dispatch_requires_pickup_supplier_payment_and_deposit(desk):
    order = reserve(desk, deposit_percent=50)
    assert not order["balance"]["can_dispatch"]
    with pytest.raises(TradeError, match="Dispatch requires"):
        transition(desk, order, "dispatch")
    desk.world.date = HarptosDate(1492, 6, 20)
    order = pay(desk, order, "customer_payment", order["quote"]["amounts"]["customer_deposit_due_gp"])
    assert not order["balance"]["can_dispatch"]
    with pytest.raises(TradeError, match="Dispatch requires"):
        transition(desk, order, "dispatch")
    order = pay(desk, order, "supplier_payment", order["quote"]["amounts"]["supplier_total_gp"])
    assert order["balance"]["can_dispatch"]
    assert transition(desk, order, "dispatch")["status"] == "dispatched"


def test_funded_order_still_waits_for_pickup_and_unfunded_deposit_blocks_dispatch(desk):
    funded = fund(desk, reserve(desk, reference="EARLY", deposit_percent=50))
    assert funded["balance"]["supplier_due_gp"] == 0
    assert funded["balance"]["deposit_remaining_gp"] == 0
    with pytest.raises(TradeError, match="Dispatch requires"):
        transition(desk, funded, "dispatch")
    order = reserve(desk, deposit_percent=50)
    order = pay(desk, order, "supplier_payment", order["quote"]["amounts"]["supplier_total_gp"])
    desk.world.date = HarptosDate(1492, 6, 20)
    assert not order["balance"]["can_dispatch"]
    with pytest.raises(TradeError, match="Dispatch requires"):
        transition(desk, order, "dispatch")
    order = pay(desk, order, "customer_payment", order["quote"]["amounts"]["customer_deposit_due_gp"])
    assert transition(desk, order, "dispatch")["status"] == "dispatched"


def test_before_dispatch_terms_require_full_customer_prepayment(desk):
    order = reserve(desk, payment_terms="before_dispatch", deposit_percent=50)
    order = fund(desk, order)
    desk.world.date = HarptosDate(1492, 6, 20)
    with pytest.raises(TradeError, match="Dispatch requires"):
        transition(desk, order, "dispatch")
    order = pay(desk, order, "customer_payment", order["balance"]["customer_due_gp"], "balance")
    assert transition(desk, order, "dispatch")["status"] == "dispatched"


def test_dispatched_and_delivered_claims_stay_consumed_and_arrival_requires_acceptance(desk):
    small_pool(desk)
    order = fund(desk, reserve(desk, quantity=120, deposit_percent=50))
    desk.world.date = HarptosDate(1492, 6, 20)
    dispatched = transition(desk, order, "dispatch")
    assert desk.store.claims()[0]["quantity"] == 120
    with pytest.raises(TradeError, match="undispatched"):
        transition(desk, dispatched, "cancel")
    desk.world.date = HarptosDate(1492, 6, 22)
    with pytest.raises(TradeError, match="travel time"):
        transition(desk, dispatched, "deliver", accepted=True)
    desk.world.date = HarptosDate(1492, 6, 23)
    assert desk.store.order(desk.world, order["id"])["balance"]["can_deliver"]
    with pytest.raises(TradeError, match="acceptance"):
        transition(desk, dispatched, "deliver")
    delivered = transition(desk, dispatched, "deliver", accepted=True)
    assert delivered["status"] == "delivered"
    assert desk.store.claims()[0]["quantity"] == 120
    assert delivered["balance"]["customer_due_gp"] > 0
    assert any("outstanding" in warning for warning in delivered["balance"]["warnings"])
    repeated = transition(desk, dispatched, "deliver", accepted=True)
    assert repeated["version"] == delivered["version"]
    assert repeated["audit"] == delivered["audit"]
    assert transition(desk, dispatched, "dispatch") == delivered


def test_dispatch_rechecks_supply_but_preserves_locked_public_prices(desk):
    order = fund(desk, reserve(desk))
    locked = deepcopy(order["quote"])
    desk.world.date = HarptosDate(1492, 6, 20)
    for offer in desk.quotes["buyer"].quality_offers:
        offer["price"] *= 2
    dispatched = transition(desk, order, "dispatch")
    assert dispatched["quote"] == locked
    assert dispatched["quote"]["amounts"]["customer_total_gp"] == locked["amounts"]["customer_total_gp"]
    assert desk.world.date == HarptosDate(1492, 6, 20)


def test_dispatch_blocks_forecast_shortage_without_releasing_claim(desk):
    small_pool(desk)
    order = fund(desk, reserve(desk, quantity=120))
    desk.world.date = HarptosDate(1492, 6, 20)
    desk.quotes["source"].production_per_day = 10
    with pytest.raises(TradeError, match="no longer covered"):
        transition(desk, order, "dispatch")
    assert desk.store.order(desk.world, order["id"])["status"] == "reserved"
    assert desk.store.claims()[0]["quantity"] == 120


@pytest.mark.parametrize("kind,total_key,refund", [
    ("customer_payment", "customer_total_gp", "customer_refund"),
    ("supplier_payment", "supplier_total_gp", "supplier_refund"),
])
def test_cash_caps_refunds_and_casefolded_reference_idempotency(desk, kind, total_key, refund):
    order = reserve(desk)
    total = order["quote"]["amounts"][total_key]
    with pytest.raises(TradeError, match="exceeds"):
        pay(desk, order, refund, .01, "unearned-refund")
    with pytest.raises(TradeError, match="exceeds"):
        pay(desk, order, kind, total + .01, "overpayment")
    paid = pay(desk, order, kind, total, "Receipt-A")
    revision = desk.store.revision
    duplicate = pay(desk, paid, kind, total, " receipt-a ")
    assert duplicate["version"] == paid["version"]
    assert duplicate["payments"] == paid["payments"]
    assert desk.store.revision == revision
    with pytest.raises(TradeError, match="different entry"):
        pay(desk, paid, kind, 1, "Receipt-A")
    with pytest.raises(TradeError, match="different entry"):
        pay(desk, paid, refund, total, "Receipt-A")
    with pytest.raises(TradeError, match="exceeds"):
        pay(desk, paid, kind, .01, "extra")
    with pytest.raises(TradeError, match="exceeds"):
        pay(desk, paid, refund, total + .01, "over-refund")
    refunded = pay(desk, paid, refund, total, "Refund-A")
    assert refunded["balance"]["can_cancel"]
    assert len(refunded["payments"]) == 2
    assert pay(desk, refunded, refund, total, "refund-a") == refunded


@pytest.mark.parametrize("amount", [True, None, "", 0, -1, .001, .019, "NaN", "Infinity"])
def test_cash_requires_positive_finite_whole_copper(desk, amount):
    order = reserve(desk)
    with pytest.raises(TradeError):
        pay(desk, order, "customer_payment", amount)
    assert desk.store.order(desk.world, order["id"])["payments"] == []


def test_expenses_affect_recorded_cash_not_forecast_or_customer_balance(desk):
    order = reserve(desk)
    original = deepcopy(order["quote"])
    paid = pay(desk, order, "customer_payment", 50)
    paid = pay(desk, paid, "supplier_payment", 20)
    paid = pay(desk, paid, "expense", 7.25)
    assert paid["balance"]["recorded_cash_gp"] == 22.75
    assert paid["balance"]["expenses_gp"] == 7.25
    assert paid["balance"]["customer_due_gp"] == original["amounts"]["customer_total_gp"] - 50
    assert paid["quote"] == original


def test_optimistic_version_and_simulation_chronology_reject_stale_actions(desk):
    order = reserve(desk)
    desk.world.date = HarptosDate(1492, 6, 12)
    newer = pay(desk, order, "expense", 1)
    assert newer["version"] == order["version"] + 1
    with pytest.raises(TradeError, match="PO changed"):
        transition(desk, order, "cancel")
    desk.world.date = HarptosDate(1492, 6, 11)
    with pytest.raises(TradeError, match="latest simulation entry"):
        pay(desk, newer, "expense", 1, "backdated")
    with pytest.raises(TradeError, match="latest simulation entry"):
        transition(desk, newer, "cancel")
    desk.world.date = HarptosDate(1492, 6, 12)
    assert transition(desk, newer, "cancel")["status"] == "cancelled"


def test_reopen_preserves_quote_cash_audit_and_paginated_orders(desk):
    first = reserve(desk)
    first = pay(desk, first, "customer_payment", 12.34)
    second = reserve(desk, reference="PO-2")
    reopened = TradeStore(desk.store.path)
    assert reopened.order(desk.world, first["id"]) == first
    assert reopened.order(desk.world, second["id"]) == second
    assert reopened.claims() == desk.store.claims()
    assert reopened.revision == desk.store.revision
    page = reopened.list_orders(desk.world, limit=1)
    next_page = reopened.list_orders(desk.world, offset=1, limit=1)
    assert page["total"] == next_page["total"] == 2
    assert {page["orders"][0]["id"], next_page["orders"][0]["id"]} == {first["id"], second["id"]}
    assert reopened.list_orders(desk.world, offset=2)["orders"] == []
    with pytest.raises(TradeError) as error:
        reopened.order(desk.world, "missing")
    assert error.value.status == 404


@pytest.mark.parametrize("offset,limit", [(-1, 1), (0, 0), (0, 501), (.5, 1), (True, 1)])
def test_order_list_rejects_invalid_pagination(desk, offset, limit):
    with pytest.raises(TradeError):
        desk.store.list_orders(desk.world, offset=offset, limit=limit)


def test_concurrent_schema_initialization_never_exposes_partial_tables(tmp_path, monkeypatch):
    path = tmp_path / "concurrent-initialization.sqlite3"
    table_created, finish_initialization = Event(), Event()
    connect = sqlite3.connect

    class PausingConnection(sqlite3.Connection):
        def execute(self, statement, *args, **kwargs):
            result = super().execute(statement, *args, **kwargs)
            if statement.lstrip().startswith("CREATE TABLE IF NOT EXISTS trade_meta"):
                table_created.set()
                assert finish_initialization.wait(timeout=10)
            return result

    def pausing_connect(*args, **kwargs):
        return connect(*args, factory=PausingConnection, **kwargs)

    monkeypatch.setattr(orders.sqlite3, "connect", pausing_connect)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(TradeStore, path)
        try:
            assert table_created.wait(timeout=10)
            observer = connect(path)
            try:
                assert observer.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == []
                assert observer.execute("PRAGMA application_id").fetchone() == (0,)
                assert observer.execute("PRAGMA user_version").fetchone() == (0,)
                assert observer.execute("PRAGMA journal_mode").fetchone()[0] != "wal"
            finally:
                observer.close()
            second = executor.submit(TradeStore, path)
        finally:
            finish_initialization.set()
        stores = [first.result(timeout=10), second.result(timeout=10)]
    assert stores[0].revision == stores[1].revision == 0
    assert stores[0].claims() == stores[1].claims() == []
    with stores[0].connection() as db:
        assert db.execute("PRAGMA application_id").fetchone()[0] == APPLICATION_ID
        assert db.execute("PRAGMA user_version").fetchone()[0] == 1


@pytest.mark.parametrize("kind", ["foreign", "version", "incomplete"])
def test_incompatible_database_guard_does_not_mutate_existing_data(tmp_path, kind):
    path = tmp_path / "other.sqlite3"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE sentinel (message TEXT)")
        db.execute("INSERT INTO sentinel VALUES ('keep me')")
        if kind in ("version", "incomplete"):
            db.execute(f"PRAGMA application_id={APPLICATION_ID}")
            db.execute(f"PRAGMA user_version={2 if kind == 'version' else 1}")
        before = (db.execute("PRAGMA application_id").fetchone(),
                  db.execute("PRAGMA user_version").fetchone())
    with pytest.raises(TradeError, match="not a supported"):
        TradeStore(path)
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT message FROM sentinel").fetchall() == [("keep me",)]
        assert db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == [("sentinel",)]
        assert before == (db.execute("PRAGMA application_id").fetchone(),
                          db.execute("PRAGMA user_version").fetchone())
