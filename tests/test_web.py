"""HTTP response handling checks for the local market board."""

from __future__ import annotations

import pytest

from faerun import web
from faerun.detailassets import PRODUCT_HTML, ROUTE_HTML
from faerun.locationassets import LOCATION_HTML
from faerun.mapassets import MAP_HTML, TERRAIN_HTML
from faerun.plannerassets import PLANNER_HTML
from faerun.web import Handler
from faerun.webassets import APP_CSS, ASSETS, INDEX_HTML


def test_map_exposes_daily_travel_rates_without_mutating_cached_payload(monkeypatch):
    cached = {"settlements": []}
    monkeypatch.setattr(web, "map_payload", lambda world: cached)
    payload = web.api_map(None, {})
    assert payload["travelMilesPerDay"]["road"] == 24
    assert payload["travelMilesPerDay"]["air"] == 80
    assert payload["travelMilesPerDay"]["sea"] == 72
    assert "teleport" not in payload["travelMilesPerDay"]
    assert "travelMilesPerDay" not in cached


def test_location_endpoint_persists_marker_edits(monkeypatch, tmp_path):
    from faerun import locationedits

    monkeypatch.setattr(locationedits, "location_edits_path", lambda: tmp_path / "edits.json")
    cached = {"settlements": [{"id": "town", "name": "Town", "x": 1, "y": 2}], "places": []}
    monkeypatch.setattr(web, "map_payload", lambda world: cached)
    handler = web.POST_ROUTES["/api/map-location"]
    result = handler(None, {"revision": 0, "name": "Camp", "x": 3, "y": 4})
    assert result["id"].startswith("location:")
    assert web.api_map(None, {})["settlements"][-1]["name"] == "Camp"
    handler(None, {"revision": 1, "id": "town", "name": "Town", "x": 5, "y": 6})
    assert web.api_map(None, {})["settlements"][0]["x"] == 5
    assert cached["settlements"][0]["x"] == 1
    handler(None, {"revision": 2, "id": "town", "deleted": True})
    assert len(web.api_map(None, {})["settlements"]) == 1
    with pytest.raises(web.ApiError, match="changed elsewhere"):
        handler(None, {"revision": 0, "name": "Old", "x": 0, "y": 0})


class DisconnectedWriter:
    def write(self, _raw: bytes) -> None:
        raise ConnectionAbortedError(10053, "client disconnected")


@pytest.mark.parametrize("method,args", [
    ("_send_json", ({"ok": True},)),
    ("_send_bytes", (b"ok", "text/plain")),
])
def test_response_writers_ignore_client_disconnects(method, args):
    handler = Handler.__new__(Handler)
    handler.send_response = lambda _status: None
    handler.send_header = lambda _name, _value: None
    handler.end_headers = lambda: None
    handler.wfile = DisconnectedWriter()

    getattr(handler, method)(*args)


def test_events_drawer_starts_collapsed_and_preserves_controls():
    assert '<details class="eventdrawer">' in INDEX_HTML
    assert '<details class="eventdrawer" open>' not in INDEX_HTML
    assert '<summary>Events</summary>' in INDEX_HTML
    assert 'id="event-template"' in INDEX_HTML
    assert 'id="event-list"' in INDEX_HTML
    assert ".eventdrawer[open] summary" in APP_CSS
    assert "max-height: min(36vh, 300px)" in APP_CSS
    assert "flex: 1 1 auto" in APP_CSS


def test_every_page_displays_the_current_world_date():
    pages = [
        INDEX_HTML,
        MAP_HTML,
        TERRAIN_HTML,
        LOCATION_HTML,
        PRODUCT_HTML,
        ROUTE_HTML,
        PLANNER_HTML,
    ]
    for page in pages:
        assert "data-world-date" in page
        assert '<script src="date.js"></script>' in page
    assert "date.js" in ASSETS


def test_terrain_cell_endpoint_saves_and_returns_refreshed_map(monkeypatch):
    saved = []
    monkeypatch.setattr(
        web, "save_terrain_override",
        lambda column, row, terrain: saved.append((column, row, terrain)) or 3,
    )
    monkeypatch.setattr(web, "api_map", lambda _world, _params: {"grid": [96, 146]})

    payload = web.post_terrain_cell(object(), {"column": 12, "row": 34, "terrain": "o"})

    assert saved == [(12, 34, "o")]
    assert payload == {"grid": [96, 146], "terrainOverrideCount": 3}