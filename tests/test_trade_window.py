"""Trade integration with real daily inventory, without the full-world replay."""

import math

from faerun.calendar import HarptosDate
from faerun.models import Event
from faerun.orders import TradeStore
from faerun.seasonal_economy import inventory_window
from faerun.trading import build_quote
from faerun.world import Edge
from test_seasonal_economy import inventory_world


def test_real_daily_export_window_bounds_the_trade_quote(monkeypatch):
    world = inventory_world(monkeypatch)
    world.commodities["grain"].production_profile = []
    world.commodities["grain"].reserve_days = 0
    world.commodities["grain"].base_price = 10
    world.config.initial_inventory[("town", "grain")] = 0
    world._edges = {
        "farm": [Edge("farm", "town", 24, 1, "road")],
        "town": [Edge("town", "farm", 24, 1, "road")],
    }
    period = inventory_window("farm", "grain", world.date, HarptosDate(1492, 1, 10), world=world)
    original_date = world.date
    quote = build_quote(world, {
        "origin": "farm", "destination": "town", "commodity": "grain", "quantity": 10,
        "supply_mode": "allocated_export", "transport_mode": "own_caravan",
        "acceptance_terms": "Inspect grain quantity and grade.",
    })
    assert quote["supply"]["flow_basis"] == "daily inventory window"
    assert quote["supply"]["capacity_units"] == math.floor(period["exports_by_destination"]["town"] + 1e-9)
    assert quote["_basis"]["production_capacity"] == math.floor(period["totals"]["production"] + 1e-9)
    assert world.date == original_date


def test_real_stored_stock_remains_sellable_with_zero_window_production(monkeypatch, tmp_path):
    world = inventory_world(monkeypatch)
    world.commodities["grain"].production_profile = []
    world.commodities["grain"].reserve_days = 0
    world.commodities["grain"].base_price = 10
    world.config.initial_inventory[("farm", "grain")] = 3000
    world.add_event(Event("stopped", "Stopped harvest", commodities=["grain"], supply=0))
    world.trade_store = TradeStore(tmp_path / "carried-window.sqlite3")
    params = {
        "origin": "farm", "destination": "farm", "commodity": "grain", "quantity": 10,
        "acceptance_terms": "Inspect stored grain quantity and grade.",
    }
    before = build_quote(world, params)
    assert before["_basis"]["production_capacity"] == 0
    assert before["reservable"]
    assert before["supply"]["claim_scope"] == "carried_inventory"
    quote = world.trade_store.quote(world, params)
    world.trade_store.reserve(world, quote_id=quote["id"], customer_name="Winter customer",
                              po_reference="WINTER", terms_accepted=True)
    after = world.trade_store.quote(world, params)
    assert after["supply"]["available_units"] == before["supply"]["available_units"] - 10
