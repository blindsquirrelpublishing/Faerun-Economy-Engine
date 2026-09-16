import pytest

from faerun.sourcing import allocate_supply


def candidate(source, destination, cost, capacity=1000):
    return {"source_id": source, "destination_id": destination, "unit_cost": cost,
            "days": 1, "distance": 20, "capacity_per_day": capacity}


def test_multiple_suppliers_respect_local_use_and_shared_export_limits():
    production = {"farm_a": 100, "farm_b": 80, "town": 10, "other": 0}
    demand = {"farm_a": 20, "farm_b": 20, "town": 120, "other": 80}
    routes = [candidate("farm_a", "town", 1), candidate("farm_b", "town", 2),
              candidate("farm_a", "other", 3), candidate("farm_b", "other", 4)]
    result = allocate_supply(production, demand, routes)
    assert [row["quantity_per_day"] for row in result["town"]["imports"]] == [80, 30]
    assert result["town"]["local_per_day"] == 10
    assert result["town"]["unmet_per_day"] == 0
    assert result["other"]["unmet_per_day"] == 50
    assert result["farm_a"]["exports_per_day"] == 80
    assert result["farm_b"]["exports_per_day"] == 60
    assert sum(row["share"] for row in result["town"]["imports"]) == pytest.approx(110 / 120)
    assert allocate_supply(production, demand, reversed(routes)) == result


def test_route_limits_and_unreserved_backup_suppliers():
    result = allocate_supply({"near": 100, "far": 100, "town": 0},
                             {"near": 0, "far": 0, "town": 10},
                             [candidate("near", "town", 1, 10), candidate("far", "town", 2)])
    assert result["town"]["imports"][0]["quantity_per_day"] == 10
    assert result["town"]["backups"][0]["source_id"] == "far"
    assert result["far"]["exports_per_day"] == 0
    limited = allocate_supply({"farm": 100, "town": 0}, {"farm": 0, "town": 50},
                              [candidate("farm", "town", 1, 15)])
    assert limited["town"]["unmet_per_day"] == 35


def test_world_grain_allocations_conserve_supply_and_expose_multiple_sources():
    from faerun.economy import _commodity_markets
    from faerun.world import World

    world = World()
    quotes = _commodity_markets(world, world.find_commodity("grain"))
    exported = {}
    assert any(len([row for row in quote.sources if row["supply_type"] == "import"]) > 1
               for quote in quotes.values())
    for quote in quotes.values():
        assert quote.local_consumption_per_day + quote.imports_per_day + quote.unmet_demand_per_day == pytest.approx(quote.demand_per_day, abs=0.001)
        assert quote.local_consumption_per_day + quote.exports_per_day <= quote.production_per_day + 0.001
        for row in quote.sources:
            if row["supply_type"] == "import":
                exported[row["source_id"]] = exported.get(row["source_id"], 0) + row["quantity_per_day"]
        assert quote.source is None or any(row["source"] == quote.source and row["supply_type"] == "import" for row in quote.sources)
    for source, quantity in exported.items():
        assert quantity == pytest.approx(quotes[source].exports_per_day)


def test_configured_lane_limit_changes_allocation_and_invalidates_cache():
    from faerun.economy import _commodity_markets
    from faerun.world import World

    world = World()
    grain = world.find_commodity("grain")
    initial = _commodity_markets(world, grain)
    destination, quote = next((place, quote) for place, quote in initial.items() if quote.imports_per_day)
    source = next(row["source_id"] for row in quote.sources if row["supply_type"] == "import")
    world.config.delivery_limits[("grain", source, destination)] = 0
    updated = _commodity_markets(world, grain)
    assert not any(row["source_id"] == source and row["supply_type"] == "import"
                   for row in updated[destination].sources)