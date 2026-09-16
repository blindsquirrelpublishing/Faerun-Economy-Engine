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
    assert min(waterdeep.x, amphail.x) <= position["x"] <= max(waterdeep.x, amphail.x)
    assert min(waterdeep.y, amphail.y) <= position["y"] <= max(waterdeep.y, amphail.y)


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
