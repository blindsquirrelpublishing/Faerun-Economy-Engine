"""Persistent simulation POs, atomic forecast claims, and manually recorded cash."""

from __future__ import annotations

from contextlib import closing, contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import math
import os
from pathlib import Path
import sqlite3
import uuid

from .trading import (
    CENT, TradeError, boolean, build_quote, integer, iso, number,
    parse_date, public_quote, remaining_supply, text,
)


APPLICATION_ID = 1178944852
SCHEMA = """
CREATE TABLE IF NOT EXISTS trade_meta (id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL);
INSERT OR IGNORE INTO trade_meta VALUES (1,0);
CREATE TABLE IF NOT EXISTS trade_quotes (
 id TEXT PRIMARY KEY, created_at TEXT NOT NULL, expires_at TEXT NOT NULL,
 snapshot TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS trade_orders (
 id TEXT PRIMARY KEY, quote_id TEXT NOT NULL UNIQUE REFERENCES trade_quotes(id),
 customer_name TEXT NOT NULL, po_reference TEXT NOT NULL,
 customer_key TEXT NOT NULL, reference_key TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('reserved','dispatched','delivered','cancelled')),
 version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL,
 simulation_date TEXT NOT NULL, dispatched_date TEXT, delivered_date TEXT,
 UNIQUE(customer_key,reference_key)
);
CREATE TABLE IF NOT EXISTS trade_claims (
 order_id TEXT PRIMARY KEY REFERENCES trade_orders(id),
 source_id TEXT NOT NULL, destination_id TEXT NOT NULL, commodity TEXT NOT NULL,
 quality TEXT NOT NULL, mode TEXT NOT NULL CHECK(mode IN ('uncommitted','allocated_export')),
 start_day INTEGER NOT NULL, end_day INTEGER NOT NULL,
 quantity INTEGER NOT NULL CHECK(quantity>0), CHECK(end_day>=start_day)
);
CREATE INDEX IF NOT EXISTS trade_claim_window ON trade_claims(source_id,commodity,start_day,end_day);
CREATE TABLE IF NOT EXISTS trade_payments (
 id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL REFERENCES trade_orders(id),
 kind TEXT NOT NULL, amount_cents INTEGER NOT NULL CHECK(amount_cents>0),
 reference TEXT NOT NULL, reference_key TEXT NOT NULL,
 created_at TEXT NOT NULL, simulation_date TEXT NOT NULL,
 UNIQUE(order_id,reference_key)
);
CREATE TABLE IF NOT EXISTS trade_audit (
 id INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL REFERENCES trade_orders(id),
 action TEXT NOT NULL, created_at TEXT NOT NULL, simulation_date TEXT NOT NULL,
 details TEXT NOT NULL
);
"""


def default_ledger_path():
    override = os.environ.get("FAERUN_TRADE_DB")
    if override:
        return Path(override).expanduser().resolve()
    root = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
    return root / "FaerunEconomyEngine" / "trade-ledger.sqlite3"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _cents(value):
    return int(Decimal(str(value)) * 100)


class TradeStore:
    def __init__(self, path):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._claims_revision = -1
        self._claims_cache = []
        with closing(sqlite3.connect(self.path, timeout=30)) as db:
            db.execute("BEGIN IMMEDIATE")
            application = db.execute("PRAGMA application_id").fetchone()[0]
            version = db.execute("PRAGMA user_version").fetchone()[0]
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
            fresh = application == 0 and version == 0 and not tables
            required = {"trade_meta", "trade_quotes", "trade_orders", "trade_claims", "trade_payments", "trade_audit"}
            if not fresh and (application != APPLICATION_ID or version != 1
                              or not required <= {row[0] for row in tables}):
                raise TradeError("Selected database is not a supported Faerun trade ledger")
            if fresh:
                for statement in SCHEMA.split(";"):
                    if statement.strip():
                        db.execute(statement)
                db.execute(f"PRAGMA application_id={APPLICATION_ID}")
                db.execute("PRAGMA user_version=1")
            db.commit()

    @contextmanager
    def connection(self, *, write=False):
        with closing(sqlite3.connect(self.path, timeout=30)) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA foreign_keys=ON")
            with db:
                if write:
                    db.execute("BEGIN IMMEDIATE")
                yield db

    @property
    def revision(self):
        with self.connection() as db:
            return db.execute("SELECT revision FROM trade_meta WHERE id=1").fetchone()[0]

    @staticmethod
    def _claims(db):
        claims = []
        for row in db.execute(
                "SELECT c.*,o.status,q.snapshot FROM trade_claims c "
                "JOIN trade_orders o ON o.id=c.order_id "
                "JOIN trade_quotes q ON q.id=o.quote_id WHERE o.status!='cancelled'"):
            claim = dict(row)
            basis = json.loads(claim.pop("snapshot"))["_basis"]
            claim["inventory_stock"] = bool(basis.get("inventory_enabled") and claim["mode"] == "uncommitted")
            claim["stock_capacities"] = basis["uncommitted_by_quality"]
            claims.append(claim)
        return claims

    def claims(self):
        with self.connection() as db:
            revision = db.execute("SELECT revision FROM trade_meta WHERE id=1").fetchone()[0]
            if revision != self._claims_revision:
                self._claims_cache = self._claims(db)
                self._claims_revision = revision
        return [dict(row) for row in self._claims_cache]

    @staticmethod
    def _audit(db, order_id, action, world, details):
        db.execute("INSERT INTO trade_audit(order_id,action,created_at,simulation_date,details) VALUES (?,?,?,?,?)",
                   (order_id, action, _now(), iso(world.date), _json(details)))
        db.execute("UPDATE trade_meta SET revision=revision+1 WHERE id=1")

    @staticmethod
    def _quote(db, quote_id):
        row = db.execute("SELECT snapshot FROM trade_quotes WHERE id=?", (quote_id,)).fetchone()
        if row is None:
            raise TradeError("Quote not found", 404)
        return json.loads(row["snapshot"])

    def quote(self, world, parameters):
        quote = build_quote(world, parameters, self.claims())
        quote.update(id=str(uuid.uuid4()), created_at=_now(),
                     expires_at=(datetime.now(timezone.utc) + timedelta(hours=24)).isoformat())
        with self.connection(write=True) as db:
            db.execute("INSERT INTO trade_quotes VALUES (?,?,?,?)",
                       (quote["id"], quote["created_at"], quote["expires_at"], _json(quote)))
        return public_quote(quote)

    def reserve(self, world, *, quote_id, customer_name, po_reference,
                terms_accepted=False, allocation_authorized=False):
        quote_id = text(quote_id, "quote_id", maximum=64)
        customer = text(customer_name, "customer_name", maximum=160)
        reference = text(po_reference, "po_reference", maximum=160)
        if not boolean(terms_accepted, "terms_accepted"):
            raise TradeError("Confirm the supplier/customer terms and eligibility for the agreed guild or producer rate")
        boolean(allocation_authorized, "allocation_authorized")
        with self.connection() as db:
            quote = self._quote(db, quote_id)
            previous = db.execute("SELECT id,customer_key,reference_key FROM trade_orders WHERE quote_id=?", (quote_id,)).fetchone()
        if previous is not None:
            if previous["customer_key"] != customer.casefold() or previous["reference_key"] != reference.casefold():
                raise TradeError("This quote already belongs to a different PO", 409)
            return self.order(world, previous["id"])
        if datetime.fromisoformat(quote["expires_at"]) <= datetime.now(timezone.utc):
            raise TradeError("Quote expired; request a new quote", 409)
        if world.date.absolute_day() > parse_date(quote["pickup_date"], "pickup_date").absolute_day():
            raise TradeError("The quoted pickup date has passed; request a new quote", 409)
        if quote["_basis"]["mode"] == "allocated_export" and not allocation_authorized:
            raise TradeError("Confirm authorization to fulfil this existing export allocation")
        fresh = build_quote(world, quote["_params"], revalidate=True)
        if fresh["_signature"] != quote["_signature"]:
            raise TradeError("Forecast, pricing or terms changed; request a fresh quote", 409)
        with self.connection(write=True) as db:
            previous = db.execute("SELECT id,customer_key,reference_key FROM trade_orders WHERE quote_id=?", (quote_id,)).fetchone()
            if previous is not None:
                if previous["customer_key"] != customer.casefold() or previous["reference_key"] != reference.casefold():
                    raise TradeError("This quote already belongs to a different PO", 409)
                return self._order(db, world, previous["id"])
            if datetime.fromisoformat(quote["expires_at"]) <= datetime.now(timezone.utc):
                raise TradeError("Quote expired during validation; request a new quote", 409)
            if db.execute("SELECT id FROM trade_orders WHERE customer_key=? AND reference_key=?",
                          (customer.casefold(), reference.casefold())).fetchone():
                raise TradeError("This customer PO reference is already recorded", 409)
            available = remaining_supply(fresh["_basis"], self._claims(db))
            if quote["quantity"] > available["available_units"]:
                raise TradeError(f"Only {available['available_units']} units remain in this dated supply pool", 409)
            order_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO trade_orders(id,quote_id,customer_name,po_reference,customer_key,reference_key,status,created_at,simulation_date) VALUES (?,?,?,?,?,?,'reserved',?,?)",
                (order_id, quote_id, customer, reference, customer.casefold(), reference.casefold(), _now(), iso(world.date)))
            basis = fresh["_basis"]
            db.execute("INSERT INTO trade_claims VALUES (?,?,?,?,?,?,?,?,?)",
                       (order_id, basis["source_id"], basis["destination_id"], basis["commodity"],
                        basis["quality"], basis["mode"], basis["start_day"], basis["end_day"], quote["quantity"]))
            self._audit(db, order_id, "reserved", world,
                        {"quantity": quote["quantity"], "terms_accepted": True,
                         "allocation_authorized": allocation_authorized, "basis": basis})
            return self._order(db, world, order_id)

    @staticmethod
    def _balances(db, order, quote, world):
        totals = {kind: 0 for kind in ("customer_payment", "customer_refund", "supplier_payment", "supplier_refund", "expense")}
        for row in db.execute("SELECT kind,SUM(amount_cents) amount FROM trade_payments WHERE order_id=? GROUP BY kind", (order["id"],)):
            totals[row["kind"]] = row["amount"]
        received = totals["customer_payment"] - totals["customer_refund"]
        paid = totals["supplier_payment"] - totals["supplier_refund"]
        amount = quote["amounts"]
        customer_total = _cents(amount["customer_total_gp"])
        supplier_total = _cents(amount["supplier_total_gp"])
        deposit = _cents(amount["customer_deposit_due_gp"])
        before_dispatch = customer_total if quote["terms"]["payment_terms"] == "before_dispatch" else deposit
        today = world.date.absolute_day()
        ready = parse_date(quote["pickup_date"], "pickup_date").absolute_day()
        arrival = (parse_date(order["dispatched_date"], "dispatch_date").absolute_day()
                   + math.ceil(quote["shipping"]["one_way_days"])) if order["dispatched_date"] else None
        warnings = []
        if received < 0 or paid < 0:
            raise TradeError("Ledger contains an invalid negative payment balance", 500)
        if order["status"] == "reserved":
            if today < ready:
                warnings.append(f"Pickup is not due until {quote['pickup_date']}; the world clock is not advanced automatically.")
            if paid < supplier_total:
                warnings.append("Record procurement payment before dispatch.")
            if received < before_dispatch:
                warnings.append("The required customer deposit/prepayment has not been recorded.")
            warnings.append("Supply is rechecked at dispatch; forecast availability is not a physical stock survey.")
        if today > parse_date(quote["delivery_date"], "delivery_date").absolute_day() and order["status"] not in ("cancelled", "delivered"):
            warnings.append("The agreed delivery date has passed; customer acceptance of a late delivery must be confirmed.")
        if order["status"] == "delivered" and received < customer_total:
            warnings.append("Delivery was accepted but the customer balance remains outstanding.")
        return {
            "customer_paid_gp": received / 100,
            "customer_due_gp": max(0, customer_total - received) / 100 if order["status"] != "cancelled" else 0,
            "supplier_paid_gp": paid / 100,
            "supplier_due_gp": max(0, supplier_total - paid) / 100 if order["status"] != "cancelled" else 0,
            "expenses_gp": totals["expense"] / 100,
            "recorded_cash_gp": (received - paid - totals["expense"]) / 100,
            "deposit_remaining_gp": max(0, deposit - received) / 100 if order["status"] != "cancelled" else 0,
            "can_dispatch": order["status"] == "reserved" and today >= ready and paid >= supplier_total and received >= before_dispatch,
            "can_deliver": order["status"] == "dispatched" and arrival is not None and today >= arrival,
            "can_cancel": order["status"] == "reserved" and received == 0 and paid == 0,
            "warnings": warnings,
        }

    def _order(self, db, world, order_id):
        row = db.execute("SELECT * FROM trade_orders WHERE id=?", (order_id,)).fetchone()
        if row is None:
            raise TradeError("PO not found", 404)
        order = dict(row)
        quote = self._quote(db, order["quote_id"])
        order.pop("customer_key")
        order.pop("reference_key")
        order["quote"] = public_quote(quote)
        order["payments"] = [
            {"kind": row["kind"], "amount_gp": row["amount_cents"] / 100,
             "reference": row["reference"], "created_at": row["created_at"], "simulation_date": row["simulation_date"]}
            for row in db.execute("SELECT * FROM trade_payments WHERE order_id=? ORDER BY id", (order_id,))
        ]
        order["audit"] = [
            {"action": row["action"], "created_at": row["created_at"],
             "simulation_date": row["simulation_date"], "details": json.loads(row["details"])}
            for row in db.execute("SELECT * FROM trade_audit WHERE order_id=? ORDER BY id", (order_id,))
        ]
        order["balance"] = self._balances(db, order, quote, world)
        return order

    def order(self, world, order_id):
        with self.connection() as db:
            return self._order(db, world, text(order_id, "order_id", maximum=64))

    @staticmethod
    def _check_date(world, order):
        latest = max(parse_date(row["simulation_date"], "record date").absolute_day()
                     for row in order["audit"])
        if world.date.absolute_day() < latest:
            raise TradeError("Cannot record an action before this PO's latest simulation entry", 409)

    def list_orders(self, world, *, offset=0, limit=50):
        offset = integer(offset, "offset", minimum=0)
        limit = integer(limit, "limit", maximum=500)
        with self.connection() as db:
            count = db.execute("SELECT COUNT(*) FROM trade_orders").fetchone()[0]
            rows = db.execute("SELECT id FROM trade_orders ORDER BY created_at DESC,id LIMIT ? OFFSET ?", (limit, offset)).fetchall()
            return {"orders": [self._order(db, world, row["id"]) for row in rows],
                    "total": count, "offset": offset, "limit": limit}

    def payment(self, world, *, order_id, kind, amount_gp, reference):
        order_id = text(order_id, "order_id", maximum=64)
        reference = text(reference, "reference", maximum=160)
        if kind not in ("customer_payment", "customer_refund", "supplier_payment", "supplier_refund", "expense"):
            raise TradeError("Unknown cash-entry kind")
        amount = number(amount_gp, "amount_gp", minimum=.01, maximum=1_000_000_000_000)
        if amount != amount.quantize(CENT):
            raise TradeError("Cash entries must be whole copper pieces (at most two gp decimals)")
        cents = _cents(amount)
        with self.connection(write=True) as db:
            order = self._order(db, world, order_id)
            previous = db.execute("SELECT kind,amount_cents FROM trade_payments WHERE order_id=? AND reference_key=?",
                                  (order_id, reference.casefold())).fetchone()
            if previous:
                if previous["kind"] != kind or previous["amount_cents"] != cents:
                    raise TradeError("This cash reference was already used for a different entry", 409)
                return order
            self._check_date(world, order)
            balance = order["balance"]
            limits = {
                "customer_payment": balance["customer_due_gp"], "customer_refund": balance["customer_paid_gp"],
                "supplier_payment": balance["supplier_due_gp"], "supplier_refund": balance["supplier_paid_gp"],
            }
            if order["status"] == "cancelled" and kind != "expense":
                raise TradeError("Cancelled orders cannot receive new payments or refunds", 409)
            if kind in limits and cents > _cents(limits[kind]):
                raise TradeError("Cash entry exceeds the outstanding balance or recorded payment", 409)
            db.execute("INSERT INTO trade_payments(order_id,kind,amount_cents,reference,reference_key,created_at,simulation_date) VALUES (?,?,?,?,?,?,?)",
                       (order_id, kind, cents, reference, reference.casefold(), _now(), iso(world.date)))
            db.execute("UPDATE trade_orders SET version=version+1 WHERE id=?", (order_id,))
            self._audit(db, order_id, kind, world, {"amount_gp": float(amount), "reference": reference})
            return self._order(db, world, order_id)

    def transition(self, world, *, order_id, action, version, accepted=False):
        order_id = text(order_id, "order_id", maximum=64)
        if action not in ("dispatch", "deliver", "cancel"):
            raise TradeError("Unknown PO action")
        target = {"dispatch": "dispatched", "deliver": "delivered", "cancel": "cancelled"}[action]
        version = integer(version, "version", maximum=1_000_000_000)
        boolean(accepted, "accepted")
        with self.connection() as db:
            initial = self._order(db, world, order_id)
            quote = self._quote(db, initial["quote_id"])
        fresh = build_quote(world, quote["_params"], revalidate=True) if action == "dispatch" and initial["status"] == "reserved" else None
        with self.connection(write=True) as db:
            order = self._order(db, world, order_id)
            if order["status"] == target or (action == "dispatch" and order["status"] == "delivered"):
                return order
            if order["version"] != version:
                raise TradeError("PO changed; refresh it before applying this action", 409)
            self._check_date(world, order)
            balance = order["balance"]
            if action == "cancel" and not balance["can_cancel"]:
                raise TradeError("Only undispatched orders can be cancelled; first record refunds of supplier and customer payments", 409)
            if action == "dispatch":
                if not balance["can_dispatch"] or fresh is None:
                    raise TradeError("Dispatch requires the pickup date, supplier payment and required customer deposit/prepayment", 409)
                other_claims = [row for row in self._claims(db) if row["order_id"] != order_id]
                if quote["quantity"] > remaining_supply(fresh["_basis"], other_claims)["available_units"]:
                    raise TradeError("Reserved supply is no longer covered by the forecast; cancel/requote or resolve the shortage before dispatch", 409)
            if action == "deliver" and (not balance["can_deliver"] or not accepted):
                raise TradeError("Record delivery only after the travel time and explicit customer acceptance", 409)
            date_field = ",dispatched_date=?" if action == "dispatch" else ",delivered_date=?" if action == "deliver" else ""
            values = [target]
            if date_field:
                values.append(iso(world.date))
            values.append(order_id)
            db.execute(f"UPDATE trade_orders SET status=?,version=version+1{date_field} WHERE id=?", values)
            self._audit(db, order_id, target, world,
                        {"accepted": accepted, "claims_released": action == "cancel",
                         "late": world.date.absolute_day() > parse_date(quote["delivery_date"], "delivery_date").absolute_day()})
            return self._order(db, world, order_id)
