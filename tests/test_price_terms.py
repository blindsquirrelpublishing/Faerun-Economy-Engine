from dataclasses import asdict

import pytest

from faerun.economy import _apply_quantity, _commodity_markets, _quality_offers, find_arbitrage, price_for
from faerun.models import Business, C, PriceQuote, S, price_terms
from faerun.web import api_businesses
from faerun.world import World


def sample_quote(**values):
    fields = dict(
        settlement="Town", commodity="widget", commodity_name="Widget", category="product",
        production_type="raw", unit="item", base_price=10.0, price=10.0, buy_price=8.0,
        multiplier=1, availability="common", stock=100, supply_index=1, demand_index=1,
        production_per_day=12, demand_per_day=8, exports_per_day=2, scarcity=1,
        stock_horizon_days=10,
    )
    fields.update(values)
    q = PriceQuote(**fields)
    q.quality_offers = _quality_offers(q.price, q.buy_price, q.stock, 3)
    return q


def test_buy_sell_markup_and_margin_have_distinct_denominators():
    data = sample_quote().to_dict()
    assert data["consumer_buy_price"] == data["price"] == 10
    assert data["consumer_sell_price"] == data["buy_price"] == 8
    assert data["merchant_spread"] == 2
    assert data["merchant_markup_pct"] == 25
    assert data["merchant_margin_pct"] == 20


def test_uncommitted_supply_protects_processing_and_allocated_exports():
    q = sample_quote(production_per_day=100, imports_per_day=20, exports_per_day=30,
                     demand_per_day=70, stock=700)
    assert q.uncommitted_supply_per_day == 20
    assert q.uncommitted_stock == 200
    reserved = sample_quote(production_per_day=100, demand_per_day=100, exports_per_day=0,
                            final_demand_per_day=20, processing_demand_per_day=80,
                            processing_consumption_per_day=0, material_closing_stock=80, stock=1000)
    assert reserved.material_closing_stock == 80
    assert reserved.uncommitted_supply_per_day == 0
    assert reserved.uncommitted_stock == 0


def test_stock_horizon_is_floored_and_capped_not_rounded_up():
    q = sample_quote(production_per_day=8.29, exports_per_day=0, stock_horizon_days=3)
    assert q.uncommitted_stock == 0
    q.production_per_day = 8.4
    assert q.uncommitted_stock == 1
    q.production_per_day = 100000
    assert q.uncommitted_stock == q.stock
    q.demand_per_day = 200000
    assert q.uncommitted_stock == 0


def test_grades_partition_one_free_pool_without_double_promising():
    q = sample_quote()
    data = q.to_dict()
    assert data["uncommitted_stock"] == 20
    assert sum(o["uncommitted_stock"] for o in data["quality_offers"]) == 20
    for offer in data["quality_offers"]:
        assert 0 <= offer["uncommitted_stock"] <= offer["stock"]
        assert offer["consumer_buy_price"] == offer["price"]
        assert offer["consumer_sell_price"] == offer["buy_price"]
        assert offer["merchant_markup_pct"] == pytest.approx(25)
    fine = next(o for o in data["quality_offers"] if o["quality"] == "fine")
    selected = PriceQuote(**dict(asdict(q), quality="fine", stock_scope="fine",
                                 stock=fine["stock"], price=fine["price"], buy_price=fine["buy_price"]))
    assert selected.uncommitted_stock == fine["uncommitted_stock"]


def test_quantity_quotes_recompute_terms_without_mutating_the_base():
    q = sample_quote()
    before = q.to_dict()
    bulk = _apply_quantity(q, 50)
    data = bulk.to_dict()
    assert data["consumer_buy_price"] > before["consumer_buy_price"]
    assert data["consumer_sell_price"] < before["consumer_sell_price"]
    assert data["merchant_markup_pct"] == pytest.approx(
        (data["price"] / data["buy_price"] - 1) * 100)
    assert data["uncommitted_stock"] == before["uncommitted_stock"]
    assert any("exceeds the uncommitted stock estimate" in note for note in data["notes"])
    assert q.to_dict() == before


@pytest.mark.parametrize("ask,bid", [(8, 10), (-1, 0), (1, -1), (float("nan"), 1), (True, 0)])
def test_invalid_price_pairs_are_not_silently_accepted(ask, bid):
    with pytest.raises(ValueError):
        price_terms(ask, bid)


def test_zero_bid_has_no_fabricated_markup_percentage():
    assert price_terms(10, 0)["merchant_markup_pct"] is None
    assert price_terms(10, 0)["merchant_margin_pct"] == 100
    assert price_terms(0, 0)["merchant_margin_pct"] is None


def tiny_world():
    return World(
        settlements=[S("Town", "Test", "test", 1000, 0, 0, ind="craft3 smith3", spec="widget3")],
        commodities=[C("widget", "Widget", "product", 10, produced_by="craft")],
        businesses=[
            Business("a", "Trader A", "town", ["town"], [], {"widget": "masterwork"}, .8),
            Business("b", "Trader B", "town", ["town"], [], {"widget": "masterwork"}, 1.2),
        ],
    )


def test_quality_quantity_and_named_merchants_expose_correct_prices_and_stock():
    w = tiny_world()
    q = price_for("Town", "widget", world=w, quality="fine", quantity=10).to_dict()
    assert q["stock_scope"] == "fine"
    assert q["consumer_buy_price"] == q["price"] > q["buy_price"] == q["consumer_sell_price"]
    base = price_for("Town", "widget", world=w).to_dict()
    grades = {o["quality"]: o for o in base["quality_offers"]}
    businesses = api_businesses(w, {"settlement": ["Town"]})["businesses"]
    for business in businesses:
        for offer in business["offers"]:
            assert offer["price"] == round(grades[offer["quality"]]["price"] * business["price_modifier"], 3)
            assert offer["buy_price"] == round(grades[offer["quality"]]["buy_price"] * business["price_modifier"], 3)
            assert offer["merchant_markup_pct"] == pytest.approx((offer["price"] / offer["buy_price"] - 1) * 100)
            assert offer["uncommitted_stock"] <= offer["stock"]
    for grade in grades:
        allocated = sum(o["uncommitted_stock"] for b in businesses for o in b["offers"] if o["quality"] == grade)
        assert allocated <= grades[grade]["uncommitted_stock"]


def test_spread_configuration_rejects_negative_or_unbounded_bids():
    w = tiny_world()
    w.config.spread_max = 1
    with pytest.raises(ValueError, match="spread bounds"):
        price_for("Town", "widget", world=w)


def test_all_market_quotes_preserve_required_demand_and_resale_markup():
    world = World()
    for c in world.commodities.values():
        for q in _commodity_markets(world, c).values():
            data = q.to_dict()
            assert data["consumer_buy_price"] > data["consumer_sell_price"] >= 0
            assert data["merchant_markup_pct"] > 0
            assert data["uncommitted_supply_per_day"] == pytest.approx(
                max(0, q.production_per_day + q.imports_per_day - q.exports_per_day - q.demand_per_day))
            assert data["uncommitted_stock"] <= q.uncommitted_supply_per_day * q.stock_horizon_days + 1e-8
            assert data["uncommitted_stock"] <= q.stock
            assert sum(o["uncommitted_stock"] for o in data["quality_offers"]) == data["uncommitted_stock"]


def test_arbitrage_only_recommends_uncommitted_units_and_respects_weight(monkeypatch):
    import faerun.economy as economy

    w = World(settlements=[S("Origin", "Test", "test", 100, 0, 0),
                           S("Buyer", "Test", "test", 100, 10, 0)],
              commodities=[C("widget", "Widget", "product", 1, weight=2)])
    source = sample_quote(price=1, buy_price=.8, production_per_day=10, demand_per_day=9,
                          exports_per_day=0, stock_horizon_days=3)
    buyer = sample_quote(price=4, buy_price=3)
    monkeypatch.setattr(economy, "_commodity_markets", lambda *a, **k: {"origin": source, "buyer": buyer})
    monkeypatch.setattr(economy, "_freight_map", lambda *a: {"buyer": 0})
    monkeypatch.setattr(economy, "_days_map", lambda *a: {"buyer": 1})
    result = find_arbitrage("Origin", world=w, cargo_pounds=100)
    assert result["deals"][0]["units_per_load"] == 3
    assert result["deals"][0]["sell_at_destination"] == 3
    assert not find_arbitrage("Origin", world=w, cargo_pounds=1)["deals"]
    source.demand_per_day = 10
    assert not find_arbitrage("Origin", world=w, cargo_pounds=100)["deals"]


@pytest.mark.parametrize("arguments", [
    ["market", "Town"], ["price", "Town", "widget", "--quantity", "2"],
    ["compare", "widget"], ["trade", "Town"],
], ids=["market", "price", "compare", "trade"])
def test_cli_price_views_show_both_directions_and_uncommitted_stock(arguments, monkeypatch, capsys):
    from faerun import cli

    world = tiny_world()
    monkeypatch.setattr(cli, "build_world", lambda args: world)
    assert cli.main(arguments) == 0
    text = capsys.readouterr().out.lower()
    assert "buy from merchant" in text
    assert "sell to merchant" in text
    assert "uncommitted" in text


def test_history_records_both_prices_and_respects_its_stock_window():
    from faerun.economy import price_history

    world = tiny_world()
    date = world.date
    history = price_history("Town", "widget", world=world, months=2)
    assert world.date == date
    for row in history["series"]:
        assert row["consumer_buy_price"] == row["price"]
        assert row["consumer_sell_price"] == row["buy_price"]
        assert row["merchant_markup_pct"] == pytest.approx((row["price"] / row["buy_price"] - 1) * 100)
        assert row["uncommitted_stock"] <= row["uncommitted_supply_per_day"] * row["stock_horizon_days"] + 1e-9
