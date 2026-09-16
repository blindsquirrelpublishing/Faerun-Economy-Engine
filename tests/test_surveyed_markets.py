"""Surveyed towns are real price markets without rewriting established trade."""

import json

from faerun import atlas
from faerun.calibration import COORDS_FILE
from faerun.economy import market_report
from faerun.data.settlements import SETTLEMENTS_BY_ID
from faerun.models import C, S
from faerun.world import SURVEYED_MARKET_TRAIT, World, _surveyed_markets


def established():
    return [
        S("Oldport", "Coast", "coast", 20000, 100, 100,
          wealth=1.2, tax=0.07, sec=0.8, terrain="coast",
          ind="farm4"),
        S("Hillkeep", "Coast", "coast", 4000, 300, 100,
          wealth=0.9, tax=0.04, sec=0.7, terrain="hills"),
    ]


def test_caer_corwell_is_the_single_canonical_market():
    settlement = SETTLEMENTS_BY_ID["caer_corwell"]

    assert "corwell" not in SETTLEMENTS_BY_ID
    assert settlement.name == "Caer Corwell"
    assert (settlement.x, settlement.y) == (431.0, 1917.6)

    world = World()
    assert "caer_corwell" in world.settlements
    assert "corwell" not in world.settlements


def test_existing_road_uses_traced_length_in_both_directions(monkeypatch):
    import pytest
    from faerun import mapdata
    from faerun import world as world_module

    monkeypatch.setattr(world_module, "NAMED_ROUTES", [
        ("Old road", ["oldport", "hillkeep"], 1.1, "road"),
    ])
    monkeypatch.setattr(mapdata, "road_connections", lambda *args, **kwargs: [{
        "a": "oldport", "b": "hillkeep", "kind": "road", "name": "Surveyed road",
        "distance": 350.0, "consecutive": False,
    }])
    world = World(settlements=established())
    forward = next(edge for edge in world.edges_from("oldport") if edge.dst == "hillkeep")
    reverse = next(edge for edge in world.edges_from("hillkeep") if edge.dst == "oldport")
    assert forward.distance == reverse.distance == pytest.approx(350.0)
    assert forward.quality == 1.1
    assert forward.name == "Old road"


def test_caer_calidyrr_is_the_single_canonical_market():
    from faerun.mapdata import map_payload

    settlement = SETTLEMENTS_BY_ID["caer_calidyrr"]

    assert "caer_callidyrr" not in SETTLEMENTS_BY_ID
    assert settlement.name == "Caer Calidyrr"
    assert settlement.population == 25000

    world = World()
    matches = [market for market in world.settlements.values()
               if market.name == "Caer Calidyrr"]
    assert [market.id for market in matches] == ["caer_calidyrr"]
    assert matches[0].population == 25000
    assert any(edge.name == "The Moonshae Crossing"
               for edge in world.edges_from("caer_calidyrr"))
    pins = [pin for pin in map_payload(world)["settlements"]
            if "calidyrr" in pin["name"].lower()
            or "callidyrr" in pin["name"].lower()]
    assert [(pin["id"], pin["name"], pin["population"]) for pin in pins] == [
        ("caer_calidyrr", "Caer Calidyrr", 25000),
    ]


def test_adjusted_markets_are_part_of_the_standard_atlas():
    world = World()
    saved = {point["id"]: (point["x"], point["y"])
             for point in json.loads(COORDS_FILE.read_text())["control"]}
    standard = {point["id"]: (point["x"], point["y"])
                for point in atlas.control_points(world.settlements.values())}

    assert saved == standard
    assert {market_id: saved[market_id] for market_id in (
        "mintarn", "orlumbor", "caer_calidyrr", "elbulder", "mimph",
        "torsch",
    )} == {
        "mintarn": (562.1, 1567.3),
        "orlumbor": (726.6, 1436.6),
        "caer_calidyrr": (442.1, 1670.4),
        "elbulder": (2266.4, 2114.6),
        "mimph": (2055.9, 2003.7),
        "torsch": (2479.3, 2211.8),
    }


def test_shining_plains_road_has_explicit_surveyed_market_legs():
    world = World()
    route = next(
        route for route in world.named_routes
        if route[0] == "The Shining Plains Road"
    )

    assert route[1:] == (
        ["riatavin", "lheshayl", "ormath", "hlondeth"], 1.0, "road",
    )
    for start, end in zip(route[1], route[1][1:]):
        edge = next(edge for edge in world.edges_from(start) if edge.dst == end)
        assert (edge.name, edge.kind) == ("The Shining Plains Road", "road")


def patch_place(monkeypatch):
    from faerun import mapdata

    current = [{"name": "Newford", "x": 140.0, "y": 110.0,
                "category": "settlement_or_site"}]
    base = [{"name": "Newford", "x": 130.0, "y": 105.0,
             "category": "settlement_or_site"}]
    monkeypatch.setattr(mapdata, "surveyed_places", lambda towns: current)
    monkeypatch.setattr(mapdata, "surveyed_places_base", lambda towns: base)


def test_surveyed_places_become_small_import_markets(monkeypatch):
    patch_place(monkeypatch)

    got = _surveyed_markets(established())

    assert len(got) == 1
    market = got[0]
    assert market.id == "newford"
    assert market.has_trait(SURVEYED_MARKET_TRAIT)
    assert market.industries == {}
    assert market.region == "Coast"
    assert getattr(market, "_base_xy") == (130.0, 105.0)


def test_baseline_failure_does_not_drop_surveyed_markets(monkeypatch):
    from faerun import mapdata

    current = [{"name": "Starmantle", "x": 1289.3, "y": 423.4,
                "category": "settlement_or_site"}]
    monkeypatch.setattr(mapdata, "surveyed_places", lambda towns: current)

    def broken_baseline(towns):
        raise ValueError("bad calibration baseline")

    monkeypatch.setattr(mapdata, "surveyed_places_base", broken_baseline)

    got = _surveyed_markets(established())

    assert [market.id for market in got] == ["starmantle"]
    assert not hasattr(got[0], "_base_xy")


def test_current_space_failure_falls_back_to_atlas_places(monkeypatch):
    from faerun import atlas, mapdata

    current = [{"name": "Starmantle", "x": 1289.3, "y": 423.4,
                "category": "settlement_or_site"}]

    def broken_current(towns):
        raise ValueError("bad reverse warp")

    monkeypatch.setattr(mapdata, "surveyed_places", broken_current)
    monkeypatch.setattr(atlas, "surveyed_places", lambda towns: current)
    monkeypatch.setattr(mapdata, "surveyed_places_base", broken_current)

    got = _surveyed_markets(established())

    assert [market.id for market in got] == ["starmantle"]


def test_surveyed_market_has_every_commodity_price(monkeypatch):
    patch_place(monkeypatch)
    core = established()
    inferred = _surveyed_markets(core)
    grain = C("grain", "Grain", "food", 1.0, produced_by="farm")
    cloth = C("cloth", "Cloth", "textile", 2.0, produced_by="farm")
    world = World(settlements=core + inferred, commodities=[grain, cloth])

    report = market_report("Newford", world=world)

    assert {row["commodity"] for row in report["prices"]} == {"grain", "cloth"}
    assert all(row["price"] > 0 for row in report["prices"])
    assert all(row["availability"] != "unavailable"
               for row in report["prices"])


def test_surveyed_market_is_a_leaf_and_not_a_route_shortcut(monkeypatch):
    patch_place(monkeypatch)
    core = established()
    inferred = _surveyed_markets(core)
    world = World(settlements=core + inferred)

    edges = world.edges_from("newford")
    assert len(edges) == 1
    assert edges[0].dst == "oldport"
    assert "Newford" not in world.route("Oldport", "Hillkeep")["path"]

    from faerun.mapdata import map_payload

    routes = map_payload(world)["routes"]
    local_route = next(route for route in routes
                       if route["name"] == "local market trail")
    assert {local_route["a"], local_route["b"]} == {"newford", "oldport"}
    assert local_route["kind"] == "trail"


def test_map_includes_caravan_tracks_used_by_trade():
    from faerun.mapdata import map_payload

    world = World()
    caravan_edges = [edge for legs in world._edges.values() for edge in legs
                     if edge.primary == "track"]
    visible_routes = map_payload(world)["routes"]

    assert caravan_edges
    visible_keys = {
        frozenset((route["a"], route["b"]))
        for route in visible_routes
        if "track" in route["modes"]
    }
    assert all(frozenset((edge.src, edge.dst)) in visible_keys
               for edge in caravan_edges)


def test_surveyed_markets_separated_by_water_use_local_ferries():
    world = World()

    for settlement_id in ("anchoril", "iron_keep", "irphong", "llewellyn",
                          "nemesser", "sambar", "sundrah"):
        edge = world.edges_from(settlement_id)[0]
        assert edge.kind == "ferry"
        assert edge.name == "local market ferry"


def test_port_ghaast_uses_khalab_ferry_instead_of_distant_feeder_trail():
    world = World()

    edges = world.edges_from("port_ghaast")

    assert [(edge.dst, edge.kind, edge.name) for edge in edges] == [
        ("khalab", "ferry", "Port Ghaast Ferry")
    ]
    assert edges[0].distance < 175


def test_surveyed_feeder_tree_uses_nearby_markets_before_distant_hubs():
    world = World()

    chavyondat_edges = world.edges_from("chavyondat")
    thruldar = next(edge for edge in chavyondat_edges
                    if edge.dst == "thruldar")

    assert thruldar.name == "Ormpе through Vaelan and Assur toward Shoun"
    assert thruldar.kind == "trail"
    from faerun.mapdata import road_connections
    import pytest

    measured = next(connection["distance"] for connection in road_connections(
        list(world.settlements.values()), include_spanning=True
    ) if {connection["a"], connection["b"]} == {"chavyondat", "thruldar"}
        and connection["name"] == thruldar.name)
    assert thruldar.distance == pytest.approx(measured)
    assert all(edge.dst != "skuld" for edge in chavyondat_edges)
    assert world.route("Chavyondat", "Skuld")["reachable"]


def test_named_underdark_connections_are_inferred_not_poster_roads():
    world = World()
    for name, endpoints in (
        ("The Deepdark Road", {"mantol_derith", "sshamath"}),
        ("Sshamath Smugglers' Road", {"sshamath", "secomber"}),
        ("Sshamath Deep Way", {"sshamath", "llorkh"}),
    ):
        edges = [edge for origin in endpoints for edge in world.edges_from(origin)
                 if edge.name == name]
        assert len(edges) == 2
        assert all({edge.src, edge.dst} == endpoints for edge in edges)
        assert all(edge.inferred for edge in edges)
        assert all("tunnel" in edge.kind.split("+") for edge in edges)


def test_local_market_feeders_are_explicitly_inferred():
    world = World()
    feeders = [edge for edges in world._edges.values() for edge in edges
               if edge.name in ("local market trail", "local market ferry")]
    assert feeders
    assert all(edge.inferred for edge in feeders)
    cedarspoke_link = [edge for edge in feeders
                      if {edge.src, edge.dst} == {"cedarspoke", "saerloon"}]
    assert len(cedarspoke_link) == 2
    assert all(edge.inferred for edge in cedarspoke_link)


def test_caravan_links_are_explicitly_inferred():
    from faerun.mapdata import map_payload

    world = World()
    edge = next(edge for edges in world._edges.values() for edge in edges
                if edge.name == "caravan track")
    assert edge.inferred
    reverse = next(reverse for reverse in world.edges_from(edge.dst) if reverse.dst == edge.src)
    assert reverse.inferred
    route = next(route for route in map_payload(world)["routes"]
                 if {route["a"], route["b"]} == {edge.src, edge.dst})
    assert route["inferred"] is True


def test_keltar_is_removed_without_dangling_routes_or_calibration():
    from faerun.mapdata import map_payload

    world = World()
    assert "keltar" not in SETTLEMENTS_BY_ID
    assert world.lookup_settlement("Keltar") is None
    assert all(point["id"] != "keltar"
               for point in json.loads(COORDS_FILE.read_text())["control"])
    assert all("keltar" not in stops for _, stops, _, _ in world.named_routes)
    payload = map_payload(world)
    assert all(place["id"] != "keltar" for place in payload["settlements"])
    assert all(route["a"] in world.settlements and route["b"] in world.settlements
               for route in payload["routes"])
    assert all("keltar" not in {route["a"], route["b"]} for route in payload["routes"])
    assert world.route("Calimport", "Suldolphor")["reachable"]


def test_tethyrian_roads_do_not_invent_a_saradush_velen_shortcut():
    world = World()
    assert not any(edge.dst == "velen" and edge.kind == "road"
                   for edge in world.edges_from("saradush"))
    assert world.route("Saradush", "Velen")["reachable"]


def test_traced_road_connector_replaces_redundant_local_trail():
    world = World()

    edges = world.edges_from("three_swords")

    assert edges
    assert all(not edge.name.startswith("local market") for edge in edges)
    assert any(edge.kind == "road" and edge.distance < 250 for edge in edges)
    assert world.route("Three Swords", "Innarlith")["reachable"]


def test_urbreth_is_a_sea_of_swords_harbour(monkeypatch):
    from faerun import mapdata

    place = [{"name": "Urbreth", "x": 140.0, "y": 110.0,
              "category": "settlement_or_site"}]
    monkeypatch.setattr(mapdata, "surveyed_places", lambda towns: place)
    monkeypatch.setattr(mapdata, "surveyed_places_base", lambda towns: place)

    market = _surveyed_markets(established())[0]

    assert market.port == "Sea of Swords"


def test_halagard_is_halarahhs_sea_gateway():
    world = World()

    assert world.settlements["halagard"].port == "Sea of Swords"
    sea_edges = [edge for edge in world.edges_from("halarahh")
                 if edge.kind == "sea"]
    assert [(edge.dst, edge.name) for edge in sea_edges] == [
        ("halagard", "Halruaa-Chult Coastal Run")
    ]
    assert any(edge.kind == "sea"
               for edge in world.edges_from("halagard"))


def test_sea_edges_stop_at_intervening_harbours():
    ports = [
        S("Westhaven", "Coast", "coast", 5000, 0, 0, port="Test Sea"),
        S("Midhaven", "Coast", "coast", 5000, 100, 5, port="Test Sea"),
        S("Easthaven", "Coast", "coast", 5000, 200, 0, port="Test Sea"),
    ]

    world = World(settlements=ports)

    assert any(edge.dst == "midhaven" and edge.kind == "sea"
               for edge in world.edges_from("westhaven"))
    assert any(edge.dst == "easthaven" and edge.kind == "sea"
               for edge in world.edges_from("midhaven"))
    assert not any(edge.dst == "easthaven" and edge.kind == "sea"
                   for edge in world.edges_from("westhaven"))


def test_automatic_coasting_legs_stop_at_a_provisioning_port():
    world = World()
    coasting = [edge for legs in world._edges.values() for edge in legs
                if edge.name.endswith("coasting run")]
    halagard_sea = [edge for edge in world.edges_from("halagard")
                    if edge.primary == "sea"]

    assert all(edge.distance <= 650 for edge in coasting)
    assert any(edge.dst == "delselar" and
               edge.name == "Halruaa-Chult Coastal Run"
               for edge in halagard_sea)
    assert not any(edge.dst == "suldolphor" for edge in halagard_sea)
    assert not any(edge.dst == "tashluta" and
                   edge.name == "Halruaa-Chult Coastal Run"
                   for edge in world.edges_from("delselar"))
    assert not any(edge.dst == "thindar" and
                   edge.name.endswith("coasting run")
                   for edge in world.edges_from("tashluta"))


def test_southern_sword_coast_is_split_into_interchanging_coastal_runs():
    world = World()
    routes = [route for route in world.named_routes
              if route[0].endswith("Coastal Run")]

    assert [(name, stops) for name, stops, _quality, _kind in routes] == [
        ("Halruaa-Chult Coastal Run",
         ["halarahh", "halagard", "delselar", "thindar", "samargol",
          "port_nyanzaru"]),
        ("Chult-Tashalar Coastal Run",
         ["port_nyanzaru", "tashluta", "almraiven", "suldolphor"]),
        ("Calimshan-Lantan Coastal Run",
         ["suldolphor", "urbreth", "lantan", "calimport"]),
    ]
    assert all(world.settlements[port].port == "Sea of Swords"
               for port in ("samargol", "thindar", "delselar"))
    assert all(kind == "sea" for _name, _stops, _quality, kind in routes)
    for name, stops, _quality, _kind in routes:
        for start, end in zip(stops, stops[1:]):
            assert any(edge.dst == end and edge.primary == "sea" and
                       edge.name == name for edge in world.edges_from(start))


def test_southern_coastal_runs_have_independent_multileg_services():
    world = World()
    routes = [route for route in world.named_routes
              if route[0].endswith("Coastal Run")]
    service_ids = set()

    for name, stops, _quality, _kind in routes:
        for start, end in zip(stops, stops[1:]):
            edge = next(edge for edge in world.edges_from(start)
                        if edge.dst == end and edge.name == name)
            carrier = next(carrier for carrier in edge.carrier_options()
                           if carrier.get("multileg"))
            assert carrier["name"] == "Sword Coast Coasters"
            service_ids.add(carrier["service_id"])

    assert service_ids == {
        "halruaa-chult-coastal-run",
        "chult-tashalar-coastal-run",
        "calimshan-lantan-coastal-run",
    }

    assert not any(
        carrier.get("multileg")
        for edge in world.edges_from("waterdeep")
        for carrier in edge.carrier_options()
    )


def test_vilhon_road_legs_share_a_ground_milk_run():
    world = World()
    route = next(route for route in world.named_routes
                 if route[0] == "The Vilhon Road")

    assert route[1] == ["hlath", "arrabar", "ormpetarr"]
    for start, end in zip(route[1], route[1][1:]):
        edge = next(edge for edge in world.edges_from(start)
                    if edge.dst == end and edge.name == route[0])
        carrier = next(carrier for carrier in edge.carrier_options()
                       if carrier.get("multileg"))
        assert carrier["name"] == "Vilhon Reach Milk Run"
        assert carrier["service_id"] == "vilhon-reach-milk-run"
        assert carrier["service_class"] == "ground"


def test_multileg_coastal_run_map_payload_contains_only_explicit_legs():
    from faerun.mapdata import map_payload

    world = World()
    routes = [route for route in world.named_routes
              if route[0].endswith("Coastal Run")]
    payload = map_payload(world)
    for name, stops, _quality, _kind in routes:
        expected_legs = {
            frozenset((start, end))
            for start, end in zip(stops, stops[1:])
        }
        rendered_legs = {
            frozenset((leg["a"], leg["b"]))
            for leg in payload["routes"] if leg["name"] == name
        }

        assert rendered_legs == expected_legs
        assert not any(geometry.get("name") == name
                       for geometry in payload["seaAirGeometries"])
