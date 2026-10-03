import copy
import json

import pytest

from faerun import locationedits


@pytest.fixture
def catalog(tmp_path, monkeypatch):
    monkeypatch.setattr(locationedits, "location_edits_path", lambda: tmp_path / "locations.json")
    return {"settlements": [{"id": "town", "name": "Town", "x": 10, "y": 20},
                            {"id": "neighbor", "name": "Neighbor", "x": 30, "y": 40}],
            "places": [{"name": "Tower", "x": 50, "y": 60}]}


def test_add_move_delete_and_reload_without_changing_neighbors(catalog):
    original = copy.deepcopy(catalog)
    created = locationedits.save_location_edit({"revision": 0, "name": "Camp", "x": 1, "y": 2}, catalog)
    assert created["settlements"][-1]["mapOnly"]
    moved = locationedits.save_location_edit({"revision": 1, "id": "town", "name": "Town", "x": 11, "y": 22}, catalog)
    assert moved["settlements"][0]["x"] == 11
    assert moved["settlements"][1] == {"verified": True, "isPort": False, **original["settlements"][1]}
    assert catalog == original
    locationedits.save_location_edit({"revision": 2, "id": "place:Tower", "deleted": True}, catalog)
    locationedits.save_location_edit({"revision": 3, "id": created["id"], "deleted": True}, catalog)
    reloaded = locationedits.apply_location_edits(catalog)
    assert reloaded["places"] == []
    assert len(reloaded["settlements"]) == 2
    assert reloaded["settlements"][0]["y"] == 22


@pytest.mark.parametrize("identifier,name,collection", [("town", "Town", "settlements"), ("place:Tower", "Tower", "places")])
def test_existing_location_type_and_verification_persist(catalog, identifier, name, collection):
    body = {"revision": 0, "id": identifier, "name": name, "x": 10, "y": 20,
            "placeType": "mine", "verified": True}
    locationedits.save_location_edit(body, catalog)
    locationedits.save_location_edit({"revision": 1, "id": identifier, "name": name, "x": 11, "y": 20}, catalog)
    marker = next(item for item in locationedits.apply_location_edits(catalog)[collection] if item["id"] == identifier)
    assert marker["verified"] is True
    assert marker["placeType"] == "mine"
    result = locationedits.save_location_edit({**body, "revision": 2, "verified": False, "placeType": "cave"}, catalog)
    marker = next(item for item in result[collection] if item["id"] == identifier)
    assert marker["verified"] is False
    assert marker["placeType"] == "cave"


@pytest.mark.parametrize("verified", ["yes", 1, None, []])
def test_invalid_verification_is_rejected(catalog, verified):
    with pytest.raises(ValueError, match="Verified"):
        locationedits.save_location_edit({"revision": 0, "name": "Camp", "x": 1, "y": 2, "verified": verified}, catalog)
    assert locationedits.load_location_edits()["revision"] == 0


def test_locations_default_to_verified_without_overriding_explicit_choices(catalog):
    original = copy.deepcopy(catalog)
    result = locationedits.apply_location_edits(catalog)
    assert all(item["verified"] for collection in ("settlements", "places") for item in result[collection])
    assert catalog == original
    created = locationedits.save_location_edit({"revision": 0, "name": "Camp", "x": 1, "y": 2}, catalog)
    assert created["settlements"][-1]["verified"] is True
    edits = {"revision": 0, "locations": {
        "town": {"verified": False},
        "location:legacy": {"name": "Legacy", "x": 1, "y": 2},
    }}
    result = locationedits.apply_location_edits(catalog, edits)
    assert result["settlements"][0]["verified"] is False
    assert result["settlements"][-1]["verified"] is True


@pytest.mark.parametrize("place_type", sorted(locationedits.PLACE_TYPES))
def test_port_attribute_is_independent_of_type(catalog, place_type):
    catalog["settlements"][0]["port"] = "Sea of Swords"
    body = {"revision": 0, "id": "town", "name": "Town", "x": 10, "y": 20,
            "placeType": place_type, "isPort": True}
    locationedits.save_location_edit(body, catalog)
    locationedits.save_location_edit({"revision": 1, "id": "town", "name": "Town", "x": 11, "y": 20}, catalog)
    marker = locationedits.apply_location_edits(catalog)["settlements"][0]
    assert marker["isPort"] is True
    assert marker["placeType"] == place_type
    result = locationedits.save_location_edit({**body, "revision": 2, "isPort": False}, catalog)
    assert result["settlements"][0]["isPort"] is False
    assert result["settlements"][0]["port"] == "Sea of Swords"


@pytest.mark.parametrize("legacy,expected", [("port", "city"), ("port_capital", "capital")])
def test_legacy_port_types_normalize_without_changing_source(catalog, legacy, expected):
    edits = {"revision": 0, "locations": {"town": {"placeType": legacy}}}
    marker = locationedits.apply_location_edits(catalog, edits)["settlements"][0]
    assert marker["placeType"] == expected
    assert marker["isPort"] is True
    assert edits["locations"]["town"]["placeType"] == legacy
    created = locationedits.save_location_edit({"revision": 0, "name": "Harbor", "x": 1, "y": 2,
                                               "placeType": legacy}, catalog)
    assert created["settlements"][-1]["placeType"] == expected
    assert created["settlements"][-1]["isPort"] is True


@pytest.mark.parametrize("is_port", ["yes", 1, None, []])
def test_invalid_port_attribute_is_rejected(catalog, is_port):
    with pytest.raises(ValueError, match="Port"):
        locationedits.save_location_edit({"revision": 0, "name": "Camp", "x": 1, "y": 2, "isPort": is_port}, catalog)


@pytest.mark.parametrize("identifier,name", [("town", "Town"), (None, "New city")])
def test_location_transport_attributes_coexist_and_survive_moves(catalog, identifier, name):
    body = {"revision": 0, "name": name, "x": 10, "y": 20, "placeType": "city",
            "isPort": True, "portalGate": True, "gryphonPort": True}
    if identifier:
        body["id"] = identifier
    created = locationedits.save_location_edit(body, catalog)
    identifier = created["id"]
    moved = locationedits.save_location_edit({"revision": 1, "id": identifier, "name": name, "x": 11, "y": 20}, catalog)
    marker = next(item for item in moved["settlements"] if item["id"] == identifier)
    assert marker["placeType"] == "city"
    assert all(marker[key] for key in ("isPort", "portalGate", "gryphonPort"))
    locationedits.save_location_edit({**body, "id": identifier, "revision": 2, "portalGate": False, "gryphonPort": False}, catalog)
    marker = next(item for item in locationedits.apply_location_edits(catalog)["settlements"] if item["id"] == identifier)
    assert marker["isPort"] is True
    assert marker["portalGate"] is False
    assert marker["gryphonPort"] is False


@pytest.mark.parametrize("attribute", ["portalGate", "gryphonPort"])
@pytest.mark.parametrize("value", ["yes", 1, None, []])
def test_invalid_transport_attributes_are_rejected(catalog, attribute, value):
    with pytest.raises(ValueError, match="must be a boolean"):
        locationedits.save_location_edit({"revision": 0, "name": "Site", "x": 1, "y": 2, attribute: value}, catalog)
    assert locationedits.load_location_edits()["revision"] == 0


def test_encamped_company_follows_edited_host_without_mutating_cached_map(catalog):
    catalog["settlements"].append({"id": "company", "name": "Company", "mobile": True,
        "status": "encamped", "host": {"id": "town"}, "x": 10, "y": 20})
    locationedits.save_location_edit({"revision": 0, "id": "town", "name": "Town", "x": 15, "y": 25}, catalog)
    markers = locationedits.apply_location_edits(catalog)["settlements"]
    assert (markers[-1]["x"], markers[-1]["y"]) == (15, 25)
    assert catalog["settlements"][-1]["x"] == 10


def test_saved_land_area_estimate_survives_move_but_not_acreage_override(catalog):
    snapshot = {"status": "scenario_estimate", "resident_population": 200000,
                "settlement_footprint_sq_miles": 20, "required_agricultural_acres": 400000,
                "surrounding_support_sq_miles": 1250, "combined_sq_miles": 1270}
    edits = {"revision": 0, "locations": {"town": {
        "landAcres": 12800, "landAreaEstimate": snapshot,
    }}}
    locationedits.location_edits_path().write_text(json.dumps(edits), encoding="utf-8")
    body = {"revision": 0, "id": "town", "name": "Town", "x": 11, "y": 20}
    locationedits.save_location_edit(body, catalog)
    reloaded = locationedits.apply_location_edits(catalog)["settlements"][0]
    assert reloaded["landAcres"] == 12800
    assert reloaded["landAreaEstimate"] == snapshot
    locationedits.save_location_edit({**body, "revision": 1, "landAcres": 640}, catalog)
    assert "landAreaEstimate" not in locationedits.apply_location_edits(catalog)["settlements"][0]


def test_waterdeep_saved_land_estimate_matches_population_model():
    from faerun.data.settlements import SETTLEMENTS
    from faerun.population import land_area_report

    settlement = next(item for item in SETTLEMENTS if item.id == "waterdeep")
    saved = locationedits.load_location_edits()["locations"][settlement.id]
    assert (saved["x"], saved["y"]) == (settlement.x, settlement.y)
    marker = locationedits.apply_location_edits({"settlements": [{
        "id": settlement.id, "name": settlement.name, "x": settlement.x, "y": settlement.y,
    }]})["settlements"][0]
    expected = land_area_report(settlement)
    snapshot = marker["landAreaEstimate"]
    for key in ("status", "resident_population", "inputs", "settlement_footprint_sq_miles",
                "required_agricultural_acres", "required_agricultural_sq_miles",
                "surrounding_support_sq_miles", "combined_sq_miles"):
        assert snapshot[key] == expected[key]
    assert marker["landAcres"] == expected["settlement_footprint_sq_miles"] * 640


def test_acreage_is_saved_preserved_on_move_and_can_be_cleared(catalog):
    body = {"revision": 0, "id": "town", "name": "Town", "x": 10, "y": 20, "landAcres": 640}
    result = locationedits.save_location_edit(body, catalog)
    assert result["settlements"][0]["landAcres"] == 640
    moved = locationedits.save_location_edit({"revision": 1, "id": "town", "name": "Town", "x": 11, "y": 20}, catalog)
    assert moved["settlements"][0]["landAcres"] == 640
    cleared = locationedits.save_location_edit({**body, "revision": 2, "landAcres": None}, catalog)
    assert "landAcres" not in cleared["settlements"][0]


@pytest.mark.parametrize("acres", [0, -1, True, float("nan"), float("inf"), "640"])
def test_invalid_acreage_is_rejected(catalog, acres):
    with pytest.raises(ValueError, match="acreage"):
        locationedits.save_location_edit({"revision": 0, "name": "Camp", "x": 1, "y": 2, "landAcres": acres}, catalog)


@pytest.mark.parametrize("changes", [{"x": float("nan")}, {"y": True}, {"name": " "},
                                    {"name": "Town"}, {"id": "missing"}, {"revision": 5},
                                    {"deleted": True}, {"revision": True}])
def test_invalid_changes_are_not_saved(catalog, changes):
    with pytest.raises(ValueError):
        locationedits.save_location_edit({"revision": 0, "name": "Camp", "x": 1, "y": 2, **changes}, catalog)
    assert locationedits.load_location_edits()["revision"] == 0


@pytest.mark.parametrize("place_type", sorted(locationedits.PLACE_TYPES))
def test_places_of_interest_metadata_survives_moves_and_reload(catalog, place_type):
    created = locationedits.save_location_edit({"revision": 0, "name": "Test site", "x": 1, "y": 2,
        "placeType": place_type, "inhabited": place_type == "inn", "notes": "  Hidden entrance  "}, catalog)
    locationedits.save_location_edit({"revision": 1, "id": created["id"], "name": "Test site", "x": 3, "y": 4}, catalog)
    marker = locationedits.apply_location_edits(catalog)["settlements"][-1]
    assert marker["placeType"] == place_type
    assert marker["inhabited"] == (place_type == "inn")
    assert marker["notes"] == "Hidden entrance"
    assert marker["population"] == 0


def test_roadside_waypoint_validates_geometry_and_can_be_detached(catalog, monkeypatch):
    leg = {"name": "Test road", "kind": "road", "points": [[0, 0], [20, 0]],
           "path": [[0, 0], [10, 10], [20, 0]]}
    monkeypatch.setattr(locationedits, "load_route_edits", lambda: {"legs": {"road": leg}})
    body = {"revision": 0, "name": "Wayside Inn", "placeType": "inn", "inhabited": True,
            "x": 5, "y": 5, "roadLegId": "road"}
    result = locationedits.save_location_edit(body, catalog)
    marker = result["settlements"][-1]
    assert marker["roadLegId"] == "road"
    assert marker["roadName"] == "Test road"
    with pytest.raises(ValueError, match="on its road"):
        locationedits.save_location_edit({**body, "id": result["id"], "revision": 1, "y": 2}, catalog)
    leg["deleted"] = True
    with pytest.raises(ValueError, match="existing road"):
        locationedits.save_location_edit({**body, "id": result["id"], "revision": 1}, catalog)
    detached = locationedits.save_location_edit({**body, "id": result["id"], "revision": 1,
                                                "roadLegId": None, "y": 2}, catalog)
    assert "roadLegId" not in detached["settlements"][-1]


@pytest.mark.parametrize("extra", [{"placeType": "unknown"}, {"placeType": []}, {"inhabited": "yes"},
                                  {"notes": "x" * 2001}, {"roadLegId": 4}])
def test_invalid_place_metadata_is_not_saved(catalog, extra):
    with pytest.raises(ValueError):
        locationedits.save_location_edit({"revision": 0, "name": "Site", "x": 1, "y": 2, **extra}, catalog)
    assert locationedits.load_location_edits()["revision"] == 0


def test_edits_refresh_two_worlds_routes_positions_and_revision(catalog, monkeypatch, tmp_path):
    from types import SimpleNamespace
    from faerun import routegeometry
    from faerun.calendar import HarptosDate
    from faerun.world import World

    monkeypatch.setattr(routegeometry, "route_edits_path", lambda: tmp_path / "roads.json")
    routegeometry.save_route_leg({"id": "road", "revision": 0, "name": "Road", "kind": "road",
                                 "points": [[0, 0], [40, 0]]})
    def build_graph(world):
        world._edges = {key: [] for key in world.settlements}
    monkeypatch.setattr(World, "_build_graph", build_graph)

    def new_world():
        world = World.__new__(World)
        world.settlements = {key: SimpleNamespace(id=key, name=key, x=east, y=0,
            security=1, region="Test", zone="Test", traits=[], port=None)
            for key, east in (("west", 0), ("east", 40))}
        world._use_route_edits = world._use_location_edits = True
        world._original_edges = world._edges = {}
        world.revision = 0
        world.date = HarptosDate(1492, 1, 1)
        world.events = {}
        world._events_stamp = None
        world.businesses = {}
        return world

    first, second = new_world(), new_world()
    assert first.route("west", "east")["distance"] == 40
    second.sync_route_edits()
    original_revision = second.revision
    payload = {"settlements": [{"id": "west", "name": "west", "x": 0, "y": 0},
                                {"id": "east", "name": "east", "x": 40, "y": 0}]}
    locationedits.save_location_edit({"id": "east", "name": "east", "revision": 0, "x": 30, "y": 0}, payload)
    assert first.route("west", "east")["distance"] == 30
    assert second.find_settlement("east").x == 30
    assert second.route("west", "east")["distance"] == 30
    assert second.revision > original_revision
    current_revision = second.revision
    second.sync_route_edits()
    assert second.revision == current_revision
    created = locationedits.save_location_edit({"revision": 1, "name": "Wayside Inn", "x": 15, "y": 0,
        "placeType": "inn", "roadLegId": "road", "inhabited": True}, payload)
    assert second.route("west", "Wayside Inn")["distance"] == 15
    assert created["id"] not in second.settlements
    locationedits.save_location_edit({"revision": 2, "id": "east", "deleted": True}, payload)
    assert second.lookup_settlement("east") is None
    assert "east" not in second.route_nodes
    assert first.lookup_settlement("east") is None