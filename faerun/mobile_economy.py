"""Read-only provisioning and stock assessments for mobile communities."""

from __future__ import annotations

import math
from typing import Dict

from .economy import price_for
from .living import living_standard, per_person_daily_requirements
from .world import World


STOCK_UNITS = {
    "preserved_food_lb": "lb",
    "fodder_lb": "lb",
    "fresh_water_gallons": "gallon",
    "firewood_lb": "lb",
    "cloth_bolts": "bolt",
    "small_tools": "tool",
    "harness_sets": "set",
    "herb_cases": "case",
    "lamp_oil_flasks": "flask",
    "trade_cargo_lb": "lb",
}
CATALOGUE_STOCK = {"lamp_oil_flasks": "lamp_oil"}


def _quantity(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite nonnegative number")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be a finite nonnegative number")
    return float(value)


def mobile_economic_report(location, world: World) -> Dict:
    """Estimate costs without adding a settlement, booking goods or spending stock."""
    company = world.find_mobile_location(location)
    profile = company.profile(world)
    date = world.date
    host = profile["position"]["host"]
    prices = {}

    def reference_price(cid):
        if cid not in prices:
            commodity = world.commodities[cid]
            if host:
                quote = price_for(host["id"], cid, world=world)
                prices[cid] = {
                    "unit_price_gp": quote.price,
                    "merchant_bid_gp": quote.buy_price,
                    "availability": quote.availability,
                    "uncommitted_stock": quote.uncommitted_stock,
                }
            else:
                prices[cid] = {
                    "unit_price_gp": commodity.base_price,
                    "merchant_bid_gp": None,
                    "availability": "no market access while travelling",
                    "uncommitted_stock": None,
                }
        return dict(prices[cid])

    household = []
    for cid, amount in per_person_daily_requirements(company.wealth).items():
        daily = _quantity(amount * company.population, f"{cid} daily requirement")
        commodity = world.commodities.get(cid)
        price = reference_price(cid) if commodity else {
            "unit_price_gp": None, "merchant_bid_gp": None,
            "availability": "commodity absent from this world's catalogue",
            "uncommitted_stock": None,
        }
        household.append({
            "commodity_id": cid,
            "commodity": commodity.name if commodity else cid,
            "unit": commodity.unit if commodity else None,
            "per_person_per_day": amount,
            "quantity_per_day": daily,
            "quantity_per_tenday": daily * 10,
            **price,
            "cost_gp_per_day": (
                daily * price["unit_price_gp"]
                if price["unit_price_gp"] is not None else None
            ),
        })

    inventory = []
    for key, amount in profile["inventory"].items():
        quantity = _quantity(amount, f"inventory[{key}]")
        cid = CATALOGUE_STOCK.get(key, key)
        commodity = world.commodities.get(cid)
        price = reference_price(cid) if commodity else None
        inventory.append({
            "id": key,
            "name": key.replace("_", " ").capitalize(),
            "quantity": quantity,
            "unit": commodity.unit if commodity else STOCK_UNITS.get(key, "unspecified"),
            "commodity_id": cid if commodity else None,
            "unit_price_gp": price["unit_price_gp"] if price else None,
            "replacement_value_gp": quantity * price["unit_price_gp"] if price else None,
            "valuation_note": (
                "Catalogue-matched quantity at the report's reference price; not cash."
                if commodity else
                "Unvalued: commodity identity or trade-unit conversion is unspecified."
            ),
        })

    requirements = profile["requirements"]
    coverage_specs = (
        ("preserved_food_lb", "Preserved food", "lb", requirements["food_lb_per_day"]),
        ("fodder_lb", "Fodder", "lb", requirements["fodder_lb_per_day"]),
        ("fresh_water_gallons", "Domestic and animal water", "gallon", {
            "low": requirements["total_water_gallons_per_day"],
            "high": requirements["total_water_gallons_per_day"],
        }),
        ("firewood_lb", "Firewood", "lb", requirements["fuel_lb_per_day"]),
    )
    supplies = []
    for key, name, unit, demand in coverage_specs:
        stock = profile["inventory"].get(key)
        if stock is not None:
            stock = _quantity(stock, key)
        low = _quantity(demand["low"], f"{key} low requirement")
        high = _quantity(demand["high"], f"{key} high requirement")
        if low > high:
            raise ValueError(f"{key} low requirement cannot exceed high requirement")
        supplies.append({
            "id": key, "name": name, "unit": unit, "stock": stock,
            "daily_need": {"low": low, "high": high},
            "days_of_cover": {
                "low": stock / high if stock is not None and high else None,
                "high": stock / low if stock is not None and low else None,
            },
            "additional_for_tenday": {
                "low": max(0.0, low * 10 - stock) if stock is not None else None,
                "high": max(0.0, high * 10 - stock) if stock is not None else None,
            },
            "basis": (
                "Authored starting stores, without resupply, collection, grazing or losses; "
                "not a replayed on-hand balance."
            ),
        })

    priced_costs = [row["cost_gp_per_day"] for row in household
                    if row["cost_gp_per_day"] is not None]
    priced_inventory = [row["replacement_value_gp"] for row in inventory
                        if row["replacement_value_gp"] is not None]
    daily_cost = math.fsum(priced_costs) if priced_costs else None
    complete = len(priced_costs) == len(household)
    limiting = min(
        (row for row in supplies if row["days_of_cover"]["low"] is not None),
        key=lambda row: row["days_of_cover"]["low"], default=None,
    )
    assumptions = [
        "This is a read-only economic estimate, not a purchase, reservation or cash ledger.",
        "Household costs reuse the wealth-sensitive 14-good living-standard benchmark. "
        "They are not a fitted caravan ration mix and are not added to the travel-food weights.",
        "The household benchmark is partial operating cost: animal feed, water, firewood, "
        "road tolls, wages, camp fees, maintenance and service inputs are not separately costed.",
        "Unit prices are linear estimates for standard goods, not bulk quotations or confirmed supply.",
        "Stores are authored starting quantities; inspecting later dates does not consume them.",
        "Water cover includes domestic and horse needs. Grazing and water collection are not guaranteed.",
        "Unidentified stock is excluded from the priced subtotal, not valued at zero. "
        "Unspecified trade cargo may overlap itemized stock; no total cargo weight is inferred.",
        "No service sales, manufacturing, imports, exports or payments are executed for this company. "
        "Revenue, profit and gross local product are therefore unavailable.",
    ]
    if not complete:
        assumptions.append("Some household commodities are absent; cost figures are priced subtotals only.")
    if not host:
        assumptions.append(
            "In transit, catalogue base prices are reference values only. "
            "They do not provide access to a destination or origin market."
        )
    return {
        "schema_version": 1,
        "report_type": "mobile_economic_report",
        "calendar": "Harptos",
        "date": profile["date"],
        "season": date.season,
        "follows_real_date": world.follows_real_date,
        "date_iso": f"{date.year:04d}-{date.month:02d}-{date.day:02d}",
        "world_state": {
            "seed": world.config.seed,
            "revision": world.revision,
            "seasonal_inventory": world.config.seasonal_inventory,
        },
        "location": profile,
        "economy": {
            "enabled": True,
            "model": "mobile_provisioning_estimate",
            "currency": "gp",
            "valuation": {
                "basis": "host_market" if host else "catalogue_reference",
                "market": host,
                "quality": "standard",
                "description": (
                    f"Current consumer purchase prices in {host['name']}."
                    if host else "Catalogue base prices; no trading access while travelling."
                ),
            },
            "living_standard": living_standard(company.wealth),
            "household_requirements": household,
            "supplies": supplies,
            "inventory": inventory,
            "services": [
                {"name": name, "delivery": "not simulated", "revenue_gp_per_day": None}
                for name in company.services
            ],
            "accounts": {
                "priced_household_cost_gp_per_day": daily_cost,
                "priced_household_cost_gp_per_tenday": (
                    daily_cost * 10 if daily_cost is not None else None
                ),
                "household_cost_complete": complete,
                "priced_household_items": len(priced_costs),
                "unpriced_household_items": len(household) - len(priced_costs),
                "priced_inventory_replacement_value_gp": (
                    math.fsum(priced_inventory) if priced_inventory else None
                ),
                "priced_inventory_items": len(priced_inventory),
                "unpriced_inventory_items": len(inventory) - len(priced_inventory),
                "revenue_gp_per_day": None,
                "profit_gp_per_day": None,
                "gross_local_product_gp_per_day": None,
                "gross_local_product_status": "not_calculated",
                "goods_imports_gp_per_day": None,
                "goods_exports_gp_per_day": None,
            },
            "glp_methodology": {
                "definition": (
                    "Value of goods and services produced less intermediate goods "
                    "and services consumed in production."
                ),
                "potential_contributions": [
                    "Value added through crafting and repairs",
                    "Performances and entertainment",
                    "Animal care, healing and other paid services",
                    "Trading margins, not the full resale value of purchased cargo",
                ],
                "missing_inputs": [
                    "Quantities of goods produced",
                    "Quantities of services delivered",
                    "Output valuations and trading margins",
                    "Intermediate goods and services consumed",
                ],
                "interpretation": (
                    "Null means not calculated, not zero. Inventory values and household "
                    "provisioning costs are not GLP."
                ),
            },
            "limiting_supply": (
                {"id": limiting["id"], "name": limiting["name"],
                 "days_of_cover": limiting["days_of_cover"]["low"]}
                if limiting else None
            ),
            "assumptions": assumptions,
        },
    }
