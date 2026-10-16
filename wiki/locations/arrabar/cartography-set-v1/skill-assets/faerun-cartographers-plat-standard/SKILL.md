---
name: faerun-cartographers-plat-standard
description: Apply deterministic Faerûn Cartographers Plat Standard v1.8 framing to all fantasy cartography plates, with locked 19:13 sheet geometry, fixed 20% sidebar and 15/15/60/10 zones, sans-serif typography, A–Q / 1–16 square-cell reference grid, official circular stamp, fixed compass and verified scale bar.
---

# Faerûn Cartographers Plat Standard v1.8

## Use
Apply whenever composing or revising any Faerûn Cartographers map plate, including land-water boundary, cadastral, topographic, regional, political, historical, trade, land-cover, and atlas plates. Do not use this full plat frame automatically for a standalone scenic or ground-level illustration unless the user requests a framed map.

**Load** `references/plat-spec-v1.8.json` and use `templates/blank-plat-v1.8.svg` as the *fixed* composition source, not as a mere visual suggestion. The companion `scripts/validate_plat.py` checks the JSON metadata contract. Each specialized drawing skill supplies *only* its appropriate geographic/theme content, never a new frame.

## Fixed sheet
- Landscape sheet 19 × 13 inches (ratio **19:13**), pure white background and restrained thin black rules.
- Left information panel = exactly **20%** of full width; remaining **80%** is map-field region (includes coordinate margins).
- The sidebar vertical zones are percentages of the total sidebar height: **Title 0–15%; Map Information 15–30%; Variable Legend 30–90%; Compass/Seal/Scale 90–100%**.
- Every section has an immutable position, height and separating rule; never move a separator just to fit a long legend.
- Entire title block (location name, map type, Faerûn Cartographers byline) is horizontally **centered**.

## Typography
Use **Arial / sans-serif** throughout. Nominal sizes at 19 × 13 inches: Location name 36pt bold, map type 18pt bold, byline 11pt normal; section headers 13pt bold; info labels 9pt bold and values 9pt regular; legend 9pt; important locations 8.5pt; map labels 10pt; coordinate labels 8pt; scale labels 8pt. Constrain or wrap text within its allotted region, never stretch layout or silently truncate required details.

## Grid and geospatial content
- Columns **A–Q** (17 columns); rows **1–16** (16 rows); labels on *both* corresponding edges (top/bottom; left/right).
- Grid **cells must be square in actual plate coordinates**, not merely drawn as a distorted array. If 17 × 16 squares do not fill the full 80% region, center them with whitespace in the larger map region; do not stretch squares or change the 20/80 partition. Do not label a false metric grid scale.
- Retain the *identical* map-field crop, mask and grid registration across derivative plates. Read and apply Fantasy Land-Water Boundary Master for all geography-dependent map families.
- Rivers, islands and connected mainland come from the user-approved source/master, not from prior generated art. Boats, docks and walls are distinct feature layers and never land or water geometry.

## Mandatory bottom-section composition
- A separator runs immediately ABOVE the bottom **10%** sidebar section.
- **Compass left and original official red circular seal right**, on an upper row; **scale bar below both**, not beside them.
- Compass diameter fixed at **72pt** at the 19×13 physical reference size, never varied across plates. If this clashes with available text space, adjust padding within the fixed section rather than scaling the compass.
- Stamp is the **unchanged image asset** `assets/faerun-cartographers-official-red-seal.png` copied from the existing project geographic-master skill. Its image rectangle MUST be 1:1; no elliptical warping, redrawing, restyling, or changing wording. Slight rotation and uneven authentic ink are acceptable. The stamp may cross the horizontal separator to simulate a stamp applied after plat approval.
- Scale must agree with stated `1 square = N feet/miles`, actual grid cell width, *and* numerical tick labels. If 1 square = 250 ft, a 1,000 ft bar occupies EXACTLY 4 grid-cell widths. If that cannot fit in the sidebar, choose a SHORTER end value (e.g. 250 or 500 ft), use a consistent unit, and physically dimension that bar to the appropriate fraction of a cell. Never shrink or stretch the bar to fill arbitrary space while retaining incompatible tick numbers.
- **Technical constraint:** at 19×13, 17×16 square cells in the 80%-wide field and a 20%-wide sidebar, a 1,000-ft bar may be too wide to fit below the icons when 1 square = 250 ft. Treat this as a real layout constraint, not a cosmetic detail. A shorter correctly dimensioned scale or a separately annotated representative scale is preferable to a false distance claim.

## Rendering and QA
1. Build or open the SVG frame, place the prescribed text and symbols, and place registered raster/vector geographic layers *inside* the fixed grid viewport.
2. Select the scale units and numeric interval only if backed by sources. Calculate `bar_length = distance / feet_per_cell * cell_side_in_inches`; scale tick positions linearly. The 17×16 references must remain square.
3. Check structure with `scripts/validate_plat.py metadata.json` (see `references/example-plate-metadata.json`). For raster output, visually measure/verify panel and symbol bounding rectangles and use side-by-side/overlay comparisons.
4. Verify seal's source pixel geometry, compass diameter, scale tick/bar measurements, accurate A–Q and 1–16 labels, transparent overlap where applied, and fixed section boundaries.
5. If any check fails, revise the composition before calling the plate final. If sources do not support numerical elevation or bathymetry, mark relief interpretive; do not invent survey values.

## Cross-skill integration
- **Source-to-Atlas Workflow**: load this skill at Stage 0 for setup; enforce it in Stage 3 registration, Stage 4 rendering and Stage 5 QA. Geographic approval is independent from visual/layout approval.
- **Land-Water Boundary Master**: own immutable hydrology/shorelines, while this skill owns frame/typography/measurement.
- **All individual mapping skills**: add their content to already-registered geographic layers and this immutable plat frame.

## Acceptance checklist
- [ ] Sheet 19:13, sidebar 20%, map-side 80%.
- [ ] Sidebar zones exactly 15/15/60/10, separators fixed.
- [ ] Center-justified title; sans-serif throughout.
- [ ] Grid 17 columns A–Q, 16 rows 1–16, all four edge labels, *square* cells.
- [ ] Compass fixed 72pt, left of official round seal, both above scale.
- [ ] Official stamp artwork intact, circular (1:1), may rotate/overlap separator.
- [ ] Scale statement, actual cell geometry, bar length and tick labels agree.
- [ ] Land-water geometry unchanged from approved geographic master.
- [ ] No unsupported cartographic precision asserted.
