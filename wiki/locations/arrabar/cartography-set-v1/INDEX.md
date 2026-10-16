# Arrabar cartography set

**Current starting point: [Detailed cadastral map](finished-plates/02-cadastral-detailed-v1.8-r02-preview.png).**

The eight planar sheets and one registered isometric reference are rendered. They are source reconstructions for review, not approved surveys. The original source files remain unchanged. Four scenic image-generation illustrations are saved in `finished-views/`, with prompts and per-image provenance.

## Finished planar sheets

| File stem | Formats | Status |
| --- | --- | --- |
| `01-land-water-master-v1.8` | [SVG](finished-plates/01-land-water-master-v1.8.svg), [PNG](finished-plates/01-land-water-master-v1.8.png), [preview](finished-plates/01-land-water-master-v1.8-preview.png), metadata JSON | Layout and visual checks passed |
| `02-cadastral-detailed-v1.8-r02` | [SVG](finished-plates/02-cadastral-detailed-v1.8-r02.svg), [PNG](finished-plates/02-cadastral-detailed-v1.8-r02.png), [preview](finished-plates/02-cadastral-detailed-v1.8-r02-preview.png), metadata JSON | Layout and visual checks passed |
| `02-cadastral-master-v1.8` | [SVG](finished-plates/02-cadastral-master-v1.8.svg), [PNG](finished-plates/02-cadastral-master-v1.8.png), [preview](finished-plates/02-cadastral-master-v1.8-preview.png), metadata JSON | Layout and visual checks passed |
| `03-topographic-concept-v1.8` | [SVG](finished-plates/03-topographic-concept-v1.8.svg), [PNG](finished-plates/03-topographic-concept-v1.8.png), [preview](finished-plates/03-topographic-concept-v1.8-preview.png), metadata JSON | Layout and visual checks passed |
| `04-five-districts-v1.8` | [SVG](finished-plates/04-five-districts-v1.8.svg), [PNG](finished-plates/04-five-districts-v1.8.png), [preview](finished-plates/04-five-districts-v1.8-preview.png), metadata JSON | Layout and visual checks passed |
| `05-port-district-v1.8` | [SVG](finished-plates/05-port-district-v1.8.svg), [PNG](finished-plates/05-port-district-v1.8.png), [preview](finished-plates/05-port-district-v1.8-preview.png), metadata JSON | Layout and visual checks passed |
| `06-netherwaters-plan-v1.8` | [SVG](finished-plates/06-netherwaters-plan-v1.8.svg), [PNG](finished-plates/06-netherwaters-plan-v1.8.png), [preview](finished-plates/06-netherwaters-plan-v1.8-preview.png), metadata JSON | Layout and visual checks passed |
| `08-illustrated-town-atlas-v1.8` | [SVG](finished-plates/08-illustrated-town-atlas-v1.8.svg), [PNG](finished-plates/08-illustrated-town-atlas-v1.8.png), [preview](finished-plates/08-illustrated-town-atlas-v1.8-preview.png), metadata JSON | Layout and visual checks passed |

The detailed r02 cadastral replaces the earlier working cadastral as the recommended deliverable. Its PNG is 5700 x 3900 pixels (19 x 13 inches at 300 dpi); its editable SVG retains separate district, parcel, street, building, pier, wall and landmark layers. Other planar PNGs are 2850 x 1950 pixels.

## Registered and scenic views

- [Registered isometric SVG](finished-views/07-isometric-registered-reference.svg) and [PNG](finished-views/07-isometric-registered-reference.png): complete source extent, exact planar coordinates, conceptual building heights and slope.
- [Camera manifest](working-geometry/view-camera-manifest-r01.json): harbor and street camera positions, bearings, eye heights, field of view and approximate depth-sorted occlusion.
- Harbor, street and basin cutaway reference PNGs are in `working-geometry/`.

- `09-basin-cutaway.png`: saved; illustrative approximation with conceptual architecture.
- `10-harbor-eye-level.png`: saved; illustrative approximation with conceptual architecture.
- `11-basin-eye-level.png`: saved; illustrative approximation with conceptual architecture.
- `12-street-eye-level.png`: saved; illustrative approximation with conceptual architecture.

The source-registered isometric SVG/PNG is the completed isometric deliverable. A painted raster variant remains unavailable because the image tool could not access either Windows or materialized reference paths. Its geometry was not replaced with an unconstrained generated town.

## Review and editable data

- [Contact sheet](arrabar-completed-maps-contact-sheet.png)
- [Source audit](SOURCE-AUDIT.md)
- [Cadastral geometry r03](working-geometry/arrabar-cadastral-geometry-r03.json)
- [Cadastral building GeoJSON](working-geometry/arrabar-cadastral-buildings-r03.geojson) and [register CSV](working-geometry/arrabar-cadastral-building-register-r03.csv)
- [Source geometry manifest](working-geometry/geometry-manifest-r01.json), [registration](working-geometry/registration-r01.json), [source hashes](source-maps/source-checksums.json)
- `working-geometry/validation/`: source overlays, geometry checks and per-sheet plat checks.
- `skill-assets/`: original v1.8 template, specification, validator and seal; original geometry workflow assets.

## Interpretation limits

475 roof-derived polygon components are drawing fragments or connected symbols, not a building census. 452 Voronoi planning parcels are inferred and shown dashed. Fine roofs and compound shapes are limited by the 1000 x 592 source raster. No legal parcel records, measured ground footprints, elevations, water depths, exact underground dimensions or modern population census were supplied.

The source 500-foot bar spans about 150 pixels. The original horizontal scale is retained; the 61,012 planning population is not used to enlarge the map. White upper/lower margins preserve the full source aspect ratio inside the fixed v1.8 grid. Conceptual relief classes H1-H6 are ordinal, not feet or metres. The Netherwaters basin is maneuvering water, never a mechanical turntable.

Regional trade mapping remains deferred. No commit or push was performed.
