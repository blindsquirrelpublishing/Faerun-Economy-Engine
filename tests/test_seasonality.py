"""Harvest timing is distinct from final consumption and workshop capacity."""

import math

import pytest

from faerun.calendar import FESTIVAL_MONTHS, HarptosDate, month_name
from faerun.data.commodities import COMMODITIES, COMMODITIES_BY_ID
from faerun.data.settlements import SETTLEMENTS_BY_ID
from faerun.models import C, S
from faerun.seasonality import (
    climate_for,
    demand_multiplier,
    production_multiplier,
    seasonal_profile,
)


def market(**kwargs):
    return S("Test Market", "Test Region", "test_zone", 100, 0, 0, **kwargs)


def monthly_rates(commodity, settlement):
    return [
        production_multiplier(commodity, settlement, HarptosDate(1492, month, 1))
        for month in range(1, 13)
    ]


def test_custom_goods_keep_flat_profiles_and_no_storage_by_default():
    commodity = C("custom", "Custom", "food", 1, season={"winter": 9, "summer": 0.1})
    profile = seasonal_profile(commodity, market(), HarptosDate(1492, 1, 31))
    assert profile["climate"] == "temperate"
    assert profile["production_multiplier"] == profile["demand_multiplier"] == 1
    assert profile["storage_days"] == profile["storage_loss"] == profile["reserve_days"] == 0
    assert all(row["production_multiplier"] == row["demand_multiplier"] == 1
               for row in profile["months"])


@pytest.mark.parametrize("field", ["production_profile", "demand_profile"])
@pytest.mark.parametrize("weights", [
    [1] * 11,
    [1] * 13,
    [0] * 12,
    [-1] + [1] * 11,
    [float("nan")] + [1] * 11,
    [float("inf")] + [1] * 11,
    [-float("inf")] + [1] * 11,
    ["bad"] + [1] * 11,
    [[1]] + [1] * 11,
])
def test_invalid_profiles_are_rejected_with_commodity_and_profile_context(field, weights):
    commodity = C("custom", "Custom", "food", 1)
    setattr(commodity, field, weights)
    with pytest.raises(ValueError, match=f"custom {field.replace('_', ' ')}"):
        seasonal_profile(commodity, market(), HarptosDate())


@pytest.mark.parametrize("weights", [
    list(range(12)),
    [1] + [0] * 11,
    [0, 1] + [0] * 10,
    [1e308] * 12,
    [1e-300] * 12,
])
def test_normalization_preserves_365_daily_baselines_including_festival_days(weights):
    commodity = C("custom", "Custom", "food", 1,
                  production_profile=weights, demand_profile=list(reversed(weights)))
    settlement = market()
    production, demand = [], []
    for month in range(1, 13):
        for day in range(1, (31 if month in FESTIVAL_MONTHS else 30) + 1):
            date = HarptosDate(1492, month, day)
            production.append(production_multiplier(commodity, settlement, date))
            demand.append(demand_multiplier(commodity, date))
    assert math.fsum(production) == pytest.approx(365)
    assert math.fsum(demand) == pytest.approx(365)
    assert all(math.isfinite(value) and value >= 0 for value in production + demand)


def test_single_festival_month_uses_31_days_and_profiles_repeat_annually():
    commodity = C("custom", "Custom", "food", 1, production_profile=[1.0] + [0.0] * 11)
    settlement = market()
    assert production_multiplier(commodity, settlement, HarptosDate(1492, 1, 31)) == pytest.approx(365 / 31)
    assert production_multiplier(commodity, settlement, HarptosDate(1493, 1, 31)) == pytest.approx(365 / 31)
    assert production_multiplier(commodity, settlement, HarptosDate(1492, 2, 1)) == 0


@pytest.mark.parametrize(("settlement_id", "climate"), [
    ("waterdeep", "temperate"),
    ("neverwinter", "temperate"),
    ("bryn_shander", "cold"),
    ("luskan", "cold"),
    ("calimport", "arid"),
    ("port_nyanzaru", "tropical"),
    ("halarahh", "tropical"),
    ("menzoberranzan", "underdark"),
])
def test_climate_uses_actual_gazetteer_settlements(settlement_id, climate):
    assert climate_for(SETTLEMENTS_BY_ID[settlement_id]) == climate


@pytest.mark.parametrize(("attributes", "climate"), [
    ({"terrain": "tundra"}, "cold"),
    ({"terrain": "taiga"}, "cold"),
    ({"terrain": "desert"}, "arid"),
    ({"terrain": "jungle"}, "tropical"),
    ({"terrain": "cavern", "traits": "cold"}, "underdark"),
    ({"underdark": True, "terrain": "desert"}, "underdark"),
    ({"terrain": "desert", "traits": "tropical"}, "tropical"),
    ({"traits": "temperate"}, "temperate"),
])
def test_climate_traits_and_terrain_precedence(attributes, climate):
    assert climate_for(market(**attributes)) == climate


@pytest.mark.parametrize(("zone", "climate"), [
    ("icewind", "cold"),
    ("silvermarches", "cold"),
    ("calimshan", "arid"),
    ("chult", "tropical"),
    ("underdark_south", "underdark"),
    ("unknown_zone", "temperate"),
])
def test_climate_falls_back_to_zone(zone, climate):
    settlement = market()
    settlement.zone = zone
    assert climate_for(settlement) == climate


def test_override_precedence_accepts_slugs_and_empty_overrides_are_flat():
    commodity = C("custom", "Custom", "food", 1, production_profile=[1.0] + [0.0] * 11)
    settlement = market()
    overrides = {
        "temperate": [0.0, 1.0] + [0.0] * 10,
        "TEST ZONE": [0.0, 0.0, 1.0] + [0.0] * 9,
        "test_region": [0.0, 0.0, 0.0, 1.0] + [0.0] * 8,
        "test_market": [0.0, 0.0, 0.0, 0.0, 1.0] + [0.0] * 7,
    }
    commodity.regional_production_profiles = overrides
    for key, peak in [("test_market", 5), ("test_region", 4), ("TEST ZONE", 3), ("temperate", 2)]:
        rates = monthly_rates(commodity, settlement)
        assert rates.index(max(rates)) + 1 == peak
        assert sum(rate > 0 for rate in rates) == 1
        del overrides[key]
    assert monthly_rates(commodity, settlement)[0] == pytest.approx(365 / 31)
    overrides["temperate"] = []
    assert monthly_rates(commodity, settlement) == [1] * 12


def test_invalid_selected_override_is_not_silently_ignored():
    commodity = C("custom", "Custom", "food", 1,
                  regional_production_profiles={"temperate": [0] * 12})
    with pytest.raises(ValueError, match=r"custom production profile \[temperate\].*all zero"):
        production_multiplier(commodity, market(), HarptosDate())


def test_profile_edits_are_not_hidden_by_normalization_cache():
    commodity = C("custom", "Custom", "food", 1, production_profile=[1.0] + [0.0] * 11)
    settlement = market()
    assert production_multiplier(commodity, settlement, HarptosDate()) > 0
    commodity.production_profile[0:2] = [0, 1]
    assert production_multiplier(commodity, settlement, HarptosDate()) == 0


def test_report_contains_all_months_current_values_and_storage_without_mutating_data():
    commodity = C("custom", "Custom", "food", 1,
                  production_profile=list(range(12)), demand_profile=list(range(12, 0, -1)),
                  storage_days=300, storage_loss=0.001, reserve_days=45)
    settlement, date = market(), HarptosDate(1492, 9, 31)
    report = seasonal_profile(commodity, settlement, date)
    assert [row["month"] for row in report["months"]] == list(range(1, 13))
    assert [row["name"] for row in report["months"]] == [month_name(month) for month in range(1, 13)]
    assert report["production_multiplier"] == production_multiplier(commodity, settlement, date)
    assert report["demand_multiplier"] == demand_multiplier(commodity, date)
    assert report["storage_days"] == 300
    assert report["storage_loss"] == 0.001
    assert report["reserve_days"] == 45
    report["months"][0]["production_multiplier"] = 999
    assert commodity.production_profile == list(range(12))
    assert seasonal_profile(commodity, settlement, date)["months"][0]["production_multiplier"] == 0


def test_wheat_and_corn_have_distinct_harvests_and_no_crop_scarcity_demand_curve():
    settlement = SETTLEMENTS_BY_ID["waterdeep"]
    wheat = COMMODITIES_BY_ID["grain"]
    corn = COMMODITIES_BY_ID["corn"]
    assert monthly_rates(wheat, settlement) != monthly_rates(corn, settlement)
    assert monthly_rates(wheat, settlement)[0] == monthly_rates(corn, settlement)[0] == 0
    assert monthly_rates(wheat, settlement)[8] > 1
    assert monthly_rates(corn, settlement)[9] > 1
    for commodity in [wheat, corn, COMMODITIES_BY_ID["bread"]]:
        assert all(demand_multiplier(commodity, HarptosDate(1492, month, 1)) == 1
                   for month in range(1, 13))


def test_regional_wheat_harvests_shift_and_tropical_coffee_has_multiple_windows():
    wheat = COMMODITIES_BY_ID["grain"]
    cold = monthly_rates(wheat, SETTLEMENTS_BY_ID["bryn_shander"])
    arid = monthly_rates(wheat, SETTLEMENTS_BY_ID["calimport"])
    assert cold.index(max(cold)) + 1 == 10
    assert arid.index(max(arid)) + 1 in {4, 5}
    coffee = COMMODITIES_BY_ID["coffee"]
    chult = monthly_rates(coffee, SETTLEMENTS_BY_ID["port_nyanzaru"])
    halruaa = monthly_rates(coffee, SETTLEMENTS_BY_ID["halarahh"])
    assert chult[2] > chult[1] and chult[2] > chult[3]
    assert chult[8] > chult[7] and chult[8] > chult[9]
    assert chult != halruaa
    assert halruaa[4] > chult[4]


def test_manufactured_goods_are_not_assigned_annual_harvest_shutdowns():
    settlement = market()
    for commodity in COMMODITIES:
        if commodity.bom or commodity.id in {"cheese", "butter", "linen", "leather", "paprika"}:
            assert monthly_rates(commodity, settlement) == [1] * 12, commodity.id
            assert commodity.regional_production_profiles == {}, commodity.id
    assert monthly_rates(COMMODITIES_BY_ID["herbs_healing"], settlement)[0] == 0
    assert monthly_rates(COMMODITIES_BY_ID["potion_healing"], settlement)[0] == 1


def test_final_consumption_curves_are_limited_and_independent_of_supply():
    winter, summer = HarptosDate(1492, 1, 1), HarptosDate(1492, 7, 1)
    for commodity_id in ("coal", "charcoal", "clothing_common", "furs", "candles", "lamp_oil"):
        commodity = COMMODITIES_BY_ID[commodity_id]
        assert demand_multiplier(commodity, winter) > demand_multiplier(commodity, summer)
        assert 0.5 < demand_multiplier(commodity, summer) < 1.5
        assert monthly_rates(commodity, market()) == [1] * 12
    for commodity_id in ("fruit", "flour", "coffee", "potion_healing"):
        assert COMMODITIES_BY_ID[commodity_id].demand_profile == []
    assert COMMODITIES_BY_ID["grain"].season["spring"] == 1.25


def test_storage_matches_trade_form_and_does_not_change_custom_constructor_defaults():
    goods = COMMODITIES_BY_ID
    assert goods["grain"].storage_days >= 365
    assert goods["bread"].storage_days == 3
    assert 3 < goods["coffee"].storage_days <= 90 < goods["grain"].storage_days
    assert goods["coffee"].storage_loss > goods["grain"].storage_loss
    assert goods["herbs_healing"].storage_days >= 180
    assert goods["potion_healing"].storage_days >= 365
    assert C("custom", "Custom", "food", 1).storage_days == 0
    assert all(0 <= c.reserve_days <= c.storage_days and 0 <= c.storage_loss <= 1
               for c in COMMODITIES)


def test_catalogue_serialization_includes_profile_and_storage_fields():
    commodity = COMMODITIES_BY_ID["grain"]
    data = commodity.to_dict()
    for field in ("production_profile", "demand_profile", "regional_production_profiles",
                  "storage_days", "storage_loss", "reserve_days"):
        assert data[field] == getattr(commodity, field)
    data["production_profile"][0] = 999
    data["regional_production_profiles"]["cold"][0] = 999
    assert commodity.production_profile[0] == 0
    assert commodity.regional_production_profiles["cold"][0] == 0


def test_every_catalogue_calendar_and_regional_override_conserves_annual_rates():
    settlement = market()
    for commodity in COMMODITIES:
        for zone in ["test_zone", *commodity.regional_production_profiles]:
            settlement.zone = zone
            profile = seasonal_profile(commodity, settlement, HarptosDate())
            for column in ("production_multiplier", "demand_multiplier"):
                total = math.fsum(row[column] * (31 if row["month"] in FESTIVAL_MONTHS else 30)
                                  for row in profile["months"])
                assert total == pytest.approx(365), (commodity.id, zone, column)
