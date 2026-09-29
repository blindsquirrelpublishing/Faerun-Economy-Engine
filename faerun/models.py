"""Core data structures for the Faerûn Economy Engine."""

from __future__ import annotations

import re
import math
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from .population import PopulationBasis, population_report

# ---------------------------------------------------------------------------
# Settlement size categories -> market depth / sophistication
# ---------------------------------------------------------------------------

SIZE_TIERS = [
    (0, "thorp"),
    (80, "hamlet"),
    (400, "village"),
    (900, "small town"),
    (5000, "large town"),
    (12000, "small city"),
    (25000, "large city"),
    (60000, "metropolis"),
]


def size_category(population: int) -> str:
    label = "thorp"
    for threshold, name in SIZE_TIERS:
        if population >= threshold:
            label = name
    return label


def _slug(name: str) -> str:
    """Fold accents then reduce to a lowercase underscore identifier."""
    folded = unicodedata.normalize("NFKD", str(name))
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "_", folded.lower()).strip("_")


slugify = _slug


def _parse_levels(spec: str) -> Dict[str, float]:
    """Parse a compact 'tag3 tag2' industry / specialty string into a dict."""
    out: Dict[str, float] = {}
    if not spec:
        return out
    for token in str(spec).split():
        match = re.match(r"^([a-z_]+?)([0-9](?:\.[0-9])?)?$", token)
        if not match:
            continue
        tag, level = match.group(1), match.group(2)
        out[tag] = float(level) if level else 1.0
    return out


def _parse_tags(spec) -> List[str]:
    if not spec:
        return []
    if isinstance(spec, (list, tuple, set)):
        return [str(s) for s in spec]
    return str(spec).split()


def _size_norm(population: int) -> float:
    return max(0.0, min(1.0, (math.log(max(population, 20)) - math.log(50)) /
                        (math.log(150000) - math.log(50))))


def _polished_commodity_description(name: str, category: str, unit: str = "item") -> str:
    """Generate a readable default description for any commodity lacking custom text."""
    title = str(name).strip()
    if not title:
        return "A traded commodity in the Faerûn economy."

    general = {
        "food": "A staple trade good prized for daily sustenance and household use.",
        "drink": "A prepared beverage traded for refreshment, hospitality, and ritual use.",
        "luxury": "A refined luxury good sought by elites, merchants, and collectors.",
        "textile": "A woven or worked textile valued for clothing, shelter, and travel.",
        "material": "A bulk material that serves as the foundation of building, crafting, and repair.",
        "product": "A practical manufactured good made for everyday trade and labor.",
        "metal": "A mined or refined metal valued for armor, tools, and industry.",
        "gem": "A prized mineral or gemstone traded for ornament, wealth, and arcane study.",
        "arcane": "A magical trade good used by spellcasters, scholars, and ritualists.",
        "arms": "A weapon or defensive item made for war, hunting, and personal protection.",
        "livestock": "A living herd animal traded for labor, food, and transport.",
        "exotic": "A rare and often imported good prized for its scarcity and prestige.",
    }
    if category in general:
        base = general[category]
    elif category in ("farm", "craft"):
        base = "A practical good produced by local industry and moved through ordinary commerce."
    else:
        base = "A traded commodity valued in the markets of Faerûn."

    if "wine" in title.lower() or "ale" in title.lower() or "beer" in title.lower() or "mead" in title.lower():
        base = "A prepared beverage prized for hospitality, ceremony, and everyday refreshment."
    elif "cloth" in title.lower() or "linen" in title.lower() or "silk" in title.lower() or "wool" in title.lower():
        base = "A woven textile valued for clothing, furnishing, and caravan gear."
    elif "ore" in title.lower() or "iron" in title.lower() or "steel" in title.lower() or "copper" in title.lower() or "gold" in title.lower() or "silver" in title.lower():
        base = "A mineral or refined metal traded for tools, industry, and coinage."
    elif "armor" in title.lower() or "sword" in title.lower() or "axe" in title.lower() or "bow" in title.lower() or "shield" in title.lower() or "dagger" in title.lower():
        base = "A weapon or protective item forged for war, hunting, and martial service."
    elif "book" in title.lower() or "parchment" in title.lower() or "paper" in title.lower() or "ink" in title.lower():
        base = "A written or scholarly good valued by scribes, mages, and record-keepers."
    elif "spell" in title.lower() or "focus" in title.lower() or "reagent" in title.lower() or "crystal" in title.lower():
        base = "A magical trade good used for ritual practice, scholarship, and spellcraft."

    return f"{title} is a {category} good in Faerûn, traded in {unit} lots for daily use, craft, and commerce. {base}"


@dataclass
class Commodity:
    """A tradeable good: raw commodity or manufactured product."""

    id: str
    name: str
    category: str
    base_price: float          # gp for one `unit` in a balanced, average market
    unit: str = "item"
    weight: float = 1.0        # lb per unit (drives freight cost)
    produced_by: List[str] = field(default_factory=list)   # industry tags
    required_skill: Dict[str, float] = field(default_factory=dict)  # minimum industry level by tag
    demand: float = 1.0        # per-capita demand index (1.0 == staple)
    luxury: float = 0.0        # 0 = necessity, 1 = pure luxury (wealth elasticity)
    perishable: float = 0.0    # 0 = imperishable, 1 = highly perishable
    demand_traits: Dict[str, float] = field(default_factory=dict)
    season: Dict[str, float] = field(default_factory=dict)
    substitutes: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)  # terrain or trait gates
    description: str = ""
    bom: Dict[str, float] = field(default_factory=dict)  # input commodity -> units
    production_profile: List[float] = field(default_factory=list)
    demand_profile: List[float] = field(default_factory=list)
    regional_production_profiles: Dict[str, List[float]] = field(default_factory=dict)
    storage_days: float = 0.0
    storage_loss: float = 0.0
    reserve_days: float = 0.0

    def season_multiplier(self, season: str) -> float:
        return float(self.season.get(season, 1.0))

    @property
    def production_type(self) -> str:
        return "processed/manufactured" if self.bom else "raw"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if not data.get("description"):
            data["description"] = _polished_commodity_description(
                data.get("name", ""),
                data.get("category", "product"),
                data.get("unit", "item"),
            )
        data["production_type"] = self.production_type
        return data


def C(
    id: str,
    name: str,
    category: str,
    base_price: float,
    unit: str = "item",
    weight: float = 1.0,
    produced_by: str = "",
    required_skill: Optional[Dict[str, float]] = None,
    demand: float = 1.0,
    luxury: float = 0.0,
    perishable: float = 0.0,
    traits: Optional[Dict[str, float]] = None,
    season: Optional[Dict[str, float]] = None,
    substitutes: str = "",
    requires: str = "",
    description: str = "",
    production_profile: Optional[List[float]] = None,
    demand_profile: Optional[List[float]] = None,
    regional_production_profiles: Optional[Dict[str, List[float]]] = None,
    storage_days: float = 0.0,
    storage_loss: float = 0.0,
    reserve_days: float = 0.0,
) -> Commodity:
    """Compact constructor used by the data tables."""
    normalized_description = description or _polished_commodity_description(
        name, category, unit
    )
    return Commodity(
        id=id,
        name=name,
        category=category,
        base_price=float(base_price),
        unit=unit,
        weight=float(weight),
        produced_by=_parse_tags(produced_by),
        required_skill={tag: float(level) for tag, level in (required_skill or {}).items()},
        demand=float(demand),
        luxury=float(luxury),
        perishable=float(perishable),
        demand_traits=dict(traits or {}),
        season=dict(season or {}),
        substitutes=_parse_tags(substitutes),
        requires=_parse_tags(requires),
        description=normalized_description,
        production_profile=list(production_profile or []),
        demand_profile=list(demand_profile or []),
        regional_production_profiles={key: list(values) for key, values in (regional_production_profiles or {}).items()},
        storage_days=storage_days,
        storage_loss=storage_loss,
        reserve_days=reserve_days,
    )


@dataclass
class GuildChapter:
    """A local guild chapter with enough presence to affect market behavior."""

    id: str
    name: str
    domains: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    commodities: List[str] = field(default_factory=list)
    size: int = 0
    power: float = 0.0
    tax_rate: float = 0.0
    enforcement: float = 0.0

    def applies_to(self, commodity: Commodity) -> bool:
        return (
            "*" in self.categories
            or commodity.id in self.commodities
            or commodity.category in self.categories
            or any(tag in self.domains for tag in commodity.produced_by)
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


GUILD_TEMPLATES = (
    {
        "id": "merchant_guild",
        "name": "Merchant Guild",
        "domains": ["trade"],
        "categories": ["*"],
        "weight": 0.75,
    },
    {
        "id": "farmers_millers_guild",
        "name": "Farmers' and Millers' Guild",
        "domains": ["farm", "orchard", "cattle", "herd", "brew", "vint", "distill"],
        "categories": ["food"],
        "weight": 0.55,
    },
    {
        "id": "fishers_watermen_guild",
        "name": "Fishers' and Watermen's Guild",
        "domains": ["fish", "whale", "ship", "salt"],
        "categories": ["food"],
        "weight": 0.5,
    },
    {
        "id": "smiths_armorers_guild",
        "name": "Smiths' and Armorers' Guild",
        "domains": ["smith", "armor", "weapon", "mine_iron", "mine_copper", "mine_tin", "mine_silver", "mine_gold", "mine_gem", "mine_mithral", "mine_adamantine", "mine_coal"],
        "categories": ["arms", "metal"],
        "weight": 0.65,
    },
    {
        "id": "artisans_guild",
        "name": "Artisans' Guild",
        "domains": ["craft", "textile", "glass", "pottery", "paper", "tan", "rope", "log", "quarry"],
        "categories": ["craft", "luxury"],
        "weight": 0.55,
    },
    {
        "id": "alchemists_apothecaries_guild",
        "name": "Alchemists' and Apothecaries' Guild",
        "domains": ["alch", "herb", "spice", "arcane"],
        "categories": ["arcane", "luxury"],
        "weight": 0.6,
    },
)


def inferred_guild_chapters(settlement: "Settlement") -> List[GuildChapter]:
    """Infer plausible active guild chapters from settlement scale and industries."""
    if settlement.population < 400:
        return []
    market_scale = _size_norm(settlement.population)
    trade_level = settlement.industry_level("trade")
    civic_bonus = 0.25 if settlement.has_trait("mercantile") else 0.0
    civic_bonus += 0.15 if settlement.has_trait("cosmopolitan") else 0.0
    chapters: List[GuildChapter] = []
    for template in GUILD_TEMPLATES:
        raw_level = max((settlement.industry_level(tag) for tag in template["domains"]), default=0.0)
        if template["id"] == "merchant_guild":
            raw_level = max(raw_level, trade_level + civic_bonus)
        level = raw_level * float(template["weight"])
        if level < 0.85 or (settlement.population < 900 and level < 1.2):
            continue
        size = max(3, round(settlement.population * (0.0015 + level * 0.0025) * (0.45 + market_scale)))
        power = min(1.0, 0.12 + 0.10 * level + 0.08 * trade_level + 0.13 * settlement.wealth
                    + 0.10 * settlement.security + 0.12 * market_scale)
        enforcement = min(1.0, math.sqrt(size) / 25.0 * power)
        tax_rate = (0.002 + 0.010 * power) * min(1.0, level / 2.5)
        chapters.append(GuildChapter(
            id=str(template["id"]),
            name=str(template["name"]),
            domains=list(template["domains"]),
            categories=list(template["categories"]),
            size=int(size),
            power=round(power, 3),
            tax_rate=round(tax_rate, 4),
            enforcement=round(enforcement, 3),
        ))
    return chapters


# ---------------------------------------------------------------------------
# Settlements
# ---------------------------------------------------------------------------


@dataclass
class Settlement:
    """A market: a town, city, citadel, port or Underdark enclave."""

    id: str
    name: str
    region: str
    zone: str
    population: int
    x: float
    y: float
    wealth: float = 1.0        # prosperity multiplier (affects luxury demand)
    tax: float = 0.05          # tariff / market duty applied to sale prices
    security: float = 0.75     # 0 = lawless, 1 = utterly safe (affects freight risk)
    port: Optional[str] = None  # sea basin name if it is a seaport
    river: bool = False
    terrain: str = "plains"
    landmass: str = "faerun"
    underdark: bool = False
    traits: List[str] = field(default_factory=list)
    industries: Dict[str, float] = field(default_factory=dict)
    specialties: Dict[str, float] = field(default_factory=dict)  # commodity id -> bonus
    shortages: List[str] = field(default_factory=list)           # commodity ids
    ruler: str = ""
    description: str = ""
    population_basis: Optional[PopulationBasis] = None
    guilds: List[GuildChapter] = field(default_factory=list)

    @property
    def size(self) -> str:
        return size_category(self.population)

    @property
    def is_port(self) -> bool:
        return bool(self.port)

    def has_trait(self, trait: str) -> bool:
        return trait in self.traits

    def industry_level(self, tag: str) -> float:
        return float(self.industries.get(tag, 0.0))

    def guild_chapters(self) -> List[GuildChapter]:
        explicit = list(self.guilds)
        explicit_ids = {guild.id for guild in explicit}
        inferred = [chapter for chapter in inferred_guild_chapters(self)
                    if chapter.id not in explicit_ids]
        return explicit + inferred

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["size"] = self.size
        data.pop("population_basis")
        data["guilds"] = [guild.to_dict() for guild in self.guild_chapters()]
        data["population_model"] = population_report(self)
        return data


@dataclass
class Business:
    """A merchant house or workshop operating in one or more settlements."""

    id: str
    name: str
    headquarters: str
    locations: List[str]
    specialties: List[str]
    offers: Dict[str, str]
    price_modifier: float = 1.0
    description: str = ""
    ability_scores: Dict[str, int] = field(default_factory=lambda: {
        "CAP": 10, "OPS": 10, "STA": 10,
        "PLN": 10, "CTR": 10, "REP": 10,
    })
    skills: Dict[str, int] = field(default_factory=dict)
    inventory: Dict[str, Dict[str, int]] = field(default_factory=dict)
    services: List[str] = field(default_factory=list)
    roles: Dict[str, int] = field(default_factory=dict)
    employees: Dict[str, int] = field(default_factory=dict)
    employee_roster: List[Dict[str, Any]] = field(default_factory=list)
    location_addresses: Dict[str, Dict[str, str]] = field(default_factory=dict)
    location_mode: str = "fixed"
    itinerary: List[Dict[str, Any]] = field(default_factory=list)
    carrier_service_id: str = ""
    carrier_modes: List[str] = field(default_factory=list)
    transport_equipment: Dict[str, int] = field(default_factory=dict)
    capacity_lb: int = 0
    capacity_ft3: float = 0.0

    def __post_init__(self) -> None:
        if self.location_mode not in {"fixed", "rolling"}:
            raise ValueError("Business location_mode must be 'fixed' or 'rolling'")
        if not self.employees:
            self.employees = {
                "owners": 1 if len(self.locations) == 1 else 2,
                "managers": max(1, len(self.locations) // 2),
                "merchants": max(2, len(self.offers)),
                "warehouse_staff": max(1, len(self.locations)),
            }
        for role, count in self.employees.items():
            if not isinstance(count, int) or count < 0:
                raise ValueError(f"Employee counts must be non-negative integers: {role}")
        if self.capacity_lb < 0 or not isinstance(self.capacity_lb, int):
            raise ValueError("Business capacity_lb must be a non-negative integer")
        if self.capacity_ft3 < 0 or not isinstance(self.capacity_ft3, (int, float)):
            raise ValueError("Business capacity_ft3 must be non-negative")
        if self.carrier_service_id and not self.capacity_ft3 and self.capacity_lb:
            self.capacity_ft3 = round(self.capacity_lb / 40.0, 2)
        for equipment, count in self.transport_equipment.items():
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise ValueError(f"Transport equipment counts must be non-negative integers: {equipment}")
        if not self.employee_roster:
            default_classes = {
                "owners": ("Manager", 5),
                "managers": ("Manager", 3),
                "merchants": ("Artisan", 2),
                "warehouse_staff": ("Laborer", 2),
            }
            self.employee_roster = [
                {"class": worker_class, "level": level, "count": count}
                for role, count in self.employees.items()
                if count and (worker_class := default_classes.get(role, ("Laborer", 1))[0])
                for level in [default_classes.get(role, ("Laborer", 1))[1]]
            ]
        for worker in self.employee_roster:
            if not isinstance(worker, dict) or not isinstance(worker.get("class"), str):
                raise ValueError("Employee roster entries require a class")
            if not isinstance(worker.get("level"), int) or not 1 <= worker["level"] <= 10:
                raise ValueError("Employee roster levels must be integers from 1 to 10")
            if not isinstance(worker.get("count"), int) or worker["count"] < 0:
                raise ValueError("Employee roster counts must be non-negative integers")
        for index, location in enumerate(self.locations, start=1):
            if location not in self.location_addresses:
                label = location.replace("_", " ").title()
                district = "Trade Quarter"
                road = "High Road" if location == self.headquarters else "Market Road"
                number = 10 + ((sum(ord(char) for char in self.id + location) + index) % 890)
                self.location_addresses[location] = {
                    "street": f"{road}, {number}",
                    "district": district,
                    "city": label,
                    "zip": f"FA-{sum(ord(char) for char in location) % 100:02d}-{number:03d}",
                }
            address = self.location_addresses[location]
            required = {"street", "district", "city", "zip"}
            if not required.issubset(address) or any(not str(address[key]).strip() for key in required):
                raise ValueError(f"Business address is incomplete: {location}")
        unknown_addresses = set(self.location_addresses) - set(self.locations)
        if unknown_addresses:
            raise ValueError(f"Business address is not a branch: {sorted(unknown_addresses)[0]}")
        if not self.inventory:
            quality_stock = {"basic": 8.0, "standard": 14.0, "fine": 9.0, "masterwork": 3.0}
            self.inventory = {
                location: {
                    commodity: int(round(quality_stock.get(quality, 8.0) * (1.5 if location == self.headquarters else 0.75)))
                    for commodity, quality in self.offers.items()
                }
                for location in self.locations
            }
        for location, stock in self.inventory.items():
            if location not in self.locations:
                raise ValueError(f"Business inventory location is not a branch: {location}")
            for commodity, quantity in stock.items():
                if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
                    raise ValueError(f"Business inventory must be a non-negative whole number: {commodity}")

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["satellites"] = [
            location for location in self.locations if location != self.headquarters
        ]
        data["inventory_total"] = round(sum(
            quantity for stock in self.inventory.values() for quantity in stock.values()
        ), 2)
        data["employee_total"] = sum(worker["count"] for worker in self.employee_roster)
        return data

    @property
    def employee_total(self) -> int:
        return sum(worker["count"] for worker in self.employee_roster)


def S(
    name: str,
    region: str,
    zone: str,
    population: int,
    x: float,
    y: float,
    wealth: float = 1.0,
    tax: float = 0.05,
    sec: float = 0.75,
    port: Optional[str] = None,
    river: bool = False,
    terrain: str = "plains",
    landmass: str = "faerun",
    underdark: bool = False,
    traits: str = "",
    ind: str = "",
    spec: str = "",
    short: str = "",
    ruler: str = "",
    desc: str = "",
    population_basis: Optional[PopulationBasis] = None,
    guilds: Optional[List[GuildChapter]] = None,
) -> Settlement:
    """Compact constructor used by the gazetteer."""
    return Settlement(
        id=_slug(name),
        name=name,
        region=region,
        zone=zone,
        population=int(population),
        x=float(x),
        y=float(y),
        wealth=float(wealth),
        tax=float(tax),
        security=float(sec),
        port=port,
        river=bool(river),
        terrain=terrain,
        landmass=landmass,
        underdark=bool(underdark),
        traits=_parse_tags(traits),
        industries=_parse_levels(ind),
        specialties=_parse_levels(spec),
        shortages=_parse_tags(short),
        ruler=ruler,
        description=desc,
        population_basis=population_basis,
        guilds=list(guilds or []),
    )


# ---------------------------------------------------------------------------
# World events
# ---------------------------------------------------------------------------


@dataclass
class Event:
    """A world event that distorts supply, demand or trade."""

    id: str
    name: str
    kind: str = "generic"
    settlements: List[str] = field(default_factory=list)  # settlement ids ([] = all)
    zones: List[str] = field(default_factory=list)        # zone names
    regions: List[str] = field(default_factory=list)
    commodities: List[str] = field(default_factory=list)  # commodity ids ([] = all)
    categories: List[str] = field(default_factory=list)   # commodity categories
    supply: float = 1.0     # multiplier on local supply
    demand: float = 1.0     # multiplier on local demand
    price: float = 1.0      # direct multiplier on the final price
    risk: float = 0.0       # added freight risk on routes touching the area
    start_month: Optional[int] = None
    duration_months: Optional[int] = None
    description: str = ""

    def applies_to_settlement(self, settlement: Settlement) -> bool:
        if not (self.settlements or self.zones or self.regions):
            return True
        return (
            settlement.id in self.settlements
            or settlement.zone in self.zones
            or settlement.region in self.regions
        )

    def applies_to_commodity(self, commodity: Commodity) -> bool:
        if not (self.commodities or self.categories):
            return True
        return commodity.id in self.commodities or commodity.category in self.categories

    def active_on(self, absolute_month: Optional[int]) -> bool:
        if self.start_month is None or absolute_month is None:
            return True
        if absolute_month < self.start_month:
            return False
        if self.duration_months is None:
            return True
        return absolute_month < self.start_month + self.duration_months

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Price results
# ---------------------------------------------------------------------------


def price_terms(price: float, buy_price: float) -> Dict[str, Any]:
    """Consumer-facing quote directions and gross resale economics."""
    if any(isinstance(value, bool) or not isinstance(value, (int, float))
           or not math.isfinite(value) or value < 0 for value in (price, buy_price)):
        raise ValueError("Buy and sell quotes must be finite non-negative prices")
    if buy_price > price:
        raise ValueError("A merchant purchase offer cannot exceed its resale quote")
    spread = price - buy_price
    return {
        "consumer_buy_price": price,
        "consumer_sell_price": buy_price,
        "merchant_spread": round(spread, 6),
        "merchant_markup_pct": spread / buy_price * 100 if buy_price else None,
        "merchant_margin_pct": spread / price * 100 if price else None,
    }


@dataclass
class PriceQuote:
    """The result of pricing one commodity in one market."""

    settlement: str
    commodity: str
    commodity_name: str
    category: str
    production_type: str
    unit: str
    base_price: float
    price: float           # what a buyer pays per unit (gp)
    buy_price: float       # what a local merchant pays a PC per unit (gp)
    multiplier: float      # price / base_price
    availability: str
    stock: int             # retail stock estimate, including protected local use
    supply_index: float
    demand_index: float
    production_per_day: float
    demand_per_day: float
    scarcity: float
    source: Optional[str] = None       # largest active import supplier
    source_distance: Optional[float] = None
    source_days: Optional[float] = None
    factors: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    quality: str = "standard"
    quality_offers: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    backup_sources: List[Dict[str, Any]] = field(default_factory=list)
    imports_per_day: float = 0.0
    exports_per_day: float = 0.0
    local_consumption_per_day: float = 0.0
    unmet_demand_per_day: float = 0.0
    production_capacity_per_day: float = 0.0
    household_demand_per_day: float = 0.0
    household_consumption_per_day: float = 0.0
    processing_demand_per_day: float = 0.0
    processing_consumption_per_day: float = 0.0
    material_closing_stock: float = 0.0
    production_inputs: List[Dict[str, Any]] = field(default_factory=list)
    final_demand_per_day: float = 0.0
    final_consumption_per_day: float = 0.0
    demand_sectors: Dict[str, float] = field(default_factory=dict)
    consumption_sectors: Dict[str, float] = field(default_factory=dict)
    stock_horizon_days: float = 10.0
    stock_scope: str = "market"
    producer_gate_price: Optional[float] = None
    producer_price_factor: float = 1.0
    guild_markup_rate: float = 0.12
    guilds: List[Dict[str, Any]] = field(default_factory=list)
    guild_tax_rate: float = 0.0
    guild_enforcement: float = 0.0
    order_available_by_quality: Optional[Dict[str, int]] = None
    order_claimed_stock: int = 0
    order_supply_window: Optional[Dict[str, Any]] = None
    seasonality: Dict[str, Any] = field(default_factory=dict)
    inventory: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {**asdict(self), **price_terms(self.price, self.buy_price)}
        data["import_need_per_day"] = self.import_need_per_day
        data["exportable_supply_per_day"] = self.exportable_supply_per_day
        data["uncommitted_supply_per_day"] = self.uncommitted_supply_per_day
        data["uncommitted_stock"] = self.uncommitted_stock
        data["forecast_uncommitted_stock"] = (
            min(self.stock, self._uncommitted_total()) if self.stock_scope == "market"
            else self._forecast_uncommitted_by_quality().get(self.stock_scope, 0))
        supplied = sum(row["quantity_per_day"] for row in self.sources)
        base_gate = (self.producer_gate_price / self.producer_price_factor
                     if self.producer_gate_price is not None else None)
        guild_floor = (sum(row["quantity_per_day"] * row["unit_cost"] for row in self.sources) / supplied
                       if supplied else base_gate)
        data["guild_wholesale_price"] = (
            round(guild_floor * self.producer_price_factor * (1 + self.guild_markup_rate), 6)
            if guild_floor is not None else None)
        free_by_quality = self._uncommitted_by_quality()
        forecast_by_quality = self._forecast_uncommitted_by_quality()
        for offer in data["quality_offers"]:
            offer.update(price_terms(offer["price"], offer["buy_price"]))
            offer["uncommitted_stock"] = free_by_quality.get(offer["quality"], 0)
            offer["stock_horizon_days"] = self.stock_horizon_days
            offer["stock_scope"] = offer["quality"]
            offer["forecast_uncommitted_stock"] = forecast_by_quality.get(offer["quality"], 0)
            offer["producer_gate_price"] = round(base_gate * offer["price_factor"], 6) if base_gate is not None else None
            offer["guild_wholesale_price"] = (
                round(guild_floor * offer["price_factor"] * (1 + self.guild_markup_rate), 6)
                if guild_floor is not None else None)
        return data

    @property
    def local_supply_per_day(self) -> float:
        opening = (max(0.0, self.inventory["opening_stock"] - self.inventory["spoilage"])
                   if self.inventory.get("enabled") else 0.0)
        return self.production_per_day + opening

    @property
    def import_need_per_day(self) -> float:
        return max(0.0, self.demand_per_day - self.local_supply_per_day)

    @property
    def exportable_supply_per_day(self) -> float:
        reserve = self.inventory["reserve_target"] if self.inventory.get("enabled") else 0.0
        return max(0.0, self.local_supply_per_day - self.demand_per_day - reserve)

    @property
    def uncommitted_supply_per_day(self) -> float:
        """Protect planned final/processing demand and already allocated exports."""
        values = (self.production_per_day, self.imports_per_day,
                  self.exports_per_day, self.demand_per_day)
        if any(not math.isfinite(value) or value < 0 for value in values):
            raise ValueError("Daily supply and demand balances must be finite and non-negative")
        surplus = max(0.0, self.production_per_day + self.imports_per_day
                      - self.exports_per_day - self.demand_per_day)
        return min(surplus, self.inventory["uncommitted_stock"]) if self.inventory.get("enabled") else surplus

    def _uncommitted_total(self) -> int:
        if not math.isfinite(self.stock_horizon_days) or self.stock_horizon_days <= 0:
            raise ValueError("Stock horizon must be finite and positive")
        pool = sum(offer["stock"] for offer in self.quality_offers) if self.quality_offers else self.stock
        quantity = (self.inventory["uncommitted_stock"] if self.inventory.get("enabled")
                    else self.uncommitted_supply_per_day * self.stock_horizon_days)
        if not math.isfinite(quantity):
            raise ValueError("Uncommitted stock estimate exceeds finite bounds")
        return min(pool, max(0, math.floor(quantity + 1e-9)))

    def _uncommitted_by_quality(self) -> Dict[str, int]:
        if self.order_available_by_quality is not None:
            return dict(self.order_available_by_quality)
        return self._forecast_uncommitted_by_quality()

    def _forecast_uncommitted_by_quality(self) -> Dict[str, int]:
        if not self.quality_offers:
            return {}
        total = self._uncommitted_total()
        stock = sum(offer["stock"] for offer in self.quality_offers)
        shares = [(offer["quality"], total * offer["stock"] / stock if stock else 0.0)
                  for offer in self.quality_offers]
        result = {quality: math.floor(share) for quality, share in shares}
        # Allocate whole trade units without granting each grade the full pool.
        remainder = total - sum(result.values())
        for quality, _ in sorted(shares, key=lambda row: -(row[1] - math.floor(row[1])))[:remainder]:
            result[quality] += 1
        return result

    @property
    def uncommitted_stock(self) -> int:
        if self.order_available_by_quality is not None:
            return (sum(self.order_available_by_quality.values()) if self.stock_scope == "market"
                    else self.order_available_by_quality.get(self.stock_scope, 0))
        if self.stock_scope == "market":
            return min(self.stock, self._uncommitted_total())
        return min(self.stock, self._uncommitted_by_quality().get(self.stock_scope, 0))

    @property
    def consumer_buy_price(self) -> float:
        return self.price

    @property
    def consumer_sell_price(self) -> float:
        return self.buy_price

    @property
    def merchant_markup_pct(self) -> Optional[float]:
        return price_terms(self.price, self.buy_price)["merchant_markup_pct"]

    @property
    def price_gp(self) -> str:
        return format_coin(self.price)


def format_coin(gp: float) -> str:
    """Render a gp amount using gp/sp/cp as appropriate."""
    if gp >= 1:
        return f"{gp:,.2f} gp"
    if gp >= 0.1:
        return f"{gp * 10:,.1f} sp"
    return f"{gp * 100:,.1f} cp"
