from collections import Counter
from copy import deepcopy
import hashlib
import json
import random

import pytest

from faerun import cli, web
from faerun.buildinggen import SOURCE, generate_buildings, roll_building_details
from faerun.census import HOUSING_SCENARIOS
from faerun.data.businesses import BUSINESSES
from faerun.data.waterdeep import PEOPLE
from faerun.locationgen import generate_location, location_profiles


def test_waterdeep_version_one_streams_are_unchanged_by_shared_rule_extraction():
    outputs = [generate_buildings(ward, count=100, seed=1357)
               for ward in ("castle", "north", "sea", "trades", "dock", "south")]
    assert hashlib.sha256(json.dumps(outputs, sort_keys=True).encode()).hexdigest() == (
        "93255110fb727e6f732bbd9116ac9c38c5367ae702414db529b3e50826e18b63"
    )


def test_profiles_are_explicit_complete_assumptions_not_waterdeep_wards():
    catalog = location_profiles()
    assert catalog["basis"] == "engine_assumptions"
    assert [p["id"] for p in catalog["profiles"]] == ["village", "town", "city", "port", "fortress"]
    for profile in catalog["profiles"]:
        assert sum(profile["class_weights"].values()) == 100
        assert set(profile["class_weights"]) == {"B", "C", "D"}
        assert profile["basis"] == "engine_assumptions"
        assert profile["condition_modifier"] in (-1, 0, 1)
    catalog["profiles"][0]["class_weights"]["A"] = 100
    assert "A" not in location_profiles()["profiles"][0]["class_weights"]


@pytest.mark.parametrize("profile", ["village", "town", "city", "port", "fortress"])
def test_each_profile_is_reproducible_exportable_and_count_only(profile):
    before = deepcopy((SOURCE, BUSINESSES, PEOPLE))
    result = generate_location("Neverwinter", profile=profile, count=100)
    assert generate_location(**result["parameters"]) == result
    assert json.loads(json.dumps(result)) == result
    assert result["location"]["basis"] == "user_supplied_label"
    assert result["generated"] and not result["surveyed"]
    assert not result["live_market_integration"] and not result["can_replace_population"]
    assert result["summary"]["city_population"] is None
    assert result["summary"]["resolved_buildings"] == 100
    assert result["summary"]["classes"] == Counter(b["building_class"] for b in result["buildings"])
    weights = result["profile"]["class_weights"]
    for row in result["buildings"]:
        assert row["location_name"] == "Neverwinter" and row["ward"] is None
        assert row["class_basis"] == "profile_assumption"
        assert row["map_position"] is row["historical_business_id"] is None
        assert row["occupants"]["named_people"] == []
        assert row["citations"] == SOURCE["citations"][:2]
        roll = row["rolls"]["class_d100"]
        expected_class = "B" if roll <= weights["B"] else (
            "C" if roll <= weights["B"] + weights["C"] else "D"
        )
        assert row["building_class"] == expected_class
        assert row["rolls"]["condition_modifier"] == result["profile"]["condition_modifier"]
        assert row["occupants"]["staff"] == sum(row["occupants"]["staff_roles"].values())
        if row["rolls"]["condition_adjusted"] in (0, 1, 7):
            assert all(row["occupants"][key] == 0 for key in ("residents", "lodging_guests", "staff"))
    assert (SOURCE, BUSINESSES, PEOPLE) == before


def test_batch_prefix_and_sensitivity_and_location_identity():
    baseline = generate_location("New Place", count=10, seed=56)
    assert baseline["buildings"] == generate_location("New Place", count=100, seed=56)["buildings"][:10]
    changed = generate_location("New Place", count=10, seed=56, footprint_sqft=2000, scenario="high")
    for a, b in zip(baseline["buildings"], changed["buildings"]):
        for key in ("id", "rolls", "structure", "condition", "use", "building_class"):
            assert a[key] == b[key]
    assert baseline["buildings"] != generate_location("New Place", count=10, seed=57)["buildings"]
    for other in ("Another Place", "New-Place"):
        result = generate_location(other, count=10, seed=56)
        assert result["location"]["id"] != baseline["location"]["id"]
        assert {b["id"] for b in result["buildings"]}.isdisjoint(b["id"] for b in baseline["buildings"])
    same_label = generate_location(" new   PLACE ", count=10, seed=56)
    assert [b["id"] for b in same_label["buildings"]] == [b["id"] for b in baseline["buildings"]]
    unicode_name = generate_location("\u6771\u306e\u753a")
    assert unicode_name["location"]["name"] == "\u6771\u306e\u753a"
    assert generate_location(**unicode_name["parameters"]) == unicode_name


@pytest.mark.parametrize("building_class", ["B", "C", "D"])
def test_custom_mix_can_select_each_class_and_preserves_shared_source_dice(building_class):
    overrides = {f"class_{key.lower()}_weight": 100 if key == building_class else 0 for key in "BCD"}
    result = generate_location("Custom Keep", profile="fortress", condition_modifier=-1, **overrides)
    assert result["profile"]["customized"]
    assert all(b["building_class"] == building_class for b in result["buildings"])
    assert generate_location(**result["parameters"]) == result
    row = result["buildings"][0]
    identity = json.dumps([
        1, "custom keep", "fortress", result["profile"]["class_weights"], -1, 1357, 0,
    ], sort_keys=True, ensure_ascii=False)
    rng = random.Random(int(hashlib.sha256(identity.encode()).hexdigest(), 16))
    assert rng.randint(1, 100) == row["rolls"]["class_d100"]
    shared = roll_building_details(rng, building_class, -1, 1000, HOUSING_SCENARIOS[1])
    for field in ("structure", "condition", "use", "occupants", "warnings"):
        assert row[field] == shared[field]


@pytest.mark.parametrize("changes", [
    {"location": ""}, {"location": "  "}, {"location": "x" * 121}, {"location": None},
    {"location": "a\x00b"}, {"profile": "dock"}, {"profile": None},
    {"count": 0}, {"count": 101}, {"count": True}, {"count": 1.5},
    {"seed": -1}, {"seed": 4294967296}, {"seed": True}, {"seed": 1.5},
    {"footprint_sqft": 0}, {"footprint_sqft": 1000001}, {"footprint_sqft": True},
    {"footprint_sqft": float("nan")}, {"footprint_sqft": float("inf")},
    {"scenario": "unknown"}, {"class_b_weight": 5},
    {"class_b_weight": True, "class_c_weight": 0, "class_d_weight": 100},
    {"class_b_weight": 1.5, "class_c_weight": 0, "class_d_weight": 100},
    {"class_b_weight": -1, "class_c_weight": 1, "class_d_weight": 100},
    {"class_b_weight": 0, "class_c_weight": 0, "class_d_weight": 0},
    {"class_b_weight": 101, "class_c_weight": 0, "class_d_weight": 0},
    {"condition_modifier": -2}, {"condition_modifier": 2}, {"condition_modifier": True},
    {"condition_modifier": 0.5},
])
def test_invalid_generic_generation_is_not_silently_repaired(changes):
    with pytest.raises(ValueError):
        generate_location(**{"location": "New Place", **changes})


def test_result_mutation_does_not_change_presets_source_or_future_generation():
    before = generate_location("New Place")
    changed = generate_location("New Place")
    changed["profile"]["class_weights"]["D"] = -100
    changed["buildings"][0]["occupants"]["named_people"].append("Not a known resident")
    changed["source"]["citations"].clear()
    assert generate_location("New Place") == before


def test_cli_api_and_mcp_share_the_read_only_engine(monkeypatch, capsys):
    expected = generate_location("Custom Port", profile="port", count=3, seed=14,
                                 class_b_weight=0, class_c_weight=100, class_d_weight=0,
                                 condition_modifier=0)
    params = {key: [str(value)] for key, value in expected["parameters"].items()}
    assert web.GET_ROUTES["/api/generated-location"](object(), params) == expected
    assert web.GET_ROUTES["/api/location-profiles"](object(), {}) == location_profiles()
    assert "/api/generated-location" not in web.POST_ROUTES
    monkeypatch.setattr(cli, "build_world", lambda _args: pytest.fail("Must not initialize world or ledger"))
    args = ["--seed", "14", "generate-location", "Custom Port", "--profile", "port",
            "--count", "3", "--class-b-weight", "0", "--class-c-weight", "100",
            "--class-d-weight", "0", "--condition-modifier", "0"]
    assert cli.main(["--json", *args]) == 0
    assert json.loads(capsys.readouterr().out) == expected
    assert cli.main(args) == 0
    text = capsys.readouterr().out
    assert "Custom Port" in text and "Assumed profile" in text
    assert cli.main(["generate-location", "Here", "--count", "0"]) == 2
    assert "count" in capsys.readouterr().err
    pytest.importorskip("mcp")
    from faerun import mcp_server
    monkeypatch.setattr(mcp_server, "world", lambda: pytest.fail("Must not initialize world"))
    assert mcp_server.generate_location(**expected["parameters"]) == expected
    assert mcp_server.get_location_generation_profiles() == location_profiles()
    assert "error" in mcp_server.generate_location("Custom Port", profile="invalid")


@pytest.mark.parametrize("params", [
    {}, {"location": [""]}, {"location": ["Test"], "count": ["1.5"]},
    {"location": ["Test"], "profile": ["invalid"]},
    {"location": ["Test"], "class_b_weight": ["40"]},
    {"location": ["Test"], "condition_modifier": ["-2"]},
    {"location": ["Test"], "footprint_sqft": ["nan"]},
])
def test_http_adapter_surfaces_invalid_input(params):
    with pytest.raises((ValueError, web.ApiError)):
        web.api_generated_location(object(), params)
