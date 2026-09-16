from types import SimpleNamespace

import pytest

from faerun.world import Edge, FREIGHT_RATE
from tools.export_transport_reference import reference_rows


def test_reference_exports_only_direct_edges_and_preserves_parallel_modes():
    edges = [Edge("first", "middle", 48, 1, "road", "Highway"),
             Edge("first", "middle", 72, 1, "sea", "Coastal lane"),
             Edge("middle", "last", 20, 0.8, "river+portage", "Transfer", True)]
    world = SimpleNamespace(
        _edges={"first": edges[:2], "middle": edges[2:]},
        settlements={name: SimpleNamespace(name=name.title()) for name in ("first", "middle", "last")},
        edge_risk=lambda edge: 0.25,
    )
    legs, carriers = reference_rows(world)
    assert len(legs) == 3
    assert not any(row["origin_id"] == "first" and row["destination_id"] == "last" for row in legs)
    road = next(row for row in legs if row["mode"] == "road")
    assert road["distance_miles"] == 48
    assert road["travel_days"] == 2
    assert road["freight_gp_per_100_lb"] == pytest.approx(48 * 1.25 * FREIGHT_RATE * 100)
    assert road["freight_gp_per_2000_lb"] == pytest.approx(20 * road["freight_gp_per_100_lb"])
    mixed = next(row for row in legs if row["mixed_mode"])
    assert mixed["inferred"]
    assert {row["carrier_mode"] for row in carriers if row["leg_id"] == mixed["leg_id"]} == {"river", "portage"}
    assert all(row["mixed_edge_component"] for row in carriers if row["leg_id"] == mixed["leg_id"])
    assert all(row["leg_id"] in {leg["leg_id"] for leg in legs} for row in carriers)


def test_fastest_routes_use_elapsed_days_and_keep_same_path_for_all_metrics():
    from faerun.world import World
    from tools.export_transport_reference import fastest_rows

    world = World.__new__(World)
    world.settlements = {name: SimpleNamespace(name=name.title())
                         for name in ("first", "middle", "last", "isolated")}
    first = Edge("first", "middle", 24, 1, "road", "Approach", True)
    second = Edge("middle", "last", 24, 1, "road", "Finish")
    world._edges = {"first": [Edge("first", "last", 72, 1, "road", "Direct"), first],
                    "middle": [second]}
    world.edge_risk = lambda edge: 10 if edge.inferred else 0
    rows = fastest_rows(world, ["first", "last", "isolated"])
    selected = next(row for row in rows if row["origin"] == "First" and row["destination"] == "Last")
    assert selected["travel_days"] == 2
    assert selected["distance_miles"] == 48
    assert selected["path"] == "First -> Middle -> Last"
    assert selected["leg_count"] == 2
    assert selected["uses_inferred"]
    assert selected["freight_gp_per_100_lb"] == pytest.approx((24 * 11 + 24) * FREIGHT_RATE * 100)
    assert all(row["travel_days"] == 0 for row in rows if row["origin"] == row["destination"])
    missing = next(row for row in rows if row["origin"] == "First" and row["destination"] == "Isolated")
    assert not missing["reachable"]
    assert missing["travel_days"] is None

    from tools.export_transport_reference import schedule_rows

    options = schedule_rows(world, ["first", "last", "isolated"])
    assert len(options) == 2
    quickest = next(row for row in options if "Fastest" in row["selection"])
    cheapest = next(row for row in options if "Lowest freight" in row["selection"])
    assert quickest["selection"] == "Fastest; Land only"
    assert quickest["connections"] == 1
    assert cheapest["connections"] == 0
    assert cheapest["travel_days"] == 3
    assert cheapest["freight_gp_per_100_lb"] < quickest["freight_gp_per_100_lb"]
    assert not any("Water only" in row["selection"] for row in options)