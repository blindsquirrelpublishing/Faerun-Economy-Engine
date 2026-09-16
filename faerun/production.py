"""Daily material accounting for a configured acyclic recipe chain."""

import math

def allocate_production(capacity, household_demand, recipes, allocate):
    """Allocate inputs upstream first; reserve households before processing."""
    for values in (capacity, household_demand):
        if any(not math.isfinite(amount) or amount < 0 for places in values.values() for amount in places.values()):
            raise ValueError("Production and demand must be finite non-negative quantities")
    order = []
    visiting = set()

    def visit(commodity):
        if commodity in visiting:
            raise ValueError("Production recipes must not contain cycles")
        if commodity in order:
            return
        if commodity not in capacity or commodity not in household_demand:
            raise ValueError(f"Missing material balance for {commodity}")
        visiting.add(commodity)
        for component, quantity in recipes.get(commodity, {}).items():
            if not math.isfinite(quantity) or quantity <= 0:
                raise ValueError("Recipe quantities must be positive")
            visit(component)
        visiting.remove(commodity)
        order.append(commodity)

    for commodity in capacity:
        visit(commodity)
    places = sorted(set().union(*(values.keys() for values in household_demand.values())))
    processing_demand = {commodity: {place: 0.0 for place in places} for commodity in order}
    for product, recipe in recipes.items():
        for component, quantity in recipe.items():
            for place in places:
                processing_demand[component][place] += capacity[product].get(place, 0.0) * quantity

    result = {}
    reservations = {}
    for commodity in order:
        production = {}
        for place in places:
            planned = capacity[commodity].get(place, 0.0)
            bounds = [reservations[component][place].get(commodity, 0.0) / quantity
                      for component, quantity in recipes.get(commodity, {}).items()]
            production[place] = min([planned] + bounds)
            # Reservation divisions can undershoot a fully supplied plan by an ulp.
            if math.isclose(production[place], planned, rel_tol=1e-12, abs_tol=0.0):
                production[place] = planned
        demand = {place: household_demand[commodity].get(place, 0.0) + processing_demand[commodity][place]
                  for place in places}
        deliveries = allocate(commodity, production, demand)
        reservations[commodity] = {}
        balances = {}
        for place in places:
            delivery = deliveries[place]
            imported = sum(row["quantity_per_day"] for row in delivery["imports"])
            available = production[place] + imported - delivery["exports_per_day"]
            household = min(available, household_demand[commodity].get(place, 0.0))
            processing = min(max(0.0, available - household), processing_demand[commodity][place])
            fraction = processing / processing_demand[commodity][place] if processing_demand[commodity][place] else 0.0
            reservations[commodity][place] = {
                product: capacity[product].get(place, 0.0) * recipe[commodity] * fraction
                for product, recipe in recipes.items() if commodity in recipe
            }
            balances[place] = {
                "capacity_per_day": capacity[commodity].get(place, 0.0),
                "production_per_day": production[place],
                "household_demand_per_day": household_demand[commodity].get(place, 0.0),
                "household_consumption_per_day": household,
                "processing_demand_per_day": processing_demand[commodity][place],
                "processing_consumption_per_day": 0.0,
                "closing_stock": available - household,
                "inputs": [],
                "allocation": delivery,
            }
        result[commodity] = balances

    for product, recipe in recipes.items():
        for place, balance in result[product].items():
            for component, quantity in recipe.items():
                consumed = balance["production_per_day"] * quantity
                component_balance = result[component][place]
                component_balance["processing_consumption_per_day"] += consumed
                component_balance["closing_stock"] = max(0.0, component_balance["closing_stock"] - consumed)
                balance["inputs"].append({
                    "commodity": component,
                    "required_per_day": balance["capacity_per_day"] * quantity,
                    "reserved_per_day": reservations[component][place][product],
                    "consumed_per_day": consumed,
                })
    return result