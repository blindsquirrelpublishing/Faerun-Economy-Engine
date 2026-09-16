"""Isolated HTTP and public-availability checks for merchant-guild POs."""

import json
from http.server import ThreadingHTTPServer
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from faerun import web
from faerun.calendar import HarptosDate
from faerun.economy import _commodity_markets, compare_prices, market_report, price_for, price_history
from faerun.location import location_detail
from faerun.models import Business, C, S
from faerun.orders import TradeStore
from faerun.world import EconomyConfig, World


@pytest.fixture
def world(tmp_path, monkeypatch):
    from faerun import economy, materials
    monkeypatch.setattr(economy, "settlement_daily_requirements",
                        lambda *args, **kwargs: {"living_standard": "test", "requirements": []})
    monkeypatch.setattr(materials, "economic_report", lambda *args, **kwargs: {"accounts": {}})
    return World(
        settlements=[S("Town", "Test", "test", 1000, 0, 0, ind="craft5", spec="widget5")],
        commodities=[C("widget", "Widget", "product", 10, produced_by="craft")],
        businesses=[Business("trader", "Guild shop", "town", ["town"], [], {"widget": "masterwork"}, 1)],
        date=HarptosDate(1492, 6, 11), config=EconomyConfig(expanded_requirements=False, noise=0),
        trade_store=TradeStore(tmp_path / "http-ledger.sqlite3"),
    )


def parameters():
    return dict(origin="town", destination="town", commodity="widget", quantity=12,
                quality="standard", acceptance_terms="Inspect quantity and grade", deposit_percent=50)


@pytest.fixture
def http(world, monkeypatch):
    monkeypatch.setattr(web, "get_world", lambda: world)
    server = ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    address = f"http://127.0.0.1:{server.server_port}"

    def request(path, body=None, headers=None, raw=None):
        data = raw if raw is not None else json.dumps(body).encode() if body is not None else None
        request_headers = {"Content-Type": "application/json"} if data is not None else {}
        request_headers.update(headers or {})
        req = Request(address + path, data=data, headers=request_headers)
        try:
            with urlopen(req, timeout=10) as response:
                return response.status, json.loads(response.read())
        except HTTPError as exc:
            with exc:
                return exc.code, json.loads(exc.read())

    try:
        yield request, address
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        assert not thread.is_alive()


def reserve(world):
    quote = world.trade_store.quote(world, parameters())
    return world.trade_store.reserve(world, quote_id=quote["id"], customer_name="Test customer",
                                    po_reference="PO-1", terms_accepted=True)


def test_quote_reserve_read_and_cash_round_trip(http, world):
    request, address = http
    status, data = request("/api/trade/options")
    assert status == 200 and data["enabled"]
    assert data["date"]["iso"] == "1492-06-11"
    status, data = request("/api/trade/quote", parameters(), {"Origin": address})
    assert status == 200
    quote = data["quote"]
    assert not any(key.startswith("_") for key in quote)
    assert quote["reservable"] and quote["pickup_date"] == "1492-06-20"
    status, data = request("/api/trade/order", dict(
        quote_id=quote["id"], customer_name="Test customer", po_reference="HTTP-1", terms_accepted=True))
    assert status == 200 and data["order"]["status"] == "reserved"
    order = data["order"]
    status, data = request("/api/trade/order?id=" + order["id"])
    assert status == 200 and data["order"]["quote"]["amounts"] == quote["amounts"]
    status, data = request("/api/trade/payment", dict(
        order_id=order["id"], kind="customer_payment",
        amount_gp=quote["amounts"]["customer_deposit_due_gp"], reference="Receipt-1"))
    assert status == 200 and data["order"]["balance"]["deposit_remaining_gp"] == 0
    assert not data["order"]["balance"]["can_dispatch"]
    assert request("/api/trade/orders?limit=1")[1]["total"] == 1
    assert TradeStore(world.trade_store.path).list_orders(world)["orders"][0]["id"] == order["id"]


@pytest.mark.parametrize("headers,raw,expected", [
    ({"Origin": "https://foreign.invalid"}, b"{}", 403),
    ({"Origin": "null"}, b"{}", 403),
    ({"Host": "foreign.invalid"}, b"{}", 403),
    ({"Content-Type": "text/plain"}, b"{}", 415),
    ({"Content-Length": "70000"}, b"{}", 413),
    ({}, b"[1,2]", 400),
    ({}, b"{bad json", 400),
    ({}, b"\xff", 400),
])
def test_mutations_reject_foreign_or_malformed_requests(http, headers, raw, expected):
    request, _ = http
    status, response = request("/api/trade/quote", raw=raw, headers=headers)
    assert status == expected
    assert "error" in response


def test_missing_fields_and_untrusted_totals_are_rejected(http):
    request, _ = http
    assert request("/api/trade/order", {"customer_name": "Test"})[0] == 400
    assert request("/api/trade/quote", {**parameters(), "supplier_total_gp": 1})[0] == 400
    assert request("/api/trade/payment", {})[0] == 400
    assert request("/api/trade/orders?limit=NaN")[0] == 400
    assert request("/api/trade/order?id=missing")[0] == 404
    assert request("/api/trade/options", headers={"Origin": "https://foreign.invalid"})[0] == 403


def test_reservations_update_all_public_quotes_without_changing_model(world):
    raw = _commodity_markets(world, world.commodities["widget"])["town"]
    physical_before = raw.to_dict()
    before = price_for("town", "widget", world).to_dict()
    order = reserve(world)
    after = price_for("town", "widget", world).to_dict()
    assert raw.to_dict() == physical_before
    assert after["uncommitted_stock"] == before["uncommitted_stock"] - 12
    assert after["forecast_uncommitted_stock"] == before["forecast_uncommitted_stock"]
    assert after["order_claimed_stock"] == 12
    assert after["order_supply_window"]["start"] == "1492-06-11"
    assert market_report("town", world)["prices"][0]["uncommitted_stock"] == after["uncommitted_stock"]
    assert compare_prices("widget", world)["markets"][0]["uncommitted_stock"] == after["uncommitted_stock"]
    assert price_history("town", "widget", world, months=1)["series"][0]["uncommitted_stock"] == after["uncommitted_stock"]
    grades = {row["quality"]: row for row in after["quality_offers"]}
    assert sum(row["uncommitted_stock"] for row in grades.values()) == after["uncommitted_stock"]
    for row in web.api_businesses(world, {"settlement": ["town"]})["businesses"][0]["offers"]:
        assert row["uncommitted_stock"] <= grades[row["quality"]]["uncommitted_stock"]
    world.trade_store.transition(world, order_id=order["id"], action="cancel", version=order["version"])
    assert price_for("town", "widget", world).uncommitted_stock == before["uncommitted_stock"]


def test_carried_stock_http_and_public_views_keep_claims_across_windows(http, world, monkeypatch):
    from faerun import economy, seasonal_economy

    raw = _commodity_markets(world, world.commodities["widget"])["town"]
    raw.production_per_day = raw.imports_per_day = raw.exports_per_day = 0
    raw.stock = 200
    raw.stock_horizon_days = 1
    raw.inventory = {
        "enabled": True, "uncommitted_stock": 200, "closing_stock": 200,
        "opening_stock": 200 + raw.demand_per_day, "spoilage": 0, "reserve_target": 0,
    }
    for offer in raw.quality_offers:
        offer["stock"] = 200 if offer["quality"] == "standard" else 0
    physical = raw.to_dict()
    monkeypatch.setattr(economy, "_commodity_markets", lambda *args, **kwargs: {"town": raw})
    monkeypatch.setattr(seasonal_economy, "inventory_window", lambda origin, cid, start, end, **kwargs: {
        "snapshots": [{"production": 0, "exports": 0, "exports_by_destination": {}}
                      for _ in range(end.absolute_day() - start.absolute_day() + 1)],
    })
    request, _ = http
    status, result = request("/api/trade/quote", parameters())
    assert status == 200
    assert result["quote"]["supply"]["available_units"] == 200
    assert result["quote"]["supply"]["claim_scope"] == "carried_inventory"
    status, result = request("/api/trade/order", {
        "quote_id": result["quote"]["id"], "customer_name": "Winter customer",
        "po_reference": "WINTER-1", "terms_accepted": True,
    })
    assert status == 200
    world.date = HarptosDate(1492, 6, 21)
    world.trade_store = TradeStore(world.trade_store.path)
    status, later = request("/api/trade/quote", parameters())
    assert status == 200
    assert later["quote"]["supply"]["available_units"] == 188
    assert price_for("town", "widget", world).uncommitted_stock == 188
    assert market_report("town", world)["prices"][0]["uncommitted_stock"] == 188
    assert compare_prices("widget", world)["markets"][0]["uncommitted_stock"] == 188
    assert raw.to_dict() == physical


def test_location_cache_uses_current_day_and_trade_revision(world, monkeypatch):
    from faerun import materials
    monkeypatch.setattr(materials, "location_requirements", lambda *args, **kwargs: {})
    before = location_detail("town", world)
    assert before["date"].startswith("11 ")
    model_revision = world.revision
    cache = getattr(world, "_price_cache", None)
    reserve(world)
    after = location_detail("town", world)
    assert before is not after
    assert after["market"]["prices"][0]["uncommitted_stock"] == before["market"]["prices"][0]["uncommitted_stock"] - 12
    assert world.revision == model_revision and getattr(world, "_price_cache", None) is cache
    assert world.date == HarptosDate(1492, 6, 11)
