"""Domestic visitor-days, admission limits, and destination food requirements."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Dict

from .requirements import FOOD_COMMODITIES, final_requirements
from .world import World


@dataclass(frozen=True)
class VisitorSegment:
    id: str
    name: str
    trips_per_resident_year: float
    nights: float
    wealth_multiplier: float


VISITOR_SEGMENTS = (
    VisitorSegment("leisure", "Leisure and sightseeing", .18, 3, 1.25),
    VisitorSegment("pilgrimage", "Pilgrimage", .08, 4, .90),
    VisitorSegment("scholarly", "Scholarly and cultural visits", .03, 7, 1.15),
    VisitorSegment("festival", "Festivals and events", .12, 2, 1.10),
    VisitorSegment("adventure", "Expeditions and adventure", .025, 6, 1.30),
    VisitorSegment("business", "Business and trade visits", .25, 2, 1.20),
)
DAYS_PER_MONTH = 30.0
DAYS_PER_YEAR = 365.0
DAY_VISIT_FOOD_SHARE = .35
MAX_AWAY_SHARE = .10


def _attraction(world: World, s, segment: VisitorSegment) -> float:
    trait = s.has_trait
    trade = min(3.0, s.industry_level("trade"))
    affinities = {
        "leisure": .5 + trait("cosmopolitan") + .5 * trait("noble") + .5 * s.is_port,
        "pilgrimage": .15 + 3 * trait("temple") + .4 * s.industry_level("temple"),
        "scholarly": .10 + 3 * trait("academic") + .4 * s.industry_level("arcane"),
        "festival": .5 + trait("cosmopolitan") + trait("temple") + .2 * trade,
        "adventure": .3 + 2 * trait("frontier") + (s.terrain in {"jungle", "mountains", "forest"}),
        "business": .5 + 2 * trait("mercantile") + trade + s.is_port,
    }
    season = {"winter": .60, "spring": 1.0, "summer": 1.35, "autumn": 1.05}[world.date.season]
    if s.has_trait("cold") and world.date.season == "winter":
        season *= .6
    if segment.id == "festival":
        season *= 1.8 if world.date.festival else .6
    risk = sum(max(0.0, event.risk) for event in world.events_for(s))
    safety = max(.02, min(1.0, s.security)) ** 1.5 / (1 + 3 * risk)
    scale = (max(1, s.population) / 1000) ** .35
    return affinities[segment.id] * scale * safety * season


def plan_visitors(world: World, beds: Dict[str, float]) -> Dict:
    """Assign domestic trips, then ration overnight stays across fixed beds."""
    scale = world.config.visitor_scale
    horizon = world.config.visitor_max_days
    if not math.isfinite(scale) or scale < 0:
        raise ValueError("Visitor scale must be finite and non-negative")
    if not math.isfinite(horizon) or horizon <= 0:
        raise ValueError("Visitor travel horizon must be finite and positive")
    if any(not math.isfinite(value) or value < 0 for value in beds.values()):
        raise ValueError("Visitor beds must be finite and non-negative")
    enabled = bool(world.config.expanded_requirements and world.config.service_economy
                   and world.config.visitor_economy)
    places = {
        sid: {
            "enabled": enabled, "beds": beds.get(sid, 0.0), "arrivals_per_month": 0.0,
            "overnight_visitors_per_day": 0.0, "day_visitors_per_day": 0.0,
            "visitors_per_day": 0.0, "visitor_food_equivalents": 0.0,
            "desired_overnight_visitors_per_day": 0.0,
            "unaccommodated_visitors_per_day": 0.0,
            "outbound_visitors_per_day": 0.0, "outbound_food_equivalents": 0.0,
            "resident_presence": float(s.population), "occupancy": None,
            "resident_population": s.population,
            "residents_at_home": float(s.population),
            "modeled_present_population": float(s.population),
            "external_visitors_per_day": None,
            "visitor_goods": {}, "home_food_reduction": {},
        } for sid, s in world.settlements.items()
    }
    if not enabled or not scale:
        return {"places": places, "flows": [], "assumptions": visitor_assumptions()}
    for s in world.settlements.values():
        if (not all(math.isfinite(value) for value in (s.population, s.wealth, s.security))
                or s.population < 0 or s.wealth < 0):
            raise ValueError(f"Invalid visitor population, wealth or security for {s.name}")
        if any(not math.isfinite(event.risk) for event in world.events_for(s)):
            raise ValueError(f"Non-finite visitor event risk for {s.name}")
    attractions = {(sid, segment.id): _attraction(world, s, segment)
                   for sid, s in world.settlements.items() for segment in VISITOR_SEGMENTS}
    if any(not math.isfinite(value) or value < 0 for value in attractions.values()):
        raise ValueError("Visitor destination attractiveness must be finite and non-negative")
    weights = {id(edge): edge.days * (1 + world.edge_risk(edge))
               for edges in world._edges.values() for edge in edges}
    if any(not math.isfinite(value) or value < 0 for value in weights.values()):
        raise ValueError("Visitor route weights must be finite and non-negative")
    flows = []
    for origin_id, origin in sorted(world.settlements.items()):
        if origin.population <= 0:
            continue
        distances, _ = world._dijkstra(origin_id, lambda edge: weights[id(edge)])
        reachable = [(sid, days) for sid, days in distances.items()
                     if sid != origin_id and 0 <= days <= horizon
                     and world.settlements[sid].population > 0]
        origin_flows = []
        for segment in VISITOR_SEGMENTS:
            annual = origin.population * segment.trips_per_resident_year * scale * max(.1, origin.wealth) ** 1.1
            annual *= {"winter": .60, "spring": 1.0, "summer": 1.35, "autumn": 1.05}[world.date.season]
            if segment.id == "festival":
                annual *= 1.8 if world.date.festival else .6
            for overnight, fraction in ((True, .8), (False, .2)):
                choices = [
                    (sid, days, attractions[sid, segment.id] / (1 + days) ** 1.5)
                    for sid, days in reachable if overnight or days <= .5
                ]
                choices.sort(key=lambda row: (-row[2], row[0]))
                choices = choices[:8 if overnight else 3]
                total = sum(weight for _, _, weight in choices)
                if not total:
                    continue
                nights = segment.nights if overnight else 0.0
                for destination_id, days, weight in choices:
                    arrivals = annual / DAYS_PER_YEAR * fraction * weight / total
                    presence = arrivals * (nights if overnight else 1.0)
                    origin_flows.append({
                        "origin_id": origin_id, "destination_id": destination_id,
                        "segment_id": segment.id, "segment": segment.name,
                        "overnight": overnight, "average_nights": nights,
                        "desired_visitors_per_day": presence,
                        "visitors_per_day": presence, "risk_adjusted_days": days,
                        "basket_wealth": max(.45, min(2.0, origin.wealth * segment.wealth_multiplier)),
                    })
        total_away = sum(flow["visitors_per_day"] for flow in origin_flows)
        cap = min(1.0, origin.population * MAX_AWAY_SHARE / total_away) if total_away else 1.0
        for flow in origin_flows:
            flow["visitors_per_day"] *= cap
            flow["desired_visitors_per_day"] *= cap
            if flow["overnight"]:
                places[flow["destination_id"]]["desired_overnight_visitors_per_day"] += flow["visitors_per_day"]
        flows.extend(origin_flows)

    for sid, place in places.items():
        desired = place["desired_overnight_visitors_per_day"]
        place["unaccommodated_visitors_per_day"] = max(0.0, desired - place["beds"])
    basket_cache = {}
    home_cache = {}
    admitted = []
    for flow in flows:
        origin_id, destination_id = flow["origin_id"], flow["destination_id"]
        origin, destination = places[origin_id], places[destination_id]
        if flow["overnight"]:
            desired = destination["desired_overnight_visitors_per_day"]
            flow["visitors_per_day"] *= min(1.0, destination["beds"] / desired) if desired else 0.0
        visitors = flow["visitors_per_day"]
        if visitors <= 0:
            continue
        equivalents = visitors * (1.0 if flow["overnight"] else DAY_VISIT_FOOD_SHARE)
        flow["food_equivalents"] = equivalents
        flow["arrivals_per_month"] = visitors / (flow["average_nights"] or 1.0) * DAYS_PER_MONTH
        destination["arrivals_per_month"] += flow["arrivals_per_month"]
        destination["overnight_visitors_per_day" if flow["overnight"] else "day_visitors_per_day"] += visitors
        destination["visitors_per_day"] += visitors
        destination["visitor_food_equivalents"] += equivalents
        origin["outbound_visitors_per_day"] += visitors
        origin["outbound_food_equivalents"] += equivalents
        basket_key = (origin_id, flow["basket_wealth"])
        if basket_key not in basket_cache:
            sample = replace(world.settlements[origin_id], population=1000, wealth=flow["basket_wealth"])
            requirements = final_requirements(sample, world.commodities.values(), include_services=False)
            basket_cache[basket_key] = {
                cid: parts.get("household", 0.0) / 1000 for cid, parts in requirements.items()
                if cid in FOOD_COMMODITIES
            }
        flow["goods_demand"] = {}
        for cid, amount in basket_cache[basket_key].items():
            quantity = amount * equivalents
            flow["goods_demand"][cid] = quantity
            destination["visitor_goods"][cid] = destination["visitor_goods"].get(cid, 0.0) + quantity
        admitted.append(flow)
    for sid, place in places.items():
        s = world.settlements[sid]
        place["occupancy"] = place["overnight_visitors_per_day"] / place["beds"] if place["beds"] else None
        place["resident_presence"] = s.population - place["outbound_food_equivalents"]
        place["residents_at_home"] = s.population - place["outbound_visitors_per_day"]
        place["modeled_present_population"] = (
            place["residents_at_home"] + place["visitors_per_day"]
        )
        if s.population:
            home_cache[sid] = final_requirements(s, world.commodities.values(), include_services=False)
            place["home_food_reduction"] = {
                cid: parts.get("household", 0.0) * place["outbound_food_equivalents"] / s.population
                for cid, parts in home_cache[sid].items() if cid in FOOD_COMMODITIES
            }
    return {"places": places, "flows": admitted, "assumptions": visitor_assumptions()}


def visitor_assumptions() -> list[str]:
    return [
        "Domestic visitors only: every admitted visitor has a modeled origin. No external gold or people are invented.",
        "Annual trips/resident by segment: leisure .18, pilgrimage .08, scholarly .03, festival .12, adventure .025, business .25; scaled by origin wealth^1.1 and visitor_scale.",
        "Nights/stay by segment: leisure 3, pilgrimage 4, scholarly 7, festival 2, adventure 6, business 2. Monthly arrivals use 30-day Harptos months; annual rates use 365 days.",
        "80% of potential trips are overnight; 20% are day trips limited to .5 risk-adjusted travel days. Each segment considers the best eight overnight or three day destinations, not all possible itineraries.",
        "Routes must be reachable within visitor_max_days. Affinity, city size^0.35, security, event risk, season, and Harptos festival months shape destinations.",
        "At most 10% of an origin's population can be visiting other markets. Overnight stays share fixed lodging beds proportionally; rejected stays remain at home.",
        "A day trip uses .35 of a normal food-day. Origin variable household food is reduced by the admitted food-day equivalent; permanent housing, clothes and other fixed resident needs are not removed.",
        "Resident presence is a food-demand equivalent, not a headcount. Modeled present population = residents - outbound visitors + inbound visitors; this is a steady-state presence estimate, not a point-in-time census.",
        "Visitor food preferences follow origin wealth with segment multipliers; rich guests can demand exotic foods in a poor destination. Lodging, care and other service inputs are additional resource pressure.",
        "Arrival, bed occupancy and trip rates are steady-state estimates, not scheduled travelers; travel-time population, fares, budgets, credit and external visitors are not simulated.",
    ]
