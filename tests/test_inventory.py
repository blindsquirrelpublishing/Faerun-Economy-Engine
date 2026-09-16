import copy
import math
import random
from typing import Any, cast

import pytest

from faerun.inventory import InventoryAllocator, allocate_inventory_day, prepare_inventory_inputs


def day(capacity, demand=None, recipes=None, opening=None, storage=None,
        reserves=None, losses=None, candidates=None):
    if storage is None:
        storage = {commodity: {place: 1000.0 for place in values}
                   for commodity, values in capacity.items()}
    return allocate_inventory_day(
        capacity, demand or {}, recipes or {}, opening or {}, storage,
        reserves or {}, losses or {}, candidates or {},
    )


def lane(source, destination, cost=1.0, days=1.0, limit=None):
    row = {"source_id": source, "destination_id": destination,
           "unit_cost": cost, "days": days}
    if limit is not None:
        row["capacity_per_day"] = limit
    return row


def assert_conservation(result):
    for commodity, places in result.items():
        all_imports, all_exports = [], []
        for balance in places.values():
            allocation = balance["allocation"]
            imported = math.fsum(row["quantity_per_day"] for row in allocation["imports"])
            incoming = math.fsum((balance["opening_stock"], balance["production_per_day"], imported))
            outgoing = math.fsum((
                balance["household_consumption_per_day"], balance["processing_consumption_per_day"],
                allocation["exports_per_day"], balance["closing_stock"],
                balance["spoilage"], balance["overflow"],
            ))
            assert incoming == pytest.approx(outgoing, rel=1e-12, abs=1e-12), commodity
            assert 0 <= balance["production_per_day"] <= balance["capacity_per_day"]
            assert 0 <= balance["closing_stock"] <= balance["storage_capacity"]
            assert 0 <= balance["uncommitted_stock"] <= balance["closing_stock"]
            assert 0 <= balance["stock_draw_per_day"] <= balance["opening_stock"] - balance["spoilage"] + 1e-12
            for request in balance["inputs"]:
                assert 0 <= request["consumed_per_day"] <= request["reserved_per_day"]
                assert request["reserved_per_day"] <= request["required_per_day"]
            all_imports.append(imported)
            all_exports.append(allocation["exports_per_day"])
        assert math.fsum(all_imports) == pytest.approx(math.fsum(all_exports), abs=1e-12)


def test_stored_grain_supports_bread_and_depletes_over_days():
    capacity = {"grain": {"town": 0}, "bread": {"town": 8}}
    recipes = {"bread": {"grain": 2}}
    demand = {"grain": {"town": 2}, "bread": {"town": 8}}
    first = day(capacity, demand, recipes, opening={"grain": {"town": 25}})
    assert first["grain"]["town"]["household_consumption_per_day"] == 2
    assert first["grain"]["town"]["processing_consumption_per_day"] == 16
    assert first["grain"]["town"]["closing_stock"] == 7
    assert first["grain"]["town"]["stock_draw_per_day"] == 18
    assert first["bread"]["town"]["production_per_day"] == 8
    opening = {commodity: {place: row["closing_stock"] for place, row in places.items()}
               for commodity, places in first.items()}
    second = day(capacity, demand, recipes, opening)
    assert second["grain"]["town"]["closing_stock"] == 0
    assert second["bread"]["town"]["production_per_day"] == 2.5
    assert_conservation(first)
    assert_conservation(second)


def test_no_grain_means_no_bread_not_invented_substitutes():
    result = day({"grain": {"town": 0}, "bread": {"town": 10}},
                 {"bread": {"town": 10}}, {"bread": {"grain": 1}})
    assert result["bread"]["town"]["production_per_day"] == 0
    assert result["bread"]["town"]["allocation"]["unmet_per_day"] == 10
    assert_conservation(result)


def test_households_precede_proportional_competing_workshops():
    result = day(
        {"grain": {"town": 80}, "flour": {"town": 60}, "ale": {"town": 40}},
        {"grain": {"town": 20}}, {"flour": {"grain": 2}, "ale": {"grain": 1}},
    )
    grain = result["grain"]["town"]
    assert grain["household_consumption_per_day"] == 20
    assert grain["processing_demand_per_day"] == 160
    assert grain["processing_consumption_per_day"] == 60
    assert result["flour"]["town"]["production_per_day"] == 22.5
    assert result["ale"]["town"]["production_per_day"] == 15
    assert grain["closing_stock"] == 0
    assert_conservation(result)


def test_recipe_order_is_topological_not_input_dictionary_order():
    result = day(
        {"bread": {"town": 10}, "flour": {"town": 10}, "grain": {"town": 0}},
        {"bread": {"town": 10}}, {"bread": {"flour": 1}, "flour": {"grain": 2}},
        opening={"grain": {"town": 20}},
    )
    assert result["bread"]["town"]["household_consumption_per_day"] == 10
    assert result["flour"]["town"]["closing_stock"] == 0
    assert result["grain"]["town"]["closing_stock"] == 0
    assert_conservation(result)


def test_reserve_is_protected_after_local_final_and_processing_use():
    result = day(
        {"grain": {"farm": 100, "city": 0}, "bread": {"farm": 20, "city": 0}},
        {"grain": {"farm": 10, "city": 100}}, {"bread": {"grain": 1}},
        reserves={"grain": {"farm": 60}},
        candidates={"grain": [lane("farm", "city")]},
    )
    farm = result["grain"]["farm"]
    assert farm["allocation"]["exports_per_day"] == 10
    assert farm["closing_stock"] == 60
    assert farm["uncommitted_stock"] == 0
    assert result["grain"]["city"]["household_consumption_per_day"] == 10
    assert_conservation(result)


def test_local_urgent_use_can_draw_the_reserve_with_no_production():
    result = day(
        {"grain": {"town": 0}, "bread": {"town": 10}},
        {"grain": {"town": 5}, "bread": {"town": 10}}, {"bread": {"grain": 1}},
        opening={"grain": {"town": 20}}, reserves={"grain": {"town": 20}},
    )
    assert result["grain"]["town"]["closing_stock"] == 5
    assert result["grain"]["town"]["stock_draw_per_day"] == 15
    assert result["bread"]["town"]["production_per_day"] == 10
    assert_conservation(result)


def test_opening_inventory_is_exportable_but_not_its_winter_reserve():
    result = day(
        {"grain": {"farm": 0, "city": 0}}, {"grain": {"city": 100}},
        opening={"grain": {"farm": 100}}, reserves={"grain": {"farm": 70}},
        candidates={"grain": [lane("farm", "city")]},
    )
    assert result["grain"]["farm"]["closing_stock"] == 70
    assert result["grain"]["farm"]["stock_draw_per_day"] == 30
    assert result["grain"]["city"]["household_consumption_per_day"] == 30
    assert_conservation(result)


def test_losses_precede_consumption_and_overflow_is_explicit():
    result = day(
        {"grain": {"town": 10}}, {"grain": {"town": 12}},
        opening={"grain": {"town": 20}}, losses={"grain": {"town": 0.25}},
        storage={"grain": {"town": 5}},
    )
    balance = result["grain"]["town"]
    assert balance["spoilage"] == 5
    assert balance["household_consumption_per_day"] == 12
    assert balance["stock_draw_per_day"] == 12
    assert balance["closing_stock"] == 5
    assert balance["overflow"] == 8
    assert_conservation(result)


def test_total_spoilage_does_not_destroy_new_production():
    result = day({"grain": {"town": 3}}, {"grain": {"town": 8}},
                 opening={"grain": {"town": 10}}, losses={"grain": {"town": 1}})
    assert result["grain"]["town"]["spoilage"] == 10
    assert result["grain"]["town"]["household_consumption_per_day"] == 3
    assert result["grain"]["town"]["stock_draw_per_day"] == 0
    assert_conservation(result)


def test_zero_storage_caps_carryover_not_same_day_throughput():
    result = day(
        {"grain": {"town": 20}, "bread": {"town": 10}},
        {"bread": {"town": 7}}, {"bread": {"grain": 1}},
        storage={"grain": {"town": 0}, "bread": {"town": 0}},
    )
    assert result["bread"]["town"]["production_per_day"] == 10
    assert result["bread"]["town"]["household_consumption_per_day"] == 7
    assert result["bread"]["town"]["overflow"] == 3
    assert result["grain"]["town"]["overflow"] == 10
    assert all(row["closing_stock"] == 0 for places in result.values() for row in places.values())
    assert_conservation(result)


def test_stock_refill_uses_remaining_lane_budget_and_is_not_consumption():
    result = day(
        {"grain": {"farm": 20, "city": 0}}, {"grain": {"city": 6}},
        reserves={"grain": {"farm": 2, "city": 10}},
        candidates={"grain": [lane("farm", "city", limit=12)]},
    )
    farm, city = result["grain"]["farm"], result["grain"]["city"]
    assert farm["allocation"]["exports_per_day"] == 12
    assert city["household_demand_per_day"] == city["household_consumption_per_day"] == 6
    assert city["processing_demand_per_day"] == city["processing_consumption_per_day"] == 0
    assert city["closing_stock"] == 6
    assert city["allocation"]["unmet_per_day"] == 0
    assert [row["quantity_per_day"] for row in city["allocation"]["imports"]] == [6, 6]
    assert city["allocation"]["imports"][1]["share"] == 0
    assert city["allocation"]["imports"][1]["purpose"] == "replenishment"
    assert_conservation(result)


def test_urgent_demand_everywhere_precedes_cheaper_reserve_replenishment():
    result = day(
        {"grain": {"farm": 10, "near": 0, "far": 0}}, {"grain": {"far": 7}},
        reserves={"grain": {"near": 10}},
        candidates={"grain": [lane("farm", "near", cost=1), lane("farm", "far", cost=9)]},
    )
    assert result["grain"]["far"]["household_consumption_per_day"] == 7
    assert result["grain"]["near"]["closing_stock"] == 3
    assert result["grain"]["farm"]["allocation"]["exports_per_day"] == 10
    assert_conservation(result)


def test_refill_stops_at_storage_capacity_and_source_reserve():
    result = day(
        {"grain": {"farm": 20, "a": 0, "b": 0}},
        storage={"grain": {"farm": 100, "a": 3, "b": 100}},
        reserves={"grain": {"farm": 10, "a": 50, "b": 50}},
        candidates={"grain": [lane("farm", "a", cost=1), lane("farm", "b", cost=2)]},
    )
    assert result["grain"]["a"]["closing_stock"] == 3
    assert result["grain"]["a"]["overflow"] == 0
    assert result["grain"]["b"]["closing_stock"] == 7
    assert result["grain"]["farm"]["closing_stock"] == 10
    assert_conservation(result)


def test_zero_storage_prevents_refill_but_still_accepts_urgent_imports():
    result = day(
        {"grain": {"farm": 20, "city": 0}}, {"grain": {"city": 5}},
        storage={"grain": {"farm": 0, "city": 0}},
        reserves={"grain": {"city": 10}},
        candidates={"grain": [lane("farm", "city")]},
    )
    assert result["grain"]["city"]["household_consumption_per_day"] == 5
    assert result["grain"]["farm"]["allocation"]["exports_per_day"] == 5
    assert result["grain"]["farm"]["overflow"] == 15
    assert result["grain"]["city"]["closing_stock"] == 0
    assert_conservation(result)


def test_unused_recipe_reservations_are_neither_exported_nor_uncommitted():
    result = day(
        {"grain": {"town": 100, "city": 0}, "salt": {"town": 2},
         "bread": {"town": 100}},
        {"bread": {"town": 100}}, {"bread": {"grain": 1, "salt": 0.1}},
        reserves={"grain": {"city": 100}},
        candidates={"grain": [lane("town", "city")]},
    )
    assert result["bread"]["town"]["production_per_day"] == 20
    assert result["grain"]["town"]["closing_stock"] == 80
    assert result["grain"]["town"]["processing_consumption_per_day"] == 20
    assert result["grain"]["town"]["allocation"]["exports_per_day"] == 0
    assert result["grain"]["town"]["uncommitted_stock"] == 0
    assert result["grain"]["city"]["allocation"]["imports"] == []
    assert_conservation(result)


def test_refill_waits_for_actual_processing_to_avoid_overbuying_unused_inputs():
    result = day(
        {"grain": {"town": 0, "farm": 100}, "salt": {"town": 0},
         "bread": {"town": 100}},
        recipes={"bread": {"grain": 1, "salt": 0.1}},
        opening={"grain": {"town": 100}}, reserves={"grain": {"town": 50}},
        candidates={"grain": [lane("farm", "town")]},
    )
    assert result["bread"]["town"]["production_per_day"] == 0
    assert result["grain"]["town"]["closing_stock"] == 100
    assert result["grain"]["town"]["allocation"]["imports"] == []
    assert_conservation(result)


def test_product_stock_reduces_manufacturing_and_scheduled_input_demand():
    result = day(
        {"grain": {"town": 100}, "bread": {"town": 20}},
        {"bread": {"town": 20}}, {"bread": {"grain": 2}},
        opening={"bread": {"town": 20}}, reserves={"bread": {"town": 5}},
    )
    bread, grain = result["bread"]["town"], result["grain"]["town"]
    assert bread["capacity_per_day"] == 20
    assert bread["production_per_day"] == 5
    assert bread["stock_draw_per_day"] == 20
    assert bread["closing_stock"] == 5
    assert bread["inputs"][0]["required_per_day"] == 10
    assert grain["processing_demand_per_day"] == 10
    assert grain["processing_consumption_per_day"] == 10
    assert grain["production_per_day"] == 100
    assert_conservation(result)


def test_existing_product_stocks_can_eliminate_manufacturing():
    result = day(
        {"grain": {"town": 0}, "bread": {"town": 10}}, {"bread": {"town": 10}},
        {"bread": {"grain": 1}}, opening={"bread": {"town": 20}},
    )
    assert result["bread"]["town"]["production_per_day"] == 0
    assert result["bread"]["town"]["household_consumption_per_day"] == 10
    assert result["bread"]["town"]["stock_draw_per_day"] == 10
    assert result["grain"]["town"]["processing_demand_per_day"] == 0
    assert_conservation(result)


def test_manufacturing_retains_export_orders_above_local_requirements():
    result = day(
        {"grain": {"town": 100}, "bread": {"town": 100, "city": 0}},
        {"bread": {"town": 10, "city": 90}}, {"bread": {"grain": 1}},
        opening={"bread": {"town": 10}},
        candidates={"bread": [lane("town", "city")]},
    )
    assert result["bread"]["town"]["production_per_day"] == 90
    assert result["grain"]["town"]["processing_demand_per_day"] == 90
    assert result["bread"]["town"]["allocation"]["exports_per_day"] == 90
    assert result["bread"]["city"]["household_consumption_per_day"] == 90
    assert_conservation(result)


def test_spoilage_is_applied_before_manufactured_schedule_reduction():
    result = day(
        {"grain": {"town": 100}, "bread": {"town": 20}}, {"bread": {"town": 20}},
        {"bread": {"grain": 1}}, opening={"bread": {"town": 20}},
        losses={"bread": {"town": 0.5}},
    )
    assert result["bread"]["town"]["production_per_day"] == 10
    assert result["bread"]["town"]["spoilage"] == 10
    assert_conservation(result)


def test_cheapest_delivery_order_is_deterministic_and_does_not_reexport_imports():
    routes = [lane("b", "city", 1, 2), lane("a", "city", 1, 1),
              lane("city", "remote", 0, 0), lane("a", "a", 0, 0)]
    capacity = {"grain": {"a": 3, "b": 8, "city": 0, "remote": 0}}
    demand = {"grain": {"city": 5, "remote": 5}}
    result = day(capacity, demand, candidates={"grain": routes})
    reverse = day(capacity, demand, candidates={"grain": list(reversed(routes))})
    assert result == reverse
    assert [row["source_id"] for row in result["grain"]["city"]["allocation"]["imports"]] == ["a", "b"]
    assert result["grain"]["remote"]["household_consumption_per_day"] == 0
    assert result["grain"]["city"]["allocation"]["exports_per_day"] == 0
    assert_conservation(result)


def test_backups_do_not_advertise_lost_or_protected_stock():
    result = day(
        {"grain": {"a": 20, "b": 20, "city": 0}}, {"grain": {"city": 5}},
        storage={"grain": {"a": 0, "b": 7, "city": 10}},
        reserves={"grain": {"b": 3}},
        candidates={"grain": [lane("a", "city", 1), lane("b", "city", 2)]},
    )
    assert result["grain"]["a"]["overflow"] == 15
    backup = result["grain"]["city"]["allocation"]["backups"]
    assert len(backup) == 1
    assert backup[0]["source_id"] == "b"
    assert backup[0]["available_per_day"] == 4
    assert_conservation(result)


def test_sparse_maps_allow_stock_only_materials_and_delivery_only_places():
    result = allocate_inventory_day(
        {"bread": {"town": 5}}, {"bread": {"town": 5}},
        {"bread": {"grain": 1}}, {"grain": {"farm": 5}},
        {}, {}, {}, {"grain": [lane("farm", "town")]},
    )
    assert result["bread"]["town"]["production_per_day"] == 5
    assert result["grain"]["farm"]["stock_draw_per_day"] == 5
    assert_conservation(result)


@pytest.mark.parametrize("field", ["capacity", "demand", "opening", "storage", "reserves", "losses"])
@pytest.mark.parametrize("invalid", [-1, math.nan, math.inf, -math.inf, "bad"])
def test_invalid_state_values_are_rejected(field, invalid):
    arguments = {"capacity": {"grain": {"town": 1}}, field: {"grain": {"town": invalid}}}
    with pytest.raises(ValueError, match="finite"):
        day(**arguments)


def test_loss_rate_above_one_fails():
    with pytest.raises(ValueError, match="at most 1"):
        day({"grain": {"town": 1}}, losses={"grain": {"town": 1.01}})


@pytest.mark.parametrize("invalid", [-1, math.nan, math.inf, "bad"])
def test_invalid_lane_limits_are_rejected_even_on_unused_lanes(invalid):
    with pytest.raises(ValueError, match="Delivery capacity"):
        day({"grain": {"town": 1}},
            candidates={"grain": [lane("town", "town", limit=invalid)]})


@pytest.mark.parametrize("invalid", [0, -1, math.nan, math.inf])
def test_recipe_coefficients_must_be_finite_positive(invalid):
    with pytest.raises(ValueError, match="Recipe"):
        day({"grain": {}, "bread": {}}, recipes={"bread": {"grain": invalid}})


def test_recipe_cycle_and_missing_inputs_are_rejected():
    with pytest.raises(ValueError, match="cycles"):
        day({"bread": {}, "flour": {}}, recipes={"bread": {"flour": 1}, "flour": {"bread": 1}})
    with pytest.raises(ValueError, match="Missing.*grain"):
        day({"bread": {}}, recipes={"bread": {"grain": 1}})
    with pytest.raises(ValueError, match="Missing.*bread"):
        day({"grain": {}}, recipes={"bread": {"grain": 1}})


def test_input_maps_and_candidate_dicts_are_not_mutated():
    arguments = (
        {"grain": {"a": 20, "b": 0}}, {"grain": {"b": 4}}, {},
        {"grain": {"a": 10}}, {"grain": {"a": 100, "b": 100}},
        {"grain": {"b": 6}}, {"grain": {"a": 0.1}},
        {"grain": [lane("a", "b", limit=8)]},
    )
    original = copy.deepcopy(arguments)
    assert_conservation(allocate_inventory_day(*arguments))
    assert arguments == original


def test_reservation_division_never_rounds_actual_use_above_reserved():
    rng = random.Random(7351)
    for _ in range(100):
        available = rng.uniform(0.01, 100)
        coefficient = rng.uniform(0.01, 100)
        result = day(
            {"grain": {"town": available}, "bread": {"town": 10000}, "ale": {"town": 10000}},
            recipes={"bread": {"grain": coefficient}, "ale": {"grain": 0.73}},
        )
        requests = [result[product]["town"]["inputs"][0] for product in ("bread", "ale")]
        assert math.fsum(row["reserved_per_day"] for row in requests) <= available
        assert math.fsum(row["consumed_per_day"] for row in requests) <= available
        assert_conservation(result)


def test_random_multiday_network_conserves_material_and_shared_trade_limits():
    rng = random.Random(8364)
    places = ("a", "b", "c", "d")
    commodities = ("grain", "salt", "flour", "bread", "ale")
    recipes = {"flour": {"grain": 1.25}, "bread": {"flour": 0.9, "salt": 0.03},
               "ale": {"grain": 0.6}}
    capacity = {commodity: {place: rng.uniform(0, 60) for place in places} for commodity in commodities}
    demand = {commodity: {place: rng.uniform(0, 10) for place in places} for commodity in commodities}
    storage = {commodity: {place: rng.uniform(0, 100) for place in places} for commodity in commodities}
    reserves = {commodity: {place: rng.uniform(0, 80) for place in places} for commodity in commodities}
    losses = {commodity: {place: rng.uniform(0, 0.4) for place in places} for commodity in commodities}
    opening = {commodity: {place: rng.uniform(0, 100) for place in places} for commodity in commodities}
    routes = {commodity: [lane(source, destination, rng.random(), limit=rng.uniform(0, 40))
                          for source in places for destination in places if source != destination]
              for commodity in commodities}
    for _ in range(15):
        result = allocate_inventory_day(capacity, demand, recipes, opening, storage, reserves, losses, routes)
        assert_conservation(result)
        for commodity in commodities:
            for route in routes[commodity]:
                shipments = result[commodity][route["destination_id"]]["allocation"]["imports"]
                quantity = math.fsum(row["quantity_per_day"] for row in shipments
                                     if row["source_id"] == route["source_id"])
                assert quantity <= route["capacity_per_day"] + 1e-12
        opening = {commodity: {place: balance["closing_stock"] for place, balance in balances.items()}
                   for commodity, balances in result.items()}


def test_empty_day_is_empty():
    assert allocate_inventory_day({}, {}, {}, {}, {}, {}, {}, {}) == {}


def test_prepared_inputs_preserve_results_and_reset_budgets_each_day():
    capacity = {"grain": {"farm": 100, "town": 0}, "bread": {"town": 20}}
    demand = {"bread": {"town": 20}}
    recipes = {"bread": {"grain": 2}}
    routes = {"grain": [lane("farm", "town", limit=50)]}
    reserves = {"grain": {"farm": 10, "town": 20}}
    prepared_recipes, prepared_routes = prepare_inventory_inputs(recipes, routes)
    expected = day(capacity, demand, recipes, reserves=reserves, candidates=routes)
    first = day(capacity, demand, prepared_recipes, reserves=reserves, candidates=prepared_routes)
    second = day(capacity, demand, prepared_recipes, reserves=reserves, candidates=prepared_routes)
    assert expected == first == second
    assert first["grain"]["farm"]["allocation"]["exports_per_day"] == 50
    assert_conservation(first)


def test_preparation_takes_immutable_snapshots_not_stale_identity_caches():
    recipes = {"bread": {"grain": 2}}
    routes = {"grain": [lane("farm", "town", limit=10)]}
    prepared_recipes, prepared_routes = prepare_inventory_inputs(recipes, routes)
    recipes["bread"]["grain"] = -1
    routes["grain"][0]["capacity_per_day"] = -1
    routes["grain"].append(lane("farm", "town", cost=-10))
    capacity = {"grain": {"farm": 100}, "bread": {"town": 5}}
    result = day(capacity, recipes=prepared_recipes, candidates=prepared_routes)
    assert result["bread"]["town"]["production_per_day"] == 5
    assert result["bread"]["town"]["inputs"][0]["required_per_day"] == 10
    with pytest.raises(TypeError):
        prepared_recipes["bread"]["grain"] = -1
    with pytest.raises(TypeError):
        prepared_routes["grain"][0]["capacity_per_day"] = -1
    with pytest.raises(TypeError):
        cast(Any, prepared_routes)["grain"] = []
    result["grain"]["town"]["allocation"]["imports"][0]["capacity_per_day"] = -10
    assert prepared_routes["grain"][0]["capacity_per_day"] == 10
    assert_conservation(result)


def test_preparation_is_idempotent_and_avoids_daily_recipe_lane_validation(monkeypatch):
    import faerun.inventory as inventory

    recipes, routes = prepare_inventory_inputs(
        {"bread": {"grain": 2}}, {"grain": [lane("farm", "town", limit=10)]},
    )
    again = prepare_inventory_inputs(recipes, routes)
    assert again[0] is recipes
    assert again[1] is routes

    def forbidden(*args):
        pytest.fail(f"Immutable prepared recipes/lanes were revalidated ({len(args)} arguments)")

    monkeypatch.setattr(inventory, "_recipe_signature", forbidden)
    monkeypatch.setattr(inventory, "_validate_candidates", forbidden)
    result = day({"grain": {"farm": 10}, "bread": {"town": 5}},
                 recipes=recipes, candidates=routes)
    assert result["bread"]["town"]["production_per_day"] == 5
    assert_conservation(result)


@pytest.mark.parametrize("field", ["capacity", "demand", "opening", "storage", "reserves", "losses"])
def test_prepared_configuration_does_not_skip_daily_state_validation(field):
    recipes, routes = prepare_inventory_inputs({}, {"grain": [lane("farm", "town")]})
    arguments = {"capacity": {"grain": {"farm": 1}}, "recipes": recipes, "candidates": routes}
    arguments[field] = {"grain": {"farm": -1}}
    with pytest.raises(ValueError, match="finite"):
        day(**arguments)


def test_prepared_materials_still_require_current_day_state_definitions():
    recipes, routes = prepare_inventory_inputs({"bread": {"grain": 2}}, {})
    with pytest.raises(ValueError, match="Missing.*grain"):
        day({"bread": {"town": 1}}, recipes=recipes, candidates=routes)
    recipes, routes = prepare_inventory_inputs({}, {"grain": [lane("farm", "town")]})
    with pytest.raises(ValueError, match="Missing.*grain"):
        day({"bread": {"town": 1}}, recipes=recipes, candidates=routes)


def test_preparation_rejects_invalid_recipe_cycles_and_lane_limits():
    with pytest.raises(ValueError, match="cycles"):
        prepare_inventory_inputs({"a": {"b": 1}, "b": {"a": 1}}, {})
    with pytest.raises(ValueError, match="Recipe"):
        prepare_inventory_inputs({"bread": {"grain": -1}}, {})
    with pytest.raises(ValueError, match="Delivery capacity"):
        prepare_inventory_inputs({}, {"grain": [lane("farm", "town", limit=-1)]})


def test_mutable_public_inputs_are_revalidated_even_after_cached_success():
    capacity = {"grain": {"farm": 10}, "bread": {"town": 5}}
    recipes = {"bread": {"grain": 2}}
    routes = {"grain": [lane("farm", "town", limit=10)]}
    assert_conservation(day(capacity, recipes=recipes, candidates=routes))
    recipes["bread"]["grain"] = -1
    with pytest.raises(ValueError, match="Recipe"):
        day(capacity, recipes=recipes, candidates=routes)
    recipes["bread"]["grain"] = 2
    routes["grain"][0]["capacity_per_day"] = -1
    with pytest.raises(ValueError, match="Delivery capacity"):
        day(capacity, recipes=recipes, candidates=routes)
    routes["grain"][0]["capacity_per_day"] = 10
    recipes["grain"] = {"bread": 1}
    with pytest.raises(ValueError, match="cycles"):
        day(capacity, recipes=recipes, candidates=routes)


def test_already_sorted_public_candidates_are_not_resorted(monkeypatch):
    import faerun.inventory as inventory

    routes = {"grain": [lane("a", "city", 1), lane("b", "city", 2)]}
    original_sorted = sorted

    def no_lane_sort(values, *args, **kwargs):
        assert kwargs.get("key") is not inventory._delivery_key
        return original_sorted(values, *args, **kwargs)

    monkeypatch.setattr(inventory, "sorted", no_lane_sort, raising=False)
    result = day({"grain": {"a": 5, "b": 5, "city": 0}}, {"grain": {"city": 7}},
                 candidates=routes)
    assert result["grain"]["city"]["household_consumption_per_day"] == 7
    assert_conservation(result)


def test_replay_allocator_defaults_to_no_backup_enumeration_but_retains_every_route():
    capacity = {"grain": {"a": 10, "b": 10, "town": 0}}
    demand = {"grain": {"town": 5}}
    storage = {"grain": dict.fromkeys(capacity["grain"], 100)}
    routes = {"grain": [lane("a", "town", 1), lane("b", "town", 2)]}
    allocator = InventoryAllocator({}, routes)
    complete = allocator.allocate(capacity, demand, {}, storage, {}, {}, include_backups=True)
    replay = allocator.allocate(capacity, demand, {}, storage, {}, {})
    assert complete == allocate_inventory_day(capacity, demand, {}, {}, storage, {}, {}, routes)
    assert complete["grain"]["town"]["allocation"]["backups"][0]["source_id"] == "b"
    for places in complete.values():
        for balance in places.values():
            balance["allocation"]["backups"] = []
    assert replay == complete
    assert_conservation(replay)


def test_replay_index_keeps_distant_supply_and_never_truncates_to_nearest_sources():
    sources = [f"s{i:03}" for i in range(100)]
    capacity = {"grain": {**dict.fromkeys(sources, 0.0), sources[-1]: 10, "town": 0}}
    routes = {"grain": [lane(source, "town", cost=i) for i, source in enumerate(sources)]}
    allocator = InventoryAllocator({}, routes)
    result = allocator.allocate(
        capacity, {"grain": {"town": 4}}, {},
        {"grain": dict.fromkeys(capacity["grain"], 100)}, {"grain": {"town": 3}}, {},
    )
    shipments = result["grain"]["town"]["allocation"]["imports"]
    assert [row["source_id"] for row in shipments] == [sources[-1], sources[-1]]
    assert [row["quantity_per_day"] for row in shipments] == [4, 3]
    assert_conservation(result)


def test_replay_parallel_lanes_have_independent_but_shared_across_rounds_budgets():
    capacity = {"grain": {"farm": 100, "town": 0}}
    routes = {"grain": [lane("farm", "town", cost=1, limit=3),
                        lane("farm", "town", cost=1, limit=7),
                        lane("farm", "town", cost=2, limit=2)]}
    storage = {"grain": {"farm": 100, "town": 100}}
    allocator = InventoryAllocator({}, routes)
    first = allocator.allocate(
        capacity, {"grain": {"town": 5}}, {}, storage, {"grain": {"town": 20}}, {},
    )
    second = allocator.allocate(
        capacity, {"grain": {"town": 5}}, {}, storage, {"grain": {"town": 20}}, {},
    )
    assert first == second
    assert first["grain"]["farm"]["allocation"]["exports_per_day"] == 12
    assert first["grain"]["town"]["closing_stock"] == 7
    assert [row["quantity_per_day"] for row in first["grain"]["town"]["allocation"]["imports"]] == [3, 2, 5, 2]
    assert_conservation(first)


def test_replay_only_opens_active_source_groups_and_uses_sparse_lane_budgets(monkeypatch):
    import faerun.inventory as inventory

    sources = [f"s{i:03}" for i in range(100)]
    destinations = [f"d{i:03}" for i in range(100)]
    routes = {"grain": [lane(source, destination) for source in sources for destination in destinations]}
    allocator = InventoryAllocator({}, routes)
    opened = []
    original = inventory._next_eligible

    def observe(network, indices, position, remaining, surplus, needs):
        assert isinstance(remaining, dict)
        assert len(remaining) <= len(destinations)
        opened.append(network.rows[indices[0]]["source_id"])
        return original(network, indices, position, remaining, surplus, needs)

    def forbidden(*args):
        pytest.fail(f"Replay scanned/revalidated the entire lane table ({len(args)} arguments)")

    monkeypatch.setattr(inventory, "_next_eligible", observe)
    monkeypatch.setattr(inventory, "_trade", forbidden)
    monkeypatch.setattr(inventory, "_validate_candidates", forbidden)
    capacity = {"grain": {**dict.fromkeys(sources + destinations, 0), sources[-1]: 10}}
    result = allocator.allocate(
        capacity, {"grain": dict.fromkeys(destinations, 1)}, {},
        {"grain": dict.fromkeys(sources + destinations, 100)}, {}, {},
    )
    assert set(opened) == {sources[-1]}
    assert result["grain"][sources[-1]]["allocation"]["exports_per_day"] == 10
    assert_conservation(result)


def test_replay_opens_no_lane_groups_when_no_destination_needs_supply(monkeypatch):
    import faerun.inventory as inventory

    allocator = InventoryAllocator({}, {"grain": [lane("farm", "town")]})

    def forbidden(*args):
        pytest.fail(f"No-demand replay should not visit any lanes ({len(args)} arguments)")

    monkeypatch.setattr(inventory, "_next_eligible", forbidden)
    result = allocator.allocate(
        {"grain": {"farm": 100, "town": 0}}, {}, {},
        {"grain": {"farm": 100, "town": 100}}, {}, {},
    )
    assert result["grain"]["farm"]["closing_stock"] == 100
    assert_conservation(result)


def test_replay_indexes_exclude_permanently_zero_capacity_lanes(monkeypatch):
    import faerun.inventory as inventory

    allocator = InventoryAllocator({}, {"grain": [lane("farm", "town", limit=0)]})

    def forbidden(*args):
        pytest.fail(f"Zero-capacity lanes should not enter the replay index ({len(args)} arguments)")

    monkeypatch.setattr(inventory, "_next_eligible", forbidden)
    result = allocator.allocate(
        {"grain": {"farm": 100, "town": 0}}, {"grain": {"town": 5}}, {},
        {"grain": {"farm": 100, "town": 100}}, {}, {},
    )
    assert result["grain"]["town"]["allocation"]["unmet_per_day"] == 5
    assert result["grain"]["town"]["allocation"]["imports"] == []
    assert_conservation(result)


@pytest.mark.parametrize("field", [
    "capacity", "final_demand", "opening_stock", "storage_capacity", "reserve_target", "loss_rates",
])
def test_replay_allocator_always_validates_daily_state_maps(field):
    allocator = InventoryAllocator({}, {"grain": [lane("farm", "town")]})
    arguments = {
        "capacity": {"grain": {"farm": 10}}, "final_demand": {}, "opening_stock": {},
        "storage_capacity": {}, "reserve_target": {}, "loss_rates": {},
    }
    arguments[field] = {"grain": {"farm": math.nan}}
    with pytest.raises(ValueError, match="finite"):
        allocator.allocate(**arguments)


def test_indexed_replay_matches_full_greedy_allocator_across_random_days():
    rng = random.Random(4047)
    places = [f"p{i}" for i in range(9)]
    commodities = ("grain", "salt", "flour", "bread", "ale")
    recipes = {"flour": {"grain": 1.2}, "bread": {"flour": 0.7, "salt": 0.03},
               "ale": {"grain": 0.6}}
    routes = {
        commodity: [lane(source, destination, cost=rng.randrange(5), days=rng.randrange(3),
                         limit=rng.uniform(0, 10))
                    for source in places for destination in places for _ in range(2)]
        for commodity in commodities
    }
    allocator = InventoryAllocator(recipes, routes)
    opening = {}
    for _ in range(20):
        capacity = {commodity: {place: rng.uniform(0, 60) if rng.random() < 0.5 else 0
                                for place in places} for commodity in commodities}
        demand = {commodity: {place: rng.uniform(0, 10) for place in places}
                  for commodity in commodities}
        storage = {commodity: {place: rng.uniform(0, 80) for place in places}
                   for commodity in commodities}
        reserves = {commodity: {place: rng.uniform(0, 40) for place in places}
                    for commodity in commodities}
        losses = {commodity: dict.fromkeys(places, 0.1) for commodity in commodities}
        expected = allocate_inventory_day(
            capacity, demand, recipes, opening, storage, reserves, losses, routes,
        )
        indexed = allocator.allocate(
            capacity, demand, opening, storage, reserves, losses, include_backups=True,
        )
        assert indexed == expected
        assert_conservation(indexed)
        opening = {commodity: {place: row["closing_stock"] for place, row in balances.items()}
                   for commodity, balances in indexed.items()}
