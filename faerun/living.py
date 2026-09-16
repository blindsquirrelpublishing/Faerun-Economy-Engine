"""Per-person necessities that anchor settlement demand."""

from __future__ import annotations

from typing import Dict, Mapping, Optional, Tuple

from .models import Settlement
from .world import World, get_world


# Quantities are per person per day in each commodity's catalogue unit.
# The profiles represent material consumption, not household expenditure.
LIVING_STANDARDS: Mapping[str, Mapping[str, float]] = {
    "poor": {
        "grain": 0.016,
        "vegetables": 0.004,
        "fruit": 0.001,
        "cheese": 0.001,
        "eggs": 0.001,
        "meat_fresh": 0.0015,
        "salt": 0.0002,
        "ale": 0.005,
        "clothing_common": 0.002,
        "charcoal": 0.016,
        "soap": 0.0004,
        "candles": 0.0002,
        "lamp_oil": 0.002,
        "pottery": 0.00015,
    },
    "common": {
        "grain": 0.020,
        "vegetables": 0.008,
        "fruit": 0.004,
        "cheese": 0.003,
        "eggs": 0.003,
        "meat_fresh": 0.005,
        "salt": 0.0003,
        "ale": 0.010,
        "clothing_common": 0.004,
        "charcoal": 0.025,
        "soap": 0.001,
        "candles": 0.0006,
        "lamp_oil": 0.006,
        "pottery": 0.0004,
    },
    "rich": {
        "grain": 0.024,
        "vegetables": 0.014,
        "fruit": 0.010,
        "cheese": 0.007,
        "eggs": 0.007,
        "meat_fresh": 0.014,
        "salt": 0.0005,
        "ale": 0.018,
        "clothing_common": 0.009,
        "charcoal": 0.045,
        "soap": 0.0025,
        "candles": 0.002,
        "lamp_oil": 0.018,
        "pottery": 0.001,
    },
}

WEALTH_ANCHORS: Tuple[Tuple[float, str], ...] = (
    (0.65, "poor"),
    (1.00, "common"),
    (1.40, "rich"),
)

FLOUR_GRAIN_EQUIVALENT = 0.9
BREAD_GRAIN_EQUIVALENT = FLOUR_GRAIN_EQUIVALENT * 0.02


def living_standard(wealth: float) -> str:
    """Return the nearest named standard for display and reporting."""
    return min(WEALTH_ANCHORS, key=lambda item: abs(item[0] - wealth))[1]


def per_person_daily_requirements(wealth: float) -> Dict[str, float]:
    """Interpolate daily necessities between the surrounding wealth profiles."""
    if wealth <= WEALTH_ANCHORS[0][0]:
        return dict(LIVING_STANDARDS["poor"])
    if wealth >= WEALTH_ANCHORS[-1][0]:
        return dict(LIVING_STANDARDS["rich"])

    for (low_wealth, low_name), (high_wealth, high_name) in zip(
        WEALTH_ANCHORS, WEALTH_ANCHORS[1:]
    ):
        if low_wealth <= wealth <= high_wealth:
            share = (wealth - low_wealth) / (high_wealth - low_wealth)
            low = LIVING_STANDARDS[low_name]
            high = LIVING_STANDARDS[high_name]
            return {
                commodity_id: low[commodity_id] + (
                    high[commodity_id] - low[commodity_id]
                ) * share
                for commodity_id in low
            }
    raise ValueError(f"could not resolve living standard for wealth {wealth}")


def settlement_per_person_daily_requirements(market: Settlement) -> Dict[str, float]:
    """Allocate staple nutrition according to local processing access."""
    requirements = per_person_daily_requirements(market.wealth)
    staple = requirements.pop("grain")
    craft = market.industry_level("craft")
    trade = market.industry_level("trade")
    bread_share = min(0.65, 0.20 + craft * 0.10 + trade * 0.05)
    flour_share = min(0.20, 0.10 + craft * 0.03)
    grain_share = 1.0 - bread_share - flour_share
    requirements.update({
        "grain": staple * grain_share,
        "flour": staple * flour_share / FLOUR_GRAIN_EQUIVALENT,
        "bread": staple * bread_share / BREAD_GRAIN_EQUIVALENT,
    })
    return requirements


def daily_requirement(commodity_id: str, wealth: float,
                      settlement: Optional[Settlement] = None) -> Optional[float]:
    """Return one person's baseline daily quantity, or None for non-necessities."""
    if settlement is not None:
        return settlement_per_person_daily_requirements(settlement).get(commodity_id)
    return per_person_daily_requirements(wealth).get(commodity_id)


def settlement_daily_requirements(settlement, world: Optional[World] = None) -> Dict:
    """Report the baseline quantities required each day by a settlement's souls."""
    world = world or get_world()
    market = world.find_settlement(settlement)
    if world.config.expanded_requirements:
        from .requirements import final_requirements

        sectors = final_requirements(market, world.commodities.values(),
                                     include_services=world.config.service_economy)
        return {
            "settlement": market.name, "population": market.population,
            "wealth": market.wealth, "living_standard": living_standard(market.wealth),
            "requirements": [
                {"commodity_id": cid, "commodity": world.commodities[cid].name,
                 "category": world.commodities[cid].category, "unit": world.commodities[cid].unit,
                 "per_person_per_day": sum(parts.values()) / market.population if market.population else 0.0,
                 "settlement_per_day": sum(parts.values()), "sectors": parts}
                for cid, parts in sectors.items()
            ],
        }
    per_person = settlement_per_person_daily_requirements(market)
    requirements = []
    for commodity_id, quantity in per_person.items():
        commodity = world.find_commodity(commodity_id)
        requirements.append({
            "commodity_id": commodity.id,
            "commodity": commodity.name,
            "category": commodity.category,
            "unit": commodity.unit,
            "per_person_per_day": round(quantity, 6),
            "settlement_per_day": round(quantity * market.population, 3),
        })
    return {
        "settlement": market.name,
        "population": market.population,
        "wealth": market.wealth,
        "living_standard": living_standard(market.wealth),
        "requirements": requirements,
    }