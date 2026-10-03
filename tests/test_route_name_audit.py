from copy import deepcopy

from tools.audit_route_names import audit


def test_name_audit_changes_only_labels_and_is_repeatable():
    places = [{"id": "a", "name": "Alpha", "x": 0, "y": 0},
              {"id": "b", "name": "Beta", "x": 20, "y": 0}]
    payload = {"revision": 3, "legs": {
        "road": {"name": "New leg", "kind": "road", "points": [[0, 0], [10, 0], [20, 0]]},
        "trail": {"name": "The Black Road (part 2) (part 1)", "kind": "trail",
                  "points": [[0, 0], [10, 0]]},
        "named": {"name": "The High Road", "kind": "road", "points": [[0, 0], [20, 0]]},
        "deleted": {"deleted": True}}, "junctions": {
        "junction": {"name": "New leg Junction 2", "point": [10, 0], "legs": ["road", "trail"]}}}
    original = deepcopy(payload)
    routes = [{"a": "a", "b": "b", "name": "Teleportation circle"}]
    updated, report = audit(payload, places, routes)
    assert payload == original
    assert updated["junctions"]["junction"]["name"] == "Alpha East Junction"
    assert updated["legs"]["road"]["name"] == "Alpha to Beta Road"
    assert updated["legs"]["trail"]["name"] == "The Black Road: Alpha to Alpha East Junction"
    assert updated["legs"]["named"] == original["legs"]["named"]
    assert updated["names"] == {"route:Teleportation circle|a|b": "Alpha to Beta Portal"}
    for key, value in updated["legs"].items():
        assert {k: v for k, v in value.items() if k != "name"} == {
            k: v for k, v in original["legs"][key].items() if k != "name"}
    second, rerun = audit(updated, places, routes)
    assert second == updated
    assert not rerun["legs"] and not rerun["junctions"] and not rerun["base_legs"]
    assert len(report["legs"]) == 2


def test_portal_name_override_preserves_price_inputs():
    from types import SimpleNamespace
    from faerun.routegeometry import build_edited_network
    from faerun.world import Edge

    places = {key: SimpleNamespace(id=key, name=key, x=x, y=0, security=1, region="Test")
              for key, x in (("a", 0), ("b", 20))}
    edge = Edge("a", "b", 30, 1.3, "teleport", "Teleportation circle")
    graph, _ = build_edited_network(places, {"a": [edge]}, {"legs": {},
        "names": {"route:Teleportation circle|a|b": "Alpha to Beta Portal"}})
    renamed = graph["a"][0]
    assert renamed.name == "Alpha to Beta Portal"
    assert renamed.carrier_options() == edge.carrier_options()
    assert renamed.days == edge.days
    assert edge.name == "Teleportation circle"