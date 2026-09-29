import json
import math

import pytest

from faerun import mapdata
from faerun.mapdata import terrain_detail
from faerun.world import World


def test_waterdeep_detail_is_a_bounded_one_mile_patch():
    detail = terrain_detail(World(), "Waterdeep", radius=250)

    # A one-mile patch is capped at 100 miles however wide the request was, so
    # one response stays near the size the five-mile grid used to send.
    assert detail["detail"] is True
    assert detail["cellMiles"] == 1
    assert detail["grid"] == [201, 201]
    assert len(detail["terrain"]) == 201 * 201
    assert len(detail["height"]) == 201 * 201
    assert detail["bounds"][2] - detail["bounds"][0] == 201
    assert detail["bounds"][3] - detail["bounds"][1] == 201


def test_detail_reaches_one_mile_across_the_whole_poster():
    detail = terrain_detail(World(), "Baldur's Gate", radius=250)

    assert detail["cellMiles"] == 1
    assert detail["grid"] == [201, 201]


def test_detail_falls_back_to_five_miles_without_the_one_mile_survey(monkeypatch):
    monkeypatch.setattr(mapdata, "_fine_grid", dict)

    detail = terrain_detail(World(), "Waterdeep", radius=250)

    assert detail["cellMiles"] == 5
    assert detail["grid"] == [101, 101]


def test_manual_terrain_override_is_persisted_and_can_be_removed(tmp_path, monkeypatch):
    path = tmp_path / "terrain-overrides.json"
    monkeypatch.setattr(mapdata, "_terrain_overrides_path", lambda: path)

    assert mapdata.save_terrain_override(4, 7, mapdata.CODES["ocean"]) == 1
    assert mapdata.terrain_overrides() == {"4,7": "o"}
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["format"] == "faerun-terrain-overrides-v1"
    assert payload["grid"] == [mapdata.GRID_W, mapdata.GRID_H]

    assert mapdata.save_terrain_override(4, 7, "") == 0
    assert mapdata.terrain_overrides() == {}


def test_manual_ocean_override_replaces_marsember_land_cell(monkeypatch):
    world = World()
    settlements = list(world.settlements.values())
    original = mapdata.terrain_grid(settlements)
    marsember = world.find_settlement("Marsember")
    x0, y0, x1, y1 = original["bounds"]
    width, height = original["grid"]
    column = math.floor((marsember.x - x0) / ((x1 - x0) / width))
    row = math.floor((marsember.y - y0) / ((y1 - y0) / height))
    index = row * width + column
    assert original["land"][index] is True

    monkeypatch.setattr(
        mapdata, "terrain_overrides", lambda: {f"{column},{row}": mapdata.CODES["ocean"]}
    )
    corrected = mapdata._build(settlements)

    assert corrected["terrain"][index] == mapdata.CODES["ocean"]
    assert corrected["land"][index] is False
    assert corrected["height"][index] < 0


@pytest.mark.parametrize("column,row", [(-1, 0), (0, -1), (10, 0), (0, 10)])
def test_manual_terrain_override_rejects_cells_outside_the_world_grid(
    tmp_path, monkeypatch, column, row
):
    monkeypatch.setattr(mapdata, "GRID_W", 10)
    monkeypatch.setattr(mapdata, "GRID_H", 10)
    monkeypatch.setattr(
        mapdata, "_terrain_overrides_path", lambda: tmp_path / "terrain-overrides.json"
    )

    with pytest.raises(mapdata.AtlasError, match="outside the world grid"):
        mapdata.save_terrain_override(column, row, mapdata.CODES["ocean"])