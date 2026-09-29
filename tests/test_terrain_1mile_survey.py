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


def test_the_legend_panel_is_not_surveyed_as_terrain(survey):
    """The printed legend and title sit over the south-eastern ocean."""
    assert set(window(survey, (2900, 3100), (-1900, -1400))) == {"U"}
