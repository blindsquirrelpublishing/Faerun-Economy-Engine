"""Real allocator regression for the numerical failure blocking guild quotes."""

import math

import pytest

from faerun import inventory


def allocate(indexed=False, capacity=None):
    amount = 0.036713644006449796
    places = {"source": amount, "one": 0, "two": 0, "three": 0}
    demands = {"one": amount / 5, "two": amount / 2, "three": amount}
    lanes = {"parchment": [
        {"source_id": "source", "destination_id": name, "unit_cost": index + 1, "days": 1}
        for index, name in enumerate(demands)
    ]}
    production = {"parchment": places} if capacity is None else capacity
    needs = {"parchment": demands}
    storage = {"parchment": dict.fromkeys(places, 1)}
    if indexed:
        return inventory.InventoryAllocator({}, lanes).allocate(production, needs, {}, storage, {}, {})
    return inventory.allocate_inventory_day(production, needs, {}, {}, storage, {}, {}, lanes)


@pytest.mark.parametrize("indexed", [False, True])
def test_exhausted_export_budget_tolerates_only_float_roundoff(indexed):
    rows = allocate(indexed)["parchment"]
    source = rows["source"]
    assert source["closing_stock"] == source["uncommitted_stock"] == 0
    received = math.fsum(
        item["quantity_per_day"] for row in rows.values() for item in row["allocation"]["imports"])
    assert received == pytest.approx(source["production_per_day"], rel=1e-14, abs=0)
    assert all(row["closing_stock"] >= 0 for row in rows.values())


def test_real_overdraw_is_not_hidden_by_roundoff_normalization(monkeypatch):
    trade = inventory._trade

    def overdraw(*args, **kwargs):
        trade(*args, **kwargs)
        args[4]["source"]["allocation"]["exports_per_day"] += 0.0001

    monkeypatch.setattr(inventory, "_trade", overdraw)
    with pytest.raises(ValueError, match="Delivered supply"):
        allocate()


def test_negative_input_is_still_invalid_even_if_very_small():
    with pytest.raises(ValueError):
        allocate(capacity={"parchment": {"source": -1e-18}})
