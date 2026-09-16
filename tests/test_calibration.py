"""Tests for the map realignment warp.

The point of calibration is that a few hand-placed markets drag the rest of the
gazetteer with them.  The properties worth pinning down are therefore: it is
exact at the points the user placed, it is smooth in between, it never
compounds when re-run, and clearing it puts everything back.
"""

import json
import math

import pytest

from faerun.calibration import (
    apply_calibration,
    base_coordinates,
    build_warp,
    load_control_points,
    save_control_points,
    warp_for,
)
from faerun.data.settlements import SETTLEMENTS_BY_ID


class Fake:
    """The smallest thing that quacks like a Settlement for the warp."""

    def __init__(self, sid, x, y):
        self.id = sid
        self.name = sid.title()
        self.x = float(x)
        self.y = float(y)


def gazetteer():
    return [
        Fake("alpha", 0.0, 0.0),
        Fake("beta", 100.0, 0.0),
        Fake("gamma", 0.0, 100.0),
        Fake("delta", 100.0, 100.0),
        Fake("middle", 50.0, 50.0),
    ]


# ---------------------------------------------------------------------------
# the warp itself
# ---------------------------------------------------------------------------


def test_no_control_points_is_the_identity():
    warp = build_warp([])
    assert warp(123.0, 456.0) == (123.0, 456.0)


def test_one_control_point_is_a_pure_translation():
    warp = build_warp([((10.0, 10.0), (30.0, 40.0))])
    assert warp(0.0, 0.0) == pytest.approx((20.0, 30.0))
    assert warp(10.0, 10.0) == pytest.approx((30.0, 40.0))


def test_warp_is_exact_at_every_control_point():
    # Deliberately inconsistent targets: no affine transform can satisfy all
    # four, so this only passes if the residual pass is doing its job.
    pairs = [
        ((0.0, 0.0), (5.0, -5.0)),
        ((100.0, 0.0), (140.0, 10.0)),
        ((0.0, 100.0), (-20.0, 90.0)),
        ((100.0, 100.0), (130.0, 160.0)),
    ]
    warp = build_warp(pairs)
    for src, dst in pairs:
        got = warp(src[0], src[1])
        assert got == pytest.approx(dst, abs=1e-6)


def test_warp_is_continuous_near_a_control_point():
    pairs = [
        ((0.0, 0.0), (0.0, 0.0)),
        ((100.0, 0.0), (100.0, 0.0)),
        ((0.0, 100.0), (0.0, 100.0)),
        ((50.0, 50.0), (70.0, 50.0)),
    ]
    warp = build_warp(pairs)
    near = warp(50.0, 50.5)
    exact = warp(50.0, 50.0)
    assert math.dist(near, exact) < 5.0


def test_collinear_control_points_fall_back_instead_of_crashing():
    # Three points on one line make the affine normal matrix singular.
    pairs = [
        ((0.0, 0.0), (10.0, 0.0)),
        ((100.0, 0.0), (110.0, 0.0)),
        ((200.0, 0.0), (210.0, 0.0)),
    ]
    warp = build_warp(pairs)
    for src, dst in pairs:
        assert warp(src[0], src[1]) == pytest.approx(dst, abs=1e-6)
    off = warp(100.0, 50.0)
    assert all(math.isfinite(v) for v in off)


def test_a_pure_shift_of_every_point_shifts_everything():
    pairs = [
        ((0.0, 0.0), (10.0, 20.0)),
        ((100.0, 0.0), (110.0, 20.0)),
        ((0.0, 100.0), (10.0, 120.0)),
    ]
    warp = build_warp(pairs)
    assert warp(50.0, 50.0) == pytest.approx((60.0, 70.0), abs=1e-6)


# ---------------------------------------------------------------------------
# applying it to a gazetteer
# ---------------------------------------------------------------------------


def test_apply_moves_the_control_point_exactly():
    towns = gazetteer()
    used = apply_calibration(towns, [{"id": "beta", "x": 160.0, "y": 0.0}])
    assert used == 1
    beta = [t for t in towns if t.id == "beta"][0]
    assert (beta.x, beta.y) == pytest.approx((160.0, 0.0))


def test_apply_carries_the_neighbours_along():
    towns = gazetteer()
    apply_calibration(towns, [
        {"id": "alpha", "x": 0.0, "y": 0.0},
        {"id": "beta", "x": 200.0, "y": 0.0},
        {"id": "gamma", "x": 0.0, "y": 100.0},
    ])
    middle = [t for t in towns if t.id == "middle"][0]
    # The east edge doubled away, so a town halfway across should follow.
    assert middle.x > 60.0


def test_recalibrating_replaces_rather_than_compounds():
    towns = gazetteer()
    points = [
        {"id": "alpha", "x": 10.0, "y": 10.0},
        {"id": "beta", "x": 110.0, "y": 10.0},
        {"id": "gamma", "x": 10.0, "y": 110.0},
    ]
    apply_calibration(towns, points)
    first = {t.id: (t.x, t.y) for t in towns}
    apply_calibration(towns, points)
    second = {t.id: (t.x, t.y) for t in towns}
    assert first == second


def test_empty_control_list_restores_the_shipped_coordinates():
    towns = gazetteer()
    shipped = {t.id: (t.x, t.y) for t in towns}
    apply_calibration(towns, [
        {"id": "alpha", "x": -50.0, "y": -50.0},
        {"id": "beta", "x": 300.0, "y": 0.0},
        {"id": "gamma", "x": 0.0, "y": 400.0},
    ])
    assert {t.id: (t.x, t.y) for t in towns} != shipped
    assert apply_calibration(towns, []) == 0
    assert {t.id: (t.x, t.y) for t in towns} == shipped


def test_unknown_ids_are_ignored_not_fatal():
    towns = gazetteer()
    used = apply_calibration(towns, [
        {"id": "atlantis", "x": 1.0, "y": 2.0},
        {"id": "beta", "x": 150.0, "y": 0.0},
    ])
    assert used == 1


def test_base_coordinates_survive_a_move():
    towns = gazetteer()
    before = base_coordinates(towns)
    apply_calibration(towns, [{"id": "beta", "x": 400.0, "y": 400.0}])
    after = base_coordinates(towns)
    assert before == after


def test_warp_for_skips_unresolvable_points():
    towns = gazetteer()
    warp = warp_for(towns, [{"id": "nowhere", "x": 5.0, "y": 5.0}])
    assert warp(7.0, 9.0) == (7.0, 9.0)


# ---------------------------------------------------------------------------
# persistence
# ---------------------------------------------------------------------------


def test_save_then_load_round_trip(tmp_path):
    target = tmp_path / "coords.json"
    save_control_points([{"id": "beta", "x": 160.04, "y": -3.0}], target)
    assert target.exists()
    back = load_control_points(target)
    assert back == [{"id": "beta", "x": 160.0, "y": -3.0}]


def test_saving_an_empty_list_deletes_the_file(tmp_path):
    target = tmp_path / "coords.json"
    save_control_points([{"id": "beta", "x": 1.0, "y": 2.0}], target)
    save_control_points([], target)
    assert not target.exists()
    assert load_control_points(target) == []


def test_missing_file_reads_as_uncalibrated(tmp_path):
    assert load_control_points(tmp_path / "absent.json") == []


def test_corrupt_file_degrades_instead_of_raising(tmp_path):
    target = tmp_path / "coords.json"
    target.write_text("{not json at all", encoding="utf-8")
    assert load_control_points(target) == []


def test_a_bare_list_is_accepted(tmp_path):
    target = tmp_path / "coords.json"
    target.write_text(json.dumps([{"id": "beta", "x": 1, "y": 2}]), encoding="utf-8")
    assert load_control_points(target) == [{"id": "beta", "x": 1.0, "y": 2.0}]


def test_junk_entries_are_dropped(tmp_path):
    target = tmp_path / "coords.json"
    target.write_text(json.dumps({"control": [
        {"id": "beta", "x": 1, "y": 2},
        {"id": "", "x": 1, "y": 2},
        {"id": "gamma", "x": "west", "y": 2},
        "nonsense",
    ]}), encoding="utf-8")
    assert load_control_points(target) == [{"id": "beta", "x": 1.0, "y": 2.0}]


def test_no_temporary_file_is_left_behind(tmp_path):
    target = tmp_path / "coords.json"
    save_control_points([{"id": "beta", "x": 1.0, "y": 2.0}], target)
    assert not list(tmp_path.glob("*.tmp"))


# ---------------------------------------------------------------------------
# the gazetteer corrections that prompted all this
# ---------------------------------------------------------------------------


# Read the *shipped* positions, not the current ones: whether the person
# running the tests happens to have a calibration saved is none of these
# assertions' business.
SHIPPED = base_coordinates(list(SETTLEMENTS_BY_ID.values()))
BY_NAME = {s.name: s.id for s in SETTLEMENTS_BY_ID.values()}


def at(name):
    return SHIPPED[BY_NAME[name]]


def x_of(name):
    return at(name)[0]


def gap(a, b):
    return math.dist(at(a), at(b))


def test_moonsea_north_shore_runs_west_to_east():
    # Zhentil Keep, Thentia, Melvaunt, Phlan in that order along the north
    # shore. The gazetteer used to have Thentia east of Melvaunt.
    xs = [x_of(n) for n in ["Zhentil Keep", "Thentia", "Melvaunt", "Phlan"]]
    assert xs == sorted(xs), xs


def test_aglarond_lies_west_of_thay():
    assert x_of("Velprintalar") < x_of("Bezantur")


def test_chondath_lies_west_of_turmish():
    assert x_of("Arrabar") < x_of("Hlath") < x_of("Alagh\u00f4n")


def test_westgate_sits_east_of_suzail_on_the_dragonmere():
    assert x_of("Westgate") > x_of("Suzail")
    # Roughly the length of the Dragonmere's south shore, not a stone's throw.
    assert 90 < gap("Westgate", "Suzail") < 220


def test_the_map_payload_carries_the_shipped_position_too():
    # The browser previews a realignment by warping from the shipped position.
    # Without bx/by it would warp an already-warped point and compound the fit.
    from faerun import get_world
    from faerun.mapdata import map_payload

    world = get_world()
    expected = base_coordinates(list(world.settlements.values()))
    pins = map_payload(world)["settlements"]
    assert pins
    for pin in pins:
        assert "bx" in pin and "by" in pin, pin["id"]
        assert (pin["bx"], pin["by"]) == expected[pin["id"]]
        if pin["id"] in SHIPPED:
            assert (pin["bx"], pin["by"]) == SHIPPED[pin["id"]]


def test_the_sword_coast_keeps_its_canonical_distances():
    # One world unit is one mile, so these are checkable against the sourcebooks.
    assert gap("Waterdeep", "Baldur's Gate") == pytest.approx(600, abs=90)
    assert gap("Waterdeep", "Neverwinter") == pytest.approx(250, abs=60)
    assert gap("Luskan", "Neverwinter") == pytest.approx(180, abs=60)
