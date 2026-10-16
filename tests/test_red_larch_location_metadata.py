from faerun.climate import location_climate
from faerun.data.location_metadata import location_metadata
from faerun.demographics import location_demographics
from faerun.location import location_detail
from faerun.world import World


def test_red_larch_metadata_is_curated_without_market_snapshot_as_canon():
    metadata = location_metadata("red_larch")
    assert metadata["id"] == "red_larch"
    assert metadata["periods"]["planning_baseline_dr"] == 1492
    assert metadata["sketch"]["file"] == "red-larch-sketch.svg"
    assert metadata["collected_research"]["snapshot_status"] == "Simulation scenario, not canon"
    assert "engine_record" not in metadata
    assert location_metadata("arrabar") is None


def test_red_larch_detail_includes_metadata_and_preserves_climate_demographics():
    world = World()
    settlement = world.find_settlement("red_larch")
    detail = location_detail("red_larch", world=world)
    assert detail["location_metadata"]["position"]["location_id"] == "fps-red-larch"
    assert detail["climate"] == location_climate(settlement, detail["season"])
    assert detail["demographics"] == location_demographics(settlement)
    assert detail["climate"]["engine_class"] != "subtropical"
    assert any(note["basis"] == "inference" for note in detail["climate"]["local_notes"])
    assert detail["demographics"]["status"] == "unresearched"
    assert detail["demographics"]["groups"] == []
