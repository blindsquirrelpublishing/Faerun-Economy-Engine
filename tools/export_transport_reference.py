"""Export direct legs or a separate fastest-route transportation reference."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from faerun.world import FREIGHT_RATE, World, describe_modes


LEG_FIELDS = (
    "leg_id", "origin_id", "origin", "destination_id", "destination", "connection",
    "mode", "mode_label", "mixed_mode", "inferred", "distance_miles",
    "quality", "effective_speed_miles_per_day", "travel_days", "risk_premium",
    "freight_gp_per_100_lb", "freight_gp_per_2000_lb",
)
CARRIER_FIELDS = (
    "leg_id", "origin", "destination", "connection", "edge_mode", "carrier_mode",
    "carrier", "inferred", "mixed_edge_component", "distance_miles", "max_load_lb",
    "speed_miles_per_day", "travel_days", "full_load_base_cost_gp",
    "base_cost_gp_per_ton_mile",
)


def reference_rows(world):
    legs, carriers = [], []
    edges = sorted(
        (edge for adjacent in world._edges.values() for edge in adjacent),
        key=lambda edge: (edge.src, edge.dst, edge.kind, edge.name, edge.distance, edge.quality),
    )
    for number, edge in enumerate(edges, 1):
        origin = world.settlements[edge.src].name
        destination = world.settlements[edge.dst].name
        leg_id = f"LEG-{number:06d}"
        risk = world.edge_risk(edge)
        unit_cost = edge.freight_units(risk) * FREIGHT_RATE
        legs.append(dict(zip(LEG_FIELDS, (
            leg_id, edge.src, origin, edge.dst, destination, edge.name,
            edge.kind, describe_modes(edge.kind), edge.multimodal, edge.inferred,
            round(edge.distance, 6), edge.quality, round(edge.speed, 6),
            round(edge.days, 6), round(risk, 6), round(unit_cost * 100, 6),
            round(unit_cost * 2000, 6),
        ))))
        for option in edge.carrier_options():
            carriers.append(dict(zip(CARRIER_FIELDS, (
                leg_id, origin, destination, edge.name, edge.kind, option["mode"],
                option["name"], edge.inferred, edge.multimodal, round(edge.distance, 6),
                option["max_load_lb"], option["speed_miles_per_day"], option["days"],
                option["cost_gp"], option["cost_gp_per_ton_mile"],
            ))))
    return legs, carriers


def export_reference(destination):
    world = World()
    legs, carriers = reference_rows(world)
    destination.mkdir(parents=True, exist_ok=True)
    for name, fields, rows in (
        ("direct-legs.csv", LEG_FIELDS, legs),
        ("direct-leg-carriers.csv", CARRIER_FIELDS, carriers),
    ):
        with (destination / name).open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    return legs, carriers


def fastest_rows(world, location_ids, *, cheapest=False, allowed_modes=None):
    rows = []

    def weight(edge):
        if allowed_modes is not None and not set(edge.modes) <= allowed_modes:
            return float("inf")
        if cheapest:
            return edge.freight_units(world.edge_risk(edge)) * FREIGHT_RATE * 100
        return edge.days

    for origin in location_ids:
        scores, previous = world._dijkstra(origin, weight)
        for destination in location_ids:
            route = []
            reachable = destination in scores
            node = destination
            while reachable and node != origin:
                edge = previous[node]
                route.append(edge)
                node = edge.src
            route.reverse()
            rows.append({
                "origin": world.settlements[origin].name,
                "destination": world.settlements[destination].name,
                "reachable": reachable,
                "distance_miles": round(sum(edge.distance for edge in route), 6) if reachable else None,
                "travel_days": round(sum(edge.days for edge in route), 6) if reachable else None,
                "freight_gp_per_100_lb": round(sum(
                    edge.freight_units(world.edge_risk(edge)) * FREIGHT_RATE * 100
                    for edge in route), 6) if reachable else None,
                "leg_count": len(route) if reachable else None,
                "uses_inferred": any(edge.inferred for edge in route),
                "path": " -> ".join([world.settlements[origin].name] + [
                    world.settlements[edge.dst].name for edge in route]) if reachable else "",
                "leg_modes": " -> ".join(edge.kind for edge in route),
                "leg_connections": " -> ".join(edge.name for edge in route),
            })
    return rows


def schedule_rows(world, location_ids):
    options = {}
    for label, cheapest, modes in (
        ("Fastest", False, None),
        ("Lowest freight", True, None),
        ("Land only", False, {"road", "trail", "track"}),
        ("Water only", False, {"sea", "river", "barge", "ferry"}),
    ):
        for row in fastest_rows(world, location_ids, cheapest=cheapest, allowed_modes=modes):
            if not row["reachable"] or row["origin"] == row["destination"]:
                continue
            identity = (row["origin"], row["destination"], row["path"],
                        row["leg_modes"], row["leg_connections"], row["travel_days"],
                        row["distance_miles"], row["freight_gp_per_100_lb"])
            if identity in options:
                options[identity]["selection"] += "; " + label
            else:
                options[identity] = {"option_id": "", "selection": label,
                                     "connections": row["leg_count"] - 1, **row}
    rows = sorted(options.values(), key=lambda row: (
        row["origin"], row["destination"], row["travel_days"], row["freight_gp_per_100_lb"]))
    for number, row in enumerate(rows, 1):
        row["option_id"] = f"OPT-{number:04d}"
    return rows


def export_schedule(destination):
    world = World()
    location_ids = ["waterdeep"] + sorted({edge.dst for edge in world._edges["waterdeep"]})
    rows = schedule_rows(world, location_ids)
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "transport-options.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def export_fastest(destination):
    world = World()
    location_ids = ["waterdeep"] + sorted({edge.dst for edge in world._edges["waterdeep"]})
    rows = fastest_rows(world, location_ids)
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "fastest-routes.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    names = [world.settlements[location].name for location in location_ids]
    lookup = {(row["origin"], row["destination"]): row for row in rows}
    for field, name in (("distance_miles", "distance-miles"), ("travel_days", "time-days"),
                        ("freight_gp_per_100_lb", "cost-gp-per-100lb")):
        with (destination / f"fastest-{name}-matrix.csv").open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["From / To", *names])
            for origin in names:
                writer.writerow([origin, *(lookup[origin, target][field] for target in names)])
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("reference/transport"))
    parser.add_argument("--fastest", action="store_true", help="Export fastest routes for Waterdeep and its direct neighbors")
    parser.add_argument("--schedule", action="store_true", help="Export distinct transport itinerary alternatives")
    args = parser.parse_args()
    if args.schedule:
        rows = export_schedule(args.output)
        print(f"Exported {len(rows)} transport options to {args.output}")
        return
    if args.fastest:
        rows = export_fastest(args.output)
        print(f"Exported {len(rows)} fastest-route cells to {args.output}")
        return
    legs, carriers = export_reference(args.output)
    print(f"Exported {len(legs)} directed legs and {len(carriers)} carrier options to {args.output}")


if __name__ == "__main__":
    main()