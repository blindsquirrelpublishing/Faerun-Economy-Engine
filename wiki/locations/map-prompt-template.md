# Location Map Prompt Template

[Location index](../README.md)

A reusable prompt for generating location maps that can be measured for housing
and population work. Use it in two passes: a flat plan that can be traced, then a
painted reference map built from it.

Image generators cannot hold a true scale or an exact building count, even with a
good prompt. Check every result against its grid before relying on it. A traced
count is only as reliable as the scale bar in the image, so record that caveat on
the location page, as [Triboar](triboar/README.md) does.

## Rules the prompts follow

- Strictly top-down and orthographic: no perspective, tilt, 3D or isometric view.
- Buildings are flat dark-grey filled shapes on a plain light background: no
  roofs, shading, textures, trees or painted style.
- A light-grey 100-foot grid with labelled axes and a scale bar, so pixels can be
  calibrated to feet and distortion spotted.
- No title banner, legend or decoration over the town, and no text on buildings.
- High resolution (3000 pixels wide) and high contrast.
- Footprints and land use come in separate images, so the footprints can be traced.

## Pass 1: measurement plan (the image to trace)

> Top-down orthographic site plan of **[NAME]**, a **[SIZE CATEGORY]** in a
> fantasy setting, covering **[WIDTH] by [HEIGHT] feet**, north at the top. Flat
> vector style. No perspective, no 3D, no shading, no trees, no painted or
> illustrated look. Plain off-white background.
>
> Buildings are solid dark-grey filled rectangles and L-shapes, each separate,
> with no overlaps and no text on them. Typical house **[HOUSE SIZE]** ft, large
> civic or commercial buildings up to **[LARGE SIZE]** ft. Roughly
> **[BUILDINGS]** buildings in total, packed in street blocks with narrow lots.
> Roads are white with thin black outlines.
>
> Features: **[WALL: with N gates / none]**, **[WATER: river on the west side /
> coast on the south / none]**, **[central market square / none]**, **[main roads
> entering from the north and east]**.
>
> Overlay a light-grey 100-foot grid with labelled axes and a scale bar from 0 to
> 500 ft. No legend, title banner, compass decoration or border over the town.
> 3000 pixels wide, high contrast, uncompressed.

## Pass 2: reference map (the image for the wiki page)

> Use the same layout as the attached image. Redraw it as a hand-painted fantasy
> cadastral map with land-use colours (residential, commercial, crafts, civic,
> religious, farmland), property boundaries and a legend. Keep every building and
> street in the same place.

## Filling in the fields

| Field | How to choose it |
| --- | --- |
| **SIZE CATEGORY** | The settlement's size category in the engine record (village, small town, large town, city) |
| **WIDTH, HEIGHT** | Built-up area in feet. Aim for about 60 to 100 people per acre inside walls: acres = population / 80, then feet = sqrt(acres x 43,560) for a square plan |
| **BUILDINGS** | Population / 5 people per household / 1.3 households per building. For a village with few mixed buildings, use population / 5 |
| **HOUSE SIZE, LARGE SIZE** | Typical house 20 by 30 ft; large buildings up to 60 by 100 ft. Raise both for wealthy or planned towns |
| **WALL, WATER, MARKET, ROADS** | The location's wiki page and engine record (port, river, terrain, route links). Use the wiki's compass directions only where confirmed |

Worked example, Triboar (population 2,500): about 31 acres, so roughly 1,200 by
1,200 feet; about 385 buildings; wall with three gates; river on the west side;
central market square; Triboar Trail from the north-west, Long Road from the
north-east and Evermoor Way to the south-east (orientation unconfirmed).

## Cautions

- Never put the population in the prompt. [census.py](../../faerun/census.py)
  estimates housing from footprints and never from a target population. The
  building count above only sets a plausible density for the image.
- Treat the traced footprints, not the requested count, as the result.
- Generators ignore requested counts. Expect a different number of buildings and
  recount from the image.
- Do not use a generated map as a source for canon. Record its provenance on the
  location page (no publisher, artist or edition) and the date it was designated
  the reference.
- An exactly scaled plan can instead be generated as an SVG from rules (street
  grid, lot and building sizes). Its counts then come from the assumptions, not
  from independent evidence.
