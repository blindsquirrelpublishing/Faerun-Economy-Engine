import copy
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from faerun import mobile_economic_report
from faerun.calendar import HarptosDate
from faerun.economy import price_for
from faerun.living import per_person_daily_requirements
from faerun.web import ApiError, GET_ROUTES, api_mobile_economy
from faerun.world import World


@pytest.fixture
def world():
    return World(date=HarptosDate(1492, 9, 18))


def test_travelling_report_uses_references_without_market_access(world, monkeypatch):
    def forbidden_quote(*args, **kwargs):
        pytest.fail("A travelling company must not borrow a settlement market")

    monkeypatch.setattr("faerun.mobile_economy.price_for", forbidden_quote)
    company = world.find_mobile_location("silver_wheel")
    before = copy.deepcopy(company)
    date, revision = world.date, world.revision
    report = mobile_economic_report(company, world)
    economy = report["economy"]
    accounts = economy["accounts"]
    expected = sum(
        amount * company.population * world.commodities[cid].base_price
        for cid, amount in per_person_daily_requirements(company.wealth).items()
    )

    assert economy["valuation"]["basis"] == "catalogue_reference"
    assert economy["valuation"]["market"] is None
    assert accounts["priced_household_cost_gp_per_day"] == pytest.approx(expected)
    assert accounts["priced_household_cost_gp_per_tenday"] == pytest.approx(expected * 10)
    assert accounts["household_cost_complete"] is True
    assert len(economy["household_requirements"]) == 14
    assert all(row["uncommitted_stock"] is None for row in economy["household_requirements"])
    assert accounts["revenue_gp_per_day"] is None
    assert accounts["profit_gp_per_day"] is None
    assert accounts["gross_local_product_gp_per_day"] is None
    assert all(row["revenue_gp_per_day"] is None for row in economy["services"])
    assert report["location"] == company.profile(world)
    assert report["date_iso"] == "1492-09-18"
    assert json.loads(json.dumps(report, allow_nan=False)) == report
    assert company == before
    assert (world.date, world.revision) == (date, revision)
    assert company.id not in world.settlements


def test_cover_and_replenishment_use_units_and_combined_water(world):
    report = mobile_economic_report("silver_wheel", world)
    supplies = {row["id"]: row for row in report["economy"]["supplies"]}
    food = supplies["preserved_food_lb"]
    assert food["daily_need"] == {"low": 110.0, "high": 137.5}
    assert food["days_of_cover"]["low"] == pytest.approx(1400 / 137.5)
    assert food["days_of_cover"]["high"] == pytest.approx(1400 / 110)
    assert food["additional_for_tenday"] == {"low": 0.0, "high": 0.0}
    fodder = supplies["fodder_lb"]
    assert fodder["daily_need"] == {"low": 516.0, "high": 645.0}
    assert fodder["additional_for_tenday"] == {"low": 960.0, "high": 2250.0}
    fuel = supplies["firewood_lb"]
    assert fuel["additional_for_tenday"] == {"low": 800.0, "high": 1800.0}
    water = supplies["fresh_water_gallons"]
    daily_water = report["location"]["requirements"]["total_water_gallons_per_day"]
    assert water["daily_need"] == {"low": daily_water, "high": daily_water}
    assert water["days_of_cover"]["low"] == pytest.approx(900 / daily_water)
    assert water["additional_for_tenday"]["low"] == pytest.approx(daily_water * 10 - 900)
    assert report["economy"]["limiting_supply"]["id"] == "fresh_water_gallons"


def test_inventory_valuation_does_not_invent_commodity_conversions(world):
    economy = mobile_economic_report("silver_wheel", world)["economy"]
    inventory = {row["id"]: row for row in economy["inventory"]}
    oil = inventory["lamp_oil_flasks"]
    assert oil["commodity_id"] == "lamp_oil"
    assert oil["unit"] == "flask"
    assert oil["replacement_value_gp"] == pytest.approx(80 * 0.1)
    assert inventory["trade_cargo_lb"]["replacement_value_gp"] is None
    assert inventory["cloth_bolts"]["replacement_value_gp"] is None
    assert inventory["preserved_food_lb"]["replacement_value_gp"] is None
    assert economy["accounts"]["priced_inventory_items"] == 1
    assert economy["accounts"]["unpriced_inventory_items"] == 9
    assert economy["accounts"]["priced_inventory_replacement_value_gp"] == pytest.approx(8)


def test_camp_reuses_host_quotes_and_caches_each_commodity_once(world, monkeypatch):
    world.set_date(HarptosDate(1492, 9, 14))
    calls = []

    def quote(host, cid, *, world):
        calls.append((host, cid))
        return SimpleNamespace(
            price=2.0 * world.commodities[cid].base_price,
            buy_price=world.commodities[cid].base_price,
            availability="abundant", uncommitted_stock=7,
        )

    monkeypatch.setattr("faerun.mobile_economy.price_for", quote)
    report = api_mobile_economy(world, {"id": ["Silver Wheel"]})
    economy = report["economy"]
    assert economy["valuation"]["basis"] == "host_market"
    assert economy["valuation"]["market"]["id"] == "waterdeep"
    assert len(calls) == len(set(calls)) == 14
    assert all(host == "waterdeep" for host, _ in calls)
    assert all(row["uncommitted_stock"] == 7 for row in economy["household_requirements"])
    assert economy["accounts"]["priced_inventory_replacement_value_gp"] == pytest.approx(16)


def test_real_host_prices_and_world_state_are_preserved(world):
    world.set_date(HarptosDate(1492, 9, 14))
    before_price = price_for("waterdeep", "lamp_oil", world=world)
    before_key = world.economy_state_key()
    before_config = copy.deepcopy(world.config)
    before_company = copy.deepcopy(world.find_mobile_location("silver_wheel"))

    report = mobile_economic_report("silver_wheel", world)

    oil = next(row for row in report["economy"]["inventory"]
               if row["commodity_id"] == "lamp_oil")
    assert oil["replacement_value_gp"] == pytest.approx(before_price.price * 80)
    assert price_for("waterdeep", "lamp_oil", world=world) == before_price
    assert world.economy_state_key() == before_key
    assert world.config == before_config
    assert world.find_mobile_location("silver_wheel") == before_company


def test_missing_catalogue_values_and_stores_remain_unknown(world):
    del world.commodities["lamp_oil"]
    company = world.find_mobile_location("silver_wheel")
    stock = dict(company.inventory)
    del stock["preserved_food_lb"]
    stock["fodder_lb"] = 0
    company = replace(company, inventory=stock, animals={})
    economy = mobile_economic_report(company, world)["economy"]
    assert economy["accounts"]["household_cost_complete"] is False
    assert economy["accounts"]["unpriced_household_items"] == 1
    assert economy["accounts"]["priced_inventory_replacement_value_gp"] is None
    supplies = {row["id"]: row for row in economy["supplies"]}
    assert supplies["preserved_food_lb"]["stock"] is None
    assert supplies["preserved_food_lb"]["additional_for_tenday"]["low"] is None
    assert supplies["fodder_lb"]["days_of_cover"] == {"low": None, "high": None}
    assert supplies["fodder_lb"]["additional_for_tenday"] == {"low": 0, "high": 0}
    json.dumps(economy, allow_nan=False)


@pytest.mark.parametrize("quantity", [-1, float("nan"), float("inf"), True, "many"])
def test_invalid_inventory_is_reported_not_silently_valued(world, quantity):
    company = world.find_mobile_location("silver_wheel")
    company = replace(company, inventory={"lamp_oil_flasks": quantity})
    with pytest.raises(ValueError, match="finite nonnegative"):
        mobile_economic_report(company, world)


@pytest.mark.parametrize("params", [{}, {"id": ["unknown company"]}])
def test_report_api_rejects_invalid_company(world, params):
    assert GET_ROUTES["/api/mobile-economy"] is api_mobile_economy
    with pytest.raises(ApiError):
        api_mobile_economy(world, params)
