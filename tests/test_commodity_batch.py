"""Bounded commodity catalogue and material-flow regressions."""

import pytest

from faerun.calendar import HarptosDate
from faerun.data.commodities import COMMODITIES_BY_ID
from faerun.data.settlements import SETTLEMENTS_BY_ID
from faerun.data_store import load_commodities
from faerun.economy import supply_index
from faerun.materials import _baseline_plan, _recipe_order
from faerun.requirements import final_requirements
from faerun.seasonality import demand_multiplier, production_multiplier
from faerun.world import World


BATCH = ("barley", "grapes", "goats", "merchant_cog", "jewelry", "musical_instrument")


def test_batch_is_persisted_with_real_ingredients_and_distinct_existing_ships():
    stored = {c.id: c for c in load_commodities()}
    for cid in BATCH:
        assert cid in stored
        assert stored[cid].base_price == COMMODITIES_BY_ID[cid].base_price
    assert "cider" not in stored
    assert stored["ale"].bom == COMMODITIES_BY_ID["ale"].bom == {"barley": .8}
    assert stored["wine_common"].bom == COMMODITIES_BY_ID["wine_common"].bom == {"grapes": 6}
    assert stored["trade_galleon"].produced_by == ["tag_trade_galleon"]
    assert stored["merchant_cog"].produced_by == ["ship"]
    assert stored["merchant_cog"].base_price == 5000
    assert stored["merchant_cog"].bom == COMMODITIES_BY_ID["merchant_cog"].bom
    assert set(stored["merchant_cog"].bom) == {"planks", "nails", "rope", "sailcloth", "pitch"}
    assert stored["jewelry"].bom == {"silver_ingot": .1, "gem_agate": 1}
    assert stored["musical_instrument"].bom == {"planks": .03, "rope": .1}
    _recipe_order(stored)


def test_raw_harvests_and_workshops_have_different_seasonality():
    world = World()
    temperate = SETTLEMENTS_BY_ID["goldenfields"]
    for cid in ("barley", "grapes"):
        c = world.commodities[cid]
        assert production_multiplier(c, temperate, HarptosDate(1492, 1, 1)) == 0
        assert production_multiplier(c, temperate, HarptosDate(1492, 9, 1)) > 0
        assert c.storage_days > 0
        assert demand_multiplier(c, HarptosDate(1492, 1, 1)) == 1
    for cid in ("ale", "wine_common", "merchant_cog", "jewelry", "musical_instrument"):
        c = world.commodities[cid]
        assert c.production_profile == []
        assert production_multiplier(c, temperate, HarptosDate(1492, 1, 1)) == 1
    assert COMMODITIES_BY_ID["goats"].storage_days == 0


def test_producers_and_explicit_port_ship_orders():
    world = World()
    orlumbor = SETTLEMENTS_BY_ID["orlumbor"]
    goldenfields = SETTLEMENTS_BY_ID["goldenfields"]
    phandalin = SETTLEMENTS_BY_ID["phandalin"]
    assert supply_index(world, orlumbor, world.commodities["merchant_cog"]) > 0
    assert supply_index(world, orlumbor, world.commodities["goats"]) > 0
    assert supply_index(world, goldenfields, world.commodities["barley"]) > 0
    assert supply_index(world, phandalin, world.commodities["merchant_cog"]) == 0
    assert final_requirements(phandalin, world.commodities.values())["merchant_cog"] == {}
    assert 0 < final_requirements(orlumbor, world.commodities.values())["merchant_cog"]["logistics"] < .01
    assert final_requirements(orlumbor, world.commodities.values())["trade_galleon"] == {}
    assert final_requirements(orlumbor, world.commodities.values())["goats"] == {
        "agriculture": pytest.approx(10 / 365)
    }
    assert final_requirements(phandalin, world.commodities.values())["goats"] == {}
    waterdeep = SETTLEMENTS_BY_ID["waterdeep"]
    waterdeep_orders = final_requirements(waterdeep, world.commodities.values())
    assert waterdeep_orders["jewelry"]["household"] > 0
    assert waterdeep_orders["musical_instrument"]["culture"] > 0
    assert waterdeep_orders["jewelry"]["household"] < 2
    assert waterdeep_orders["musical_instrument"]["culture"] < 1


def test_batch_planning_consumes_ingredients_only_for_scheduled_output():
    world = World()
    plan = _baseline_plan(world)
    ship_orders = sum(sum(parts.values()) for goods in plan["sectors"].values()
                      for cid, parts in goods.items() if cid == "merchant_cog")
    assert 0 < ship_orders < 1
    assert sum(plan["capacity"]["merchant_cog"].values()) == pytest.approx(ship_orders)
    assert plan["capacity"]["merchant_cog"]["orlumbor"] > 0
    assert plan["capacity"]["goats"]["orlumbor"] > 0
    assert plan["capacity"]["grapes"]["hlondeth"] > 0
    wine = sum(plan["capacity"]["wine_common"].values())
    grapes = sum(plan["capacity"]["grapes"].values())
    assert wine > 0
    assert grapes >= wine * world.commodities["wine_common"].bom["grapes"]
    assert world.commodities["grapes"].base_price * 6 < world.commodities["wine_common"].base_price
    for cid in BATCH:
        assert cid in plan["capacity"]
