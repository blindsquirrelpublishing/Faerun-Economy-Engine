"""Sourced climate descriptions for location details.

These are descriptive notes, kept separate from the model's coarse climate class
(`faerun.seasonality.climate_for`), which alone drives production calendars.
"""

VILHON_REACH = {
    "label": "Warm, humid, subtropical",
    "summary": (
        "The weather of the Vilhon Reach is subtropical and humid. Summers are very hot; "
        "winters are mild and rainy, and snow is rare."
    ),
    "seasons": [
        {
            "season": "spring",
            "onset": "Arrives in early Mirtul, heralded by the opening of the mierngras blossoms.",
            "conditions": "Days can reach 80°F / 27°C; evenings and early mornings rarely drop below 60°F / 16°C.",
        },
        {
            "season": "summer",
            "onset": "Begins when the druids' Long Night festival ends in early Eleasis.",
            "conditions": "High humidity, with heat reaching 110°F / 43°C.",
        },
        {
            "season": "autumn",
            "onset": "Approaches in late Marpenoth; crops are harvested and stored, and winter crops are planted in late Uktar.",
            "conditions": "Cooler, with daytime highs ranging from 80°F down to 50°F / 27-10°C.",
        },
        {
            "season": "winter",
            "onset": "",
            "conditions": "Heavy rain; usual highs of 50-65°F / 10-18°C. Cold spells can reach 35°F / 2°C; snow is rare.",
        },
    ],
    "scope_note": "These are regional figures for the Vilhon Reach, not readings specific to this settlement.",
    "calendar_note": (
        "The source dates the seasons by Reach festivals and crop work; the highlighted season "
        "follows the engine's Harptos calendar, which only approximates that timing."
    ),
    "sources": [{
        "title": "The Vilhon Reach (1996), Introduction: Climate, p. 4",
        "url": "https://housegriffon.com/RPG/Games/DnD/add2/ForgottenRealms/The%20Vilhon%20Reach.pdf",
        "accessed": "2026-10-14",
        "kind": "primary",
    }],
}

THE_NORTH_INLAND = {
    "label": "Cool, cloudy, subarctic inland North",
    "summary": (
        "The North describes the land from the Spine of the World to Waterdeep as subarctic: "
        "long, bitter winters, short humid summers, mixed rain, hail, sleet and snow, and skies "
        "that are almost always cloudy."
    ),
    "seasons": [
        {
            "season": "summer",
            "onset": "",
            "conditions": (
                "Short and warm, with highs up to 80°F / 27°C, high humidity and warm breezes from the "
                "southern seas. Rain is usual, but hail, sleet and snow are common. Unpredictable, "
                "even magical, \"wizard weather\" occurs near the High Forest."
            ),
        },
        {
            "season": "winter",
            "onset": "Long winters run from mid Marpenoth to late Tarsakh.",
            "conditions": (
                "Lows can reach -30°F / -34°C and highs rarely pass 40°F / 4°C. Storms off the western "
                "ocean drop heavy snow across the midlands, frequent blizzards leave drifts often 10 feet "
                "deep that isolate communities, and rivers freeze thick enough to carry wagons and draft "
                "teams between Uktar and early Ches."
            ),
        },
    ],
    "scope_note": (
        "These are regional figures for the inland North, from the Spine of the World to Waterdeep, "
        "not readings specific to this settlement. The source describes only summer and winter, so "
        "spring and autumn are not shown."
    ),
    "calendar_note": (
        "The source dates winter by Harptos months; the highlighted season follows the engine's "
        "calendar, which only approximates that timing."
    ),
    "sources": [{
        "title": "The North: Guide to the Savage Frontier (1996), Weather, p. 5",
        "url": "https://housegriffon.com/RPG/Games/DnD/add2/ForgottenRealms/The%20North%20-%20Guide%20to%20the%20Savage%20Frontier.pdf",
        "accessed": "2026-10-15",
        "kind": "primary",
    }],
}

THE_NORTH_COAST = {
    "label": "Temperate, ocean-warmed northern coast",
    "summary": (
        "The North describes a temperate coastal strip extending north to Port Llast, "
        "moderated by ocean currents; this is a regional historical description, "
        "not measured weather at the settlement."
    ),
    "seasons": [],
    "scope_note": (
        "The 1996 source describes the northern coastal strip as a whole, not this "
        "settlement. Its application here follows the settlement's documented coastal "
        "position; no city-specific temperatures or seasonal onsets were supplied."
    ),
    "calendar_note": "The source supplies no coastal seasonal calendar for this entry.",
    "sources": [{
        "title": "The North: Guide to the Savage Frontier (1996), Weather, p. 5",
        "url": "https://housegriffon.com/RPG/Games/DnD/add2/ForgottenRealms/The%20North%20-%20Guide%20to%20the%20Savage%20Frontier.pdf",
        "accessed": "2026-10-15",
        "kind": "primary",
    }],
}

# Engine zones whose settlements lie on the Vilhon Reach.
REGIONAL_CLIMATES = {
    "vilhon": VILHON_REACH,
    "turmish": VILHON_REACH,
}

# Local notes carry their basis so inference is never shown as sourced fact.
LOCAL_NOTES = {
    "amphail": [{"basis": "inference", "text": "The inland North weather band is a regional placement inference, not a village weather observation."}],
    "goldenfields": [{"basis": "inference", "text": "The inland North weather band is a regional placement inference, not an abbey weather observation."}],
    "griffon_s_nest": [{"basis": "inference", "text": "Applying the inland North band to the Surbrin Hills is geographic inference, not a hamlet observation."}],
    "red_larch": [{"basis": "inference", "text": "Applying the inland North band to the Dessarin Valley is geographic inference, not a village observation; the collected Red Larch research supplies no village-specific temperatures or seasonal measurements."}],
    "stone_bridge": [{"basis": "inference", "text": "The inland North band describes the bridge's area, not an inhabited settlement or measured bridge weather."}],
    "triboar": [{"basis": "inference", "text": "Applying the inland North band to inland Triboar is geographic inference, not a town observation."}],
    "yartar": [{"basis": "inference", "text": "Applying the inland North band to inland Yartar is geographic inference, not a city observation."}],
    "waterdeep": [{"basis": "inference", "text": "Waterdeep sits at the source's coastal/inland boundary; the coastal band is an interpretation, not a city measurement."}],
    "neverwinter": [{"basis": "sourced", "text": "The Neverwinter River warms the harbor and immediate area, but this does not establish city-wide temperatures (Forgotten Realms Wiki: Neverwinter; historical descriptions)."}],
    "secomber": [
        {
            "basis": "sourced",
            "text": (
                "The Singing Sprite, a stone inn, is described as cold and damp in winter and warmer "
                "and damp in summer (Volo's Guide to the Sword Coast, 1994, p. 83)."
            ),
        },
        {
            "basis": "inference",
            "text": (
                "The book does not place Secomber in a climate band. It lies inland, level with "
                "Waterdeep on the engine map, so the subarctic description is the closest fit; "
                "the model class for Secomber is temperate."
            ),
        },
        {
            "basis": "inference",
            "text": (
                "If the Delimbiyr freezes in the book's window, river traffic past the town, including "
                "the rivermen who carry passengers down from Daggerford, would likely halt or move "
                "onto the ice."
            ),
        },
    ],
    "arrabar": [
        {
            "basis": "inference",
            "text": (
                "For city art, the regional climate suggests shaded streets, light clothing, lush "
                "planting, and buildings suited to heat and heavy rain."
            ),
        },
        {
            "basis": "inference",
            "text": "The Netherwaters would likely feel damp and cooler than the streets above.",
        },
    ],
}

# Climates for a single settlement, used when its zone is shared with places the source
# does not cover. They take precedence over the zone entries above. Inland placements
# are regional interpretations, not town-specific measurements or engine overrides.
SETTLEMENT_CLIMATES = {
    "secomber": THE_NORTH_INLAND,
    "amphail": THE_NORTH_INLAND,
    "goldenfields": THE_NORTH_INLAND,
    "griffon_s_nest": THE_NORTH_INLAND,
    "red_larch": THE_NORTH_INLAND,
    "stone_bridge": THE_NORTH_INLAND,
    "triboar": THE_NORTH_INLAND,
    "yartar": THE_NORTH_INLAND,
    "leilon": THE_NORTH_COAST,
    "neverwinter": THE_NORTH_COAST,
    "waterdeep": THE_NORTH_COAST,
}
