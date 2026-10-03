"""Review or apply source-supported terrain repairs, regionally or whole-sheet."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

try:
    from tools import survey_terrain_1mile as survey
except ModuleNotFoundError:
    import survey_terrain_1mile as survey


ROOT = Path(__file__).resolve().parents[1]
REGIONS = ("Cormanthor", "Jungles of Chult", "The High Forest", "The Wood of Sharp Teeth")


def interior_patches(codes, support, maximum_patch_cells=25):
    open_ground = np.isin(codes, ["G", "P"])
    safe = ~survey._dilate(~np.isin(codes, ["F", "G", "P"]), 6)
    visited = np.zeros(codes.shape, bool)
    patches = []
    for start_row, start_column in zip(*np.where(open_ground)):
        if visited[start_row, start_column]:
            continue
        pending = [(int(start_row), int(start_column))]
        visited[start_row, start_column] = True
        component = []
        enclosed = True
        while pending:
            row, column = pending.pop()
            component.append((row, column))
            for delta_row, delta_column in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                other_row, other_column = row + delta_row, column + delta_column
                if not (0 <= other_row < codes.shape[0] and 0 <= other_column < codes.shape[1]):
                    enclosed = False
                elif open_ground[other_row, other_column]:
                    if not visited[other_row, other_column]:
                        visited[other_row, other_column] = True
                        pending.append((other_row, other_column))
                elif codes[other_row, other_column] != "F":
                    enclosed = False
        if not enclosed or len(component) > maximum_patch_cells:
            continue
        rows, columns = np.array(component).T
        if np.all(safe[rows, columns] & support[rows, columns]):
            patches.append(component)
    return patches


def propose(payload, locations, topographical, high_forest=False):
    red, green, blue = (topographical[:, :, channel] for channel in range(3))
    value = topographical.max(axis=2)
    forest = (green - (red + blue) / 2 >= survey.GREEN_MIN) & (value < (215 if high_forest else 205))
    forest &= ~((red - blue >= survey.DESERT_WARM) & (green - blue >= survey.DESERT_GREEN_GAP))
    supported = forest & (survey._box_mean(forest, 1) >= (0.75 if high_forest else 0.9))
    changes = []
    summaries = []
    seen = set()
    for name in (("The High Forest",) if high_forest else REGIONS):
        location = next(item for item in locations if item["name"] == name)
        center_column = round(location["east_miles"])
        center_row = round(location["north_miles"])
        column_min = max(payload["column_min"], center_column - 120)
        column_max = min(payload["column_max"], center_column + 120)
        row_min = max(payload["row_min"], center_row - 120)
        row_max = min(payload["row_max"], center_row + 120)
        codes = np.array([
            list(payload["rows"][str(row)][column_min - payload["column_min"]:column_max - payload["column_min"] + 1])
            for row in range(row_max, row_min - 1, -1)
        ])
        rows, columns = np.indices(codes.shape)
        native_x = np.rint((survey.ANCHOR_PIXEL[0] + (column_min + columns) * survey.PIXELS_PER_MILE) * topographical.shape[1] / 4763).astype(int)
        native_y = np.rint((survey.ANCHOR_PIXEL[1] - (row_max - rows) * survey.PIXELS_PER_MILE) * topographical.shape[0] / 3185).astype(int)
        patches = interior_patches(codes, supported[native_y, native_x], 400 if high_forest else 25)
        count = 0
        for patch in patches:
            for row, column in patch:
                coordinate = (column_min + column, row_max - row)
                if coordinate in seen:
                    continue
                seen.add(coordinate)
                changes.append({"column": coordinate[0], "row": coordinate[1], "before": str(codes[row, column]), "after": "F", "region": name})
                count += 1
        summaries.append({"region": name, "patches": len(patches), "cells": count})
    return changes, summaries


def apply_changes(payload, changes, consistency=False):
    updated = dict(payload)
    updated["rows"] = dict(payload["rows"])
    changed_rows = {}
    for change in changes:
        row = str(change["row"])
        cells = changed_rows.setdefault(row, list(payload["rows"][row]))
        column = change["column"] - payload["column_min"]
        assert cells[column] == change["before"]
        if not consistency:
            assert change["before"] in ("G", "P") and change["after"] == "F"
        cells[column] = change["after"]
    for row, cells in changed_rows.items():
        updated["rows"][row] = "".join(cells)
    return updated


def connected_support(mask, seeds, minimum_size=1):
    visited = np.zeros(mask.shape, bool)
    result = np.zeros(mask.shape, bool)
    for start_row, start_column in zip(*np.where(mask)):
        if visited[start_row, start_column]:
            continue
        pending = [(int(start_row), int(start_column))]
        visited[start_row, start_column] = True
        component = []
        seeded = False
        while pending:
            row, column = pending.pop()
            component.append((row, column))
            seeded |= bool(seeds[row, column])
            for delta_row, delta_column in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                other_row, other_column = row + delta_row, column + delta_column
                if (0 <= other_row < mask.shape[0] and 0 <= other_column < mask.shape[1]
                        and mask[other_row, other_column] and not visited[other_row, other_column]):
                    visited[other_row, other_column] = True
                    pending.append((other_row, other_column))
        if seeded and len(component) >= minimum_size:
            rows, columns = np.array(component).T
            result[rows, columns] = True
    return result


def consistency_codes(codes, original, topographical, relief):
    result = codes.copy()
    red, green, blue = (topographical[:, :, channel] for channel in range(3))
    topographic_water = (blue - red > 12) & (blue - green > 3)
    wooded = (green - (red + blue) / 2 >= 8) & (topographical.max(axis=2) < 225)
    forest_core = survey._box_mean(codes == "F", 8) >= 0.65
    forest_support = survey._box_mean(wooded, 3) >= 0.7
    forest_fill = np.isin(codes, ["G", "P", "D"]) & forest_core & forest_support
    forest_fill &= ~survey._dilate(np.isin(codes, ["S", "W", "M", "H", "I", "T", "U"]), 2)
    result[forest_fill] = "F"

    red, green, blue = (original[:, :, channel] for channel in range(3))
    river_ink = (blue - red > 12) & (blue - green > 3) & (original.max(axis=2) > 80)
    river_ink &= survey._dilate(topographic_water, 3)
    water = codes == "W"
    rivers = connected_support(river_ink | water, water, minimum_size=12)
    river_fill = rivers & river_ink & ~np.isin(codes, ["S", "I", "U", "T"])

    warm = (red - blue >= 18) & (red - green >= 8) & (original.max(axis=2) < 178)
    warm &= (original.max(axis=2) - original.min(axis=2)) < 0.42 * original.max(axis=2)
    peaks = codes == "M"
    closed_peaks = survey._erode(survey._dilate(peaks, 3), 3)
    mountain_support = (survey._box_mean(warm, 2) >= 0.08) | (relief >= 0.35)
    mountain_fill = closed_peaks & mountain_support & np.isin(codes, ["H", "P", "G"])
    mountain_fill &= ~survey._dilate(np.isin(codes, ["S", "W", "I", "T", "U"]), 1)
    result[mountain_fill] = "M"
    result[river_fill] = "W"
    result[:8] = codes[:8]
    result[-8:] = codes[-8:]
    result[:, :8] = codes[:, :8]
    result[:, -8:] = codes[:, -8:]
    return result


def propose_consistency(payload):
    column_min, column_max, row_min, row_max = 140, 510, -40, 350
    size = (column_max - column_min + 1, row_max - row_min + 1)
    codes = np.array([list(payload["rows"][str(row)][column_min - payload["column_min"]:column_max - payload["column_min"] + 1])
                      for row in range(row_max, row_min - 1, -1)])
    box = (survey.ANCHOR_PIXEL[0] + (column_min - 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[1] - (row_max + 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[0] + (column_max + 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[1] - (row_min - 0.5) * survey.PIXELS_PER_MILE)
    images = []
    for name in ("Faerun Hires.jpg", "Fareun Topographical.png"):
        with Image.open(ROOT / "maps" / name) as handle:
            image = handle.convert("RGB")
            scaled_box = (box[0] * image.width / 4763, box[1] * image.height / 3185,
                          box[2] * image.width / 4763, box[3] * image.height / 3185)
            images.append(np.asarray(image.resize(size, Image.Resampling.BILINEAR, box=scaled_box), dtype=np.int16))
    alphabet = {letter: index / (len(payload["value_alphabet"]) - 1) for index, letter in enumerate(payload["value_alphabet"])}
    relief = np.array([[alphabet[letter] for letter in payload["relief"][str(row)][column_min - payload["column_min"]:column_max - payload["column_min"] + 1]]
                       for row in range(row_max, row_min - 1, -1)])
    updated = consistency_codes(codes, images[0], images[1], relief)
    changes = [{"column": column_min + int(column), "row": row_max - int(row),
                "before": str(codes[row, column]), "after": str(updated[row, column]), "region": "The High Forest"}
               for row, column in zip(*np.where(codes != updated))]
    return changes, [{"region": "The High Forest", "cells": len(changes),
                      "transitions": dict(Counter(change["before"] + "->" + change["after"] for change in changes))}]


def propose_regions(payload, configuration):
    if configuration.get("frame") != "FPS1:WD" or configuration.get("coordinate_units") != "miles":
        raise ValueError("Regions must use FPS1:WD coordinates in miles")
    staged = {}
    owners = {}
    for region in configuration["regions"]:
        column_min, column_max, row_min, row_max = region["bounds"]
        vertices = region["polygon"]
        if len(vertices) < 3 or any(not (column_min <= column <= column_max and row_min <= row <= row_max)
                                    for column, row in vertices):
            raise ValueError("Region polygon must lie inside its bounds")
        if not (payload["column_min"] <= column_min <= column_max <= payload["column_max"] and
                payload["row_min"] <= row_min <= row_max <= payload["row_max"]):
            raise ValueError("Region bounds must lie inside the terrain grid")
        if region["terrain"] not in ("F", "M", "H") or not set(region["replace"]) <= set("FGPDHM"):
            raise ValueError("Region fill cannot replace protected terrain")
        feather = int(region.get("feather_miles", 0))
        if not 0 <= feather <= 15:
            raise ValueError("Feather width must be between zero and fifteen miles")
        if feather:
            column_min = max(payload["column_min"], column_min - feather)
            column_max = min(payload["column_max"], column_max + feather)
            row_min = max(payload["row_min"], row_min - feather)
            row_max = min(payload["row_max"], row_max + feather)
        mask = Image.new("1", (column_max - column_min + 1, row_max - row_min + 1))
        ImageDraw.Draw(mask).polygon([(column - column_min, row_max - row) for column, row in vertices], fill=1)
        if feather:
            core = np.asarray(mask).copy()
            band = survey._dilate(core, feather) & ~core
            with Image.open(ROOT / "maps" / "Fareun Topographical.png") as handle:
                source = np.asarray(handle.convert("RGB"), dtype=np.int16)
            red, green, blue = (source[:, :, channel] for channel in range(3))
            wooded = (green - (red + blue) / 2 >= 8) & (source.max(axis=2) < 225)
            wooded &= (red - blue < 52)
            support = survey._box_mean(wooded, 1)
            rows, columns = np.indices(core.shape)
            native_x = np.clip(np.rint((survey.ANCHOR_PIXEL[0] + (column_min + columns) * survey.PIXELS_PER_MILE) * source.shape[1] / 4763).astype(int), 0, source.shape[1] - 1)
            native_y = np.clip(np.rint((survey.ANCHOR_PIXEL[1] - (row_max - rows) * survey.PIXELS_PER_MILE) * source.shape[0] / 3185).astype(int), 0, source.shape[0] - 1)
            distance = np.full(core.shape, feather, dtype=float)
            for radius in range(feather - 1, 0, -1):
                distance[survey._dilate(core, radius)] = radius
            threshold = 0.55 + 0.3 * distance / feather
            accepted = band & wooded[native_y, native_x] & (support[native_y, native_x] >= threshold)
            for row_index, column_index in zip(*np.where(accepted)):
                column, row = column_min + int(column_index), row_max - int(row_index)
                key = (column, row)
                before = payload["rows"][str(row)][column - payload["column_min"]]
                if before == "M" and region["terrain"] == "F":
                    staged[key] = "F"
                    owners[key] = region["name"]
        for row_index, column_index in zip(*np.where(np.asarray(mask))):
            column, row = column_min + int(column_index), row_max - int(row_index)
            key = (column, row)
            before = payload["rows"][str(row)][column - payload["column_min"]]
            current = staged.get(key, before)
            if current in region["replace"]:
                staged[key] = region["terrain"]
                owners[key] = region["name"]
    changes = []
    for (column, row), after in sorted(staged.items()):
        before = payload["rows"][str(row)][column - payload["column_min"]]
        if before != after:
            changes.append({"column": column, "row": row, "before": before,
                            "after": after, "region": owners[(column, row)]})
    summaries = [{"region": region["name"], "cells": sum(change["region"] == region["name"] for change in changes)}
                 for region in configuration["regions"]]
    return changes, summaries


SEPARATE_SOURCES = ("Flat-color Faerun ground cover map.png", "Faerun elevation and sea-depth map.png")


def mountain_elevation(elevation):
    red, green, blue = (elevation[:, :, channel].astype(np.int16) for channel in range(3))
    mountain = (red > green + 25) & (red > blue + 25)
    # Shaded red slopes and pale-red summit highlights belong to the same band.
    pink_peak = ((red >= 220) & (blue >= 130) & (np.abs(green - blue) <= 20)
                 & (red > green + 5) & (red > blue + 5))
    white_peak = elevation.min(axis=2) >= 240
    return mountain | pink_peak | white_peak


def above_treeline(elevation):
    red, green, blue = (elevation[:, :, channel].astype(np.int16) for channel in range(3))
    # Red hues stop at 15 degrees; orange slopes remain below the treeline.
    red_band = 4 * (green - blue) <= red - blue
    return mountain_elevation(elevation) & (red_band | (elevation.min(axis=2) >= 240))


def separated_source_codes(codes, cover, elevation, whole=False):
    forest_color = np.array([62, 132, 66], dtype=np.int32)
    forest_distance_squared = np.sum((cover.astype(np.int32) - forest_color) ** 2, axis=2)
    forest = forest_distance_squared < 45 ** 2
    if whole:
        footprint = forest
    else:
        seeds = np.zeros(codes.shape, bool)
        seeds[codes.shape[0] // 2, codes.shape[1] // 2] = True
        footprint = connected_support(forest, seeds)
    red, green, blue = (elevation[:, :, channel].astype(np.int16) for channel in range(3))
    lowland = (green > red + 15) & (green > blue + 45)
    upland = (red > 175) & (green > 145) & (blue < 100)
    result = codes.copy()
    land = np.isin(codes, list("FGPDHM"))
    eligible = footprint & land
    result[eligible & lowland] = "F"
    result[(land if whole else eligible) & upland] = "H"
    mountain = mountain_elevation(elevation)
    treeless = above_treeline(elevation)
    result[land & mountain] = "M"
    result[eligible & mountain & ~treeless] = "F"
    return result, footprint


def separate_source_bounds(payload, whole=False):
    if whole:
        return tuple(payload[key] for key in ("column_min", "column_max", "row_min", "row_max"))
    return 140, 510, -40, 350


def sample_separate_sources(payload, bounds=None):
    column_min, column_max, row_min, row_max = bounds or separate_source_bounds(payload)
    size = (column_max - column_min + 1, row_max - row_min + 1)
    codes = np.array([list(payload["rows"][str(row)][column_min - payload["column_min"]:column_max - payload["column_min"] + 1])
                      for row in range(row_max, row_min - 1, -1)])
    box = (survey.ANCHOR_PIXEL[0] + (column_min - 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[1] - (row_max + 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[0] + (column_max + 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[1] - (row_min - 0.5) * survey.PIXELS_PER_MILE)
    images = []
    for name in SEPARATE_SOURCES:
        with Image.open(ROOT / "maps" / name) as handle:
            image = handle.convert("RGB")
            scaled = (box[0] * image.width / 4763, box[1] * image.height / 3185,
                      box[2] * image.width / 4763, box[3] * image.height / 3185)
            images.append(np.asarray(image.resize(size, Image.Resampling.NEAREST, box=scaled), dtype=np.int16))
    return codes, images


def propose_separate_sources(payload, whole=False):
    bounds = separate_source_bounds(payload, whole)
    column_min, _, _, row_max = bounds
    region = "Whole Faerun" if whole else "High Forest"
    codes, images = sample_separate_sources(payload, bounds)
    updated, footprint = separated_source_codes(codes, *images, whole=whole)
    if not footprint.any():
        raise ValueError(f"{region} ground-cover forest is empty; check source colors and alignment")
    changes = [{"column": column_min + int(column), "row": row_max - int(row),
                "before": str(codes[row, column]), "after": str(updated[row, column]),
                "ground_cover": "F" if footprint[row, column] else None,
                "region": region + " separated sources"}
               for row, column in zip(*np.where(codes != updated))]
    return changes, [{"region": region, "forest_source_cells": int(footprint.sum()), "cells": len(changes),
                      "transitions": dict(Counter(change["before"] + "->" + change["after"] for change in changes))}]


def boundary_segments(mask, column_min, row_max):
    segments = []
    for row in range(mask.shape[0] - 1):
        edges = mask[row] != mask[row + 1]
        transitions = np.diff(np.pad(edges.astype(int), (1, 1)))
        for start, stop in zip(np.flatnonzero(transitions == 1), np.flatnonzero(transitions == -1)):
            segments.append([column_min + int(start), row_max - row,
                             column_min + int(stop), row_max - row])
    for column in range(mask.shape[1] - 1):
        edges = mask[:, column] != mask[:, column + 1]
        transitions = np.diff(np.pad(edges.astype(int), (1, 1)))
        for start, stop in zip(np.flatnonzero(transitions == 1), np.flatnonzero(transitions == -1)):
            segments.append([column_min + column + 1, row_max + 1 - int(start),
                             column_min + column + 1, row_max + 1 - int(stop)])
    return segments


def rebuild_source_boundaries(payload, destination):
    codes, images = sample_separate_sources(payload)
    _, footprint = separated_source_codes(codes, *images)
    if not footprint.any():
        raise ValueError("High Forest ground-cover footprint is empty")
    masks = {"forest": footprint & ~above_treeline(images[1]),
             "mountain": codes == "M", "water": np.isin(codes, ["S", "W"])}
    output = {
        "format": "faerun-source-boundaries-v1", "frame": "FPS1:WD", "coordinate_units": "miles",
        "bounds": [140, 511, -40, 351],
        "description": "High Forest vegetation outline from the connected ground-cover mass below the treeline; only red and white elevation bands are treeless. Orange slopes retain source-supported forest. Mountains and shorelines follow the current one-mile terrain. Crop edges are not boundaries.",
        "supersedes": ["high-forest", "lost-peaks", "star-mounts"],
        "source_sha256": {name: hashlib.sha256((ROOT / "maps" / name).read_bytes()).hexdigest() for name in SEPARATE_SOURCES},
        "terrain_sha256": hashlib.sha256((ROOT / "maps" / "terrain-1-mile.json").read_bytes()).hexdigest(),
        "segments": {name: boundary_segments(mask, 140, 350) for name, mask in masks.items()},
    }
    destination.write_text(json.dumps(output, separators=(",", ":")), encoding="utf-8")
    print(json.dumps({"boundary_segments": {name: len(lines) for name, lines in output["segments"].items()},
                      "destination": str(destination)}))


def render_high_forest_review(payload, destination, regions=None, bounds=None, sources=None):
    column_min, column_max, row_min, row_max = bounds or (140, 510, -40, 350)
    width, height = column_max - column_min + 1, row_max - row_min + 1
    sources = sources or ("Faerun Hires.jpg", "Fareun Topographical.png")
    with Image.open(ROOT / "maps" / sources[0]) as handle:
        original = handle.convert("RGB").resize((4763, 3185), Image.Resampling.NEAREST)
    with Image.open(ROOT / "maps" / sources[1]) as handle:
        topographical = handle.convert("RGB").resize(original.size, Image.Resampling.NEAREST)
    box = (survey.ANCHOR_PIXEL[0] + (column_min - 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[1] - (row_max + 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[0] + (column_max + 0.5) * survey.PIXELS_PER_MILE,
           survey.ANCHOR_PIXEL[1] - (row_min - 0.5) * survey.PIXELS_PER_MILE)
    codes = np.array([list(payload["rows"][str(row)][column_min - payload["column_min"]:column_max - payload["column_min"] + 1])
                      for row in range(row_max, row_min - 1, -1)])
    picture = np.zeros((height, width, 3), np.uint8)
    for index, color in survey.RENDER_COLOURS.items():
        picture[codes == survey.LETTERS[index]] = color
    review = Image.new("RGB", (width * 6, height * 2))
    for index, image in enumerate((original.crop(box), topographical.crop(box), Image.fromarray(picture))):
        review.paste(image.resize((width * 2, height * 2), Image.Resampling.NEAREST), (index * width * 2, 0))
    if regions:
        drawing = ImageDraw.Draw(review)
        for panel in range(3):
            for region in regions["regions"]:
                color = "#0055ff" if region["terrain"] == "F" else "#e000bb"
                vertices = [(panel * width * 2 + (column - column_min) * 2, (row_max - row) * 2)
                            for column, row in region["polygon"]]
                drawing.line(vertices + vertices[:1], fill=color, width=3)
                west, east, south, north = region["bounds"]
                drawing.rectangle((panel * width * 2 + (west - column_min) * 2, (row_max - north) * 2,
                                   panel * width * 2 + (east - column_min) * 2, (row_max - south) * 2), outline=color)
                drawing.text((vertices[0][0] + 4, vertices[0][1] + 4), region["name"], fill=color)
    destination.parent.mkdir(parents=True, exist_ok=True)
    review.save(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--high-forest", action="store_true",
                        help="review larger High Forest interiors with the forest wash threshold")
    parser.add_argument("--review", action="store_true", help="render High Forest source and terrain side by side")
    parser.add_argument("--consistency", action="store_true", help="review source-supported High Forest cover, mountain gaps and river ink")
    parser.add_argument("--regions", action="store_true", help="use explicit High Forest and mountain bounding regions")
    parser.add_argument("--region-file", type=Path, help="use another explicit terrain region configuration")
    parser.add_argument("--audit-file", type=Path, help="write a new rollback audit without replacing earlier audits")
    parser.add_argument("--separate-sources", action="store_true", help="classify High Forest from separate cover and elevation images")
    parser.add_argument("--whole", action="store_true",
                        help="apply separate-source elevation and treeline rules across the entire one-mile survey")
    parser.add_argument("--rebuild-boundaries", action="store_true", help="rebuild High Forest source outlines without changing terrain")
    args = parser.parse_args()
    if args.whole and (not args.separate_sources or args.high_forest or args.review
                      or args.consistency or args.regions or args.region_file or args.rebuild_boundaries):
        parser.error("--whole requires --separate-sources and cannot be combined with regional operations")
    if args.region_file:
        args.regions = True
    grid_path = ROOT / "maps" / "terrain-1-mile.json"
    image_path = ROOT / "maps" / "Fareun Topographical.png"
    audit_path = ROOT / "maps" / ("terrain-high-forest-cleanup.json" if args.high_forest else "terrain-interior-cleanup.json")
    if args.consistency:
        audit_path = ROOT / "maps" / "terrain-high-forest-consistency.json"
    if args.separate_sources:
        audit_path = ROOT / "maps" / ("terrain-whole-separate-sources-audit.json" if args.whole
                                     else "terrain-high-forest-separate-sources-audit.json")
    configuration = None
    if args.regions:
        region_path = args.region_file or ROOT / "maps" / "high-forest-regions.json"
        configuration = json.loads(region_path.read_text(encoding="utf-8"))
        audit_path = ROOT / "maps" / ("terrain-" + region_path.stem + "-audit.json")
    if args.audit_file:
        audit_path = args.audit_file
    original = grid_path.read_bytes()
    payload = json.loads(original)
    assert payload["cell_miles"] == 1 and payload["frame"] == "FPS1:WD"
    if args.rebuild_boundaries:
        rebuild_source_boundaries(payload, ROOT / "maps" / "high-forest-source-boundaries.json")
        return
    if args.review:
        destination = ROOT / "maps" / "terrain-1-mile-review" / "high-forest-comparison.png"
        render_high_forest_review(payload, destination)
        print(destination)
        return
    locations = json.loads((ROOT / "maps" / "locations.json").read_text(encoding="utf-8"))["locations"]
    with Image.open(image_path) as image:
        topographical = np.asarray(image.convert("RGB"), dtype=np.int16)
    changes, summaries = (propose_separate_sources(payload, whole=args.whole) if args.separate_sources else
                          propose_regions(payload, configuration) if configuration else
                          propose_consistency(payload) if args.consistency else
                          propose(payload, locations, topographical, args.high_forest))
    updated = apply_changes(payload, changes, args.consistency or args.regions or args.separate_sources)
    assert all(updated[key] == value for key, value in payload.items() if key != "rows")
    actual = Counter()
    for row, before in payload["rows"].items():
        after = updated["rows"][row]
        assert len(before) == len(after)
        actual.update((old, new) for old, new in zip(before, after) if old != new)
    assert sum(actual.values()) == len(changes)
    if args.separate_sources:
        assert all(old in "FGPDHM" and new in "FHM" for old, new in actual)
        render_high_forest_review(updated, ROOT / "maps" / "terrain-1-mile-review" / "high-forest-separated-proposed.png", sources=SEPARATE_SOURCES)
        if args.whole:
            render_high_forest_review(updated, ROOT / "maps" / "terrain-1-mile-review" / "stormhorns-separated-proposed.png",
                                      bounds=(760, 1010, -370, -120), sources=SEPARATE_SOURCES)
    elif args.regions:
        assert all(old in "FGPDHM" and new in "FMH" for old, new in actual)
        render_high_forest_review(updated, ROOT / "maps" / "terrain-1-mile-review" / (region_path.stem + ".png"),
                                  configuration, configuration.get("review_bounds"))
    elif args.consistency:
        assert all((old in ("G", "P", "D") and new == "F") or
                   (old in ("H", "P", "G") and new == "M") or
                   (old not in ("S", "I", "U", "T") and new == "W") for old, new in actual)
        render_high_forest_review(updated, ROOT / "maps" / "terrain-1-mile-review" / "high-forest-proposed.png")
    else:
        assert all(old in ("G", "P") and new == "F" for old, new in actual)
    print(json.dumps({"regions": summaries, "total_cells": len(changes), "applied": args.apply}, indent=2))
    if not args.apply or not changes:
        return
    if audit_path.exists():
        raise SystemExit("An audit already exists; refusing to overwrite its rollback record.")
    encoded = json.dumps(updated, separators=(",", ":")).encode("utf-8")
    audit = {
        "source": image_path.name,
        "source_sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
        "before_sha256": hashlib.sha256(original).hexdigest(),
        "after_sha256": hashlib.sha256(encoded).hexdigest(),
        "rules": {"maximum_patch_cells": 400 if args.high_forest else 25, "protected_buffer_cells": 6, "forest_value_below": 215 if args.high_forest else 205, "native_support_radius": 1, "minimum_support": 0.75 if args.high_forest else 0.9, "region_radius_cells": 120},
        "regions": summaries,
        "changes": changes,
    }
    if args.consistency:
        audit["rules"] = {"bounds_fps_miles": [140, 510, -40, 350], "edge_buffer": 8,
                          "forest_neighborhood_radius": 8, "forest_majority": 0.65,
                          "forest_source_support": 0.7, "forest_value_below": 225,
                          "mountain_gap_radius": 3, "river_minimum_component": 12,
                          "river_requires_existing_water_and_both_images": True,
                          "relief_unchanged": True}
        audit["original_source_sha256"] = hashlib.sha256((ROOT / "maps" / "Faerun Hires.jpg").read_bytes()).hexdigest()
    if args.regions:
        audit["rules"] = configuration
    if args.separate_sources:
        audit["source"] = list(SEPARATE_SOURCES)
        audit["source_sha256"] = {name: hashlib.sha256((ROOT / "maps" / name).read_bytes()).hexdigest() for name in SEPARATE_SOURCES}
        audit["rules"] = {"bounds_fps_miles": list(separate_source_bounds(payload, args.whole)),
                          "scope": "whole-sheet" if args.whole else "High Forest",
                          "cover": ("All" if args.whole else "Connected") + " dark-green forest wash; RGB distance <45 from (62,132,66)",
                          "uplands_require_forest_cover": not args.whole,
                          "elevation": "Green lowland, yellow upland, orange/red mountains, white highest peaks; not calibrated heights",
                          "white_peak_minimum_rgb": 240, "white_peaks_require_forest_cover": False,
                          "treeline": "Only red and white elevation bands are treeless; orange mountains retain source-supported forest",
                          "red_hue_maximum_degrees": 15,
                          "red_band_includes_shadows_and_pale_red_highlights": True,
                          "alignment": "Full-sheet normalized coordinates; nearest-neighbor sampling",
                          "water_and_unclassified_preserved": True, "relief_unchanged": True,
                          "source_resolution_miles_per_pixel": 2.48}
    if args.whole:
        del audit["changes"]
        audit["row_changes"] = {
            row: {"before": before, "after": updated["rows"][row]}
            for row, before in payload["rows"].items() if before != updated["rows"][row]
        }
    assert grid_path.read_bytes() == original, "Grid changed during review; refusing to overwrite."
    with audit_path.open("x", encoding="utf-8") as handle:
        json.dump(audit, handle, indent=2)
    temporary = grid_path.with_suffix(".cleanup.tmp")
    with temporary.open("xb") as handle:
        handle.write(encoded)
    temporary.replace(grid_path)
    assert grid_path.read_bytes() == encoded
    print(f"Applied {len(changes)} cells; rollback values recorded in {audit_path.name}.")


if __name__ == "__main__":
    main()