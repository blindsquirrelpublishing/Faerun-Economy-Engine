from copy import deepcopy

import pytest

from faerun.calendar import HarptosDate
from faerun.economy import _commodity_markets, price_for
from faerun.models import C, Event, S
from faerun.world import EconomyConfig, World


def inventory_world(monkeypatch, *, date=None, grain_stock=50):
    from faerun import materials

    grain = C("grain", "Wheat", "food", 1, produced_by="farm")
    grain.production_profile = [0] * 8 + [1] + [0] * 3
    grain.storage_days = 365
    grain.reserve_days = 10
    flour = C("flour", "Flour", "food", 2, produced_by="craft")
    flour.bom = {"grain": 1}
    bread = C("bread", "Bread", "food", 3, produced_by="craft")
    bread.bom = {"flour": 1}
    herbs = C("herbs", "Herbs", "arcane", 2, produced_by="herb")
    herbs.production_profile = [0] * 5 + [1] + [0] * 6
    herbs.storage_days = 365
    potion = C("potion", "Potion", "arcane", 10, produced_by="alch")
    potion.bom = {"herbs": 1}
    goods = [grain, flour, bread, herbs, potion]
    monkeypatch.setattr(
        materials, "final_requirements",
        lambda s, goods, **kwargs: {
            c.id: {"household": 2 if c.id == "bread" else 1 if c.id == "potion" else 0}
            for c in goods
        },
    )
    monkeypatch.setattr(materials, "local_resource_capacity",
                        lambda s, c: 10 if s.id == "farm" and c.id in {"grain", "herbs"} else 0)
    config = EconomyConfig(
        seasonal_inventory=True, inventory_epoch="1492-01-01",
        service_economy=False, visitor_economy=False, calibrate_source_districts=False,
        noise=0,
        initial_inventory={(sid, cid): value for sid in ("farm", "town")
                           for cid, value in (("grain", grain_stock), ("herbs", 3))},
    )
    return World(
        settlements=[S("Farm", "Test", "test", 100, 0, 0, ind="farm3 craft3 alch3 herb3"),
                     S("Town", "Test", "test", 100, 20, 0, ind="craft3 alch3")],
        commodities=deepcopy(goods), businesses=[], date=date or HarptosDate(1492, 1, 1),
        config=config,
    )


def test_stored_wheat_feeds_constant_bread_demand_in_winter(monkeypatch):
    world = inventory_world(monkeypatch, date=HarptosDate(1492, 1, 5))
    wheat = price_for("Town", "grain", world=world)
    bread = price_for("Town", "bread", world=world)
    assert wheat.production_per_day == 0
    assert wheat.inventory["stock_draw_per_day"] == pytest.approx(2)
    assert wheat.inventory["closing_stock"] == pytest.approx(40)
    assert bread.production_per_day == bread.final_demand_per_day == 2
    assert bread.seasonality["demand_multiplier"] == 1
    assert wheat.factors["season"] == 1
    assert wheat.import_need_per_day == 0
    assert wheat.uncommitted_stock <= max(0, wheat.inventory["closing_stock"] - wheat.inventory["reserve_target"])


def test_year_round_potions_stop_only_when_stored_ingredients_run_out(monkeypatch):
    world = inventory_world(monkeypatch)
    assert price_for("Town", "potion", world=world).production_per_day == 1
    world.set_date(HarptosDate(1492, 1, 5))
    potion = price_for("Town", "potion", world=world)
    assert potion.production_per_day == 0
    assert potion.unmet_demand_per_day == 1
    assert potion.seasonality["production_multiplier"] == 1


def test_empty_granary_does_not_create_winter_grain_or_bread(monkeypatch):
    world = inventory_world(monkeypatch, grain_stock=0)
    bread = price_for("Town", "bread", world=world)
    assert bread.production_per_day == 0
    assert bread.unmet_demand_per_day == 2
    assert price_for("Town", "grain", world=world).inventory["closing_stock"] == 0


def test_inventory_queries_replay_identically_in_any_order_and_after_restart(monkeypatch):
    world = inventory_world(monkeypatch)
    world.set_date(HarptosDate(1492, 2, 2))
    expected = price_for("Town", "grain", world=world).to_dict()
    world.set_date(HarptosDate(1492, 1, 10))
    earlier = price_for("Town", "grain", world=world).to_dict()
    assert earlier["inventory"]["closing_stock"] > expected["inventory"]["closing_stock"]
    world.set_date(HarptosDate(1492, 2, 2))
    assert price_for("Town", "grain", world=world).to_dict() == expected
    restarted = inventory_world(monkeypatch, date=HarptosDate(1492, 2, 2))
    assert price_for("Town", "grain", world=restarted).to_dict() == expected


def test_daily_inventory_conserves_materials_and_does_not_reset_at_new_year(monkeypatch):
    world = inventory_world(monkeypatch, date=HarptosDate(1492, 12, 30))
    year_end = price_for("Town", "grain", world=world).inventory["closing_stock"]
    world.set_date(HarptosDate(1493, 1, 1))
    assert price_for("Town", "grain", world=world).inventory["opening_stock"] == year_end
    for c in world.commodities.values():
        markets = _commodity_markets(world, c)
        assert sum(q.imports_per_day for q in markets.values()) == pytest.approx(
            sum(q.exports_per_day for q in markets.values()))
        for q in markets.values():
            inventory = q.inventory
            assert inventory["opening_stock"] + q.production_per_day + q.imports_per_day == pytest.approx(
                q.final_consumption_per_day + q.processing_consumption_per_day + q.exports_per_day
                + inventory["closing_stock"] + inventory["spoilage"] + inventory["overflow"]
            )
            assert 0 <= inventory["closing_stock"] <= inventory["storage_capacity"]
            assert q.uncommitted_stock <= q.stock
            assert sum(offer["uncommitted_stock"] for offer in q.to_dict()["quality_offers"]) == q.uncommitted_stock


def test_new_event_and_initial_stock_changes_invalidate_history(monkeypatch):
    world = inventory_world(monkeypatch, date=HarptosDate(1492, 9, 1), grain_stock=0)
    normal = price_for("Farm", "grain", world=world)
    assert normal.production_per_day > 0
    world.add_event(Event("failed_harvest", "Failed harvest", commodities=["grain"],
                          supply=0, start_month=1492 * 12 + 9, duration_months=1))
    assert price_for("Farm", "grain", world=world).production_per_day == 0
    world.set_date(HarptosDate(1492, 1, 1))
    assert price_for("Town", "bread", world=world).production_per_day == 0
    world.config.initial_inventory[("town", "grain")] = 20
    assert price_for("Town", "bread", world=world).production_per_day == 2


def test_pre_epoch_dates_are_explicitly_labelled_not_replayed_backwards(monkeypatch):
    world = inventory_world(monkeypatch, date=HarptosDate(1491, 12, 1))
    quote = price_for("Town", "grain", world=world)
    assert quote.inventory["enabled"] is False
    assert "Before" in quote.inventory["reason"]


@pytest.mark.parametrize("epoch", ["1492-13-01", "1492-02-31", "garbage", "1492"])
def test_invalid_epoch_is_rejected(monkeypatch, epoch):
    world = inventory_world(monkeypatch)
    world.config.inventory_epoch = epoch
    with pytest.raises(ValueError):
        price_for("Town", "grain", world=world)


def test_initial_stock_and_storage_override_validation(monkeypatch):
    world = inventory_world(monkeypatch)
    world.config.storage_capacity[("town", "grain")] = 5
    with pytest.raises(ValueError, match="exceeds storage"):
        price_for("Town", "grain", world=world)
    world.config.initial_inventory[("town", "grain")] = 5
    assert price_for("Town", "grain", world=world).inventory["storage_capacity"] == 5
    world.config.initial_inventory[("missing", "grain")] = 1
    with pytest.raises(ValueError, match="Unknown"):
        price_for("Town", "grain", world=world)


def test_absolute_day_roundtrip_includes_harptos_festivals():
    start = HarptosDate(1492, 1, 1)
    for offset in range(366):
        date = start.add_days(offset)
        assert HarptosDate.from_absolute_day(date.absolute_day()) == date
    assert start.add_days(365) == HarptosDate(1493, 1, 1)
    assert HarptosDate(1492, 1, 30).add_days().festival is not None


def test_stock_pressure_propagates_to_bread_without_legacy_seasonal_price_markup(monkeypatch):
    tight = inventory_world(monkeypatch, grain_stock=50)
    stocked = inventory_world(monkeypatch, grain_stock=500)
    for world in (tight, stocked):
        world.find_commodity("grain").base_price = 10
        world.find_commodity("grain").season = {"winter": 100}
    assert price_for("Town", "bread", world=tight).price > price_for("Town", "bread", world=stocked).price
    assert price_for("Town", "grain", world=tight).factors["season"] == 1


def test_service_releases_remain_in_next_days_physical_stocks():
    from faerun.data.commodities import COMMODITIES

    goods = deepcopy(COMMODITIES)
    world = World(
        settlements=[S("Village", "Test", "test", 1000, 0, 0,
                       ind="farm3 craft3 herb3 alch3 temple2 log3")],
        commodities=goods, businesses=[], date=HarptosDate(1492, 1, 1),
        config=EconomyConfig(
            seasonal_inventory=True, visitor_economy=False,
            initial_inventory={("village", c.id): 0 for c in goods},
        ),
    )
    closing = {}
    for c in goods:
        q = price_for("Village", c.id, world=world)
        inv = q.inventory
        assert inv["opening_stock"] + q.production_per_day + q.imports_per_day == pytest.approx(
            q.final_consumption_per_day + q.processing_consumption_per_day + q.exports_per_day
            + inv["closing_stock"] + inv["spoilage"] + inv["overflow"], abs=1e-6,
        )
        closing[c.id] = inv["closing_stock"]
    world.set_date(HarptosDate(1492, 1, 2))
    for c in goods:
        assert price_for("Village", c.id, world=world).inventory["opening_stock"] == closing[c.id]


def test_service_release_roundoff_cannot_make_consumption_or_stock_draw_negative():
    from faerun.inventory import allocate_inventory_day
    from faerun.seasonal_economy import _consume_services

    balances = allocate_inventory_day(
        {"material": {"town": 0.3}}, {"material": {"town": 0.3}, "missing": {"town": 2}},
        {}, {}, {"material": {"town": 1}}, {}, {}, {},
    )
    sectors = {"town": {"material": {"a": 0.1, "b": 0.2}, "missing": {"a": 1, "b": 1}}}
    services = {"town": [
        {"id": key, "planned_per_day": 1, "inputs_per_unit": {"material": amount, "missing": 1}}
        for key, amount in (("a", 0.1), ("b", 0.2))
    ]}
    _consume_services(balances, sectors, services)
    material = balances["material"]["town"]
    assert material["household_consumption_per_day"] == 0
    assert material["stock_draw_per_day"] == 0
    assert material["consumption_sectors"] == {"a": 0, "b": 0}
    assert material["closing_stock"] == 0.1 + 0.2
    assert material["closing_stock"] == pytest.approx(material["production_per_day"], abs=1e-16)


def test_service_release_guard_does_not_hide_a_material_overrelease(monkeypatch):
    from faerun import accounts
    from faerun.inventory import allocate_inventory_day
    from faerun.seasonal_economy import _consume_services

    balances = allocate_inventory_day(
        {"material": {"town": 0.3}}, {"material": {"town": 0.3}},
        {}, {}, {"material": {"town": 1}}, {}, {}, {},
    )
    monkeypatch.setattr(accounts, "service_consumption",
                        lambda *args: (0, {"material": 0.3001}, {"material": 0}))
    with pytest.raises(ValueError, match="Service consumption must be finite and non-negative"):
        _consume_services(balances, {"town": {"material": {"a": 0.3}}},
                          {"town": [{"id": "a", "inputs_per_unit": {"material": 0.3}}]})


def test_reserve_forecast_includes_seasonal_consumption():
    from faerun.seasonal_economy import _cover_calendar

    flat = [1] * 12
    summer_low = [1.5, 1.5, 1.5, 1, 1, 0.5, 0.5, 0.5, 1, 1, 1, 1]
    assert _cover_calendar(flat, flat)[0] == 0
    assert _cover_calendar(flat, summer_low)[0] > 40


def test_location_and_trade_reports_do_not_call_stored_food_an_unfilled_import_need(monkeypatch):
    from faerun.economy import trade_summary
    from faerun.materials import location_requirements

    world = inventory_world(monkeypatch)
    report = location_requirements("Town", world)
    wheat = next(row for row in report["materials"] if row["commodity_id"] == "grain")
    assert wheat["production_per_day"] == 0
    assert wheat["import_need_per_day"] == 0
    assert wheat["surplus_per_day"] == 0
    assert all(row["commodity"] != "Wheat" for row in trade_summary("Town", world)["imports"])


def test_profile_cache_cannot_accept_boolean_weights_as_previous_numeric_weights():
    from faerun.seasonality import demand_multiplier

    good = C("good", "Good", "test", 1, demand_profile=[1] * 12)
    assert demand_multiplier(good, HarptosDate()) == 1
    good.demand_profile = [True] * 12
    with pytest.raises(ValueError, match="numbers"):
        demand_multiplier(good, HarptosDate())


def test_price_history_exposes_availability_and_restores_current_market_cache(monkeypatch):
    from faerun.economy import price_history

    world = inventory_world(monkeypatch)
    original = price_for("Town", "grain", world=world)
    date = world.date
    report = price_history("Town", "grain", world=world, months=4)
    assert world.date == date
    assert price_for("Town", "grain", world=world) is original
    assert len(report["series"]) == 4
    assert report["series"][0]["inventory"] == original.inventory
    assert report["series"][0]["production_per_day"] == 0
    assert report["series"][0]["demand_per_day"] == 2
    assert report["series"][0]["seasonality"]["demand_multiplier"] == 1


def test_festival_visitor_requirements_do_not_reuse_ordinary_month_cache(monkeypatch):
    from faerun import materials
    from faerun.seasonal_economy import InventoryHistory

    world = inventory_world(monkeypatch)
    plan = materials._baseline_plan(world)
    history = InventoryHistory(world, plan)

    def festival_requirements(world, plan):
        sectors = deepcopy(plan["sectors"])
        if world.date.festival:
            for needs in sectors.values():
                needs["bread"]["household"] *= 2
        return sectors, {sid: [] for sid in world.settlements}, {}

    monkeypatch.setattr(materials, "_active_requirements", festival_requirements)
    ordinary = history._month(HarptosDate(1492, 1, 30))
    festival = history._month(HarptosDate(1492, 1, 31))
    assert ordinary[1]["bread"]["town"] == 2
    assert festival[1]["bread"]["town"] == 4
    assert history._month(HarptosDate(1492, 1, 29))[1]["bread"]["town"] == 2


def test_replenishment_without_current_consumption_uses_landed_cost_not_fake_scarcity():
    good = C("good", "Good", "test", 1)
    world = World(
        settlements=[S("Supplier", "Test", "test", 100, 0, 0),
                     S("Second", "Test", "test", 100, 20, 0),
                     S("Buyer", "Test", "test", 100, 10, 0)],
        commodities=[good], date=HarptosDate(),
        config=EconomyConfig(noise=0),
    )
    deliveries = {
        sid: {"local_per_day": 0, "imports": [], "backups": [],
              "unmet_per_day": 0, "exports_per_day": 2 if sid == "supplier" else 0}
        for sid in world.settlements
    }
    deliveries["buyer"]["imports"] = [{
        "source_id": "supplier", "source": "Supplier", "quantity_per_day": 1,
        "unit_cost": 4, "producer_unit_cost": 1, "distance": 10, "days": 1,
        "share": 0, "purpose": "replenishment",
    }]
    deliveries["buyer"]["imports"].append(dict(deliveries["buyer"]["imports"][0]))
    deliveries["buyer"]["imports"].append({
        **deliveries["buyer"]["imports"][0],
        "source_id": "second", "source": "Second", "quantity_per_day": 1.5,
    })
    deliveries["second"]["exports_per_day"] = 1.5
    quote = _commodity_markets(world, good, _material={
        "production": {"supplier": 10, "second": 10, "buyer": 0},
        "demand": {sid: 0 for sid in world.settlements},
        "unit_cost": {sid: 0 for sid in world.settlements},
        "inventory_pressure": {sid: 1 for sid in world.settlements},
        "allocations": deliveries,
    })["buyer"]
    assert quote.factors["core_price"] == 4
    assert quote.source == "Supplier"
    assert not any("no eligible export" in note for note in quote.notes)


def test_date_navigation_preserves_baseline_and_quote_cache_but_edits_invalidate(monkeypatch):
    from faerun.materials import _baseline_plan

    world = inventory_world(monkeypatch)
    baseline = _baseline_plan(world)
    original = price_for("Town", "grain", world=world)
    revision = world.inventory_revision
    world.set_date(HarptosDate(1492, 1, 2))
    price_for("Town", "grain", world=world)
    assert world.inventory_revision == revision
    assert _baseline_plan(world) is baseline
    world.set_date(HarptosDate(1492, 1, 1))
    assert price_for("Town", "grain", world=world) is original
    world.revision += 1
    assert _baseline_plan(world) is not baseline
    assert price_for("Town", "grain", world=world) is not original


def test_fifo_stock_replacement_is_not_counted_as_extra_market_supply(monkeypatch):
    world = inventory_world(monkeypatch)
    bread = world.find_commodity("bread")
    bread.storage_days = 3
    bread.reserve_days = 1
    world.config.initial_inventory[("town", "bread")] = 2
    quote = price_for("Town", "bread", world=world)
    assert quote.production_per_day == 2
    assert quote.inventory["stock_draw_per_day"] == 2
    assert quote.inventory["closing_stock"] == 2
    assert quote.supply_index == quote.demand_index


def test_service_release_recomputes_fifo_draw_from_remaining_actual_use():
    from faerun.seasonal_economy import _consume_services

    def balance(opening, consumed, demand, closing):
        return {
            "opening_stock": opening, "household_consumption_per_day": consumed,
            "household_demand_per_day": demand, "processing_consumption_per_day": 0,
            "closing_stock": closing, "storage_capacity": 100, "spoilage": 0,
            "overflow": 0, "stock_draw_per_day": min(opening, consumed),
            "allocation": {"exports_per_day": 0},
        }

    balances = {"material": {"town": balance(10, 50, 50, 10)},
                "water": {"town": balance(0, 6, 10, 0)}}
    sectors = {"town": {"material": {"service": 50}, "water": {"service": 10}}}
    services = {"town": [{"id": "service", "planned_per_day": 10,
                          "inputs_per_unit": {"material": 5, "water": 1}}]}
    _consume_services(balances, sectors, services)
    material = balances["material"]["town"]
    assert material["household_consumption_per_day"] == 30
    assert material["closing_stock"] == 30
    assert material["stock_draw_per_day"] == 10


@pytest.mark.parametrize("prepared", [False, True])
def test_exhausted_export_budget_tolerates_only_floating_point_roundoff(prepared):
    from faerun.inventory import InventoryAllocator, allocate_inventory_day

    available = 47.84551854108633
    needs = [0.9962957430227805, 13.55108598561702, 2.462756974320667,
             7.309697918533616, 14.832775704968, 8.180854096237994,
             13.851560581039232, 4.15470606083423, 7.4455985360270605,
             6.048493348779318, 5.171904983844805, 5.891573231006402]
    capacity = {"good": {"source": available}}
    demand = {"good": {str(i): amount for i, amount in enumerate(needs)}}
    candidates = {"good": [
        {"source_id": "source", "destination_id": str(i), "unit_cost": i + 1, "days": 1}
        for i in range(len(needs))
    ]}
    if prepared:
        result = InventoryAllocator({}, candidates).allocate(capacity, demand, {}, {}, {}, {})
    else:
        result = allocate_inventory_day(capacity, demand, {}, {}, {}, {}, {}, candidates)
    source = result["good"]["source"]
    assert source["closing_stock"] == 0
    assert source["allocation"]["exports_per_day"] == pytest.approx(available, abs=1e-12)


@pytest.mark.parametrize("prepared", [False, True])
@pytest.mark.parametrize("exports", [1.000001, float("inf"), float("nan")])
def test_delivered_supply_guard_rejects_real_overspend_and_nonfinite_values(monkeypatch, prepared, exports):
    from faerun import inventory

    def invalid_allocation(routes, remaining, surplus, needs, balances, used, **kwargs):
        balances["source"]["allocation"]["exports_per_day"] = exports

    monkeypatch.setattr(inventory, "_trade_indexed" if prepared else "_trade", invalid_allocation)
    capacity = {"good": {"source": 1}}
    demand = {"good": {"buyer": 1}}
    candidates = {"good": [
        {"source_id": "source", "destination_id": "buyer", "unit_cost": 1, "days": 1}
    ]}
    with pytest.raises(ValueError, match="Delivered supply must be finite and non-negative"):
        if prepared:
            inventory.InventoryAllocator({}, candidates).allocate(capacity, demand, {}, {}, {}, {})
        else:
            inventory.allocate_inventory_day(capacity, demand, {}, {}, {}, {}, {}, candidates)


def test_persisted_checkpoints_reconstruct_same_day_without_replaying_the_year(monkeypatch, tmp_path):
    from faerun.inventory import InventoryAllocator

    cache = str(tmp_path / "inventory.sqlite3")
    world = inventory_world(monkeypatch, date=HarptosDate(1492, 2, 5))
    world.config.inventory_cache_path = cache
    expected = price_for("Town", "grain", world=world).to_dict()
    assert expected["inventory"]["checkpoint_storage"] == "local SQLite cache"
    restarted = inventory_world(monkeypatch, date=world.date)
    restarted.config.inventory_cache_path = cache
    allocate = InventoryAllocator.allocate
    calls = []

    def counted(self, *args, **kwargs):
        calls.append(1)
        return allocate(self, *args, **kwargs)

    monkeypatch.setattr(InventoryAllocator, "allocate", counted)
    assert price_for("Town", "grain", world=restarted).to_dict() == expected
    assert len(calls) == 1
    restarted.config.initial_inventory[("town", "grain")] = 70
    calls.clear()
    price_for("Town", "grain", world=restarted)
    assert len(calls) > 1


def test_persistent_cache_rejects_corrupt_quantities_and_keys_change_with_scenario(monkeypatch, tmp_path):
    from faerun.inventory_cache import InventoryCheckpointStore, scenario_key

    world = inventory_world(monkeypatch)
    signature = scenario_key(world)
    world.set_date(HarptosDate(1492, 2, 1))
    assert scenario_key(world) == signature
    world.add_event(Event("shock", "Shock", commodities=["grain"], supply=0))
    assert scenario_key(world) != signature
    store = InventoryCheckpointStore(tmp_path / "cache.sqlite3", signature)
    store.save(1, {"grain": {"town": 50}})
    with pytest.raises(ValueError, match="Invalid inventory"):
        store.load(1, {"grain": {"town": 10}})


@pytest.mark.parametrize("payload", [b"broken", b"\xff", b"{", b"[]", b'{"grain": []}'])
def test_persistent_cache_reports_corrupt_payloads(tmp_path, payload):
    import sqlite3
    import zlib
    from contextlib import closing

    from faerun.inventory_cache import InventoryCheckpointStore

    store = InventoryCheckpointStore(tmp_path / "cache.sqlite3", "scenario")
    encoded = payload if payload == b"broken" else zlib.compress(payload)
    with closing(sqlite3.connect(store.path)) as connection, connection:
        connection.execute(
            "INSERT INTO inventory_checkpoints(scenario,day,stock) VALUES(?,?,?)",
            ("scenario", 1, encoded),
        )
    with pytest.raises(ValueError, match="inventory checkpoint|Inventory checkpoint"):
        store.load(1, {"grain": {"town": 10}})


@pytest.mark.parametrize("failure", [False, True])
def test_counterfactual_comparison_restores_active_inventory_history(monkeypatch, failure):
    from contextlib import nullcontext

    from faerun.location import _without_events
    from faerun.seasonal_economy import InventoryHistory

    world = inventory_world(monkeypatch)
    world.add_event(Event("shock", "Shock", commodities=["bread"], demand=2))
    price_for("Town", "grain", world=world)
    history = world._inventory_history
    events = world.events
    with pytest.raises(RuntimeError, match="comparison failed") if failure else nullcontext():
        with _without_events(world):
            price_for("Town", "grain", world=world)
            assert world._inventory_history is not history
            if failure:
                raise RuntimeError("comparison failed")
    assert world._inventory_history is history
    assert world.events is events

    def unexpected_rebuild(*args, **kwargs):
        pytest.fail("A temporary price comparison discarded the active inventory history")

    monkeypatch.setattr(InventoryHistory, "__init__", unexpected_rebuild)
    world.set_date(world.date.add_days())
    price_for("Town", "grain", world=world)
