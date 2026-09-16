from copy import deepcopy
import math

import pytest

from faerun.data.commodities import COMMODITIES, COMMODITIES_BY_ID
from faerun.data.settlements import SETTLEMENTS
from faerun.living import settlement_per_person_daily_requirements
from faerun.models import C, S
from faerun.requirements import (
    DAYS_PER_YEAR,
    FOOD_COMMODITIES,
    SECTORS,
    final_requirements,
    local_resource_capacity,
    resource_assumptions,
    settlement_profile,
)


def village(**kwargs):
    return S("Example", "Test", "test", kwargs.pop("population", 1000), 0, 0, **kwargs)


def total(rows, cid):
    return sum(rows[cid].values())


def output(s, cid):
    return local_resource_capacity(s, COMMODITIES_BY_ID[cid])


def test_zero_population_has_no_people_requirements_or_raw_output():
    s = village(population=0, traits="arcane military frontier", ind="arcane3 farm3")
    p = settlement_profile(s)
    for key in ("population", "mage_population", "standing_army", "militia",
                "builders", "carpenters", "new_homes_per_year", "annual_growth_rate"):
        assert p[key] == 0
    assert all(row["workers"] == row["count"] == 0 for row in p["establishments"])
    assert set(final_requirements(s, COMMODITIES)) == set(COMMODITIES_BY_ID)
    assert all(not sectors for sectors in final_requirements(s, COMMODITIES).values())
    assert all(local_resource_capacity(s, c) == 0 for c in COMMODITIES)


@pytest.mark.parametrize("population", [1, 7, 80, 1000, 130000])
def test_demographic_sectors_are_bounded_and_assumptions_exposed(population):
    s = village(population=population, wealth=1.4, traits="arcane military frontier magocracy",
                ind="arcane3 farm3 fish3 trade3 smith3")
    p = settlement_profile(s)
    assert p["mage_population"] + p["standing_army"] + p["militia"] <= population
    assert sum(row["workers"] for row in p["establishments"]) <= p["worker_population"] <= population
    assert all(isinstance(p[key], int) for key in (
        "mage_population", "standing_army", "militia", "builders", "carpenters"))
    assert 0 <= p["annual_growth_rate"] <= .03
    assert "not canon" in p["provenance"]
    assert p["assumptions"] and p["formula_assumptions"]
    assert all(row["basis"] and row["workers"] >= row["count"] >= 0
               for row in p["establishments"])


def test_all_catalogue_goods_have_nonnegative_finite_sector_flows():
    for s in SETTLEMENTS:
        demand = final_requirements(s, iter(COMMODITIES))
        assert set(demand) == set(COMMODITIES_BY_ID)
        for sectors in demand.values():
            assert set(sectors) <= SECTORS
            assert all(isinstance(v, float) and math.isfinite(v) and v >= 0
                       for v in sectors.values())


def test_rich_diets_include_weight_consistent_exotic_foods_even_outside_food_category():
    poor = final_requirements(village(wealth=.65), COMMODITIES)
    rich = final_requirements(village(wealth=1.4), COMMODITIES)
    for cid in ("coffee", "tea", "chultan_fruit", "spices_exotic", "saffron", "wine_fine"):
        assert total(rich, cid) > total(poor, cid)
        assert "household" in rich[cid]
    heavy = deepcopy(COMMODITIES_BY_ID["chultan_fruit"])
    heavy.weight *= 2
    assert total(final_requirements(village(wealth=1.4), [heavy]), heavy.id) == pytest.approx(
        total(rich, heavy.id) / 2)
    cocoa = C("cocoa", "Cocoa beans", "luxury", 10, "sack", 20, requires="jungle")
    assert total(final_requirements(village(wealth=1.4), [cocoa]), "cocoa") == pytest.approx(
        1000 * .008 / 20)


def test_food_classification_includes_edible_luxury_exotics_and_drinks_only():
    assert isinstance(FOOD_COMMODITIES, frozenset)
    assert {c.id for c in COMMODITIES if c.category in {"food", "drink"}} <= FOOD_COMMODITIES
    assert {"coffee", "tea", "cocoa", "chultan_fruit", "spices_exotic", "saffron",
            "wine_fine", "dwarven_spirits", "elverquisst"} <= FOOD_COMMODITIES
    assert not FOOD_COMMODITIES.intersection({
        "incense", "perfume", "spell_components", "faerzress_crystal",
        "teak", "dinosaur_hide", "whale_oil", "herbs_healing",
    })


def test_diet_diversification_conserves_original_food_family_mass():
    s = village(wealth=1.25, port="Sea")
    core = settlement_per_person_daily_requirements(s)
    rows = final_requirements(s, COMMODITIES)
    for source, family in (
        ("meat_fresh", ("meat_fresh", "fish_fresh", "meat_salt", "fish_salt")),
        ("fruit", ("fruit", "chultan_fruit", "nuts")),
        ("cheese", ("cheese", "butter")),
        ("grain", ("grain", "corn", "rice")),
    ):
        pounds = sum(rows[cid].get("household", 0) * COMMODITIES_BY_ID[cid].weight
                     for cid in family)
        assert pounds == pytest.approx(core[source] * COMMODITIES_BY_ID[source].weight * s.population)


def test_mage_absence_suppresses_arcane_fallback_but_not_explicit_health_needs():
    plain = village(population=10000)
    magical = village(population=10000, traits="arcane magocracy", ind="arcane3")
    custom = C("new_reagent", "New reagent", "arcane", 1, demand=2)
    mundane = final_requirements(plain, [*COMMODITIES, custom])
    arcane = final_requirements(magical, [*COMMODITIES, custom])
    assert settlement_profile(plain)["mage_population"] == 0
    for cid in ("spell_components", "reagents_rare", "arcane_focus", "spellbook_blank",
                "faerzress_crystal", "new_reagent"):
        assert mundane[cid] == {}
        assert arcane[cid]["arcane"] > 0
    assert mundane["herbs_healing"]["health"] > 0
    assert mundane["potion_healing"]["health"] > 0
    assert mundane["holy_water"] == {}
    temple = final_requirements(village(population=10000, traits="temple", ind="temple2"), COMMODITIES)
    assert temple["holy_water"]["religion"] > 0
    legacy = final_requirements(village(population=10000, traits="temple", ind="temple2"),
                                COMMODITIES, include_services=False)
    assert legacy["holy_water"]["civic"] > 0


@pytest.mark.parametrize("context", [
    {"traits": "arcane"}, {"traits": "magocracy"}, {"ind": "arcane1"},
])
@pytest.mark.parametrize("population", [0, 1, 2, 80])
def test_explicit_small_magical_settlements_keep_one_mage_when_workers_allow(context, population):
    s = village(population=population, **context)
    profile = settlement_profile(s)
    expected = 1 if profile["worker_population"] else 0
    assert profile["mage_population"] == expected
    assert profile["mage_population"] <= profile["worker_population"]
    rows = final_requirements(s, COMMODITIES)
    assert bool(rows["spell_components"]) == bool(expected)
    assert bool(rows["reagents_rare"]) == bool(expected)
    assert settlement_profile(village(population=population))["mage_population"] == 0
    assert any("at least one mage" in text for text in profile["assumptions"])


def test_defense_uses_stock_renewal_not_daily_full_re_equipment():
    s = village(population=10000, traits="military frontier")
    p = settlement_profile(s)
    rows = final_requirements(s, COMMODITIES)
    inventory = p["defense_equipment"]["sword"]
    assert inventory["militia_stock"] > 0
    assert inventory["standing_stock"] > 0
    expected = (inventory["annual_replacement"] + inventory["annual_growth_additions"]) / DAYS_PER_YEAR
    assert rows["sword"] == {"defense": pytest.approx(expected)}
    assert expected < (inventory["standing_stock"] + inventory["militia_stock"]) / 1000
    civilian = final_requirements(village(population=10000), COMMODITIES)
    for cid in ("bread", "fish_fresh", "meat_fresh", "eggs"):
        assert rows[cid].get("household") == civilian[cid].get("household")
        assert "defense" not in rows[cid]


def test_growth_needs_additional_builders_and_materials_but_stable_towns_repair():
    stable = village(population=10000, wealth=1.0, traits="stable")
    growing = village(population=10000, wealth=1.4, traits="frontier mercantile")
    a, b = settlement_profile(stable), settlement_profile(growing)
    assert a["annual_growth_rate"] == a["new_homes_per_year"] == 0
    assert b["new_homes_per_year"] == pytest.approx(10000 / 5 * b["annual_growth_rate"])
    assert b["builders"] > a["builders"] > 0
    assert b["carpenters"] > a["carpenters"] > 0
    for cid in ("timber", "planks", "bricks", "nails"):
        assert final_requirements(growing, COMMODITIES)[cid]["construction"] > (
            final_requirements(stable, COMMODITIES)[cid]["construction"]) > 0


def test_waterdeep_has_small_local_farms_and_surplus_fisheries_without_industry_tags():
    waterdeep = next(s for s in SETTLEMENTS if s.id == "waterdeep")
    assert waterdeep.industry_level("farm") == waterdeep.industry_level("fish") == 0
    demand = final_requirements(waterdeep, COMMODITIES)
    assert 0 < output(waterdeep, "grain") < total(demand, "grain")
    assert output(waterdeep, "fish_fresh") > total(demand, "fish_fresh")
    assert output(waterdeep, "vegetables") > 0
    assert output(waterdeep, "eggs") > 0
    assert settlement_profile(waterdeep)["farm_workers"] > 0


def test_small_surveyed_markets_have_farm_surplus_without_declared_industries():
    s = village(population=400, traits="surveyed_market", terrain="plains")
    assert output(s, "grain") > total(final_requirements(s, COMMODITIES), "grain")
    assert output(s, "corn") > 0
    assert "surveyed" in settlement_profile(s)["provenance"]


@pytest.mark.parametrize("terrain", ["desert", "tundra", "cavern"])
def test_harsh_terrain_does_not_invent_normal_crop_forests_or_tropical_output(terrain):
    s = village(terrain=terrain, wealth=2, ind="farm3 orchard3 log3")
    for cid in ("grain", "corn", "vegetables", "fruit", "eggs", "honey",
                "timber", "teak", "coffee", "black_pepper", "chultan_fruit"):
        assert output(s, cid) == 0


def test_irrigated_desert_allows_limited_crops_but_not_forests():
    irrigated = village(terrain="desert", river=True, ind="farm3")
    plains = village(terrain="plains", river=True, ind="farm3")
    assert 0 < output(irrigated, "grain") < output(plains, "grain")
    assert output(irrigated, "rice") > 0
    assert output(irrigated, "timber") == 0


def test_environment_and_requires_gates_override_affluence_and_generic_industries():
    plains = village(wealth=2, terrain="plains", traits="noble mining", ind="smith3")
    hills = village(terrain="hills")
    forest = village(terrain="forest")
    cavern = village(terrain="plains", underdark=True)
    assert output(plains, "iron_ore") == 0
    assert output(hills, "iron_ore") > 0
    assert output(hills, "granite") > 0
    assert output(forest, "timber") > output(plains, "timber") > 0
    assert output(cavern, "grain") == output(cavern, "timber") == 0
    assert output(hills, "mithral_ingot") == output(hills, "adamantine_ingot") == 0
    assert output(village(terrain="mountains", ind="mine_mithral1"), "mithral_ingot") > 0
    for cid in ("coffee", "teak", "chultan_fruit", "black_pepper"):
        assert output(plains, cid) == 0
        assert output(village(terrain="jungle"), cid) > 0
    assert output(village(terrain="hills"), "saffron") == 0


def test_one_land_budget_and_finite_raw_only_production_independent_of_requirements():
    s = village(terrain="hills", ind="farm2 log1")
    r = resource_assumptions(s)
    assert sum(r["land_shares"].values()) == pytest.approx(1.0)
    assert sum(r["land_acres"].values()) == pytest.approx(r["farm_acres"])
    changed = deepcopy(s)
    changed.wealth = 3
    changed.shortages = ["grain", "timber"]
    for c in COMMODITIES:
        capacity = local_resource_capacity(s, c)
        assert math.isfinite(capacity) and capacity >= 0
        assert capacity == local_resource_capacity(changed, c)
        if c.bom:
            assert capacity == 0
    altered = deepcopy(COMMODITIES_BY_ID["grain"])
    altered.demand = 100000
    assert local_resource_capacity(s, altered) == output(s, "grain")
    altered.requires = ["jungle"]
    assert local_resource_capacity(s, altered) == 0


def test_final_uses_exclude_intermediates_but_finished_goods_keep_finite_baseline():
    s = village()
    raw = C("test_raw", "Input", "material", 1, demand=.3)
    finished = C("test_product", "Output", "product", 1, demand=.2)
    finished.bom = {"test_raw": 10000}
    rows = final_requirements(s, [raw, finished])
    assert rows["test_raw"] == {}
    assert rows["test_product"]["household"] == pytest.approx(.2 * 1000 * .002)
    assert final_requirements(s, []) == {}


def test_waterdeep_has_no_unmodeled_final_ore_or_workshop_material_demand():
    waterdeep = next(s for s in SETTLEMENTS if s.id == "waterdeep")
    rows = final_requirements(waterdeep, COMMODITIES)
    legacy = final_requirements(waterdeep, COMMODITIES, include_services=False)
    services = settlement_profile(waterdeep)["service_sectors"]
    for cid in ("iron_ore", "iron_ingot", "steel_ingot", "coal", "leather",
                "wool", "cotton", "gem_agate", "dye_indigo", "wax"):
        assert legacy[cid] == {}
        explicit = {service["id"]: service["planned_per_day"] * service["inputs_per_unit"][cid]
                    for service in services if service["planned_per_day"] > 0
                    and service["inputs_per_unit"].get(cid, 0) > 0}
        assert rows[cid] == pytest.approx(explicit)
    for cid, sector in (
        ("grain", "household"), ("charcoal", "household"), ("timber", "construction"),
        ("planks", "construction"), ("nails", "construction"), ("linen", "health"),
        ("sword", "defense"), ("spellbook_blank", "arcane"),
    ):
        assert rows[cid][sector] > 0


def test_generic_material_without_recipe_has_no_arbitrary_final_consumption():
    goods = [C("new_" + category, "Unmodeled stock", category, 1, demand=10)
             for category in ("material", "metal", "textile", "gem")]
    assert all(not sectors for sectors in final_requirements(village(), goods).values())


def test_recipe_input_detection_is_not_limited_to_material_categories():
    ingredient = C("custom_ingredient", "Ingredient", "exotic", 1, demand=100)
    product = C("custom_product", "Finished good", "product", 1, demand=.2)
    product.bom = {ingredient.id: 500}
    rows = final_requirements(village(), [ingredient, product])
    assert rows[ingredient.id] == {}
    assert rows[product.id]["household"] == pytest.approx(.2 * 1000 * .002)


@pytest.mark.parametrize("weight", [0, -1, float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("cid", ["grain", "sword", "iron_ore"])
def test_invalid_weights_raise_even_for_intermediates_or_manufactured_goods(weight, cid):
    good = deepcopy(COMMODITIES_BY_ID[cid])
    good.weight = weight
    with pytest.raises(ValueError, match="finite|positive"):
        final_requirements(village(), [good])
    with pytest.raises(ValueError, match="finite|positive"):
        local_resource_capacity(village(), good)
    with pytest.raises(ValueError, match="finite|positive"):
        final_requirements(village(population=0), [good])


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_demographics_demand_and_industry_values_raise(value):
    for field in ("wealth", "security"):
        s = village()
        setattr(s, field, value)
        with pytest.raises(ValueError, match="finite"):
            settlement_profile(s)
    s = village()
    s.industries["farm"] = value
    with pytest.raises(ValueError, match="finite"):
        resource_assumptions(s)
    for cid in ("grain", "iron_ore"):
        good = deepcopy(COMMODITIES_BY_ID[cid])
        good.demand = value
        with pytest.raises(ValueError, match="finite"):
            final_requirements(village(), [good])


def test_profile_mutation_does_not_modify_future_assumptions():
    profile = settlement_profile(village())
    profile["formula_assumptions"]["house_materials_lb_per_home_equivalent"]["timber"] = -1
    profile["resource_assumptions"]["land_shares"]["grain"] = -1
    fresh = settlement_profile(village())
    assert fresh["formula_assumptions"]["house_materials_lb_per_home_equivalent"]["timber"] > 0
    assert fresh["resource_assumptions"]["land_shares"]["grain"] > 0


def test_establishment_industries_and_inferred_labor_capacity_are_explicit():
    profile = settlement_profile(village(population=10000))
    catalog_industries = {industry for c in COMMODITIES for industry in c.produced_by}
    for row in profile["establishments"]:
        if "industry" in row:
            assert row["industry"] in catalog_industries
        assert row["count_basis"] == "inferred_labor_capacity"
        assert row["labor_capacity_workdays_per_year"] == row["workers"] * 240
        assert row["count"] == math.ceil(row["workers"] / row["workers_per_establishment"])
        assert "Not real surveyed businesses" in row["basis"]
    rows = {row["id"]: row for row in profile["establishments"]}
    for cid, industry in (("farms", "farm"), ("fisheries", "fish"),
                          ("smiths", "smith"), ("carpenters", "craft")):
        assert rows[cid]["industry"] == industry


@pytest.mark.parametrize("population", [0, 80, 1000, 130000])
def test_service_requirements_have_finite_daily_needs_and_balanced_shortfalls(population):
    profile = settlement_profile(village(population=population))
    assert "independent of selected month" in profile["reference_period"]
    services = profile["service_requirements"]
    assert len(services) == 2
    for row in services:
        assert row["name"] and row["unit"] and row["basis"]
        assert "independent of month" in row["basis"]
        for key in ("required_per_day", "local_capacity_per_day", "unmet_per_day"):
            assert math.isfinite(row[key]) and row[key] >= 0
            if population == 0:
                assert row[key] == 0
        assert row["unmet_per_day"] == pytest.approx(
            max(0, row["required_per_day"] - row["local_capacity_per_day"]))
    from faerun.water import LITRES_PER_GALLON
    assert services[0]["unit"] == "gallon"
    assert services[0]["required_per_day"] == pytest.approx(population * 20 / LITRES_PER_GALLON)
    assert services[1]["required_per_day"] == population * 4


def test_water_and_waste_share_workers_and_ports_do_not_imply_fresh_water():
    from faerun.water import LITRES_PER_GALLON
    dry = settlement_profile(village(terrain="desert"))
    port = settlement_profile(village(terrain="desert", port="Sea"))
    river = settlement_profile(village(terrain="desert", river=True))
    assert dry["sanitation_workers"] == port["sanitation_workers"] == river["sanitation_workers"]
    assert dry["service_requirements"][0]["local_capacity_per_day"] == (
        port["service_requirements"][0]["local_capacity_per_day"])
    assert river["service_requirements"][0]["local_capacity_per_day"] > (
        dry["service_requirements"][0]["local_capacity_per_day"])
    assert dry["service_requirements"][0]["local_capacity_per_day"] == pytest.approx(
        dry["sanitation_workers"] * .6 * 5000 * .3 / LITRES_PER_GALLON)
    assert dry["service_requirements"][1]["local_capacity_per_day"] == pytest.approx(
        dry["sanitation_workers"] * .4 * 2500)
