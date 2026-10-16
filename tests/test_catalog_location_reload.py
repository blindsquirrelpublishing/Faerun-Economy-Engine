"""Reload must preserve explicit saved map locations over calibration controls."""

from copy import deepcopy

from faerun import catalog, locationedits
from faerun.data import businesses, commodities, settlements
from faerun.models import S
from faerun.world import World


def test_reload_reapplies_saved_position_over_stale_control_point(monkeypatch, tmp_path):
    # A stale calibration says 621.7/1126; the saved market/map edit says
    # 648.5289/1161.7169. This reproduces the Amphail disagreement without
    # touching the real map drafts, network or running server.
    calibrated = S("Amphail", "Dessarin Valley", "waterdeep", 850, 621.7, 1126.0)
    world = World(settlements=[deepcopy(calibrated)])
    world._use_location_edits = True
    world._use_route_edits = False
    edit_path = tmp_path / "location-edits.json"
    edit_path.write_text('{"revision":1}', encoding="utf-8")
    monkeypatch.setattr(locationedits, "location_edits_path", lambda: edit_path)
    monkeypatch.setattr(locationedits, "load_location_edits", lambda: {
        "revision": 1, "locations": {"amphail": {
            "name": "Amphail", "x": 648.5289, "y": 1161.7169,
            "mapPositionEdited": True,
        }},
    })
    world.sync_location_edits()
    assert (world.find_settlement("amphail").x, world.find_settlement("amphail").y) == (
        648.5289, 1161.7169,
    )

    # Reloaded module again supplies the stale calibration result. Catalog
    # reload should restore the map override, not publish stale coordinates.
    monkeypatch.setattr(catalog, "_world", lambda: world)
    monkeypatch.setattr(catalog.importlib, "reload", lambda module: module)
    monkeypatch.setattr(settlements, "SETTLEMENTS", [deepcopy(calibrated)])
    monkeypatch.setattr(commodities, "COMMODITIES", list(world.commodities.values()))
    monkeypatch.setattr(businesses, "BUSINESSES", [])
    catalog.reload_from_disk()
    town = world.find_settlement("amphail")
    assert (town.x, town.y) == (648.5289, 1161.7169)
    assert (world._location_base_settlements["amphail"].x,
            world._location_base_settlements["amphail"].y) == (621.7, 1126.0)


def test_real_catalog_reload_keeps_saved_amphail_position_and_route_edges():
    from faerun.world import get_world

    world = get_world()
    from faerun.locationedits import load_location_edits

    saved = load_location_edits()["locations"]["amphail"]
    assert saved.get("mapPositionEdited") is True
    before_edges = len(world._edges.get("amphail", []))
    catalog.reload_from_disk()
    amphail = world.find_settlement("amphail")
    assert (amphail.x, amphail.y) == (saved["x"], saved["y"])
    assert len(world._edges.get("amphail", [])) == before_edges
