"""Catalog-wide checks for unsourced model-derived climate context."""

from faerun.climate import location_climate
from faerun.data.climate import REGIONAL_CLIMATES, SETTLEMENT_CLIMATES
from faerun.data.lore import LORE
from faerun.data.settlements import SETTLEMENTS
from faerun.models import Settlement, slugify
from faerun.seasonality import climate_for


def test_remaining_catalog_settlements_get_only_sourced_or_estimated_climate():
    remaining = [place for place in SETTLEMENTS if place.id not in LORE]
    assert len(SETTLEMENTS) == 325
    assert len(LORE) == 16
    assert len(remaining) == 309
    statuses = {"estimated": 0, "sourced": 0}
    for place in remaining:
        result = location_climate(place, "winter")
        sourced = (place.id in SETTLEMENT_CLIMATES
                   or slugify(place.zone) in REGIONAL_CLIMATES)
        assert result["status"] == ("sourced" if sourced else "estimated"), place.id
        assert result["engine_class"] == climate_for(place)
        assert result["settlement_id"] == place.id
        assert result["current_season"] == "winter"
        statuses[result["status"]] += 1
        if not sourced:
            assert result["sources"] == [] and result["seasons"] == []
            assert "not a sourced" in result["scope_note"]
            assert place.zone in result["scope_note"]
            assert "1492 DR planning baseline" in result["era_note"]
    assert statuses == {"estimated": 290, "sourced": 19}


def test_class_context_covers_every_model_class_without_claiming_local_weather():
    for place in SETTLEMENTS:
        if place.id in LORE or place.id in SETTLEMENT_CLIMATES:
            continue
        if slugify(place.zone) in REGIONAL_CLIMATES:
            continue
        result = location_climate(place)
        assert climate_for(place) in result["label"]
        assert "local temperature and precipitation are unknown" in result["summary"] or (
            climate_for(place) == "underdark" and "surface weather cannot be inferred" in result["summary"]
        )
        assert "no observed" in result["calendar_note"].lower()


def test_reviewed_settlements_and_unknown_settlements_remain_unresearched_without_source():
    for place in SETTLEMENTS:
        if place.id in LORE and place.id not in SETTLEMENT_CLIMATES and slugify(place.zone) not in REGIONAL_CLIMATES:
            assert location_climate(place)["status"] == "unresearched", place.id
    unknown = Settlement("outside_catalog", "Outside Catalog", "Test", "icewind", 1, 0, 0)
    assert location_climate(unknown)["status"] == "unresearched"


def test_estimated_result_is_not_shared_with_future_responses():
    place = next(place for place in SETTLEMENTS if place.id not in LORE
                 and place.id not in SETTLEMENT_CLIMATES
                 and slugify(place.zone) not in REGIONAL_CLIMATES)
    result = location_climate(place)
    result["sources"].append({"title": "fabricated"})
    result["seasons"].append({"season": "winter"})
    assert location_climate(place)["sources"] == []
    assert location_climate(place)["seasons"] == []
