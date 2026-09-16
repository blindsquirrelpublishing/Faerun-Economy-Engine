"""World events: wars, blockades, blights, festivals and gold rushes.

Events are layered on top of the static world and distort supply, demand,
price and travel risk.  A DM can apply a template to any settlement, zone or
region, or build a bespoke event.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from .models import Event, slugify
from .world import World, get_world

#: name -> (kind, supply, demand, price, risk, description)
EVENT_TEMPLATES: Dict[str, Dict] = {
    "siege": dict(kind="war", supply=0.35, demand=1.6, price=1.0, risk=0.9,
                  categories=["food", "arms", "drink"],
                  description="An army sits outside the walls; nothing gets in cheaply."),
    "war": dict(kind="war", supply=0.8, demand=1.8, price=1.0, risk=0.5,
                categories=["arms", "food", "livestock"],
                description="Open warfare: weapons, rations and horses are bought at any price."),
    "blockade": dict(kind="war", supply=0.4, demand=1.2, price=1.0, risk=0.7,
                     description="A naval blockade strangles the harbour."),
    "drought": dict(kind="blight", supply=0.35, demand=1.15, price=1.0, risk=0.0,
                    categories=["food", "livestock"],
                    description="The rains failed; the harvest with them."),
    "blight": dict(kind="blight", supply=0.25, demand=1.1, price=1.0, risk=0.0,
                   categories=["food"],
                   description="Crop blight ruins the granaries."),
    "famine": dict(kind="blight", supply=0.2, demand=1.75, price=1.15, risk=0.35,
                   categories=["food", "livestock", "drink"],
                   description="Famine. The granaries are empty and bread is "
                               "sold at whatever the desperate will pay."),
    "hard_winter": dict(kind="weather", supply=0.55, demand=1.45, price=1.0, risk=0.5,
                        categories=["food", "material", "textile", "drink"],
                        description="A savage winter: the passes shut, and fuel "
                                    "and warm cloth are worth their weight."),
    "flood": dict(kind="disaster", supply=0.45, demand=1.3, price=1.0, risk=0.45,
                  categories=["food", "livestock"],
                  description="The river broke its banks and took the "
                              "low fields with it."),
    "monster": dict(kind="disaster", supply=0.75, demand=1.2, price=1.0, risk=1.0,
                    description="Something is hunting the outlying farms; "
                                "no one will travel alone."),
    "refugees": dict(kind="politics", supply=0.9, demand=1.55, price=1.0, risk=0.25,
                     categories=["food", "textile", "drink"],
                     description="Refugees crowd the gates: many more mouths, "
                                 "and little to feed them with."),
    "caravan_boom": dict(kind="boon", supply=1.45, demand=1.1, price=0.92, risk=0.0,
                         description="The roads are thick with caravans and "
                                     "the warehouses are full."),
    "plague": dict(kind="plague", supply=0.6, demand=1.3, price=1.0, risk=0.6,
                   description="Plague empties the workshops and closes the gates."),
    "bumper_harvest": dict(kind="boon", supply=1.9, demand=1.0, price=1.0, risk=0.0,
                           categories=["food"],
                           description="A golden harvest floods the markets."),
    "gold_rush": dict(kind="boon", supply=1.6, demand=1.4, price=1.0, risk=0.2,
                      categories=["metal", "gem"],
                      description="A new strike; ore floods out and everything else costs more."),
    "festival": dict(kind="festival", supply=1.0, demand=1.5, price=1.0, risk=0.0,
                     categories=["drink", "food", "luxury"],
                     description="A great festival: food, drink and finery in demand."),
    "bandits": dict(kind="banditry", supply=0.9, demand=1.0, price=1.0, risk=0.8,
                    description="Brigands work the roads; caravans demand danger money."),
    "pirates": dict(kind="banditry", supply=0.85, demand=1.0, price=1.0, risk=0.9,
                    description="Corsairs prowl the sea lanes."),
    "dragon": dict(kind="disaster", supply=0.5, demand=1.4, price=1.0, risk=1.2,
                   description="A dragon has claimed the region as its hunting ground."),
    "boom": dict(kind="boon", supply=1.2, demand=1.5, price=1.0, risk=0.0,
                 description="A building boom: labour, timber and iron are eaten up."),
    "trade_embargo": dict(kind="politics", supply=0.7, demand=1.0, price=1.25, risk=0.3,
                          description="Rival powers have closed their markets."),
    "magical_surge": dict(kind="arcane", supply=1.4, demand=1.7, price=1.0, risk=0.1,
                          categories=["arcane", "gem", "exotic"],
                          description="A surge in the Weave: reagents both flow and vanish."),
}


def make_event(
    template: Optional[str] = None,
    name: Optional[str] = None,
    settlements: Optional[Sequence[str]] = None,
    zones: Optional[Sequence[str]] = None,
    regions: Optional[Sequence[str]] = None,
    commodities: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
    supply: Optional[float] = None,
    demand: Optional[float] = None,
    price: Optional[float] = None,
    risk: Optional[float] = None,
    duration_months: Optional[int] = None,
    start_month: Optional[int] = None,
    description: Optional[str] = None,
    world: Optional[World] = None,
    event_id: Optional[str] = None,
) -> Event:
    """Build (but do not register) an event, optionally from a template."""
    world = world or get_world()
    base: Dict = dict(EVENT_TEMPLATES.get(template or "", {}))
    label = name or (template.replace("_", " ").title() if template else "Event")
    resolved_settlements: List[str] = []
    for key in settlements or []:
        found = world.lookup_settlement(key)
        resolved_settlements.append(found.id if found else slugify(key))
    resolved_commodities: List[str] = []
    for key in commodities or []:
        found = world.lookup_commodity(key)
        resolved_commodities.append(found.id if found else slugify(key))

    where = resolved_settlements or list(zones or []) or list(regions or []) or ["Faerûn"]
    return Event(
        id=event_id or slugify(f"{label}-{where[0]}"),
        name=label,
        kind=base.get("kind", "generic"),
        settlements=resolved_settlements,
        zones=list(zones or []),
        regions=list(regions or []),
        commodities=resolved_commodities,
        categories=list(categories or base.get("categories", [])),
        supply=float(supply if supply is not None else base.get("supply", 1.0)),
        demand=float(demand if demand is not None else base.get("demand", 1.0)),
        price=float(price if price is not None else base.get("price", 1.0)),
        risk=float(risk if risk is not None else base.get("risk", 0.0)),
        start_month=start_month,
        duration_months=duration_months,
        description=description or base.get("description", ""),
    )


def apply_event(world: Optional[World] = None, **kwargs) -> Event:
    """Build an event and register it with the world."""
    world = world or get_world()
    event = make_event(world=world, **kwargs)
    return world.add_event(event)
