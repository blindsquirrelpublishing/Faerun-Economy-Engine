"""Tests for realigning the markets from a surveyed poster index.

The survey is the fast path for the whole realignment problem: instead of
dragging 125 dots onto a poster by hand, a file states where every label sits
on the artwork and the engine reads it.  What matters here is that the reading
is faithful (the scale comes off the artwork, the anchor town does not move,
north is not flipped), that name matching is forgiving of spelling but not
reckless (a forest must never be mistaken for a market), and that a survey the
engine cannot use says so loudly instead of silently doing nothing.
"""

import json
import math

import pytest

from faerun import atlas
from faerun.calibration import load_control_points


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


class Fake:
    """The smallest thing that quacks like a Settlement."""

    def __init__(self, sid, name, x, y):
        self.id = sid
        self.name = name
        self.x = float(x)
        self.y = float(y)


def gazetteer():
    # Waterdeep sits where the real one does, so anchoring is testable.
    return [
        Fake("waterdeep", "Waterdeep", 600.0, 1200.0),
        Fake("baldur_s_gate", "Baldur's Gate", 700.0, 1500.0),
        Fake("alaghon", "Alagh\u00f4n", 1660.0, 1945.0),
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


def survey(entries, header=None):
    return {
        "coordinate_system": dict(HEADER, **(header or {})),
        "locations": entries,
    }


def place(name, east, north, category="settlement_or_site", **extra):
    item = {"name": name, "category": category,
            "east_miles": east, "north_miles": north}
    item.update(extra)
    return item


def write(tmp_path, payload):
    target = tmp_path / "locations.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# reading the header
# ---------------------------------------------------------------------------


def test_the_scale_bar_is_preferred_over_the_declared_ratio():
    # The bar is measured off the artwork itself, so it wins. Both agree in the
    # real file, so make them disagree to prove which one is used.
    header = dict(HEADER, pixels_per_unit=1.0)
    _ox, _oy, mpp, _sign = atlas._scale_from_header(header)
    assert mpp == pytest.approx(480.0 / (4246 - 3644))


def test_the_declared_ratio_is_the_fallback_with_no_scale_bar():
    header = dict(HEADER)
    header.pop("scale_bar")
    _ox, _oy, mpp, _sign = atlas._scale_from_header(header)
    assert mpp == pytest.approx(120.0 / 150.5)


def test_the_real_survey_scale_is_self_consistent():
    _ox, _oy, mpp, _sign = atlas._scale_from_header(HEADER)
    assert mpp == pytest.approx(120.0 / 150.5, rel=1e-3)


def test_darkhold_symbol_is_not_assigned_to_sshamath():
    survey_path = atlas.find_atlas()
    assert survey_path is not None
    payload = json.loads(survey_path.read_text(encoding="utf-8"))
    places = {entry["name"]: entry for entry in payload["locations"]}

    assert (places["Mantol-Derith"]["pixel_x"], places["Mantol-Derith"]["pixel_y"]) == (853, 231)
    assert (places["Darkhold"]["pixel_x"], places["Darkhold"]["pixel_y"]) == (1590, 945)
    for name in ("Mantol-Derith", "Darkhold"):
        assert places[name]["anchor"] == "symbol_center"
        assert places[name]["method"] == "manual_approximate"
    assert places["Sshamath"]["method"] == "engine_inferred"
    assert "pixel_x" not in places["Sshamath"]
    assert "pixel_y" not in places["Sshamath"]

    control_points = {point["id"]: point for point in load_control_points()}
    assert (control_points["mantol_derith"]["x"], control_points["mantol_derith"]["y"]) == (726.8, 840.4)
    assert (control_points["darkhold"]["x"], control_points["darkhold"]["y"]) == (1314.4, 1409.7)
    assert (control_points["sshamath"]["x"], control_points["sshamath"]["y"]) == (700.0, 1400.0)


def test_pixels_are_used_when_miles_are_absent(tmp_path):
    # A leaner survey may only record where the label sits on the image.
    entry = {"name": "Eastward", "category": "settlement_or_site",
             "pixel_x": 694 + 150.5, "pixel_y": 682}
    write(tmp_path, survey([entry]))
    data = atlas.load_atlas(str(tmp_path / "locations.json"))
    east = data["places"][0]["east"]
    assert east == pytest.approx(120.0, rel=1e-2)


def test_north_is_not_flipped(tmp_path):
    # Pixel rows grow downward but the survey counts north upward, so a label
    # above the origin must read as positive north.
    entry = {"name": "Northward", "category": "settlement_or_site",
             "pixel_x": 694, "pixel_y": 682 - 150.5}
    write(tmp_path, survey([entry]))
    data = atlas.load_atlas(str(tmp_path / "locations.json"))
    assert data["places"][0]["north"] == pytest.approx(120.0, rel=1e-2)


# ---------------------------------------------------------------------------
# name matching
# ---------------------------------------------------------------------------


def test_names_fold_case_accents_and_punctuation():
    assert atlas.normalise("Baldur's Gate") == atlas.normalise("baldurs gate")
    assert atlas.normalise("Alagh\u00f4n") == atlas.normalise("Alaghon")
    assert atlas.normalise("The Vast") == atlas.normalise("Vast")
    assert atlas.normalise("Corwell") == atlas.normalise("Caer Corwell")


def test_caer_corwell_survey_marker_beats_the_inferred_duplicate():
    index = atlas._place_index([
        dict(place("Caer Corwell", -169.0, -717.6, method="manual_approximate"),
             key=atlas.normalise("Caer Corwell"), east=-169.0, north=-717.6),
        dict(place("Corwell", -403.9, -53.9, method="engine_inferred"),
             key=atlas.normalise("Corwell"), east=-403.9, north=-53.9),
    ])

    assert index[atlas.normalise("Corwell")]["name"] == "Caer Corwell"
    assert index[atlas.normalise("Corwell")]["method"] == "manual_approximate"


def test_a_town_beginning_with_the_is_not_mangled():
    # "Thentia" is a real market on the Moonsea; a naive leading-"the" strip
    # would fold it to "ntia" and quietly wreck the match.
    assert atlas.normalise("Thentia") == "thentia"
    assert atlas.normalise("Thesk") == "thesk"
    assert atlas.normalise("Theymarsh") == "theymarsh"


def test_a_forest_is_never_mistaken_for_a_market():
    # Plenty of Realms forests share a name with a town; a label centre for a
    # wood is not a place to put a market.
    index = atlas._place_index([
        place("Cormanthor", 10.0, 10.0, category="geographic_feature"),
    ])
    assert "cormanthor" not in index


def test_a_settlement_beats_a_feature_of_the_same_name():
    index = atlas._place_index([
        place("Mistledale", 10.0, 10.0, category="geographic_feature"),
        place("Mistledale", 20.0, 20.0, category="settlement_or_site"),
    ])
    assert index["mistledale"]["east"] == 20.0


def test_a_survey_with_no_categories_is_still_usable():
    index = atlas._place_index([place("Elturel", 5.0, 5.0, category="")])
    assert "elturel" in index


# ---------------------------------------------------------------------------
# alignment
# ---------------------------------------------------------------------------


def test_the_anchor_town_does_not_move(tmp_path):
    # Pinning the origin is what stops an alignment sliding the whole world
    # sideways.  Give the origin a non-zero reading to prove it is honoured.
    write(tmp_path, survey([
        place("Waterdeep", 40.0, 40.0),
        place("Baldur's Gate", 312.7, -338.7),
    ]))
    data = atlas.load_atlas(str(tmp_path / "locations.json"))
    report = atlas.align(gazetteer(), atlas=data)

    by_name = {m["name"]: m for m in report["matched"]}
    assert by_name["Waterdeep"]["x"] == pytest.approx(600.0)
    assert by_name["Waterdeep"]["y"] == pytest.approx(1200.0)
    # 272.7 miles east and 378.7 south of Waterdeep, once the origin offset is
    # taken out.
    assert by_name["Baldur's Gate"]["x"] == pytest.approx(872.7)
    assert by_name["Baldur's Gate"]["y"] == pytest.approx(1578.7)


def test_north_becomes_smaller_y():
    # The engine counts y southward down the page while the survey counts north
    # upward.  Getting this backwards would mirror the whole continent, so pin
    # it: a town 100 miles north of the anchor must sit 100 units *above* it.
    markets = [
        Fake("waterdeep", "Waterdeep", 600.0, 1200.0),
        Fake("uphill", "Uphill", 0.0, 0.0),
    ]
    data = {"places": [
        place("Waterdeep", 0.0, 0.0),
        place("Uphill", 0.0, 100.0),
    ], "origin_name": "Waterdeep", "count": 2, "path": ""}
    report = atlas.align(markets, atlas=data)
    by_name = {m["name"]: m for m in report["matched"]}
    assert by_name["Uphill"]["y"] == pytest.approx(1100.0)
    assert by_name["Uphill"]["x"] == pytest.approx(600.0)


def test_unsurveyed_markets_are_reported_and_left_alone(tmp_path):
    write(tmp_path, survey([place("Waterdeep", 0.0, 0.0)]))
    data = atlas.load_atlas(str(tmp_path / "locations.json"))
    report = atlas.align(gazetteer(), atlas=data)
    assert "Nowhere" in report["missing"]
    assert [m["name"] for m in report["matched"]] == ["Waterdeep"]


def test_inferred_coordinates_are_matched_without_being_called_surveyed(tmp_path):
    write(tmp_path, survey([
        place("Waterdeep", 0.0, 0.0, method="manual_approximate"),
        place("Nowhere", 300.0, 300.0, method="engine_inferred"),
    ]))
    data = atlas.load_atlas(str(tmp_path / "locations.json"))
    report = atlas.align(gazetteer(), atlas=data)

    assert report["inferred"] == ["Nowhere"]
    assert report["surveyed"] == 1
    assert "Nowhere" not in report["missing"]


def test_an_anchor_the_gazetteer_lacks_is_an_error():
    data = {"places": [place("Elsewhere", 0.0, 0.0)],
            "origin_name": "Elsewhere", "count": 1, "path": ""}
    with pytest.raises(atlas.AtlasError):
        atlas.align(gazetteer(), atlas=data)


def test_control_points_are_ready_to_save(tmp_path):
    write(tmp_path, survey([
        place("Waterdeep", 0.0, 0.0),
        place("Baldur's Gate", 272.7, -378.7),
    ]))
    data = atlas.load_atlas(str(tmp_path / "locations.json"))
    points = atlas.control_points(gazetteer(), atlas=data)
    assert {p["id"] for p in points} == {"waterdeep", "baldur_s_gate"}
    for p in points:
        assert set(p) == {"id", "x", "y"}
        assert isinstance(p["x"], float) and isinstance(p["y"], float)


# ---------------------------------------------------------------------------
# failure reporting
# ---------------------------------------------------------------------------


def test_a_broken_survey_complains_rather_than_going_quiet(tmp_path):
    target = tmp_path / "locations.json"
    target.write_text("{not json at all", encoding="utf-8")
    with pytest.raises(atlas.AtlasError):
        atlas.load_atlas(str(target))


def test_no_survey_at_all_is_simply_absent(tmp_path):
    assert atlas.load_atlas(str(tmp_path / "nothing.json")) is None


def test_atlas_info_reports_where_it_looked(tmp_path):
    info = atlas.atlas_info(str(tmp_path / "nothing.json"))
    assert info["available"] is False
    assert info["searched"]


# ---------------------------------------------------------------------------
# the shipped survey, if the user has supplied one
# ---------------------------------------------------------------------------


def test_the_shipped_survey_reproduces_canon_distances():
    found = atlas.find_atlas()
    if found is None:
        pytest.skip("no survey supplied in maps/")
    data = atlas.load_atlas()
    index = atlas._place_index(data["places"])

    def apart(a, b):
        p, q = index[atlas.normalise(a)], index[atlas.normalise(b)]
        return math.hypot(p["east"] - q["east"], p["north"] - q["north"])

    # Waterdeep to Neverwinter is about 250 miles up the Sword Coast; if the
    # scale or the axes were wrong this is the first thing that would break.
    assert apart("Waterdeep", "Neverwinter") == pytest.approx(250.0, abs=60.0)
    # Baldur's Gate to Elturel is a few days up the Chionthar.
    assert apart("Baldur's Gate", "Elturel") == pytest.approx(220.0, abs=60.0)


def test_the_shipped_survey_aligns_most_of_the_gazetteer():
    if atlas.find_atlas() is None:
        pytest.skip("no survey supplied in maps/")
    from faerun.data.settlements import SETTLEMENTS

    report = atlas.align(list(SETTLEMENTS))
    # The survey indexes several hundred labels, so it should recognise the
    # bulk of the gazetteer.  A collapse here means name matching regressed.
    assert report["count"] >= len(SETTLEMENTS) // 2
    assert report["anchor"] == "Waterdeep"
