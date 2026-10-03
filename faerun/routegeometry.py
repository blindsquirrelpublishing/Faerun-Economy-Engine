"""User-authored map leg geometry, separate from the economic route graph."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
import threading
from typing import Any
from uuid import uuid4

from .atlas import project_root


LEG_TYPES = frozenset({
    "road", "trail", "track", "sea", "river", "barge", "ferry", "portage",
    "tunnel", "teleport", "air", "skyship",
})
_LOCK = threading.Lock()


def route_edits_path() -> Path:
    return project_root() / "maps" / "route-leg-edits.json"


def load_route_edits() -> dict[str, Any]:
    path = route_edits_path()
    if not path.exists():
        return {"format": "faerun-route-leg-edits-v1", "revision": 0, "legs": {}}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(payload, dict)
            or payload.get("format") != "faerun-route-leg-edits-v1"
            or not isinstance(payload.get("revision"), int)
            or not isinstance(payload.get("legs"), dict)):
        raise ValueError("Unsupported map route edits file")
    return payload


def save_route_leg(body: dict[str, Any]) -> dict[str, Any]:
    identifier = body.get("id")
    if not isinstance(identifier, str) or not identifier or len(identifier) > 1000:
        raise ValueError("A map leg needs an ID of at most 1000 characters")
    revision = body.get("revision")
    if type(revision) is not int or revision < 0:
        raise ValueError("A map leg needs an integer revision")
    deleted = body.get("deleted", False)
    if not isinstance(deleted, bool):
        raise ValueError("Deleted must be a boolean")
    leg: dict[str, Any] = {"deleted": deleted}
    if not deleted:
        name, kind, points = body.get("name"), body.get("kind"), body.get("points")
        if not isinstance(name, str) or not name.strip() or len(name) > 160:
            raise ValueError("A map leg needs a name of at most 160 characters")
        if not isinstance(kind, str) or kind not in LEG_TYPES:
            raise ValueError("Unknown map leg type")
        if not isinstance(points, list) or not 2 <= len(points) <= 10000:
            raise ValueError("A map leg needs between 2 and 10000 waypoints")
        clean = []
        for point in points:
            if (not isinstance(point, list) or len(point) != 2
                    or any(type(value) not in (int, float)
                           or not math.isfinite(value) or abs(value) > 100000
                           for value in point)):
                raise ValueError("Waypoints must contain two finite world-mile coordinates")
            clean.append([float(value) for value in point])
        if not any(point != clean[0] for point in clean[1:]):
            raise ValueError("A map leg must have distinct waypoints")
        leg.update(name=name.strip(), kind=kind, points=clean)
        if "path" in body or "pointIndices" in body:
            path, indices = body.get("path"), body.get("pointIndices")
            if not isinstance(path, list) or not 2 <= len(path) <= 10000:
                raise ValueError("A preserved path needs between 2 and 10000 vertices")
            for point in path:
                if (not isinstance(point, list) or len(point) != 2
                        or any(type(value) not in (int, float) or not math.isfinite(value)
                               or abs(value) > 100000 for value in point)):
                    raise ValueError("Invalid preserved path coordinates")
            if (not isinstance(indices, list) or len(indices) != len(clean)
                    or any(type(index) is not int or not 0 <= index < len(path) for index in indices)
                    or indices[0] != 0 or indices[-1] != len(path) - 1
                    or any(a >= b for a, b in zip(indices, indices[1:]))
                    or any(path[index] != point for index, point in zip(indices, clean))):
                raise ValueError("Waypoints must match ordered preserved path vertices")
            leg.update(path=path, pointIndices=indices)
    split_index = body.get("split_index")
    if split_index is not None:
        if deleted or type(split_index) is not int or not 0 < split_index < len(leg["points"]) - 1:
            raise ValueError("Choose an interior waypoint to split the leg")
        for section in (leg["points"][:split_index + 1], leg["points"][split_index:]):
            if not any(point != section[0] for point in section[1:]):
                raise ValueError("Both split legs must have nonzero length")
    with _LOCK:
        payload = load_route_edits()
        if revision != payload["revision"]:
            raise ValueError("Map legs changed elsewhere. Reload before saving; your draft has not been saved.")
        split_ids = []
        if split_index is None:
            payload["legs"][identifier] = leg
            for junction in payload.get("junctions", {}).values():
                connected = (not deleted and leg.get("kind") in {"road", "trail", "track"}
                             and any(math.dist(junction["point"], point) < 0.001
                                     for point in leg["points"]))
                if identifier in junction["legs"] and not connected:
                    junction["legs"].remove(identifier)
                elif connected and identifier not in junction["legs"]:
                    junction["legs"].append(identifier)
        else:
            payload["legs"][identifier] = {"deleted": True}
            for number, section in enumerate((leg["points"][:split_index + 1], leg["points"][split_index:]), 1):
                child_id = "custom:" + str(uuid4())
                split_ids.append(child_id)
                payload["legs"][child_id] = {**leg, "name": leg["name"][:151] + f" (part {number})", "points": section}
                if "path" in leg:
                    cut = leg["pointIndices"][split_index]
                    child = payload["legs"][child_id]
                    child["path"] = leg["path"][:cut + 1] if number == 1 else leg["path"][cut:]
                    child["pointIndices"] = (leg["pointIndices"][:split_index + 1] if number == 1
                                             else [index - cut for index in leg["pointIndices"][split_index:]])
            for junction in payload.get("junctions", {}).values():
                if identifier not in junction["legs"]:
                    continue
                junction["legs"].remove(identifier)
                junction["legs"].extend(child_id for child_id in split_ids if any(
                    math.dist(junction["point"], point) < 0.001 for point in payload["legs"][child_id]["points"]))
        payload["revision"] += 1
        path = route_edits_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
        return {**payload, "splitLegIds": split_ids} if split_ids else payload


def build_edited_network(settlements, original_edges, payload, locations=None):
    from dataclasses import replace
    from types import SimpleNamespace
    from .world import Edge

    nodes = {**settlements, **(locations or {})}
    graph = {identifier: [] for identifier in settlements}
    junctions = payload.get("junctions", {})
    edits = payload["legs"]

    def node_at(point, leg_id):
        for identifier, junction in junctions.items():
            if leg_id in junction["legs"] and math.dist(point, junction["point"]) < 0.001:
                key = "junction:" + identifier
                name = junction["name"]
                break
        else:
            closest = min(settlements.values(), key=lambda place: math.dist(point, (place.x, place.y)))
            if math.dist(point, (closest.x, closest.y)) <= 2.5:
                return closest.id
            key = "waypoint:%.6f,%.6f" % tuple(point)
            name = "Road waypoint (%.6f, %.6f)" % tuple(point)
        if key not in nodes:
            closest = min(settlements.values(), key=lambda place: math.dist(point, (place.x, place.y)))
            nodes[key] = SimpleNamespace(id=key, name=name, x=point[0], y=point[1],
                security=closest.security, region=closest.region, zone=getattr(closest, "zone", ""), traits=[], port=None)
        return key

    def connect(edge):
        graph.setdefault(edge.src, []).append(edge)

    for edges in original_edges.values():
        for edge in edges:
            if edge.kind not in {"air", "skyship", "teleport"}:
                continue
            endpoints = sorted((edge.src, edge.dst))
            identifier = "route:" + edge.name + "|" + "|".join(endpoints)
            if identifier not in edits:
                name = payload.get("names", {}).get(identifier)
                connect(replace(edge, name=name, map_leg_id=identifier) if name else edge)

    for identifier, leg in edits.items():
        if leg.get("deleted"):
            continue
        points = leg.get("path") or leg["points"]
        attachments = {}
        for place in list(settlements.values()) + list((locations or {}).values()):
            road_id = getattr(place, "road_leg_id", None)
            if road_id and road_id != identifier:
                continue
            nearest = None
            for index, (start, end) in enumerate(zip(points, points[1:])):
                delta = [end[0] - start[0], end[1] - start[1]]
                length_squared = sum(value * value for value in delta)
                fraction = max(0, min(1, ((place.x - start[0]) * delta[0] +
                    (place.y - start[1]) * delta[1]) / length_squared)) if length_squared else 0
                point = [start[0] + fraction * delta[0], start[1] + fraction * delta[1]]
                distance = math.dist(point, (place.x, place.y))
                if distance <= 2.5 and (nearest is None or distance < nearest[0]):
                    nearest = (distance, index, fraction, point)
            if nearest is not None:
                _, index, fraction, point = nearest
                attachments.setdefault(index, []).append((fraction, point, place.id))
        expanded = []
        attached_nodes = {}
        for index, point in enumerate(points):
            if not expanded or expanded[-1] != point:
                expanded.append(point)
            for fraction, projection, node_id in sorted(attachments.get(index, [])):
                if expanded[-1] != projection:
                    expanded.append(projection)
                attached_nodes[len(expanded) - 1] = node_id
        points = expanded
        anchors = []
        distance = 0.0
        for index, point in enumerate(points):
            if index:
                distance += math.dist(points[index - 1], point)
            shared = any(identifier in junction["legs"] and math.dist(point, junction["point"]) < 0.001
                         for junction in junctions.values())
            if index in (0, len(points) - 1) or shared or index in attached_nodes:
                anchors.append((attached_nodes.get(index) or node_at(point, identifier), distance, index))
        quality = 0.85 if leg["kind"] == "road" else 0.7 if leg["kind"] in {"trail", "track"} else 1.0
        for (start, start_distance, start_index), (end, end_distance, end_index) in zip(anchors, anchors[1:]):
            if start == end or end_distance <= start_distance:
                continue
            geometry = points[start_index:end_index + 1]
            connect(Edge(start, end, end_distance - start_distance, quality, leg["kind"], leg["name"],
                         mapped=True, map_leg_id=identifier, points=geometry))
            connect(Edge(end, start, end_distance - start_distance, quality, leg["kind"], leg["name"],
                         mapped=True, map_leg_id=identifier, points=list(reversed(geometry))))
    return graph, nodes


def save_road_junction(body: dict[str, Any]) -> dict[str, Any]:
    deleted = body.get("deleted", False)
    if type(deleted) is not bool:
        raise ValueError("Deleted must be a boolean")
    if deleted:
        if type(body.get("revision")) is not int:
            raise ValueError("A junction needs an integer revision")
        with _LOCK:
            payload = load_route_edits()
            if body["revision"] != payload["revision"]:
                raise ValueError("Map legs changed elsewhere. Reload before saving.")
            identifier = body.get("id")
            junctions = payload.get("junctions", {})
            if not isinstance(identifier, str) or identifier not in junctions:
                raise ValueError("Unknown junction")
            del junctions[identifier]
            payload["revision"] += 1
            path = route_edits_path()
            temporary = path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            temporary.replace(path)
            return payload
    name = body.get("name")
    point = body.get("point")
    identifiers = body.get("legs")
    if name is not None and (not isinstance(name, str) or not name.strip() or len(name) > 160):
        raise ValueError("A junction needs a name of at most 160 characters")
    if (not isinstance(point, list) or len(point) != 2
            or any(type(value) not in (int, float) or not math.isfinite(value)
                   or abs(value) > 100000 for value in point)):
        raise ValueError("A junction needs two finite world-mile coordinates")
    if (not isinstance(identifiers, list) or not 1 <= len(identifiers) <= 20
            or any(not isinstance(identifier, str) for identifier in identifiers)
            or len(set(identifiers)) != len(identifiers)):
        raise ValueError("Choose at least one distinct saved road leg")
    if type(body.get("revision")) is not int:
        raise ValueError("A junction needs an integer revision")
    with _LOCK:
        payload = load_route_edits()
        if body["revision"] != payload["revision"]:
            raise ValueError("Map legs changed elsewhere. Reload before saving.")
        for identifier in identifiers:
            leg = payload["legs"].get(identifier)
            if not leg or leg.get("deleted") or leg.get("kind") not in {"road", "trail", "track"}:
                raise ValueError("Junctions must join saved road, trail or track legs")
            if not any(math.dist(point, waypoint) < 0.001 for waypoint in leg["points"]):
                raise ValueError("Snap a waypoint on each leg to the junction before saving")
        junctions = payload.setdefault("junctions", {})
        junction_id = body.get("id")
        if junction_id is not None and (not isinstance(junction_id, str) or junction_id not in junctions):
            raise ValueError("Unknown junction")
        if name is None:
            if junction_id:
                name = junctions[junction_id]["name"]
            else:
                names = []
                for identifier in identifiers:
                    base = re.sub(r" \(part [12]\)$", "", payload["legs"][identifier]["name"])
                    base = base.partition(": ")[0].strip()
                    if base and base.casefold() not in {item.casefold() for item in names}:
                        names.append(base)
                stem = ("/".join(names) or "Waypoint")[:140]
                name = stem + " Junction"
                existing = {junction["name"].casefold() for junction in junctions.values()}
                number = 2
                while name.casefold() in existing:
                    name = f"{stem} Junction {number}"
                    number += 1
        if any(junction["name"].casefold() == name.strip().casefold()
               for key, junction in junctions.items() if key != junction_id):
            raise ValueError("A junction with that name already exists")
        if junction_id:
            old_name = junctions[junction_id]["name"]
            for leg in payload["legs"].values():
                if leg.get("deleted") or leg.get("kind") != "road":
                    continue
                base, separator, endpoints = leg["name"].partition(": ")
                if separator and " to " in endpoints:
                    origin, destination = endpoints.split(" to ", 1)
                    origin = name.strip() if origin == old_name else origin
                    destination = name.strip() if destination == old_name else destination
                    leg["name"] = f"{base}: {origin} to {destination}"
                    if len(leg["name"]) > 160:
                        raise ValueError("Renamed road name exceeds 160 characters")
        junctions[junction_id or str(uuid4())] = {"name": name.strip(), "point": point, "legs": identifiers}
        payload["revision"] += 1
        path = route_edits_path()
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
        return payload