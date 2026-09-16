"""Tests for the two things the survey gives us beyond moving the markets.

The first is the poster itself: the survey records which pixel it measured from
and how many miles a pixel covers, so the whole image can be laid down in world
coordinates instead of being nudged into place with four sliders.  The second is
the several hundred towns the survey names that the economy never modelled - the
map was drawn with 125 markets on it and the poster shows far more, so the rest
ride along as plain dots.

What matters here is that the poster's corners are worked out from the anchor
rather than guessed, that the extra towns never shadow a real market, and that
they are drawn in whatever space the *map* is currently in - which is not the
survey's space until the realignment has actually been applied.
"""

import json
import math

import pytest

from faerun import atlas, mapdata


class Fake:
    """The smallest thing that quacks like a Settlement."""

    def __init__(self, sid, name, x, y):
        self.id = sid
        self.name = name
        self.x = float(x)
        self.y = float(y)


def gazetteer():
    return [
        Fake("waterdeep", "Waterdeep", 600.0, 1200.0),
        Fake("baldur_s_gate", "Baldur's Gate", 700.0, 1500.0),
        Fake("nowhere", "Nowhere", 900.0, 900.0),
    ]


HEADER = {
    "source_image": "Faerun Hires.jpg",
    "image_width": 4763,
    "image_height": 3185,
    "origin_name": "Waterdeep",
    "origin_pixel": {"x": 694, "y": 682},
    "positive_x": "east",
    "positive_y": "north",
    "miles_per_unit": 120,
    "pixels_per_unit": 150.5,
    "scale_bar": {"start_x": 3644, "end_x": 4246, "miles": 480},
}

MPP = 480.0 / (4246 - 3644)


def place(name, east, north, category="settlement_or_site"):
    return {"name": name, "category": category,
            "east_miles": east, "north_miles": north}


def loaded(tmp_path, entries, header=None):
    """Write a survey and read it back the way the engine would."""
    payload = {
        "coordinate_system": dict(HEADER, **(header or {})),
        "locations": entries,
    }
    target = tmp_path / "locations.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return atlas.load_atlas(str(target))


WATERDEEP = place("Waterdeep", 0, 0)


# ---------------------------------------------------------------------------
# placing the poster itself
# ---------------------------------------------------------------------------


def test_the_poster_corners_are_measured_from_the_anchor(tmp_path):
    data = loaded(tmp_path, [WATERDEEP])
    fit = atlas.underlay_placement(gazetteer(), data)

    assert fit["available"]
    # Waterdeep is 694px from the left edge and 682px down, and it lives at
    # (600, 1200), so the top-left corner is that far back from it.
    assert fit["x"] == pytest.approx(600 - 694 * MPP, abs=0.2)
    assert fit["y"] == pytest.approx(1200 - 682 * MPP, abs=0.2)
    assert fit["widthMiles"] == pytest.approx(4763 * MPP, abs=0.2)
    assert fit["heightMiles"] == pytest.approx(3185 * MPP, abs=0.2)
    assert not fit["flipped"]


def test_the_anchor_pixel_lands_on_the_anchor_town(tmp_path):
    """The whole point: the poster's Waterdeep must sit on ours."""
    data = loaded(tmp_path, [WATERDEEP])
    fit = atlas.underlay_placement(gazetteer(), data)

    mpp_x = fit["widthMiles"] / fit["imageWidth"]
    mpp_y = fit["heightMiles"] / fit["imageHeight"]
    assert fit["x"] + 694 * mpp_x == pytest.approx(600, abs=0.3)
    assert fit["y"] + 682 * mpp_y == pytest.approx(1200, abs=0.3)


def test_a_southward_survey_still_gives_an_upright_rectangle(tmp_path):
    data = loaded(tmp_path, [WATERDEEP], header={"positive_y": "south"})
    fit = atlas.underlay_placement(gazetteer(), data)

    assert fit["flipped"]
    assert fit["widthMiles"] > 0
    assert fit["heightMiles"] > 0


def test_a_survey_with_no_image_size_declines_to_place_the_poster(tmp_path):
    data = loaded(tmp_path, [WATERDEEP],
                  header={"image_width": None, "image_height": None})
    fit = atlas.underlay_placement(gazetteer(), data)

    assert not fit["available"]
    assert "size" in fit["error"]


def test_an_anchor_the_gazetteer_lacks_is_reported_not_raised(tmp_path):
    """An overlay must never take the map screen down with it."""
    data = loaded(tmp_path, [WATERDEEP], header={"origin_name": "Myth Drannor"})
    fit = atlas.underlay_placement(gazetteer(), data)

    assert not fit["available"]
    assert "Myth Drannor" in fit["error"]


def test_a_missing_anchor_is_still_an_error_for_the_markets(tmp_path):
    data = loaded(tmp_path, [WATERDEEP], header={"origin_name": "Myth Drannor"})
    with pytest.raises(atlas.AtlasError):
        atlas._survey_frame(gazetteer(), data)


# ---------------------------------------------------------------------------
# the towns the economy does not model
# ---------------------------------------------------------------------------


def test_surveyed_towns_exclude_the_markets_we_already_have(tmp_path):
    data = loaded(tmp_path, [
        WATERDEEP,
        place("Baldur's Gate", 100, -300),
        place("Daggerford", 0, -110),
    ])
    names = [p["name"] for p in atlas.surveyed_places(gazetteer(), data)]

    assert names == ["Daggerford"]


def test_a_forest_is_not_offered_as_a_town(tmp_path):
    data = loaded(tmp_path, [
        WATERDEEP,
        place("Kryptgarden Forest", 30, 90, category="geographic_feature"),
    ])
    assert atlas.surveyed_places(gazetteer(), data) == []


def test_a_surveyed_town_is_placed_in_miles_from_the_anchor(tmp_path):
    data = loaded(tmp_path, [WATERDEEP, place("Daggerford", 12, -110)])
    got = atlas.surveyed_places(gazetteer(), data)[0]

    # East grows with x; north counts against y, because y runs down the page.
    assert got["x"] == pytest.approx(612.0)
    assert got["y"] == pytest.approx(1310.0)


def test_the_same_town_twice_is_only_drawn_once(tmp_path):
    data = loaded(tmp_path, [
        WATERDEEP,
        place("Daggerford", 12, -110),
        place("daggerford", 13, -111),
    ])
    assert len(atlas.surveyed_places(gazetteer(), data)) == 1


# ---------------------------------------------------------------------------
# drawing them in the space the map is actually in
# ---------------------------------------------------------------------------


def test_extra_towns_are_brought_back_to_the_shipped_coordinates(
        tmp_path, monkeypatch):
    """Until the survey is applied, the map is still on its old coordinates.

    Dropping the extra towns in at their surveyed positions would leave them
    hovering in a cloud several hundred miles from the markets they belong
    beside, so they have to come back through the reverse of the very fit that
    would move those markets.
    """
    # Baldur's Gate is surveyed 300 miles east of where the gazetteer has it,
    # so the survey frame is badly out of step with the shipped map.
    data = loaded(tmp_path, [
        WATERDEEP,
        place("Baldur's Gate", 400, -300),
        place("Nowhere", 300, 300),
        place("Beregost", 400, -280),
    ])
    monkeypatch.setattr(atlas, "load_atlas", lambda *a, **k: data)
    monkeypatch.setattr(mapdata, "load_control_points", lambda *a, **k: [])

    got = mapdata.surveyed_places(gazetteer())
    assert [p["name"] for p in got] == ["Beregost"]

    # Beregost is surveyed 20 miles north of Baldur's Gate, so it belongs beside
    # wherever Baldur's Gate actually sits on this map - not beside the survey's
    # idea of it, 300 miles further east.
    x, y = got[0]["x"], got[0]["y"]
    near_gate = math.hypot(x - 700.0, y - 1480.0)
    near_survey = math.hypot(x - 1000.0, y - 1480.0)
    assert near_gate < near_survey
    assert near_gate < 60.0


def test_with_a_calibration_in_force_the_survey_space_is_used_as_is(
        tmp_path, monkeypatch):
    data = loaded(tmp_path, [
        WATERDEEP,
        place("Baldur's Gate", 400, -300),
        place("Beregost", 400, -280),
    ])
    monkeypatch.setattr(atlas, "load_atlas", lambda *a, **k: data)
    monkeypatch.setattr(mapdata, "load_control_points",
                        lambda *a, **k: [{"id": "waterdeep", "x": 600, "y": 1200}])

    got = mapdata.surveyed_places(gazetteer())
    # Straight out of the survey: 400 miles east of Waterdeep and 280 south.
    assert got[0]["x"] == pytest.approx(1000.0)
    assert got[0]["y"] == pytest.approx(1480.0)


def test_a_broken_survey_never_costs_us_the_map(monkeypatch):
    from faerun import get_world

    def boom(*a, **k):
        raise RuntimeError("the survey is nonsense")

    monkeypatch.setattr(mapdata, "surveyed_places", boom)
    payload = mapdata.map_payload(get_world())
    assert payload["places"] == []
    # The map still arrives in full, which is the point.
    assert payload["settlements"]
    assert payload["height"]


def test_the_map_payload_carries_the_extra_towns():
    from faerun import get_world

    payload = mapdata.map_payload(get_world())
    assert "places" in payload
    known = {p["name"] for p in payload["settlements"]}
    for p in payload["places"]:
        assert p["name"] not in known
        assert isinstance(p["x"], (int, float))
        assert isinstance(p["y"], (int, float))
    assert payload["routes"]
    assert all(route["days"] > 0 for route in payload["routes"])
