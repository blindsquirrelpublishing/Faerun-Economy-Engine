from faerun.data.lore import LORE, LORE_SOURCE_POLICY
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
            assert source["kind"] in {"primary", "secondary"}


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


def test_phandalin_supplements_without_overwriting_engine_facts():
    settlement = Settlement("phandalin", "Phandalin", "Test", "test", 500, 0, 0,
                            description="Engine-authored description")
    result = location_lore(settlement)
    assert result["status"] == "researched"
    assert result["sources"][0]["url"] == "https://forgottenrealms.fandom.com/wiki/Phandalin"
    assert "three deep wells" in " ".join(result["paragraphs"])
    assert "1496" in result["era_note"]
    assert result["existing_note"] == "Engine-authored description"
    assert settlement.population == 500
    assert settlement.description == "Engine-authored description"
    assert "500" in result["model_context"]


def test_griffons_nest_uses_latest_dated_lore_and_preserves_history():
    settlement = Settlement("griffon_s_nest", "Griffon's Nest", "Test", "test", 80, 0, 0,
                            description="Engine-authored description")
    result = location_lore(settlement)
    paragraphs = " ".join(result["paragraphs"])
    assert result["status"] == "researched"
    assert result["sources"][0]["url"] == "https://forgottenrealms.fandom.com/wiki/Griffon%27s_Nest"
    assert "latest documented snapshot is 1485 DR" in paragraphs
    assert "approximately 300" in paragraphs
    assert "Halric Bonesnapper" in paragraphs
    for date in ("1358", "1366", "1372"):
        assert date in paragraphs
    assert "6,713" in paragraphs
    assert "not verified for 1492" in result["era_note"]
    assert "Targ Keifer" in result["era_note"]
    assert result["source_policy"]["role"] == "canonical_lore_reference"
    assert result["existing_note"] == "Engine-authored description"
    assert settlement.population == 80
    assert settlement.description == "Engine-authored description"


def test_neverwinter_supplements_with_historical_not_current_census():
    settlement = Settlement("neverwinter", "Neverwinter", "Sword Coast North", "swordcoast_north",
                            23000, 0, 0, ruler="Lord Protector Neverember",
                            description="Engine-authored description")
    result = location_lore(settlement)
    paragraphs = " ".join(result["paragraphs"])
    assert result["status"] == "researched"
    assert result["sources"][0]["url"] == "https://www.realmshelps.net/faerun/north.shtml"
    assert "Historical reference only" in paragraphs
    assert "23,192" in paragraphs
    assert "water clocks" in paragraphs
    assert "Not verified for 1492 DR" in result["era_note"]
    assert "census date is not explicit" in result["era_note"]
    primary_source = next(source for source in result["sources"] if source["kind"] == "primary")
    assert primary_source["url"] == "https://www.dndbeyond.com/sources/dnd/basic-rules-2014/appendix-c-the-five-factions"
    assert "Lords' Alliance" in paragraphs
    assert "no exact in-world date" in result["era_note"]
    assert "guaranteed caravan protection" in paragraphs
    assert result["source_policy"]["preferred_source"] == "Forgotten Realms Wiki"
    assert settlement.population == 23000
    assert settlement.ruler == "Lord Protector Neverember"
    assert result["existing_note"] == "Engine-authored description"
    assert "23,000" in result["model_context"]


def test_triboar_supplements_with_qualified_alternative_source():
    settlement = Settlement("triboar", "Triboar", "Dessarin Valley", "dessarin", 2500, 0, 0,
                            description="Engine-authored description")
    result = location_lore(settlement)
    paragraphs = " ".join(result["paragraphs"])
    assert result["status"] == "researched"
    assert result["sources"][0]["url"] == "https://thecampaign20xx.blogspot.com/2016/08/dungeons-dragons-guide-to-storm-kings.html"
    assert result["sources"][0]["kind"] == "secondary"
    for name in ("Othovir", "Northshield House", "Narth Tezrin"):
        assert name in paragraphs
    assert "after 1485 DR" in result["era_note"]
    assert "not verified for 1492" in result["era_note"]
    assert "not independently consulted" in result["era_note"]
    assert result["source_policy"]["preferred_source"] == "Forgotten Realms Wiki"
    assert settlement.population == 2500
    assert settlement.description == "Engine-authored description"
    assert result["existing_note"] == "Engine-authored description"
    assert "2,500" in result["model_context"]


def test_canon_source_policy_does_not_invent_research():
    settlement = Settlement("unknown", "Unknown", "Test", "test", 12, 0, 0)
    result = location_lore(settlement)
    assert result["source_policy"]["role"] == "canonical_lore_reference"
    assert result["source_policy"]["kind"] == "secondary"
    assert result["sources"] == []
    assert result["paragraphs"] == []
    assert result["status"] == "unresearched"
    result["source_policy"].clear()
    assert LORE_SOURCE_POLICY["preferred_source"] == "Forgotten Realms Wiki"