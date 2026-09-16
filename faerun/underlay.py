"""Locate and serve a user-supplied poster map to sit under the world map.

The published Faerun poster maps are Wizards of the Coast artwork, so no image
is shipped with this project and none is ever copied into it. Instead this
module *finds* a copy the user already owns, on their own machine, and the web
server streams those bytes to the browser at request time. Delete the file and
the overlay simply disappears again.

Resolution order, first hit wins:

1. an explicit path handed to `set_override` (the `--underlay` CLI flag),
2. the `FAERUN_MAP_UNDERLAY` environment variable,
3. a file called `underlay.<ext>` in `maps/`, the project root or the working
   directory,
4. a case-insensitive world-poster name (such as "Faerun map.jpg" or
   "Faerun Hires.jpg") in
   `maps/`, the project root, the working directory, `~/Downloads`,
   `~/Pictures` and `~/Desktop`.

`maps/` is searched first, but city maps and unrelated images are not candidates.
Rule 4 exists because that is where a downloaded poster actually lands, and
asking someone to move or rename a 30 MB scan before the feature works is a
poor trade for a few lines of globbing. The match is deliberately loose - the
file that prompted this feature is named `Faeun Map.jpg`, missing an "r".
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# Formats every current browser can decode from an <img> tag.
EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".avif": "image/avif",
}

# Require a world/region name even inside maps/, where city maps also live.
NAME_HINT = re.compile(
    r"(fae\w{0,4}n|sword[\s\-_]*coast|realms|toril)[\s\-_.]{0,4}.{0,20}"
    r"(?:map|hi(?:gh)?[\s\-_]*res(?:olution)?)", re.I
)

ENV_VAR = "FAERUN_MAP_UNDERLAY"

_override: Optional[Path] = None

# The file is read once and held, keyed on (path, mtime, size), so panning the
# map does not re-read a 30 MB scan off disk on every request.
_cache: Optional[Dict[str, Any]] = None


def set_override(path: Optional[str]) -> None:
    """Pin the underlay to an explicit path (or clear the pin with None)."""
    global _override, _cache
    _override = Path(path).expanduser() if path else None
    _cache = None


def project_root() -> Path:
    """The directory that holds the `faerun` package."""
    return Path(__file__).resolve().parent.parent


def _search_dirs() -> List[Path]:
    root = project_root()
    # `maps/` is checked before the root itself: it is the obvious place to put
    # a poster, and looking there first means the file does not have to sit
    # loose in the project directory to be found.
    dirs: List[Path] = [root / "maps", root, Path.cwd(), Path.cwd() / "maps"]
    home = Path.home()
    dirs.extend([home / "Downloads", home / "Pictures", home / "Desktop"])
    seen: List[Path] = []
    for d in dirs:
        if d not in seen:
            seen.append(d)
    return seen


def _usable(path: Optional[Path]) -> Optional[Path]:
    if path is None:
        return None
    try:
        if path.is_file() and path.suffix.lower() in MIME_TYPES:
            return path
    except OSError:
        return None
    return None


def _mtime(path: Path) -> float:
    """Modification time, or 0.0 if the file went away mid-scan."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def find_underlay() -> Optional[Path]:
    """Return the first plausible poster map on disk, or None."""
    hit = _usable(_override)
    if hit is not None:
        return hit

    env = os.environ.get(ENV_VAR, "").strip()
    if env:
        hit = _usable(Path(env).expanduser())
        if hit is not None:
            return hit

    dirs = _search_dirs()

    # Explicitly named file first: it is the documented way to be unambiguous.
    for folder in dirs:
        for ext in EXTENSIONS:
            hit = _usable(folder / ("underlay" + ext))
            if hit is not None:
                return hit

    # Only world-poster name matches compete by recency, never arbitrary city maps.
    for folder in dirs:
        try:
            entries = sorted(folder.iterdir())
        except OSError:
            continue
        matches = [
            p for p in entries
            if p.suffix.lower() in MIME_TYPES
            and NAME_HINT.search(p.name)
        ]
        if not matches:
            continue
        matches.sort(key=_mtime, reverse=True)
        hit = _usable(matches[0])
        if hit is not None:
            return hit

    return None


def underlay_bytes() -> Optional[Dict[str, Any]]:
    """Read the underlay, memoised on path/mtime/size. None when absent."""
    global _cache
    path = find_underlay()
    if path is None:
        _cache = None
        return None
    try:
        stat = path.stat()
    except OSError:
        _cache = None
        return None
    stamp = (str(path), stat.st_mtime, stat.st_size)
    if _cache is not None and _cache["stamp"] == stamp:
        return _cache
    try:
        raw = path.read_bytes()
    except OSError:
        _cache = None
        return None
    _cache = {
        "stamp": stamp,
        "path": path,
        "raw": raw,
        "mime": MIME_TYPES.get(path.suffix.lower(), "application/octet-stream"),
    }
    return _cache


def underlay_info() -> Dict[str, Any]:
    """A small JSON-safe description for the browser.

    The pixel size is deliberately *not* reported: working it out would mean
    parsing JPEG/PNG/WebP headers by hand, and the browser already knows it for
    free from `naturalWidth` once the image loads.
    """
    path = find_underlay()
    if path is None:
        return {
            "available": False,
            "url": "",
            "name": "",
            "path": "",
            "mime": "",
            "bytes": 0,
            "searched": [str(d) for d in _search_dirs()],
            "env_var": ENV_VAR,
        }
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return {
        "available": True,
        "url": "/underlay.img",
        "name": path.name,
        "path": str(path),
        "mime": MIME_TYPES.get(path.suffix.lower(), "application/octet-stream"),
        "bytes": size,
        "searched": [str(d) for d in _search_dirs()],
        "env_var": ENV_VAR,
    }
