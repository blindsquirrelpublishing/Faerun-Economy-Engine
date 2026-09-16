from copy import deepcopy
import json

import pytest

from faerun import cli, web
from faerun.buildinggen import (
    CONDITIONS, SOURCE, USE_ROLLS, _class_for_roll, _occupants, _structure, generate_buildings,
)
from faerun.census import HOUSING_SCENARIOS
from faerun.data.businesses import BUSINESSES
from faerun.data.waterdeep import PEOPLE


@pytest.mark.parametrize("ward,expected", [
    ("castle", "BBBBCCCCDD"), ("north", "BBBBBBCCCC"),
    ("sea", "BBBBBBBCCC"), ("trades", "BBBCCCCDDD"),
    ("dock", "BCCCCCDDDD"), ("south", "BB??CCCDDD"),
])
def test_source_class_dice_exhaustive(ward, expected):
    assert "".join(_class_for_roll(ward, roll) or "?" for roll in range(1, 11)) == expected


def test_source_story_dice_and_use_tables():
    assert [_structure("B", roll)["stories"] for roll in range(1, 9)] == [1, 2, 3, 4, 1, 2, 3, 4]
    assert [_structure("B", roll)["basement"] for roll in range(1, 9)] == [False] * 4 + [True] * 4
    assert [_structure("C", roll)["stories"] for roll in range(1, 5)] == [2, 3, 3, 2]
    assert [_structure("C", roll)["basement"] for roll in range(1, 5)] == [False, False, True, True]
    assert all(_structure("D", roll)["stories"] == 1 for roll in range(1, 5))
    assert [_structure("D", roll)["basement"] for roll in range(1, 5)] == [False, False, True, False]
    assert _structure("B", 8)["tower_or_partial_upper"]
    assert _structure("D", 4)["tower_or_partial_upper"]
    assert USE_ROLLS["B"] == (
        "hoist_warehouse", "hoist_warehouse", "major_offices", "major_offices",
        "rooming_house", "rooming_house", "shop_apartments", "office_apartments",
        "noble_family", "noble_individual",
    )
    assert USE_ROLLS["C"] == (
        "warehouse", "shop_offices", "shop_apartments", "shop_storage",
        "rooming_house", "rooming_house", "shop_mixed", "shop_mixed", "apartments", "apartments",
    )
    assert USE_ROLLS["D"] == (
        "warehouse", "warehouse", "warehouse", "warehouse", "single_family",
        "rooming_house", "shop", "office", "apartments", "shared_storage",
    )


def test_repeatability_prefixes_aliases_and_sensitivity_hold_buildings_fixed():
    first = generate_buildings("Dock Ward", count=10, seed=98)
    assert first == generate_buildings("dock", count=10, seed=98)
    assert first["buildings"] == generate_buildings("Dock Ward", count=30, seed=98)["buildings"][:10]
    assert first != generate_buildings("Dock Ward", count=10, seed=99)
    alternative = generate_buildings("Dock Ward", count=10, seed=98, footprint_sqft=2000, scenario="high")
    for base, changed in zip(first["buildings"], alternative["buildings"]):
        for field in ("id", "rolls", "building_class", "structure", "condition", "use"):
            assert base[field] == changed[field]
    assert generate_buildings("South Ward") == generate_buildings("Southern Ward")
    assert json.loads(json.dumps(first))["generated"] is True


def test_southern_missing_rolls_are_not_rerolled_or_treated_as_zero():
    data = generate_buildings("South Ward", count=100)
    unresolved = [b for b in data["buildings"] if b["status"] == "unresolved_source_roll"]
    assert unresolved
    for row in unresolved:
        assert row["rolls"]["class_d10"] in (3, 4)
        assert row["occupants"] is None
        assert row["structure"] is None
        assert row["warnings"]
    assert data["summary"]["unresolved_buildings"] == len(unresolved)
    override = generate_buildings("South Ward", count=100, building_class="C")
    assert override["summary"]["unresolved_buildings"] == 0
    assert all(b["rolls"]["class_d10"] is None for b in override["buildings"])


def test_provenance_condition_counts_and_no_invented_people_or_locations():
    before = deepcopy((BUSINESSES, PEOPLE, SOURCE))
    for ward in ("Sea Ward", "North Ward", "Castle Ward", "Trades Ward", "Dock Ward"):
        data = generate_buildings(ward, count=100)
        assert data["generated"] and not data["surveyed"]
        assert not data["can_replace_population"] and not data["live_market_integration"]
        assert data["summary"]["city_population"] is None
        for row in data["buildings"]:
            assert row["provenance"] == "generated_scenario"
            assert row["map_position"] is None and row["historical_business_id"] is None
            assert row["occupants"]["named_people"] == []
            assert row["citations"] == SOURCE["citations"][:2]
            adjusted = row["rolls"]["condition_adjusted"]
            assert row["condition"] == CONDITIONS[adjusted]
            if adjusted in (0, 1, 7):
                assert all(row["occupants"][key] == 0 for key in ("residents", "lodging_guests", "staff"))
            assert row["occupants"]["staff"] == sum(row["occupants"]["staff_roles"].values())
        assert data["summary"]["modeled_residents_in_resolved_buildings"] == sum(
            b["occupants"]["residents"] for b in data["buildings"])
    assert before == (BUSINESSES, PEOPLE, SOURCE)


def test_occupancy_counts_upper_floors_staff_and_source_proprietor_rule():
    central = HOUSING_SCENARIOS[1]
    apartments = _occupants("shop_apartments", 3, 1000, central, True, None)
    assert apartments["residential_floor_equivalents"] == 2
    assert apartments["occupied_household_sized_units"] == 3
    assert apartments["residents"] == 15 and apartments["staff"] == 2
    assert _occupants("shop_apartments", 1, 1000, central, True, None)["residents"] == 0
    mixed = _occupants("shop_mixed", 3, 1000, central, True, None)
    assert mixed["residential_floor_equivalents"] == 1
    assert mixed["staff_roles"] == {"Shop workers": 2, "Office workers": 3}
    resident = _occupants("shop_storage", 3, 1000, central, True, True)
    assert resident["residents"] == 1 and "Night watchman" not in resident["staff_roles"]
    nonresident = _occupants("shop_storage", 3, 1000, central, True, False)
    assert nonresident["residents"] == 0 and nonresident["staff_roles"]["Night watchman"] == 1
    rooming = _occupants("rooming_house", 2, 1000, central, True, None)
    assert rooming["residents"] + rooming["lodging_guests"] == 15
    assert _occupants("noble_individual", 4, 1000, central, True, None)["residents"] == 1
    assert _occupants("single_family", 1, 1000, central, True, None)["residents"] == 5


@pytest.mark.parametrize("kwargs", [
    {"ward": "unknown"}, {"ward": "City of the Dead"}, {"building_class": "A"},
    {"building_class": "unknown"}, {"count": 0}, {"count": 101}, {"count": True},
    {"count": 2.5}, {"seed": True}, {"seed": -1}, {"seed": 4294967296},
    {"seed": 1.2}, {"footprint_sqft": 0}, {"footprint_sqft": -1},
    {"footprint_sqft": float("nan")}, {"footprint_sqft": float("inf")},
    {"footprint_sqft": True}, {"footprint_sqft": 1000001}, {"scenario": "guess"},
])
def test_invalid_requests_are_explicit(kwargs):
    with pytest.raises(ValueError):
        generate_buildings(**kwargs)


def test_returned_data_cannot_mutate_source_or_future_scenarios():
    baseline = generate_buildings()
    changed = generate_buildings()
    changed["source"]["title"] = "changed"
    changed["buildings"][0]["warnings"].append("changed")
    changed["buildings"][0]["citations"][0]["printed_page"] = -1
    assert baseline == generate_buildings()


def test_public_surfaces_use_shared_generator_without_world_or_ledger(monkeypatch, capsys):
    expected = generate_buildings("Dock Ward", count=3, seed=12)
    assert web.GET_ROUTES["/api/generated-buildings"](object(), {
        "ward": ["Dock Ward"], "count": ["3"], "seed": ["12"],
    }) == expected
    assert "/api/generated-buildings" not in web.POST_ROUTES
    monkeypatch.setattr(cli, "build_world", lambda _args: pytest.fail("Must not open world or trade ledger"))
    assert cli.main(["--json", "--seed", "12", "generate-buildings", "--ward", "Dock Ward", "--count", "3"]) == 0
    assert json.loads(capsys.readouterr().out) == expected
    assert cli.main(["generate-buildings", "--count", "0"]) == 2
    assert "count" in capsys.readouterr().err
    pytest.importorskip("mcp")
    from faerun.mcp_server import generate_city_buildings
    assert generate_city_buildings("Dock Ward", count=3, seed=12) == expected
    assert "error" in generate_city_buildings(building_class="A")


@pytest.mark.parametrize("query,expected_status", [
    ("?count=2&seed=0", 200), ("?count=101", 400),
    ("?seed=abc", 400), ("?footprint_sqft=nan", 400),
    ("?ward=City%20of%20the%20Dead", 400),
])
def test_http_status_codes(monkeypatch, query, expected_status):
    handler = web.Handler.__new__(web.Handler)
    handler.path = "/api/generated-buildings" + query
    replies = []
    handler._send_json = lambda data, status=200: replies.append((data, status))
    monkeypatch.setattr(web, "get_world", lambda: object())
    handler.do_GET()
    assert replies[0][1] == expected_status
