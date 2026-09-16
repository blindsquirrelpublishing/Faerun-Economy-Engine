"""Tests for rebuilding the map's scenery from the survey.

Realigning the markets is only half the job.  The coastline, the deserts and
the mountain ranges were drawn to fit the old hand-placed coordinates, and if
they are dragged along purely by the towns then the empty quarters go wrong -
which is unfortunate, because the empty quarters are where most of the map is.
Anauroch, the Great Glacier and Raurin have no markets in them at all, so
nothing local pins them down.

The survey names those features and knows where they sit, so they can be nailed
down directly.  What matters here is that pinning the scenery never disturbs a
market (the markets are the thing prices are computed from), and that a label
matched to the wrong feature is rejected rather than allowed to tear the
coastline apart.
"""

import json

import pytest

from faerun import atlas, mapdata
from faerun.calibration import build_warp


# ---------------------------------------------------------------------------
# what counts as a landmark
# ---------------------------------------------------------------------------


def test_every_named_sea_desert_and_range_is_a_landmark():
    names = [n for n, _p in mapdata.terrain_landmarks()]
    assert "Sea of Fallen Stars" in names
    assert "Anauroch" in names
    assert "Spine of the World" in names
    assert len(names) == len(mapdata.SEAS) + len(mapdata.ZONES) + \
        len(mapdata.RANGES)


def test_the_continent_itself_is_not_a_landmark():
    # "Faerun" is the whole landmass; the centre of it is not a place a poster
    # puts a label, so pinning to it would be meaningless.
    names = [n for n, _p in mapdata.terrain_landmarks()]
    assert "Faerun" not in names


def test_a_landmark_point_sits_inside_its_own_feature():
    marks = dict(mapdata.terrain_landmarks())
    poly = dict(mapdata.SEAS)["Moonsea"]
    x, y = marks["Moonsea"]
    assert min(p[0] for p in poly) <= x <= max(p[0] for p in poly)
    assert min(p[1] for p in poly) <= y <= max(p[1] for p in poly)


def test_surveyed_jungles_of_chult_anchor_is_land_and_jungle():
    point = (762, 2797)
    chult_zone = next(poly for name, kind, poly in mapdata.ZONES
                      if name == "Chult" and kind == "jungle")

    assert mapdata._inside(*point, mapdata.CHULT, mapdata._bbox(mapdata.CHULT))
    assert mapdata._inside(*point, chult_zone, mapdata._bbox(chult_zone))


# ---------------------------------------------------------------------------
# the survey supplies feature positions
# ---------------------------------------------------------------------------


class Fake:
    def __init__(self, sid, name, x, y):
        self.id = sid
        self.name = name
        self.x = float(x)
        self.y = float(y)


HEADER = {
    "origin_name": "Waterdeep",
    "origin_pixel": {"x": 694, "y": 682},
    "positive_x": "east",
    "positive_y": "north",
    "miles_per_unit": 120,
    "pixels_per_unit": 150.5,
    "scale_bar": {"start_x": 3644, "end_x": 4246, "miles": 480},
}


def loaded(tmp_path, entries):
    """A survey as `align` wants it: written out, then read back properly."""
    target = tmp_path / "locations.json"
    target.write_text(
        json.dumps({"coordinate_system": dict(HEADER), "locations": entries}),
        encoding="utf-8")
    return atlas.load_atlas(str(target))


WATERDEEP = {"name": "Waterdeep", "category": "settlement_or_site",
             "east_miles": 0, "north_miles": 0}


def test_features_are_reported_separately_from_markets(tmp_path):
    towns = [Fake("waterdeep", "Waterdeep", 600.0, 1200.0)]
    data = loaded(tmp_path, [
        WATERDEEP,
        {"name": "Anauroch", "category": "geographic_feature",
         "east_miles": 772.6, "north_miles": 292.8},
    ])
    report = atlas.align(towns, atlas=data)
    # The desert is not a market, so it must not appear among the matched
    # markets - but the map still needs to know where it is.
    assert [m["name"] for m in report["matched"]] == ["Waterdeep"]
    assert "anauroch" in report["features"]


def test_a_feature_is_placed_in_miles_from_the_anchor(tmp_path):
    towns = [Fake("waterdeep", "Waterdeep", 600.0, 1200.0)]
    data = loaded(tmp_path, [
        WATERDEEP,
        {"name": "Anauroch", "category": "geographic_feature",
         "east_miles": 772.6, "north_miles": 292.8},
    ])
    report = atlas.align(towns, atlas=data)
    spot = report["features"]["anauroch"]
    assert spot["x"] == pytest.approx(600.0 + 772.6, abs=0.2)
    # North is up on the poster and down in the engine, so north subtracts.
    assert spot["y"] == pytest.approx(1200.0 - 292.8, abs=0.2)


# ---------------------------------------------------------------------------
# the sanity check on a scenery anchor
# ---------------------------------------------------------------------------


def _one_feature(tmp_path, monkeypatch, name, offset=(0.0, 0.0)):
    """Point the map at a survey naming exactly one terrain feature."""
    towns = [Fake("waterdeep", "Waterdeep", 600.0, 1200.0)]
    marks = dict(mapdata.terrain_landmarks())
    fx, fy = marks[name]
    fx += offset[0]
    fy += offset[1]
    data = loaded(tmp_path, [
        WATERDEEP,
        {"name": name, "category": "geographic_feature",
         # invert the placement maths so the feature lands on (fx, fy)
         "east_miles": fx - 600.0, "north_miles": 1200.0 - fy},
    ])
    monkeypatch.setattr(atlas, "load_atlas", lambda *a, **k: data)
    return towns, marks


def test_the_report_splits_anchored_from_unsurveyed(tmp_path, monkeypatch):
    towns, marks = _one_feature(tmp_path, monkeypatch, "Anauroch")

    out = mapdata.terrain_alignment(towns, [])
    assert "Anauroch" in [a["name"] for a in out["anchored"]]
    assert out["landmarks"] == len(marks)
    # Everything else in the map is simply not in this toy survey.
    assert "Moonsea" in out["unsurveyed"]
    assert out["rejected"] == []


def test_a_wildly_misplaced_label_is_rejected(tmp_path, monkeypatch):
    """A name can match the wrong feature; the towns are the arbiter.

    With no control points the towns say nothing should move, so a survey
    claiming the desert is thousands of miles away is disagreeing with them and
    must be thrown out rather than allowed to drag the coastline with it.
    """
    far = mapdata.TERRAIN_ANCHOR_LIMIT * 4.0
    towns, _marks = _one_feature(tmp_path, monkeypatch, "Anauroch", (far, 0.0))

    out = mapdata.terrain_alignment(towns, [])
    assert "Anauroch" in [r["name"] for r in out["rejected"]]
    assert out["anchored"] == []


def test_a_rejected_anchor_is_left_out_of_the_warp(tmp_path, monkeypatch):
    towns, marks = _one_feature(
        tmp_path, monkeypatch, "Anauroch",
        (mapdata.TERRAIN_ANCHOR_LIMIT * 4.0, 0.0))
    coarse = build_warp([])
    assert mapdata._terrain_pairs(towns, coarse) == []

    # ...whereas a believable one is kept.
    towns, marks = _one_feature(tmp_path, monkeypatch, "Anauroch", (60.0, 0.0))
    pairs = mapdata._terrain_pairs(towns, coarse)
    assert len(pairs) == 1
    src, target = pairs[0]
    assert src == marks["Anauroch"]
    assert target[0] == pytest.approx(marks["Anauroch"][0] + 60.0, abs=0.2)


def test_a_bad_survey_never_stops_the_report(monkeypatch):
    def boom(*_a, **_k):
        raise RuntimeError("unreadable")

    monkeypatch.setattr(atlas, "load_atlas", boom)
    out = mapdata.terrain_alignment([Fake("w", "Waterdeep", 600.0, 1200.0)], [])
    assert out["landmarks"] > 0
    assert "error" in out


# ---------------------------------------------------------------------------
# the markets must survive the scenery being pinned
# ---------------------------------------------------------------------------


def test_pinning_the_scenery_does_not_move_a_single_market():
    """The whole point: prices come from distances between markets.

    Adding scenery anchors to the warp must refine where the ink goes without
    nudging a town, or freight costs would drift every time the map was
    redrawn.
    """
    towns = [
        Fake("waterdeep", "Waterdeep", 600.0, 1200.0),
        Fake("baldur_s_gate", "Baldur's Gate", 700.0, 1500.0),
        Fake("silverymoon", "Silverymoon", 1000.0, 800.0),
    ]
    points = [
        {"id": "waterdeep", "x": 600.0, "y": 1200.0},
        {"id": "baldur_s_gate", "x": 872.7, "y": 1578.7},
        {"id": "silverymoon", "x": 1180.0, "y": 690.0},
    ]
    pairs = [((t.x, t.y), (p["x"], p["y"]))
             for t, p in zip(towns, points)]

    marks = dict(mapdata.terrain_landmarks())
    scenery = [(marks["Anauroch"],
                (marks["Anauroch"][0] + 120.0, marks["Anauroch"][1] - 60.0))]

    warp = build_warp(pairs + scenery)
    for t, p in zip(towns, points):
        x, y = warp(t.x, t.y)
        assert x == pytest.approx(p["x"], abs=0.5), t.name
        assert y == pytest.approx(p["y"], abs=0.5), t.name

    # ...and the scenery went where it was told, too.
    sx, sy = warp(*marks["Anauroch"])
    assert sx == pytest.approx(marks["Anauroch"][0] + 120.0, abs=0.5)
    assert sy == pytest.approx(marks["Anauroch"][1] - 60.0, abs=0.5)


def test_an_uncalibrated_map_pins_nothing():
    # With no control points there is no realignment to follow, so the shipped
    # terrain must be handed back untouched.
    assert mapdata._warped_geometry(None)[3] is mapdata.RANGES


# ---------------------------------------------------------------------------
# against the real shipped survey
# ---------------------------------------------------------------------------


def test_the_real_survey_pins_the_great_empty_regions():
    """These are the places with no markets to carry them."""
    if not atlas.find_atlas():
        pytest.skip("no survey shipped")
    from faerun.data.settlements import SETTLEMENTS

    report = atlas.align(list(SETTLEMENTS))
    features = report["features"]
    for name in ("Anauroch", "Sea of Fallen Stars", "Cormanthor"):
        assert atlas.normalise(name) in features, name
