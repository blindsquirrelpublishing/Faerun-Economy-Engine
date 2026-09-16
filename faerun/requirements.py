"""Estimated demographics, final consumption, and local raw-resource floors.

These are transparent economic scenarios, not canonical census or geological
data. Consumption is in catalogue trade units/day; mass budgets are in pounds
and are divided by the supplied commodity's pounds/unit. Recipes are expanded
by the material-flow engine, never here.
"""

from __future__ import annotations

from copy import deepcopy
import math
from typing import Iterable

from .living import settlement_per_person_daily_requirements
from .models import Commodity, Settlement
from .population import population_report
from .water import LITRES_PER_GALLON


DAYS_PER_YEAR = 365.0
SECTORS = frozenset({
    "household", "defense", "arcane", "construction", "health",
    "logistics", "agriculture", "civic",
    "religion", "animals", "administration", "knowledge", "commerce",
    "communications", "hospitality", "utilities", "civil_security",
    "maintenance", "culture", "professional", "visitors",
})
PROVENANCE = (
    "Estimated economic model, not canon: population and geography come from "
    "the settlement record; occupations, diets, growth, equipment stocks and "
    "accessible hinterland are inferred, including for surveyed markets."
)

# Named tables are also included in each profile's formula_assumptions.
LAND_SHARES = {
    "grain": .36, "corn": .08, "rice": .025, "vegetables": .07,
    "fruit": .055, "nuts": .02, "pasture": .27, "poultry": .03,
    "herbs": .02, "olives": .025, "spices": .015, "tropical": .03,
}
CROP_YIELDS = {
    "grain": 600.0, "corn": 800.0, "rice": 1000.0,
    "vegetables": 2400.0, "fruit": 1500.0, "nuts": 300.0, "olives": 900.0,
}
TERRAIN_FARM_FACTORS = {
    "plains": 1.0, "coast": .75, "hills": .55, "forest": .35,
    "jungle": .45, "marsh": .25, "swamp": .20, "mountains": .12,
    "taiga": .08, "tundra": 0.0, "desert": 0.0, "cavern": 0.0,
}
WOODLAND_SHARES = {
    "plains": .04, "coast": .06, "hills": .15, "forest": .70,
    "jungle": .65, "marsh": .15, "swamp": .20, "mountains": .15,
    "taiga": .70, "tundra": 0.0, "desert": 0.0, "cavern": 0.0,
}
SPICE_SHARES = {
    "spices_common": .35, "spices_exotic": .08, "black_pepper": .10,
    "long_pepper": .01, "cinnamon": .025, "cassia": .015, "cloves": .01,
    "nutmeg": .01, "mace_spice": .005, "cardamom": .015, "ginger": .05,
    "turmeric": .025, "cumin": .04, "coriander": .04, "mustard_seed": .05,
    "fennel_seed": .025, "anise": .015, "star_anise": .005, "fenugreek": .025,
    "saffron": .001, "sumac": .02, "allspice": .01, "vanilla": .004,
    "chili_pepper": .025, "paprika": .025, "juniper_berry": .02,
    "asafoetida": .015,
}
# Poor/rich endpoints, linearly interpolated at wealth .65 / 1.40.
FOOD_PORTIONS_LB = {
    "coffee": (.0002, .012), "tea": (.0003, .006),
    "cocoa": (0.0, .008),  # Optional catalogue extension; never invent an id.
    "honey": (.002, .018), "sugar": (.0002, .030),
    "olives": (.001, .015), "olive_oil": (.003, .020),
    "wine_common": (.005, .10), "wine_fine": (0.0, .04),
    "brandy": (0.0, .008), "mead": (.002, .030),
    "dwarven_spirits": (0.0, .004), "elverquisst": (0.0, .0002),
}
# Category-independent edible goods; callers intersect with their catalogue.
FOOD_COMMODITIES = frozenset({
    "grain", "corn", "rice", "flour", "bread", "vegetables", "fruit",
    "chultan_fruit", "nuts", "cheese", "butter", "eggs", "meat_fresh",
    "meat_salt", "fish_fresh", "fish_salt", "salt", "ale",
} | FOOD_PORTIONS_LB.keys() | SPICE_SHARES.keys())
HOUSE_MATERIALS_LB = {
    "timber": 2000.0, "planks": 6000.0, "bricks": 6000.0,
    "granite": 4000.0, "nails": 80.0, "glassware": 20.0,
}
# Army equipment/person, militia equipment/person, annual renewal fractions.
EQUIPMENT = {
    "dagger": (.80, .35, .08, .04),
    "sword": (.25, .05, .08, .04),
    "axe_battle": (.10, .10, .08, .04),
    "spear": (.30, .60, .10, .05),
    "bow_short": (.10, .15, .10, .05),
    "bow_long": (.10, .04, .10, .05),
    "crossbow": (.15, .06, .08, .04),
    "armor_leather": (.45, .25, .12, .06),
    "armor_chain": (.50, .10, .06, .03),
    "armor_plate": (.05, 0.0, .04, .02),
    "shield": (.60, .70, .15, .08),
}
ARCANE_DAILY_UNITS = {
    "spell_components": .02, "reagents_rare": .002,
    "arcane_focus": .20 / DAYS_PER_YEAR,
    "spellbook_blank": .50 / DAYS_PER_YEAR,
    "faerzress_crystal": .05 / DAYS_PER_YEAR,
}
MINERALS = {
    # Required extraction industry and lb per extractor-day. No inferred rare ores.
    "iron_ore": ("mine_iron", 100.0), "coal": ("mine_coal", 120.0),
    "copper_ingot": ("mine_copper", 3.0), "tin_ingot": ("mine_tin", 2.0),
    "lead_ingot": ("mine_silver", 2.0), "silver_ingot": ("mine_silver", .02),
    "gold_ingot": ("mine_gold", .002), "mithral_ingot": ("mine_mithral", .01),
    "adamantine_ingot": ("mine_adamantine", .005),
    "gem_agate": ("mine_gem", .002), "gem_moonstone": ("mine_gem", .0002),
    "gem_emerald": ("mine_gem", .00002), "gem_ruby": ("mine_gem", .00002),
    "gem_diamond": ("mine_gem", .000005),
}
ESTABLISHMENT_INDUSTRIES = {
    "arcane": "arcane", "builders": "craft", "carpenters": "craft",
    "farms": "farm", "fisheries": "fish", "bakeries": "craft",
    "butchers": "cattle", "brewers": "brew", "smiths": "smith",
    "textiles": "textile", "health": "alch",
    "forestry": "log", "temples": "temple",
}
SERVICE_PARAMETERS = {
    "water_gallons_per_resident_day": 20.0 / LITRES_PER_GALLON,
    "waste_lb_per_resident_day": 4.0,
    "water_worker_share": .60,
    "water_gallons_per_worker_day": 5000.0 / LITRES_PER_GALLON,
    "waste_lb_per_worker_day": 2500.0,
    "water_collection_factors": {
        "river": 1.5, "oasis": .9, "desert": .3, "tundra": .5,
        "cavern": .4, "default": 1.0,
    },
}

ASSUMPTIONS = [
    PROVENANCE,
    "A year is 365 days; stocks are trade units, flows trade units/day. Population "
    "includes soldiers, mages and militia: everyone eats the household diet once.",
    "Wealth interpolates living.py necessities and supplementary food portions "
    "between .65 and 1.40, clamped at the endpoints; no demand_index or events apply here.",
    "Food diversity replaces existing staple, meat, dairy and fruit mass, rather "
    "than adding another full ration. Spices share one normalized seasoning budget; "
    "coffee, tea and optional cocoa are dry ingredients, not beverage weights.",
    "Mage fraction is zero without arcane industry/trait or magocracy; otherwise "
    ".001 + .0015*arcane_level + .008*magocracy + .0005*academic, capped at .025. "
    "Industry levels are clamped to 0..3; population estimates round down, except "
    "explicit magical settlements retain at least one mage when the worker pool "
    "allows it. The mage fraction is the nominal rate before integer rounding.",
    "Standing army fraction = min(.04, .003 + .004*security + .012*military "
    "+ .008*mercenary + .004*frontier). Militia fraction = min(.10, "
    ".03 + .04*frontier + .02*military); militia is a civilian reserve, not extra workers.",
    "Annual growth = clamp(.004 + .012*(wealth-1) + .004*frontier + .002*mercantile "
    "+ .002*agrarian - .015*wartorn, 0, .03). Stable/ruined and empty settlements "
    "have zero growth. Five residents/home; existing homes need .0075 home-equivalents "
    "of repairs/year. Each home-equivalent takes 180 workdays; a worker provides "
    "240 days/year, 65% building and 35% carpentry.",
    "Half the population is the modeled worker pool. All listed occupations are "
    "disjoint, bounded by that pool; militia is not subtracted again. Establishment "
    "workers are totals, not workers per establishment. Partial workshops round up. "
    "Counts are inferred labor/capacity estimates, not real surveyed businesses or "
    "proof of material-supported production; planned-output counts are computed "
    "separately by the material-flow engine.",
    "Defense purchases are stock*annual renewal/365 plus stock*growth/365, not a "
    "daily re-equipping. Ranged soldiers expend four sheaves/year and militia one. "
    "Mounted troops are 8% of military armies, otherwise 2%; horses renew at 10%/year.",
    "Construction timber is unsawn structural beams, distinct from planks. House "
    "materials include repairs; ingredients for planks, nails, tools and other "
    "products are NOT counted here. The global recipe engine adds BOM inputs.",
    "Raw capacity is an inferred annual-average gross harvest/extraction floor, "
    "independent of requirements, wealth, shortages, prices and events. Product "
    "recipes always have zero inferred raw capacity. Catalogue requires gates apply.",
    "Hinterland size factor = min(1,(2500/max(population,2500))**.7). Farm acres "
    "= population*6*size_factor*terrain_factor*(1+.12*farm_level). Desert farms "
    "require a river or oasis and use terrain factor .12; tundra and cavern crops "
    "are zero. Invalid climate allocations stay unused, never reassigned.",
    "Crop, orchard, pasture, poultry, herb, spice and tropical shares sum to one "
    "land budget. Crop yields are net of seed; fodder is pastured, purchased grain "
    "supplements are agricultural final use. Milk splits 85% cheese/15% butter; "
    "honey and wax are joint hive outputs, not independent full harvests.",
    "Woodland acres = population*8*size_factor*woodland_share, sustainably yielding "
    "180 lb/acre/year; jungle teak gets 15% of that same wood budget. A logging "
    "industry implies at least .18 woodland share only in non-arid surface terrain.",
    "A port implies fisheries even without a fish industry. Fisher fraction = "
    "min(.05, (.018 port/.006 river/.01 coast or documented inland fishery) "
    "+ .006*fish_level); catch = 60 lb/fisher-workday at 220 days/year. "
    "No water evidence means no fishery, even for an inherited port trait.",
    "Hills, mountains and caverns permit a small common iron/stone estimate, not "
    "rare deposits. Other metals require their named mining industry. Extractors "
    "share one workforce across eligible ores, stone and clay; a wealthy market "
    "does not acquire ore or tropical growing conditions.",
    "Unmodeled finished consumption goods retain demand*population*.002 trade "
    "units/day in an appropriate sector. Unmodeled BOM inputs and generic metal, "
    "material, textile and gem stocks have zero final consumption: industrial "
    "demand belongs to the recipe engine. Explicit end-uses such as grain, fuel, "
    "construction materials and medical linen are retained. Unmodeled arcane "
    "goods use mage population instead, so fallback cannot recreate mage demand "
    "in nonmagical settlements.",
    "Population, growth rates and staffing are fixed annual-average baseline "
    "assumptions, independent of the selected month. Time selection neither "
    "compounds population growth nor changes these census estimates.",
    "Legacy municipal staffing references split sanitation labor 60% water/40% waste; "
    "they are not total water availability. The domestic-water assessment separately "
    "estimates natural sources, household collection, municipal delivery and essential "
    "needs. Source yields are inferred, not a hydrological survey; a seaport alone "
    "does not provide fresh drinking water.",
]


def _finite(value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"Expected a finite number, got {value!r}")
    return value


def _commodity_weight(c: Commodity) -> float:
    weight = _finite(c.weight)
    if weight <= 0:
        raise ValueError(f"Commodity {c.id!r} weight must be positive, got {weight!r}")
    return weight


def _population(s: Settlement) -> int:
    return max(0, int(s.population))


def _level(s: Settlement, tag: str) -> float:
    return min(3.0, max(0.0, _finite(s.industry_level(tag))))


def _wealth_share(s: Settlement) -> float:
    return min(1.0, max(0.0, (_finite(s.wealth) - .65) / .75))


def _gates_allow(s: Settlement, c: Commodity) -> bool:
    return not c.requires or any(
        gate == s.terrain or gate in s.traits
        or (gate == "cavern" and s.underdark)
        for gate in c.requires
    )


def resource_assumptions(s: Settlement) -> dict:
    """Expose inferred footprints, shared allocations and extraction rates."""
    pop = _population(s)
    terrain = "cavern" if s.underdark else s.terrain
    size_factor = (2500.0 / max(pop, 2500)) ** .7
    irrigated = bool(s.river or s.has_trait("oasis"))
    farm_factor = TERRAIN_FARM_FACTORS.get(terrain, 0.0)
    if terrain == "desert" and irrigated:
        farm_factor = .12
    acres = pop * 6.0 * size_factor * farm_factor * (1 + .12 * _level(s, "farm"))
    land = {cid: acres * share for cid, share in LAND_SHARES.items()}
    woodland_share = WOODLAND_SHARES.get(terrain, 0.0)
    if terrain not in {"desert", "tundra", "cavern"} and _level(s, "log"):
        woodland_share = max(.18, woodland_share)
    woodland = pop * 8.0 * size_factor * woodland_share
    water = s.is_port or s.river or terrain == "coast" or _level(s, "fish") > 0
    fish_fraction = min(.05, (
        (.018 if s.is_port else .006 if s.river else .01)
        + .006 * _level(s, "fish")
    )) if water else 0.0
    fishers = int(pop * fish_fraction)
    rocky = terrain in {"hills", "mountains", "cavern"}
    weights = {}
    for cid, (industry, _) in MINERALS.items():
        level = _level(s, industry)
        if level or (cid == "iron_ore" and rocky):
            weights[cid] = level or .35
    if rocky or _level(s, "quarry"):
        weights["granite"] = 1 + _level(s, "quarry")
    if _level(s, "quarry") and s.specialties.get("marble", 0) > 0:
        weights["marble"] = _level(s, "quarry")
    if terrain in {"plains", "coast", "marsh", "swamp"} or (
        terrain not in {"tundra", "cavern"} and irrigated
    ):
        weights["bricks"] = .5 + _level(s, "pottery")
    extractors = pop * .01 * size_factor if weights else 0.0
    total = sum(weights.values()) or 1.0
    mineral_workers = {cid: extractors * w / total for cid, w in weights.items()}
    dairy_stock = land["pasture"] * .25
    poultry_stock = land["poultry"] * 12.0
    hives = (land["fruit"] + land["nuts"]) / 8.0
    draft_oxen = acres / 80.0
    return {
        "provenance": PROVENANCE,
        "size_factor": size_factor,
        "farm_terrain_factor": farm_factor,
        "irrigated": irrigated,
        "farm_acres": acres,
        "land_acres": land,
        "land_shares": dict(LAND_SHARES),
        "crop_yields_lb_per_acre_year": dict(CROP_YIELDS),
        "woodland_acres": woodland,
        "woodland_share": woodland_share,
        "sustainable_wood_lb_per_acre_year": 180.0,
        "fishers": fishers,
        "fish_catch_lb_per_worker_day": 60.0,
        "fishing_workdays_per_year": 220.0,
        "mineral_workers": mineral_workers,
        "mineral_lb_per_worker_day": {
            **{cid: rate for cid, (_, rate) in MINERALS.items()},
            "granite": 160.0, "bricks": 100.0, "marble": 80.0,
        },
        "dairy_stock": dairy_stock,
        "poultry_stock": poultry_stock,
        "hives": hives,
        "draft_oxen": draft_oxen,
        "supplemental_feed_lb_per_day": (
            dairy_stock * .5 + poultry_stock * .12 + draft_oxen * 2.0
        ),
        "assumptions": [
            "Pasture supports .25 cattle/acre, yielding 800 lb milk/head/year; "
            "85% becomes cheese at 6:1, 15% butter at 22:1. Annual cull is .15 "
            "at 300 lb edible meat/head.",
            "Poultry ground supports 12 birds/acre, 18 lb eggs/bird/year, "
            ".35 annual cull at 4 lb meat/bird. No separate full herd meat budget.",
            "Orchards support one hive/8 acres; honey 35 lb/hive/year and wax "
            "1 lb/hive/year. Shared milk, meat, honey and wax are joint outputs.",
            "Draft ox stock = farm acres/80. Supplemental grain/day is .5 lb/cow, "
            ".12 lb/bird and 2 lb/ox; pasture and crop residues provide other fodder.",
            "Herb acres yield 100 lb/year: 60% medicinal herbs, 40% tea. Spice acres "
            "yield 100 lb/year shared by SPICE_SHARES. Tropical acres split equally "
            "among chultan_fruit (1500 lb/acre/year), coffee (300), cocoa (250). "
            "All tropical output requires jungle terrain/trait; temperate tea "
            "represents the catalogue's herbal infusions.",
            "Ordinary rice requires jungle, marsh or irrigated desert; olives need "
            "jungle or irrigated desert. Taiga allows only grain, vegetables, "
            "pasture and herbs; tundra/cavern no normal surface crops.",
            "Extractor workforce = population*.01*size_factor, apportioned by "
            "industry levels (common iron .35, stone 1+quarry, clay .5+pottery). "
            "Raw smelted metals reflect the catalogue's current no-BOM definitions.",
        ],
    }


def _service_requirements(s: Settlement, pop: int, sanitation_workers: int) -> list[dict]:
    parameters = SERVICE_PARAMETERS
    sources = parameters["water_collection_factors"]
    source = ("river" if s.river else "oasis" if s.has_trait("oasis")
              else "cavern" if s.underdark else s.terrain)
    source_factor = sources.get(source, sources["default"])
    water_workers = sanitation_workers * parameters["water_worker_share"]
    waste_workers = sanitation_workers - water_workers
    estimates = (
        (
            "Municipal water staffing reference (not total water availability)", "gallon",
            pop * parameters["water_gallons_per_resident_day"],
            water_workers * parameters["water_gallons_per_worker_day"] * source_factor,
            f"Estimated {parameters['water_gallons_per_resident_day']:.3f} gallons/resident/day; "
            f"60% of {sanitation_workers} sanitation workers at "
            f"{parameters['water_gallons_per_worker_day']:.3f} gallons/worker-day, collection factor {source_factor:g}. "
            "Collection factors: river 1.5, oasis .9, desert .3, tundra .5, cavern .4, "
            "otherwise 1; ports supply no freshwater bonus.",
        ),
        (
            "Sanitation: waste and night-soil collection", "lb",
            pop * parameters["waste_lb_per_resident_day"],
            waste_workers * parameters["waste_lb_per_worker_day"],
            f"Estimated 4 lb/resident/day; remaining 40% of {sanitation_workers} "
            "sanitation workers at 2,500 lb/worker-day. This is solid waste and "
            "night-soil collection, not an additional drinking-water ration.",
        ),
    )
    return [
        {
            "name": name, "unit": unit,
            "scope": "municipal_water_reference" if unit == "gallon" else "municipal_service_reference",
            "required_per_day": float(required),
            "local_capacity_per_day": float(capacity),
            "unmet_per_day": float(max(0.0, required - capacity)),
            "basis": basis + " Inferred baseline municipal capacity, not surveyed "
            "infrastructure; excludes household self-service and is independent of month.",
        }
        for name, unit, required, capacity, basis in estimates
    ]


def settlement_profile(s: Settlement, *, include_services: bool = True) -> dict:
    """Return estimated demographics and an optional disjoint service classification.

    Original worker buckets remain the baseline census, not additional workers
    to sum with service rows. ``service_labor`` reconciles both classifications.
    """
    if include_services:
        population = _finite(s.population)
        if isinstance(s.population, bool) or population < 0 or not population.is_integer():
            raise ValueError("Population must be a finite nonnegative integer")
    pop = _population(s)
    wealth = max(0.0, _finite(s.wealth))
    security = min(1.0, max(0.0, _finite(s.security)))
    trait = s.has_trait
    worker_pool = int(pop * .5)
    mage_rate = 0.0
    if _level(s, "arcane") or trait("arcane") or trait("magocracy"):
        mage_rate = min(.025, .001 + .0015 * _level(s, "arcane")
                        + .008 * trait("magocracy") + .0005 * trait("academic"))
    mages = min(worker_pool, max(1, int(pop * mage_rate))) if mage_rate else 0
    army_rate = min(.04, .003 + .004 * security + .012 * trait("military")
                    + .008 * trait("mercenary") + .004 * trait("frontier"))
    army = min(worker_pool - mages, int(pop * army_rate))
    militia = min(pop - army - mages, int(pop * min(
        .10, .03 + .04 * trait("frontier") + .02 * trait("military"))))
    growth = min(.03, max(0.0, .004 + .012 * (wealth - 1)
                         + .004 * trait("frontier") + .002 * trait("mercantile")
                         + .002 * trait("agrarian") - .015 * trait("wartorn")))
    if not pop or trait("stable") or trait("ruined"):
        growth = 0.0
    homes = pop / 5.0
    new_homes = homes * growth
    repairs = homes * .0075
    construction_workers = (new_homes + repairs) * 180.0 / 240.0
    resources = resource_assumptions(s)
    remaining = worker_pool
    establishments = []

    def occupation(cid: str, name: str, desired: float, team: int, basis: str,
                   industry: str | None = None) -> int:
        nonlocal remaining
        workers = min(remaining, max(0, int(desired)))
        remaining -= workers
        row = {
            "id": cid, "name": name,
            "count": math.ceil(workers / team), "workers": workers,
            "workers_per_establishment": team,
            "labor_capacity_workdays_per_year": workers * 240,
            "count_basis": "inferred_labor_capacity",
            "basis": f"Estimated inferred labor/capacity: {basis}; {team} workers/"
            "establishment; worker-pool capped. Not real surveyed businesses "
            "or a claim of material-supported planned output.",
        }
        industry = industry or ESTABLISHMENT_INDUSTRIES.get(cid)
        if industry:
            row["industry"] = industry
        establishments.append(row)
        return workers

    occupation("arcane", "Mages and magical workshops", mages, 4, "modeled mage population")
    occupation("garrison", "Standing garrison companies", army, 50, "standing army, not militia")
    builders = occupation("builders", "Building crews", math.ceil(construction_workers * .65),
                          6, "home-equivalents*180/240*.65 worker-years")
    carpenters = occupation("carpenters", "Carpenters", math.ceil(construction_workers * .35),
                            4, "home-equivalents*180/240*.35 worker-years")
    farmers = occupation("farms", "Farms and market gardens", resources["farm_acres"] / 15,
                         5, "15 mixed farm acres/worker, includes stock and orchard care")
    fishers = occupation("fisheries", "Fishing crews", resources["fishers"],
                         4, "water access and fishing-industry catch workforce")
    occupation("bakeries", "Bakeries and mills", pop / 100, 5, "one food processor/100 residents")
    occupation("butchers", "Butchers and dairies", pop / 250, 3, "one processor/250 residents")
    occupation("brewers", "Breweries and inns", pop / 150, 5, "one worker/150 residents")
    occupation("smiths", "Smithies and tool workshops", pop * (.004 + .002 * _level(s, "smith")),
               4, "population*(.004+.002*smith_level)")
    occupation("textiles", "Textile and clothing workshops",
               pop * (.008 + .003 * _level(s, "textile")), 5,
               "population*(.008+.003*textile_level)")
    health_workers = occupation("health", "Healers and apothecaries",
                                pop * (.002 + .001 * _level(s, "temple")), 3,
                                "population*(.002+.001*temple_level)")
    logistics_workers = occupation("logistics", "Carriers and warehouses",
                                   pop * (.015 + .005 * _level(s, "trade")), 8,
                                   "population*(.015+.005*trade_level)")
    sanitation_workers = occupation(
        "sanitation", "Sanitation and water crews", pop * .005, 5, ".005*population")
    extractor_groups = {}
    for cid, workers in resources["mineral_workers"].items():
        industry = MINERALS[cid][0] if cid in MINERALS else (
            "pottery" if cid == "bricks" else "quarry")
        extractor_groups[industry] = extractor_groups.get(industry, 0.0) + workers
    for industry, workers in sorted(extractor_groups.items()):
        occupation("extraction_" + industry, "Extraction: " + industry.replace("_", " "),
                   workers, 8, "resource-weighted share of one extractor workforce", industry)
    occupation("forestry", "Woodland management and logging",
               resources["woodland_acres"] / 200, 6, "200 managed woodland acres/worker")
    temple_workers = occupation("temples", "Temple staff", pop * (
        .002 + .002 * _level(s, "temple")) if trait("temple") or _level(s, "temple") else 0,
        6, "population*(.002+.002*temple_level), only with a temple")
    equipment = {}
    for cid, (army_share, reserve_share, army_renewal, reserve_renewal) in EQUIPMENT.items():
        standing_stock, militia_stock = army * army_share, militia * reserve_share
        equipment[cid] = {
            "standing_stock": standing_stock, "militia_stock": militia_stock,
            "standing_replacement_rate": army_renewal,
            "militia_replacement_rate": reserve_renewal,
            "annual_replacement": standing_stock * army_renewal + militia_stock * reserve_renewal,
            "annual_growth_additions": (standing_stock + militia_stock) * growth,
        }
    mounted = army * (.08 if trait("military") else .02)
    equipment["warhorse"] = {
        "standing_stock": mounted, "militia_stock": 0.0,
        "standing_replacement_rate": .10, "militia_replacement_rate": 0.0,
        "annual_replacement": mounted * .10, "annual_growth_additions": mounted * growth,
    }
    profile = {
        "population": pop, "wealth": wealth, "mage_population": mages,
        "population_model": population_report(s),
        "standing_army": army, "militia": militia, "annual_growth_rate": growth,
        "builders": builders, "carpenters": carpenters,
        "new_homes_per_year": new_homes, "existing_homes": homes,
        "repair_home_equivalents_per_year": repairs,
        "worker_population": worker_pool, "unallocated_workers": remaining,
        "farm_workers": farmers, "fishers": fishers, "health_workers": health_workers,
        "logistics_workers": logistics_workers, "temple_workers": temple_workers,
        "sanitation_workers": sanitation_workers,
        "mage_population_fraction": mage_rate, "standing_army_fraction": army_rate,
        "defense_equipment": equipment, "mounted_troops": mounted,
        "establishments": establishments, "resource_assumptions": resources,
        "service_requirements": _service_requirements(s, pop, sanitation_workers),
        "reference_period": "Fixed annual-average baseline; independent of selected month.",
        "assumptions": list(ASSUMPTIONS), "provenance": PROVENANCE,
        "formula_assumptions": {
            "days_per_year": DAYS_PER_YEAR,
            "food_portions_lb_per_person_day_poor_rich": deepcopy(FOOD_PORTIONS_LB),
            "spice_mix_weights": dict(SPICE_SHARES),
            "house_materials_lb_per_home_equivalent": dict(HOUSE_MATERIALS_LB),
            "equipment_shares_and_annual_renewal": dict(EQUIPMENT),
            "arcane_trade_units_per_mage_day": dict(ARCANE_DAILY_UNITS),
            "farm_terrain_factors": dict(TERRAIN_FARM_FACTORS),
            "woodland_shares": dict(WOODLAND_SHARES),
            "service_parameters": deepcopy(SERVICE_PARAMETERS),
            "diet_allocation": (
                "Raw grain: 10% corn, 0..8% rice by wealth; convert at 60 lb/bushel. "
                "Meat: 30% fresh fish at ports, otherwise 20%; 6% salted meat, "
                "4% salted fish, remainder fresh meat (40 lb/side). Cheese mass "
                "splits 15% butter/85% cheese (20 lb/wheel). Fruit (30 lb/crate) "
                "splits 10% nuts, .5..20% Chultan fruit by wealth, remainder fruit. "
                "Spice budget .003..015 lb/person/day, normalized by mix weights."
            ),
            "institutional_final_use": (
                "Health/day/person: .002 lb herbs, .003 lb soap, .0005 lb linen. "
                "Antitoxin/year/person .003 (.02 jungle); healing potions .005 "
                "times (.5+wealth_share). Temple worker/day: .04 holy water, "
                ".01 lb incense, .02 lb candles. Mage/day: .02 lb herbs, "
                ".01 parchment sheets, .002 ink vials. Carpenter kits/year "
                "= .2*carpenters+.1*builders."
            ),
            "infrastructure_final_use": (
                "Carrier stock: population/250 carts and /1000 wagons, times "
                "(1+.25*trade_level+.5*port); renew 12%/year. Barrels stock "
                ".25*population, renew 25%/year; cargo animals population/500 "
                "times carrier factor, renew 10%/year and eat 4 lb grain/day. "
                "Fishers/4 boats renew 5%/year, .5 nets/fisher renew 35%/year. "
                "Rope stock 2 coils/fisher+.5/carrier, renew 30%/year. "
                "Farm plows and oxen: acres/80, renew 15% and 8%/year. "
                "Farm hand-tool kits .1/farm-worker/year. Mounted troops eat "
                "8 lb supplemental grain/horse/day; .5 saddles/horse-stock/year. "
                "Civic lighting .0005 lb oil/person/day; clerical paper "
                ".003 sheets/person/day*(1+academic); .0001 ink vials/person/day."
            ),
        },
    }
    if include_services:
        from .data.commodities import COMMODITIES
        from .services import service_sector_plans

        plans = service_sector_plans(s, COMMODITIES, profile)
        reused = math.fsum(row["reclassified_workers"] for row in plans)
        new = math.fsum(row["newly_allocated_workers"] for row in plans)
        other = math.fsum(row["workers"] for row in establishments) - reused
        profile["service_sectors"] = plans
        profile["service_labor"] = {
            "worker_population": worker_pool,
            "reclassified_workers": reused,
            "newly_allocated_workers": new,
            "service_workers": math.fsum(row["workers"] for row in plans),
            "other_occupation_workers": other,
            "remaining_unallocated_workers": max(0.0, remaining - new),
            "basis": (
                "Service FTE replace their recorded worker_sources, never add a "
                "second census. Original establishments and unallocated_workers "
                "are preserved as base-profile values. Other occupations + services "
                "+ remaining unallocated FTE partition the original worker pool. "
                "Legacy institutional/infrastructure formulas describe the disabled "
                "service model; enabled service inputs use service_sectors instead."
            ),
        }
    return profile


def final_requirements(
    s: Settlement, commodities: Iterable[Commodity], *, include_services: bool = True,
) -> dict[str, dict[str, float]]:
    """Final planned uses in trade units/day, including optional service inputs.

    Service inputs replace legacy health/civic/carrier uses, rather than adding
    a second copy. Visitor increments and actual delivery belong to the material
    engine. ``include_services=False`` preserves the original final-use model.
    """
    catalogue = tuple(commodities)
    if include_services:
        _finite(s.population)
    goods = {c.id: c for c in catalogue}
    weights = {cid: _commodity_weight(c) for cid, c in goods.items()}
    demand_indices = {cid: _finite(c.demand) for cid, c in goods.items()}
    intermediate_ids = {cid for c in goods.values() for cid in c.bom}
    result: dict[str, dict[str, float]] = {cid: {} for cid in goods}
    p = settlement_profile(s, include_services=False)
    plans = []
    if include_services:
        from .services import service_sector_plans

        plans = service_sector_plans(s, catalogue, p)
    pop = p["population"]
    if not pop:
        return result
    share = _wealth_share(s)
    modeled = set()

    def add(cid: str, sector: str, units: float) -> None:
        modeled.add(cid)
        if cid in result and (quantity := max(0.0, _finite(units))) > 0:
            result[cid][sector] = result[cid].get(sector, 0.0) + quantity

    def mass(cid: str, sector: str, pounds: float) -> None:
        modeled.add(cid)
        if cid in goods:
            add(cid, sector, pounds / weights[cid])

    core = settlement_per_person_daily_requirements(s)
    # The core's catalogue units are deliberate anchors, not freight weights
    # of livestock or liquid packaging; only edible mass is diversified here.
    staple_lb = core.pop("grain") * 60.0 * pop
    mass("grain", "household", staple_lb * (.90 - .08 * share))
    mass("corn", "household", staple_lb * .10)
    mass("rice", "household", staple_lb * .08 * share)
    meat_lb = core.pop("meat_fresh") * 40.0 * pop
    fish_share = .30 if s.is_port else .20
    mass("meat_fresh", "household", meat_lb * (.90 - fish_share))
    mass("fish_fresh", "household", meat_lb * fish_share)
    mass("meat_salt", "household", meat_lb * .06)
    mass("fish_salt", "household", meat_lb * .04)
    dairy_lb = core.pop("cheese") * 20.0 * pop
    mass("cheese", "household", dairy_lb * .85)
    mass("butter", "household", dairy_lb * .15)
    fruit_lb = core.pop("fruit") * 30.0 * pop
    exotic_share = .005 + .195 * share
    mass("fruit", "household", fruit_lb * (.90 - exotic_share))
    mass("chultan_fruit", "household", fruit_lb * exotic_share)
    mass("nuts", "household", fruit_lb * .10)
    for cid, units in core.items():
        add(cid, "household", units * pop)
    for cid, (poor, rich) in FOOD_PORTIONS_LB.items():
        mass(cid, "household", (poor + (rich - poor) * share) * pop)
    spice_budget = pop * (.003 + .012 * share)
    for cid, portion in SPICE_SHARES.items():
        mass(cid, "household", spice_budget * portion / sum(SPICE_SHARES.values()))

    for cid, inventory in p["defense_equipment"].items():
        add(cid, "defense", (inventory["annual_replacement"]
                            + inventory["annual_growth_additions"]) / DAYS_PER_YEAR)
    army_archers = sum(p["defense_equipment"][cid]["standing_stock"]
                       for cid in ("bow_short", "bow_long", "crossbow"))
    militia_archers = sum(p["defense_equipment"][cid]["militia_stock"]
                          for cid in ("bow_short", "bow_long", "crossbow"))
    add("arrows", "defense", (army_archers * 4 + militia_archers) / DAYS_PER_YEAR)
    add("saddle", "defense", p["mounted_troops"] * .5 / DAYS_PER_YEAR)
    mass("grain", "agriculture", p["mounted_troops"] * 8)
    mages = p["mage_population"]
    for cid, daily in ARCANE_DAILY_UNITS.items():
        add(cid, "arcane", mages * daily)
    mass("herbs_healing", "arcane", mages * .02)
    add("parchment", "arcane", mages * .01)
    add("ink", "arcane", mages * .002)

    home_equivalents = p["new_homes_per_year"] + p["repair_home_equivalents_per_year"]
    for cid, pounds in HOUSE_MATERIALS_LB.items():
        mass(cid, "construction", home_equivalents * pounds / DAYS_PER_YEAR)
    add("tools_carpenter", "construction", (
        p["carpenters"] * .2 + p["builders"] * .1) / DAYS_PER_YEAR)
    if not include_services:
        mass("herbs_healing", "health", pop * .002)
        mass("soap", "health", pop * .003)
        mass("linen", "health", pop * .0005)
        add("antitoxin", "health", pop * (.02 if s.terrain == "jungle" or s.has_trait("jungle")
                                        else .003) / DAYS_PER_YEAR)
        add("potion_healing", "health", pop * .005 * (.5 + share) / DAYS_PER_YEAR)
        add("holy_water", "civic", p["temple_workers"] * .04)
        mass("incense", "civic", p["temple_workers"] * .01)
        mass("candles", "civic", p["temple_workers"] * .02)
        mass("lamp_oil", "civic", pop * .0005)
        add("paper", "civic", pop * .003 * (1 + s.has_trait("academic")))
        add("ink", "civic", pop * .0001)
    else:
        modeled.update({
            "herbs_healing", "soap", "linen", "antitoxin", "potion_healing",
            "holy_water", "incense", "candles", "lamp_oil", "paper", "ink",
        })

    carrier_factor = 1 + .25 * _level(s, "trade") + .5 * s.is_port
    animals = pop / 500 * carrier_factor
    if not include_services:
        for cid, residents_per_vehicle in (("cart", 250), ("wagon", 1000)):
            add(cid, "logistics", pop / residents_per_vehicle * carrier_factor * .12 / DAYS_PER_YEAR)
        add("barrel", "logistics", pop * .25 * .25 / DAYS_PER_YEAR)
        add("mule", "logistics", animals * .1 / DAYS_PER_YEAR)
        add("ship_boat", "logistics", p["fishers"] / 4 * .05 / DAYS_PER_YEAR)
        add("rope", "logistics", (p["fishers"] * 2 + p["logistics_workers"] * .5) * .3 / DAYS_PER_YEAR)
    else:
        modeled.update({"cart", "wagon", "barrel", "mule"})
        # Fishing capital belongs to the unchanged fishing occupation, not
        # to the separately classified carrier service workforce.
        add("ship_boat", "agriculture", p["fishers"] / 4 * .05 / DAYS_PER_YEAR)
        add("rope", "agriculture", p["fishers"] * 2 * .3 / DAYS_PER_YEAR)
    mass("grain", "agriculture", animals * 4)
    add("fishing_net", "agriculture", p["fishers"] * .5 * .35 / DAYS_PER_YEAR)
    resources = p["resource_assumptions"]
    add("plow", "agriculture", resources["draft_oxen"] * .15 / DAYS_PER_YEAR)
    add("ox", "agriculture", resources["draft_oxen"] * .08 / DAYS_PER_YEAR)
    add("tools_carpenter", "agriculture", p["farm_workers"] * .1 / DAYS_PER_YEAR)
    mass("grain", "agriculture", resources["supplemental_feed_lb_per_day"])

    for cid, c in goods.items():
        if cid in modeled:
            continue
        if cid in intermediate_ids or c.category in {"metal", "material", "textile", "gem"}:
            continue
        if c.category == "arcane":
            add(cid, "arcane", max(0.0, demand_indices[cid]) * mages * .002)
            continue
        sector = {
            "arms": "defense", "livestock": "agriculture",
        }.get(c.category, "household")
        add(cid, sector, max(0.0, demand_indices[cid]) * pop * .002)
    # Add after household fallback so explicit service use does not erase an
    # existing household final good (e.g. lanterns, pottery or bound books).
    for plan in plans:
        for cid, units in plan["inputs_per_unit"].items():
            add(cid, plan["id"], plan["planned_per_day"] * units)
    return result


def local_resource_capacity(s: Settlement, c: Commodity) -> float:
    """Conservative annual-average RAW output floor, in this good's units/day."""
    weight = _commodity_weight(c)
    if c.bom or not _population(s) or not _gates_allow(s, c):
        return 0.0
    r = resource_assumptions(s)
    terrain = "cavern" if s.underdark else s.terrain
    tropical = terrain != "cavern" and (terrain == "jungle" or s.has_trait("jungle"))
    cid = c.id
    pounds = 0.0
    if cid in CROP_YIELDS:
        allowed = terrain not in {"tundra", "cavern"}
        if terrain == "taiga":
            allowed = cid in {"grain", "vegetables"}
        if cid == "rice":
            allowed = tropical or terrain in {"marsh", "swamp"} or (
                terrain == "desert" and r["irrigated"])
        if cid == "olives":
            allowed = tropical or (terrain == "desert" and r["irrigated"])
        if allowed:
            pounds = r["land_acres"][cid] * CROP_YIELDS[cid] / DAYS_PER_YEAR
    elif cid in {"cheese", "butter"}:
        milk = r["dairy_stock"] * 800.0 / DAYS_PER_YEAR
        pounds = milk * (.85 / 6 if cid == "cheese" else .15 / 22)
    elif cid == "meat_fresh":
        pounds = (r["dairy_stock"] * .15 * 300 + r["poultry_stock"] * .35 * 4) / DAYS_PER_YEAR
    elif cid == "eggs":
        pounds = r["poultry_stock"] * 18 / DAYS_PER_YEAR
    elif cid in {"honey", "wax"} and terrain != "taiga":
        pounds = r["hives"] * (35 if cid == "honey" else 1) / DAYS_PER_YEAR
    elif cid in {"herbs_healing", "tea"}:
        pounds = r["land_acres"]["herbs"] * 100 * (.6 if cid == "herbs_healing" else .4) / DAYS_PER_YEAR
    elif cid in {"chultan_fruit", "coffee", "cocoa"} and tropical:
        yields = {"chultan_fruit": 1500.0, "coffee": 300.0, "cocoa": 250.0}
        pounds = r["land_acres"]["tropical"] / 3 * yields[cid] / DAYS_PER_YEAR
    elif cid in SPICE_SHARES and terrain != "taiga":
        # Gate generic exotic blends too; they lack catalogue requires.
        if cid != "spices_exotic" or tropical:
            pounds = r["land_acres"]["spices"] * 100 * (
                SPICE_SHARES[cid] / sum(SPICE_SHARES.values())) / DAYS_PER_YEAR
    elif cid == "fish_fresh":
        pounds = r["fishers"] * r["fish_catch_lb_per_worker_day"] * (
            r["fishing_workdays_per_year"] / DAYS_PER_YEAR)
    elif cid in {"timber", "teak"}:
        teak_share = .15 if tropical else 0.0
        share = teak_share if cid == "teak" else 1 - teak_share
        pounds = r["woodland_acres"] * r["sustainable_wood_lb_per_acre_year"] * share / DAYS_PER_YEAR
    elif cid in r["mineral_workers"]:
        pounds = r["mineral_workers"][cid] * r["mineral_lb_per_worker_day"][cid]
    return max(0.0, _finite(pounds / weight))
