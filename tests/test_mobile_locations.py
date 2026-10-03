import subprocess

import pytest

from faerun.calendar import HarptosDate
from faerun.mapdata import map_payload
from faerun.mobileassets import MOBILE_HTML, MOBILE_JS
from faerun.web import STATIC, api_bootstrap, api_mobile_location
from faerun.world import World


def test_silver_wheel_is_encamped_at_waterdeep_in_mid_eleint():
    world = World(date=HarptosDate(1492, 9, 14))

    profile = world.find_mobile_location("Silver Wheel").profile(world)

    assert profile["kind"] == "mobile_location"
    assert profile["position"]["status"] == "encamped"
    assert profile["position"]["host"] == {
        "id": "waterdeep",
        "name": "Waterdeep",
    }
    assert profile["position"]["camp"] == "South Ward caravan field"
    assert profile["requirements"]["total_water_gallons_per_day"] > 500
    assert profile["inventory"]["trade_cargo_lb"] == 5200


def test_mobile_location_interpolates_along_a_dated_route():
    world = World(date=HarptosDate(1492, 9, 18))
    location = world.find_mobile_location("silver_wheel")

    position = location.position(world)
    waterdeep = world.find_settlement("waterdeep")
    amphail = world.find_settlement("amphail")

    assert position["status"] == "travelling"
    assert position["route"] == "The Long Road"
    assert position["progress"] == pytest.approx(1 / 3, abs=0.0001)
    assert position["position_source"] in {"mapped_route", "route_unavailable"}


def test_company_follows_bent_route_by_distance(monkeypatch):
    from types import SimpleNamespace
    from faerun.data.mobile_locations import MOBILE_LOCATIONS
    from faerun import locationedits

    monkeypatch.setattr(locationedits, "load_location_edits", lambda: {"locations": {}})
    stops = {identifier: SimpleNamespace(id=identifier, name=identifier, x=east, y=south)
             for identifier, east, south in [("waterdeep", 0, 0), ("amphail", 20, 10)]}
    def route(origin, destination, **options):
        assert options["include_inferred"] is False
        assert options["route_types"] == {"road", "track", "trail", "ferry"}
        return {"reachable": True, "mapRoads": True,
                "legs": [{"points": [[0, 0], [0, 10], [20, 10]]}]}
    world = SimpleNamespace(date=HarptosDate(1492, 9, 18), find_settlement=stops.__getitem__, route=route)
    position = MOBILE_LOCATIONS[0].position(world)
    assert (position["x"], position["y"]) == (0, 10)
    assert position["position_source"] == "mapped_route"
    world.date = HarptosDate(1492, 9, 20)
    assert MOBILE_LOCATIONS[0].position(world)["x"] == 20
    world.route = lambda *args, **kwargs: {"reachable": False}
    missing = MOBILE_LOCATIONS[0].position(world)
    assert missing["position_source"] == "route_unavailable"
    assert (missing["x"], missing["y"]) == (0, 0)


def test_company_camp_uses_edited_host_coordinates(monkeypatch):
    from types import SimpleNamespace
    from faerun.data.mobile_locations import MOBILE_LOCATIONS
    from faerun import locationedits

    monkeypatch.setattr(locationedits, "load_location_edits", lambda: {"locations": {"amphail": {"x": 650, "y": 1160}}})
    host = SimpleNamespace(id="amphail", name="Amphail", x=621.7, y=1126)
    world = SimpleNamespace(date=HarptosDate(1492, 9, 31), find_settlement=lambda identifier: host)
    position = MOBILE_LOCATIONS[0].position(world)
    assert (position["x"], position["y"]) == (650, 1160)


def test_festival_day_gap_keeps_the_company_at_its_previous_stop():
    world = World(date=HarptosDate(1492, 9, 31))

    position = world.find_mobile_location("silver_wheel").position(world)

    assert position["status"] == "encamped"
    assert position["host"]["id"] == "amphail"


def test_mobile_locations_are_exposed_without_becoming_settlements():
    world = World(date=HarptosDate(1492, 9, 14))

    bootstrap = api_bootstrap(world, {})
    profile = api_mobile_location(world, {"id": ["silver_wheel"]})

    assert "silver_wheel" not in world.settlements
    assert bootstrap["mobile_locations"][0]["id"] == "silver_wheel"
    assert profile["market_access"]["host"]["id"] == "waterdeep"


def test_world_map_contains_a_dated_mobile_pin():
    world = World(date=HarptosDate(1492, 9, 18))

    pin = next(
        row for row in map_payload(world)["settlements"]
        if row["id"] == "silver_wheel"
    )

    assert pin["mobile"] is True
    assert pin["status"] == "travelling"
    assert pin["origin"]["id"] == "waterdeep"
    assert pin["destination"]["id"] == "amphail"


def test_mobile_profile_assets_are_served_and_link_to_host_markets():
    assert "mobile.html" in STATIC
    assert "/api/mobile-location" in MOBILE_JS
    assert "Open host settlement" in MOBILE_JS
    assert "Dated itinerary" in MOBILE_JS
    assert "data-world-date" in MOBILE_HTML
    result = subprocess.run(
        ["node", "--check"], input=MOBILE_JS, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
