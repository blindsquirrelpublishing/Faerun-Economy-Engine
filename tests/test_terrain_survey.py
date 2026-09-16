from faerun.mapdata import (
    _full_terrain_cell,
    _parse_full_terrain,
    _parse_location_terrain,
)


def test_location_terrain_uses_relief_without_inventing_elevation():
    contexts = _parse_location_terrain({
        "metadata": {"cell_miles": 10},
        "locations": [
            {
                "name": "Adder Peaks",
                "fps": "FPS1:WD:X+016.65:Y-007.81",
                "cell_dominant_terrain": "mountains",
                "cell_relief": "mountainous",
                "elevation_meters": None,
            },
            {
                "name": "Akhlaur Swamp",
                "cell_dominant_terrain": "wetland",
                "cell_relief": "gentle_or_wet_low_relief",
                "elevation_meters": None,
            },
        ],
    })

    assert contexts["adderpeaks"]["terrain"] == "mountains"
    assert contexts["adderpeaks"]["floor"] == 0.58
    assert round(contexts["adderpeaks"]["east"], 1) == 1998.0
    assert round(contexts["adderpeaks"]["north"], 1) == -937.2
    assert contexts["akhlaurswamp"]["terrain"] == "marsh"
    assert contexts["akhlaurswamp"]["floor"] == 0.06
    assert all("elevation" not in context for context in contexts.values())


def test_full_terrain_grid_uses_floor_for_negative_coordinates():
    grid = _parse_full_terrain({
        "format": "faerun-terrain-simple-v1",
        "column_min": -1,
        "column_max": 1,
        "row_min": -1,
        "row_max": 1,
        "width": 3,
        "height": 3,
        "cell_count": 9,
        "cell_miles": 10,
        "rows": {"-1": "JMS", "0": "PFS", "1": "TWS"},
    })

    assert _full_terrain_cell(grid, -0.1, -0.1) == "jungle"
    assert _full_terrain_cell(grid, 0.1, 0.1) == "forest"
    assert _full_terrain_cell(grid, 10.1, 10.1) == "ocean"
