"""Durable freight reuse must preserve prices, routes and finite reachability."""

import pytest

from faerun.calendar import HarptosDate
from faerun.models import C, S
from faerun.world import Edge, World


def world():
    result = World(
        settlements=[S(name, "Test", "test", 100, index, 0)
                     for index, name in enumerate(("A", "B", "C", "Unreachable"))],
        commodities=[C("goods", "Goods", "raw", 10)],
        businesses=[], date=HarptosDate(1492, 6, 1),
    )
    result._edges = {
        "a": [Edge("a", "b", 20, 1, "road"), Edge("a", "c", 100, 1, "road")],
        "b": [Edge("b", "c", 20, 1, "road")],
        "c": [], "unreachable": [],
    }
    return result


@pytest.mark.parametrize("pounds,price", [(1, 0), (.03, 7.576), (50, 0.004), (4000, 99.123456)])
def test_durable_routes_match_unscaled_reference_search(pounds, price):
    instance = world()
    actual = instance.multi_source_freight({"a": price}, pounds, 0, 10)
    # Nonzero perishability with zero value has exactly zero spoilage cost,
    # but exercises the existing non-cached search.
    expected = instance.multi_source_freight({"a": price}, pounds, 1, 0)
    assert actual[0] == pytest.approx(expected[0], rel=1e-12, abs=1e-12)
    assert actual[1] == expected[1]
    assert actual[2] == expected[2]
    assert "unreachable" not in actual[0]


def test_durable_routes_are_reused_but_returned_maps_are_independent():
    instance = world()
    first = instance.multi_source_freight({"a": 5}, 1, 0, 10)
    cached = instance._durable_freight_cache["a"]
    first[0]["b"] = -100
    first[2]["b"] = (-100, -100)
    second = instance.multi_source_freight({"a": 100}, 500, 0, 900)
    assert instance._durable_freight_cache["a"] is cached
    assert second[0]["b"] >= 100
    assert second[2]["b"][0] == 20


def test_route_cache_expires_on_revision_and_month_change():
    instance = world()
    instance.multi_source_freight({"a": 0}, 1, 0, 10)
    first = instance._durable_freight_cache["a"]
    instance.revision += 1
    instance.multi_source_freight({"a": 0}, 1, 0, 10)
    assert instance._durable_freight_cache["a"] is not first
    second = instance._durable_freight_cache["a"]
    instance.date = instance.date.advance()
    instance.multi_source_freight({"a": 0}, 1, 0, 10)
    assert instance._durable_freight_cache["a"] is not second


def test_fresh_limits_and_multi_source_competition_keep_existing_searches():
    instance = world()
    fresh = instance.multi_source_freight({"a": 0}, 1, 0, 10, max_days=0)
    assert fresh[0] == {"a": 0}
    mixed = instance.multi_source_freight({"a": 100, "b": 0}, 1, 0, 10)
    assert mixed[1]["c"] == "b"
    assert not hasattr(instance, "_durable_freight_cache")
