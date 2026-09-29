"""Market board: customer-posted commodity requests other parties can bid on."""

import pytest

from faerun.calendar import HarptosDate
from faerun.models import C, S
from faerun.orders import TradeStore
from faerun.trading import TradeError
from faerun.world import EconomyConfig, World


def make_world(store, *, date=HarptosDate(1492, 6, 11)):
    return World(
        settlements=[S("Source", "Test", "test", 100, 0, 0, tax=.05),
                     S("Buyer", "Test", "test", 100, 1, 0, tax=.10)],
        commodities=[C("wine", "Wine", "drink", 3, unit="bottle", weight=2, produced_by="vint")],
        businesses=[], date=date,
        config=EconomyConfig(noise=0, expanded_requirements=False, seasonal_inventory=False),
        trade_store=store,
    )


@pytest.fixture
def board(tmp_path):
    store = TradeStore(tmp_path / "ledger.sqlite3")
    return store, make_world(store)


def post(store, world, **changes):
    fields = dict(
        requester_name="Innkeeper Mira", commodity="wine", quantity=100, quality="standard",
        settlement_id="source", needed_by="1492-07-01", notes="Needed for a festival.",
    )
    fields.update(changes)
    return store.post_request(world, **fields)


def test_post_request_creates_open_request_with_no_bids(board):
    store, world = board
    request = post(store, world)
    assert request["status"] == "open"
    assert request["bids"] == []
    assert request["version"] == 1
    assert request["max_price_gp"] is None


def test_post_request_rejects_unknown_commodity_settlement_and_quality(board):
    store, world = board
    with pytest.raises(TradeError):
        post(store, world, commodity="unobtainium")
    with pytest.raises(TradeError):
        post(store, world, settlement_id="nowhere")
    with pytest.raises(TradeError):
        post(store, world, quality="legendary")


def test_post_request_rejects_past_needed_by_date(board):
    store, world = board
    with pytest.raises(TradeError):
        post(store, world, needed_by="1492-01-01")


def test_bid_and_accept_closes_request_and_rejects_other_bids(board):
    store, world = board
    request = post(store, world)
    request = store.bid(world, request_id=request["id"], bidder_name="Caravan Co",
                        price_gp=5, quantity=100, delivery_by="1492-06-25")
    request = store.bid(world, request_id=request["id"], bidder_name="River Traders",
                        price_gp=4.5, quantity=80, delivery_by="1492-06-20")
    assert len(request["bids"]) == 2
    winner = next(b for b in request["bids"] if b["bidder_name"] == "River Traders")
    loser = next(b for b in request["bids"] if b["bidder_name"] == "Caravan Co")
    request = store.accept_bid(world, request_id=request["id"], bid_id=winner["id"], version=request["version"])
    assert request["status"] == "accepted"
    assert request["accepted_bid_id"] == winner["id"]
    bids = {b["id"]: b for b in request["bids"]}
    assert bids[winner["id"]]["status"] == "accepted"
    assert bids[loser["id"]]["status"] == "rejected"
    with pytest.raises(TradeError):
        store.bid(world, request_id=request["id"], bidder_name="Late Bidder",
                  price_gp=6, quantity=10, delivery_by="1492-06-20")


def test_bid_cannot_exceed_requested_quantity_or_slip_past_needed_by(board):
    store, world = board
    request = post(store, world, quantity=50, needed_by="1492-07-01")
    with pytest.raises(TradeError):
        store.bid(world, request_id=request["id"], bidder_name="Caravan Co",
                  price_gp=5, quantity=51, delivery_by="1492-06-25")
    with pytest.raises(TradeError):
        store.bid(world, request_id=request["id"], bidder_name="Caravan Co",
                  price_gp=5, quantity=10, delivery_by="1492-07-02")


def test_withdraw_bid_prevents_it_from_being_accepted(board):
    store, world = board
    request = post(store, world)
    request = store.bid(world, request_id=request["id"], bidder_name="Caravan Co",
                        price_gp=5, quantity=100, delivery_by="1492-06-25")
    bid_id = request["bids"][0]["id"]
    request = store.withdraw_bid(world, request_id=request["id"], bid_id=bid_id)
    assert request["bids"][0]["status"] == "withdrawn"
    with pytest.raises(TradeError):
        store.accept_bid(world, request_id=request["id"], bid_id=bid_id, version=request["version"])


def test_cancel_request_blocks_further_bids(board):
    store, world = board
    request = post(store, world)
    request = store.cancel_request(world, request_id=request["id"], version=request["version"])
    assert request["status"] == "cancelled"
    with pytest.raises(TradeError):
        store.bid(world, request_id=request["id"], bidder_name="Caravan Co",
                  price_gp=5, quantity=100, delivery_by="1492-06-25")


def test_cancel_request_rejects_stale_version(board):
    store, world = board
    request = post(store, world)
    with pytest.raises(TradeError):
        store.cancel_request(world, request_id=request["id"], version=request["version"] + 1)


def test_list_requests_filters_by_status_and_paginates(board):
    store, world = board
    first = post(store, world, requester_name="A")
    post(store, world, requester_name="B")
    store.cancel_request(world, request_id=first["id"], version=first["version"])
    open_only = store.list_requests(world, status="open")
    assert open_only["total"] == 1
    assert open_only["requests"][0]["requester_name"] == "B"
    everything = store.list_requests(world, status=None, limit=1)
    assert everything["total"] == 2
    assert len(everything["requests"]) == 1
