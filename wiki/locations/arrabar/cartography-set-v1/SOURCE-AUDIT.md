# Arrabar cartography source audit

## Authority and preserved source frame

`ArrabarIA.webp` (1000 x 592) provides the tracing frame and source scale; `Arrabar_map.webp` corroborates road and district layout through five non-collinear control points. `OIP.webp` is contextual because it uses a different key. The earlier sketch and generated pictures are not positional authorities. Original files have byte-identical copies in `source-maps/`.

North is up. No source area is cropped in full-city planar sheets. The Port sheet is a documented uniform crop, x=285-545 and y=95-360. The source scale is 500 feet per approximately 150 pixels (about two pixels reading uncertainty), not a survey measurement. The small source-scaled city and the 61,012 planning population remain inconsistent; no arbitrary rescaling resolves them.

## Shared geography

`ARRABAR-LW-r01-DRAFT` is the shared draft master. Its coast checksum is `7067e0cb9ffa8660eea888d3402510594954e8570e1771b03807da9ca9394b4b`. One mainland and one connected western water body are retained, with no invented islands or river. Piers are separate built structures over the water mask. Source sea-color bands are not bathymetry. User geographic approval remains outstanding; the label is a review status, not a block on producing authorized derivatives.

## Detailed cadastral reconstruction

The latest `02-cadastral-detailed-v1.8-r02` uses `arrabar-cadastral-geometry-r03.json`. Roof-color components are traced in source coordinates. Strongly rectangular symbols use fitted rectangles; other compound outlines retain simplified contours. Disconnected pieces are preserved instead of silently discarded. The output has 475 polygon components; this is neither a count of buildings nor a property census. Source roof extents are ground-footprint proxies, with roughly one-to-two-pixel interpretation uncertainty. Landmark bounds are reference outlines, not filled replacement building boxes.

The 452 inferred planning parcels use nearest-building Voronoi cells clipped to interpreted urban blocks and source street corridors. Dashed boundaries explicitly distinguish them from surveyed ownership. This layer follows the user's express request for inferred delineation; the default GIS style's prohibition on inventing factual parcel boundaries remains respected. Outside-city symbols do not acquire invented urban parcels.

## Setting facts and disputed details

Port lies west, Warehouse northwest, Governor central, Living east and Merchant south. Generon remains in the northern Governor precinct. The atlas places Temple to Tempus west of Governor, while prose says east; its mapped position is retained and the discrepancy disclosed. Crying Claw belongs in Warehouse District, but its exact plot is unresolved. Source sites 10-12 have no readable anchor numerals, so no coordinates are fabricated.

The current economic population 61,012 is an adopted planning estimate based on a 1372 DR figure, not a verified 1492 DR census. The map does not imply that its drawn buildings accommodate that population. Warm humid subtropical climate informs scenic art but does not authorize invented vegetation footprints on the plans.

## Relief and underground interpretation

No measured elevation, vertical datum or underground plan exists in the supplied sources. Relative bands H1-H6 and downslope arrows are hypothetical terrain guides; there is no numeric elevation interval. The covered canal routes and basin at proposed image coordinate (460,282) are explicit reconstructions. The light well is smaller than the water basin. Boats turn in water; there is no rotating structure. Docks, canal widths and structural depths are unverified.

## Views and image generation

The isometric reference uses exact plan coordinates with a fixed axonometric projection; heights and gentle slope are conceptual. Harbor and street camera references use source roof polygons, specified cameras and depth-sorted face occlusion. Scenic images are generated illustrations from the numeric camera and composition descriptions, rather than pixel-registered raster transformations: the image tool rejected Windows reference paths. Their architecture, heights, facade rhythms and local details must not be treated as measured geometry or used to revise the master.

## Checks and delivery

The original v1.8 frame, JSON specification, validator and red seal were recovered and used unchanged as source assets. All eight planar sheets pass the supplied validator. Additional checks cover the 19 x 13 inch sheet, square 17 x 16 grid, 72-point compass, unchanged square seal, uniform source fit and scale-bar length. All full-sheet previews were visually inspected; the detailed cadastral city and sidebar were additionally inspected at full resolution.

The earlier Windows metadata-transfer blocker was resolved using native NTFS extended attributes without modifying the Library helper. A later batch upload failed before creating files because its hosted-app endpoint lacked the preparation tool. Individual host-upload actions remain supported; successful Library IDs are recorded with their local files. Original source files and unrelated repository work are untouched. No commit or push is part of this delivery.
