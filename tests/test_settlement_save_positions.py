"""Saving the catalog must keep raw positions, not calibrated or map-edited ones."""

from faerun import catalog, data_store
from faerun.models import S
from faerun.world import World


def _capture(monkeypatch):
    saved = {}
    monkeypatch.setattr(data_store, "_save_json", lambda name, rows: saved.setdefault(name, rows))
    return saved


def test_save_writes_raw_position_not_live_position(monkeypatch):
    town = S("Testville", "Test", "test", 1000, 108.1, 1316.0)
    town._base_xy = (84.1, 819.6)
    saved = _capture(monkeypatch)
    data_store.save_settlements([town])
    assert (saved["settlements"][0]["x"], saved["settlements"][0]["y"]) == (84.1, 819.6)


def test_save_without_a_raw_position_uses_live_position(monkeypatch):
    saved = _capture(monkeypatch)
    data_store.save_settlements([S("Newtown", "Test", "test", 1000, 10.0, 20.0)])
    assert (saved["settlements"][0]["x"], saved["settlements"][0]["y"]) == (10.0, 20.0)


def test_update_settlement_position_is_saved_as_the_new_raw_position(monkeypatch):
    town = S("Testville", "Test", "test", 1000, 5.0, 6.0)
    town._base_xy = (5.0, 6.0)
    world = World(settlements=[town])
    monkeypatch.setattr(catalog, "_world", lambda: world)
    saved = _capture(monkeypatch)
    catalog.update_settlement("testville", x=50.0, y=60.0)
    assert (saved["settlements"][0]["x"], saved["settlements"][0]["y"]) == (50.0, 60.0)


def test_update_settlement_without_position_keeps_the_raw_position(monkeypatch):
    town = S("Testville", "Test", "test", 1000, 108.1, 1316.0)
    town._base_xy = (84.1, 819.6)
    world = World(settlements=[town])
    monkeypatch.setattr(catalog, "_world", lambda: world)
    saved = _capture(monkeypatch)
    catalog.update_settlement("testville", ruler="Council")
    row = saved["settlements"][0]
    assert (row["x"], row["y"], row["ruler"]) == (84.1, 819.6, "Council")
