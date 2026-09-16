"""Re-survey the gazetteer against a real map.

The built-in coordinates in `data/settlements.py` were hand-tuned for plausible
travel times, not for cartographic accuracy, and the error is *not* uniform: the
Sword Coast is close to canon while the Western Heartlands are squashed and the
Backlands are stretched.  No amount of nudging the poster overlay's pan/scale
sliders can reconcile the two, because a single rigid transform cannot undo a
distortion that changes sign across the map.

So instead of moving the poster to fit the dots, this module moves the dots to
fit the poster.  You place a handful of *control points* - "Waterdeep really
belongs here" - and it fits a smooth warp through them and carries every other
settlement along for the ride.  A dozen well-spread control points is usually
enough to pull all 125 markets into place.

The warp is a least-squares affine fit plus an inverse-distance-weighted
correction of the residuals.  That combination is exact at every control point
(so a city you placed by hand stays exactly where you put it) and blends
smoothly in between, which is what lets it absorb a distortion that varies
across the map.

Only the control points are persisted, in `data/coords.json`.  The gazetteer
stays the single readable source of truth and the calibration rides on top as a
small, auditable overlay - delete the file and you are back to the shipped
coordinates.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

Point = Tuple[float, float]
Pair = Tuple[Point, Point]
Warp = Callable[[float, float], Point]

# Where the control points live.  Sits beside settlements.py so a calibrated
# checkout is obvious at a glance.
COORDS_FILE = Path(__file__).resolve().parent / "data" / "coords.json"

# Guards the inverse-distance weights from blowing up when a query point sits
# exactly on a control point.  In map miles, so this is a 1-mile softening.
_EPSILON = 1.0

# Beyond this the residual correction is not meaningful any more - the affine
# part carries the point instead.  Keeps a single stray control point in Thay
# from dragging Icewind Dale sideways.
_FALLOFF = 900.0


# ---------------------------------------------------------------------------
# linear algebra (deliberately tiny - the whole point is to stay dependency free)
# ---------------------------------------------------------------------------


def _solve3(matrix: List[List[float]], rhs: List[float]) -> Optional[List[float]]:
    """Solve a 3x3 system by Gaussian elimination with partial pivoting.

    Returns None when the system is singular, which happens whenever the
    control points are collinear - a real possibility if someone calibrates
    three cities straight up the Sword Coast.
    """
    m = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(3):
        pivot = max(range(col, 3), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-9:
            return None
        m[col], m[pivot] = m[pivot], m[col]
        pv = m[col][col]
        for r in range(3):
            if r == col:
                continue
            factor = m[r][col] / pv
            if factor:
                for c in range(col, 4):
                    m[r][c] -= factor * m[col][c]
    return [m[i][3] / m[i][i] for i in range(3)]


def _fit_affine(pairs: Sequence[Pair]) -> Optional[Tuple[float, ...]]:
    """Least-squares fit of x' = a.x + b.y + c and y' = d.x + e.y + f."""
    if len(pairs) < 3:
        return None
    normal = [[0.0] * 3 for _ in range(3)]
    rhs_x = [0.0] * 3
    rhs_y = [0.0] * 3
    for (sx, sy), (tx, ty) in pairs:
        basis = (sx, sy, 1.0)
        for i in range(3):
            for j in range(3):
                normal[i][j] += basis[i] * basis[j]
            rhs_x[i] += basis[i] * tx
            rhs_y[i] += basis[i] * ty
    sol_x = _solve3(normal, rhs_x)
    sol_y = _solve3(normal, rhs_y)
    if sol_x is None or sol_y is None:
        return None
    return (sol_x[0], sol_x[1], sol_x[2], sol_y[0], sol_y[1], sol_y[2])


def _fit_similarity(pairs: Sequence[Pair]) -> Optional[Tuple[float, ...]]:
    """Fallback fit: rotation, uniform scale and translation only.

    Needs just two distinct points and cannot go singular on collinear input,
    which is exactly the case the affine fit gives up on.
    """
    n = len(pairs)
    if n < 2:
        return None
    sx0 = sum(p[0][0] for p in pairs) / n
    sy0 = sum(p[0][1] for p in pairs) / n
    tx0 = sum(p[1][0] for p in pairs) / n
    ty0 = sum(p[1][1] for p in pairs) / n
    num_re = num_im = denom = 0.0
    for (sx, sy), (tx, ty) in pairs:
        ax, ay = sx - sx0, sy - sy0
        bx, by = tx - tx0, ty - ty0
        # complex multiply b * conj(a)
        num_re += bx * ax + by * ay
        num_im += by * ax - bx * ay
        denom += ax * ax + ay * ay
    if denom < 1e-9:
        return None
    a = num_re / denom
    b = num_im / denom
    # x' = a.x - b.y + c ; y' = b.x + a.y + f
    c = tx0 - (a * sx0 - b * sy0)
    f = ty0 - (b * sx0 + a * sy0)
    return (a, -b, c, b, a, f)


def _fit_translation(pairs: Sequence[Pair]) -> Tuple[float, ...]:
    """Last resort: shift everything by the mean offset."""
    n = len(pairs) or 1
    dx = sum(t[0] - s[0] for s, t in pairs) / n
    dy = sum(t[1] - s[1] for s, t in pairs) / n
    return (1.0, 0.0, dx, 0.0, 1.0, dy)


# ---------------------------------------------------------------------------
# the warp
# ---------------------------------------------------------------------------


def build_warp(pairs: Sequence[Pair]) -> Warp:
    """Build a smooth map-miles -> map-miles function through `pairs`.

    With no pairs this is the identity, so an uncalibrated install pays nothing
    but a function call.
    """
    pairs = [p for p in pairs]
    if not pairs:
        return lambda x, y: (x, y)
    if len(pairs) == 1:
        (sx, sy), (tx, ty) = pairs[0]
        dx, dy = tx - sx, ty - sy
        return lambda x, y: (x + dx, y + dy)

    coeff = _fit_affine(pairs) or _fit_similarity(pairs) or _fit_translation(pairs)
    a, b, c, d, e, f = coeff

    def affine(x: float, y: float) -> Point:
        return (a * x + b * y + c, d * x + e * y + f)

    # What the affine part failed to explain at each control point.  Feeding
    # these back in through inverse-distance weighting is what makes the warp
    # interpolate exactly rather than merely approximate.
    anchors: List[Tuple[float, float, float, float]] = []
    for (sx, sy), (tx, ty) in pairs:
        ax, ay = affine(sx, sy)
        anchors.append((sx, sy, tx - ax, ty - ay))

    if all(abs(rx) < 1e-9 and abs(ry) < 1e-9 for _, _, rx, ry in anchors):
        return affine

    def warp(x: float, y: float) -> Point:
        bx, by = affine(x, y)
        total = 0.0
        sum_x = 0.0
        sum_y = 0.0
        for sx, sy, rx, ry in anchors:
            dx = x - sx
            dy = y - sy
            d2 = dx * dx + dy * dy
            if d2 < 1e-12:
                return (bx + rx, by + ry)
            dist = math.sqrt(d2)
            # 1/d^2 for a tight local pull, tapered so distant control points
            # stop mattering entirely rather than contributing a constant bias.
            taper = max(0.0, 1.0 - dist / _FALLOFF)
            if taper <= 0.0:
                continue
            w = taper * taper / (d2 + _EPSILON)
            total += w
            sum_x += w * rx
            sum_y += w * ry
        if total <= 0.0:
            return (bx, by)
        return (bx + sum_x / total, by + sum_y / total)

    return warp


# ---------------------------------------------------------------------------
# persistence
# ---------------------------------------------------------------------------


def load_control_points(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Read the saved control points, tolerating a missing or broken file.

    Calibration is a convenience, never a hard dependency: a corrupt file
    degrades to "not calibrated" instead of taking the whole engine down.
    """
    target = Path(path) if path is not None else COORDS_FILE
    try:
        raw = target.read_text(encoding="utf-8")
    except (OSError, ValueError):
        return []
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    if isinstance(data, dict):
        data = data.get("control") or data.get("points") or []
    if not isinstance(data, list):
        return []
    points: List[Dict[str, Any]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        sid = str(item.get("id") or "").strip()
        try:
            x = float(item.get("x"))
            y = float(item.get("y"))
        except (TypeError, ValueError):
            continue
        if sid:
            points.append({"id": sid, "x": x, "y": y})
    return points


def save_control_points(
    points: Iterable[Dict[str, Any]], path: Optional[Path] = None
) -> Path:
    """Write control points out, or delete the file when the list is empty.

    Writes through a temporary file and replaces, so an interrupted save cannot
    leave a half-written calibration behind.
    """
    target = Path(path) if path is not None else COORDS_FILE
    clean: List[Dict[str, Any]] = []
    for item in points or []:
        sid = str((item or {}).get("id") or "").strip()
        if not sid:
            continue
        try:
            x = float(item.get("x"))
            y = float(item.get("y"))
        except (TypeError, ValueError):
            continue
        clean.append({"id": sid, "x": round(x, 1), "y": round(y, 1)})

    if not clean:
        try:
            target.unlink()
        except OSError:
            pass
        return target

    payload = {
        "note": (
            "Control points captured on the map screen. Each entry says where a "
            "settlement really belongs; every other market is carried along by a "
            "smooth fit through these. Delete this file to restore the shipped "
            "coordinates."
        ),
        "control": clean,
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(target))
    return target


# ---------------------------------------------------------------------------
# applying it
# ---------------------------------------------------------------------------


# Attribute used to remember a settlement's shipped position the first time it
# is calibrated.  Every warp is applied to *that*, never to an already-moved
# position, so re-calibrating replaces the previous fit instead of compounding
# it.  Stashing it on the object rather than in a module-level table keyed by
# id() avoids the classic id-reuse trap when a temporary gazetteer is collected.
BASE_ATTR = "_base_xy"


def base_coordinates(settlements: Sequence[Any]) -> Dict[str, Point]:
    """The pre-calibration position of each settlement in `settlements`."""
    snapshot: Dict[str, Point] = {}
    for s in settlements:
        sid = getattr(s, "id", "")
        if not sid:
            continue
        src = getattr(s, BASE_ATTR, None)
        if src is None:
            src = (float(s.x), float(s.y))
            setattr(s, BASE_ATTR, src)
        snapshot[sid] = src
    return snapshot


def warp_for(settlements: Sequence[Any], points: Sequence[Dict[str, Any]]) -> Warp:
    """Resolve control points against a gazetteer and build the warp."""
    base = base_coordinates(settlements)
    pairs: List[Pair] = []
    for item in points:
        src = base.get(item["id"])
        if src is None:
            continue
        pairs.append((src, (float(item["x"]), float(item["y"]))))
    return build_warp(pairs)


def apply_calibration(
    settlements: Sequence[Any], points: Optional[Sequence[Dict[str, Any]]] = None
) -> int:
    """Move every settlement through the saved warp, in place.

    Returns the number of control points that actually matched a settlement, so
    callers can report "calibrated against 9 landmarks" without re-reading the
    file.  An empty control list restores the shipped coordinates.
    """
    control = list(points) if points is not None else load_control_points()
    base = base_coordinates(settlements)
    used = sum(1 for item in control if item["id"] in base)

    if not used:
        # Nothing to fit - put everything back where it started.  This is the
        # path taken when the user clears their calibration.
        for s in settlements:
            src = base.get(getattr(s, "id", ""))
            if src is not None:
                s.x, s.y = src
        return 0

    warp = warp_for(settlements, control)
    for s in settlements:
        src = base.get(getattr(s, "id", ""))
        if src is None:
            continue
        x, y = warp(src[0], src[1])
        s.x = round(x, 1)
        s.y = round(y, 1)
    return used
