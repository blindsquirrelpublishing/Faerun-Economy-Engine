import pytest

from faerun import routegeometry


@pytest.fixture
def edits_path(tmp_path, monkeypatch):
    path = tmp_path / "route-leg-edits.json"
    monkeypatch.setattr(routegeometry, "route_edits_path", lambda: path)
    return path


def test_delete_junction_keeps_roads_waypoints_and_other_junctions(edits_path):
    import copy

    routegeometry.save_route_leg({"id": "road", "revision": 0, "name": "Road", "kind": "road",
                                 "points": [[0, 0], [10, 0], [20, 0]]})
    first = routegeometry.save_road_junction({"revision": 1, "name": "First", "point": [10, 0], "legs": ["road"]})
    identifier = next(iter(first["junctions"]))
    before = routegeometry.save_road_junction({"revision": 2, "name": "Second", "point": [20, 0], "legs": ["road"]})
    expected = copy.deepcopy(before)
    del expected["junctions"][identifier]
    expected["revision"] += 1

    saved = routegeometry.save_road_junction({"revision": 3, "id": identifier, "deleted": True})

    assert saved == expected
    assert routegeometry.load_route_edits() == expected
    assert saved["legs"] == before["legs"]


@pytest.mark.parametrize("body,message", [
    ({"revision": 0, "id": "missing", "deleted": True}, "Unknown junction"),
    ({"revision": 0, "deleted": True}, "Unknown junction"),
    ({"revision": 0, "id": [], "deleted": True}, "Unknown junction"),
    ({"revision": 1, "id": "missing", "deleted": True}, "changed elsewhere"),
    ({"revision": True, "id": "missing", "deleted": True}, "integer revision"),
    ({"revision": 0, "id": "missing", "deleted": "yes"}, "boolean"),
])
def test_invalid_junction_deletion_does_not_write(edits_path, body, message):
    with pytest.raises(ValueError, match=message):
        routegeometry.save_road_junction(body)
    assert not edits_path.exists()


def test_edited_network_drives_routes_freight_and_refresh(edits_path):
    from types import SimpleNamespace
    from faerun.calendar import HarptosDate
    from faerun.transport import plan_shipment
    from faerun.world import Edge, World

    world = World.__new__(World)
    world.settlements = {name: SimpleNamespace(id=name, name=name, x=position, y=0,
        security=1, region="Test", zone="Test", traits=[], port=None)
        for name, position in (("west", 0), ("bank", 20), ("east", 40))}
    world._original_edges = {"west": [Edge("west", "east", 1, 1, "road", "Obsolete shortcut")]}
    world._edges = world._original_edges
    world._use_route_edits = True
    world.revision = 0
    world.date = HarptosDate(1492, 1, 1)
    world.events = {}
    world._events_stamp = None
    world.businesses = {}
    routegeometry.save_route_leg({"id":"road", "revision":0, "name":"New road", "kind":"road",
                                 "points":[[0,0],[10,0],[20,0]]})
    routegeometry.save_route_leg({"id":"ferry", "revision":1, "name":"New ferry", "kind":"ferry",
                                 "points":[[20,0],[40,0]]})
    routegeometry.save_road_junction({"revision":2, "point":[10,0], "legs":["road"]})
    result = world.route("west", "east")
    assert result["reachable"]
    assert result["distance"] == 40
    assert result["modes"] == ["ferry", "road"]
    assert len(world.settlements) == 3
    assert len(world.route_nodes) == 4
    plan = plan_shipment(world, "west", "east")
    assert plan["options"]
    for option in plan["options"]:
        assert option["distance_miles"] == 40
        assert any(leg["mode"] == "ferry" for leg in option["legs"])
        assert option["costs"]["total_gp"] > 0
    routegeometry.save_route_leg({"id":"ferry", "revision":3, "deleted":True})
    assert not world.route("west", "east")["reachable"]
    assert not plan_shipment(world, "west", "east")["options"]
    routegeometry.save_route_leg({"id":"sea", "revision":4, "name":"Measured sea", "kind":"sea",
                                 "points":[[20,0],[40,0]]})
    assert world.route("west", "east")["distance"] == 40


def test_saved_map_preserves_only_undeleted_special_links():
    from types import SimpleNamespace
    from faerun.world import Edge

    places = {name: SimpleNamespace(id=name, name=name, x=position, y=0, security=1, region="Test")
              for name, position in (("west", 0), ("east", 20))}
    original = {"west": [Edge("west", "east", 20, 1, kind, kind)
                          for kind in ("road", "air", "skyship", "teleport")]}
    graph, _ = routegeometry.build_edited_network(places, original, {
        "legs":{"route:air|east|west":{"deleted":True}}, "junctions":{}})
    assert {edge.kind for edge in graph["west"]} == {"skyship", "teleport"}


def test_current_saved_world_route_and_freight_agree():
    from faerun.world import World
    from faerun.transport import plan_shipment

    world = World()
    if not getattr(world, "_route_edits_stamp", None):
        pytest.skip("No edited map is installed")
    route = world.route("Waterdeep", "Peltarch", route_types={"road", "trail", "ferry"})
    assert route["reachable"]
    assert "ferry" in route["modes"]
    assert all(leg["points"] for leg in route["legs"])
    plan = plan_shipment(world, "Waterdeep", "Peltarch", route_types={"road", "trail", "ferry"})
    assert plan["options"]
    assert all(any(leg["mode"] == "ferry" for leg in option["legs"]) for option in plan["options"])


def test_create_edit_delete_and_reload_map_leg(edits_path):
    body = {"id": "custom:one", "revision": 0, "name": "New road", "kind": "road",
            "points": [[600, 1200], [610, 1220]]}
    saved = routegeometry.save_route_leg(body)
    assert saved == routegeometry.load_route_edits()
    assert saved["revision"] == 1
    body.update(revision=1, kind="trail", points=[[600, 1200], [604, 1211], [610, 1220]])
    routegeometry.save_route_leg(body)
    assert len(routegeometry.load_route_edits()["legs"][body["id"]]["points"]) == 3
    routegeometry.save_route_leg({"id": body["id"], "revision": 2, "deleted": True})
    assert routegeometry.load_route_edits()["legs"][body["id"]] == {"deleted": True}
    assert not edits_path.with_suffix(".json.tmp").exists()


def test_convert_single_waypoint_and_attach_branch_later(edits_path):
    routegeometry.save_route_leg({"id": "main", "revision": 0,
        "name": "Red Larch Trail: Red Larch to Secomber", "kind": "trail",
        "points": [[0, 0], [10, 10], [20, 20]]})
    request = {"revision": 1, "point": [10, 10], "legs": ["main"]}
    saved = routegeometry.save_road_junction(request)
    identifier = next(iter(saved["junctions"]))
    assert saved["junctions"][identifier]["name"] == "Red Larch Trail Junction"
    assert saved == routegeometry.load_route_edits()
    branch = {"id": "branch", "revision": 2, "name": "Goldenfields Branch",
              "kind": "trail", "points": [[10, 10], [30, 10]]}
    saved = routegeometry.save_route_leg(branch)
    assert saved["junctions"][identifier]["legs"] == ["main", "branch"]
    saved = routegeometry.save_road_junction({**request, "revision": 3, "id": identifier,
                                           "legs": ["main", "branch"]})
    assert saved["junctions"][identifier]["name"] == "Red Larch Trail Junction"
    saved = routegeometry.save_road_junction({**request, "revision": 4, "point": [20, 20]})
    assert {item["name"] for item in saved["junctions"].values()} == {
        "Red Larch Trail Junction", "Red Larch Trail Junction 2"}
    saved = routegeometry.save_route_leg({**branch, "revision": 5, "points": [[11, 10], [30, 10]]})
    assert saved["junctions"][identifier]["legs"] == ["main"]


@pytest.mark.parametrize("changes", [{"legs": []}, {"point": [11, 11]}, {"legs": ["missing"]}])
def test_invalid_single_waypoint_conversion_does_not_write(edits_path, changes):
    routegeometry.save_route_leg({"id": "main", "revision": 0, "name": "Trail", "kind": "trail",
                                 "points": [[0, 0], [10, 10]]})
    before = edits_path.read_text()
    with pytest.raises(ValueError):
        routegeometry.save_road_junction({"revision": 1, "point": [10, 10], "legs": ["main"], **changes})
    assert edits_path.read_text() == before


@pytest.mark.parametrize("changes", [
    {"kind": "unknown"}, {"points": [[0, 0]]}, {"points": [[0, 0], [float("nan"), 2]]},
    {"points": [[0, 0], [True, 2]]}, {"points": [[0, 0], [0, 0]]},
    {"name": " "}, {"deleted": "yes"}, {"revision": True},
])
def test_invalid_legs_do_not_write(edits_path, changes):
    body = {"id": "custom:one", "revision": 0, "name": "Road", "kind": "road",
            "points": [[0, 0], [1, 2]], **changes}
    with pytest.raises(ValueError):
        routegeometry.save_route_leg(body)
    assert not edits_path.exists()


def test_stale_revision_does_not_overwrite(edits_path):
    body = {"id": "road:one", "revision": 0, "deleted": True}
    routegeometry.save_route_leg(body)
    with pytest.raises(ValueError, match="changed elsewhere"):
        routegeometry.save_route_leg({**body, "id": "road:two"})
    assert list(routegeometry.load_route_edits()["legs"]) == ["road:one"]


def test_split_leg_is_atomic_and_preserves_junctions(edits_path):
    body = {"id": "main", "revision": 0, "name": "Trade Way", "kind": "road",
            "points": [[0, 0], [10, 10], [20, 20]]}
    routegeometry.save_route_leg(body)
    routegeometry.save_route_leg({**body, "id": "branch", "revision": 1, "points": [[10, 10], [30, 10]]})
    routegeometry.save_road_junction({"revision": 2, "name": "Secomber Junction", "point": [10, 10], "legs": ["main", "branch"]})
    before = edits_path.read_text()
    for split_index in (0, 2, True, -1):
        with pytest.raises(ValueError):
            routegeometry.save_route_leg({**body, "revision": 3, "split_index": split_index})
        assert edits_path.read_text() == before
    result = routegeometry.save_route_leg({**body, "revision": 3, "split_index": 1})
    first, second = result["splitLegIds"]
    saved = routegeometry.load_route_edits()
    assert saved["revision"] == 4
    assert saved["legs"]["main"] == {"deleted": True}
    assert saved["legs"][first]["points"] == [[0, 0], [10, 10]]
    assert saved["legs"][second]["points"] == [[10, 10], [20, 20]]
    assert saved["legs"][first]["kind"] == "road"
    assert set(next(iter(saved["junctions"].values()))["legs"]) == {"branch", first, second}
    with pytest.raises(ValueError, match="changed elsewhere"):
        routegeometry.save_route_leg({**body, "revision": 3, "split_index": 1})


def test_preserved_path_survives_save_reload_and_split(edits_path):
    body = {"id": "road", "revision": 0, "name": "Road", "kind": "road",
            "points": [[0, 0], [24, 0], [30, 18], [30, 30]],
            "path": [[0, 0], [24, 0], [30, 0], [30, 18], [30, 30]],
            "pointIndices": [0, 1, 3, 4]}
    routegeometry.save_route_leg(body)
    saved = routegeometry.load_route_edits()["legs"]["road"]
    assert saved["path"] == body["path"]
    assert saved["points"] == body["points"]
    result = routegeometry.save_route_leg({**body, "revision": 1, "split_index": 2})
    first, second = [result["legs"][key] for key in result["splitLegIds"]]
    assert first["path"] == body["path"][:4]
    assert first["pointIndices"] == [0, 1, 3]
    assert second["path"] == [[30, 18], [30, 30]]
    assert second["pointIndices"] == [0, 1]
    before = edits_path.read_text()
    for indices in ([0, 1, 2, 4], [0, 1, 3, 99], [0, 1, 3, True]):
        with pytest.raises(ValueError):
            routegeometry.save_route_leg({**body, "revision": 2, "pointIndices": indices})
        assert edits_path.read_text() == before


def test_route_leg_api_dispatch_and_validation(edits_path):
    from faerun.web import ApiError, GET_ROUTES, POST_ROUTES

    save = POST_ROUTES["/api/map-route-leg"]
    read = GET_ROUTES["/api/map-route-legs"]
    assert read(None, {})["revision"] == 0
    assert save(None, {"id": "road:one", "revision": 0, "deleted": True})["revision"] == 1
    with pytest.raises(ApiError):
        save(None, {"id": "road:one", "revision": 0, "deleted": True})


def test_map_leg_write_is_guarded_before_reading_body():
    from faerun.web import ApiError, Handler

    handler = Handler.__new__(Handler)
    handler.path = "/api/map-route-leg"
    sent = []
    calls = []

    def deny(mutation=False):
        calls.append(mutation)
        raise ApiError("Local requests only", 403)

    handler._guard_trade_request = deny
    handler._send_json = lambda payload, status: sent.append((payload, status))
    handler._discard_rejected_trade_body = lambda: None
    handler.do_POST()
    assert calls == [True]
    assert sent == [({"error": "Local requests only"}, 403)]


def test_named_junction_requires_shared_saved_waypoint(edits_path):
    routegeometry.save_route_leg({"id": "main", "revision": 0, "name": "Trade Way", "kind": "road",
                                 "points": [[0, 0], [10, 10], [20, 20]]})
    routegeometry.save_route_leg({"id": "minor", "revision": 1, "name": "Secomber Road", "kind": "road",
                                 "points": [[10, 10], [30, 10]]})
    request = {"revision": 2, "name": "Secomber Junction", "point": [10, 10], "legs": ["main", "minor"]}
    with pytest.raises(ValueError, match="Snap a waypoint"):
        routegeometry.save_road_junction({**request, "point": [11, 11]})
    with pytest.raises(ValueError, match="distinct"):
        routegeometry.save_road_junction({**request, "legs": ["main", "main"]})
    saved = routegeometry.save_road_junction(request)
    assert saved == routegeometry.load_route_edits()
    assert next(iter(saved["junctions"].values())) == {
        "name": "Secomber Junction", "point": [10, 10], "legs": ["main", "minor"]}
    with pytest.raises(ValueError, match="changed elsewhere"):
        routegeometry.save_road_junction(request)
    with pytest.raises(ValueError, match="already exists"):
        routegeometry.save_road_junction({**request, "revision": 3})
    identifier = next(iter(saved["junctions"]))
    routegeometry.save_route_leg({"id": "minor", "revision": 3,
        "name": "Secomber Road: Secomber to Secomber Junction", "kind": "road",
        "points": [[10, 10], [30, 10]]})
    renamed = routegeometry.save_road_junction({**request, "revision": 4, "id": identifier,
        "name": "Trade Way/Secomber Road Junction"})
    assert list(renamed["junctions"]) == [identifier]
    assert renamed["junctions"][identifier]["legs"] == ["main", "minor"]
    assert renamed["legs"]["minor"]["name"] == "Secomber Road: Secomber to Trade Way/Secomber Road Junction"
    assert renamed == routegeometry.load_route_edits()