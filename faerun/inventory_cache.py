"""Disposable, versioned inventory checkpoints; never an order or purchase ledger."""

import hashlib
import json
import math
import os
import sqlite3
from contextlib import closing
from pathlib import Path
import zlib


SCHEMA_VERSION = 1


def default_inventory_cache_path():
    root = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
    return root / "FaerunEconomyEngine" / "inventory-checkpoints.sqlite3"


def scenario_key(world):
    settings = dict(world.economy_state_key(month=0)[2])
    settings.pop("inventory_cache_path", None)
    payload = {
        "version": SCHEMA_VERSION,
        "settings": settings,
        "commodities": [c.to_dict() for c in world.commodities.values()],
        "settlements": [s.to_dict() for s in world.settlements.values()],
        "events": [event.to_dict() for event in world.events.values()],
        "routes": [[edge.src, edge.dst, edge.distance, edge.quality, edge.kind, edge.name]
                   for edges in world._edges.values() for edge in edges],
    }
    encoded = json.dumps(payload, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class InventoryCheckpointStore:
    def __init__(self, path, signature):
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.signature = signature
        with closing(sqlite3.connect(self.path, timeout=60)) as connection, connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS inventory_checkpoints ("
                "scenario TEXT NOT NULL, day INTEGER NOT NULL, stock BLOB NOT NULL, "
                "PRIMARY KEY(scenario, day))"
            )

    def save(self, day, stocks):
        encoded = json.dumps(stocks, allow_nan=False, separators=(",", ":")).encode()
        compressed = zlib.compress(encoded)
        with closing(sqlite3.connect(self.path, timeout=60)) as connection, connection:
            connection.execute(
                "INSERT OR REPLACE INTO inventory_checkpoints(scenario,day,stock) VALUES(?,?,?)",
                (self.signature, day, compressed),
            )

    def load(self, day, capacity):
        with closing(sqlite3.connect(self.path, timeout=60)) as connection:
            row = connection.execute(
                "SELECT day,stock FROM inventory_checkpoints WHERE scenario=? AND day<=? "
                "ORDER BY day DESC LIMIT 1", (self.signature, day),
            ).fetchone()
        if row is None:
            return None
        try:
            stocks = json.loads(zlib.decompress(row[1]))
        except (zlib.error, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ValueError(f"Invalid compressed inventory checkpoint in {self.path}") from error
        if not isinstance(stocks, dict) or stocks.keys() != capacity.keys():
            raise ValueError("Inventory checkpoint commodities do not match this scenario")
        for cid, values in stocks.items():
            if not isinstance(values, dict) or values.keys() != capacity[cid].keys():
                raise ValueError(f"Inventory checkpoint locations do not match for {cid}")
            for sid, value in values.items():
                if (isinstance(value, bool) or not isinstance(value, (int, float))
                        or not math.isfinite(value) or not 0 <= value <= capacity[cid][sid]):
                    raise ValueError(f"Invalid inventory checkpoint quantity for {sid}/{cid}")
        return row[0], stocks
