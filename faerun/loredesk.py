"""Persistent, asynchronous conversations between the user and the Lore agent."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import sqlite3
from urllib.parse import urlparse
from uuid import uuid4

from .atlas import project_root
from .data.lore import LORE


def desk_path():
    return project_root() / ".local" / "lore-desk.sqlite3"


@contextmanager
def connection():
    path = desk_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    database = sqlite3.connect(path, timeout=10)
    database.row_factory = sqlite3.Row
    try:
        database.execute("CREATE TABLE IF NOT EXISTS threads (id TEXT PRIMARY KEY, title TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL, updated TEXT NOT NULL)")
        database.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, thread_id TEXT NOT NULL, author TEXT NOT NULL, body TEXT NOT NULL, sources TEXT NOT NULL, created TEXT NOT NULL)")
        with database:
            yield database
    finally:
        database.close()


def text(value, name, limit):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise ValueError(f"{name} must contain 1 to {limit} characters")
    return value.strip()


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def append_message(database, thread_id, author, body, sources):
    database.execute(
        "INSERT INTO messages(thread_id, author, body, sources, created) VALUES (?, ?, ?, ?, ?)",
        (thread_id, author, body, json.dumps(sources), timestamp()),
    )


def read_desk(world=None, params=None):
    with connection() as database:
        threads = [dict(row) for row in database.execute("SELECT * FROM threads ORDER BY updated DESC")]
        for thread in threads:
            thread["messages"] = [
                {**dict(row), "sources": json.loads(row["sources"])}
                for row in database.execute("SELECT * FROM messages WHERE thread_id = ? ORDER BY id", (thread["id"],))
            ]
    return {"threads": threads, "research": [{"id": identifier, **entry} for identifier, entry in LORE.items()]}


def post_desk(world, body):
    action = body.get("action", "create")
    with connection() as database:
        database.execute("BEGIN IMMEDIATE")
        if action == "create":
            title = text(body.get("title"), "Title", 160)
            message = text(body.get("body"), "Message", 12000)
            kind = body.get("kind", "research")
            if kind not in ("research", "question", "map", "economy"):
                raise ValueError("Unknown research category")
            identifier = str(uuid4())
            database.execute("INSERT INTO threads VALUES (?, ?, ?, ?, ?)", (identifier, title, kind, "queued", timestamp()))
            append_message(database, identifier, "You", message, [])
        else:
            identifier = text(body.get("id"), "Thread ID", 80)
            thread = database.execute("SELECT * FROM threads WHERE id = ?", (identifier,)).fetchone()
            if thread is None:
                raise KeyError(identifier)
            if action == "reply":
                if thread["status"] == "closed":
                    raise ValueError("Reopen the conversation before replying")
                append_message(database, identifier, "You", text(body.get("body"), "Message", 12000), [])
                status = "queued"
            elif action == "status" and body.get("status") in ("queued", "closed"):
                status = body["status"]
            else:
                raise ValueError("Unknown conversation action")
            database.execute("UPDATE threads SET status = ?, updated = ? WHERE id = ?", (status, timestamp(), identifier))
    return {"id": identifier}


def publish_reply(thread_id, body, sources=()):
    """Publish a real agent response locally; never exposed as a browser mutation."""
    message = text(body, "Message", 12000)
    citations = []
    for source in sources:
        title = text(source.get("title"), "Source title", 300)
        url = text(source.get("url"), "Source URL", 2000)
        if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
            raise ValueError("Sources require HTTP or HTTPS URLs")
        citations.append({"title": title, "url": url})
    with connection() as database:
        database.execute("BEGIN IMMEDIATE")
        thread = database.execute("SELECT * FROM threads WHERE id = ?", (thread_id,)).fetchone()
        if thread is None:
            raise KeyError(thread_id)
        if thread["status"] == "closed":
            raise ValueError("Conversation is closed")
        append_message(database, thread_id, "Lore", message, citations)
        database.execute("UPDATE threads SET status = 'answered', updated = ? WHERE id = ?", (timestamp(), thread_id))
    return {"id": thread_id}