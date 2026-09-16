import pytest

from faerun.accounts import deliver_services, local_accounts
from faerun.models import C, PriceQuote, S
from faerun.visitors import plan_visitors
from faerun.world import World


def quote(cid, production=0, demand=0, consumption=None, **kwargs):
    q = PriceQuote(
        settlement="Town", commodity=cid, commodity_name=cid, category="test",
        production_type="raw", unit="unit", base_price=1, price=1, buy_price=.8,
        multiplier=1, availability="common", stock=0, supply_index=1, demand_index=1,
        production_per_day=production, demand_per_day=demand, scarcity=1,
        final_demand_per_day=demand, final_consumption_per_day=consumption if consumption is not None else demand,
        **kwargs,
    )
    return q


def service(**kwargs):
    return {
        "id": "health", "name": "Health", "unit": "case", "workers": 2,
        "establishments": 1, "resident_demand_per_day": 10, "visitor_demand_per_day": 0,
        "demand_per_day": 10, "capacity_per_day": 10, "planned_per_day": 10,
        "fee_gp_per_unit": 5, "market_service": True, "visitor_units_per_person_day": .1,
        "inputs_per_unit": {"herbs": 1, "linen": 1}, **kwargs,
    }


def test_service_bottlenecks_release_unused_inputs_and_preserve_households():
    w = World(settlements=[S("Town", "Test", "test", 100, 0, 0)],
              commodities=[C("herbs", "Herbs", "test", 1), C("linen", "Linen", "test", 3)])
    markets = {
        "herbs": {"town": quote("herbs", 15, 15, demand_sectors={"household": 5, "health": 10})},
        "linen": {"town": quote("linen", 2, 10, consumption=2, demand_sectors={"health": 10})},
    }
    delivered = deliver_services(w, markets, {"town": [service()]})["town"][0]
    assert delivered["delivered_per_day"] == 2
    assert delivered["unmet_per_day"] == 8
    herbs = markets["herbs"]["town"]
    assert herbs.consumption_sectors == {"household": 5, "health": 2}
    assert herbs.final_consumption_per_day == 7
    assert herbs.material_closing_stock == 8
    assert herbs.production_per_day == herbs.final_consumption_per_day + herbs.material_closing_stock
    assert all(row["consumed_per_day"] <= row["reserved_per_day"] for row in delivered["inputs"])


def test_service_reporting_does_not_release_inventory_inputs_a_second_time():
    from copy import deepcopy

    world = World(settlements=[S("Town", "Test", "test", 100, 0, 0)],
                  commodities=[C("herbs", "Herbs", "test", 1), C("linen", "Linen", "test", 3)])
    markets = {
        cid: {"town": quote(
            cid, consumption=0, demand=10,
            consumption_sectors={"health": 3.469446951953614e-18 if cid == "linen" else 0},
            inventory={"enabled": True, "closing_stock": 0.25}, material_closing_stock=0.25,
        )}
        for cid in ("herbs", "linen")
    }
    before = {cid: deepcopy(places["town"].__dict__) for cid, places in markets.items()}
    report = deliver_services(world, markets, {"town": [service()]})
    assert report["town"][0]["delivered_per_day"] == 0
    for cid, places in markets.items():
        assert places["town"].__dict__ == before[cid]


def test_glp_subtracts_each_intermediate_once():
    a, b = C("a", "Raw", "test", 2), C("b", "Finished", "test", 5)
    b.bom = {"a": 1}
    w = World(settlements=[S("Town", "Test", "test", 100, 0, 0)], commodities=[a, b])
    w.config.visitor_economy = False
    markets = {
        "a": {"town": quote("a", 10, 6, demand_sectors={"household": 6})},
        "b": {"town": quote("b", 4, 4, demand_sectors={"household": 2, "health": 2},
                           production_inputs=[{"commodity": "a", "consumed_per_day": 4}])},
    }
    plans = {"town": [service(planned_per_day=2, demand_per_day=2, resident_demand_per_day=2,
                              fee_gp_per_unit=10, inputs_per_unit={"b": 1})]}
    industries = deliver_services(w, markets, plans)
    account = local_accounts(w, markets, industries, plan_visitors(w, {}))["town"]["accounts"]
    assert account["goods_output_gp_per_day"] == 40
    assert account["goods_intermediate_gp_per_day"] == 8
    assert account["service_output_gp_per_day"] == 20
    assert account["service_intermediate_gp_per_day"] == 10
    assert account["gross_local_product_gp_per_day"] == 42
    assert account["gross_local_product_gp_per_year"] == 42 * 365
    assert account["glp_per_resident_gp_per_year"] == 42 * 365 / 100


def test_goods_trade_books_the_same_gate_price_not_landed_cost():
    w = World(settlements=[S("Mine", "Test", "test", 100, 0, 0),
                           S("Town", "Test", "test", 100, 30, 0)],
              commodities=[C("ore", "Ore", "test", 2)])
    w.config.visitor_economy = False
    markets = {"ore": {
        "mine": quote("ore", 10),
        "town": quote("ore", 0, 4, demand_sectors={"household": 4}, sources=[{
            "source_id": "mine", "supply_type": "import", "quantity_per_day": 4,
            "producer_unit_cost": 3, "unit_cost": 7,
        }]),
    }}
    sectors = deliver_services(w, markets, {"mine": [], "town": []})
    result = local_accounts(w, markets, sectors, plan_visitors(w, {}))
    assert result["mine"]["accounts"]["goods_exports_gp_per_day"] == 12
    assert result["town"]["accounts"]["goods_imports_gp_per_day"] == 12
    assert result["town"]["accounts"]["unassigned_inbound_freight_gp_per_day"] == 16
    assert sum(r["accounts"]["goods_trade_balance_gp_per_day"] for r in result.values()) == 0


def test_visitor_receipts_are_a_matched_transfer_not_added_to_glp():
    w = World(settlements=[S("Home", "Test", "test", 100, 0, 0),
                           S("Host", "Test", "test", 100, 30, 0)],
              commodities=[C("bread", "Bread", "food", 2)])
    w.config.visitor_economy = False
    travel = plan_visitors(w, {})
    travel["places"]["host"].update({"visitor_goods": {"bread": 2},
                                     "visitors_per_day": 2, "overnight_visitors_per_day": 2})
    travel["flows"] = [{
        "origin_id": "home", "destination_id": "host", "segment_id": "leisure",
        "segment": "Leisure", "overnight": True, "average_nights": 3,
        "visitors_per_day": 2, "arrivals_per_month": 20, "goods_demand": {"bread": 2},
    }]
    markets = {"bread": {
        "home": quote("bread"),
        "host": quote("bread", 4, 4, demand_sectors={"household": 2, "visitors": 2}),
    }}
    sectors = deliver_services(w, markets, {"home": [], "host": []})
    result = local_accounts(w, markets, sectors, travel)
    host, home = result["host"]["accounts"], result["home"]["accounts"]
    assert host["visitor_receipts_gp_per_day"] == home["resident_travel_spending_gp_per_day"] == 2
    assert host["gross_local_product_gp_per_day"] == 8
    assert sum(r["accounts"]["net_visitor_receipts_gp_per_day"] for r in result.values()) == 0
    assert sum(r["accounts"]["external_balance_gp_per_day"] for r in result.values()) == 0


def test_capital_purchases_are_not_deducted_from_gross_value_added():
    w = World(settlements=[S("Town", "Test", "test", 100, 0, 0)],
              commodities=[C("cart", "Cart", "product", 10)])
    w.config.visitor_economy = False
    markets = {"cart": {"town": quote("cart", 1, 1, demand_sectors={"health": 1})}}
    industries = deliver_services(w, markets, {
        "town": [service(planned_per_day=1, demand_per_day=1, inputs_per_unit={"cart": 1},
                          fee_gp_per_unit=20)]
    })
    account = local_accounts(w, markets, industries, plan_visitors(w, {}))["town"]["accounts"]
    assert account["service_capital_purchases_gp_per_day"] == 10
    assert account["service_intermediate_gp_per_day"] == 0
    assert account["gross_local_product_gp_per_day"] == 30


def test_hospitality_charges_lodging_only_to_overnight_guests():
    w = World(settlements=[S("Home", "Test", "test", 100, 0, 0),
                           S("Host", "Test", "test", 100, 30, 0)],
              commodities=[C("bread", "Bread", "food", 1)])
    w.config.visitor_economy = False
    travel = plan_visitors(w, {})
    travel["places"]["host"].update({"visitors_per_day": 4, "overnight_visitors_per_day": 2})
    travel["flows"] = [{
        "origin_id": "home", "destination_id": "host", "segment_id": "leisure",
        "segment": "Leisure", "overnight": overnight, "average_nights": 3 if overnight else 0,
        "visitors_per_day": 2, "arrivals_per_month": 20 if overnight else 60,
        "goods_demand": {},
    } for overnight in (True, False)]
    markets = {"bread": {"home": quote("bread"), "host": quote("bread")}}
    plans = {"home": [], "host": [service(
        id="hospitality", planned_per_day=4.4, demand_per_day=4.4,
        resident_demand_per_day=2, visitor_demand_per_day=2.4,
        visitor_units_per_person_day=.1, fee_gp_per_unit=2, inputs_per_unit={},
    )]}
    industries = deliver_services(w, markets, plans)
    result = local_accounts(w, markets, industries, travel)
    assert result["host"]["accounts"]["visitor_receipts_gp_per_day"] == pytest.approx(4.8)
    assert result["home"]["accounts"]["resident_travel_spending_gp_per_day"] == pytest.approx(4.8)


def test_nonmarket_service_value_is_not_tourist_cash():
    w = World(settlements=[S("Town", "Test", "test", 100, 0, 0)],
              commodities=[C("bread", "Bread", "food", 1)])
    w.config.visitor_economy = False
    markets = {"bread": {"town": quote("bread")}}
    industries = deliver_services(w, markets, {"town": [service(inputs_per_unit={}, market_service=False)]})
    account = local_accounts(w, markets, industries, plan_visitors(w, {}))["town"]["accounts"]
    assert account["service_output_gp_per_day"] == 50
    assert account["visitor_receipts_gp_per_day"] == 0
