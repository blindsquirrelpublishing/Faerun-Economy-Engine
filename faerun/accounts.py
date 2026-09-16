"""Material-backed services and explicitly valued local production/trade accounts."""

from __future__ import annotations

from typing import Dict

from .models import PriceQuote
from .world import World


CAPITAL_GOODS = frozenset({
    "tools_carpenter", "cart", "wagon", "plow", "saddle", "ship_boat",
    "horse_riding", "warhorse", "mule", "ox", "lantern", "fishing_net",
})


def service_consumption(plan: Dict, available: Dict):
    coefficients = plan["inputs_per_unit"]
    allocated = {cid: min(available.get(cid, 0.0), plan["planned_per_day"] * coefficient)
                 for cid, coefficient in coefficients.items()}
    delivered = min(
        [plan["planned_per_day"]]
        + [allocated[cid] / coefficient for cid, coefficient in coefficients.items() if coefficient > 0]
    )
    consumed = {cid: min(allocated[cid], delivered * coefficient)
                for cid, coefficient in coefficients.items()}
    return delivered, allocated, consumed


def deliver_services(world: World, markets: Dict[str, Dict[str, PriceQuote]], plans: Dict) -> Dict:
    """Reserve final-use shares, execute services, and release unused inputs."""
    for quotes in markets.values():
        for q in quotes.values():
            if q.inventory.get("enabled"):
                continue
            fraction = q.final_consumption_per_day / q.final_demand_per_day if q.final_demand_per_day else 0.0
            q.consumption_sectors = {sector: amount * fraction for sector, amount in q.demand_sectors.items()}
    result = {sid: [] for sid in world.settlements}
    for sid, sectors in plans.items():
        for plan in sectors:
            coefficients = plan["inputs_per_unit"]
            delivered, allocated, consumption = service_consumption(
                plan, {cid: markets[cid][sid].consumption_sectors.get(plan["id"], 0.0)
                       for cid in coefficients},
            )
            inputs = []
            for cid, coefficient in coefficients.items():
                q = markets[cid][sid]
                consumed = consumption[cid]
                released = allocated[cid] - consumed
                # Seasonal quotes already include the physical ledger's service
                # releases. Reporting must not spend or credit those inputs again.
                if not q.inventory.get("enabled"):
                    q.consumption_sectors[plan["id"]] = q.consumption_sectors.get(plan["id"], 0.0) - released
                    q.final_consumption_per_day -= released
                    q.household_consumption_per_day = q.final_consumption_per_day
                    q.material_closing_stock += released
                inputs.append({
                    "commodity_id": cid, "commodity": world.commodities[cid].name,
                    "unit": world.commodities[cid].unit,
                    "required_per_day": plan["planned_per_day"] * coefficient,
                    "reserved_per_day": allocated[cid], "consumed_per_day": consumed,
                    "capital_good": cid in CAPITAL_GOODS,
                })
            result[sid].append({
                **plan, "delivered_per_day": delivered,
                "unmet_per_day": max(0.0, plan["demand_per_day"] - delivered),
                "service_output_gp_per_day": delivered * plan["fee_gp_per_unit"],
                "inputs": inputs,
            })
    return result


def local_accounts(world: World, markets: Dict[str, Dict[str, PriceQuote]],
                   industries: Dict, travel: Dict) -> Dict:
    """Book matched counterparties; do not add sales or visitor receipts to GLP."""
    output = {}
    for sid, s in world.settlements.items():
        goods_output = sum(quotes[sid].production_per_day * world.commodities[cid].base_price
                           for cid, quotes in markets.items())
        goods_inputs = sum(
            ingredient["consumed_per_day"] * world.commodities[ingredient["commodity"]].base_price
            for quotes in markets.values() for ingredient in quotes[sid].production_inputs
        )
        service_output = sum(row["service_output_gp_per_day"] for row in industries[sid])
        service_inputs = sum(
            item["consumed_per_day"] * world.commodities[item["commodity_id"]].base_price
            for row in industries[sid] for item in row["inputs"] if not item["capital_good"]
        )
        capital = sum(
            item["consumed_per_day"] * world.commodities[item["commodity_id"]].base_price
            for row in industries[sid] for item in row["inputs"] if item["capital_good"]
        )
        glp = goods_output - goods_inputs + service_output - service_inputs
        visitor = {k: v for k, v in travel["places"][sid].items()
                   if k not in {"visitor_goods", "home_food_reduction"}}
        visitor.update({
            "visitor_goods_demand_weight_lb_per_day": sum(
                quotes[sid].demand_sectors.get("visitors", 0.0) * world.commodities[cid].weight
                for cid, quotes in markets.items()
            ),
            "visitor_goods_supplied_weight_lb_per_day": sum(
                quotes[sid].consumption_sectors.get("visitors", 0.0) * world.commodities[cid].weight
                for cid, quotes in markets.items()
            ),
            "visitor_spending_gp_per_day": 0.0, "visitor_spending_abroad_gp_per_day": 0.0,
            "net_visitor_receipts_gp_per_day": 0.0,
            "segments": [], "origins": [], "destinations": [],
        })
        output[sid] = {
            "enabled": True, "industries": industries[sid], "visitors": visitor,
            "accounts": {
                "currency": "gp",
                "goods_output_gp_per_day": goods_output,
                "goods_intermediate_gp_per_day": goods_inputs,
                "goods_value_added_gp_per_day": goods_output - goods_inputs,
                "service_output_gp_per_day": service_output,
                "service_intermediate_gp_per_day": service_inputs,
                "service_capital_purchases_gp_per_day": capital,
                "service_value_added_gp_per_day": service_output - service_inputs,
                "gross_local_product_gp_per_day": glp,
                "gross_local_product_gp_per_year": glp * 365,
                "glp_per_resident_gp_per_year": glp * 365 / s.population if s.population else None,
                "goods_exports_gp_per_day": 0.0, "goods_imports_gp_per_day": 0.0,
                "goods_trade_balance_gp_per_day": 0.0,
                "visitor_receipts_gp_per_day": 0.0, "resident_travel_spending_gp_per_day": 0.0,
                "net_visitor_receipts_gp_per_day": 0.0, "external_balance_gp_per_day": 0.0,
                "unassigned_inbound_freight_gp_per_day": 0.0,
                "trade_valuation_basis": "Matched current producer-gate prices plus export margin; freight, retail markups and destination tariffs excluded.",
                "output_valuation_basis": "Constant catalogue commodity prices and baseline service valuations; output minus consumed intermediate inputs. Public services are imputed, not necessarily fee income.",
            },
            "assumptions": accounting_assumptions() + travel["assumptions"],
        }
    for quotes in markets.values():
        for destination_id, q in quotes.items():
            for source in q.sources:
                if source["supply_type"] != "import":
                    continue
                value = source["quantity_per_day"] * source["producer_unit_cost"]
                output[source["source_id"]]["accounts"]["goods_exports_gp_per_day"] += value
                output[destination_id]["accounts"]["goods_imports_gp_per_day"] += value
                output[destination_id]["accounts"]["unassigned_inbound_freight_gp_per_day"] += (
                    source["quantity_per_day"] * max(0.0, source["unit_cost"] - source["producer_unit_cost"])
                )

    segment_rows = {sid: {} for sid in output}
    origin_rows = {sid: {} for sid in output}
    destination_rows = {sid: {} for sid in output}
    for flow in travel["flows"]:
        origin_id, destination_id = flow["origin_id"], flow["destination_id"]
        destination = output[destination_id]
        price = 0.0
        for cid, requested in flow["goods_demand"].items():
            total = travel["places"][destination_id]["visitor_goods"].get(cid, 0.0)
            if total:
                q = markets[cid][destination_id]
                price += q.consumption_sectors.get("visitors", 0.0) * requested / total * q.price
        for service in industries[destination_id]:
            if not service["market_service"]:
                continue
            units = flow["visitors_per_day"] * service["visitor_units_per_person_day"]
            if service["id"] == "hospitality" and flow["overnight"]:
                units += flow["visitors_per_day"]
            if service["demand_per_day"]:
                price += service["service_output_gp_per_day"] * units / service["demand_per_day"]
        destination["accounts"]["visitor_receipts_gp_per_day"] += price
        output[origin_id]["accounts"]["resident_travel_spending_gp_per_day"] += price
        segment = segment_rows[destination_id].setdefault(flow["segment_id"], {
            "id": flow["segment_id"], "name": flow["segment"],
            "visitors_per_day": 0.0, "arrivals_per_month": 0.0,
            "average_nights": 0.0, "spending_gp_per_day": 0.0,
        })
        segment["visitors_per_day"] += flow["visitors_per_day"]
        segment["arrivals_per_month"] += flow["arrivals_per_month"]
        segment["average_nights"] += flow["arrivals_per_month"] * flow["average_nights"]
        segment["spending_gp_per_day"] += price
        for ledger, key, name in (
            (origin_rows[destination_id], origin_id, world.settlements[origin_id].name),
            (destination_rows[origin_id], destination_id, world.settlements[destination_id].name),
        ):
            row = ledger.setdefault(key, {"id": key, "name": name, "visitors_per_day": 0.0, "spending_gp_per_day": 0.0})
            row["visitors_per_day"] += flow["visitors_per_day"]
            row["spending_gp_per_day"] += price
    for sid, entry in output.items():
        a = entry["accounts"]
        a["goods_trade_balance_gp_per_day"] = a["goods_exports_gp_per_day"] - a["goods_imports_gp_per_day"]
        a["net_visitor_receipts_gp_per_day"] = a["visitor_receipts_gp_per_day"] - a["resident_travel_spending_gp_per_day"]
        a["external_balance_gp_per_day"] = a["goods_trade_balance_gp_per_day"] + a["net_visitor_receipts_gp_per_day"]
        for segment in segment_rows[sid].values():
            segment["average_nights"] /= segment["arrivals_per_month"] or 1.0
        entry["visitors"].update({
            "visitor_spending_gp_per_day": a["visitor_receipts_gp_per_day"],
            "visitor_spending_abroad_gp_per_day": a["resident_travel_spending_gp_per_day"],
            "net_visitor_receipts_gp_per_day": a["net_visitor_receipts_gp_per_day"],
            "segments": sorted(segment_rows[sid].values(), key=lambda row: row["id"]),
            "origins": sorted(origin_rows[sid].values(), key=lambda row: -row["visitors_per_day"]),
            "destinations": sorted(destination_rows[sid].values(), key=lambda row: -row["visitors_per_day"]),
        })
    return output


def accounting_assumptions() -> list[str]:
    return [
        "GLP is an estimated gross-local-product proxy: goods and service output less intermediate inputs, not gross sales, household income, government revenue, or profit.",
        "The material table's final-demand column means non-manufacturing orders, including service-provider inputs. It is not the national-accounts definition of final expenditure; service intermediate inputs are deducted separately in GLP.",
        "Goods output and intermediate inputs use constant catalogue prices. Service output uses baseline fee/replacement valuations; nonmarket public/religious services are imputed, not assumed cash payments.",
        "Named durable service assets are capital acquisitions, not intermediate inputs deducted from gross product; depreciation is not deducted. The material ledger records acquisitions but holds no persistent asset inventory.",
        "Annual GLP and per-resident figures annualize the current day by 365; they are not a sum of historical months. Source-district extrapolation makes this a location-and-hinterland estimate, not a city-boundary census.",
        "A shipment has the identical producer-gate invoice on its exporter's and importer's books. Freight and tariffs are separate unassigned costs, not fictitious local output or an unmatched trade deficit.",
        "Visitor receipts price only allocated visitor goods and delivered market services. The same amount is charged to the visitor's origin; domestic visits redistribute gold rather than create it.",
        "Travel receipts include on-site purchases by nonresidents. They are reported separately from merchandise shipments and are NOT added again to GLP: the goods and services are already valued in output.",
        "Merchandise balance plus net visitor receipts is a partial external-flow balance, not a complete balance of payments. Investment, remittances, finance, budgets, cash inventories and other service exports are not simulated.",
        "No wealth, population or gold balance is mutated when a report is read. Lack of inputs reduces service delivery; unused input reservations remain in closing material rather than vanishing.",
    ]
