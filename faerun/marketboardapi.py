"""JSON-facing market board: customer-posted commodity requests and bids."""

from .trading import TradeError, iso


def _store(world):
    if world.trade_store is None:
        raise TradeError("The market board ledger is not configured for this world", 503)
    return world.trade_store


def _fields(body, allowed, required):
    if not isinstance(body, dict) or set(body) - set(allowed):
        raise TradeError("Request contains unsupported fields")
    missing = set(required) - set(body)
    if missing:
        raise TradeError("Missing required fields: " + ", ".join(sorted(missing)))


def options(world, params):
    locations = sorted(world.settlements.values(), key=lambda s: s.name)
    goods = sorted(world.commodities.values(), key=lambda c: c.name)
    return {
        "enabled": world.trade_store is not None,
        "date": {"iso": iso(world.date), "label": str(world.date)},
        "settlements": [{"id": s.id, "name": s.name} for s in locations],
        "commodities": [{"id": c.id, "name": c.name, "unit": c.unit} for c in goods],
        "qualities": ["basic", "standard", "fine", "masterwork"],
        "assumptions": [
            "The market board is a public bulletin board: anyone can post a commodity request or "
            "bid on an open one. It does not move goods, reserve stock or transfer coin.",
            "A requester accepts at most one bid; accepting closes the request and rejects the "
            "other pending bids. Fulfilment, payment and delivery happen outside this board.",
            "Bids must promise delivery on or before the request's needed-by date and cannot "
            "offer more than the requested quantity.",
        ],
    }


def requests(world, params):
    return _store(world).list_requests(
        world, status=(params.get("status", [None])[0] or None),
        offset=params.get("offset", ["0"])[0], limit=params.get("limit", ["50"])[0])


def request(world, params):
    return {"request": _store(world).request(world, params.get("id", [""])[0])}


def post_request(world, body):
    required = ("requester_name", "commodity", "quantity", "quality", "settlement_id", "needed_by")
    _fields(body, (*required, "notes", "max_price_gp"), required)
    return {"request": _store(world).post_request(world, **body)}


def cancel_request(world, body):
    required = ("request_id", "version")
    _fields(body, required, required)
    return {"request": _store(world).cancel_request(world, **body)}


def bid(world, body):
    required = ("request_id", "bidder_name", "price_gp", "quantity", "delivery_by")
    _fields(body, (*required, "notes"), required)
    return {"request": _store(world).bid(world, **body)}


def withdraw_bid(world, body):
    required = ("request_id", "bid_id")
    _fields(body, required, required)
    return {"request": _store(world).withdraw_bid(world, **body)}


def accept_bid(world, body):
    required = ("request_id", "bid_id", "version")
    _fields(body, required, required)
    return {"request": _store(world).accept_bid(world, **body)}


GET_BOARD_ROUTES = {
    "/api/board/options": options,
    "/api/board/requests": requests,
    "/api/board/request": request,
}

POST_BOARD_ROUTES = {
    "/api/board/request": post_request,
    "/api/board/request/cancel": cancel_request,
    "/api/board/bid": bid,
    "/api/board/bid/withdraw": withdraw_bid,
    "/api/board/bid/accept": accept_bid,
}
