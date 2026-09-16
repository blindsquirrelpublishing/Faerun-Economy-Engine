"""The map frame and its heightfield resize to cover the poster.

The hand-drawn terrain was authored into a tall, narrow window.  A real poster
map of the Realms is neither: it is wider than it is tall and it reaches a long
way further east.  Laid on top of the old frame, three quarters of the image
hung off the edge with no ground underneath it.  These tests pin down that the
frame grows to hold the whole poster, that the heightfield grows with it, and
that the cells stay square while it happens.
"""

import pytest

from faerun import mapdata


@pytest.fixture(autouse=True)
def restore_frame():
    """The frame lives in module globals, so every test must put it back."""
    saved = (mapdata.BOUNDS, mapdata.GRID_W, mapdata.GRID_H)
    yield
    mapdata.BOUNDS, mapdata.GRID_W, mapdata.GRID_H = saved


class Town:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def no_poster(monkeypatch):
    monkeypatch.setattr(mapdata, "poster_frame", lambda *a, **k: None)


def with_poster(monkeypatch, rect):
    monkeypatch.setattr(mapdata, "poster_frame", lambda *a, **k: rect)


# ---------------------------------------------------------------------------
# sizing the grid
# ---------------------------------------------------------------------------


def test_cells_come_out_square():
    w, h = mapdata._grid_for(3800.0, 3120.0)
    cw = 3800.0 / w
    ch = 3120.0 / h
    assert abs(cw - ch) < 0.1 * max(cw, ch)


def test_a_wide_frame_gets_a_wide_grid():
    """The old code capped each axis on its own, which made cells oblong."""
    w, h = mapdata._grid_for(3800.0, 2540.0)
    assert w > h, "a landscape frame should have more columns than rows"
    cw = 3800.0 / w
    ch = 2540.0 / h
    assert abs(cw - ch) < 0.1 * max(cw, ch)


def test_the_field_stays_inside_its_budget():
    # A frame nobody should ever produce, to prove the ceiling holds.
    w, h = mapdata._grid_for(40000.0, 40000.0)
    assert w * h <= mapdata.MAX_CELLS
    assert w <= mapdata.MAX_GRID_W and h <= mapdata.MAX_GRID_H
    # Square even under the ceiling: the reduction is applied to both axes.
    assert w == h


def test_the_shipped_frame_still_gets_the_shipped_field():
    west, north, east, south = mapdata.SHIPPED_BOUNDS
    w, h = mapdata._grid_for(east - west, south - north)
    assert (w, h) == (mapdata.SHIPPED_GRID_W, mapdata.SHIPPED_GRID_H)


# ---------------------------------------------------------------------------
# resolving the frame
# ---------------------------------------------------------------------------


def test_nothing_to_accommodate_leaves_the_shipped_frame_alone(monkeypatch):
    no_poster(monkeypatch)
    mapdata._resolve_frame([Town(9999.0, 9999.0)], False)

    # Uncalibrated the markets do not move the frame, however far out they sit.
    assert mapdata.BOUNDS == mapdata.SHIPPED_BOUNDS
    assert (mapdata.GRID_W, mapdata.GRID_H) == \
        (mapdata.SHIPPED_GRID_W, mapdata.SHIPPED_GRID_H)


def test_the_frame_stretches_to_cover_the_poster(monkeypatch):
    # Roughly what the real survey computes: wider than the shipped window,
    # much further east, and starting south of its northern edge.
    rect = (46.6, 656.2, 3844.4, 3195.7)
    with_poster(monkeypatch, rect)
    mapdata._resolve_frame([], False)

    west, north, east, south = mapdata.BOUNDS
    assert west <= rect[0] and east >= rect[2], "poster hangs off east or west"
    assert north <= rect[1] and south >= rect[3], "poster hangs off top or foot"

    # Growing only: the hand-drawn terrain must keep its ground too.
    assert west <= mapdata.SHIPPED_BOUNDS[0]
    assert north <= mapdata.SHIPPED_BOUNDS[1]
    assert east >= mapdata.SHIPPED_BOUNDS[2]
    assert south >= mapdata.SHIPPED_BOUNDS[3]


def test_the_grid_follows_the_frame(monkeypatch):
    rect = (46.6, 656.2, 3844.4, 3195.7)
    with_poster(monkeypatch, rect)
    mapdata._resolve_frame([], False)

    west, north, east, south = mapdata.BOUNDS
    cw = (east - west) / mapdata.GRID_W
    ch = (south - north) / mapdata.GRID_H
    assert mapdata.GRID_W > mapdata.SHIPPED_GRID_W, "the field did not widen"
    assert abs(cw - ch) < 0.1 * max(cw, ch), "cells went oblong"
    # Detail must not quietly collapse: cells stay in the same ballpark as the
    # 20.8 miles the terrain was drawn for.
    assert cw < mapdata.CELL_MILES * 1.5
    assert mapdata.GRID_W * mapdata.GRID_H <= mapdata.MAX_CELLS


def test_a_realignment_still_pulls_the_frame_out(monkeypatch):
    no_poster(monkeypatch)
    mapdata._resolve_frame([Town(4200.0, 1200.0)], True)

    assert mapdata.BOUNDS[2] >= 4200.0 + mapdata.FRAME_MARGIN
    assert mapdata.BOUNDS[0] <= mapdata.SHIPPED_BOUNDS[0]
    assert mapdata.GRID_W > mapdata.SHIPPED_GRID_W


def test_the_poster_and_the_markets_are_both_accommodated(monkeypatch):
    with_poster(monkeypatch, (46.6, 656.2, 3844.4, 3195.7))
    mapdata._resolve_frame([Town(4200.0, 3600.0)], True)

    west, north, east, south = mapdata.BOUNDS
    assert east >= 4200.0 + mapdata.FRAME_MARGIN, "the market fell off"
    assert south >= 3600.0 + mapdata.FRAME_MARGIN, "the market fell off"
    assert west <= 46.6, "the poster fell off"


# ---------------------------------------------------------------------------
# reading the poster's footprint
# ---------------------------------------------------------------------------


def test_a_broken_poster_never_costs_us_the_frame(monkeypatch):
    from faerun import atlas

    def boom(*a, **k):
        raise RuntimeError("the survey is nonsense")

    monkeypatch.setattr(atlas, "underlay_placement", boom)
    assert mapdata.poster_frame([]) is None

    # And the frame still resolves, rather than taking the map screen down.
    mapdata._resolve_frame([], False)
    assert mapdata.BOUNDS == mapdata.SHIPPED_BOUNDS


def test_an_unplaceable_poster_is_simply_no_poster(monkeypatch):
    from faerun import atlas

    monkeypatch.setattr(atlas, "underlay_placement",
                        lambda *a, **k: {"available": False, "error": "no survey"})
    assert mapdata.poster_frame([]) is None


def test_a_poster_with_no_size_is_no_poster(monkeypatch):
    from faerun import atlas

    monkeypatch.setattr(atlas, "underlay_placement", lambda *a, **k: {
        "available": True, "x": 10.0, "y": 20.0,
        "widthMiles": 0.0, "heightMiles": 100.0,
    })
    assert mapdata.poster_frame([]) is None


def test_a_placed_poster_becomes_a_rectangle(monkeypatch):
    from faerun import atlas

    monkeypatch.setattr(atlas, "underlay_placement", lambda *a, **k: {
        "available": True, "x": 10.0, "y": 20.0,
        "widthMiles": 100.0, "heightMiles": 200.0,
    })
    assert mapdata.poster_frame([]) == (10.0, 20.0, 110.0, 220.0)


# ---------------------------------------------------------------------------
# the cached heightfield has to notice
# ---------------------------------------------------------------------------


def test_dropping_a_poster_in_rebuilds_the_field(monkeypatch):
    """The cache key is the gazetteer, so the poster has to be folded in too.

    Otherwise the first field built without a poster would be served forever
    and the frame would never grow.
    """
    towns = [Town(600.0, 1200.0), Town(700.0, 1500.0)]
    for i, t in enumerate(towns):
        t.id = "t%d" % i
        t.landmass = "faerun"
        t.terrain = "plains"

    no_poster(monkeypatch)
    small = mapdata.terrain_grid(towns)
    assert tuple(small["bounds"]) == mapdata.SHIPPED_BOUNDS

    with_poster(monkeypatch, (46.6, 656.2, 3844.4, 3195.7))
    big = mapdata.terrain_grid(towns)
    assert big is not small, "the stale field was served"
    assert big["bounds"][2] >= 3844.4
    assert big["grid"][0] > small["grid"][0]
