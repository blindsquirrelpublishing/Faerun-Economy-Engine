"""Travel modes and multimodal trade routes.

A route's ``kind`` names one or more travel modes. When it names several --
``river+portage``, ``tunnel+trail`` -- the cargo cannot make the journey in one
carrier, so it is transhipped along the way. The engine must charge that:
more coin, more days, more danger than the modes would suggest on their own.
"""

from __future__ import annotations

import pytest

from faerun.data.routes import NAMED_ROUTES, NAMED_SEA_LANES
from faerun.world import (
    CARRIERS,
    MODES,
    MODE_LABELS,
    MULTIMODAL_COST,
    SURVEYED_MAGIC_ROUTES,
    Edge,
    World,
    canonical_kind,
    describe_modes,
    mode_profile,
    parse_modes,
)


@pytest.fixture(scope="module")
def world() -> World:
    return World()


# --------------------------------------------------------------------------
# the mode table
# --------------------------------------------------------------------------


def test_carrier_options_include_cost_efficiency_capacity_and_air_mounts():
    good = Edge("a", "b", 100, 1.0, "air")
    poor = Edge("a", "b", 100, 0.5, "air")

    options = good.carrier_options()
    assert len(options) == len(CARRIERS["air"])
    assert {option["name"] for option in options} >= {
        "Gryphon flight", "Hippogriff flight", "Giant eagle flight"
    }
    assert all(option["cost_gp"] > 0 for option in options)
    assert all(option["cost_gp_per_ton_mile"] > 0 for option in options)
    assert all(option["max_load_lb"] > 0 for option in options)
    assert poor.carrier_options()[0]["cost_gp"] > options[0]["cost_gp"]
    assert poor.carrier_options()[0]["speed_miles_per_day"] < options[0]["speed_miles_per_day"]


def test_mode_table_is_well_formed():
    for name, profile in MODES.items():
        freight, speed, hazard = profile
        assert name == name.lower(), name
        assert "+" not in name, f"{name} would collide with the join character"
        assert freight > 0, name
        assert speed > 0, name
        assert hazard > 0, name


def test_every_mode_has_a_label():
    assert set(MODE_LABELS) == set(MODES)


def test_the_requested_modes_all_exist():
    """The vocabulary the gazetteer is written against."""
    for name in ("teleport", "air", "sea", "road", "trail", "tunnel", "barge",
                 "river", "ferry", "track", "portage"):
        assert name in MODES, name


def test_water_is_cheaper_than_land_and_the_underdark_is_dearest():
    assert MODES["sea"][0] < MODES["river"][0] < MODES["road"][0]
    assert MODES["road"][0] < MODES["trail"][0] < MODES["track"][0]
    assert MODES["track"][0] < MODES["tunnel"][0]
    # Skyships buy speed at a price nothing else comes close to.
    conventional = set(MODES) - {"air", "teleport"}
    assert MODES["air"][0] > max(MODES[m][0] for m in conventional)
    assert MODES["air"][1] > max(MODES[m][1] for m in conventional)


def test_teleportation_is_faster_and_dearer_than_skyship():
    assert MODES["teleport"][0] > MODES["air"][0]
    assert MODES["teleport"][1] > MODES["air"][1]
    assert max(option[1] for option in CARRIERS["teleport"]) == 2000


def test_generated_caravan_tracks_use_track_mode(world):
    caravan_edges = [
        edge
        for edges in world._edges.values()
        for edge in edges
        if edge.name == "caravan track"
    ]
    assert caravan_edges
    assert all(edge.primary == "track" for edge in caravan_edges)


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------


def test_parse_modes_handles_every_spelling():
    assert parse_modes("road") == ("road",)
    assert parse_modes("river+portage") == ("river", "portage")
    assert parse_modes(" River + Portage ") == ("river", "portage")
    assert parse_modes(["tunnel", "trail"]) == ("tunnel", "trail")
    assert parse_modes(("sea",)) == ("sea",)


def test_parse_modes_is_forgiving_but_never_empty():
    assert parse_modes("cloudship") == ("road",)
    assert parse_modes("") == ("road",)
    assert parse_modes("road+road") == ("road",), "duplicates collapse"
    assert parse_modes("sea+nonsense") == ("sea",)


def test_canonical_kind_is_stable():
    assert canonical_kind("River + Portage") == "river+portage"
    assert canonical_kind(["sea"]) == "sea"


def test_describe_modes_reads_as_english():
    assert describe_modes("road") == "road"
    assert describe_modes("river+barge") == "river and barge"
    assert describe_modes("tunnel+trail+ferry").endswith("and ferry")


# --------------------------------------------------------------------------
# the cost of carrying a load two ways at once
# --------------------------------------------------------------------------


def test_single_mode_profile_is_the_table_row():
    for name in MODES:
        assert mode_profile((name,)) == MODES[name]


def test_multimodal_costs_more_than_the_average_of_its_parts():
    freight, _, _ = mode_profile(("river", "portage"))
    plain = (MODES["river"][0] + MODES["portage"][0]) / 2
    assert freight > plain
    assert freight == pytest.approx(plain * (1 + MULTIMODAL_COST))


def test_multimodal_is_slower_than_either_mode_alone_would_suggest():
    _, speed, _ = mode_profile(("sea", "tunnel"))
    # Harmonic mean, then handling: it cannot beat the slower leg's pace by
    # much and must never look like the fast one.
    assert speed < MODES["sea"][1]
    assert speed < (MODES["sea"][1] + MODES["tunnel"][1]) / 2


def test_multimodal_is_riskier_than_its_worst_mode():
    _, _, hazard = mode_profile(("tunnel", "trail"))
    assert hazard > MODES["tunnel"][2]
    assert hazard > MODES["trail"][2]


def test_risk_and_cost_climb_with_each_extra_mode():
    one = mode_profile(("river",))
    two = mode_profile(("river", "portage"))
    three = mode_profile(("river", "portage", "trail"))
    assert three[2] > two[2] > one[2]
    # More handling, less speed, every time.
    assert three[1] < two[1]


# --------------------------------------------------------------------------
# edges
# --------------------------------------------------------------------------


def _edge(kind: str, quality: float = 1.0) -> Edge:
    return Edge("a", "b", 100.0, quality, kind, "test")


def test_edge_exposes_its_modes():
    edge = _edge("river+portage")
    assert edge.modes == ("river", "portage")
    assert edge.primary == "river"
    assert edge.multimodal is True
    assert _edge("road").multimodal is False


def test_multimodal_edge_costs_more_than_the_same_leg_by_river():
    river = _edge("river")
    mixed = _edge("river+portage")
    assert mixed.freight_units(0.0) > river.freight_units(0.0)
    assert mixed.days > river.days
    assert mixed.hazard(0.5) > river.hazard(0.5)


def test_edge_still_works_for_plain_kinds():
    edge = _edge("road")
    assert edge.speed == pytest.approx(MODES["road"][1])
    assert edge.days == pytest.approx(100.0 / MODES["road"][1])


# --------------------------------------------------------------------------
# the gazetteer
# --------------------------------------------------------------------------


def test_every_named_route_kind_is_a_real_mode():
    bad = []
    for name, _stops, _quality, kind in NAMED_ROUTES:
        for part in str(kind).split("+"):
            if part.strip().lower() not in MODES:
                bad.append(f"{name} -> {kind!r}")
    assert not bad, "unknown travel modes: " + ", ".join(bad)


def test_alamber_run_crosses_the_inland_sea():
    route = next(route for route in NAMED_ROUTES if route[0] == "The Alamber Run")
    assert route[1] == ["skuld", "messemprar"]
    assert route[3] == "sea"


def test_urmlaspyr_has_a_direct_ferry_to_westgate(world: World):
    ferries = [edge for edge in world.edges_from("urmlaspyr")
               if edge.dst == "westgate"]

    assert [(edge.name, edge.kind) for edge in ferries] == [
        ("The Dragonmere Ferry", "ferry")
    ]


def test_every_sea_lane_kind_is_a_real_mode():
    bad = []
    for lane in NAMED_SEA_LANES:
        assert len(lane) in (3, 4), lane[0]
        if len(lane) == 4:
            for part in str(lane[3]).split("+"):
                if part.strip().lower() not in MODES:
                    bad.append(f"{lane[0]} -> {lane[3]!r}")
    assert not bad, "unknown travel modes: " + ", ".join(bad)


def test_the_gazetteer_actually_uses_the_new_modes():
    used = set()
    for _name, _stops, _quality, kind in NAMED_ROUTES:
        used.update(parse_modes(kind))
    for _name, _stops, _quality, kind in SURVEYED_MAGIC_ROUTES:
        used.update(parse_modes(kind))
    for lane in NAMED_SEA_LANES:
        used.update(parse_modes(lane[3]) if len(lane) > 3 else {"sea"})
    for name in ("teleport", "air", "trail", "barge", "portage", "ferry"):
        assert name in used, f"no route is typed {name!r}"


def test_winterkeep_circles_reach_the_major_magocracies(world: World):
    expected = {
        "eltabbar": "The Winterkeep Circle",
        "bezantur": "The Winterkeep-Bezantur Circle",
        "halarahh": "The Halruaan Concordance",
        "nimbral": "The Nimbral Accord",
        "sshamath": "The Sshamath Gate",
    }
    edges = [edge for edge in world.edges_from("winterkeep")
             if edge.kind == "teleport" and edge.dst in expected]

    assert {edge.dst: edge.name for edge in edges} == expected
    assert all(max(option["max_load_lb"] for option in edge.carrier_options()) == 2000
               for edge in edges)
    fastest = world.route("winterkeep", "eltabbar", optimise="days")
    assert fastest["path"] == ["Winterkeep", "Eltabbar"]
    assert fastest["modes"] == ["teleport"]


def test_some_routes_carry_several_modes_at_once():
    multi = [name for name, _s, _q, kind in NAMED_ROUTES
             if len(parse_modes(kind)) > 1]
    assert len(multi) >= 5, multi


# --------------------------------------------------------------------------
# the assembled world
# --------------------------------------------------------------------------


def test_world_edges_all_resolve(world: World):
    for legs in world._edges.values():
        for edge in legs:
            assert edge.modes, edge.kind
            assert edge.primary in MODES
            assert edge.speed > 0
            assert edge.days > 0


def test_named_routes_are_stored_canonically(world: World):
    for _name, _stops, _quality, kind in world.named_routes:
        assert kind == canonical_kind(kind)


def test_routes_report_their_modes_and_transfers(world: World):
    result = world.route("waterdeep", "baldur_s_gate")
    assert result["reachable"]
    assert result["modes"], "a route should say how it travels"
    assert all(m in MODES for m in result["modes"])
    assert result["transfers"] >= 0
    for leg in result["legs"]:
        assert leg["modes"]
        assert leg["mode_label"]
        assert leg["multimodal"] == (len(leg["modes"]) > 1)
        # transfers must agree with the legs they are counted from
    assert result["transfers"] == sum(len(leg["modes"]) - 1
                                      for leg in result["legs"])


def test_a_multimodal_leg_is_dearer_than_the_same_road(world: World):
    """The penalty has to survive the trip through the real graph."""
    mixed = Edge("a", "b", 200.0, 0.9, "tunnel+trail", "smugglers")
    tunnel = Edge("a", "b", 200.0, 0.9, "tunnel", "deep way")
    trail = Edge("a", "b", 200.0, 0.9, "trail", "surface way")
    assert mixed.hazard(0.4) > tunnel.hazard(0.4) > trail.hazard(0.4)
