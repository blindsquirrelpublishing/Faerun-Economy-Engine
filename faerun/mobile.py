"""Dated mobile communities that travel between established markets."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .calendar import HarptosDate
from .models import slugify


@dataclass(frozen=True)
class ItineraryEntry:
    start: HarptosDate
    end: HarptosDate
    kind: str
    origin: str
    destination: Optional[str] = None
    route: str = ""
    camp: str = ""

    def __post_init__(self) -> None:
        if self.kind not in {"camp", "travel"}:
            raise ValueError("Itinerary kind must be 'camp' or 'travel'")
        if self.end.absolute_day() < self.start.absolute_day():
            raise ValueError("Itinerary entries cannot end before they start")
        if self.kind == "travel" and not self.destination:
            raise ValueError("Travel itinerary entries require a destination")

    def contains(self, date: HarptosDate) -> bool:
        day = date.absolute_day()
        return self.start.absolute_day() <= day <= self.end.absolute_day()


@dataclass(frozen=True)
class MobileLocation:
    id: str
    name: str
    description: str
    population: int
    households: int
    wealth: float
    security: float
    traits: Sequence[str]
    industries: Dict[str, float]
    specialties: Sequence[str]
    wagons: Dict[str, int]
    animals: Dict[str, int]
    roles: Dict[str, int]
    inventory: Dict[str, float]
    services: Sequence[str]
    itinerary: Sequence[ItineraryEntry] = field(default_factory=tuple)
    miles_per_day: float = 16.0
    travel_days_per_tenday: int = 6

    def __post_init__(self) -> None:
        if slugify(self.id) != self.id:
            raise ValueError("Mobile location IDs must be normalized slugs")
        if self.population <= 0 or self.households <= 0:
            raise ValueError("Mobile locations require people and households")
        if self.miles_per_day <= 0:
            raise ValueError("Travel speed must be positive")
        ordered = sorted(self.itinerary, key=lambda row: row.start.absolute_day())
        for previous, current in zip(ordered, ordered[1:]):
            if current.start.absolute_day() <= previous.end.absolute_day():
                raise ValueError("Mobile itinerary entries cannot overlap")

    def position(self, world: Any, date: Optional[HarptosDate] = None) -> Dict[str, Any]:
        current = date or world.date
        entries = sorted(self.itinerary, key=lambda row: row.start.absolute_day())
        active = next((row for row in entries if row.contains(current)), None)
        if active is None:
            if not entries:
                raise ValueError(f"{self.name} has no itinerary")
            previous = [
                row for row in entries
                if row.end.absolute_day() < current.absolute_day()
            ]
            active = previous[-1] if previous else entries[0]

        origin = world.find_settlement(active.origin)
        destination = (
            world.find_settlement(active.destination)
            if active.destination else None
        )
        if active.kind == "camp" or destination is None:
            progress = 0.0
            x, y = origin.x, origin.y
            status = "encamped"
            host = origin
        else:
            first = active.start.absolute_day()
            span = max(1, active.end.absolute_day() - first)
            progress = min(1.0, max(0.0, (current.absolute_day() - first) / span))
            x = origin.x + (destination.x - origin.x) * progress
            y = origin.y + (destination.y - origin.y) * progress
            status = "travelling"
            host = None

        return {
            "status": status,
            "x": round(x, 3),
            "y": round(y, 3),
            "origin": {"id": origin.id, "name": origin.name},
            "destination": (
                {"id": destination.id, "name": destination.name}
                if destination else None
            ),
            "host": (
                {"id": host.id, "name": host.name}
                if host else None
            ),
            "route": active.route,
            "camp": active.camp,
            "progress": round(progress, 4),
            "start": str(active.start),
            "end": str(active.end),
        }

    def profile(self, world: Any, date: Optional[HarptosDate] = None) -> Dict[str, Any]:
        current = date or world.date
        position = self.position(world, current)
        horses = sum(
            count for animal, count in self.animals.items()
            if "horse" in animal
        )
        people_water = self.population * 5.283
        essential_water = self.population * 1.321
        animal_water = horses * 6.5
        food_low = self.population * 2.0
        food_high = self.population * 2.5
        fodder_low = horses * 12.0
        fodder_high = horses * 15.0
        entries: List[Dict[str, Any]] = []
        for row in self.itinerary:
            item = asdict(row)
            item["start"] = str(row.start)
            item["end"] = str(row.end)
            item["active"] = row.contains(current)
            entries.append(item)
        return {
            "id": self.id,
            "name": self.name,
            "kind": "mobile_location",
            "description": self.description,
            "date": str(current),
            "population": self.population,
            "households": self.households,
            "wealth": self.wealth,
            "security": self.security,
            "traits": list(self.traits),
            "industries": dict(self.industries),
            "specialties": list(self.specialties),
            "wagons": dict(self.wagons),
            "animals": dict(self.animals),
            "roles": dict(self.roles),
            "inventory": dict(self.inventory),
            "services": list(self.services),
            "travel": {
                "miles_per_day": self.miles_per_day,
                "travel_days_per_tenday": self.travel_days_per_tenday,
            },
            "requirements": {
                "food_lb_per_day": {
                    "low": round(food_low, 1),
                    "high": round(food_high, 1),
                },
                "essential_water_gallons_per_day": round(essential_water, 1),
                "domestic_water_gallons_per_day": round(people_water, 1),
                "animal_water_gallons_per_day": round(animal_water, 1),
                "total_water_gallons_per_day": round(people_water + animal_water, 1),
                "fodder_lb_per_day": {
                    "low": round(fodder_low, 1),
                    "high": round(fodder_high, 1),
                },
                "fuel_lb_per_day": {"low": 150.0, "high": 250.0},
            },
            "position": position,
            "itinerary": entries,
            "market_access": {
                "mode": "host_market" if position["host"] else "carried_inventory",
                "host": position["host"],
                "notes": (
                    "The company uses the host settlement's prices while encamped. "
                    "While travelling it can consume or sell only carried inventory."
                ),
            },
        }


def mobile_location_summary(location: MobileLocation, world: Any) -> Dict[str, Any]:
    position = location.position(world)
    return {
        "id": location.id,
        "name": location.name,
        "kind": "mobile_location",
        "population": location.population,
        "households": location.households,
        "status": position["status"],
        "position": position,
        "traits": list(location.traits),
    }
