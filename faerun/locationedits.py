"""Persistent map marker edits, independent of the economic settlement catalog."""

from __future__ import annotations

import json
import math
import threading
from uuid import uuid4

from .atlas import project_root
from .routegeometry import load_route_edits


_LOCK = threading.Lock()
PLACE_TYPES = frozenset({"location", "city", "village", "vale", "town", "hamlet", "fortress", "ruin", "site", "capital",
                         "temple", "bridge", "crypt", "cave", "mine",
                         "shrine", "landmark", "inn", "campsite", "caravan_stop", "trading_post"})


def normalize_location_port(marker):
    marker = dict(marker)
    legacy_type = marker.get("placeType")
    if legacy_type in ("port", "port_capital"):
        marker["placeType"] = "capital" if legacy_type == "port_capital" else "city"
    marker["isPort"] = marker.get("isPort", bool(marker.get("port")) or legacy_type in ("port", "port_capital"))
    return marker


def validate_road_waypoint(identifier, coordinates):
    if not isinstance(identifier, str):
        raise ValueError("Choose a saved road for this waypoint")
    leg = load_route_edits()["legs"].get(identifier)
    if not leg or leg.get("deleted") or leg.get("kind") not in {"road", "track", "trail"}:
        raise ValueError("Choose an existing road, track or trail for this waypoint")
    points = leg.get("path") or leg["points"]
    for start, end in zip(points, points[1:]):
        delta = [end[0] - start[0], end[1] - start[1]]
        length_squared = sum(value * value for value in delta)
        fraction = max(0, min(1, sum((value - origin) * change for value, origin, change
                                     in zip(coordinates, start, delta)) / length_squared)) if length_squared else 0
        nearest = [start[0] + fraction * delta[0], start[1] + fraction * delta[1]]
        if math.dist(nearest, coordinates) < 0.001:
            return leg["name"]
    raise ValueError("Place the waypoint on its road before saving")


def location_edits_path():
    return project_root() / "maps" / "location-edits.json"


def load_location_edits():
    path = location_edits_path()
    if not path.exists():
        return {"revision": 0, "locations": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def apply_location_edits(payload, edits=None):
    edits = load_location_edits() if edits is None else edits
    result = {**payload, "locationRevision": edits["revision"]}
    known = set()
    for collection in ("settlements", "places"):
        result[collection] = []
        for original in payload.get(collection, []):
            identifier = original.get("id") or "place:" + original["name"]
            known.add(identifier)
            edit = edits["locations"].get(identifier, {})
            if edit.get("deleted"):
                continue
            result[collection].append(normalize_location_port({"verified": True, **original, "id": identifier, **edit}))
    for identifier, edit in edits["locations"].items():
        if identifier not in known and identifier.startswith("location:") and not edit.get("deleted"):
            result["settlements"].append(normalize_location_port({"verified": True, **edit, "id": identifier, "mapOnly": True,
                                          "population": 0, "size": "location", "region": ""}))
    markers = {item["id"]: item for item in result["settlements"]}
    for marker in result["settlements"]:
        if marker.get("mobile") and marker.get("status") == "encamped":
            host = markers.get((marker.get("host") or {}).get("id"))
            if host:
                marker.update(x=host["x"], y=host["y"], bx=host["x"], by=host["y"])
    return result


def save_location_edit(body, payload):
    if type(body.get("revision")) is not int:
        raise ValueError("A location needs an integer revision")
    deleted = body.get("deleted", False)
    if type(deleted) is not bool:
        raise ValueError("Deleted must be a boolean")
    with _LOCK:
        edits = load_location_edits()
        if body["revision"] != edits["revision"]:
            raise ValueError("Locations changed elsewhere. Reload before saving.")
        locations = apply_location_edits(payload, edits)
        known = {item["id"]: item for collection in ("settlements", "places")
                 for item in locations[collection]}
        identifier = body.get("id")
        if identifier is not None and (not isinstance(identifier, str) or identifier not in known):
            raise ValueError("Unknown location")
        if identifier and known[identifier].get("mobile"):
            raise ValueError("Moving companies cannot be edited as fixed locations")
        if deleted:
            if identifier is None:
                raise ValueError("Choose a location to delete")
            edit = {"deleted": True}
        else:
            name = body.get("name")
            if not isinstance(name, str) or not name.strip() or len(name.strip()) > 160:
                raise ValueError("A location needs a name of at most 160 characters")
            if any(item["name"].casefold() == name.strip().casefold()
                   for key, item in known.items() if key != identifier):
                raise ValueError("A location with that name already exists")
            coordinates = [body.get("x"), body.get("y")]
            if any(type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 100000
                   for value in coordinates):
                raise ValueError("Locations need two finite world-mile coordinates")
            if identifier and not known[identifier].get("mapOnly") and name.strip() != known[identifier]["name"]:
                raise ValueError("Existing catalog location names cannot be changed here")
            edit = {"name": name.strip(), "x": coordinates[0], "y": coordinates[1], "mapPositionEdited": True}
            previous = known.get(identifier, {})
            verified = body.get("verified", previous.get("verified", True))
            if type(verified) is not bool:
                raise ValueError("Verified must be a boolean")
            place_type = body.get("placeType", previous.get("placeType", "location"))
            legacy_port = isinstance(place_type, str) and place_type in ("port", "port_capital")
            if legacy_port:
                place_type = "capital" if place_type == "port_capital" else "city"
            is_port = body.get("isPort", legacy_port or previous.get("isPort", False))
            if type(is_port) is not bool:
                raise ValueError("Port must be a boolean")
            if not isinstance(place_type, str) or place_type not in PLACE_TYPES:
                raise ValueError("Unknown place type")
            edit.update(verified=verified, placeType=place_type, isPort=is_port)
            for attribute, label in (("portalGate", "Portal gate"), ("gryphonPort", "Gryphon port")):
                value = body.get(attribute, previous.get(attribute, False))
                if type(value) is not bool:
                    raise ValueError(label + " must be a boolean")
                edit[attribute] = value
            acres = body.get("landAcres", known.get(identifier, {}).get("landAcres"))
            if acres is not None:
                if type(acres) not in (int, float) or not math.isfinite(acres) or acres <= 0:
                    raise ValueError("Land acreage must be a finite positive number")
                edit["landAcres"] = acres
            if "landAreaEstimate" in previous and acres == previous.get("landAcres"):
                edit["landAreaEstimate"] = previous["landAreaEstimate"]
            if identifier is None or known[identifier].get("mapOnly"):
                previous = known.get(identifier, {})
                inhabited = body.get("inhabited", previous.get("inhabited", False))
                notes = body.get("notes", previous.get("notes", ""))
                if type(inhabited) is not bool:
                    raise ValueError("Inhabited must be a boolean")
                if not isinstance(notes, str) or len(notes) > 2000:
                    raise ValueError("Place notes must be at most 2000 characters")
                edit.update(placeType=place_type, inhabited=inhabited, notes=notes.strip())
                road_id = body.get("roadLegId", previous.get("roadLegId"))
                if road_id is not None:
                    edit.update(roadLegId=road_id, roadName=validate_road_waypoint(road_id, coordinates))
        identifier = identifier or "location:" + str(uuid4())
        edits["locations"][identifier] = edit
        edits["revision"] += 1
        path = location_edits_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(edits, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
        return {"id": identifier, **apply_location_edits(payload, edits)}