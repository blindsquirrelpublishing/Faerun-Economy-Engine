"""One-mile terrain survey of the poster map.

Rebuild the whole sheet (about half an hour):

    .\\.venv\\Scripts\\python.exe tools\\survey_terrain_1mile.py --whole --render

Or one patch, for checking a biome before committing to the full pass:

    .\\.venv\\Scripts\\python.exe tools\\survey_terrain_1mile.py --center 1500,-900 --render

The five-mile grid in ``maps/terrain-5-mile.json`` is too coarse to trace a
shoreline or a river: a single cell swallows the whole of Waterdeep harbour.
This script resamples the poster itself at one mile per cell.

The poster carries about 1.25 pixels per mile, so a one-mile cell is roughly
one source pixel. Three things are done to get usable detail out of that:

1. The crop is upsampled before classification, so a cell is decided by ~25
   interpolated samples and a coastline lands between source pixels rather
   than being snapped to one.
2. Lettering, roads and political lines are found as *ink* and painted out
   before any terrain colour is read. Without this, "THE SWORD COAST" set in
   navy across the water reads as a mountain range, and every road reads as a
   ridge. Ink is classified by hue so the four label inks (black, navy, green,
   red) can be removed while the warm brown relief hachure is kept.
3. Relief is measured as the *density* of that brown hachure over a few miles,
   not from any single pixel, because hills and mountains on this poster are
   drawn as line work over the same tan wash as the plains.

The whole sheet at one mile is 3796 x 2539 cells. Classifying it in one piece
would need about 17 GB, so it is worked in tiles that overlap by PAD_MILES and
then assembled. Everything that needs to see the whole map at once - the
open-sea flood fill, the mountain-range consolidation - runs afterwards on the
assembled cell grid, which is small.

Everything here is a reading of artwork, not a survey of terrain. Cells are
evidence about what the cartographer drew.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "maps" / "Faerun Hires.jpg"
WHOLE_OUTPUT = ROOT / "maps" / "terrain-1-mile.json"
PATCH_OUTPUT = ROOT / "maps" / "terrain-1-mile-patch.json"
REVIEW = ROOT / "maps" / "terrain-1-mile-review"

# Poster georeference, shared with faerun/mapdata.py.
MILES_PER_FPS_UNIT = 120.0
PIXELS_PER_FPS_UNIT = 150.5
PIXELS_PER_MILE = PIXELS_PER_FPS_UNIT / MILES_PER_FPS_UNIT
ANCHOR_PIXEL = (694.0, 682.0)  # Waterdeep, the FPS1:WD origin
ANCHOR_NAME = "Waterdeep"

SUPERSAMPLE = 4  # ~5 samples per mile per axis
# Tiles overlap by this much so the box filters and the ink repair never see a
# cropped edge. It has to exceed the furthest any of them reaches; the repair,
# at one supersampled pixel per round, is the greediest.
PAD_MILES = 12
TILE_MILES = 400  # keeps a tile near 350 MB
REPAIR_ROUNDS = 32
# Patch mode only. "Is this water connected to the ocean" is a question about
# the whole sheet, so a patch is worked with this much extra around it and then
# cropped back; without it a river that leaves the patch reads as sea.
FLOOD_MARGIN_MILES = 60

# --- ink thresholds (source pixels, 0-255) --------------------------------
INK_VALUE = 178  # washes on this poster all sit above this
NEUTRAL_SPREAD = 46  # max-min channel spread that still counts as black ink
NAVY_COOL = 26  # blue minus red for label navy
LABEL_GREEN = 14  # green minus the red/blue average for label green
WARM_SPREAD = 18  # red minus blue for the brown relief hachure
# Red must beat green by this much as well. The olive forest canopy is warm
# enough on red-minus-blue to pass, and drew a false ring of hills around every
# wood. Measured over Cormanthor against the Earthfast range, a gap of 8 keeps
# 97.5% of real hachure while dropping 83% of canopy.
WARM_GREEN_GAP = 8
# Warm ink is bimodal in saturation: the relief hachure is a grey-brown pen
# line and peaks around 0.17, while the red range names and orange country
# names are flat saturated colour and tail off above 0.4. Measured over the
# Sword Coast, Chult, Anauroch and the Sea of Fallen Stars.
LABEL_SATURATION = 0.42
# Labels are set with a pale halo that survives the dark-ink test and then reads
# as snow, so the label mask is grown to swallow it.
LABEL_HALO = 3
# A cell this smothered in lettering has no wash left to read, so it is taken
# from its confident neighbours instead of from an invented colour.
INK_DOUBT = 0.45
DOUBT_RADIUS_MILES = 4

# --- relief ----------------------------------------------------------------
RELIEF_RADIUS_MILES = 1.75# Ranges are drawn with heavier, darker strokes than hill hachure, so mountains
# are the cells where dark line work is both present and crowded.
MOUNTAIN_INK_VALUE = 140
MOUNTAIN_DENSITY = 0.100
# A range is a range, not a scatter of stray dark strokes: a mountain cell has
# to keep company with other mountain cells or it is demoted to hills.
MOUNTAIN_SUPPORT = 0.30
MOUNTAIN_SUPPORT_MILES = 2
HILL_DENSITY = 0.070

# --- woodland --------------------------------------------------------------
# The legend draws Forest as dark canopy over cream and Grasslands as a pale
# green wash, but at 1.25 pixels to the mile the poster does not resolve the
# canopy: both arrive as flat washes, and what separates them is lightness.
# Green land is a continuum rather than two clean modes, so the threshold is
# set midway between the legend's own swatches - Forest at value 192 and
# Grasslands at 239 - rather than at any trough in the histogram. It is a
# sensitive dial: over Cormanthor, 198 reads 17% of green as wood and 220
# reads 75%.
GREEN_MIN = 8  # green minus the red/blue average, to count as green at all
FOREST_VALUE = 215

# --- wash colours ----------------------------------------------------------
WATER_COOL = 15  # blue minus red
WATER_VALUE = 160
DESERT_WARM = 52
DESERT_GREEN_GAP = 22
GLACIER_VALUE = 243  # a wash this pale and this cold is ice, not paper
GLACIER_COOL = 6
# A tongue of "water" hugging an ice sheet is the sheet's own blue-grey edge,
# not a lake, so ice wins where ice dominates the neighbourhood.
GLACIER_ABSORB_MILES = 3
# Ice fields are hundreds of miles across, so a speck of "glacier" is a pale
# highlight on water or the halo inside big lettering, not an ice sheet.
GLACIER_SUPPORT = 0.35
GLACIER_SUPPORT_MILES = 5

#: Sheet furniture, as inclusive one-mile cells with the letter to fill them
#: with. The legend panel and title are opaque boxes over the south-eastern
#: ocean and nothing can be said about what is under them; the compass rose is
#: a medallion floating in open water, where the answer is simply sea.
FURNITURE = (
    (2800, 3243, -1995, -1330, "U"),  # legend panel and title
    (2330, 2890, -1995, -1918, "U"),  # scale bar
    (-480, -196, -1941, -1670, "S"),  # compass rose, in the Trackless Sea
)

# Cells are held as indices into this string all the way through; it is both
# the working representation and the on-disk alphabet.
LETTERS = "SWPGFHMTDIU"
(SEA, WATER, PLAINS, GRASS, FOREST, HILLS, MOUNTAINS,
 WETLAND, DESERT, GLACIER, UNKNOWN) = range(11)

LEGEND = {
    "S": "sea",
    "W": "inland_water",
    "P": "cleared_mixed",
    "G": "grassland",
    "F": "forest",
    "H": "hills",
    "M": "mountains",
    "T": "wetland",
    "D": "sandy_desert",
    "I": "ice_glacier",
    "U": "unknown",
}

# Relief and ink are one printable character per cell. At nine and a half
# million cells, JSON arrays of integers would be most of a gigabyte.
VALUE_ALPHABET = (
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz+-"
)
VALUE_MAX = len(VALUE_ALPHABET) - 1  # 63

RENDER_COLOURS = {
    SEA: (94, 150, 196),
    WATER: (128, 190, 226),
    PLAINS: (232, 223, 195),
    GRASS: (198, 210, 152),
    FOREST: (104, 138, 88),
    HILLS: (192, 166, 124),
    MOUNTAINS: (140, 118, 110),
    WETLAND: (156, 178, 160),
    DESERT: (232, 206, 146),
    GLACIER: (238, 244, 250),
    UNKNOWN: (255, 0, 255),
}


# ---------------------------------------------------------------------------
# small array helpers (kept local so the tool needs only numpy and Pillow)
# ---------------------------------------------------------------------------


def _box_mean(values: np.ndarray, radius: int) -> np.ndarray:
    """Mean of a (2r+1) square window, edge-extended, via an integral image."""
    if radius <= 0:
        return values.astype(np.float64)
    height, width = values.shape
    padded = np.pad(values.astype(np.float64), radius, mode="edge")
    integral = np.zeros((height + 2 * radius + 1, width + 2 * radius + 1), np.float64)
    integral[1:, 1:] = padded.cumsum(0).cumsum(1)
    span = 2 * radius + 1
    total = (
        integral[span:, span:]
        - integral[:-span, span:]
        - integral[span:, :-span]
        + integral[:-span, :-span]
    )
    return total / float(span * span)


def _dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    return _box_mean(mask.astype(np.float64), radius) > 1e-9


def _erode(mask: np.ndarray, radius: int) -> np.ndarray:
    return _box_mean(mask.astype(np.float64), radius) > 0.999


def _block_mean(values: np.ndarray, y_edges: np.ndarray,
                x_edges: np.ndarray) -> np.ndarray:
    """Average `values` over each cell, given integer sample-grid edges."""
    block = values[y_edges[0]:y_edges[-1], x_edges[0]:x_edges[-1]]
    rows = np.add.reduceat(block, y_edges[:-1] - y_edges[0], axis=0)
    rows = rows / np.diff(y_edges)[:, None]
    columns = np.add.reduceat(rows, x_edges[:-1] - x_edges[0], axis=1)
    return columns / np.diff(x_edges)[None, :]


def _repair(rgb: np.ndarray, ink: np.ndarray) -> np.ndarray:
    """Replace ink with the colour of the nearest surviving wash pixel.

    Nearest rather than average on purpose. Averaging across a road that runs
    along a shoreline mixes sea blue with land tan and invents a band of cells
    that are neither, so a removed stroke is instead split down the middle
    between the washes on either side of it.
    """
    values = rgb.astype(np.float32).copy()
    valid = ~ink
    offsets = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    for _ in range(REPAIR_ROUNDS):
        if valid.all():
            break
        filled = valid.copy()
        for dy, dx in offsets:
            source_valid = np.roll(np.roll(valid, dy, axis=0), dx, axis=1)
            take = (~filled) & source_valid
            if not take.any():
                continue
            shifted = np.roll(np.roll(values, dy, axis=0), dx, axis=1)
            values[take] = shifted[take]
            filled |= take
        if not (filled & ~valid).any():
            break
        valid = filled
    return values


# ---------------------------------------------------------------------------
# reading the artwork
# ---------------------------------------------------------------------------


def _ink_masks(rgb: np.ndarray) -> Dict[str, np.ndarray]:
    """Split the poster's line work into label ink and relief hachure.

    Label ink is removed before terrain colour is read; relief hachure is the
    only evidence this poster offers for hills and mountains, so it is kept as
    a separate density channel and only then painted out.
    """
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    value = rgb.max(axis=2)
    low = rgb.min(axis=2)
    spread = value - low
    greenness = green - (red + blue) / 2.0

    dark = value < INK_VALUE
    saturated = spread >= LABEL_SATURATION * np.maximum(value, 1)
    # Warm ink is tested first. Much of the hill hachure is mid-tone brown whose
    # channel spread also passes the neutral test, and losing it to the label
    # mask would flatten every range on the sheet.
    warm = dark & ((red - blue) >= WARM_SPREAD) & ((red - green) >= WARM_GREEN_GAP)
    black = dark & (spread < NEUTRAL_SPREAD) & ~warm  # roads, city dots, lettering
    navy = dark & ((blue - red) >= NAVY_COOL)  # water and river lettering
    leaf = dark & (greenness >= LABEL_GREEN)
    # Most dark green on this sheet is forest wash, not lettering: the forest
    # mode sits at value 182, below the ink threshold. Only the saturated part
    # is a place name, and only that may be painted out - masking the rest
    # would erase every wood on the map.
    green_label = leaf & saturated
    # Range and country names share the hachure's hue, so they are told apart
    # by how saturated they are rather than by colour or stroke shape.
    glyph = warm & saturated

    label = _dilate(black | navy | green_label | glyph, LABEL_HALO)
    # Black lettering on a warm wash leaves warm-tinted JPEG fringes that would
    # otherwise be counted as relief, so the grown label mask wins here.
    hachure = warm & ~label
    return {
        "label": label,
        "hachure": hachure,
        "mountain": hachure & (value < MOUNTAIN_INK_VALUE),
        "ink": label | hachure,
    }


def _wash_classes(wash: np.ndarray) -> np.ndarray:
    """Land-cover index per supersampled pixel, from the repaired colour wash."""
    red = wash[:, :, 0]
    green = wash[:, :, 1]
    blue = wash[:, :, 2]
    value = wash.max(axis=2)
    greenness = green - (red + blue) / 2.0

    codes = np.full(value.shape, PLAINS, np.uint8)
    wooded_or_grass = greenness >= GREEN_MIN
    codes[wooded_or_grass] = GRASS
    codes[wooded_or_grass & (value < FOREST_VALUE)] = FOREST
    # Desert is tested after green because sandy yellow reads as green on this
    # metric: the Sandy Desert swatch scores 17.6, above the grassland mode.
    codes[((red - blue) >= DESERT_WARM) & ((green - blue) >= DESERT_GREEN_GAP)] = DESERT
    codes[(value >= GLACIER_VALUE) & ((blue - red) >= GLACIER_COOL)] = GLACIER
    codes[((blue - red) >= WATER_COOL) & (value >= WATER_VALUE)] = WATER
    return codes


#: What the colour wash can say on its own. Hills and mountains are added
#: afterwards from hachure density, and sea is separated from inland water by
#: flood fill.
WASH_CANDIDATES = (PLAINS, GRASS, FOREST, DESERT, GLACIER, WATER)


def _modal_codes(classes: np.ndarray, y_edges: np.ndarray,
                 x_edges: np.ndarray) -> np.ndarray:
    """Collapse supersampled classes to one per cell by majority vote."""
    best: np.ndarray | None = None
    chosen: np.ndarray | None = None
    for candidate in WASH_CANDIDATES:
        score = _block_mean((classes == candidate).astype(np.float32), y_edges, x_edges)
        if best is None:
            best = score
            chosen = np.full(score.shape, candidate, np.uint8)
            continue
        assert chosen is not None
        better = score > best
        best[better] = score[better]
        chosen[better] = candidate
    assert chosen is not None
    return chosen


# ---------------------------------------------------------------------------
# tiling
# ---------------------------------------------------------------------------


def poster_bounds() -> Tuple[int, int, int, int]:
    """The whole sheet, as inclusive one-mile cell columns and rows."""
    with Image.open(SOURCE) as handle:
        width, height = handle.size
    column_min = math.ceil(0.5 - ANCHOR_PIXEL[0] / PIXELS_PER_MILE)
    column_max = math.floor((width - ANCHOR_PIXEL[0]) / PIXELS_PER_MILE - 0.5)
    row_max = math.floor(ANCHOR_PIXEL[1] / PIXELS_PER_MILE - 0.5)
    row_min = math.ceil((ANCHOR_PIXEL[1] - height) / PIXELS_PER_MILE + 0.5)
    return column_min, column_max, row_min, row_max


def _tile_geometry(c0: int, c1: int, r0: int, r1: int):
    """Crop box in poster pixels plus the cell edges within the upsampled crop."""
    columns = np.arange(c1 - c0 + 2) + c0 - 0.5
    # FPS rows grow north while poster y grows south, so the northern edge of
    # the top row comes first and every array here is held north-first.
    rows = (r1 + 0.5) - np.arange(r1 - r0 + 2)
    x_px = ANCHOR_PIXEL[0] + columns * PIXELS_PER_MILE
    y_px = ANCHOR_PIXEL[1] - rows * PIXELS_PER_MILE
    pad = PAD_MILES * PIXELS_PER_MILE
    box = (
        int(math.floor(x_px[0] - pad)),
        int(math.floor(y_px[0] - pad)),
        int(math.ceil(x_px[-1] + pad)),
        int(math.ceil(y_px[-1] + pad)),
    )
    x_edges = np.rint((x_px - box[0]) * SUPERSAMPLE).astype(np.intp)
    y_edges = np.rint((y_px - box[1]) * SUPERSAMPLE).astype(np.intp)
    return box, y_edges, x_edges


def _classify_tile(source: Image.Image, c0: int, c1: int, r0: int, r1: int):
    box, y_edges, x_edges = _tile_geometry(c0, c1, r0, r1)
    crop = source.crop(box)
    crop = crop.resize(
        (crop.width * SUPERSAMPLE, crop.height * SUPERSAMPLE), Image.BICUBIC
    )
    rgb = np.asarray(crop).astype(np.int16)
    del crop

    masks = _ink_masks(rgb)
    wash = _repair(rgb, masks["ink"])
    del rgb

    radius = max(1, int(round(RELIEF_RADIUS_MILES * PIXELS_PER_MILE * SUPERSAMPLE)))
    hill = _block_mean(_box_mean(masks["hachure"], radius), y_edges, x_edges)
    mountain = _block_mean(_box_mean(masks["mountain"], radius), y_edges, x_edges)
    ink = _block_mean(masks["ink"].astype(np.float32), y_edges, x_edges)
    codes = _modal_codes(_wash_classes(wash), y_edges, x_edges)
    return codes, hill, mountain, ink


def _tile_spans(low: int, high: int) -> List[Tuple[int, int]]:
    spans = []
    start = low
    while start <= high:
        stop = min(high, start + TILE_MILES - 1)
        spans.append((start, stop))
        start = stop + 1
    return spans


def survey_region(c0: int, c1: int, r0: int, r1: int, progress: bool = True):
    """Classify every one-mile cell in the region, tile by tile."""
    shape = (r1 - r0 + 1, c1 - c0 + 1)
    codes = np.zeros(shape, np.uint8)
    hill = np.zeros(shape, np.float32)
    mountain = np.zeros(shape, np.float32)
    ink = np.zeros(shape, np.float32)

    column_spans = _tile_spans(c0, c1)
    row_spans = _tile_spans(r0, r1)
    total = len(column_spans) * len(row_spans)
    done = 0
    started = time.perf_counter()
    with Image.open(SOURCE) as handle:
        source = handle.convert("RGB")
        for tr0, tr1 in row_spans:
            for tc0, tc1 in column_spans:
                tile = _classify_tile(source, tc0, tc1, tr0, tr1)
                # North-first in both the tile and the region, so FPS row r
                # sits at index r1 - r.
                rows = slice(r1 - tr1, r1 - tr0 + 1)
                cols = slice(tc0 - c0, tc1 - c0 + 1)
                codes[rows, cols], hill[rows, cols] = tile[0], tile[1]
                mountain[rows, cols], ink[rows, cols] = tile[2], tile[3]
                done += 1
                if progress and total > 1:
                    elapsed = time.perf_counter() - started
                    print(
                        f"  tile {done}/{total}  columns {tc0}..{tc1}"
                        f" rows {tr0}..{tr1}  {elapsed:5.0f}s elapsed,"
                        f" {elapsed / done * (total - done):5.0f}s left",
                        flush=True,
                    )
    return codes, hill, mountain, ink


# ---------------------------------------------------------------------------
# passes that need the whole region at once
# ---------------------------------------------------------------------------


def _resolve_doubt(codes: np.ndarray, doubt: np.ndarray, radius: int) -> np.ndarray:
    """Re-read cells buried under lettering from the cells that were legible."""
    confident = ~doubt
    best = np.zeros(codes.shape, np.float32)
    chosen = np.full(codes.shape, UNKNOWN, np.uint8)
    for candidate in WASH_CANDIDATES:
        score = _box_mean(confident & (codes == candidate), radius).astype(np.float32)
        better = score > best
        best[better] = score[better]
        chosen[better] = candidate
    result = codes.copy()
    replace = doubt & (best > 0.0)
    result[replace] = chosen[replace]
    return result


def _flood_sea(codes: np.ndarray) -> np.ndarray:
    """Water connected to the edge of the sheet is sea; the rest is inland."""
    height, width = codes.shape
    stride = width + 4
    # A ring of virtual ocean around the sheet, itself inside a dead border.
    # The ring makes every edge water cell reachable from one seed and, because
    # a row start's left neighbour is then a ring cell, removes the need to
    # check for row wrap; the dead border keeps every neighbour index in range.
    padded = np.zeros((height + 4, stride), bool)
    padded[2:-2, 2:-2] = codes == WATER
    padded[1, 1:-1] = padded[-2, 1:-1] = True
    padded[1:-1, 1] = padded[1:-1, -2] = True
    water = padded.ravel()
    seen = np.zeros(water.shape, bool)

    start = stride + 1
    seen[start] = True
    stack = [start]
    while stack:
        index = stack.pop()
        for step in (1, -1, stride, -stride):
            nxt = index + step
            if water[nxt] and not seen[nxt]:
                seen[nxt] = True
                stack.append(nxt)

    result = codes.copy()
    result[seen.reshape(height + 4, stride)[2:-2, 2:-2]] = SEA
    return result


def _finish(codes: np.ndarray, hill: np.ndarray, mountain: np.ndarray,
            ink: np.ndarray):
    lonely_ice = (codes == GLACIER) & (
        _box_mean(codes == GLACIER, GLACIER_SUPPORT_MILES) < GLACIER_SUPPORT
    )
    codes = _resolve_doubt(codes, (ink >= INK_DOUBT) | lonely_ice, DOUBT_RADIUS_MILES)
    # Relief is a separate reading from land cover: a wooded hillside is still
    # woodland, so only open ground is promoted to hills. Mountain line work is
    # dense enough to bury whatever is beneath it and does override.
    open_ground = (codes == PLAINS) | (codes == GRASS)
    codes[open_ground & (hill >= HILL_DENSITY)] = HILLS
    peaks = (codes != WATER) & (mountain >= MOUNTAIN_DENSITY)
    peaks &= _box_mean(peaks, MOUNTAIN_SUPPORT_MILES) >= MOUNTAIN_SUPPORT
    codes[peaks] = MOUNTAINS

    ice = _box_mean(codes == GLACIER, GLACIER_ABSORB_MILES)
    codes[(codes == WATER) & (ice > _box_mean(codes == WATER, GLACIER_ABSORB_MILES))] = GLACIER
    codes = _flood_sea(codes)

    relief = np.clip((hill + 2.0 * mountain) / (3.0 * MOUNTAIN_DENSITY), 0.0, 1.0)
    relief[(codes == SEA) | (codes == WATER)] = 0.0
    return codes, relief


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

_LETTER_LUT = np.frombuffer(LETTERS.encode("ascii"), np.uint8)
_VALUE_LUT = np.frombuffer(VALUE_ALPHABET.encode("ascii"), np.uint8)


def _letter_rows(codes: np.ndarray, row_max: int) -> Dict[str, str]:
    return {
        str(row_max - index): _LETTER_LUT[row].tobytes().decode("ascii")
        for index, row in enumerate(codes)
    }


def _value_rows(values: np.ndarray, row_max: int) -> Dict[str, str]:
    scaled = np.rint(np.clip(values, 0.0, 1.0) * VALUE_MAX).astype(np.uint8)
    return {
        str(row_max - index): _VALUE_LUT[row].tobytes().decode("ascii")
        for index, row in enumerate(scaled)
    }


def write_payload(destination: Path, codes, relief, ink,
                  c0: int, c1: int, r0: int, r1: int) -> dict:
    width = c1 - c0 + 1
    height = r1 - r0 + 1
    payload = {
        "format": "faerun-terrain-simple-v1",
        "description": (
            "One-mile terrain cells read from the poster map. Lettering, roads "
            "and political lines are masked out before terrain colour is "
            "sampled; hills and mountains come from hachure density, not from "
            "a single pixel. relief and ink are one character per cell, "
            "indexed into value_alphabet; ink is how much of the cell was line "
            "work, so a high ink value marks a weak reading."
        ),
        "frame": "FPS1:WD",
        "origin": ANCHOR_NAME,
        "cell_miles": 1,
        "source": SOURCE.name,
        "pixels_per_mile": round(PIXELS_PER_MILE, 6),
        "supersample": SUPERSAMPLE,
        "column_min": c0,
        "column_max": c1,
        "row_min": r0,
        "row_max": r1,
        "width": width,
        "height": height,
        "cell_count": width * height,
        "legend": LEGEND,
        "value_alphabet": VALUE_ALPHABET,
        "rows": _letter_rows(codes, r1),
        "relief": _value_rows(relief, r1),
        "ink": _value_rows(ink, r1),
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    return payload


def render_review(codes: np.ndarray, relief: np.ndarray, ink: np.ndarray,
                  name: str, scale: int) -> None:
    REVIEW.mkdir(parents=True, exist_ok=True)
    height, width = codes.shape

    picture = np.zeros((height, width, 3), np.uint8)
    for value, colour in RENDER_COLOURS.items():
        picture[codes == value] = colour
    grey = (255 - np.clip(relief, 0.0, 1.0) * 215).astype(np.uint8)
    doubt = (np.clip(ink, 0.0, 1.0) * 255).astype(np.uint8)

    for suffix, array in (
        ("terrain", picture),
        ("relief", np.dstack([grey] * 3)),
        ("ink", np.dstack([doubt] * 3)),
    ):
        image = Image.fromarray(array)
        if scale != 1:
            image = image.resize((width * scale, height * scale), Image.NEAREST)
        image.save(REVIEW / f"{name}-{suffix}.png")


def render_source(c0: int, c1: int, r0: int, r1: int, name: str, scale: int) -> None:
    """The artwork the survey read, at the same size as the review renders."""
    box, _, _ = _tile_geometry(c0, c1, r0, r1)
    pad = int(round(PAD_MILES * PIXELS_PER_MILE))
    box = (box[0] + pad, box[1] + pad, box[2] - pad, box[3] - pad)
    with Image.open(SOURCE) as handle:
        crop = handle.convert("RGB").crop(box)
    crop = crop.resize(((c1 - c0 + 1) * scale, (r1 - r0 + 1) * scale), Image.LANCZOS)
    REVIEW.mkdir(parents=True, exist_ok=True)
    crop.save(REVIEW / f"{name}-source.png")


# ---------------------------------------------------------------------------
# entry points
# ---------------------------------------------------------------------------


def survey(c0: int, c1: int, r0: int, r1: int, destination: Path,
           name: str, render: bool, scale: int, margin: int = 0) -> dict:
    if not SOURCE.is_file():
        raise SystemExit(
            f"poster not found: {SOURCE}\n"
            "This survey reads a poster you supply; none is shipped with the project."
        )
    sheet = poster_bounds()
    c0, c1 = max(sheet[0], c0), min(sheet[1], c1)
    r0, r1 = max(sheet[2], r0), min(sheet[3], r1)
    w0, w1 = max(sheet[0], c0 - margin), min(sheet[1], c1 + margin)
    v0, v1 = max(sheet[2], r0 - margin), min(sheet[3], r1 + margin)
    codes, hill, mountain, ink = survey_region(w0, w1, v0, v1)
    codes, relief = _finish(codes, hill, mountain, ink)
    for fc0, fc1, fr0, fr1, letter in FURNITURE:
        left, right = max(w0, fc0) - w0, min(w1, fc1) - w0
        # North-first, so the high row number is the low array index.
        top, bottom = v1 - min(v1, fr1), v1 - max(v0, fr0)
        if right >= left and bottom >= top:
            codes[top:bottom + 1, left:right + 1] = LETTERS.index(letter)
            relief[top:bottom + 1, left:right + 1] = 0.0

    rows = slice(v1 - r1, v1 - r0 + 1)
    columns = slice(c0 - w0, c1 - w0 + 1)
    codes, relief, ink = codes[rows, columns], relief[rows, columns], ink[rows, columns]

    payload = write_payload(destination, codes, relief, ink, c0, c1, r0, r1)
    if render:
        render_review(codes, relief, ink, name, scale)
        render_source(c0, c1, r0, r1, name, scale)
    return payload


def _report(payload: dict, destination: Path) -> None:
    counts: Dict[str, int] = {}
    for row in payload["rows"].values():
        for letter in row:
            counts[letter] = counts.get(letter, 0) + 1
    total = payload["cell_count"]
    size = destination.stat().st_size / 1e6
    print(
        f"Wrote {payload['width']} x {payload['height']} one-mile cells "
        f"({total:,} cells, {size:.1f} MB) to {destination}"
    )
    for letter, count in sorted(counts.items(), key=lambda item: -item[1]):
        print(f"  {letter} {LEGEND[letter]:<14} {count:9,d}  {100 * count / total:5.1f}%")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--whole", action="store_true",
                        help="survey the entire poster instead of one patch")
    parser.add_argument("--center", default="0,0",
                        help="patch centre as one-mile column,row from Waterdeep")
    parser.add_argument("--radius", type=int, default=100)
    parser.add_argument("--name", default=None, help="prefix for review images")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--render", action="store_true", help="write review images")
    args = parser.parse_args()

    if args.whole:
        c0, c1, r0, r1 = poster_bounds()
        destination = args.output or WHOLE_OUTPUT
        name = args.name or "whole"
        scale = 1
        margin = 0
    else:
        column, row = (int(part) for part in args.center.split(","))
        c0, c1 = column - args.radius, column + args.radius
        r0, r1 = row - args.radius, row + args.radius
        destination = args.output or PATCH_OUTPUT
        name = args.name or f"patch-{column}-{row}"
        scale = 5
        margin = FLOOD_MARGIN_MILES
    payload = survey(c0, c1, r0, r1, destination, name, args.render, scale, margin)
    _report(payload, destination)


if __name__ == "__main__":
    main()
