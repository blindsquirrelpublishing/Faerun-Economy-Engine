"""Reproduce a deliberately PARTIAL survey of the local City System scans.

No image libraries are imported by the application or by --check. Reproduction
requires PyMuPDF, Pillow, numpy and OpenCV in the analysis environment only.
Nothing is downloaded, and the source is never sent to a remote service.

Example (from the project directory):
  .\\.venv\\Scripts\\python.exe tools\\survey_waterdeep.py --rebuild --render
  .\\.venv\\Scripts\\python.exe tools\\survey_waterdeep.py --check

The observations below trace depicted roof outlines, not rooms, roof faces,
households, named landmarks, or connected ink components. They are intentionally
not extrapolated to a city total. See the generated inventory's limitations.

Application contract: buildings[] contains id, status ("verified"), ward,
footprint_sqft, class, footprint_area_px2 and source {pdf_page, sheet, bbox_px,
polygon_px}. Unknown physical measurements/classifications are null, never zero.
complete/deduplicated describe citywide readiness; the selected subset has its
own explicit deduplication flag under coverage.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "volo" / "tsr01040 - AD&D_FR_-_City_System.pdf"
OUTPUT = ROOT / "faerun" / "data" / "waterdeep_buildings.json"
SOURCE_SHA256 = "5e83e5b9ce306aff6d9252427c68a0211439199a16e26a07dcf06aa43b27f82d"
THRESHOLDS = (134, 138, 140, 142, 146)
WARD_EVIDENCE = {
    "city-dead-enclosure": {
        "ward": "city_of_the_dead",
        "building_class": "A",
        "status": "verified_for_selected_interior_roofs_only",
        "boundary": "Visible cemetery wall separates the selected interior roofs from Samarin's Street/Beaconmarch and surrounding street blocks.",
        "citations": [
            {"pdf_page": 4, "printed_page": 3, "basis": "City of the Dead is the only walled ward."},
            {"pdf_page": 91, "map_sheet": 8, "basis": "Visible enclosure and numbered sites 165, 166 and 167."},
            {"pdf_page": 13, "printed_page": 12, "basis": "165 Merchant's Rest (tomb), 166 Ahghairon's Statue (monument), 167 House of the Homeless (tomb for the poor)."},
            {"pdf_page": 11, "printed_page": 10, "basis": "City of the Dead consists entirely of Class A buildings."},
        ],
        "occupancy": "Not supplied by the map or these citations. Tombs are not assigned living residents or zero occupancy.",
    },
}


def rectangle(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


# Integer coordinates are local to each crop, on the ORIGINAL embedded raster.
# A roof ridge is not a footprint boundary. Irregular/attached forms that cannot
# be confidently resolved are kept separately rather than forced into a count.
PATCHES = [
    {
        "id": "lamp-street-north",
        "pdf_page": 53,
        "sheet": 3,
        "bbox_px": [405, 10, 552, 145],
        "context": "Whole small block immediately north of Lamp Street.",
        "ward_hint": "Castle Ward",
        "ward_basis": "Magenta city area near Piergeiron's Palace, sheet 3; no surveyed ward boundary.",
        "complete_roof_review": True,
        "footprints": [
            [[17, 30], [45, 27], [47, 50], [20, 53]],
            rectangle(48, 29, 59, 47),
            [[61, 27], [72, 25], [74, 52], [62, 53]],
            [[75, 25], [86, 24], [87, 59], [75, 60]],
            rectangle(89, 24, 99, 42),
            [[100, 23], [122, 22], [123, 37], [100, 39]],
            [[90, 43], [100, 43], [100, 39], [124, 38], [124, 57], [90, 59]],
            rectangle(100, 61, 123, 79),
            [[99, 81], [125, 80], [126, 100], [99, 102]],
            [[99, 104], [125, 103], [126, 123], [99, 124]],
            [[84, 96], [95, 98], [96, 124], [84, 125]],
            rectangle(68, 91, 80, 125),
            rectangle(59, 80, 80, 90),
            [[31, 54], [47, 54], [49, 88], [31, 90]],
            [[35, 90], [51, 90], [51, 104], [36, 105]],
            [[30, 106], [56, 104], [57, 124], [31, 126]],
        ],
        "unresolved_groups": [],
        "review_note": (
            "16 separately outlined roof glyphs reviewed at 4x enlargement; "
            "central ridges and hatch marks are not additional buildings. "
            "Polygon edges are approximate, generally within two native pixels."
        ),
    },
    {
        "id": "wrightstone-sul-shield",
        "pdf_page": 73,
        "sheet": 5,
        "bbox_px": [320, 350, 510, 542],
        "context": "Block south of Wrightstone Street, between Sul Street and Shield Street.",
        "ward_hint": "Sea Ward",
        "ward_basis": "Yellow northwestern city area east of Raventree (96), sheet 5; no surveyed ward boundary.",
        "complete_roof_review": False,
        "footprints": [
            rectangle(20, 20, 38, 57),
            rectangle(20, 58, 38, 85),
            rectangle(54, 17, 89, 45),
            rectangle(55, 47, 69, 57),
            rectangle(92, 17, 110, 50),
            rectangle(124, 19, 137, 44),
            rectangle(141, 17, 170, 40),
            rectangle(143, 42, 171, 59),
            rectangle(133, 63, 172, 81),
            rectangle(143, 85, 172, 100),
            rectangle(139, 104, 173, 121),
            rectangle(143, 123, 173, 140),
            rectangle(143, 143, 169, 179),
            rectangle(124, 163, 138, 179),
            rectangle(19, 127, 37, 180),
            rectangle(20, 103, 54, 124),
            rectangle(18, 89, 42, 101),
            rectangle(50, 64, 66, 84),
            rectangle(76, 64, 122, 93),
        ],
        "unresolved_groups": [
            {
                "polygon": [[69, 94], [122, 94], [122, 119], [105, 120], [105, 111], [87, 111], [87, 132], [69, 132]],
                "reason": "U/attached plan: subdivision between roof wings is unclear.",
            },
            {
                "polygon": [[104, 132], [121, 152], [122, 180], [111, 180], [111, 157], [95, 141]],
                "reason": "Angled-to-straight attached roof: bend may divide structures.",
            },
            {
                "polygon": [[51, 151], [80, 151], [80, 163], [91, 163], [92, 179], [51, 179]],
                "reason": "Stepped adjoining roofs: shared ridge versus two footprints unresolved.",
            },
        ],
        "review_note": (
            "19 confidently separated map roof glyphs and three unresolved roof "
            "groups. No exact block total or recall denominator is asserted."
        ),
    },
    {
        "id": "net-eel-pelnimbars",
        "pdf_page": 45,
        "sheet": 2,
        "bbox_px": [210, 310, 378, 480],
        "context": "Block between Net Street and Eel Street, south of Lackpurse Lane and north of Pelnimbar's Street; north of Dock Street and the Great Harbor.",
        "ward_hint": "Dock Ward",
        "ward_basis": "Harbor-side position on sheet 2, near numbered Dhalmass Warehouse (281; printed13/PDF14). Color alone is not a verified ward boundary.",
        "complete_roof_review": False,
        "footprints": [
            [[12, 10], [39, 9], [39, 27], [11, 26]],
            rectangle(10, 29, 40, 51),
            rectangle(10, 53, 32, 62),
            rectangle(10, 65, 38, 78),
            rectangle(10, 79, 30, 90),
            rectangle(10, 92, 47, 106),
            rectangle(10, 114, 48, 129),
            [[9, 139], [50, 135], [51, 150], [9, 154]],
            rectangle(53, 9, 83, 31),
            rectangle(52, 37, 74, 52),
            rectangle(53, 54, 81, 69),
            rectangle(54, 70, 76, 80),
            rectangle(55, 81, 75, 100),
            rectangle(78, 86, 98, 99),
            rectangle(92, 6, 112, 55),
            rectangle(115, 7, 129, 34),
            rectangle(136, 8, 157, 40),
            rectangle(131, 46, 158, 61),
            rectangle(131, 63, 158, 84),
            rectangle(127, 91, 155, 107),
            rectangle(138, 110, 155, 117),
            [[141, 125], [153, 122], [153, 145], [140, 150]],
            [[123, 128], [137, 128], [137, 152], [123, 153]],
            [[111, 133], [120, 134], [116, 153], [107, 154]],
            rectangle(79, 141, 105, 153),
            [[60, 112], [78, 115], [77, 153], [59, 152]],
        ],
        "unresolved_groups": [
            {
                "polygon": [[93, 104], [102, 97], [101, 72], [120, 71], [121, 109], [94, 109]],
                "reason": "L-shaped roof with a low wing: one footprint versus attached structures is unresolved.",
            },
        ],
        "review_note": "26 separate roof outlines. Enlarged second review merged two pairs of roof faces at internal ridges. Circular courtyard feature and street lettering excluded; the attached L-shaped group is not counted. No complete block count asserted.",
    },
    {
        "id": "lamp-street-south",
        "pdf_page": 53,
        "sheet": 3,
        "bbox_px": [425, 140, 565, 352],
        "context": "Block immediately south of Lamp Street, west of the Street of the Sword; distinct from the retained north-of-Lamp block.",
        "ward_hint": "Castle Ward",
        "ward_basis": "Same street-labelled sheet 3 neighborhood as the earlier Lamp Street patch; boundary confirmation remains pending.",
        "complete_roof_review": False,
        "footprints": [
            [[17, 13], [54, 10], [55, 29], [19, 33]],
            rectangle(28, 35, 53, 43),
            rectangle(27, 45, 54, 58),
            rectangle(25, 61, 53, 68),
            rectangle(39, 69, 51, 92),
            rectangle(28, 94, 54, 113),
            [[28, 114], [55, 113], [56, 132], [29, 135]],
            rectangle(12, 140, 53, 160),
            rectangle(67, 20, 80, 34),
            [[64, 73], [79, 72], [80, 102], [65, 104]],
            [[62, 134], [80, 131], [85, 166], [67, 171]],
            rectangle(84, 12, 111, 29),
            rectangle(83, 31, 113, 53),
            [[84, 54], [115, 53], [116, 70], [85, 71]],
            rectangle(85, 73, 116, 89),
            rectangle(88, 91, 119, 101),
            [[90, 105], [116, 102], [119, 122], [92, 125]],
            rectangle(92, 126, 120, 141),
            rectangle(95, 146, 126, 156),
            rectangle(106, 160, 130, 174),
            rectangle(105, 180, 133, 190),
            [[95, 169], [103, 168], [104, 192], [96, 196]],
            [[80, 180], [94, 178], [95, 196], [81, 199]],
            [[63, 181], [77, 179], [79, 199], [64, 201]],
            [[42, 179], [54, 176], [58, 201], [44, 203]],
            [[14, 182], [38, 180], [39, 204], [15, 206]],
        ],
        "unresolved_groups": [],
        "review_note": "26 separately outlined roofs; enlarged second review merged two roof faces at an internal ridge and corrected incomplete edges. Untraced courtyard pixels remain excluded. The street gap separates this patch from the original north-of-Lamp observations even where the rectangular crop masks overlap.",
    },
    {
        "id": "heroes-garden-favenbar",
        "pdf_page": 73,
        "sheet": 5,
        "bbox_px": [370, 65, 554, 248],
        "context": "Block east of the Favenbar and Heroes' Garden, north of Wrightstone Street. Not the earlier block south of Wrightstone Street.",
        "ward_hint": "Sea Ward",
        "ward_basis": "Northern sheet 5 street geometry near Heroes' Garden, distinct from the Raventree (96) sample. Ward coloring is contextual, not a boundary survey.",
        "complete_roof_review": False,
        "footprints": [
            [[70, 7], [95, 16], [88, 41], [60, 38]],
            [[97, 18], [119, 24], [109, 55], [90, 48]],
            [[122, 26], [140, 33], [130, 59], [112, 54]],
            [[142, 36], [158, 39], [155, 65], [138, 64]],
            rectangle(160, 39, 174, 64),
            [[61, 48], [80, 58], [73, 70], [56, 63]],
            [[54, 65], [72, 72], [68, 86], [48, 78]],
            [[46, 80], [68, 90], [63, 101], [41, 93]],
            rectangle(9, 152, 27, 178),
            rectangle(28, 157, 41, 178),
            rectangle(44, 163, 58, 178),
            rectangle(71, 160, 84, 178),
            rectangle(86, 145, 99, 178),
            rectangle(102, 155, 119, 178),
            rectangle(121, 141, 138, 173),
            rectangle(121, 127, 139, 139),
            rectangle(153, 111, 176, 123),
            rectangle(162, 91, 176, 109),
            rectangle(161, 72, 177, 87),
            rectangle(144, 74, 151, 96),
            rectangle(118, 73, 140, 96),
            [[91, 65], [116, 77], [110, 88], [87, 78]],
            [[84, 88], [102, 94], [99, 103], [81, 97]],
            [[104, 100], [137, 111], [132, 127], [99, 115]],
        ],
        "unresolved_groups": [
            {
                "polygon": [[37, 96], [55, 104], [49, 139], [37, 150], [17, 139]],
                "reason": "Oblique lower Favenbar roof row: blurred eaves/ridges do not confidently resolve its subdivisions.",
            },
        ],
        "review_note": "24 separately outlined roofs. Three initially traced shapes were demoted together to an unresolved roof group during enlarged re-review. Trees, the circular courtyard feature and roofs west of the Favenbar are excluded. No exhaustive block count.",
    },
    {
        "id": "saerdoun-trollwall",
        "pdf_page": 99,
        "sheet": 9,
        "bbox_px": [340, 320, 505, 482],
        "context": "Unnumbered block southeast of Saerdoun Street, near Lion Street and Trollwall March; east of Stormweather (149).",
        "ward_hint": "North Ward",
        "ward_basis": "Sheet 9 northern inland neighborhood near Stormweather (149), Gralhund (152), the Raging Lion (153), and North Trollwall. No inferred boundary from blue ink.",
        "complete_roof_review": False,
        "footprints": [
            [[46, 22], [58, 27], [49, 48], [37, 41]],
            [[61, 14], [78, 14], [77, 42], [62, 43]],
            [[85, 19], [98, 23], [89, 43], [80, 42]],
            [[107, 29], [116, 34], [98, 59], [86, 55]],
            [[117, 40], [128, 47], [110, 72], [100, 65]],
            [[128, 50], [139, 58], [123, 80], [113, 74]],
            [[145, 61], [154, 71], [139, 83], [129, 76]],
            [[153, 75], [162, 87], [148, 95], [138, 88]],
            rectangle(123, 96, 153, 113),
            rectangle(124, 115, 145, 122),
            rectangle(121, 125, 144, 132),
            rectangle(113, 135, 145, 153),
            rectangle(71, 121, 99, 155),
            rectangle(7, 121, 29, 156),
            rectangle(32, 122, 51, 155),
            rectangle(53, 133, 60, 155),
            rectangle(10, 90, 51, 119),
            [[17, 65], [43, 77], [40, 88], [11, 76]],
            [[30, 43], [60, 59], [54, 75], [23, 58]],
        ],
        "unresolved_groups": [],
        "review_note": "19 selected roof outlines in a blue inland block. Enlarged second review merged two faces of one southern roof and corrected its neighbor's exterior edge. Central trees and untraced courtyard pixels excluded; this is not a representative North Ward sample.",
    },
    {
        "id": "city-dead-north-enclosure",
        "pdf_page": 91,
        "sheet": 8,
        "bbox_px": [245, 42, 605, 652],
        "context": "Selected isolated roofs inside the cemetery wall south of Samarin's Street and Beaconmarch; the sheet also depicts numbered tombs 165/167 and Ahghairon's Statue (166).",
        "ward_hint": "City of the Dead",
        "ward": "city_of_the_dead",
        "building_class": "A",
        "ward_basis": "Printed3/PDF4 identifies City of the Dead as the only walled ward; sheet8/PDF91 shows this enclosed tomb landscape and labels 165-167, identified as tombs/monument on printed12/PDF13.",
        "ward_evidence_id": "city-dead-enclosure",
        "complete_roof_review": False,
        "footprints": [
            [[193, 14], [222, 12], [224, 29], [192, 32]],
            [[252, 15], [266, 21], [254, 42], [240, 36]],
            [[101, 89], [127, 92], [125, 113], [100, 110]],
            [[146, 87], [173, 79], [187, 122], [159, 132]],
            [[259, 109], [280, 101], [287, 114], [267, 123]],
            [[318, 123], [335, 144], [324, 151], [310, 133]],
            rectangle(259, 156, 291, 173),
            [[87, 183], [112, 176], [119, 199], [94, 206]],
            [[124, 187], [140, 175], [158, 192], [140, 210]],
            [[17, 221], [40, 221], [41, 237], [17, 237]],
            [[81, 226], [105, 231], [102, 247], [80, 242]],
            [[187, 210], [226, 204], [230, 233], [191, 239]],
            rectangle(269, 201, 300, 229),
            [[325, 181], [342, 171], [357, 199], [340, 209]],
            [[143, 229], [194, 264], [175, 291], [121, 257]],
            [[26, 317], [55, 295], [81, 333], [53, 355]],
            [[119, 332], [141, 347], [126, 365], [104, 349]],
            [[262, 303], [300, 300], [301, 328], [262, 332]],
            [[70, 377], [99, 399], [55, 454], [29, 432]],
            [[205, 381], [229, 387], [227, 400], [204, 397]],
            [[324, 352], [342, 373], [328, 382], [309, 361]],
            [[241, 408], [266, 429], [251, 447], [226, 426]],
            [[285, 428], [311, 420], [321, 454], [295, 463]],
            [[109, 521], [133, 537], [114, 563], [92, 544]],
            [[166, 542], [200, 529], [219, 583], [184, 598]],
            rectangle(323, 520, 348, 537),
        ],
        "unresolved_groups": [],
        "review_note": "26 selected isolated roof glyphs reviewed inside the wall. Numbered white tomb masks, statue marks, the circular/apsidal stone symbol and turreted paved-looking plan were not counted as roofs. All cemetery roof classes are A per printed10/PDF11; occupancy remains unknown, not zero.",
    },
]


def area(polygon):
    return abs(sum(
        x0 * y1 - x1 * y0
        for (x0, y0), (x1, y1) in zip(polygon, polygon[1:] + polygon[:1])
    )) / 2


def bounds(polygon):
    xs, ys = zip(*polygon)
    return [min(xs), min(ys), max(xs), max(ys)]


def translate(polygon, dx, dy):
    return [[x + dx, y + dy] for x, y in polygon]


def reviewed_patch_area(patches):
    """Union rectangular review masks per native page, not across map overlaps."""
    total = 0
    for page in {patch["pdf_page"] for patch in patches}:
        boxes = [patch["bbox_px"] for patch in patches if patch["pdf_page"] == page]
        xs = sorted({x for box in boxes for x in (box[0], box[2])})
        for left, right in zip(xs, xs[1:]):
            intervals = sorted((y0, y1) for x0, y0, x1, y1 in boxes if x0 < right and x1 > left)
            end = -math.inf
            for bottom, top in intervals:
                total += (right - left) * max(0, top - max(bottom, end))
                end = max(end, top)
    return total


def polygons_overlap(first, second):
    """Detect positive-area overlap; a shared boundary alone is not duplication."""
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def inside(point, polygon):
        x, y = point
        result = False
        for a, b in zip(polygon, polygon[1:] + polygon[:1]):
            if cross(a, b, point) == 0 and min(a[0], b[0]) <= x <= max(a[0], b[0]) and min(a[1], b[1]) <= y <= max(a[1], b[1]):
                return False
            if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
                result = not result
        return result

    for a, b in zip(first, first[1:] + first[:1]):
        for c, d in zip(second, second[1:] + second[:1]):
            if cross(a, b, c) * cross(a, b, d) < 0 and cross(c, d, a) * cross(c, d, b) < 0:
                return True
    for polygon, other in ((first, second), (second, first)):
        probes = polygon + [[(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
                            for a, b in zip(polygon, polygon[1:] + polygon[:1])]
        if any(inside(point, other) for point in probes):
            return True
    return {tuple(p) for p in first} == {tuple(p) for p in second}


def sheet_page(sheet, row, column):
    if not (1 <= sheet <= 10 and 0 <= row < 2 and 0 <= column < 4):
        raise ValueError("Only the ten city sheets and their 2 x 4 tiles are admissible")
    return 34 + (sheet - 1) * 8 + row * 4 + column


def detect_patch(rgb, threshold):
    """Diagnostic components, explicitly NOT a building-count algorithm."""
    import cv2
    import numpy as np

    blurred = cv2.GaussianBlur(rgb, (5, 5), 0)
    mask = np.uint8(
        (blurred[:, :, 0] > threshold)
        & (blurred[:, :, 1] < 100)
        & (blurred[:, :, 2] > 60)
    ) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    candidates, rejected_large = [], []
    for label in range(1, count):
        x, y, width, height, pixels = (int(v) for v in stats[label])
        component = {
            "component_label": label,
            "bbox_px": [x, y, x + width, y + height],
            "component_area_px2": pixels,
        }
        if 35 < pixels < 1200 and width >= 4 and height >= 4:
            candidates.append(component)
        elif pixels >= 1200:
            rejected_large.append(component)
    return labels, candidates, rejected_large


def evaluate_candidates(labels, candidates, polygons):
    """Associate components by overlap; do not turn matches into verified roofs."""
    import numpy as np
    from PIL import Image, ImageDraw

    masks = []
    for polygon in polygons:
        image = Image.new("1", (labels.shape[1], labels.shape[0]))
        ImageDraw.Draw(image).polygon([tuple(p) for p in polygon], fill=1)
        masks.append(np.array(image, dtype=bool))
    roof_hits = [0] * len(masks)
    for candidate in candidates:
        component = labels == candidate["component_label"]
        hits = []
        for index, mask in enumerate(masks):
            overlap = int(np.count_nonzero(mask & component))
            if overlap >= max(8, .1 * int(mask.sum())):
                hits.append(index + 1)
                roof_hits[index] += 1
        candidate["overlapping_manual_roofs"] = hits
    return {
        "candidate_count": len(candidates),
        "manual_roof_count": len(polygons),
        "missed_manual_roofs": sum(hit == 0 for hit in roof_hits),
        "split_manual_roofs": sum(hit > 1 for hit in roof_hits),
        "merged_candidates": sum(len(c["overlapping_manual_roofs"]) > 1 for c in candidates),
        "false_candidates": sum(not c["overlapping_manual_roofs"] for c in candidates),
        "one_to_one_candidates": sum(
            len(c["overlapping_manual_roofs"]) == 1
            and roof_hits[c["overlapping_manual_roofs"][0] - 1] == 1
            for c in candidates
        ),
    }


def extract_native(doc, page_number):
    from io import BytesIO
    from PIL import Image

    images = doc[page_number - 1].get_images(full=True)
    if len(images) != 1:
        raise ValueError(f"Expected one embedded raster on PDF page {page_number}")
    return Image.open(BytesIO(doc.extract_image(images[0][0])["image"])).convert("RGB")


def add_model_contract(payload):
    """Project reviewed evidence into a small, explicit population-model interface."""
    payload["schema_version"] = 2
    payload["complete"] = False
    payload["deduplicated"] = False
    payload["readiness_scope"] = "citywide; selected-subset deduplication is reported separately"
    payload["source"]["physical_scale_verified"] = False
    payload["buildings"] = [
        {
            "id": observation["id"],
            "status": "verified",
            "ward": observation["ward"],
            "footprint_sqft": observation["area_sqft"],
            "class": observation["building_class"],
            "footprint_area_px2": observation["area_px2"],
            "source": {
                "patch_id": observation["patch_id"],
                "pdf_page": observation["pdf_page"],
                "sheet": observation["sheet"],
                "bbox_px": observation["bbox_px"],
                "polygon_px": observation["polygon_px"],
                "coordinate_system": "native embedded raster pixels, top-left origin",
                "ward_evidence_id": observation.get("ward_evidence_id"),
            },
            "verification_scope": "Visually reviewed depicted roof outline, not certified structure/residence/foundation area.",
        }
        for observation in payload["observations"]
    ]
    payload["coverage"].update(
        selected_subset_deduplicated=True,
        verified_building_count=len(payload["buildings"]),
        candidate_building_count=0,
        physically_scaled_building_count=0,
        verified_footprint_sqft=None,
        model_contract_note=(
            "buildings contains reviewed roof outlines only. Rejected image components "
            "remain in diagnostic_candidates and are not promoted to candidate buildings. "
            "Null metric area means unknown, not zero floor space or zero residents."
        ),
        ward_assigned_building_count=sum(b["ward"] is not None for b in payload["buildings"]),
        individually_classified_building_count=sum(b["class"] is not None for b in payload["buildings"]),
        class_a_building_count=sum(b["class"] == "A" for b in payload["buildings"]),
    )
    return payload


def registration_audit(doc):
    """Attempt local feature registration, retaining failures rather than a mosaic."""
    import cv2
    import numpy as np
    from PIL import Image

    sift = cv2.SIFT_create(nfeatures=25000)
    descriptors = {}
    for sheet in range(1, 11):
        canvas = Image.new("RGB", (2400, 1560), "white")
        for row in range(2):
            for column in range(4):
                image = extract_native(doc, sheet_page(sheet, row, column))
                canvas.paste(image.resize((600, 780)), (600 * column, 780 * row))
        gray = cv2.cvtColor(np.array(canvas), cv2.COLOR_RGB2GRAY)
        mask = np.zeros(gray.shape, np.uint8)
        mask[25:1530, 25:2370] = 255
        descriptors[sheet] = sift.detectAndCompute(gray, mask)
    pairs = ([(s, s + 1) for s in range(1, 5)]
             + [(s, s + 1) for s in range(6, 10)]
             + [(s, s + 5) for s in range(1, 6)])
    matcher, trials = cv2.BFMatcher(), []
    cv2.setRNGSeed(0)
    for first, second in pairs:
        keys_a, desc_a = descriptors[first]
        keys_b, desc_b = descriptors[second]
        good = []
        for match, other in matcher.knnMatch(desc_a, desc_b, k=2):
            if match.distance >= .8 * other.distance:
                continue
            xa, ya = keys_a[match.queryIdx].pt
            xb, yb = keys_b[match.trainIdx].pt
            dx, dy = xb - xa, yb - ya
            if second == first + 1 and abs(dx) < 150 and 1200 < dy < 1540:
                good.append(match)
            elif second == first + 5 and -2380 < dx < -1900 and abs(dy) < 150:
                good.append(match)
        trial = {
            "from_sheet": first, "to_sheet": second, "plausible_matches": len(good),
            "accepted": False, "reason": "No independent street/landmark control-point validation; repeated roof glyphs can mimic matches.",
        }
        if len(good) >= 4:
            pa = np.float32([keys_a[m.queryIdx].pt for m in good])
            pb = np.float32([keys_b[m.trainIdx].pt for m in good])
            matrix, mask = cv2.estimateAffinePartial2D(
                pa, pb, method=cv2.RANSAC, ransacReprojThreshold=5, maxIters=10000,
            )
            if matrix is not None:
                errors = np.linalg.norm(cv2.transform(pa[:, None], matrix)[:, 0] - pb, axis=1)
                trial.update(
                    inliers=int(mask.sum()), matrix=matrix.tolist(),
                    median_inlier_error_px=float(np.median(errors[mask[:, 0] > 0])),
                    fitted_scale=float(math.hypot(matrix[0, 0], matrix[0, 1])),
                )
        trials.append(trial)
    return {
        "sift_max_features": 25000, "lowe_ratio": .8, "ransac_tolerance_px": 5,
        "max_iterations": 10000, "accepted_transform_count": 0, "trials": trials,
        "warning": "Small fitted residuals do not establish cartographic correspondence.",
    }


def make_inventory(source, artifacts, render=False, audit_registration=False):
    import cv2
    import numpy as np
    import PIL
    import pymupdf
    from PIL import Image, ImageDraw

    artifacts.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_hash != SOURCE_SHA256:
        raise ValueError("Source digest differs: the stored manual coordinates must be re-surveyed")
    doc = pymupdf.open(source)
    if len(doc) != 130:
        raise ValueError("This survey is pinned to the 130-page user-provided PDF")
    sheets = []
    for sheet in range(1, 11):
        tiles = []
        canvas = Image.new("RGB", (2400, 1560), "white") if render else None
        for row in range(2):
            for column in range(4):
                page = sheet_page(sheet, row, column)
                image = extract_native(doc, page)
                tiles.append({
                    "pdf_page": page, "row": row, "column": column,
                    "native_size_px": list(image.size),
                    "preview_bbox_px": [column * 600, row * 780, (column + 1) * 600, (row + 1) * 780],
                })
                if canvas is not None:
                    canvas.paste(image.resize((600, 780)), (column * 600, row * 780))
        if canvas is not None:
            canvas.save(artifacts / f"sheet-{sheet:02}.png")
        sheets.append({
            "sheet": sheet, "tiles": tiles,
            "source_layout_column": (sheet - 1) % 5,
            "source_layout_row": (sheet - 1) // 5,
            "layout_reference": "PDF4, printed3, Waterdeep at a Glance",
            "review_status": "partial" if any(p["sheet"] == sheet for p in PATCHES) else "not_surveyed",
            "city_building_total": None,
        })

    observations, unresolved, patches = [], [], []
    for definition in PATCHES:
        patch = {key: value for key, value in definition.items() if key not in ("footprints", "unresolved_groups")}
        x0, y0, x1, y1 = patch["bbox_px"]
        patch["reviewed_area_px2"] = (x1 - x0) * (y1 - y0)
        patch["coordinate_system"] = "native embedded raster; origin top-left; x right, y down"
        patch["verified_map_footprint_count"] = len(definition["footprints"])
        patch["unresolved_group_count"] = len(definition["unresolved_groups"])
        patch["mask_policy"] = "Only listed footprint polygons are accepted; all other pixels excluded from inventory."
        image = extract_native(doc, patch["pdf_page"]).crop((x0, y0, x1, y1))
        overlay = image.resize(((x1 - x0) * 4, (y1 - y0) * 4))
        draw = ImageDraw.Draw(overlay)
        for index, local in enumerate(definition["footprints"], 1):
            polygon = translate(local, x0, y0)
            observations.append({
                "id": f"{patch['id']}-{index:02}",
                "patch_id": patch["id"], "pdf_page": patch["pdf_page"], "sheet": patch["sheet"],
                "status": "visually_verified_map_footprint",
                "verification": "Visual roof-outline review at 4x with enlarged ridge/edge rechecks for new patches; not independent human certification.",
                "polygon_px": polygon, "bbox_px": bounds(polygon), "area_px2": area(polygon),
                "ward": patch.get("ward"), "ward_hint": patch["ward_hint"],
                "ward_status": "verified_enclosure" if patch.get("ward") else "provisional_map_position_not_boundary_surveyed",
                "ward_evidence_id": patch.get("ward_evidence_id"),
                "building_class": patch.get("building_class"), "residential_use": None, "floor_count": None,
                "area_sqft": None,
                "deduplication": "One canonical observation per traced roof in this selected patch; not a citywide deduplication.",
            })
            scaled = [(x * 4, y * 4) for x, y in local]
            draw.line(scaled + scaled[:1], fill="lime", width=2)
            draw.text(scaled[0], str(index), fill="white", stroke_width=1, stroke_fill="black")
        for index, group in enumerate(definition["unresolved_groups"], 1):
            polygon = translate(group["polygon"], x0, y0)
            unresolved.append({
                "id": f"{patch['id']}-unresolved-{index:02}", "patch_id": patch["id"],
                "pdf_page": patch["pdf_page"], "sheet": patch["sheet"],
                "polygon_px": polygon, "bbox_px": bounds(polygon), "area_px2": area(polygon),
                "reason": group["reason"], "building_count": None,
                "status": "unresolved_roof_group_not_counted",
            })
            scaled = [(x * 4, y * 4) for x, y in group["polygon"]]
            draw.line(scaled + scaled[:1], fill="orange", width=3)
            draw.text(scaled[0], f"U{index}", fill="orange", stroke_width=1, stroke_fill="black")
        overlay.save(artifacts / f"{patch['id']}-review.png")
        patches.append(patch)

    definition = PATCHES[0]
    x0, y0, x1, y1 = definition["bbox_px"]
    rgb = np.array(extract_native(doc, definition["pdf_page"]).crop((x0, y0, x1, y1)))
    sensitivity, saved_candidates = [], []
    for threshold in THRESHOLDS:
        labels, candidates, rejected_large = detect_patch(rgb, threshold)
        metrics = evaluate_candidates(labels, candidates, definition["footprints"])
        rejected_metrics = evaluate_candidates(labels, rejected_large, definition["footprints"])
        metrics["rejected_large_components"] = len(rejected_large)
        metrics["rejected_large_components_hitting_multiple_roofs"] = rejected_metrics["merged_candidates"]
        sensitivity.append({"red_threshold": threshold, **metrics})
        if threshold == 140:
            for index, candidate in enumerate(candidates, 1):
                bx0, by0, bx1, by1 = candidate["bbox_px"]
                saved_candidates.append({
                    "id": f"diagnostic-component-{index:02}", **candidate,
                    "bbox_px": [bx0 + x0, by0 + y0, bx1 + x0, by1 + y0],
                    "pdf_page": 53, "sheet": 3, "patch_id": definition["id"],
                    "status": "unverified_image_component_not_a_building",
                })
    for sheet in sheets:
        owned = [o for o in observations if o["sheet"] == sheet["sheet"]]
        sheet["selected_verified_map_footprints"] = len(owned)
        sheet["selected_footprint_area_px2"] = sum(o["area_px2"] for o in owned)
    scanned_area = sum(t["native_size_px"][0] * t["native_size_px"][1] for s in sheets for t in s["tiles"])
    reviewed_area = reviewed_patch_area(patches)
    payload = {
        "schema_version": 1,
        "survey_id": "waterdeep-city-system-local-partial-v2",
        "status": "partial_evidence_not_a_city_census",
        "census_ready": False,
        "source": {
            "relative_path": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else source.name,
            "sha256": source_hash, "pdf_page_count": len(doc),
            "map_sheet_pages": [34, 113],
            "source_year_dr": 1357,
            "source_year_citation": {"pdf_page": 5, "printed_page": 4},
            "verified_for_1492_dr": False,
            "map_scale_printed": "One inch equals 100 feet",
            "physical_scale_status": "Not calibrated against original sheet dimensions; no square-foot conversion.",
            "pdf_page_numbering": "1-based file pages, NOT printed page numbers",
            "scale_audit": {
                "map_scale_citation": {"pdf_page": 69, "map_sheet": 5},
                "floor_plan_scale": "One square equals 5 feet",
                "floor_plan_scale_citation": {"pdf_page": 70, "map_sheet": 5},
                "floor_plan_scale_applies_to_city_roofs": False,
                "pdf_page_size_points": [594, 773],
                "accepted_physical_calibrations": 0,
                "rejected_shortcuts": [
                    "PDF page inches are the tiled scan's page dimensions, not verified original poster inches.",
                    "Border letter/number references locate sites, but are not a printed distance scale.",
                    "Five-foot grids belong to separately drawn floor-plan examples outside city geometry, not the adjacent roof map.",
                    "Preview tiles are resized independently; neither preview pixels nor all native tile pixels share a demonstrated feet-per-pixel scale.",
                ],
            },
        },
        "counting_unit": "Depicted external roof outline, not a roof face, room, household or named landmark.",
        "coverage": {
            "city_sheets_present": 10, "city_sheets_fully_surveyed": 0,
            "city_sheets_with_samples": len({p["sheet"] for p in patches}), "sample_patches": len(patches),
            "native_tile_area_px2_including_overlaps_and_exclusions": scanned_area,
            "review_patch_area_px2": reviewed_area,
            "review_patch_area_px2_including_patch_overlaps": sum(p["reviewed_area_px2"] for p in patches),
            "raw_tile_area_review_fraction": reviewed_area / scanned_area,
            "city_land_area_review_fraction": None,
            "city_building_review_fraction": None,
            "citywide_unique_building_count": None,
            "selected_unique_verified_map_footprints": len(observations),
            "selected_footprint_area_px2": sum(o["area_px2"] for o in observations),
            "unresolved_roof_groups": len(unresolved),
            "coverage_warning": "Raw scanned-pixel fraction is NOT city-area or building coverage.",
        },
        "exclusions": [
            {"pdf_pages": [1, 33], "reason": "Cover/booklet; instructions and samples, not city map geometry."},
            {"pdf_pages": [114, 121], "reason": "Scenic perspective, map12, not plan-view city inventory."},
            {"pdf_pages": [122, 126], "reason": "Ship diagrams, not land buildings."},
            {"pdf_pages": [127, 130], "reason": "Castle interior/additional material, map11, not additional city buildings."},
            {"pdf_pages": [34, 113], "reason": "Outside the explicit patch masks, no pixels contribute to the inventory. Inside masks only traced roofs count. Excludes sample floor plans, sea, trees, streets, wall symbols, labels and unreviewed city."},
        ],
        "reconstruction": {
            "tile_layout": "Four columns by two rows per city sheet; PDF order row-major.",
            "preview_tile_size_px": [600, 780],
            "native_sizes_vary": True,
            "preview_is_metric_map": False,
            "cross_sheet_topology": "Booklet PDF4 gives sheets1-5 top row,6-10 bottom row in its rotated overview.",
            "cross_sheet_registration_status": "unresolved",
            "deduplication_scope": "Selected nonidentical city blocks only; no citywide seam ownership established.",
            "registration_trial": (
                "SIFT/BF matching of adjacent normalized sheets produced spurious "
                "matches at repeated legends, numbers and roof symbols; unconstrained "
                "fits included near-zero scales. Constraining expected overlap strips "
                "still yielded too few reliable correspondences or implausible scales. "
                "No automated affine fits were accepted."
            ),
            "required_before_city_totals": "Survey city/exterior masks, register each sheet with distinct street/landmark control points, then assign seam ownership and reconcile duplicates.",
            "layout_citations": [
                {"pdf_page": 3, "printed_page": 2, "basis": "Ten city maps overlap; exterior space contains example floor plans. Map11 is Castle Waterdeep interior; map12 is perspective."},
                {"pdf_page": 4, "printed_page": 3, "basis": "Overview shows sheets1-5 above sheets6-10, with map north pointing toward the right."},
            ],
            "selected_subset_deduplication": {
                "method": "Manual street-block/enclosure identity, not image-feature registration or polygon distance across different scans.",
                "canonical_pages": sorted({p["pdf_page"] for p in patches}),
                "within_page": "North/south Lamp blocks are separated by Lamp Street; the Favenbar and Sul/Shield blocks are separated by Wrightstone Street. All accepted polygons are pairwise nonoverlapping within each native page.",
                "between_sheets": "Harbor Net/Eel block (2), central Lamp blocks (3), Heroes' Garden/Wrightstone blocks (5), walled cemetery interior (8) and Saerdoun/Trollwall block (9) have distinct street/enclosure contexts. Other appearances in sheet overlaps are not inventoried.",
                "citywide_seam_ownership": False,
            },
        },
        "sheets": sheets, "patches": patches, "ward_evidence": WARD_EVIDENCE,
        "observations": observations, "unresolved_groups": unresolved,
        "diagnostic_candidates": saved_candidates,
        "validation": {
            "manual_reference_patch": definition["id"],
            "manual_reference_roof_count": len(definition["footprints"]),
            "selection": "Convenience samples, not random or representative sampling.",
            "reviewer": "Assistant visual inspection; independent human review pending.",
            "expansion_review": {
                "baseline_verified_roofs": 35,
                "new_reviewed_patches": 5,
                "method": "Trace native outlines, inspect numbered overlays against unmarked source, enlarge ambiguous ridges/edges, merge roof faces or demote unresolved groups.",
                "corrections_before_acceptance": [
                    "Net/Eel: two pairs of roof faces merged into two complete external outlines.",
                    "Lamp south: two faces merged and incomplete exterior edges corrected.",
                    "Saerdoun/Trollwall: two faces merged and adjacent roof edges corrected.",
                    "Favenbar: three uncertain shapes demoted to one unresolved roof group; no group building count.",
                ],
            },
            "detector_status": "rejected_for_inventory_and_extrapolation",
            "analysis_versions": {
                "pymupdf": pymupdf.VersionBind, "pillow": PIL.__version__,
                "numpy": np.__version__, "opencv": cv2.__version__,
            },
            "detector_parameters": {
                "blur_kernel": [5, 5], "green_less_than": 100, "blue_greater_than": 60,
                "opening_kernel": [3, 3], "area_strictly_between_px2": [35, 1200],
                "minimum_bbox_dimension_px": 4,
            },
            "association_rule": "A component hits a manual roof when intersection >= max(8px,10% of rasterized reference roof). Multiple hits expose split/merge failures.",
            "false_candidate_definition": "Unmatched by this area criterion; includes small roof fragments, not necessarily non-roof objects. Filtered metrics exclude rejected large merged components, reported separately.",
            "sensitivity": sensitivity,
            "generalization": "Color-specific threshold tested only on the Castle sample; NOT valid across wards.",
        },
        "limitations": [
            f"{len(observations)} selected visually verified roof glyphs are a partial physical sample, not a city building total.",
            "No citywide count, ward total, occupancy, residential share, floor count or population is inferred.",
            "Only selected roofs inside the independently identified City of the Dead wall have confirmed ward/Class A assignments. Other ward hints remain contextual, not confirmed.",
            "Roof outline is not necessarily foundation footprint; tracing has approximately two-pixel edge uncertainty.",
            "Native pixel areas from different resized scans cannot be assumed to share a physical scale.",
            "Adjacent wings and contiguous rows sometimes have ambiguous structural boundaries.",
            "No extrapolation from the 282 named locations or either reference population.",
            f"{len(unresolved)} unresolved roof groups are excluded, not rounded into synthetic building counts.",
            "Source evidence is historical 1357 DR, not a verified 1492 DR building stock or census.",
        ],
    }
    if audit_registration:
        payload["reconstruction"]["feature_registration_audit"] = registration_audit(doc)
    if render:
        doc[10].get_pixmap(matrix=pymupdf.Matrix(2, 2)).save(artifacts / "pdf-page-011.png")
    doc.close()
    return add_model_contract(payload)


def validate_inventory(payload):
    if payload["schema_version"] != 2 or payload["source"]["sha256"] != SOURCE_SHA256:
        raise ValueError("Unsupported inventory schema or source identity")
    if payload["census_ready"] is not False or payload["coverage"]["citywide_unique_building_count"] is not None:
        raise ValueError("A partial survey must never be census-ready or assert a city total")
    if payload["complete"] is not False or payload["deduplicated"] is not False:
        raise ValueError("Citywide completeness or deduplication has not been established")
    observations = payload["observations"]
    if len({o["id"] for o in observations}) != len(observations):
        raise ValueError("Duplicate canonical observation IDs")
    if sum(s["selected_verified_map_footprints"] for s in payload["sheets"]) != len(observations):
        raise ValueError("Sheet totals do not reconcile with selected unique observations")
    if payload["coverage"]["selected_unique_verified_map_footprints"] != len(observations):
        raise ValueError("Coverage count does not reconcile")
    if payload["coverage"]["verified_building_count"] != len(observations):
        raise ValueError("Model contract count does not reconcile")
    expected_buildings = add_model_contract({"observations": observations, "source": {}, "coverage": {}})["buildings"]
    if payload["buildings"] != expected_buildings:
        raise ValueError("Model contract differs from its reviewed source observations")
    total_area = sum(o["area_px2"] for o in observations)
    if not math.isclose(payload["coverage"]["selected_footprint_area_px2"], total_area):
        raise ValueError("Coverage area does not reconcile")
    patches = {p["id"]: p for p in payload["patches"]}
    definitions = {p["id"]: p for p in PATCHES}
    if patches.keys() != definitions.keys() or len(patches) != len(payload["patches"]):
        raise ValueError("Patch manifest differs from the reproducible manual review")
    if payload.get("ward_evidence") != WARD_EVIDENCE:
        raise ValueError("Ward evidence differs from reviewed source citations")
    if payload["source"]["physical_scale_verified"]:
        raise ValueError("No physical calibration has been accepted")
    if payload["source"].get("source_year_dr") != 1357 or payload["source"].get("verified_for_1492_dr") is not False:
        raise ValueError("Historical evidence must not be asserted as verified 1492 stock")
    coverage = payload["coverage"]
    if coverage["city_sheets_fully_surveyed"] != 0 or coverage["city_land_area_review_fraction"] is not None or coverage["city_building_review_fraction"] is not None:
        raise ValueError("Partial review cannot assert city/ward completeness")
    if coverage["physically_scaled_building_count"] != 0 or coverage["verified_footprint_sqft"] is not None or coverage["candidate_building_count"] != 0:
        raise ValueError("Uncalibrated roofs or diagnostic components cannot supply new physical evidence")
    if [s["sheet"] for s in payload["sheets"]] != list(range(1, 11)):
        raise ValueError("City sheet manifest is incomplete")
    if [t["pdf_page"] for s in payload["sheets"] for t in s["tiles"]] != list(range(34, 114)):
        raise ValueError("City tile manifest is incomplete")
    scanned_area = sum(t["native_size_px"][0] * t["native_size_px"][1] for s in payload["sheets"] for t in s["tiles"])
    if coverage["native_tile_area_px2_including_overlaps_and_exclusions"] != scanned_area or not math.isclose(
        coverage["raw_tile_area_review_fraction"], reviewed_patch_area(payload["patches"]) / scanned_area
    ):
        raise ValueError("Raw tile pixel accounting does not reconcile")
    if coverage["sample_patches"] != len(patches) or coverage["city_sheets_with_samples"] != len({p["sheet"] for p in patches.values()}):
        raise ValueError("Patch coverage does not reconcile")
    if coverage["review_patch_area_px2"] != reviewed_patch_area(payload["patches"]):
        raise ValueError("Review area must union overlapping masks on each native page")
    if coverage["unresolved_roof_groups"] != len(payload["unresolved_groups"]):
        raise ValueError("Unresolved group counts do not reconcile")
    for name, predicate in (
        ("ward_assigned_building_count", lambda o: o["ward"] is not None),
        ("individually_classified_building_count", lambda o: o["building_class"] is not None),
        ("class_a_building_count", lambda o: o["building_class"] == "A"),
    ):
        if coverage[name] != sum(predicate(o) for o in observations):
            raise ValueError("Classification coverage does not reconcile")
    for patch_id, patch in patches.items():
        definition = definitions[patch_id]
        for key in ("pdf_page", "sheet", "bbox_px", "ward", "ward_evidence_id", "building_class"):
            if patch.get(key) != definition.get(key):
                raise ValueError("Patch provenance differs from reviewed source")
        owned = [o for o in observations if o["patch_id"] == patch_id]
        if len(owned) != len(definition["footprints"]) or patch["verified_map_footprint_count"] != len(owned):
            raise ValueError("Patch footprint count differs from manual review")
        for observation, local in zip(owned, definition["footprints"]):
            if observation["polygon_px"] != translate(local, *patch["bbox_px"][:2]):
                raise ValueError("Footprint differs from its reproducible manual outline")
        groups = [g for g in payload["unresolved_groups"] if g["patch_id"] == patch_id]
        if len(groups) != len(definition["unresolved_groups"]) or patch["unresolved_group_count"] != len(groups):
            raise ValueError("Unresolved patch groups do not reconcile")
        for group, reviewed in zip(groups, definition["unresolved_groups"]):
            polygon = translate(reviewed["polygon"], *patch["bbox_px"][:2])
            if group["polygon_px"] != polygon or group["bbox_px"] != bounds(polygon) or group["area_px2"] != area(polygon):
                raise ValueError("Unresolved group geometry differs from manual review")
            if group["building_count"] is not None or group["status"] != "unresolved_roof_group_not_counted":
                raise ValueError("Unresolved roof groups must not become building counts")
    for sheet in payload["sheets"]:
        owned = [o for o in observations if o["sheet"] == sheet["sheet"]]
        if sheet["selected_verified_map_footprints"] != len(owned):
            raise ValueError("Individual sheet count does not reconcile")
        if not math.isclose(sheet["selected_footprint_area_px2"], sum(o["area_px2"] for o in owned)):
            raise ValueError("Individual sheet area does not reconcile")
        for tile in sheet["tiles"]:
            if tile["pdf_page"] != sheet_page(sheet["sheet"], tile["row"], tile["column"]):
                raise ValueError("Incorrect sheet tile provenance")
    for observation in observations:
        patch = patches[observation["patch_id"]]
        if observation["pdf_page"] != patch["pdf_page"] or observation["sheet"] != patch["sheet"]:
            raise ValueError("Observation provenance does not match its patch")
        if not 34 <= observation["pdf_page"] <= 113:
            raise ValueError("Excluded page contributes a building")
        if observation["status"] != "visually_verified_map_footprint":
            raise ValueError("Unverified component mixed into observations")
        if observation["area_sqft"] is not None:
            raise ValueError("Uncalibrated physical precision")
        if observation["ward"] != patch.get("ward") or observation["building_class"] != patch.get("building_class") or observation.get("ward_evidence_id") != patch.get("ward_evidence_id"):
            raise ValueError("Ward/class assignment lacks the reviewed patch evidence")
        x0, y0, x1, y1 = patch["bbox_px"]
        if not all(x0 <= x <= x1 and y0 <= y <= y1 for x, y in observation["polygon_px"]):
            raise ValueError("Footprint escapes its reviewed patch")
        if observation["bbox_px"] != bounds(observation["polygon_px"]):
            raise ValueError("Incorrect footprint bounding box")
        if not math.isclose(observation["area_px2"], area(observation["polygon_px"])):
            raise ValueError("Incorrect footprint area")
    for index, observation in enumerate(observations):
        for other in observations[index + 1:]:
            if observation["pdf_page"] == other["pdf_page"] and polygons_overlap(observation["polygon_px"], other["polygon_px"]):
                raise ValueError(f"Overlapping canonical roof outlines: {observation['id']}, {other['id']}")
        for group in payload["unresolved_groups"]:
            if observation["pdf_page"] == group["pdf_page"] and polygons_overlap(observation["polygon_px"], group["polygon_px"]):
                raise ValueError("Verified footprint overlaps an unresolved roof group")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--artifacts", type=Path, default=ROOT / ".waterdeep-survey")
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--registration-audit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.rebuild:
        payload = make_inventory(args.source.resolve(), args.artifacts, args.render, args.registration_audit)
        validate_inventory(payload)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    elif args.check:
        payload = json.loads(args.output.read_text(encoding="utf-8"))
        validate_inventory(payload)
    else:
        parser.error("Choose --rebuild or --check")
    print(json.dumps(payload["coverage"], indent=2))
    print("PARTIAL EVIDENCE ONLY: census application remains blocked.")


if __name__ == "__main__":
    main()
