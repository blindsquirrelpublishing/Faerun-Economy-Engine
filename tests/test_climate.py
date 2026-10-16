from faerun.climate import location_climate
from faerun.data.climate import LOCAL_NOTES, REGIONAL_CLIMATES
from faerun.location import location_detail
from faerun.models import Settlement
from faerun.world import World


def test_arrabar_gets_sourced_vilhon_climate_with_model_class_kept_separate():
    world = World()
    result = location_climate(world.find_settlement("arrabar"), "summer")
    assert result["status"] == "sourced"
    assert result["label"] == "Warm, humid, subtropical"
    assert result["engine_class"] == "temperate"
    assert "does not decide whether a settlement can produce a good" in result["engine_note"]
    assert result["current_season"] == "summer"
    by_season = {row["season"]: row["conditions"] for row in result["seasons"]}
    assert list(by_season) == ["spring", "summer", "autumn", "winter"]
    assert "110°F / 43°C" in by_season["summer"]
    assert "snow is rare" in by_season["winter"]
    assert "not readings specific to this settlement" in result["scope_note"]
    assert all(source["url"].startswith("https://") and "utm_" not in source["url"]
               for source in result["sources"])
    assert {note["basis"] for note in result["local_notes"]} == {"inference"}


def test_regional_north_placements_are_not_conflated_with_engine_class():
    world = World()
    inland = ("amphail", "goldenfields", "griffon_s_nest", "red_larch",
              "stone_bridge", "triboar", "yartar", "secomber")
    for identifier in inland:
        result = location_climate(world.find_settlement(identifier))
        assert result["status"] == "sourced"
        assert "inland North" in result["scope_note"]
        assert result["sources"][0]["accessed"]
        if identifier != "secomber":
            assert any(note["basis"] == "inference" for note in result["local_notes"])
    for identifier in ("leilon", "neverwinter", "waterdeep"):
        result = location_climate(world.find_settlement(identifier))
        assert result["status"] == "sourced"
        assert "coastal strip" in result["scope_note"]
        assert result["seasons"] == []
    for identifier in ("daggerford", "orlumbor", "phandalin"):
        assert location_climate(world.find_settlement(identifier))["status"] == "unresearched"


def test_unresearched_location_reports_only_the_model_class():
    settlement = Settlement("somewhere", "Somewhere", "Test", "icewind", 12, 0, 0)
    result = location_climate(settlement)
    assert result["status"] == "unresearched"
    assert result["engine_class"] == "cold"
    assert result["seasons"] == [] and result["sources"] == [] and result["local_notes"] == []
    assert "No sourced climate description" in result["era_note"]


def test_climate_response_cannot_mutate_catalogue():
    world = World()
    result = location_climate(world.find_settlement("arrabar"))
    result["seasons"].clear()
    result["local_notes"].clear()
    assert REGIONAL_CLIMATES["vilhon"]["seasons"]
    assert LOCAL_NOTES["arrabar"]


def test_location_detail_carries_climate_for_the_selected_date():
    world = World()
    detail = location_detail("arrabar", world=world)
    assert detail["climate"]["settlement_id"] == "arrabar"
    assert detail["climate"]["current_season"] == detail["season"]


def test_secomber_gets_its_own_sourced_climate_without_covering_its_zone_mates():
    world = World()
    result = location_climate(world.find_settlement("secomber"), "winter")
    assert result["status"] == "sourced"
    assert result["engine_class"] == "temperate"
    by_season = {row["season"]: row["conditions"] for row in result["seasons"]}
    assert set(by_season) == {"summer", "winter"}
    assert "-30°F / -34°C" in by_season["winter"]
    assert "not readings specific to this settlement" in result["scope_note"]
    assert all(source["url"].startswith("https://") and source["accessed"] for source in result["sources"])
    assert {note["basis"] for note in result["local_notes"]} == {"sourced", "inference"}
    assert location_climate(world.find_settlement("waterdeep"))["label"] != result["label"]
    assert location_climate(world.find_settlement("daggerford"))["status"] == "unresearched"
