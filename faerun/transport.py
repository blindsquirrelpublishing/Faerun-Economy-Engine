"""Shipment route alternatives and explicit, user-supplied cost allowances."""

import hashlib
import json
import math
from dataclasses import replace

from .world import FREIGHT_RATE, MULTIMODAL_COST, MULTIMODAL_DELAY


def shipment_leg(world, edge, pounds, premium, minimum, choices):
    identity = (edge.src, edge.dst, edge.kind, edge.name, edge.distance, edge.quality)
    leg_id = hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:20]
    selected = choices.get(leg_id, {})
    if not set(selected) <= set(edge.modes):
        raise ValueError("Selected transport mode is not available on this leg")
    extra = len(edge.modes) - 1
    cost_adjustment = (1 + premium) * (1 + MULTIMODAL_COST * extra)
    time_adjustment = 1 / max(0.35, 1 - MULTIMODAL_DELAY * extra)
    stages = []
    carriers = []
    for mode in edge.modes:
        segment = replace(edge, kind=mode, distance=edge.distance / len(edge.modes))
        options = []
        for carrier in segment.carrier_options():
            count = math.ceil(pounds / carrier["max_load_lb"])
            load_cost = carrier["cost_gp"] * cost_adjustment
            options.append({"name": carrier["name"], "mode": mode,
                            "capacity_lb": carrier["max_load_lb"], "shipments_required": count,
                            "full_load_cost_gp": load_cost, "shipment_cost_gp": load_cost * count,
                            "travel_days": carrier["days"] * time_adjustment,
                            "selected": selected.get(mode) == carrier["name"]})
        chosen = next((carrier for carrier in options if carrier["selected"]), None)
        if selected.get(mode) and chosen is None:
            raise ValueError("Selected carrier is not available on this leg")
        shared_cost = segment.freight_units(0) * FREIGHT_RATE * pounds * cost_adjustment
        stages.append({"mode": mode, "distance_miles": segment.distance,
                       "selected_carrier": chosen["name"] if chosen else "",
                       "shared_cost_gp": shared_cost,
                       "shared_travel_days": segment.days * time_adjustment,
                       "cost_gp": chosen["shipment_cost_gp"] if chosen else shared_cost,
                       "travel_days": chosen["travel_days"] if chosen else segment.days * time_adjustment,
                       "carriers": options})
        carriers.extend(options)
    freight = sum(stage["cost_gp"] for stage in stages)
    return {"id": leg_id, "origin": world.settlements[edge.src].name,
            "destination": world.settlements[edge.dst].name, "connection": edge.name,
            "mode": edge.kind, "distance_miles": edge.distance,
            "travel_days": sum(stage["travel_days"] for stage in stages),
            "line_haul_gp": freight, "minimum_topup_gp": max(0, minimum - freight),
            "risk_premium": premium, "inferred": edge.inferred,
            "carrier_loads": carriers, "transport_stages": stages}


def direct_path(world, origin, destination, weight):
    scores, previous = world._dijkstra(origin, weight)
    if destination not in scores:
        return None
    legs = []
    node = destination
    while node != origin:
        edge = previous[node]
        legs.append(edge)
        node = edge.src
    return list(reversed(legs))


def plan_shipment(world, origin, destination, *, pounds=100, minimum=0, handling=0,
                  daily=0, fixed=0, contingency=0, include_inferred=False,
                  include_events=False, allow_special=False, purchase_per_lb=None,
                  carrier_choices=None):
    if carrier_choices is None:
        carrier_choices = {}
    if not isinstance(carrier_choices, dict) or any(
        not isinstance(key, str) or not isinstance(modes, dict) or any(
            not isinstance(mode, str) or not isinstance(name, str) for mode, name in modes.items())
        for key, modes in carrier_choices.items()
    ):
        raise ValueError("carrier_choices must map leg IDs to mode/carrier names")
    values = {"pounds": pounds, "minimum": minimum, "handling": handling,
              "daily": daily, "fixed": fixed, "contingency": contingency}
    if purchase_per_lb is not None:
        values["purchase_per_lb"] = purchase_per_lb
    for name, value in values.items():
        if not math.isfinite(value) or value < 0 or value > 1e9:
            raise ValueError(f"{name} must be a finite non-negative number no greater than 1 billion")
    if pounds == 0:
        raise ValueError("Shipment weight must be greater than zero")
    if contingency > 100:
        raise ValueError("Contingency must be between 0 and 100 percent")
    start, end = world.find_settlement(origin), world.find_settlement(destination)
    if start.id == end.id:
        raise ValueError("Choose different origin and destination locations")

    def risk(edge):
        if include_events:
            return world.edge_risk(edge)
        security = (world.settlements[edge.src].security + world.settlements[edge.dst].security) / 2
        return edge.hazard(security) * 0.6

    def freight(edge):
        return edge.freight_units(risk(edge)) * FREIGHT_RATE * pounds

    options = {}
    unavailable = []
    for label, cheapest, allowed in (
        ("Fastest", False, None),
        ("Lowest line-haul", True, None),
        ("Land only", False, {"road", "trail", "track"}),
        ("Water only", False, {"sea", "river", "barge", "ferry"}),
    ):
        def weight(edge):
            if not include_inferred and edge.inferred:
                return math.inf
            if not allow_special and set(edge.modes) & {"air", "teleport"}:
                return math.inf
            if allowed is not None and not set(edge.modes) <= allowed:
                return math.inf
            return freight(edge) if cheapest else edge.days

        route = direct_path(world, start.id, end.id, weight)
        if route is None:
            unavailable.append(label)
            continue
        identity = tuple((edge.src, edge.dst, edge.kind, edge.name, edge.distance, edge.quality)
                         for edge in route)
        if identity in options:
            options[identity]["labels"].append(label)
            continue
        legs = [shipment_leg(world, edge, pounds, risk(edge), minimum, carrier_choices) for edge in route]
        days = sum(leg["travel_days"] for leg in legs)
        costs = {"line_haul_gp": sum(leg["line_haul_gp"] for leg in legs),
                 "minimum_topup_gp": sum(leg["minimum_topup_gp"] for leg in legs),
                 "handling_gp": handling * (len(route) - 1), "daily_gp": daily * days,
                 "fixed_gp": fixed}
        subtotal = sum(costs.values())
        costs.update(subtotal_gp=subtotal, contingency_gp=subtotal * contingency / 100,
                     total_gp=subtotal * (1 + contingency / 100))
        purchase = None if purchase_per_lb is None else pounds * purchase_per_lb
        landed = None if purchase is None else purchase + costs["total_gp"]
        costs.update(purchase_value_gp=purchase, landed_total_gp=landed,
                 landed_gp_per_lb=None if landed is None else landed / pounds)
        options[identity] = {"id": ".".join(leg["id"] for leg in legs),
                     "labels": [label], "legs": legs, "connections": len(route) - 1,
                             "travel_days": days, "distance_miles": sum(edge.distance for edge in route),
                             "path": [start.name] + [leg["destination"] for leg in legs],
                             "uses_inferred": any(edge.inferred for edge in route), "costs": costs}
    known_legs = {leg["id"] for option in options.values() for leg in option["legs"]}
    if not set(carrier_choices) <= known_legs:
        raise ValueError("Carrier choices refer to routes no longer available")
    return {"origin": start.name, "destination": end.name, "pounds": pounds,
            "date": str(world.date), "include_events": include_events,
            "assumptions": {**values, "purchase_per_lb": purchase_per_lb,
                            "include_inferred": include_inferred, "allow_special": allow_special,
                            "carrier_choices": carrier_choices},
            "profile_inferred": "surveyed_market" in start.traits or "surveyed_market" in end.traits,
            "options": sorted(options.values(), key=lambda row: (row["travel_days"], row["costs"]["total_gp"])),
            "unavailable": unavailable}