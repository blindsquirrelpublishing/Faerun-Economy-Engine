---
name: faerun-map-geometry-master
description: Required source-of-truth workflow for converting any supplied settlement map into alternate fantasy cartographic styles while preserving geographic landmarks and geometry.
---

# Map Geometry Master (read before any style)

## Prime directive
**Transform appearance, not geography.** The supplied reference is authoritative. Never move, rotate, resize, add, remove, or rename a verified landmark to make a prettier composition. Preserve roads, intersections, bridges, gates, shorelines, waterways, city walls, neighborhoods, building footprint centroids, orientations, and relative order. Keep north direction unchanged unless user requests rotation; record the rotation.

## Input audit
1. Read every reference and identify authoritative source versus illustrative examples.
2. Record map bounds, aspect ratio, north arrow, scale, known control points, landmark IDs, names, geometry, and confidence.
3. Build a feature inventory and a geometry manifest. Use normalized image coordinates (u=x/width, v=y/height; origin upper-left) when true GIS coordinates are unavailable.
4. Trace canonical roads as centerline polylines; waterways as polygons/centerlines; buildings as footprint polygons; landmarks as anchored points; walls as lines; and elevations as source-derived data only.
5. If the user supplies multiple geographic references, register them with at least three non-collinear matching control points, and note contradictions. Do not silently choose among conflicts.
6. If reference has no wall, harbor, docks, or river, do not create one.

## Rendering contract
- Freeze the canonical geometry layer. Apply the requested style to the *same* feature geometry.
- Project roofs within footprint bounds. Decorate roof surfaces; don't shift building location.
- Do not straighten winding roads, enlarge plazas, add waterways, change bridge crossings, or move manor/castle to dramatic heights.
- Avoid invented labels. For unreadable labels, use a verified feature ID or omit.
- Output at source aspect ratio by default; preserve entire extent unless crop explicitly requested.
- In crop requests, preserve the original crop geometry and record crop bounds.
- For ground-level/oblique views, require camera location, bearing, elevation/eye height, and field of view; occlude unseen structures instead of moving them.
- When elevation is absent, state that relief is artistic/hypothetical, not surveyed.

## Mandatory validation before delivery
Check against source:
1. north orientation and coastline/river alignment
2. road junctions and bridge endpoints
3. walls, gates, towers, manor/castle, square
4. all named/numbered landmarks
5. building counts, density and footprints at a neighborhood level
6. field/orchard/forest footprints
7. no invented or lost major feature
8. scale/grid integrity if claimed
If any fails, regenerate or explicitly disclose the discrepancy. Image-generation-only conversions are *approximate*: do not claim pixel-perfect preservation without actual traced vector overlays and verification.

## Preferred production modes
**Geometry-locked:** trace/edit vector layers (SVG/GeoJSON/GIS), render them with controlled symbology and textures; recommended for strict spatial accuracy.
**Illustrative:** image transformation with the source image attached and strong preservation instructions; visually faithful but cannot guarantee precise placement.

## Files
- `references/geometry-manifest-template.json` is the canonical data schema starter.
- `references/validation-checklist.md` is the QA form.

## Output audit and fidelity report
For each transformation, record the geographic source filename, style source filename (if any), named landmarks checked, road intersections checked, water crossings checked, and any omissions. Classify fidelity as `geometry-locked` only when source geometry is explicitly traced and validated; otherwise classify as `illustrative approximation`. Do not claim perfect accuracy from a generated image.

## Style catalog linking
See `STYLE-CATALOG.md` at collection root. Keep geography, style and labels separate in the workflow.
