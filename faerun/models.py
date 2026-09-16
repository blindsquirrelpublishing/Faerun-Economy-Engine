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


# ---------------------------------------------------------------------------
# Commodities
# ---------------------------------------------------------------------------


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
    return Commodity(
        id=id,
        name=name,
        category=category,
        base_price=float(base_price),
        unit=unit,
        weight=float(weight),
        produced_by=_parse_tags(produced_by),
        demand=float(demand),
        luxury=float(luxury),
        perishable=float(perishable),
        demand_traits=dict(traits or {}),
        season=dict(season or {}),
        substitutes=_parse_tags(substitutes),
        requires=_parse_tags(requires),
        description=description,
        production_profile=list(production_profile or []),
        demand_profile=list(demand_profile or []),
        regional_production_profiles={key: list(values) for key, values in (regional_production_profiles or {}).items()},
        storage_days=storage_days,
        storage_loss=storage_loss,
        reserve_days=reserve_days,
    )


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

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["size"] = self.size
        data.pop("population_basis")
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

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["satellites"] = [
            location for location in self.locations if location != self.headquarters
        ]
        return data


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
