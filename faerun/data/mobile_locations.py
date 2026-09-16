"""Authored travelling communities."""

from ..calendar import HarptosDate
from ..mobile import ItineraryEntry, MobileLocation


MOBILE_LOCATIONS = [
    MobileLocation(
        id="silver_wheel",
        name="Silver Wheel Company",
        description=(
            "An extended household caravan of traders, repairers, animal handlers, "
            "messengers and performers travelling the roads of the Sword Coast."
        ),
        population=55,
        households=11,
        wealth=0.90,
        security=0.65,
        traits=(
            "mobile", "mercantile", "craft", "performance", "animal",
            "multilingual",
        ),
        industries={
            "trade": 2, "craft": 2, "animal": 2, "textile": 1,
            "performance": 3, "repair": 2, "herb": 1,
        },
        specialties=(
            "tool and wagon repair", "horse care", "small-lot trade",
            "music and storytelling", "letters and parcels",
        ),
        wagons={"living": 12, "freight": 4},
        animals={"draft_horses": 28, "riding_horses": 9, "remount_horses": 6, "dogs": 4},
        roles={
            "craft_and_trade": 18,
            "drivers_handlers_scouts": 8,
            "performers": 6,
            "guards_hunters": 5,
            "healers_midwives": 3,
            "scribes_interpreters": 2,
            "children_elders_dependents": 13,
        },
        inventory={
            "preserved_food_lb": 1400,
            "fodder_lb": 4200,
            "fresh_water_gallons": 900,
            "firewood_lb": 700,
            "cloth_bolts": 18,
            "small_tools": 45,
            "harness_sets": 8,
            "herb_cases": 6,
            "lamp_oil_flasks": 80,
            "trade_cargo_lb": 5200,
        },
        services=(
            "animal care and training",
            "communications and small parcels",
            "repair and reclamation",
            "culture and entertainment",
            "herbal care and midwifery",
            "translation, appraisal and bookkeeping",
        ),
        itinerary=(
            ItineraryEntry(
                HarptosDate(1492, 8, 20), HarptosDate(1492, 8, 30),
                "camp", "daggerford", camp="North caravan field",
            ),
            ItineraryEntry(
                HarptosDate(1492, 9, 1), HarptosDate(1492, 9, 10),
                "travel", "daggerford", "waterdeep", route="The Trade Way",
            ),
            ItineraryEntry(
                HarptosDate(1492, 9, 11), HarptosDate(1492, 9, 16),
                "camp", "waterdeep", camp="South Ward caravan field",
            ),
            ItineraryEntry(
                HarptosDate(1492, 9, 17), HarptosDate(1492, 9, 20),
                "travel", "waterdeep", "amphail", route="The Long Road",
            ),
            ItineraryEntry(
                HarptosDate(1492, 9, 21), HarptosDate(1492, 9, 30),
                "camp", "amphail", camp="Autumn horse-fair ground",
            ),
            ItineraryEntry(
                HarptosDate(1492, 10, 1), HarptosDate(1492, 10, 8),
                "travel", "amphail", "red_larch", route="The Long Road",
            ),
            ItineraryEntry(
                HarptosDate(1492, 10, 9), HarptosDate(1492, 10, 20),
                "camp", "red_larch", camp="Common pasture beside the Long Road",
            ),
            ItineraryEntry(
                HarptosDate(1492, 10, 21), HarptosDate(1492, 10, 30),
                "travel", "red_larch", "triboar", route="The Long Road",
            ),
            ItineraryEntry(
                HarptosDate(1492, 11, 1), HarptosDate(1492, 11, 20),
                "camp", "triboar", camp="Winter caravan paddock",
            ),
        ),
    ),
]
