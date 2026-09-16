from faerun.mapdata import _align_road_geometry, _parse_road_geometries


class Place:
    def __init__(self, location_id, name, x, y):
        self.id = location_id
        self.name = name
        self.x = x
        self.y = y


def test_corm_orp_branch_does_not_create_hills_edge_sshamath_leg():
    from faerun.world import World
    from faerun.mapdata import road_connections

    world = World()
    connections = [entry for entry in road_connections(world.settlements.values())
                   if entry["name"] == "Corm Orp south branch toward Hluthvar junction"]
    assert [(entry["a"], entry["b"]) for entry in connections] == [("corm_orp", "hluthvar")]
    for edges in world._edges.values():
        for edge in edges:
            if edge.name == "Corm Orp south branch toward Hluthvar junction":
                assert {edge.src, edge.dst} == {"corm_orp", "hluthvar"}


def test_surface_roads_do_not_snap_to_underdark_markets(monkeypatch):
    from faerun import mapdata

    start = Place("hills_edge", "Hill's Edge", 0, 0)
    underground = Place("sshamath", "Sshamath", 100, 0)
    underground.underdark = True
    surface = Place("darkhold", "Darkhold", 100, 0)
    places = [start, underground, surface]
    corridor = {"name": "Corm Orp south branch toward Hluthvar junction",
                "surface": "road", "points": [[0, 0], [50, 0], [100, 0]]}
    aligned = _align_road_geometry(corridor, places)
    assert aligned is not None
    assert aligned["locations"] == ["hills_edge", "darkhold"]
    assert _align_road_geometry(corridor, [underground]) is None
    monkeypatch.setattr(mapdata, "road_geometries", lambda _: [aligned])
    connections = mapdata.road_connections(places)
    assert [(entry["a"], entry["b"]) for entry in connections] == [("hills_edge", "darkhold")]


def test_road_connections_measure_bends_and_access_spurs(monkeypatch):
    import pytest
    from faerun import mapdata

    places = [Place("start", "Start", 0, 0), Place("bend", "Bend", 0, 100),
              Place("end", "End", 100, 100), Place("spur", "Spur", 50, 110)]
    monkeypatch.setattr(mapdata, "road_geometries", lambda _: [{
        "name": "Bent road", "surface": "road",
        "points": [[0, 0], [0, 100], [100, 100]],
        "anchors": [0, 1, 2], "locations": ["start", "bend", "end"],
    }])
    connections = mapdata.road_connections(places, include_spanning=True)
    by_pair = {(entry["a"], entry["b"]): entry for entry in connections}
    assert by_pair["start", "end"]["distance"] == pytest.approx(200)
    assert by_pair["bend", "spur"]["distance"] == pytest.approx(60)
    assert by_pair["spur", "end"]["distance"] == pytest.approx(60)
    assert not by_pair["start", "end"]["consecutive"]
    assert len(mapdata.road_connections(places)) == 3


def test_shaar_road_follows_poster_stops_without_lhesper_detour(monkeypatch):
    import pytest
    from faerun import mapdata

    corridor = _parse_road_geometries({"corridors": [{
        "id": "shaar-main-road",
        "name": "Shaarmid through Kholtar and Eartheart to Delzimmer",
        "surface": "road", "fps_waypoints": [{"x": 0, "y": 0}, {"x": 1, "y": 1}],
    }]})[0]
    assert corridor["stops"] == ["shaarmid", "kholtar", "eartheart", "delzimmer"]
    assert corridor["exclusive_stops"]
    points = [[600 + point[0] * 120, 1200 - point[1] * 120] for point in corridor["fps"]]
    places = [Place("shaarmid", "Shaarmid", 2262.5, 2459.8),
              Place("kholtar", "Kholtar", 2742.5, 2511.6),
              Place("eartheart", "Eartheart", 2815.8, 2563.5),
              Place("delzimmer", "Delzimmer", 2993.6, 2556.3),
              Place("lhesper", "Lhesper", 2252.9, 2518.0)]
    aligned = _align_road_geometry({**corridor, "points": points}, places)
    assert aligned is not None
    assert aligned["locations"] == corridor["stops"]
    assert all(end[0] >= start[0] for start, end in zip(aligned["points"], aligned["points"][1:]))
    monkeypatch.setattr(mapdata, "road_geometries", lambda _: [aligned])
    connections = mapdata.road_connections(places)
    assert [(entry["a"], entry["b"]) for entry in connections] == [
        ("shaarmid", "kholtar"), ("kholtar", "eartheart"), ("eartheart", "delzimmer"),
    ]
    assert connections[1]["distance"] == pytest.approx(92, abs=5)


def test_dragon_coast_branch_uses_shared_waypoints_not_nearby_towns():
    from faerun.mapdata import _connect_dragon_coast_trails

    def fps(east, south):
        return [(east - 694) / 150.5, (682 - south) / 150.5]

    coast = {"id": "elversult-starmantle-trail", "fps": [fps(1859, 1207), fps(1990, 1215), fps(2311, 1213)]}
    plains = {"id": "shining-plains-road", "fps": [fps(1900, 1550), fps(2100, 1550), fps(2200, 1560)]}
    branch = {"id": "dragon-coast-shining-trail", "fps": [fps(1990, 1216), fps(2028, 1450), fps(2050, 1549)]}
    _connect_dragon_coast_trails([coast, plains, branch])
    assert coast["stops"] == ["elversult", "starmantle"]
    assert branch["stops"] == ["elversult", "lheshayl"]
    assert branch["exclusive_stops"] and coast["exclusive_stops"]
    assert branch["fps"][0] == coast["fps"][0]
    assert branch["fps"][1] in coast["fps"]
    assert branch["fps"][-2] in plains["fps"]
    assert branch["fps"][-1] in plains["fps"]
    assert fps(2028, 1450) in branch["fps"]


def test_corrected_corridors_keep_graph_legs_on_their_named_stops():
    from faerun.world import World

    world = World()
    expected = {
        "Elversult to Starmantle trail": {frozenset(("elversult", "starmantle"))},
        "Dragon Coast trail to Shining Plains road": {frozenset(("elversult", "lheshayl"))},
        "Shaarmid through Kholtar and Eartheart to Delzimmer": {
            frozenset(("shaarmid", "kholtar")), frozenset(("kholtar", "eartheart")),
            frozenset(("eartheart", "delzimmer")),
        },
    }
    for name, pairs in expected.items():
        actual = {frozenset((edge.src, edge.dst)) for edges in world._edges.values()
                  for edge in edges if edge.name == name}
        assert actual == pairs, (name, actual)


def test_traced_road_corridors_keep_curved_fps_waypoints():
    corridors = _parse_road_geometries({
        "corridors": [{
            "id": "high-road",
            "name": "High Road",
            "surface": "road",
            "fps_waypoints": [
                {"x": -1.0, "y": 2.0},
                {"x": -0.8, "y": 1.7},
                {"x": 0.0, "y": 0.0},
            ],
        }],
    })

    assert corridors == [{
        "id": "high-road",
        "name": "High Road",
        "surface": "road",
        "fps": [[-1.0, 2.0], [-0.8, 1.7], [0.0, 0.0]],
    }]


def test_vilhon_road_joins_its_existing_traced_corridors():
    corridors = _parse_road_geometries({
        "corridors": [
            {"id": "emerald-way", "surface": "road", "fps_waypoints": [
                {"x": 14.47, "y": -5.06}, {"x": 13.28, "y": -6.05},
            ]},
            {"id": "arrabar-emerald-way", "surface": "road", "fps_waypoints": [
                {"x": 12.25, "y": -6.60}, {"x": 13.49, "y": -6.13},
            ]},
            {"id": "golden-road-south", "surface": "road", "fps_waypoints": [
                {"x": 12.25, "y": -6.60}, {"x": 12.31, "y": -6.83},
                {"x": 12.33, "y": -7.06}, {"x": 12.32, "y": -7.32},
                {"x": 12.45, "y": -7.66},
            ]},
        ],
    })

    assert [corridor["id"] for corridor in corridors] == [
        "vilhon-road-hlath-arrabar", "vilhon-road-arrabar-ormpetarr",
        "golden-road-ormpetarr-innarlith",
        "golden-road-innarlith-shaarmid",
    ]
    assert [corridor["name"] for corridor in corridors] == [
        "The Vilhon Road",
        "The Vilhon Road",
        "The Golden Road: Ormpetarr to Innarlith",
        "The Golden Road: Innarlith to Shaarmid",
    ]
    assert corridors[0]["fps"] == [
        [14.47, -5.06], [13.28, -6.05], [13.49, -6.13], [12.25, -6.6],
    ]
    assert corridors[1]["fps"][-1] == [12.32, -7.32]
    assert corridors[2]["fps"][0] == corridors[1]["fps"][-1]
    assert corridors[2]["fps"][-1] == corridors[3]["fps"][0]
    assert corridors[3]["fps"][-1] == [12.45, -7.66]


def test_shining_plains_road_joins_before_endpoint_alignment():
    corridors = _parse_road_geometries({
        "corridors": [
            {"id": "riatavin-lheshayl", "surface": "road", "fps_waypoints": [
                {"x": 7.05, "y": -7.43}, {"x": 8.31, "y": -5.78},
            ]},
            {"id": "shining-road-east", "surface": "road", "fps_waypoints": [
                {"x": 8.31, "y": -5.78}, {"x": 11.91, "y": -6.20},
            ]},
        ],
    })

    assert corridors == [{
        "id": "shining-plains-road",
        "name": "The Shining Plains Road",
        "surface": "road",
        "fps": [[7.05, -7.43], [8.31, -5.78], [11.91, -6.2]],
        "stops": ["riatavin", "lheshayl", "ormath", "hlondeth"],
    }]


def test_explicit_road_stops_become_exact_geometry_anchors():
    corridor = {
        "id": "shining-plains-road",
        "name": "The Shining Plains Road",
        "surface": "road",
        "stops": ["riatavin", "lheshayl", "ormath", "hlondeth"],
        "points": [[0.0, 0.0], [90.0, 4.0], [180.0, 6.0], [270.0, 0.0]],
    }
    places = [
        Place("riatavin", "Riatavin", 0.0, 0.0),
        Place("lheshayl", "Lheshayl", 88.0, 0.0),
        Place("ormath", "Ormath", 182.0, 0.0),
        Place("hlondeth", "Hlondeth", 270.0, 0.0),
    ]

    aligned = _align_road_geometry(corridor, places)

    assert aligned is not None
    assert aligned["locations"] == [
        "riatavin", "lheshayl", "ormath", "hlondeth",
    ]
    assert [aligned["points"][index] for index in aligned["anchors"]] == [
        [0.0, 0.0], [88.0, 0.0], [182.0, 0.0], [270.0, 0.0],
    ]


def test_traced_trail_terminates_at_locations_and_crosses_named_stops():
    corridor = {
        "id": "ormath-nathlekh",
        "name": "Ormath through Assam to Nathlekh",
        "surface": "trail",
        "points": [[17.0, 100.0], [15.0, 50.0], [16.0, 0.0]],
    }
    places = [
        Place("ormath", "Ormath", 0.0, 100.0),
        Place("assam", "Assam", 0.0, 50.0),
        Place("nathlekh", "Nathlekh", 0.0, 0.0),
    ]

    aligned = _align_road_geometry(corridor, places)

    assert aligned is not None
    assert aligned["points"][0] == [0.0, 100.0]
    assert [0.0, 50.0] in aligned["points"]
    assert aligned["points"][-1] == [0.0, 0.0]
    assert aligned["anchors"] == [0, 1, 2]
    assert aligned["locations"] == ["ormath", "assam", "nathlekh"]


def test_traced_leg_with_no_location_at_one_end_is_omitted():
    corridor = {
        "id": "map-edge-spur",
        "name": "Road to the map edge",
        "surface": "road",
        "points": [[0.0, 0.0], [500.0, 0.0]],
    }
    places = [Place("town", "Town", 0.0, 0.0)]

    assert _align_road_geometry(corridor, places) is None
