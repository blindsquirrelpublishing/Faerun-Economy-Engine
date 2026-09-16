import math

import pytest

from faerun.calendar import HarptosDate
from faerun.inventory import InventoryAllocator
from faerun.models import Event
from faerun.seasonal_economy import inventory_window
from test_seasonal_economy import inventory_world


def test_window_sums_actual_harvest_days_and_conserves_stocks(monkeypatch):
    world = inventory_world(monkeypatch)
    date, revision = world.date, world.revision
    start, end = HarptosDate(1492, 8, 30), HarptosDate(1492, 9, 2)
    result = inventory_window("Farm", "grain", start, end, world=world)
    assert world.date is date
    assert world.revision == revision
    assert result["days"] == end.absolute_day() - start.absolute_day() + 1
    assert result["snapshots"][0]["production"] == 0
    assert result["snapshots"][-1]["production"] > 0
    totals = result["totals"]
    assert totals["production"] == math.fsum(row["production"] for row in result["snapshots"])
    assert totals["production"] != result["snapshots"][-1]["production"] * result["days"]
    assert result["opening_stock"] + totals["production"] + totals["imports"] == pytest.approx(
        result["closing_stock"] + totals["exports"] + totals["final_consumption"]
        + totals["processing_consumption"] + totals["spoilage"] + totals["overflow"])
    assert "uncommitted_stock" not in totals
    assert "closing_stock" not in totals


def test_window_export_destinations_match_daily_deliveries_and_cache_is_detached(monkeypatch):
    world = inventory_world(monkeypatch)
    world.commodities["grain"].production_profile = []
    world.commodities["grain"].reserve_days = 0
    world.config.initial_inventory[("town", "grain")] = 0
    start, end = world.date, world.date.add_days(2)
    calls = []
    allocate = InventoryAllocator.allocate

    def counted(self, *args, **kwargs):
        calls.append(kwargs["include_backups"])
        return allocate(self, *args, **kwargs)

    monkeypatch.setattr(InventoryAllocator, "allocate", counted)
    result = inventory_window("Farm", "grain", start, end, world=world)
    assert calls == [False, False, False]
    assert result["exports_by_destination"]["town"] > 0
    assert math.fsum(result["exports_by_destination"].values()) == pytest.approx(result["totals"]["exports"])
    for row in result["snapshots"]:
        assert math.fsum(row["exports_by_destination"].values()) == pytest.approx(row["exports"])
    production = result["totals"]["production"]
    result["totals"]["production"] = -1
    result["snapshots"][0]["exports_by_destination"].clear()
    cached = inventory_window("Farm", "grain", start, end, world=world)
    assert cached["totals"]["production"] == production
    assert cached["snapshots"][0]["exports_by_destination"]
    assert len(calls) == 3
    history = world._inventory_history[1]
    with_backups, _ = history.at(end)
    assert calls[-1] is True
    assert with_backups["grain"]["farm"]["closing_stock"] == cached["closing_stock"]


def test_window_cache_invalidates_for_events_and_starting_inventory(monkeypatch):
    world = inventory_world(monkeypatch)
    world.commodities["grain"].production_profile = []
    start, end = world.date, world.date.add_days(1)
    original = inventory_window("Farm", "grain", start, end, world=world)
    assert original["totals"]["production"] > 0
    world.add_event(Event("shock", "Shock", commodities=["grain"], supply=0))
    shocked = inventory_window("Farm", "grain", start, end, world=world)
    assert shocked["totals"]["production"] == 0
    world.config.initial_inventory[("farm", "grain")] = 100
    reseeded = inventory_window("Farm", "grain", start, end, world=world)
    assert reseeded["opening_stock"] == 100


def test_positive_daily_flow_can_still_be_reserved_for_storage(monkeypatch):
    world = inventory_world(monkeypatch, grain_stock=0)
    world.commodities["grain"].production_profile = []
    result = inventory_window("Farm", "grain", world.date, world.date, world=world)
    row = result["snapshots"][0]
    assert row["production"] + row["imports"] - row["demand"] - row["exports"] > 0
    assert row["closing_stock"] > 0
    assert row["uncommitted_stock"] == 0
    assert row["closing_stock"] <= row["reserve_target"]


@pytest.mark.parametrize("start,end", [
    (HarptosDate(1491, 12, 30), HarptosDate(1492, 1, 1)),
    (HarptosDate(1492, 1, 2), HarptosDate(1492, 1, 1)),
    (HarptosDate(1492, 1, 1), HarptosDate(1492, 2, 2)),
    ("1492-01-01", HarptosDate(1492, 1, 1)),
])
def test_window_rejects_unsupported_dates(monkeypatch, start, end):
    world = inventory_world(monkeypatch)
    with pytest.raises(ValueError, match="Inventory window"):
        inventory_window("Farm", "grain", start, end, world=world)


@pytest.mark.parametrize("setting", ["seasonal_inventory", "expanded_requirements"])
def test_window_requires_explicit_physical_inventory_mode(monkeypatch, setting):
    world = inventory_world(monkeypatch)
    setattr(world.config, setting, False)
    with pytest.raises(ValueError, match="require seasonal_inventory"):
        inventory_window("Farm", "grain", world.date, world.date, world=world)


def test_app_default_does_not_enable_historical_inventory_replay():
    from faerun.world import _new_world

    world = _new_world()
    assert world.config.seasonal_inventory is False
    assert not hasattr(world, "_inventory_history")
    assert world.config.inventory_cache_path


@pytest.mark.parametrize("flags,initial,expected", [
    ([], False, False),
    ([], True, True),
    (["--seasonal-inventory"], False, True),
    (["--no-seasonal-inventory"], True, False),
])
def test_cli_seasonal_mode_is_an_explicit_override(monkeypatch, tmp_path, flags, initial, expected):
    from faerun import cli
    from faerun.orders import TradeStore

    world = inventory_world(monkeypatch)
    world.config.seasonal_inventory = initial
    world.trade_store = TradeStore(tmp_path / "orders.sqlite3")
    monkeypatch.setattr(cli, "get_world", lambda: world)
    args = cli.build_parser().parse_args([*flags, "calendar"])
    assert cli.build_world(args).config.seasonal_inventory is expected
