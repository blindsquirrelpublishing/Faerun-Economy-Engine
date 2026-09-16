"""Whole-world requirements planning and finite material-backed production."""

from __future__ import annotations

import math
from collections import OrderedDict
from copy import deepcopy
from typing import Dict, List, Optional

from .models import Commodity, PriceQuote, Settlement, slugify
from .production import allocate_production
from .requirements import FOOD_COMMODITIES, final_requirements, local_resource_capacity, settlement_profile
from .world import World, get_world


def _recipe_order(commodities: Dict[str, Commodity]) -> List[str]:
    order: List[str] = []
    visiting = set()

    def visit(cid: str) -> None:
        if cid in visiting:
            raise ValueError(f"Production recipes contain a cycle at {cid}")
        if cid in order:
            return
        if cid not in commodities:
            raise ValueError(f"Missing recipe ingredient: {cid}")
        visiting.add(cid)
        for component, coefficient in commodities[cid].bom.items():
            if not math.isfinite(coefficient) or coefficient <= 0:
                raise ValueError(f"Invalid recipe coefficient: {cid} / {component}")
            visit(component)
        visiting.remove(cid)
        order.append(cid)

    for cid in commodities:
        visit(cid)
    return order


def _can_process(s: Settlement, c: Commodity) -> bool:
    from .economy import _region_allows

    return _region_allows(s, c) and (
        c.id in {"bread", "flour"}
        or s.specialties.get(c.id, 0) > 0
        or any(s.industry_level(tag) > 0 for tag in c.produced_by)
    )


def _baseline_plan(world: World) -> Dict:
    """Plan capacity before events; shocks must not conjure replacement supply."""
    from .economy import _daily_market_volume, _region_allows, supply_index

    key = (world.inventory_revision, world.config.staple_reserve_ratio, world.config.resource_reserve_ratio,
           world.config.calibrate_source_districts, world.config.service_economy)
    cached = getattr(world, "_requirements_plan", None)
    if cached is not None and cached[0] == key:
        return cached[1]
    order = _recipe_order(world.commodities)
    sectors = {sid: final_requirements(s, world.commodities.values(), include_services=world.config.service_economy)
               for sid, s in world.settlements.items()}
    profiles = {sid: settlement_profile(s, include_services=False) for sid, s in world.settlements.items()}
    services = {sid: [] for sid in world.settlements}
    if world.config.service_economy:
        from .services import service_sector_plans

        services = {sid: service_sector_plans(s, world.commodities.values(), profiles[sid])
                    for sid, s in world.settlements.items()}
    capacity = {}
    for cid in order:
        c = world.commodities[cid]
        capacity[cid] = {}
        for sid, s in world.settlements.items():
            allowed = _region_allows(s, c)
            established = (_daily_market_volume(s, c) * supply_index(world, s, c, include_events=False)
                           if allowed else 0.0)
            inferred = local_resource_capacity(s, c) if allowed else 0.0
            if cid in s.shortages:
                inferred *= 0.12
            capacity[cid][sid] = max(established, inferred)
            if c.bom and _can_process(s, c) and cid not in s.shortages:
                capacity[cid][sid] = max(capacity[cid][sid], sum(sectors[sid][cid].values()))

    # Downstream workshops create upstream orders at the place of production,
    # not at the ultimate buyer. Raw extraction remains geographically fixed.
    processing = {cid: {sid: 0.0 for sid in world.settlements} for cid in order}
    for cid in reversed(order):
        c = world.commodities[cid]
        if c.bom:
            needed = {sid: sum(sectors[sid][cid].values()) + processing[cid][sid]
                      for sid in world.settlements}
            for sid, s in world.settlements.items():
                if _can_process(s, c) and cid not in s.shortages:
                    capacity[cid][sid] = max(capacity[cid][sid], needed[sid])
            # A workshop's ability to make 100 swords is not an order for 100
            # swords. Schedule local needs plus a finite share of export orders.
            scheduled = {sid: min(quantity, needed[sid]) for sid, quantity in capacity[cid].items()}
            spare = {sid: quantity - scheduled[sid] for sid, quantity in capacity[cid].items()}
            export_orders = sum(needed[sid] - scheduled[sid] for sid in world.settlements)
            spare_total = sum(spare.values())
            if world.config.calibrate_source_districts and not spare_total:
                spare = dict(capacity[cid])
                spare_total = sum(spare.values())
            fraction = export_orders / spare_total if spare_total else 0.0
            if not world.config.calibrate_source_districts:
                fraction = min(1.0, fraction)
            capacity[cid] = {sid: quantity + spare[sid] * fraction
                             for sid, quantity in scheduled.items()}
            for component, coefficient in c.bom.items():
                for sid in world.settlements:
                    processing[component][sid] += capacity[cid][sid] * coefficient

    reserve = world.config.staple_reserve_ratio
    if not math.isfinite(reserve) or reserve < 1.0:
        raise ValueError("Staple reserve ratio must be finite and at least one")
    resource_reserve = world.config.resource_reserve_ratio
    if not math.isfinite(resource_reserve) or resource_reserve < 1.0:
        raise ValueError("Resource reserve ratio must be finite and at least one")
    factors = {}
    for cid in order:
        c = world.commodities[cid]
        staple = cid in {"grain", "salt"}
        if c.bom or not world.config.calibrate_source_districts:
            continue
        needed = sum(sum(sectors[sid][cid].values()) + processing[cid][sid]
                     for sid in world.settlements)
        existing = sum(capacity[cid].values())
        target = reserve if staple else resource_reserve
        factor = max(1.0, needed * target / existing) if existing else 1.0
        factors[cid] = factor
        capacity[cid] = {sid: quantity * factor for sid, quantity in capacity[cid].items()}
    plan = {"capacity": capacity, "sectors": sectors, "order": order, "factors": factors,
            "profiles": profiles, "services": services}
    setattr(world, "_requirements_plan", (key, plan))
    return plan


def _active_requirements(world: World, plan: Dict) -> tuple:
    from .visitors import plan_visitors
    from .water import constrain_utilities, validate_overrides, water_resources

    sectors = {sid: {cid: dict(parts) for cid, parts in goods.items()}
               for sid, goods in plan["sectors"].items()}
    beds = {sid: next((row.get("lodging_beds", row["capacity_per_day"]) for row in rows if row["id"] == "hospitality"), 0.0)
            for sid, rows in plan["services"].items()}
    travel = plan_visitors(world, beds)
    if not isinstance(world.config.water_overrides, dict):
        raise ValueError("water_overrides must map settlement IDs to water scenarios")
    overrides = {}
    for location, values in world.config.water_overrides.items():
        sid = slugify(location)
        if sid not in world.settlements:
            raise ValueError(f"Unknown water scenario location: {location}")
        if sid in overrides:
            raise ValueError(f"Duplicate water scenario location: {location}")
        overrides[sid] = validate_overrides(values)
    travel["water"] = {
        sid: water_resources(s, world.date.season, overrides.get(sid))
        for sid, s in world.settlements.items()
    }
    services = deepcopy(plan["services"])
    if world.config.service_economy:
        from .services import service_sector_plans

        for sid, s in world.settlements.items():
            visitors = travel["places"][sid]
            services[sid] = service_sector_plans(
                s, world.commodities.values(), plan["profiles"][sid],
                visitor_days=visitors["visitors_per_day"],
                overnight_visitors=visitors["overnight_visitors_per_day"],
            )
            before = {row["id"]: row for row in plan["services"][sid]}
            for row in services[sid]:
                visitor_units = visitors["visitors_per_day"] * row["visitor_units_per_person_day"]
                if row["id"] == "hospitality":
                    visitor_units += visitors["overnight_visitors_per_day"]
                if not math.isclose(row["visitor_demand_per_day"], visitor_units, rel_tol=1e-9, abs_tol=1e-9):
                    raise ValueError(f"Visitor service units do not reconcile for {sid}/{row['id']}")
                if row["id"] == "utilities":
                    constrain_utilities(
                        row, travel["water"][sid], plan["profiles"][sid],
                        visitors["resident_presence"], visitors["visitor_food_equivalents"],
                    )
                old = before[row["id"]]
                for cid in set(old["inputs_per_unit"]) | set(row["inputs_per_unit"]):
                    delta = (row["planned_per_day"] * row["inputs_per_unit"].get(cid, 0.0)
                             - old["planned_per_day"] * old["inputs_per_unit"].get(cid, 0.0))
                    amount = sectors[sid][cid].get(row["id"], 0.0) + delta
                    if amount < -1e-9:
                        raise ValueError(f"Service requirement mismatch for {sid}/{row['id']}/{cid}")
                    sectors[sid][cid][row["id"]] = max(0.0, amount)
    for sid, visitors in travel["places"].items():
        for cid, reduction in visitors["home_food_reduction"].items():
            sectors[sid][cid]["household"] = max(0.0, sectors[sid][cid].get("household", 0.0) - reduction)
        for cid, quantity in visitors["visitor_goods"].items():
            sectors[sid][cid]["visitors"] = quantity
    return sectors, services, travel


def _economy_cache(world: World) -> OrderedDict:
    cache = getattr(world, "_service_accounts_cache", None)
    if cache is None:
        cache = OrderedDict()
        setattr(world, "_service_accounts_cache", cache)
    return cache


def economic_report(settlement, world: Optional[World] = None) -> Dict:
    """Service, visitor and production accounts for one location and month."""
    world = world or get_world()
    s = world.find_settlement(settlement)
    if not world.config.expanded_requirements:
        return {"enabled": False, "industries": [], "visitors": {}, "accounts": {}, "assumptions": []}
    key = world.economy_state_key()
    if key not in _economy_cache(world):
        markets = requirements_markets(world)
        price_cache = getattr(world, "_price_cache", None)
        if price_cache is None:
            price_cache = {}
            setattr(world, "_price_cache", price_cache)
        price_cache.update({(cid,) + key: quotes for cid, quotes in markets.items()})
    return _economy_cache(world)[key][s.id]


def _steady_materials(world: World, plan: Dict):
    from .economy import _commodity_markets

    capacity = {cid: dict(values) for cid, values in plan["capacity"].items()}
    sectors, services, travel = _active_requirements(world, plan)
    for sid, s in world.settlements.items():
        for event in world.events_for(s):
            if not math.isfinite(event.supply) or not math.isfinite(event.demand):
                raise ValueError(f"Event {event.name} has non-finite supply or demand")
            for cid, c in world.commodities.items():
                if event.applies_to_commodity(c):
                    # Legacy chronicle intensities can exceed a total loss.
                    capacity[cid][sid] *= max(0.0, event.supply)
                    sectors[sid][cid] = {sector: quantity * max(0.0, event.demand)
                                         for sector, quantity in sectors[sid][cid].items()}
                    for service in services[sid]:
                        if cid in service["inputs_per_unit"]:
                            service["inputs_per_unit"][cid] *= max(0.0, event.demand)
    final = {cid: {sid: sum(sectors[sid][cid].values()) for sid in world.settlements}
             for cid in plan["order"]}
    recipes = {cid: world.commodities[cid].bom for cid in plan["order"]
               if world.commodities[cid].bom}
    quotes: Dict[str, Dict[str, PriceQuote]] = {}

    def allocate(cid, production, demand):
        costs = {sid: 0.0 for sid in world.settlements}
        for component, coefficient in recipes.get(cid, {}).items():
            for sid, quote in quotes[component].items():
                supplied = sum(row["quantity_per_day"] for row in quote.sources)
                if supplied:
                    costs[sid] += coefficient * sum(
                        row["quantity_per_day"] * row["unit_cost"] for row in quote.sources
                    ) / supplied
        quotes[cid] = _commodity_markets(
            world, world.commodities[cid],
            _material={"production": production, "demand": demand, "unit_cost": costs},
        )
        return {sid: {
            "local_per_day": quote.local_consumption_per_day,
            "imports": [row for row in quote.sources if row["supply_type"] == "import"],
            "backups": quote.backup_sources,
            "unmet_per_day": quote.unmet_demand_per_day,
            "exports_per_day": quote.exports_per_day,
        } for sid, quote in quotes[cid].items()}

    balances = allocate_production(capacity, final, recipes, allocate)
    return quotes, balances, sectors, services, travel


def requirements_markets(world: World) -> Dict[str, Dict[str, PriceQuote]]:
    """Solve every good together; all recipes share finite inputs and exporters."""
    from .economy import _quality_capability, _quality_offers
    from .seasonal_economy import inventory_enabled, inventory_epoch, inventory_quotes

    plan = _baseline_plan(world)
    seasonal = inventory_enabled(world)
    if seasonal:
        quotes, balances, sectors, services, travel = inventory_quotes(world, plan)
    else:
        quotes, balances, sectors, services, travel = _steady_materials(world, plan)
    for cid, markets in quotes.items():
        c = world.commodities[cid]
        for sid, quote in markets.items():
            balance = balances[cid][sid]
            quote.production_capacity_per_day = balance["capacity_per_day"]
            quote.production_per_day = balance["production_per_day"]
            if quote.production_per_day <= 0:
                quote.producer_gate_price = None
            quote.final_demand_per_day = balance["household_demand_per_day"]
            quote.final_consumption_per_day = balance["household_consumption_per_day"]
            quote.demand_sectors = sectors[sid][cid]
            if seasonal:
                quote.consumption_sectors = dict(balance["consumption_sectors"])
            elif world.config.seasonal_inventory:
                from .seasonality import seasonal_profile

                quote.seasonality = seasonal_profile(c, world.settlements[sid], world.date)
                quote.inventory = {"enabled": False, "epoch": str(inventory_epoch(world)),
                                   "reason": "Before the inventory epoch; historical steady-state estimate"}
                quote.notes.append(quote.inventory["reason"])
            # Keep legacy final-use accounting fields available to API clients.
            quote.household_demand_per_day = quote.final_demand_per_day
            quote.household_consumption_per_day = quote.final_consumption_per_day
            quote.processing_demand_per_day = balance["processing_demand_per_day"]
            quote.processing_consumption_per_day = balance["processing_consumption_per_day"]
            quote.demand_per_day = quote.final_demand_per_day + quote.processing_demand_per_day
            quote.material_closing_stock = balance["closing_stock"]
            quote.production_inputs = [
                {**row, "unit": world.commodities[row["commodity"]].unit}
                for row in balance["inputs"]
            ]
            quote.factors["hinterland_capacity_multiplier"] = plan["factors"].get(cid, 1.0)
            quote.factors["expanded_requirements"] = 1.0
            stock_days = (1.0 if seasonal else
                          min(10.0, world.config.fresh_bread_days) if cid == "bread" else 10.0)
            quote.stock_horizon_days = stock_days
            quote.stock = (max(0, math.floor(quote.material_closing_stock + 1e-9)) if seasonal else
                           max(0, round((quote.final_consumption_per_day + quote.material_closing_stock) * stock_days)))
            capability = max((_quality_capability(world.settlements[row["source_id"]], c)
                              for row in quote.sources), default=0.0)
            quote.quality_offers = _quality_offers(quote.price, quote.buy_price, quote.stock, capability)
            if (quote.stock == 0 and quote.availability != "unavailable"
                    and not (seasonal and quote.production_per_day > 0
                             and quote.final_consumption_per_day >= quote.final_demand_per_day)):
                quote.availability = "rare"
            if quote.production_inputs:
                quote.notes.append(
                    f"input-backed production: {quote.production_per_day:.3f} of "
                    f"{quote.production_capacity_per_day:.3f} {c.unit}/day capacity"
                )
    from .accounts import deliver_services, local_accounts
    from .water import DOMESTIC_GALLONS_PER_PERSON, water_balance

    delivered = deliver_services(world, quotes, services)
    cache = _economy_cache(world)
    key = world.economy_state_key()
    cache[key] = local_accounts(world, quotes, delivered, travel)
    for sid, entry in cache[key].items():
        utility = next((row for row in delivered[sid] if row["id"] == "utilities"), None)
        if utility is not None:
            municipal_capacity = utility["labor_capacity_per_day"] * DOMESTIC_GALLONS_PER_PERSON
            municipal_delivery = utility["delivered_per_day"] * DOMESTIC_GALLONS_PER_PERSON
        else:
            reference = next(row for row in plan["profiles"][sid]["service_requirements"]
                             if row["scope"] == "municipal_water_reference")
            municipal_capacity = reference["local_capacity_per_day"] * travel["water"][sid]["municipal_collection_multiplier"]
            municipal_delivery = municipal_capacity
        presence = travel["places"][sid]
        entry["water"] = water_balance(
            travel["water"][sid], presence["resident_presence"],
            presence["visitor_food_equivalents"], municipal_capacity, municipal_delivery,
        )
        entry["water"]["municipal_delivery_basis"] = (
            "Input-backed complete municipal-service equivalents"
            if utility is not None else "Staffing estimate; service-economy accounting disabled"
        )
    cache.move_to_end(key)
    while len(cache) > 16:
        cache.popitem(last=False)
    return quotes


def location_requirements(settlement, world: Optional[World] = None) -> Dict:
    """Expose the same requirements and allocations that drive market prices."""
    from .economy import _commodity_markets

    world = world or get_world()
    s = world.find_settlement(settlement)
    profile = settlement_profile(s, include_services=world.config.service_economy and world.config.expanded_requirements)
    if not world.config.expanded_requirements:
        return {"enabled": False, "model": "Legacy market model", "date": str(world.date),
                "profile": profile, "materials": [], "summary": {}, "assumptions": []}
    economy = economic_report(s.id, world)
    from .trading import claims_for, tradable_quote
    claims = claims_for(world)
    rows = []
    for cid, c in world.commodities.items():
        markets = _commodity_markets(world, c)
        q = tradable_quote(world, markets[s.id], claims)
        destinations = [
            {"destination_id": sid, "destination": world.settlements[sid].name,
             "quantity_per_day": source["quantity_per_day"]}
            for sid, quote in markets.items() for source in quote.sources
            if source["supply_type"] == "import" and source["source_id"] == s.id
        ]
        rows.append({
            "commodity_id": cid, "commodity": c.name, "category": c.category, "unit": c.unit,
            "final_demand_per_day": q.final_demand_per_day, "sectors": q.demand_sectors,
            "consumption_sectors": q.consumption_sectors,
            "processing_demand_per_day": q.processing_demand_per_day,
            "demand_per_day": q.demand_per_day, "capacity_per_day": q.production_capacity_per_day,
            "production_per_day": q.production_per_day,
            "local_use_per_day": q.local_consumption_per_day,
            "import_need_per_day": q.import_need_per_day,
            "surplus_per_day": q.exportable_supply_per_day,
            "uncommitted_supply_per_day": q.uncommitted_supply_per_day,
            "uncommitted_stock": q.uncommitted_stock,
            "stock_horizon_days": q.stock_horizon_days,
            "order_claimed_stock": q.order_claimed_stock,
            "order_supply_window": q.order_supply_window,
            "imports_per_day": q.imports_per_day, "exports_per_day": q.exports_per_day,
            "unmet_per_day": q.unmet_demand_per_day,
            "consumption_per_day": q.final_consumption_per_day + q.processing_consumption_per_day,
            "final_consumption_per_day": q.final_consumption_per_day,
            "closing_stock": q.material_closing_stock,
            "inventory": q.inventory, "seasonality": q.seasonality,
            "inputs": q.production_inputs, "sources": q.sources,
            "export_destinations": destinations,
            "hinterland_capacity_multiplier": q.factors.get("hinterland_capacity_multiplier", 1.0),
        })
    summary = {
        "goods_with_import_need": sum(row["import_need_per_day"] > 1e-6 for row in rows),
        "goods_with_shortfall": sum(row["unmet_per_day"] > 1e-6 for row in rows),
        "goods_with_surplus": sum(row["surplus_per_day"] > 1e-6 for row in rows),
        "import_weight_lb_per_day": sum(row["imports_per_day"] * world.commodities[row["commodity_id"]].weight for row in rows),
        "export_weight_lb_per_day": sum(row["exports_per_day"] * world.commodities[row["commodity_id"]].weight for row in rows),
        "food_demand_lb_per_day": sum(
            (row["sectors"].get("household", 0.0) + row["sectors"].get("visitors", 0.0)) * world.commodities[row["commodity_id"]].weight
            for row in rows if row["commodity_id"] in FOOD_COMMODITIES
        ),
        "food_consumption_lb_per_day": sum(
            (row["consumption_sectors"].get("household", 0.0) + row["consumption_sectors"].get("visitors", 0.0))
            * world.commodities[row["commodity_id"]].weight
            for row in rows if row["commodity_id"] in FOOD_COMMODITIES
        ),
    }
    visitors = economy["visitors"]
    net_presence = visitors["visitor_food_equivalents"] - visitors["outbound_food_equivalents"]
    for service in profile.get("service_requirements", []):
        baseline = service["required_per_day"]
        service["resident_requirement_per_day"] = baseline
        service["visitor_requirement_increment_per_day"] = baseline / s.population * net_presence if s.population else 0.0
        service["required_per_day"] += service["visitor_requirement_increment_per_day"]
        service["unmet_per_day"] = max(0.0, service["required_per_day"] - service["local_capacity_per_day"])
        service["basis"] += " The displayed requirement includes net visitor-day demand; capacity is unchanged."
    profile["reference_period"] = "Fixed population and staffing; material and municipal demand include the selected month's visitors."
    profile["output_establishments"] = _output_establishments(world, s, rows, visitors)
    return {
        "enabled": True, "model": "Estimated daily requirements and finite supply",
        "date": str(world.date), "profile": profile, "materials": rows, "summary": summary,
        "economy": economy, "water": economy["water"],
        "assumptions": [
            "Demographics, establishments and local resource capacities are estimates, not a canonical census.",
            "All material flows are catalogue trade units per day. Equipment stocks are amortized into daily replacement orders.",
            "Residents include soldiers, militia and mages; their ordinary food is not counted twice.",
            "Domestic visits move variable food demand from origins to destinations and add hospitality/service pressure. Baseline source capacity is not recalibrated to erase a monthly visitor surge.",
            "Final-use demand is reserved before workshop inputs; competing workshops share available ingredients proportionally.",
            "Workshops order inputs where production occurs. Outputs are limited by the least available ingredient.",
            "With source districts enabled, export manufacturing orders are apportioned across existing capable producers; workshop counts estimate the facilities required, not an independently surveyed labor ceiling. Planned capacity is scheduled output, not idle maximum machinery capacity.",
            "Local needs are reserved first; finite export surplus is assigned by delivered cost, then travel time and stable location IDs.",
            "Import need and surplus are before trade; allocated imports and exports are commitments, not additional production.",
            "Unmet demand includes unfilled workshop plans. Unused ingredient reservations remain in closing stock, not a second export pass.",
            "When calibrate_source_districts is enabled (default), existing eligible raw producers represent supporting production districts sized to baseline world needs plus reserves, before events. No new source location or rare deposit is created.",
            "Per-material hinterland multipliers disclose that inferred source-district scale. Grain/salt uses staple_reserve_ratio (default 1.15); other raw goods use resource_reserve_ratio (default 1.10). This is an equilibrium scenario, not a land or workforce survey. Disable calibrate_source_districts for conservative footprints.",
            "Baseline population and growth estimates are fixed; the selected month applies events and prices, not a historical census.",
            "Legacy event intensities below zero mean complete cessation, not negative production or consumption.",
            ("Daily inventories carry forward from an explicit epoch; seed stocks represent prior harvest reserves. "
             "Storage spoilage and overflow are physical losses. Imports remain same-day steady-state deliveries, "
             "not scheduled shipments. Manufacturing labor ceilings are not independently surveyed."
             if any(row["inventory"].get("enabled") for row in rows) else
             "Historical/legacy stock figures are steady-state estimates, not persistent inventory. "
             "Shipment arrival schedules, manufacturing labor ceilings and physical spoilage losses are not simulated."),
        ],
    }


def _output_establishments(world: World, s: Settlement, materials: List[Dict],
                           visitors: Optional[Dict] = None) -> List[Dict]:
    """Workshop equivalents for planned/actual volumes, not a second workforce."""
    by_id = {row["commodity_id"]: row for row in materials}
    workshops = (
        ("Bakeries", ("bread",), 500.0, False),
        ("Flour mills", ("flour",), 20.0, False),
        ("Butchers (meat handling)", ("meat_fresh",), 160.0, True),
        ("Blacksmiths and toolmakers", ("nails", "tools_carpenter", "plow"), 60.0, True),
        ("Weapon makers", ("dagger", "sword", "axe_battle", "spear", "bow_short",
                           "bow_long", "crossbow", "arrows"), 30.0, True),
        ("Armorers", ("armor_leather", "armor_chain", "armor_plate", "shield"), 40.0, True),
        ("Sawmills", ("planks",), 3000.0, True),
    )
    result = []
    for name, ids, throughput, by_weight in workshops:
        selected = [by_id[cid] for cid in ids if cid in by_id]
        if not selected:
            continue
        handling = name.startswith("Butchers")
        planned = sum(row["demand_per_day" if handling else "capacity_per_day"]
                      * (world.commodities[row["commodity_id"]].weight if by_weight else 1)
                      for row in selected)
        actual = sum(row["consumption_per_day" if handling else "production_per_day"]
                     * (world.commodities[row["commodity_id"]].weight if by_weight else 1)
                     for row in selected)
        unit = "lb" if by_weight else world.commodities[selected[0]["commodity_id"]].unit
        result.append({
            "name": name, "count": math.ceil(planned / throughput),
            "active_equivalents": actual / throughput,
            "planned_per_day": planned, "actual_per_day": actual, "unit": unit,
            "throughput_per_day": throughput,
            "basis": (
                f"Estimated facility equivalents at {throughput:g} {unit}/facility-day; "
                + ("handles final and preserving-workshop meat needs, including imports."
                   if handling else "planned capacity versus input-backed local output.")
                + " Not additional workers, a census, or a labor constraint."
            ),
        })
    food = [row for row in materials if row["commodity_id"] in FOOD_COMMODITIES]
    required = sum((row["sectors"].get("household", 0.0) + row["sectors"].get("visitors", 0.0))
                   * world.commodities[row["commodity_id"]].weight for row in food)
    consumed = sum((row["consumption_sectors"].get("household", 0.0) + row["consumption_sectors"].get("visitors", 0.0))
                   * world.commodities[row["commodity_id"]].weight for row in food)
    visitor_days = visitors["visitor_food_equivalents"] if visitors else 0.0
    resident_days = visitors["resident_presence"] if visitors else s.population
    meals = resident_days * .15 + visitor_days * .80
    supported = meals * min(1.0, consumed / required) if required else 0.0
    result.append({
        "name": "Taverns and cookshops", "count": math.ceil(meals / 80),
        "active_equivalents": supported / 80,
        "planned_per_day": meals, "actual_per_day": supported, "unit": "meal",
        "throughput_per_day": 80.0,
        "basis": "15% of present residents and 80% of visitor food-days buy one meal/day at 80 meals/facility-day; meal equivalents "
                 "supported in proportion to supplied food mass, not a nutritional simulation. "
                 "Already part of household food demand, not additional consumption or workers.",
    })
    return result
