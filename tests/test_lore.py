from faerun.data.lore import LORE
from faerun.lore import location_lore
from faerun.models import Settlement
from faerun.world import World


def test_every_market_has_separate_model_context():
    world = World()
    for settlement in world.settlements.values():
        result = location_lore(settlement)
        assert result["settlement_id"] == settlement.id
        assert settlement.name in result["model_context"]
        assert "simulation assumptions" in result["model_context"]
        assert result["status"] in {"researched", "unresearched"}


def test_researched_entries_have_sources_and_era_notes():
    for entry in LORE.values():
        assert entry["status"] == "researched"
        assert len(entry["paragraphs"]) >= 2
        assert entry["era_note"]
        assert entry["sources"]
        for source in entry["sources"]:
            assert source["url"].startswith("https://")
            assert source["accessed"]
            assert source["kind"] == "secondary"


def test_unknown_location_does_not_invent_a_source():
    settlement = Settlement("unknown", "Unknown", "Test", "test", 12, 0, 0)
    result = location_lore(settlement)
    assert result["status"] == "unresearched"
    assert result["sources"] == []
    assert result["paragraphs"] == []


def test_lore_response_cannot_mutate_catalogue():
    world = World()
    result = location_lore(world.find_settlement("Waterdeep"))
    result["paragraphs"].clear()
    assert LORE["waterdeep"]["paragraphs"]