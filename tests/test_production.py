import pytest

from faerun.production import allocate_production
from faerun.sourcing import allocate_supply


def local_only(commodity, production, demand):
    return allocate_supply(production, demand, [])


def test_recipes_cannot_consume_the_same_material_twice():
    capacity = {"grain": {"town": 100}, "flour": {"town": 80}, "ale": {"town": 80}}
    demand = {"grain": {"town": 20}, "flour": {"town": 80}, "ale": {"town": 80}}
    result = allocate_production(capacity, demand, {"flour": {"grain": 1}, "ale": {"grain": 1}}, local_only)
    assert result["grain"]["town"]["household_consumption_per_day"] == 20
    assert result["grain"]["town"]["processing_consumption_per_day"] == 80
    assert result["flour"]["town"]["production_per_day"] == 40
    assert result["ale"]["town"]["production_per_day"] == 40


def test_bottleneck_returns_unused_inputs_to_closing_stock():
    capacity = {"flour": {"town": 100}, "salt": {"town": 2}, "bread": {"town": 100}}
    demand = {"flour": {"town": 0}, "salt": {"town": 0}, "bread": {"town": 100}}
    result = allocate_production(capacity, demand, {"bread": {"flour": 1, "salt": 0.1}}, local_only)
    assert result["bread"]["town"]["production_per_day"] == 20
    assert result["flour"]["town"]["processing_consumption_per_day"] == 20
    assert result["flour"]["town"]["closing_stock"] == 80
    assert result["salt"]["town"]["closing_stock"] == 0


def test_recipe_cycles_fail_explicitly():
    with pytest.raises(ValueError, match="cycles"):
        allocate_production({"flour": {"town": 1}}, {"flour": {"town": 1}},
                            {"flour": {"flour": 1}}, local_only)


def test_world_bread_chain_conserves_all_materials():
    from faerun.economy import _commodity_markets, commodity_sources
    from faerun.world import World

    world = World()
    quotes = {commodity: _commodity_markets(world, world.find_commodity(commodity))
              for commodity in ("grain", "flour", "salt", "bread")}
    for commodity in quotes:
        for producer in commodity_sources(commodity, world=world, limit=10000)["sources"]:
            assert producer["production_per_day"] == quotes[commodity][producer["id"]].production_per_day
    for commodity, markets in quotes.items():
        for place, quote in markets.items():
            incoming = quote.production_per_day + quote.imports_per_day
            outgoing = (quote.exports_per_day + quote.household_consumption_per_day
                        + quote.processing_consumption_per_day + quote.material_closing_stock)
            assert incoming == pytest.approx(outgoing, abs=0.001)
            assert quote.production_per_day <= quote.production_capacity_per_day + 0.001
            assert quote.demand_per_day == pytest.approx(quote.household_demand_per_day + quote.processing_demand_per_day, abs=0.001)
            for ingredient in quote.production_inputs:
                assert ingredient["consumed_per_day"] <= ingredient["reserved_per_day"] + 1e-6
                coefficient = world.commodities[commodity].bom[ingredient["commodity"]]
                assert ingredient["consumed_per_day"] == pytest.approx(quote.production_per_day * coefficient, abs=0.001)
                assert ingredient["consumed_per_day"] <= quotes[ingredient["commodity"]][place].processing_consumption_per_day + 1e-6


def test_missing_grain_stops_baking_without_inventing_replacement_supply():
    from faerun.economy import _commodity_markets
    from faerun.models import Event
    from faerun.world import World

    world = World()
    grain = world.find_commodity("grain")
    baseline = _commodity_markets(world, grain)
    factor = baseline["goldenfields"].factors["hinterland_capacity_multiplier"]
    world.add_event(Event(id="grain_failure", name="Grain crop failure", supply=0.0, commodities=["grain"]))
    after = _commodity_markets(world, grain)
    assert after["goldenfields"].factors["hinterland_capacity_multiplier"] == factor
    bread = _commodity_markets(world, world.find_commodity("bread"))
    assert all(quote.production_per_day == 0 for quote in bread.values())
    assert bread["waterdeep"].production_capacity_per_day > 0
    assert bread["waterdeep"].unmet_demand_per_day > 0