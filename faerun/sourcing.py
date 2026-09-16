"""Daily supply allocation; quantities are trade units, not inventory balances."""


def allocate_supply(production, demand, candidates):
    """Reserve local needs first, then allocate cheapest eligible deliveries."""
    local = {place: min(production.get(place, 0.0), need) for place, need in demand.items()}
    surplus = {place: max(0.0, amount - local.get(place, 0.0))
               for place, amount in production.items()}
    remaining = {place: max(0.0, need - local[place]) for place, need in demand.items()}
    imports = {place: [] for place in demand}
    backups = {place: [] for place in demand}
    exports = {place: 0.0 for place in production}
    ordered = sorted(candidates, key=lambda row: (
        row["unit_cost"], row["days"], row["source_id"], row["destination_id"],
    ))
    used = set()
    for row in ordered:
        source, destination = row["source_id"], row["destination_id"]
        if source == destination:
            continue
        capacity = row.get("capacity_per_day", float("inf"))
        quantity = min(surplus.get(source, 0.0), remaining.get(destination, 0.0), capacity)
        if quantity <= 1e-9:
            continue
        imports[destination].append({**row, "quantity_per_day": quantity,
                                     "share": quantity / demand[destination]})
        surplus[source] -= quantity
        remaining[destination] -= quantity
        exports[source] += quantity
        used.add((source, destination))
    for row in ordered:
        source, destination = row["source_id"], row["destination_id"]
        if source == destination or (source, destination) in used:
            continue
        available = min(surplus.get(source, 0.0), row.get("capacity_per_day", float("inf")))
        if available > 1e-9:
            backups[destination].append({**row, "available_per_day": available})
    return {place: {"local_per_day": local[place], "imports": imports[place],
                    "backups": backups[place], "unmet_per_day": max(0.0, remaining[place]),
                    "exports_per_day": exports.get(place, 0.0)}
            for place in demand}