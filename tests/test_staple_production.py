from types import SimpleNamespace

import pytest

from faerun.economy import price_for, supply_index
from faerun.world import World


@pytest.mark.parametrize("settlement", ["Waterdeep", "Daggerford"])
def test_local_baking_meets_normal_needs(settlement):
    world = World()
    bread = price_for(settlement, "bread", world=world)
    assert bread.production_per_day >= bread.demand_per_day
    assert bread.factors["local_share"] == 1.0
    assert bread.source is None
    assert bread.availability in {"common", "abundant"}
    assert bread.stock > 0
    if settlement == "Waterdeep":
        assert price_for(settlement, "grain", world=world).source is not None


def test_baking_disruption_can_reduce_default_capacity(monkeypatch):
    world = World()
    market = world.find_settlement("Waterdeep")
    bread = world.find_commodity("bread")
    baseline = supply_index(world, market, bread)
    event = SimpleNamespace(supply=0.5, demand=1.0, applies_to_commodity=lambda _: True)
    monkeypatch.setattr(world, "events_for", lambda _: [event])
    assert supply_index(world, market, bread) == pytest.approx(baseline / 2)


def test_fresh_freight_keeps_faster_alternatives_and_rejects_expired_deliveries():
    world = World.__new__(World)

    def edge(destination, days, freight):
        return SimpleNamespace(dst=destination, days=days, distance=days * 20,
                               freight_units=lambda _: freight)

    world._edges = {
        "bakery": [edge("junction", 2.5, 1), edge("junction", 1, 10)],
        "junction": [edge("town", 1, 1), edge("distant", 4, 1)],
    }
    world.edge_risk = lambda _: 0
    landed, origins, haul = world.multi_source_freight(
        {"bakery": 0.02}, 1, 0.9, 0.02, max_days=3,
    )
    assert "town" in landed
    assert origins["town"] == "bakery"
    assert haul["town"][1] == 2
    assert "distant" not in landed


def test_freight_weights_are_reused_and_invalidated():
    from faerun.calendar import HarptosDate

    world = World.__new__(World)
    world.revision = 0
    world.date = HarptosDate(1492, 1)
    risk_calls = []
    edge = SimpleNamespace(dst="town", days=1, distance=20,
                           freight_units=lambda risk: 1 + risk)
    world._edges = {"farm": [edge]}

    def risk_for(leg):
        risk_calls.append(leg)
        return world.revision

    world.edge_risk = risk_for
    baseline = world.multi_source_freight({"farm": 1}, 1, 0.2, 1)
    repeated = world.multi_source_freight({"farm": 1}, 1, 0.2, 1)
    fresh = world.multi_source_freight({"farm": 1}, 1, 0.2, 1, max_days=3)
    assert baseline == repeated == fresh
    assert len(risk_calls) == 1

    world.revision += 1
    changed = world.multi_source_freight({"farm": 1}, 1, 0.2, 1)
    assert len(risk_calls) == 2
    assert changed[0]["town"] > baseline[0]["town"]
    assert changed[2] == baseline[2]

    world.date = HarptosDate(1492, 2)
    world.multi_source_freight({"farm": 1}, 1, 0.2, 1)
    assert len(risk_calls) == 3
    for pounds, perishable, base_price in [(2, 0.2, 1), (2, 0.4, 1), (2, 0.4, 2)]:
        world.multi_source_freight({"farm": 1}, pounds, perishable, base_price)
    assert len(risk_calls) == 6