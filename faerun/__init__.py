"""Faerûn Economy Engine.

A simulation of commodity and product prices across the towns and cities of
Faerûn, driven by local supply, demand, trade-route distance, tariffs,
seasonality and world events.
"""

from .calendar import HarptosDate
from .economy import (
    compare_prices,
    find_arbitrage,
    market_report,
    price_for,
    price_history,
    trade_summary,
)
from .events import EVENT_TEMPLATES, apply_event, make_event
from .living import (
    LIVING_STANDARDS,
    daily_requirement,
    living_standard,
    per_person_daily_requirements,
    settlement_daily_requirements,
    settlement_per_person_daily_requirements,
)
from .world import World, get_world
from .mobile import ItineraryEntry, MobileLocation

# Imported last: both of these reach back into `world`, so they must land after
# it or the package would import itself in a circle.
from .chronicle import (  # noqa: E402
    chronicle_summary,
    chronicle_window,
    clear_chronicle,
    install_chronicle,
    settlement_timeline,
)
from .location import location_detail, location_timeline  # noqa: E402
from .materials import economic_report, location_requirements  # noqa: E402
from .mobile_economy import mobile_economic_report  # noqa: E402

__version__ = "0.1.0"

__all__ = [
    "World",
    "MobileLocation",
    "ItineraryEntry",
    "get_world",
    "price_for",
    "market_report",
    "compare_prices",
    "find_arbitrage",
    "price_history",
    "trade_summary",
    "LIVING_STANDARDS",
    "daily_requirement",
    "living_standard",
    "per_person_daily_requirements",
    "settlement_daily_requirements",
    "settlement_per_person_daily_requirements",
    "apply_event",
    "make_event",
    "EVENT_TEMPLATES",
    "HarptosDate",
    "chronicle_summary",
    "chronicle_window",
    "clear_chronicle",
    "install_chronicle",
    "settlement_timeline",
    "location_detail",
    "location_requirements",
    "economic_report",
    "mobile_economic_report",
    "location_timeline",
    "__version__",
]
