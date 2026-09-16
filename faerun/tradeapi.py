"""JSON-facing merchant guild and customer PO operations."""

from .trading import TradeError, iso


def _store(world):
    if world.trade_store is None:
        raise TradeError("The trade ledger is not configured for this world", 503)
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
        "commodities": [{"id": c.id, "name": c.name, "unit": c.unit, "weight": c.weight} for c in goods],
        "qualities": ["basic", "standard", "fine", "masterwork"],
        "defaults": {
            "origin": "berdusk" if "berdusk" in world.settlements else locations[0].id,
            "destination": "proskur" if "proskur" in world.settlements else locations[-1].id,
            "commodity": "wine_fine" if "wine_fine" in world.commodities else goods[0].id,
            "quantity": 1000, "quality": "standard", "supply_mode": "allocated_export",
            "purchase_channel": "producer", "delivery_terms": "pickup",
            "transport_mode": "own_caravan", "daily_gp": 5, "fixed_gp": 0,
            "contingency_pct": 10, "return_trip": True,
            "customer_price_mode": "retail", "tax_terms": "included",
            "deposit_percent": 50, "payment_terms": "on_delivery",
            "acceptance_terms": "Customer to confirm the agreed quantity and grade on delivery; rejected goods and any late delivery require explicit agreement.",
        },
        "assumptions": [
            "Merchant guild (wholesale) rates are not retail prices or merchant buyback offers. Producer-gate procurement is a separate channel.",
            "Quotations expire after 24 real-world hours. Only confirming a PO reserves a dated forecast quota.",
            "Reservations and manual cash entries persist locally across restarts. They do not send orders, move real money, reserve a vehicle, or create a second GDP/trade flow.",
            "Dispatch requires the agreed pickup date, recorded supplier payment and the customer's agreed deposit/prepayment. Delivery requires elapsed travel time and explicit acceptance.",
            "Physical stock and supplier authorization must be confirmed independently; this is a planning and recordkeeping model.",
        ],
    }


def quote(world, body):
    return {"quote": _store(world).quote(world, body)}


def reserve(world, body):
    required = ("quote_id", "customer_name", "po_reference")
    _fields(body, (*required, "terms_accepted", "allocation_authorized"), required)
    return {"order": _store(world).reserve(world, **body)}


def payment(world, body):
    required = ("order_id", "kind", "amount_gp", "reference")
    _fields(body, required, required)
    return {"order": _store(world).payment(world, **body)}


def status(world, body):
    required = ("order_id", "action", "version")
    _fields(body, (*required, "accepted"), required)
    return {"order": _store(world).transition(world, **body)}


def orders(world, params):
    return _store(world).list_orders(world, offset=params.get("offset", ["0"])[0],
                                    limit=params.get("limit", ["50"])[0])


def order(world, params):
    return {"order": _store(world).order(world, params.get("id", [""])[0])}


GET_TRADE_ROUTES = {
    "/api/trade/options": options, "/api/trade/orders": orders, "/api/trade/order": order,
}
POST_TRADE_ROUTES = {
    "/api/trade/quote": quote, "/api/trade/order": reserve,
    "/api/trade/payment": payment, "/api/trade/status": status,
}
