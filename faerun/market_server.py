"""Start/stop control for the standalone market-board web server.

The dashboard (``faerun.cli ... serve``) runs as its own long-lived process
with its own copy of the world in memory, entirely separate from whatever
process is running the MCP server. Editing the catalog through
:mod:`faerun.catalog` only changes the MCP server's process, so the running
dashboard keeps showing whatever it had loaded at startup until it is
restarted. This module tracks the last server this code started and gives
the MCP tool a one-call way to bounce it.
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = Path(__file__).resolve().parent / "data" / "store" / "market_server.json"


def _load_state() -> Optional[Dict[str, Any]]:
    if not STATE_PATH.exists():
        return None
    try:
        with STATE_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def _save_state(state: Dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def _pid_is_ours(pid: int) -> bool:
    """True if `pid` is still alive and looks like a faerun market server."""
    if sys.platform == "win32":
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"(Get-CimInstance Win32_Process -Filter \"ProcessId={pid}\").CommandLine"],
            capture_output=True, text=True, timeout=10,
        )
        cmdline = result.stdout or ""
    else:
        try:
            cmdline = Path(f"/proc/{pid}/cmdline").read_text(errors="ignore").replace("\x00", " ")
        except OSError:
            return False
    return "faerun.cli" in cmdline and "serve" in cmdline


def _kill(pid: int) -> bool:
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"],
                            capture_output=True, timeout=10)
        else:
            import os
            import signal

            os.kill(pid, signal.SIGTERM)
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def _port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def stop_market_server() -> Dict[str, Any]:
    """Stop the last server this module started, if it is still running."""
    state = _load_state()
    if not state:
        return {"stopped": False, "reason": "no tracked server"}
    pid = state.get("pid")
    if not pid or not _pid_is_ours(pid):
        return {"stopped": False, "reason": "tracked process is no longer running"}
    killed = _kill(pid)
    return {"stopped": killed, "pid": pid}


def restart_market_server(
    host: str = "127.0.0.1", port: int = 8883,
    seasonal_inventory: bool = False, category: str = "",
    wait_seconds: float = 10.0,
) -> Dict[str, Any]:
    """Stop the tracked server (if any) and start a fresh one with today's catalog.

    A freshly started process reads the current ``faerun/data/store/*.json``
    catalog and price snapshots from disk, so this is how a running dashboard
    picks up commodities, settlements, businesses or routes added or edited
    through the MCP catalog tools since it was last launched.
    """
    stopped = stop_market_server()

    args = [
        sys.executable, "-u", "-m", "faerun.cli",
        "--seasonal-inventory" if seasonal_inventory else "--no-seasonal-inventory",
        "serve", "--host", host, "--port", str(port), "--no-browser",
    ]
    if category:
        args += ["--category", category]
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS \
        if sys.platform == "win32" else 0
    process = subprocess.Popen(
        args, cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=creationflags, close_fds=True,
    )

    deadline = time.monotonic() + wait_seconds
    up = False
    while time.monotonic() < deadline:
        if _port_open(host, port):
            up = True
            break
        if process.poll() is not None:
            break
        time.sleep(0.3)

    _save_state({
        "pid": process.pid, "host": host, "port": port,
        "seasonal_inventory": seasonal_inventory, "started_at": time.time(),
    })
    return {
        "previous_server": stopped,
        "started_pid": process.pid,
        "url": f"http://{host}:{port}/",
        "up": up,
        "exited_immediately": process.poll() is not None,
    }
