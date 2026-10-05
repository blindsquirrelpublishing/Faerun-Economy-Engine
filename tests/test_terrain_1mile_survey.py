"""The one-mile poster survey is evidence about artwork, so it is checked as such.

The survey is built by tools/survey_terrain_1mile.py from a poster the user
supplies. These tests read the shipped result, not the poster, so they run
without the artwork present.
"""

import json
from pathlib import Path

import pytest

from faerun import mapdata

SURVEY = Path(__file__).resolve().parents[1] / "maps" / mapdata.FINE_TERRAIN_NAME

pytestmark = pytest.mark.skipif(
    not SURVEY.is_file(), reason="one-mile survey has not been built"
)


@pytest.fixture(scope="module")
def survey():
    return json.loads(SURVEY.read_text(encoding="utf-8"))


def window(survey, columns, rows):
    """Every terrain letter in an inclusive column/row box."""
    start = columns[0] - survey["column_min"]
    stop = columns[1] - survey["column_min"] + 1
    return "".join(
        survey["rows"][str(row)][start:stop] for row in range(rows[0], rows[1] + 1)
    )


def commonest(cells, ignore=""):
    counts = {}
    for letter in cells:
        if letter not in ignore:
            counts[letter] = counts.get(letter, 0) + 1
    return max(counts, key=counts.__getitem__)


def test_survey_covers_the_sheet_as_a_consistent_one_mile_grid(survey):
    width = survey["column_max"] - survey["column_min"] + 1
    height = survey["row_max"] - survey["row_min"] + 1

    assert survey["cell_miles"] == 1
    assert survey["frame"] == "FPS1:WD"
    assert survey["origin"] == "Waterdeep"
    assert (survey["width"], survey["height"]) == (width, height)
    assert survey["cell_count"] == width * height
    assert len(survey["rows"]) == height
    assert all(len(row) == width for row in survey["rows"].values())
    assert set("".join(survey["rows"].values())) <= set(survey["legend"])


def test_relief_and_ink_are_reported_for_every_cell(survey):
    for key, row in survey["rows"].items():
        assert len(survey["relief"][key]) == len(row)
        assert len(survey["ink"][key]) == len(row)
    joined = "".join(survey["relief"].values()) + "".join(survey["ink"].values())
    assert set(joined) <= set(survey["value_alphabet"])


def test_the_sea_is_read_and_inland_water_survives_it(survey):
    """Rivers and lakes must not be swallowed by the open-sea flood fill."""
    cells = "".join(survey["rows"].values())

    # The sheet is more land than ocean, so sea is not the commonest cell; it
    # is still a fifth of it, and the lakes and rivers are a class of their own.
    assert cells.count("S") / len(cells) > 0.20
    assert cells.count("W") > 100_000


def test_waterdeep_sits_on_its_own_shoreline(survey):
    around = window(survey, (-2, 2), (-2, 2))

    assert "S" in around
    assert set(around) - set("SW")


def test_lettering_did_not_turn_the_trackless_sea_into_land(survey):
    """"THE TRACKLESS SEA" is set in navy across the empty south-western ocean.

    Read naively that lettering is dark ink on blue and classifies as relief,
    which is the whole reason the survey masks labels before sampling colour.
    The window is chosen well clear of the Moonshae and Nelanther isles, which
    are real land in the middle of that ocean.
    """
    cells = window(survey, (-520, -250), (-1900, -1400))

    assert cells.count("S") / len(cells) > 0.99


def test_anauroch_reads_as_desert_and_chult_as_wooded(survey):
    assert commonest(window(survey, (620, 780), (300, 420))) == "D"
    # Chult is drawn as the dark green wash, which is the forest reading.
    assert commonest(window(survey, (200, 400), (-1800, -1650)), ignore="S") == "F"


def test_grassland_is_told_apart_from_forest(survey):
    """The poster draws Grasslands as a pale green wash and Forest as a darker
    one. Keying on greenness alone cannot separate them - the Grasslands swatch
    is *greener* on average than the Forest swatch, because forest is canopy
    over cream - so the survey splits them on lightness instead."""
    cells = "".join(survey["rows"].values())

    assert cells.count("G") > 200_000
    assert cells.count("F") > 200_000
    # Cormanthor and the Dalelands: open country beside a great wood.
    dales = window(survey, (1350, 1650), (-75, 225))
    assert "G" in dales and "F" in dales


def test_ice_is_confined_to_the_far_north(survey):
    southern = window(survey, (survey["column_min"], survey["column_max"]),
                      (survey["row_min"], 200))
    northern = window(survey, (survey["column_min"], survey["column_max"]),
                      (201, survey["row_max"]))

    assert northern.count("I") > 1000
    assert southern.count("I") < northern.count("I") / 20


def test_high_forest_consistency_preserves_water_and_edges():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import consistency_codes

    codes = np.full((51, 51), "F")
    codes[20:30, 20:30] = "G"
    codes[25, 25] = "W"
    codes[2, 2] = "G"
    image = np.full((51, 51, 3), (120, 160, 110), dtype=np.int16)
    result = consistency_codes(codes, image, image, np.zeros(codes.shape))
    assert result[21, 21] == "F"
    assert result[25, 25] == "W"
    assert result[2, 2] == "G"
    assert codes[21, 21] == "G"


def test_high_forest_rivers_require_two_sources_and_existing_water():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import consistency_codes

    codes = np.full((51, 51), "F")
    codes[25, 10] = "W"
    image = np.full((51, 51, 3), (120, 160, 110), dtype=np.int16)
    river_image = image.copy()
    river_image[25, 10:40] = (80, 120, 190)
    relief = np.zeros(codes.shape)
    result = consistency_codes(codes, river_image, river_image, relief)
    assert np.all(result[25, 10:40] == "W")
    assert np.array_equal(consistency_codes(codes, river_image, image, relief), codes)
    assert np.all(consistency_codes(np.full(codes.shape, "F"), river_image, river_image, relief) == "F")


def test_high_forest_mountain_gaps_need_relief_evidence():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import consistency_codes

    codes = np.full((51, 51), "P")
    codes[20:31, 20:31] = "M"
    codes[23:27, 23:27] = "H"
    image = np.full((51, 51, 3), (230, 230, 230), dtype=np.int16)
    relief = np.zeros(codes.shape)
    assert consistency_codes(codes, image, image, relief)[25, 25] == "H"
    relief[23:27, 23:27] = 0.5
    result = consistency_codes(codes, image, image, relief)
    assert result[25, 25] == "M"
    assert result[15, 15] == "P"


def test_bounding_regions_preserve_water_and_prioritize_mountains():
    pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import propose_regions

    payload = {"column_min": 0, "column_max": 6, "row_min": 0, "row_max": 6,
               "rows": {str(row): "GGGWGGG" for row in range(7)}}
    configuration = {"frame": "FPS1:WD", "coordinate_units": "miles", "regions": [
        {"name": "Forest", "terrain": "F", "replace": ["G"],
         "bounds": [1, 5, 1, 5], "polygon": [[1, 1], [5, 1], [5, 5], [1, 5]]},
        {"name": "Mountains", "terrain": "M", "replace": ["F", "G"],
         "bounds": [2, 4, 2, 4], "polygon": [[2, 2], [4, 2], [4, 4], [2, 4]]},
    ]}
    changes, _ = propose_regions(payload, configuration)
    assert all(change["column"] != 3 for change in changes)
    assert all(1 <= change["column"] <= 5 and 1 <= change["row"] <= 5 for change in changes)
    assert next(change for change in changes if (change["column"], change["row"]) == (2, 2))["after"] == "M"
    assert next(change for change in changes if (change["column"], change["row"]) == (1, 1))["after"] == "F"
    configuration["regions"][0]["replace"].append("W")
    with pytest.raises(ValueError, match="protected"):
        propose_regions(payload, configuration)


def test_forest_clears_stray_mountains_but_retains_named_ranges():
    pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import propose_regions, apply_changes

    payload = {"column_min": 0, "column_max": 6, "row_min": 0, "row_max": 6,
               "rows": {str(row): "MMMWMMM" for row in range(7)}}
    configuration = {"frame": "FPS1:WD", "coordinate_units": "miles", "regions": [
        {"name": "Forest", "terrain": "F", "replace": ["M"],
         "bounds": [1, 5, 1, 5], "polygon": [[1, 1], [5, 1], [5, 5], [1, 5]]},
        {"name": "Range", "terrain": "M", "replace": ["F"],
         "bounds": [2, 4, 2, 4], "polygon": [[2, 2], [4, 2], [4, 4], [2, 4]]},
    ]}
    changes, _ = propose_regions(payload, configuration)
    updated = apply_changes(payload, changes, consistency=True)
    assert updated["rows"]["1"][1] == "F"
    assert updated["rows"]["2"][2] == "M"
    assert updated["rows"]["0"] == payload["rows"]["0"]
    assert all(row[3] == "W" for row in updated["rows"].values())
    assert not propose_regions(updated, configuration)[0]


def test_forest_feather_requires_image_support_and_preserves_water(tmp_path, monkeypatch):
    pytest.importorskip("numpy")
    image_module = pytest.importorskip("PIL.Image")
    from tools import clean_terrain_interiors as cleanup

    folder = tmp_path / "maps"
    folder.mkdir()
    source = folder / "Fareun Topographical.png"
    image_module.new("RGB", (1533, 1026), (120, 160, 110)).save(source)
    monkeypatch.setattr(cleanup, "ROOT", tmp_path)
    payload = {"column_min": 0, "column_max": 10, "row_min": 0, "row_max": 10,
               "rows": {str(row): "MMMMMWMMMMM" for row in range(11)}}
    configuration = {"frame": "FPS1:WD", "coordinate_units": "miles", "regions": [
        {"name": "Forest", "terrain": "F", "replace": ["M"], "feather_miles": 2,
         "bounds": [4, 6, 4, 6], "polygon": [[4, 4], [6, 4], [6, 6], [4, 6]]},
    ]}
    changes, _ = cleanup.propose_regions(payload, configuration)
    assert any(change["column"] == 2 for change in changes)
    assert all(2 <= change["column"] <= 8 and 2 <= change["row"] <= 8 for change in changes)
    assert all(change["column"] != 5 for change in changes)
    image_module.new("RGB", (1533, 1026), (235, 235, 230)).save(source)
    unsupported, _ = cleanup.propose_regions(payload, configuration)
    assert all(4 <= change["column"] <= 6 and 4 <= change["row"] <= 6 for change in unsupported)


def test_boundary_controls_and_region_payload():
    from faerun.mapassets import MAP_ASSETS
    from faerun.web import map_boundary_regions

    for name in ("map.html", "terrain.html"):
        assert MAP_ASSETS[name][0].count('id="planar-boundaries"') == 1
    assert {region["id"] for region in map_boundary_regions()} >= {"high-forest", "lost-peaks", "star-mounts"}
    assert "drawPlanarBoundaries(firstColumn, lastColumn, firstRow, lastRow);" in MAP_ASSETS["map.js"][0]


def test_hill_regions_preserve_other_terrain():
    pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import propose_regions

    payload = {"column_min": 0, "column_max": 6, "row_min": 0, "row_max": 2,
               "rows": {str(row): "GPMWFTI" for row in range(3)}}
    configuration = {"frame": "FPS1:WD", "coordinate_units": "miles", "regions": [
        {"name": "Hills", "terrain": "H", "replace": ["G", "P", "D"],
         "bounds": [0, 6, 0, 2], "polygon": [[0, 0], [6, 0], [6, 2], [0, 2]]},
    ]}
    changes, _ = propose_regions(payload, configuration)
    assert len(changes) == 6
    assert all(change["before"] in "GP" and change["after"] == "H" for change in changes)


def test_planar_grid_and_land_detail_have_independent_controls():
    from faerun.mapassets import MAP_ASSETS

    for name in ("map.html", "terrain.html"):
        assert MAP_ASSETS[name][0].count('id="planar-land-detail"') == 1
        assert MAP_ASSETS[name][0].count('id="planar-cell"') == 1
    javascript = MAP_ASSETS["map.js"][0]
    assert "if (state.planarLandDetail === 1)" in javascript
    assert "if (state.planarCell === 1)" not in javascript
    assert "var cell = state.planarCell;" in javascript


def test_separate_cover_and_elevation_sources_do_not_invent_mountains():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import separated_source_codes

    codes = np.full((21, 21), "M")
    cover = np.full((21, 21, 3), (62, 132, 66), dtype=np.int16)
    elevation = np.full((21, 21, 3), (95, 190, 40), dtype=np.int16)
    elevation[3:7, 3:7] = (220, 110, 30)
    elevation[12:16, 12:16] = (210, 190, 40)
    elevation[17, 17] = (130, 130, 130)
    codes[10, 10] = "W"
    codes[10, 11] = "S"
    codes[10, 12] = "T"
    result, footprint = separated_source_codes(codes, cover, elevation)
    assert footprint.all()
    assert result[0, 0] == "F"
    assert result[4, 4] == "M"
    assert result[13, 13] == "H"
    assert result[17, 17] == "M"
    assert list(result[10, 10:13]) == ["W", "S", "T"]
    assert codes[0, 0] == "M"


def test_separate_sources_only_adjust_the_connected_high_forest():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import separated_source_codes

    codes = np.full((21, 21), "M")
    cover = np.full((21, 21, 3), (210, 232, 141), dtype=np.int16)
    cover[8:14, 8:14] = (62, 132, 66)
    cover[1:4, 1:4] = (62, 132, 66)
    elevation = np.full((21, 21, 3), (95, 190, 40), dtype=np.int16)
    result, footprint = separated_source_codes(codes, cover, elevation)
    assert result[10, 10] == "F"
    assert result[2, 2] == "M"
    assert result[17, 17] == "M"
    assert footprint.sum() == 36


def test_source_boundaries_have_correct_orientation_without_crop_edges():
    np = pytest.importorskip("numpy")
    pytest.importorskip("PIL")
    from tools.clean_terrain_interiors import boundary_segments

    mask = np.zeros((3, 3), bool)
    mask[1, 1] = True
    assert sorted(boundary_segments(mask, 10, 20)) == sorted([
        [11, 20, 12, 20], [11, 19, 12, 19], [11, 20, 11, 19], [12, 20, 12, 19],
    ])
    assert boundary_segments(np.ones((4, 4), bool), 0, 3) == []


def test_new_boundaries_supersede_manual_high_forest_outlines():
    from faerun.web import map_source_boundaries
    from faerun.mapassets import MAP_ASSETS

    boundaries = map_source_boundaries()
    assert set(boundaries["segments"]) == {"forest", "mountain", "water"}
    assert set(boundaries["supersedes"]) == {"high-forest", "lost-peaks", "star-mounts"}
    assert all(boundaries["segments"].values())
    assert "source.supersedes" in MAP_ASSETS["map.js"][0]


def test_the_legend_panel_is_not_surveyed_as_terrain(survey):
    """The printed legend and title sit over the south-eastern ocean."""
    assert set(window(survey, (2900, 3100), (-1900, -1400))) == {"U"}
