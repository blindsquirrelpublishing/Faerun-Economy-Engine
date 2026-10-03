"""Audit and replace generic saved-map labels without changing connectivity."""

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import shutil
from urllib.request import urlopen


GENERIC = re.compile(r"\b(?:new leg|unnamed|untitled|map leg)\b|^junction(?:\s+\d+)?$", re.I)
NUMBERED_JUNCTION = re.compile(r"\bJunction\s+\d+$", re.I)
PART = re.compile(r"(?:\s+\(part \d+\))+$", re.I)
KINDS = {"road": "Road", "trail": "Trail", "track": "Track", "ferry": "Ferry",
         "sea": "Sea Route", "river": "River Route", "barge": "Barge Route",
         "portage": "Portage", "tunnel": "Tunnel", "air": "Flight",
         "skyship": "Skyship Route", "teleport": "Portal"}


def audit(payload, places, routes=()):
    updated = deepcopy(payload)
    places = [place for place in places if not place.get("mobile")]
    if not places:
        raise ValueError("No settlement coordinates available")
    junctions = updated.get("junctions", {})
    report = {"revision": payload["revision"], "legs": [], "junctions": [], "warnings": [], "base_legs": []}

    def nearest(point):
        place = min(places, key=lambda item: math.dist(point, (item["x"], item["y"])))
        distance = math.dist(point, (place["x"], place["y"]))
        return place, distance

    def local_label(point):
        place, distance = nearest(point)
        if distance <= 2.5:
            return place["name"], distance
        angle = math.atan2(point[0] - place["x"], place["y"] - point[1])
        direction = ("North", "Northeast", "East", "Southeast", "South", "Southwest", "West", "Northwest")[round(angle / (math.pi / 4)) % 8]
        return place["name"] + " " + direction, distance

    used = {item["name"].casefold() for item in places}
    used.update(item["name"].casefold() for item in junctions.values()
                if not GENERIC.search(item["name"]) and not NUMBERED_JUNCTION.search(item["name"]))
    replacements = {}
    for identifier, junction in junctions.items():
        old = junction["name"]
        if not (GENERIC.search(old) or NUMBERED_JUNCTION.search(old)):
            continue
        label, distance = local_label(junction["point"])
        stem = label + " Junction"
        name = stem
        number = 2
        while name.casefold() in used:
            name = f"{stem} {number}"
            number += 1
        used.add(name.casefold())
        junction["name"] = name
        replacements[old] = name
        report["junctions"].append({"id": identifier, "old": old, "new": name,
                                     "nearest_settlement_miles": round(distance, 2)})

    def endpoint(point):
        for junction in junctions.values():
            if math.dist(point, junction["point"]) < 0.001:
                return junction["name"]
        label, distance = local_label(point)
        return label if distance <= 2.5 else label + " Waypoint"

    for identifier, leg in updated["legs"].items():
        if leg.get("deleted"):
            continue
        old = leg["name"]
        name = old
        if GENERIC.search(old):
            points = leg.get("path") or leg["points"]
            start, end = endpoint(points[0]), endpoint(points[-1])
            if start == end:
                name = start + " " + KINDS[leg["kind"]] + " Loop"
            else:
                name = start + " to " + end + " " + KINDS[leg["kind"]]
        elif PART.search(old):
            points = leg.get("path") or leg["points"]
            base = PART.sub("", old).partition(": ")[0]
            name = base + ": " + endpoint(points[0]) + " to " + endpoint(points[-1])
        else:
            for before, after in sorted(replacements.items(), key=lambda item: -len(item[0])):
                name = re.sub(re.escape(before) + r"(?![\w\d])", lambda match: after, name)
        if name != old:
            if len(name) > 160:
                raise ValueError(f"Proposed name exceeds 160 characters: {name}")
            leg["name"] = name
            report["legs"].append({"id": identifier, "old": old, "new": name, "kind": leg["kind"]})
        for point in (leg["points"][0], leg["points"][-1]):
            if not any(math.dist(point, item["point"]) < 0.001 for item in junctions.values()):
                place, distance = nearest(point)
                if distance > 2.5:
                    report["warnings"].append({"id": identifier, "nearest": place["name"],
                                               "miles": round(distance, 2), "point": point})

    for collection in ("legs", "junctions"):
        for identifier, before in payload.get(collection, {}).items():
            after = updated[collection][identifier]
            assert {key: value for key, value in before.items() if key != "name"} == {
                key: value for key, value in after.items() if key != "name"}
    assert not any(GENERIC.search(item["name"]) for item in updated["legs"].values() if not item.get("deleted"))
    assert not any(GENERIC.search(item["name"]) for item in junctions.values())
    assert len({item["name"].casefold() for item in junctions.values()}) == len(junctions)
    by_id = {place["id"]: place for place in places}
    for route in routes:
        identifier = "route:" + route["name"] + "|" + "|".join(sorted((route["a"], route["b"])))
        if identifier in payload["legs"]:
            continue
        old = payload.get("names", {}).get(identifier, route["name"])
        if old.casefold() != "teleportation circle":
            continue
        start, end = by_id[route["a"]]["name"], by_id[route["b"]]["name"]
        name = start + " to " + end + " Portal"
        updated.setdefault("names", {})[identifier] = name
        report["base_legs"].append({"id": identifier, "old": old, "new": name})
    report["active_legs_audited"] = sum(not leg.get("deleted") for leg in payload["legs"].values())
    report["junctions_audited"] = len(junctions)
    return updated, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8893")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--revision", type=int)
    args = parser.parse_args()
    path = Path(__file__).resolve().parents[1] / "maps" / "route-leg-edits.json"
    original = path.read_bytes()
    payload = json.loads(original)
    with urlopen(args.url + "/api/map", timeout=120) as response:
        map_data = json.load(response)
    updated, report = audit(payload, map_data["settlements"], map_data["routes"])
    if args.apply:
        if args.revision is None or payload["revision"] != args.revision:
            raise ValueError("Specify the audited current revision before applying")
        if path.read_bytes() != original:
            raise ValueError("Map edited during audit; rerun before applying")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = path.with_name("route-leg-edits.before-name-audit-" + timestamp + ".json")
        shutil.copy2(path, backup)
        updated["revision"] += 1
        temporary = path.with_suffix(".audit.tmp")
        temporary.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")
        if path.read_bytes() != original:
            temporary.unlink()
            raise ValueError("Concurrent edits detected; names were not applied")
        temporary.replace(path)
        assert json.loads(path.read_text(encoding="utf-8")) == updated
        report["backup"] = str(backup)
        report["saved_revision"] = updated["revision"]
        output = path.with_name("route-name-audit-" + timestamp + ".json")
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["report"] = str(output)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()