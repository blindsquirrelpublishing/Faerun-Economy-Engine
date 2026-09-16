from faerun.mapdata import _parse_sea_air_geometries


def test_water_routes_use_constrained_points_and_skip_blocked_legs():
    geometries = _parse_sea_air_geometries({
        "routes": [{
            "route_id": "coast-run",
            "name": "Coast Run",
            "mode": "sea",
            "modes": ["sea"],
            "legs": [
                {
                    "leg_index": 1,
                    "from": "Start",
                    "to": "Middle",
                    "status": "water_routed",
                    "pixels": [[10, 10], [30, 30]],
                    "water_pixels": [[12, 14], [18, 25], [28, 29]],
                },
                {
                    "leg_index": 2,
                    "from": "Middle",
                    "to": "End",
                    "status": "blocked_water_path",
                    "pixels": [[30, 30], [40, 40]],
                    "water_pixels": None,
                },
            ],
        }],
    })

    assert geometries == [{
        "id": "coast-run-leg-1",
        "name": "Coast Run",
        "from": "Start",
        "to": "Middle",
        "surface": "sea",
        "multimodal": False,
        "pixels": [[12.0, 14.0], [18.0, 25.0], [28.0, 29.0]],
    }]


def test_schematic_air_routes_keep_endpoint_geometry():
    geometries = _parse_sea_air_geometries({
        "routes": [{
            "route_id": "skyroad",
            "name": "Skyroad",
            "mode": "air",
            "legs": [{
                "leg_index": 1,
                "from": "Start",
                "to": "End",
                "status": "mapped_schematic",
                "pixels": [[100, 200], [300, 400]],
            }],
        }],
    })

    assert geometries[0]["surface"] == "air"
    assert geometries[0]["from"] == "Start"
    assert geometries[0]["to"] == "End"
    assert geometries[0]["pixels"] == [[100.0, 200.0], [300.0, 400.0]]
