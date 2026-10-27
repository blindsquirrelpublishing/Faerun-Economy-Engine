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


def test_commodity_flows_endpoint_returns_sorted_import_paths():
    payload = web.api_commodity_flows(web.get_world(), {"commodity": ["grain"]})

    assert payload["commodity"] == "grain"
    assert payload["unit"]
    assert "/api/commodity-flows" in web.GET_ROUTES
    assert web.GET_ROUTES["/api/commodity-flows"] is web.api_commodity_flows
    flows = payload["flows"]
    assert isinstance(flows, list)
    if len(flows) > 1:
        assert flows[0]["quantity_per_day"] >= flows[1]["quantity_per_day"]
    if flows:
        row = flows[0]
        assert row["source_id"] != row["destination_id"]
        assert row["quantity_per_day"] > 0
        assert row["source"]
        assert row["destination"]
        assert row["route"]["reachable"] is True
        assert isinstance(row["route"]["legs"], list)
    totals = payload["totals"]
    assert all("exports_per_day" in totals[sid] and "imports_per_day" in totals[sid] for sid in totals)
    assert "leg_flows" in payload
    assert "node_flows" in payload
    if payload["leg_flows"]:
        leg = payload["leg_flows"][0]
        assert "from" in leg and "to" in leg
        assert leg["quantity_per_day"] > 0
    if payload["node_flows"]:
        node = payload["node_flows"][0]
        assert "cross_docked_per_day" in node
        assert "consumed_per_day" in node
        assert "modeled_local_consumption_per_day" in node
    assert payload["tiered_plan"] is None

def test_commodity_flows_can_return_tiered_plan_for_origin():
    payload = web.api_commodity_flows(web.get_world(), {"commodity": ["coffee"], "origin": ["Port Nyanzaru"]})

    plan = payload["tiered_plan"]
    assert plan is not None
    assert plan["origin"] == "Port Nyanzaru"
    assert plan["total_export_per_day"] >= 0
    assert isinstance(plan["tier1_hubs"], list)
    assert isinstance(plan["tier2_feeders"], list)
    assert isinstance(plan["tier3_tail_markets"], list)
    assert isinstance(plan["top_legs"], list)


def test_network_overlay_endpoint_reads_transport_geojson(tmp_path, monkeypatch):
    transport = tmp_path / "reference" / "transport"
    transport.mkdir(parents=True)
    sample = transport / "sample-overlay.geojson"
    sample.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")

    monkeypatch.setattr(web, "transport_reference_dir", lambda: transport)

    payload = web.api_network_overlay(web.get_world(), {"name": ["sample-overlay"]})

    assert payload["name"] == "sample-overlay.geojson"
    assert payload["overlay"]["type"] == "FeatureCollection"
    assert "/api/network-overlay" in web.GET_ROUTES
    assert web.GET_ROUTES["/api/network-overlay"] is web.api_network_overlay


def test_network_overlay_endpoint_rejects_invalid_name(tmp_path, monkeypatch):
    monkeypatch.setattr(web, "transport_reference_dir", lambda: tmp_path / "missing")

    with pytest.raises(web.ApiError, match="overlay name must use"):
        web.api_network_overlay(web.get_world(), {"name": ["../bad"]})

