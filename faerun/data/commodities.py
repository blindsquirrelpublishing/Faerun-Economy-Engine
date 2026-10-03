"""The commodity and product catalogue of Faerûn.

Base prices are expressed in gold pieces for the stated trade unit in a
notional "average" market with balanced supply and demand.  The engine then
adjusts them per settlement.

`produced_by` lists the industry tags that can create the good locally.
`demand` is a per-capita consumption index (1.0 == an everyday staple).
`luxury` is the wealth elasticity: 0 = necessity, 1 = pure luxury.
`perishable` drives spoilage losses over long trade routes.

Harvest, final-demand and warehouse settings below are explicit fictional
modeling assumptions, not canonical Forgotten Realms agricultural research.
Monthly weights run from Hammer through Nightal; the seasonality helpers
normalize them by Harptos month length. Legacy `season` price flags are retained
for the non-inventory model and are not crop consumption calendars.
"""

from __future__ import annotations

from ..data_store import load_commodities

# Editable at runtime via the MCP server's commodity tools; rows are persisted
# to faerun/data/store/commodities.json rather than defined here.
COMMODITIES = load_commodities()
COMMODITIES_BY_ID = {c.id: c for c in COMMODITIES}

# Input quantities make one trade unit of the output. They are deliberately
# simple economic recipes rather than workshop-level instructions.
SIMPLE_BOMS = {
  "flour": {"grain": 0.9},
  "bread": {"flour": 0.02, "salt": 0.001},
  "meat_salt": {"meat_fresh": 2.5, "salt": 0.2},
  "fish_salt": {"fish_fresh": 1.7, "salt": 0.2},
  "olive_oil": {"olives": 0.7},
  "ale": {"grain": 0.8},
  "mead": {"honey": 0.6},
  "wine_common": {"fruit": 3.5},
  "wine_fine": {"wine_common": 0.03},
  "brandy": {"wine_common": 0.08},
  "dwarven_spirits": {"grain": 0.08},
  "cloth_dyed": {"linen": 1.0, "dye_indigo": 0.25},
  "clothing_common": {"linen": 0.15},
  "clothing_fine": {"cloth_dyed": 0.25, "silk": 0.1},
  "charcoal": {"timber": 0.12},
  "iron_ingot": {"iron_ore": 0.15, "charcoal": 0.04},
  "steel_ingot": {"iron_ingot": 1.0, "coal": 0.04},
  "nails": {"iron_ingot": 3.0},
  "planks": {"timber": 0.65},
  "pitch": {"timber": 0.12},
  "sailcloth": {"linen": 1.2, "rope": 0.5},
  "glassware": {"coal": 0.05},
  "soap": {"olive_oil": 0.25, "salt": 0.03},
  "candles": {"wax": 1.5},
  "lamp_oil": {"olive_oil": 0.07},
  "parchment": {"leather": 0.005},
  "paper": {"timber": 0.0002},
  "ink": {"charcoal": 0.01, "olive_oil": 0.01},
  "book": {"paper": 100.0, "leather": 0.25, "ink": 0.25},
  "incense": {"spices_common": 0.5, "charcoal": 0.01},
  "perfume": {"spices_exotic": 0.1, "olive_oil": 0.02},
  "warhorse": {"horse_riding": 1.0, "grain": 20.0, "saddle": 1.0},
  "tools_carpenter": {"steel_ingot": 1.0, "planks": 0.02},
  "plow": {"iron_ingot": 5.0, "planks": 0.15},
  "cart": {"planks": 0.5, "nails": 0.2},
  "wagon": {"planks": 1.0, "nails": 0.5, "iron_ingot": 1.0},
  "barrel": {"planks": 0.2, "iron_ingot": 0.1},
  "saddle": {"leather": 2.0, "iron_ingot": 0.2},
  "lantern": {"iron_ingot": 0.15, "glassware": 0.05},
  "fishing_net": {"rope": 2.0},
  "ship_boat": {"planks": 8.0, "nails": 4.0, "rope": 5.0, "sailcloth": 2.0},
  "dagger": {"steel_ingot": 0.12, "leather": 0.03},
  "sword": {"steel_ingot": 0.3, "leather": 0.08},
  "axe_battle": {"steel_ingot": 0.35, "planks": 0.01},
  "spear": {"steel_ingot": 0.08, "planks": 0.01},
  "bow_short": {"planks": 0.005, "rope": 0.01},
  "bow_long": {"planks": 0.007, "rope": 0.012},
  "crossbow": {"steel_ingot": 0.2, "planks": 0.01, "rope": 0.01},
  "arrows": {"planks": 0.003, "steel_ingot": 0.03},
  "armor_leather": {"leather": 1.0},
  "armor_chain": {"steel_ingot": 5.5},
  "armor_plate": {"steel_ingot": 6.5, "leather": 0.5},
  "shield": {"planks": 0.015, "iron_ingot": 0.4, "leather": 0.1},
  "antitoxin": {"herbs_healing": 0.1, "ink": 0.02},
  "potion_healing": {"herbs_healing": 0.2, "honey": 0.02},
  "arcane_focus": {"gem_agate": 0.1, "silver_ingot": 0.02},
  "spellbook_blank": {"paper": 150.0, "leather": 1.0, "ink": 1.0},
  "smokepowder": {"charcoal": 0.2, "salt": 0.1},
  "scrimshaw": {"ivory": 0.1},
}

for commodity_id, components in SIMPLE_BOMS.items():
  COMMODITIES_BY_ID[commodity_id].bom = dict(components)

# Advanced goods require an established craft tradition, not just ingredients.
SKILL_REQUIREMENTS = {
    "steel_ingot": {"smith": 2},
    "clothing_fine": {"textile": 2},
    "armor_plate": {"armor": 3},
    "potion_healing": {"alch": 2},
    "arcane_focus": {"arcane": 2},
    "book": {"paper": 2},
}
for commodity_id, requirements in SKILL_REQUIREMENTS.items():
    COMMODITIES_BY_ID[commodity_id].required_skill = dict(requirements)

# Surface harvests change timing, not annual potential or production eligibility.
# Cold harvests are later/shorter, irrigated arid harvests avoid high summer, and
# tropical districts can supply several harvest windows. Underground agriculture
# uses its existing resource gates without inheriting a surface winter.
_HARVEST_CALENDARS = {
    "grain": {
        "temperate": [0, 0, 0, 0, 0, 0, 0.5, 3, 5, 1.5, 0, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 3, 7, 0, 0],
        "arid": [0, 0, 1, 4, 4, 1, 0, 0, 0, 0, 0, 0],
        "tropical": [0, 1, 3, 1, 0, 0, 0, 1, 3, 1, 0, 0],
    },
    "corn": {
        "temperate": [0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 1, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 1, 7, 2, 0],
        "arid": [0, 0, 0, 1, 3, 1, 0, 0, 0, 1, 3, 1],
        "tropical": [0, 0, 1, 3, 1, 0, 0, 0, 1, 3, 1, 0],
    },
    "rice": {
        "temperate": [0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 1, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 0, 0],
        "arid": [0, 0, 0, 1, 4, 1, 0, 0, 0, 1, 4, 1],
        "tropical": [0, 0, 1, 3, 1, 0, 0, 1, 3, 1, 0, 0],
    },
    "vegetables": {
        "temperate": [0, 0, 0.1, 0.4, 1, 2, 3, 3, 3, 2, 0.5, 0],
        "cold": [0, 0, 0, 0, 0, 0.3, 2, 4, 3, 0.7, 0, 0],
        "arid": [1, 2, 3, 2, 1, 0.2, 0.1, 0.2, 1, 2, 3, 2],
        "tropical": [1, 1, 1.5, 2, 1.5, 1, 1, 1, 1.5, 2, 1.5, 1],
    },
    "fruit": {
        "temperate": [0, 0, 0, 0, 0.2, 1, 2, 3, 4, 2, 0, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0.5, 2, 4, 1, 0, 0],
        "arid": [0.3, 0.5, 1, 2, 2, 1, 0.2, 0.5, 2, 3, 2, 0.5],
        "tropical": [1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1],
    },
    "nuts": {
        "temperate": [0, 0, 0, 0, 0, 0, 0, 0.5, 3, 5, 1.5, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 1, 7, 2, 0],
        "arid": [0, 0, 0, 0, 0, 0, 1, 3, 4, 2, 0, 0],
        "tropical": [0.5, 1, 2, 1, 0.5, 0.5, 0.5, 1, 2, 1, 0.5, 0.5],
    },
    "olives": {
        "temperate": [0.5, 0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 2.5],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 6, 3],
        "arid": [0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 1],
        "tropical": [1, 1, 2, 1, 0.5, 0.5, 1, 1, 2, 1, 0.5, 0.5],
    },
    "herbs": {
        "temperate": [0, 0, 0.2, 0.8, 2, 3, 3, 2, 1, 0.2, 0, 0],
        "cold": [0, 0, 0, 0, 0, 1, 3, 4, 2, 0, 0, 0],
        "arid": [0.5, 1, 3, 3, 1, 0.1, 0.1, 0.2, 1, 2, 1, 0.5],
        "tropical": [1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1],
    },
    "seed_spices": {
        "temperate": [0, 0, 0, 0, 0, 1, 2, 3, 3, 1, 0, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 1, 5, 4, 0, 0],
        "arid": [0, 1, 3, 4, 2, 0, 0, 0, 0, 0, 0, 0],
        "tropical": [0, 1, 2, 2, 0, 0, 0, 1, 2, 2, 0, 0],
    },
    "tropical_spices": {
        "temperate": [0, 0, 0, 0, 0.5, 1, 2, 3, 2, 1, 0.5, 0],
        "cold": [0, 0, 0, 0, 0, 0, 1, 3, 4, 2, 0, 0],
        "arid": [0.5, 1, 2, 2, 0.5, 0, 0, 0, 0.5, 1, 2, 0.5],
        "tropical": [1, 2, 3, 2, 1, 0.5, 1, 2, 3, 2, 1, 0.5],
    },
    "coffee": {
        "temperate": [0, 0, 0, 0, 0, 0, 0.5, 2, 4, 3, 0.5, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 3, 0],
        "arid": [1, 3, 3, 1, 0, 0, 0, 0, 0, 0, 1, 1],
        "tropical": [1, 3, 4, 2, 0.5, 0.2, 1, 3, 4, 2, 0.5, 0.2],
        "chult": [1, 3, 4, 2, 0.5, 0.2, 1, 3, 4, 2, 0.5, 0.2],
        "halruaa": [0.5, 0.2, 1, 3, 4, 2, 0.5, 0.2, 1, 3, 4, 2],
    },
    "cotton": {
        "temperate": [0, 0, 0, 0, 0, 0, 0, 1, 3, 4, 2, 0],
        "cold": [0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 4, 0],
        "arid": [0, 0, 0, 0, 0, 0, 0, 0.5, 2, 4, 3, 0.5],
        "tropical": [2, 3, 2, 0.5, 0, 0, 0, 0, 0, 0.5, 1, 2],
    },
    "wool": {
        "temperate": [0, 0, 0, 1, 5, 4, 0, 0, 0, 0, 0, 0],
        "cold": [0, 0, 0, 0, 1, 5, 4, 0, 0, 0, 0, 0],
        "arid": [0, 1, 4, 4, 1, 0, 0, 0, 0, 0, 0, 0],
        "tropical": [0, 0, 1, 3, 1, 0, 0, 0, 1, 3, 1, 0],
    },
}
_HARVEST_GOODS = {
    "grain": "grain",
    "corn": "corn",
    "rice": "rice",
    "vegetables": "vegetables",
    "fruit": "fruit chultan_fruit",
    "nuts": "nuts",
    "olives": "olives",
    "herbs": "herbs_healing tea spices_common",
    "seed_spices": "cumin coriander mustard_seed fennel_seed anise fenugreek",
    "tropical_spices": (
        "spices_exotic black_pepper long_pepper cinnamon cassia cloves nutmeg "
        "mace_spice cardamom ginger turmeric star_anise allspice vanilla"
    ),
    "coffee": "coffee coffee_green",
    "cotton": "cotton",
    "wool": "wool",
}
_HARVEST_GOODS["fruit"] += " chili_pepper juniper_berry sumac"
_HARVEST_GOODS["herbs"] += " asafoetida"
_HARVEST_CALENDARS["saffron"] = {
    "temperate": [0, 0, 0, 0, 0, 0, 0, 0, 1, 5, 4, 0],
    "arid": [0, 0, 0, 0, 0, 0, 0, 0, 2, 5, 3, 0],
}
_HARVEST_GOODS["saffron"] = "saffron"

for calendar_id, goods in _HARVEST_GOODS.items():
    calendar = _HARVEST_CALENDARS[calendar_id]
    for commodity_id in goods.split():
        commodity = COMMODITIES_BY_ID[commodity_id]
        commodity.production_profile = list(calendar["temperate"])
        commodity.regional_production_profiles = {
            climate: list(weights) for climate, weights in calendar.items()
            if climate != "temperate"
        }
        commodity.regional_production_profiles["underdark"] = []

# Consumption curves are deliberately limited to uses with seasonal demand.
# Crop scarcity price flags do NOT imply that people eat less bread in winter.
# Workshops, mills, roasters-as-workshops, brewers and alchemists have no annual
# shutdown: the aggregate roasted coffee and green-bean goods follow crop supply.
_DEMAND_CALENDARS = {
    "heating": [1.5, 1.4, 1.15, 1, 0.85, 0.7, 0.65, 0.7, 0.9, 1.1, 1.3, 1.45],
    "lighting": [1.35, 1.25, 1.1, 1, 0.9, 0.8, 0.75, 0.8, 1, 1.1, 1.2, 1.35],
    "warm_goods": [1.25, 1.2, 1.1, 1, 0.9, 0.8, 0.75, 0.8, 1, 1.15, 1.25, 1.3],
    "summer_drink": [0.95, 0.95, 1, 1, 1, 1.1, 1.15, 1.1, 1, 1, 0.95, 0.95],
    "spring_tools": [0.9, 1, 1.25, 1.3, 1.2, 1, 0.95, 0.95, 1, 1, 0.9, 0.85],
}
for calendar_id, goods in {
    "heating": "coal charcoal",
    "lighting": "candles lamp_oil whale_oil",
    "warm_goods": "clothing_common furs wool",
    "summer_drink": "ale",
    "spring_tools": "plow",
}.items():
    for commodity_id in goods.split():
        COMMODITIES_BY_ID[commodity_id].demand_profile = list(_DEMAND_CALENDARS[calendar_id])

# Storage days are capacity in baseline daily-use units, not a hard expiration
# date. Loss is a fraction of stock per day; reserves are baseline days of use.
# Live animals remain outside warehouse carryover (feeding is not modeled here).
for commodity in COMMODITIES:
    if commodity.category != "livestock":
        commodity.storage_days = 365
        commodity.storage_loss = 0.0001
        commodity.reserve_days = 15

_STORAGE_POLICIES = [
    ("grain corn rice", 400, 0.0003, 75),
    ("flour", 120, 0.002, 20),
    ("bread", 3, 0.25, 0.5),
    ("vegetables", 14, 0.05, 2),
    ("fruit chultan_fruit", 10, 0.08, 1),
    ("nuts", 270, 0.001, 30),
    ("cheese", 90, 0.004, 10),
    ("butter", 14, 0.04, 2),
    ("eggs", 21, 0.025, 3),
    ("meat_fresh fish_fresh", 2, 0.35, 0.25),
    ("meat_salt fish_salt olives", 180, 0.0015, 30),
    ("honey sugar salt", 730, 0.00005, 45),
    ("olive_oil lamp_oil whale_oil", 365, 0.0008, 30),
    ("ale", 60, 0.006, 7),
    ("mead wine_common", 365, 0.0005, 30),
    ("wine_fine brandy dwarven_spirits elverquisst", 730, 0.0001, 30),
    ("herbs_healing tea", 270, 0.0015, 60),
    ("antitoxin potion_healing holy_water reagents_rare spell_components", 730, 0.0001, 30),
    ("coffee", 60, 0.012, 7),
    ("coffee_green", 365, 0.0005, 60),
    ("cotton wool linen cloth_dyed furs", 400, 0.0004, 45),
    ("coal charcoal timber wax", 400, 0.0001, 45),
]
_SPICE_GOODS = (
    "spices_common spices_exotic black_pepper long_pepper cinnamon cassia cloves "
    "nutmeg mace_spice cardamom ginger turmeric cumin coriander mustard_seed "
    "fennel_seed anise star_anise fenugreek saffron sumac allspice vanilla "
    "chili_pepper paprika juniper_berry asafoetida"
)
_STORAGE_POLICIES.append((_SPICE_GOODS, 365, 0.0008, 45))
# Coffee's description explicitly says roasted: allow weeks, not the many
# months appropriate to green beans.
for goods, days, loss, reserve in _STORAGE_POLICIES:
    for commodity_id in goods.split():
        commodity = COMMODITIES_BY_ID[commodity_id]
        commodity.storage_days = days
        commodity.storage_loss = loss
        commodity.reserve_days = reserve

CATEGORIES = sorted({c.category for c in COMMODITIES})
