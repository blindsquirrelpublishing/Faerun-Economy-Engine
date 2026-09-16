"""Local, reproducible full-map roof-candidate survey and probability sample audit.

Rebuild: .\\.venv\\Scripts\\python.exe tools\\survey_waterdeep_hires.py --rebuild --render
Check:   .\\.venv\\Scripts\\python.exe tools\\survey_waterdeep_hires.py --check

Geometry is in ORIGINAL IMAGE PIXELS, not geographic coordinates. Connected
roof-colour regions are candidates, never automatically verified buildings.
The UI contract exposes features as a list and boundary as a MultiPolygon;
boundary_features preserves the individual boundary-feature metadata.

The final predictor is distance-seeded watershed, not connected components.
All 659 boundary-intersecting 160-pixel cells form the frame. Five fixed
candidate-density strata each contribute eight seeded SRSWOR cells. The 40
visual tallies and their interpretation ranges are preserved below. The
stratified difference estimator corrects the known full-map predictor total
using area-cell count residuals; finite-population sampling uncertainty is
reported separately from roof-interpretation sensitivity. This is not an
exact city building enumeration or a population estimate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "maps" / "waterdeep-map-hires.jpg"
OUTPUT = ROOT / "faerun" / "data" / "waterdeep_hires_survey.json"
REVIEW = ROOT / "maps" / "hires-survey-review"
SHA256 = "1c98bab4f7346cf70b0533e31f60f9956b339934ed50a0f6f3aef87c5d2d1797"
WIDTH, HEIGHT = 3560, 7256
CELL = 160
SEED = 20260916
SAMPLE_PER_STRATUM = 8

# Trace on a 981 x 2000 overview, transformed to the original raster below.
# The harbor-chain pylons are not buildings; the fortified islands are included.
BOUNDARY_TRACES = {
    "mainland": [
        [214, 45], [251, 52], [353, 82], [469, 115], [578, 143],
        [657, 174], [730, 224], [783, 275], [826, 308], [815, 335],
        [823, 358], [810, 412], [807, 481], [815, 555], [827, 616],
        [834, 706], [838, 791], [835, 835], [817, 891], [811, 949],
        [797, 1010], [791, 1103], [804, 1152], [819, 1188],
        [886, 1190], [923, 1197], [931, 1220], [921, 1255],
        [899, 1290], [908, 1355], [932, 1402], [959, 1481],
        [960, 1572], [943, 1591], [943, 1663], [929, 1701],
        [915, 1743], [887, 1780], [853, 1790], [833, 1768],
        [813, 1745], [787, 1721], [749, 1720], [725, 1688],
        [710, 1675], [675, 1650], [635, 1635], [588, 1615],
        [563, 1592], [522, 1570], [490, 1535], [471, 1515],
        [445, 1470], [414, 1435], [392, 1405], [381, 1378],
        [362, 1363], [329, 1364], [282, 1378], [242, 1383],
        [238, 1397], [220, 1396], [209, 1370], [172, 1364],
        [144, 1369], [135, 1398], [149, 1425], [163, 1436],
        [165, 1460], [149, 1475], [131, 1469], [127, 1426],
        [108, 1405], [99, 1374], [91, 1343], [115, 1284],
        [143, 1250], [144, 1216], [165, 1173], [188, 1144],
        [196, 1102], [218, 1079], [217, 1037], [208, 1012],
        [212, 953], [219, 925], [214, 899], [219, 881],
        [216, 855], [190, 815], [183, 774], [193, 743],
        [181, 720], [166, 702], [146, 690], [121, 660],
        [80, 649], [78, 619], [102, 576], [124, 524],
        [109, 493], [106, 478], [137, 483], [143, 449],
        [145, 387], [152, 333], [151, 286], [169, 224],
        [187, 173], [213, 130], [205, 106], [197, 84], [204, 61],
    ],
    "stormhaven-island": [
        [94, 1544], [119, 1558], [122, 1581], [116, 1605],
        [109, 1629], [111, 1651], [101, 1657], [86, 1641],
        [82, 1623], [79, 1607], [85, 1579],
    ],
    "deepwater-isle": [
        [195, 1716], [229, 1700], [256, 1681], [294, 1668],
        [344, 1665], [356, 1674], [342, 1686], [307, 1686],
        [290, 1693], [279, 1728], [283, 1755], [301, 1788],
        [333, 1809], [351, 1814], [382, 1817], [419, 1833],
        [452, 1842], [489, 1847], [520, 1848], [556, 1830],
        [584, 1797], [614, 1778], [648, 1783], [687, 1790],
        [707, 1784], [713, 1798], [686, 1821], [686, 1834],
        [696, 1853], [688, 1875], [666, 1879], [650, 1899],
        [615, 1895], [593, 1902], [565, 1912], [543, 1922],
        [515, 1927], [489, 1920], [471, 1931], [446, 1928],
        [429, 1941], [408, 1948], [384, 1930], [362, 1924],
        [341, 1917], [313, 1915], [298, 1900], [280, 1881],
        [263, 1845], [237, 1831], [213, 1815], [195, 1787],
        [193, 1750],
    ],
}

def audit(lower, preferred, upper, note):
    return {
        "status": "assistant_visual_review_with_interpretation_uncertainty",
        "reviewer": "Copilot image review; not an independent human ground truth",
        "lower_interpretation": lower,
        "preferred_count": preferred,
        "upper_interpretation": upper,
        "note": note,
    }


# These are single-reviewer visual roof-symbol tallies, NOT authoritative building
# identities. Ranges explicitly retain attached-roof/edge/label uncertainty.
# Final frame was frozen after segmentation and shoreline feasibility checks,
# before recording these tallies. No drawn cell was replaced or discarded.
MANUAL_AUDIT = {
    "x1280-y0640": audit(16, 19, 22, "Sandorim Street: roofs north of wall, west frontage and crescent block. Open circular wall platform excluded. Attached bends and north-edge centers are ambiguous."),
    "x1440-y4640": audit(16, 20, 23, "Eels Street/The Slide: two courtyard groups and lower detached roofs. Central U-shaped roof and tiny adjoining annexes cause interpretation spread; lower-edge roofs centered outside core excluded."),
    "x1760-y1920": audit(12, 14, 17, "Sulmor Street: four preferred upper-row symbols and ten around the lower courtyard. L-shaped roof wings are not automatically separate buildings; top/bottom edge centers remain uncertain."),
    "x2080-y4320": audit(19, 23, 25, "Soldiers Street: four upper symbols, nine flanking the diagonal lane, two on east frontage and eight in lower blocks. Lower-right U courtyard may combine several roof symbols."),
    "x2240-y4320": audit(23, 29, 35, "Simple's Street/Soothsayer's Way: dense rows with repeated small roofs. Preferred interpretation groups several L-shaped wings; plausible finer partitions and boundary symbols give upper tally."),
    "x2400-y2720": audit(22, 27, 30, "Curving lane: outer crescent, inner three-roof row, east frontage and lower diagonal row. Long curved connected groups have several roof subdivisions; edge halos inspected."),
    "x2400-y3840": audit(20, 24, 29, "Revorn Street/Whater's Alley: roofed wall tower included, open wall excluded. Dense angular courtyard and southern row have unresolved attached divisions."),
    "x2560-y0960": audit(26, 31, 37, "Shanty Lane: tightly packed Field Ward roofs above the inner wall. Small irregular attached glyphs make single-building divisions uncertain. Open circular wall platform excluded."),
    "x0960-y4800": audit(16, 18, 21, "Sea Lion Street/Sail Street: detached west plots, two street-front rows and six preferred waterfront-row symbols. Top-edge long roofs and annex splits remain uncertain. Pier excluded."),
    "x1440-y4960": audit(8, 9, 10, "Wharf: large four-faced central roof counted once, not four buildings; three northern small roofs, two northeast roofs, one east strip and two southern roofs. Dock platforms excluded."),
    "x1600-y6880": audit(0, 0, 0, "Deepwater Isle southern shoreline: cliff hatching, rocks and water, not roof structures. Roofed wall tower in top halo has its center outside the core."),
    "x1920-y2400": audit(13, 17, 20, "High Road: preferred eight east-frontage roofs, adjacent standalone rectangle, three northwest roofs, central L roof and four southwest roofs. Attached row seams and edge centers remain uncertain."),
    "x1920-y3680": audit(18, 21, 24, "Street of Bells: repeated small roof glyphs on both frontages, detached central L building and minor outbuildings. Machine regions merge long rows; small annexes give interpretation range."),
    "x2080-y1600": audit(10, 12, 15, "Ilzanta area: large stepped/L roofs each treated as one unless a separate outer outline is visible; small square courtyard roof included. Lower-edge L roof center uncertain."),
    "x2400-y3360": audit(3, 3, 4, "City of the Dead: one northern rectangular roof, one bent central roof and one roofed wall tower. Vegetation/plots excluded; bent plan could be two attached structures."),
    "x2880-y2560": audit(7, 8, 11, "The Passar near east wall: four preferred eastern row symbols, small detached roof, west U complex, lower hook complex and southeast roof. U/hook plans might contain additional structures."),
    "x1920-y2880": audit(12, 14, 18, "Great Drunkard label area: visible parts of roof rows surrounding courtyard and east frontage. Label hides edges; upper tally allows plausible subdivisions, not claimed hidden-building observations."),
    "x1920-y3200": audit(11, 13, 17, "Castle label/central street: six preferred west-frontage symbols, upper/right groups, central L/round-ended building and lower roof row. Lettering and edge roofs make some divisions unresolved."),
    "x2080-y0640": audit(13, 19, 25, "Northyard/Field Ward label: open yard excluded; irregular roof blocks south/east tallied from exposed outlines. Large translucent lettering makes this a particularly uncertain count."),
    "x2080-y4960": audit(14, 19, 24, "Three Daggers/Dock Ward lettering: exposed northern, middle-frontage and southern courtyard roofs. DOCK lettering conceals seams; range is interpretation sensitivity, not recovered hidden roofs."),
    "x2080-y5440": audit(23, 27, 31, "Keel Alley/Dar Alley: curved west frontage, east small-roof rows and southern freestanding symbols. Roof ridges not separately counted; adjoining footprints retain ambiguity."),
    "x2400-y1600": audit(14, 17, 20, "Brom area: upper diagonal/U group, two southwest rectangles, four preferred middle-right frontage roofs and eastern rectangle. Large U versus attached roofs and border centers uncertain."),
    "x2720-y1760": audit(12, 14, 17, "Angled/curved street blocks: seven preferred southwest crescent symbols, northeast row, isolated rectangle and one southern edge roof. Roof joins at bends remain ambiguous."),
    "x2720-y2560": audit(12, 16, 20, "The Passar: west upper/lower roof triplets, east courtyard group and southern roof row. Some contiguous courtyard roofs could form one U-shaped building."),
    "x0320-y4480": audit(0, 0, 0, "Coastal grass and cliff hatching. Roofed wall towers are outside the cyan core; terrain candidates rejected by visual review."),
    "x0480-y4800": audit(0, 1, 1, "Coastal circular red-capped structure centered inside southwest core counted provisionally; its symbol may instead be an open tower platform. Water/rocks excluded."),
    "x0640-y3840": audit(2, 2, 2, "Two clearly roofed square wall towers with centers inside the buffered city boundary; connecting wall and cliff hatching excluded."),
    "x1280-y6880": audit(0, 0, 0, "Island shoreline and water; brown offshore shape is a rock and lies below the core."),
    "x1440-y2560": audit(6, 7, 9, "Market edge: four preferred small roofs in west cluster and three in east cluster; open market/street excluded. Detector merges nearly the whole row into one region."),
    "x3200-y4800": audit(0, 0, 0, "Empty eastern slope with cliff hatching, not buildings; city boundary clips the core."),
    "x3200-y6080": audit(0, 0, 1, "Fortification edge: large gatehouse center lies to east outside core and small circular platform center below core. Upper sensitivity allows unresolved gatehouse-center placement."),
    "x3360-y5120": audit(0, 0, 0, "Eastern boundary slope: hatching and vegetation, no roof symbols in included portion."),
    "x1280-y4960": audit(0, 0, 0, "Harbor water and open timber piers; no roofed structures in included core."),
    "x1440-y7040": audit(0, 0, 0, "Southern island boundary, coastal ground and offshore rocks; no buildings."),
    "x1600-y6560": audit(0, 0, 0, "Water and north shore of Deepwater Isle; no roofs."),
    "x2880-y3680": audit(0, 0, 0, "East wall/slope: excluded outside-city reddish detail is not counted; no roof centered inside boundary and core."),
    "x3040-y4960": audit(0, 0, 0, "Empty ground east of inner city wall. Square tower at lower-left is centered below the cyan core."),
    "x3200-y5120": audit(0, 0, 0, "Empty eastern terrain and cliff edge, no roof symbols."),
    "x3200-y5600": audit(0, 0, 0, "Empty eastern terrain, no roof symbols."),
    "x3200-y6400": audit(0, 0, 0, "Southern shore/cliff and vegetation. No roof in city-boundary portion of core."),
}


def closed(points):
    return points + [points[0]] if points[-1] != points[0] else points


def boundaries():
    return {
        name: closed([[round(x * WIDTH / 981), round(y * HEIGHT / 2000)] for x, y in points])
        for name, points in BOUNDARY_TRACES.items()
    }


def boundary_mask(np, cv2):
    mask = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    for polygon in boundaries().values():
        cv2.fillPoly(mask, [np.array(polygon, dtype=np.int32)], 1)
    # Include roofed wall/gate structures whose centers straddle a wall trace.
    mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (65, 65)))
    return mask


def inclusion_features(mask, cv2):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    features = []
    for index, contour in enumerate(sorted(contours, key=cv2.contourArea, reverse=True), 1):
        points = cv2.approxPolyDP(contour, 1, True)[:, 0, :].tolist()
        features.append({"type": "Feature", "id": f"city-boundary-{index}",
                         "properties": {"status": "manually_traced_approximate",
                                        "wall_trace_buffer_px": 32},
                         "geometry": {"type": "Polygon", "coordinates": [closed(points)]}})
    return features


def detect(image, mask, np, cv2, green_limit=145):
    rgb = np.asarray(image).astype(np.int16)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    roof = ((r - g > 16) & (g - b > 5) & (g < green_limit)).astype(np.uint8)
    roof = cv2.morphologyEx(roof, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    roof = cv2.morphologyEx(roof, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    distance = cv2.distanceTransform(roof, cv2.DIST_L2, 5)
    smoothed = cv2.GaussianBlur(distance, (0, 0), 1.5)
    maxima = ((smoothed >= cv2.dilate(smoothed, np.ones((15, 15), np.uint8)) - 0.00001)
              & (smoothed >= 3.0)).astype(np.uint8)
    _, seeds = cv2.connectedComponents(maxima, 8)
    markers = seeds + 1
    markers[(roof != 0) & (seeds == 0)] = 0
    labels = cv2.watershed(cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR), markers)
    labels[roof == 0] = 1
    region_ids = np.unique(labels)
    accepted, rejected = [], {"too_small": 0, "too_large": 0, "outside_boundary": 0}
    # Scan label statistics in one vectorized pass; one full-image mask per
    # candidate would be quadratic in the number of roofs.
    flat = np.maximum(labels, 0).ravel()
    counts = np.bincount(flat)
    yy, xx = np.indices(labels.shape, dtype=np.int32)
    sum_x = np.bincount(flat, weights=xx.ravel())
    sum_y = np.bincount(flat, weights=yy.ravel())
    xmins = np.full(len(counts), WIDTH, dtype=np.int32)
    xmaxs = np.zeros(len(counts), dtype=np.int32)
    ymins = np.full(len(counts), HEIGHT, dtype=np.int32)
    ymaxs = np.zeros(len(counts), dtype=np.int32)
    np.minimum.at(xmins, flat, xx.ravel())
    np.maximum.at(xmaxs, flat, xx.ravel())
    np.minimum.at(ymins, flat, yy.ravel())
    np.maximum.at(ymaxs, flat, yy.ravel())
    for i in region_ids:
        if i < 2:
            continue
        x, y = int(xmins[i]), int(ymins[i])
        w, h, area = int(xmaxs[i] - x + 1), int(ymaxs[i] - y + 1), int(counts[i])
        cx, cy = sum_x[i] / area, sum_y[i] / area
        if not mask[min(HEIGHT - 1, int(cy)), min(WIDTH - 1, int(cx))]:
            rejected["outside_boundary"] += 1
            continue
        if area < 45 or w < 5 or h < 5:
            rejected["too_small"] += 1
            continue
        if area > 18000 or w > 500 or h > 500:
            rejected["too_large"] += 1
            continue
        local = (labels[y:y + h, x:x + w] == i).astype(np.uint8)
        contours, _ = cv2.findContours(local, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour = max(contours, key=cv2.contourArea)
        polygon = cv2.approxPolyDP(contour, 1.0, True)[:, 0, :]
        if len(polygon) < 3:
            rejected["too_small"] += 1
            continue
        points = closed([[int(a) + x, int(b) + y] for a, b in polygon])
        identity = hashlib.sha256(json.dumps(points, separators=(",", ":")).encode()).hexdigest()[:14]
        accepted.append({
            "type": "Feature",
            "id": f"wdhr-{identity}",
            "geometry": {"type": "Polygon", "coordinates": [points]},
            "properties": {
                "status": "automatic_unverified",
                "ward": None,
                "kind": "watershed_roof_candidate",
                "verified": False,
                "centroid_px": [round(float(cx), 3), round(float(cy), 3)],
                "bbox_px": [x, y, x + w, y + h],
                "segmented_area_px2": area,
                "footprint_sqft": None,
                "may_contain_multiple_structures": True,
            },
        })
    accepted.sort(key=lambda f: (f["properties"]["centroid_px"][1], f["properties"]["centroid_px"][0]))
    return accepted, rejected


def stratum_for(count):
    for name, maximum in (("zero", 0), ("sparse", 3), ("low", 8), ("medium", 14), ("high", 24)):
        if count <= maximum:
            return name
    return "very_high"


def sampling_frame(features, mask):
    cells = {}
    for y in range(0, HEIGHT, CELL):
        for x in range(0, WIDTH, CELL):
            pixels = int(mask[y:y + CELL, x:x + CELL].sum())
            if pixels:
                key = f"x{x:04d}-y{y:04d}"
                cells[key] = {"id": key, "bbox_px": [x, y, min(x + CELL, WIDTH), min(y + CELL, HEIGHT)],
                              "boundary_pixels": pixels, "candidate_count": 0}
    for feature in features:
        x, y = feature["properties"]["centroid_px"]
        key = f"x{int(x) // CELL * CELL:04d}-y{int(y) // CELL * CELL:04d}"
        cells[key]["candidate_count"] += 1
    groups = {}
    for cell in cells.values():
        cell["stratum"] = stratum_for(cell["candidate_count"])
        groups.setdefault(cell["stratum"], []).append(cell)
    rng = random.Random(SEED)
    strata = []
    for name, group in groups.items():
        group.sort(key=lambda c: c["id"])
        sample = rng.sample(group, min(SAMPLE_PER_STRATUM, len(group)))
        for cell in sample:
            cell["sampled"] = True
            cell["inclusion_probability"] = len(sample) / len(group)
            cell["manual"] = MANUAL_AUDIT.get(cell["id"])
        strata.append({"id": name, "population_cells": len(group), "sample_cells": len(sample),
                       "candidate_count": sum(c["candidate_count"] for c in group),
                       "sample_ids": [c["id"] for c in sample]})
    return list(cells.values()), strata


def render(image, report):
    from PIL import ImageDraw, ImageFont

    REVIEW.mkdir(exist_ok=True)
    font = ImageFont.truetype("arial.ttf", 20)
    selected = [cell for cell in report["sampling"]["frame"] if cell.get("sampled")]
    selected.sort(key=lambda c: (c["stratum"], c["id"]))
    expected = {f"{cell['id']}{suffix}.jpg" for cell in selected for suffix in ("", "-candidates")}
    for stale in REVIEW.glob("x*-y*.jpg"):
        if stale.name not in expected:
            stale.unlink()
    overview = image.copy()
    overview_draw = ImageDraw.Draw(overview)
    for feature in report["boundary_features"]["features"]:
        overview_draw.line([tuple(p) for p in feature["geometry"]["coordinates"][0]], fill="#00ff55", width=5)
    overview.resize((981, 2000)).save(REVIEW / "boundary-overview.jpg")
    overview.crop((750, 4650, 1700, 5250)).resize((1425, 900)).save(REVIEW / "boundary-harbor.jpg")
    for cell in report["sampling"]["frame"]:
        overview_draw.rectangle(cell["bbox_px"], outline="#ffcc00" if cell.get("sampled") else "#00aaff",
                                width=6 if cell.get("sampled") else 1)
    overview.resize((981, 2000)).save(REVIEW / "sampling-frame-overview.jpg")
    for cell in selected:
        x, y, x1, y1 = cell["bbox_px"]
        halo = 24
        crop = image.crop((x - halo, y - halo, x + CELL + halo, y + CELL + halo)).resize((624, 624))
        draw = ImageDraw.Draw(crop)
        draw.rectangle([72, 72, 551, 551], outline="#00ffff", width=2)
        for feature in report["boundary_features"]["features"]:
            polygon = feature["geometry"]["coordinates"][0]
            draw.line([((px - x + halo) * 3, (py - y + halo) * 3) for px, py in polygon],
                      fill="#00ff55", width=2)
        crop.save(REVIEW / f"{cell['id']}.jpg")
        overlay = crop.copy()
        odraw = ImageDraw.Draw(overlay)
        local_features = []
        for feature in report["features"]:
            cx, cy = feature["properties"]["centroid_px"]
            if x <= cx < x1 and y <= cy < y1:
                local_features.append(feature)
        for i, feature in enumerate(local_features, 1):
            coords = feature["geometry"]["coordinates"][0]
            odraw.line([((px - x + halo) * 3, (py - y + halo) * 3) for px, py in coords],
                       fill="#00ffff", width=1)
            cx, cy = feature["properties"]["centroid_px"]
            odraw.text(((cx - x + halo) * 3, (cy - y + halo) * 3), str(i), font=font,
                       fill="#ffffff", stroke_width=2, stroke_fill="#000000")
        overlay.save(REVIEW / f"{cell['id']}-candidates.jpg")
    for start in range(0, len(selected), 6):
        from PIL import Image
        sheet = Image.new("RGB", (1248, 1992), "white")
        draw = ImageDraw.Draw(sheet)
        for j, cell in enumerate(selected[start:start + 6]):
            xx, yy = (j % 2) * 624, (j // 2) * 664
            sheet.paste(Image.open(REVIEW / f"{cell['id']}.jpg"), (xx, yy + 40))
            draw.text((xx + 8, yy + 7), f"{start + j + 1}: {cell['id']} {cell['stratum']} C={cell['candidate_count']}",
                      fill="black", font=font)
        sheet.save(REVIEW / f"sample-sheet-{start // 6 + 1:02d}.jpg")


def rebuild(render_images=False):
    import cv2
    import numpy as np
    import PIL
    from PIL import Image
    sys.path.insert(0, str(ROOT))
    from faerun.hires_survey import estimate_from_sample

    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SHA256:
        raise ValueError("Map checksum mismatch: do not use truncated or changed imagery")
    image = Image.open(SOURCE).convert("RGB")
    if image.size != (WIDTH, HEIGHT):
        raise ValueError("Unexpected map dimensions")
    mask = boundary_mask(np, cv2)
    features, rejected = detect(image, mask, np, cv2)
    cells, strata = sampling_frame(features, mask)
    selected = [cell for cell in cells if cell.get("sampled")]
    if set(MANUAL_AUDIT) != {cell["id"] for cell in selected}:
        raise ValueError("Final seeded frame differs from the recorded visual audit")
    estimate = estimate_from_sample(cells, strata)
    sensitivity = []
    for limit in (135, 140, 145, 150, 155):
        variants = features if limit == 145 else detect(image, mask, np, cv2, limit)[0]
        sensitivity.append({"green_limit": limit, "candidate_count": len(variants)})
    boundary_features = inclusion_features(mask, cv2)
    report = {
        "schema_version": 2,
        "title": "Waterdeep high-resolution citywide roof survey",
        "reproduction": {
            "command": ".\\.venv\\Scripts\\python.exe tools\\survey_waterdeep_hires.py --rebuild --render",
            "check_command": ".\\.venv\\Scripts\\python.exe -S tools\\survey_waterdeep_hires.py --check",
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "estimator_module_sha256": hashlib.sha256((ROOT / "faerun" / "hires_survey.py").read_bytes()).hexdigest(),
            "analysis_versions": {"python": sys.version.split()[0], "opencv": cv2.__version__,
                                  "numpy": np.__version__, "pillow": PIL.__version__},
            "network_access": "None during analysis; image and derived artifacts remain local.",
        },
        "coordinate_system": {"name": "original_image_pixels", "origin": "top_left",
                              "x_direction": "right", "y_direction": "down", "not_lon_lat": True},
        "coordinate_space": {"width": WIDTH, "height": HEIGHT,
                             "units": "image_pixels", "origin": "top_left"},
        "source": {"path": "maps/waterdeep-map-hires.jpg", "sha256": SHA256,
                   "bytes": len(raw), "width_px": WIDTH, "height_px": HEIGHT,
                   "url": "https://www.worldanvil.com/uploads/maps/db75270b93ad2dee4f0d303aadeb0aaf.jpg",
                   "physical_scale_verified": False,
                   "survey_scope": "Whole mapped city including Field Ward, City of the Dead, Stormhaven Island and Deepwater Isle; excluding outlying farms."},
        "boundary": {"type": "MultiPolygon",
                     "coordinates": [feature["geometry"]["coordinates"] for feature in boundary_features]},
        "boundary_features": {"type": "FeatureCollection", "features": boundary_features},
        "coverage": {"machine_processed": {"complete": True, "image_pixels": WIDTH * HEIGHT,
                                          "boundary_pixels": int(mask.sum()), "frame_cells": len(cells)},
                     "manually_validated": {
                         "complete": False, "sample_complete": True,
                         "reviewer": "Copilot visual image review; not independent human validation",
                         "sample_cells": len(selected),
                         "sampled_frame_cell_fraction": len(selected) / len(cells),
                         "reviewed_boundary_pixels": sum(c["boundary_pixels"] for c in selected),
                         "reviewed_boundary_pixel_fraction": sum(c["boundary_pixels"] for c in selected) / int(mask.sum()),
                         "preferred_roof_symbol_tally": sum(c["manual"]["preferred_count"] for c in selected),
                         "individual_building_identities_verified": 0,
                     },
                     "complete_visual_building_enumeration": False},
        "detector": {"method": "RGB r-g>16, g-b>5, g<145; close 3x3 then open 2x2. Distance-transform maxima (Gaussian sigma1.5, 15x15 neighborhood, distance>=3) seed watershed on source imagery. Keep area>=45 and <=18000 pixels.",
                     "candidate_count": len(features), "rejected_regions": rejected,
                     "geometry_meaning": "Simplified largest exterior contour of each accepted watershed label, not a verified footprint. Internal holes and disconnected fragments are not detailed; segmented_area_px2 is raster-label area, not physical area.",
                     "threshold_sensitivity": sensitivity,
                     "sensitivity_is_confidence_interval": False,
                     "feasibility_checks": [
                         "Full-image connected colour components were inadequate (606 accepted regions at initial boundary); touching roof rows merged.",
                         "Distance-seeded watershed increased citywide spatial detail; 4835 candidates after the shoreline/wall inclusion correction.",
                         "Five colour thresholds were processed across the entire image. None is treated as ground truth or a confidence interval.",
                     ],
                     "boundary_rule": "Extract full image first; retain region when its segmented centroid is within the traced boundary."},
        "features": features,
        "sampling": {"design": "Stratified simple random sampling without replacement of 160x160 original-pixel area cells; strata fixed by citywide detector counts before visual review.",
                     "seed": SEED, "cell_size_px": CELL, "sample_per_stratum": SAMPLE_PER_STRATUM,
                     "inclusion_rule": "Count a depicted structure when the visual center of its roof outline lies inside the cyan half-open core [x0,x1) x [y0,y1) and city boundary; 24-pixel halo supplies edge context.",
                     "counting_unit": "Visibly depicted outer roof/structure glyph; distinguish discernible adjoining roof units, group roof faces and clearly continuous wings; include roofed defensive towers and tomb roofs, exclude open wall platforms, piers, trees, rocks and hatching.",
                     "audit_images": "maps/hires-survey-review/{cell_id}.jpg; original crop plus 24-pixel halo, displayed at 3x; cyan core, green city boundary.",
                     "count_ranges": "Single-assistant visual interpretation ranges, not verified lower/upper true-building bounds. All 40 drawn cells retained, including labels, empty land and ambiguous roofs.",
                     "selection_order": "Boundary/segmentation feasibility first, final seeded frame fixed second, visual tally recording last. No population target or occupancy parameter used.",
                     "strata": strata, "frame": cells},
        "estimate": estimate,
        "limitations": [
            "An automated colour region may represent one roof, multiple attached roofs, a roof fragment, or non-building ink. It is not a verified building.",
            "Map-symbol roof structures are a proxy for buildings, not cadastral units, households or inhabitants.",
            "The city boundary is a manual pixel trace, not a surveyed administrative boundary; outlying farms are excluded.",
            "No physical area is calculated: image scale has not been independently verified.",
            "Population assumptions and the baseline census are not used by this survey.",
            "Visual sample tallies are an AI assistant's single-reviewer interpretation, not independent human ground truth; attached roofs and obscuring labels remain unresolved.",
            "The sampling interval measures probability-sampling error conditional on the preferred visible-roof interpretation. It excludes map omissions, hidden roofs, observer bias and boundary error.",
            "Interpretation sensitivity is a scenario range, not a confidence interval or rigorous bound on actual buildings.",
            "Candidate count agreement is assessed through area-cell count residuals; feature-level precision/recall and a complete manual citywide building list have not been established.",
        ],
    }
    report["summary"] = {
        "candidate_count": len(features),
        "estimated_depicted_roof_structures": estimate["rounded_estimate"],
        "sampling_interval": estimate["sampling_interval"],
        "interpretation_sensitivity": estimate["interpretation_sensitivity"],
        "sample_cells_reviewed": len(selected),
        "frame_cells": len(cells),
        "complete_visual_enumeration": False,
        "population_estimate": None,
    }
    sample_features = []
    for cell in selected:
        x0, y0, x1, y1 = cell["bbox_px"]
        sample_features.append({
            "type": "Feature", "id": cell["id"],
            "geometry": {"type": "Polygon", "coordinates": [
                closed([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
            ]},
            "properties": {
                "status": "visually_reviewed_sample_not_verified_building_inventory",
                "stratum": cell["stratum"],
                "candidate_count": cell["candidate_count"],
                **cell["manual"],
            },
        })
    report["sampling"]["features"] = {"type": "FeatureCollection", "features": sample_features}
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(report, separators=(",", ":")) + "\n", encoding="utf-8")
    if render_images:
        render(image, report)
    print(json.dumps({"candidates": len(features), "cells": len(cells), "estimate": estimate,
                      "sensitivity": sensitivity}, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.rebuild:
        rebuild(args.render)
    elif args.check:
        sys.path.insert(0, str(ROOT))
        from faerun.hires_survey import estimate_from_sample, waterdeep_hires_report

        report = waterdeep_hires_report()
        if report["source"]["sha256"] != hashlib.sha256(SOURCE.read_bytes()).hexdigest():
            raise ValueError("Source map checksum mismatch")
        if report["reproduction"]["script_sha256"] != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
            raise ValueError("Analysis script changed: rebuild the survey")
        module_hash = hashlib.sha256((ROOT / "faerun" / "hires_survey.py").read_bytes()).hexdigest()
        if report["reproduction"]["estimator_module_sha256"] != module_hash:
            raise ValueError("Estimator module changed: rebuild the survey")
        cells = report["sampling"]["frame"]
        if sum(c["candidate_count"] for c in cells) != report["detector"]["candidate_count"]:
            raise ValueError("Area frame does not account for every candidate")
        calculated = estimate_from_sample(cells, report["sampling"]["strata"])
        if calculated != report["estimate"]:
            raise ValueError("Persisted estimate does not match the sample audit")
        print("Map checksum, stable candidate inventory, complete area frame and sample estimator checked.")
    else:
        parser.error("Choose --rebuild or --check")


if __name__ == "__main__":
    main()
