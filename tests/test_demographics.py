import pytest

from faerun.data.demographics import DEMOGRAPHICS_STATUSES, SETTLEMENT_DEMOGRAPHICS
from faerun.data.lore import LORE
from faerun.demographics import location_demographics
from faerun.location import location_detail
from faerun.models import Settlement
from faerun.world import World


def test_every_researched_lore_entry_has_a_demographics_record():
    assert set(LORE) <= set(SETTLEMENT_DEMOGRAPHICS)


@pytest.mark.parametrize("settlement_id", sorted(SETTLEMENT_DEMOGRAPHICS))
def test_demographics_records_follow_the_schema(settlement_id):
    entry = SETTLEMENT_DEMOGRAPHICS[settlement_id]
    assert entry["status"] in DEMOGRAPHICS_STATUSES
    assert entry["era_note"]
    if entry["status"] == "unresearched":
        assert entry["groups"] == []
        assert entry["sources"] == []
        return
    assert entry["reference_period"] and entry["scope"]
    assert entry["groups"]
    assert entry["sources"]
    for source in entry["sources"]:
        assert source["url"].startswith("https://")
        assert source["accessed"]
        assert source["kind"] in {"primary", "secondary"}
    shares = [g["share_pct"] for g in entry["groups"] if g["share_pct"] is not None]
    assert all(0 <= share <= 100 for share in shares)
    assert sum(shares) <= 100.0
    estimates = [g.get("estimated_share_pct") for g in entry["groups"]
                 if g.get("estimated_share_pct") is not None]
    if entry["status"] == "quantified":
        assert shares and not estimates
    elif entry["status"] == "estimated":
        assert not shares
        assert len(estimates) == len(entry["groups"])
        assert all(0 <= estimate <= 100 for estimate in estimates)
        assert sum(estimates) == 100
        assert any("no source supplies" in note.lower() for note in entry["notes"])
    else:
        assert not shares and not estimates
        assert all(g["descriptor"] for g in entry["groups"])
    for group in entry["groups"]:
        assert group["race"]
        for sub in group.get("subgroups", []):
            assert sub["name"]
            assert sub["share_pct"] is None or 0 <= sub["share_pct"] <= 100


def test_unknown_location_is_unresearched_and_invents_nothing():
    settlement = Settlement("unknown", "Unknown", "Test", "test", 12, 0, 0)
    result = location_demographics(settlement)
    assert result["status"] == "unresearched"
    assert result["groups"] == []
    assert result["sources"] == []
    assert result["settlement_id"] == "unknown"


def test_demographics_stay_separate_from_the_modeled_population():
    settlement = Settlement("secomber", "Secomber", "Test", "test", 1300, 0, 0)
    result = location_demographics(settlement)
    assert result["status"] == "estimated"
    assert sum(g["estimated_share_pct"] for g in result["groups"]) == 100
    assert all(g["share_pct"] is None for g in result["groups"])
    assert "1,300" in result["model_note"]
    assert "not divided by race" in result["model_note"]
    assert settlement.population == 1300


def test_hlondeth_carries_sourced_percentages():
    result = location_demographics(Settlement("hlondeth", "Hlondeth", "Test", "test", 60000, 0, 0))
    assert result["status"] == "quantified"
    shares = {g["race"]: g["share_pct"] for g in result["groups"]}
    assert shares["Human"] == 84.0 and shares["Kobold"] == 15.0
    human = next(g for g in result["groups"] if g["race"] == "Human")
    assert sum(sub["share_pct"] for sub in human["subgroups"]) == 100.0


def test_historical_neverwinter_groups_and_waterdeep_scope_are_not_presented_as_1492_census():
    neverwinter = SETTLEMENT_DEMOGRAPHICS["neverwinter"]
    assert neverwinter["status"] == "qualitative"
    assert {group["race"] for group in neverwinter["groups"]} >= {"Human", "Half-elf", "Dwarf", "Orc"}
    assert all(group["share_pct"] is None for group in neverwinter["groups"])
    assert "1491" in neverwinter["reference_period"]
    waterdeep = SETTLEMENT_DEMOGRAPHICS["waterdeep"]
    assert "not explicit" in waterdeep["scope"]
    assert sum(group["share_pct"] for group in waterdeep["groups"]) == 100
    hlondeth = SETTLEMENT_DEMOGRAPHICS["hlondeth"]
    assert "not independently established" in hlondeth["scope"]
    assert next(g for g in hlondeth["groups"] if g["race"] == "Halfling")["share_pct"] is None


def test_demographics_response_cannot_mutate_catalogue():
    world = World()
    result = location_demographics(world.find_settlement("Secomber"))
    result["groups"].clear()
    assert SETTLEMENT_DEMOGRAPHICS["secomber"]["groups"]


def test_location_detail_carries_demographics():
    world = World()
    detail = location_detail("secomber", world=world)
    assert detail["demographics"]["settlement_id"] == "secomber"
    assert [g["race"] for g in detail["demographics"]["groups"]][:2] == ["Human", "Halfling"]
    assert [g["estimated_share_pct"] for g in detail["demographics"]["groups"]] == [49, 45, 3, 2, 1]
    arrabar = location_detail("arrabar", world=world)["demographics"]
    assert arrabar["status"] == "qualitative"
