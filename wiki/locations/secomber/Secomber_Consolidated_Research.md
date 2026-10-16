# Secomber: Consolidated Research and Economy-Engine Brief

**Reference baseline:** circa 1492 DR, *not* a verified 1492 snapshot.  
**Area:** Delimbiyr Vale, north bank of the Delimbiyr at the Unicorn Run confluence.  
**Compiled:** 15 October 2026.  
**Purpose:** Research input and proposed corrections for Faerûn economy/settlement documents; not an automatic data patch.

## How to use this package

Read `secomber-economy-engine-research.json` for structured facts, dated evidence, engine record, flags and proposals. The complete prior research dossier is preserved verbatim as `source/README.md`, and the previously supplied JSON as `source/secomber.json`. This brief summarizes the key issues and what should change. Preserve `supported_secondary`, `engine_only`, `reconstruction` and `proposed` states in your data. Do not turn fan-map illustrations, inference or undated descriptions into established 1492 facts.

## Strong historical/geographic findings

Secomber was founded in 516 DR by **halflings from the Delimbiyr Vale and humans from Delimbiyran**. It occupies three stone hills north of the Delimbiyr; the Unicorn Run comes from the north and joins the river on the settlement's eastern/southeastern side. The High Moor lies south across the Delimbiyr. The east-west Delimbiyr Route serves the town, with a northern/northwestern trail toward Uluvin. It is a modest settlement rather than a major city.

It is fair to call Secomber strongly **halfling-influenced**, but not an exclusively halfling or Tolkien-style hobbit settlement. Older descriptions say humans were most numerous with **almost as many halflings**, plus a smaller dwarf, gnome and moon-elf presence. Prior map revisions emphasized low homes and gardens, but individual turf roofs, precise housing types and the count of halfling homes are not independently documented for 1492 DR.

Historical population readings: **900 (1358 DR), 900 (1367 DR), 1,417 (1372 DR)**. The engine has **1,300**, an undated estimate. No reliable 1492 count was established. Keep the historical values as separate dated observations; use 1,300 only as a clearly named model assumption pending review.

Principal supported work is **farming, fishing, stone-cutting, caravan support and guides/guards**. Historic named enterprises include the Singing Sprite inn (1367–1396), Seven-Stringed Harp tavern (1396), Samril's Fine Blades, Gleskur's Finemetals, halfling sour-vinegar vineyards and the external Moon Mountain Brewery. None has been shown to be operating precisely in 1492 DR. The quarry industry was already added in the reviewed engine record. Gem mining, agate, and moonstone outputs currently in the engine have **no evidence in the assembled sources**; audit rather than present them as canon.

By **1479 DR** Secomber faced Urshani hobgoblin pressure, raids and tribute. Circa **1491 DR** the town was described as impoverished by tribute. This should affect any 1492 economic scenario only under an explicit, consistent model rule. Neither a particular tribute sum nor a measured poverty multiplier is known. The old town justice system has elected Rods of Justice; a lord and garrison appear in much older eras. Do not project historical rulers or force strength onto 1492.

## Proposed priorities for the economy engine

| Order | Engine item | Recommendation | Confidence / caution |
|---|---|---|---|
| 1 | SE6: gems and mining | Audit/remove unsourced `mine_gem=2`, `gem_agate=2`, `gem_moonstone=1` and `mining` trait | No support in reviewed lore; not proof of impossibility |
| 2 | SE7: transport | Model Delimbiyr Route, Uluvin trail, and candidate river transport; correct "Black Road" names | Route evidence strong; numeric travel metrics require separate calibration |
| 3 | SE13: trade imports | Investigate extreme import imbalance and flat demand for unsupported goods | Engine-wide simulation error likely; do not patch using fictional prices |
| 4 | SE8: security/tribute | Add a dated raiding / tribute scenario or drain after rules are agreed | Qualitative evidence strong; amount not known |
| 5 | SE4: population | Separate year-specific population observations from 1,300 working estimate | No established 1492 value |
| 6 | SE9–12: businesses | Store period and confidence for inns, workshops, vineyards and brewery link | Dates differ; not automatically current |
| 7 | SE1–3 | Retain previously applied quarry, description and region updates | Confirm on current engine snapshot |

## Economy snapshot from source dossier (model outputs, not historical facts)

| Metric | Before noted change | After noted change |
|---|---:|---:|
| Gross local product, gp/day | 850.8 | 1,013.6 |
| Goods exports, gp/day | 247.9 | 296.5 |
| Imports, gp/day | 59,799 | 59,795 |

The dossier links the second reading to the applied `quarry=1` change and region relabel; it does **not** prove that one change caused every difference. Exports and imports are too imbalanced to treat as a calibrated trade model.

## Cartography and map evidence rules

**Primary reconstruction:** three-hill Secomber town plan, probably associated with the 1479 DR era. It has **no known scale** and is not confirmed as an official surveyed plan. The alternate numbered digital map and graph-paper map show conflicting property, bridge and road layouts. Do not combine these as if they share exact surveyed geometry. The shorelines, three hills, town road route, bridge at Unicorn Run and south-bank Delimbiyr waterfront are useful relative references. Exact polygons, property sizes, elevation levels and land area are unknown.

The latest AI-generated Town Atlas, Isometric and Ground-Level revisions depict the desired **human/halfling character** through gardens and low-built neighborhoods; their buildings, commercial signs, plot boundaries, pontoon positions, stone bridge and stated measured map scales are **illustrative, not verified records**. In particular, the 250-ft grid and 50-ft contour labels are not supported by independently surveyed source dimensions. The v1.8 plat skill defines page layout and scale-validation rules, not Secomber's actual land distances.

**Wall conflict:** older material records a defensive palisade/fort and later 1479 town wall. A later-era claim of removed walls was discussed but its full primary text has not been brought into this packet. Keep wall status as **time-dependent and unresolved for 1492**. Show ruins or missing walls only if the specific later source is verified; do not silently keep or remove them.

**Named hills and sectors:** High Hill, Goodhill, Lord’s Hill, The Green, Flanks, Harbour, South Greens, etc. appear in secondary/fan reference maps. These names may be useful as **working district labels**, but are not verified labels for the canonical three-hill town plan. The Singing Sprite, Seven-Stringed Harp and Tower of Amelior Amanitas are supported names but their individual lot positions are unknown.

## Other source-derived details worth keeping

- Civic justice: six to nine Rods of Justice, elected for four years; juries of nine landowners (period applicability uncertain).
- Old garrison: about 30 Lords' Alliance personnel; militia of more than 100 in older source, not proved for 1492.
- Notable work: Samril's blade finishing required metal, grips, leather and finishing supplies; Gleskur's braided copper wire supported grips. Treat goods as candidates, not current market volumes.
- Moon Mountain Brewery lay roughly two days north in circa 1372 DR; its ale, rum and cider indicate a historical trade connection, not a verified 1492 production site.
- Halfling vineyards northwest of town made sour vinegar, according to undated accounts published much later.
- Green river crabs served at Singing Sprite offer a small qualitative indicator for Delimbiyr fisheries.
- Engine settlement record has `port=null` and `river=true`: illustrated piers do not prove the presence of a model-class port.

## Source quality and provenance

The 2026-10-14 research dossier mostly consulted the **Forgotten Realms Wiki** and related pages; it lists original books but says most books were **not independently checked**. Preserve that limit. The period dates cited above should travel with every asserted fact. The working SVG sketch and generated images are *derived visual references*, not new primary evidence. The alternate graph-paper map may be associated with the NineLizards Secomber project, but that attribution should be checked before formal citation.

### Important source URLs

- https://forgottenrealms.fandom.com/wiki/Secomber
- https://forgottenrealms.fandom.com/wiki/File:Secomber.jpg
- https://forgottenrealms.fandom.com/wiki/Delimbiyr_Route
- https://forgottenrealms.fandom.com/wiki/Secomber_Trail
- https://www.ninelizards.com/archive/secomber%202.htm

## Files in this package

`secomber-economy-engine-research.json`: structured intake with original engine data, evidence, map conflicts, commodity suggestions and issues SE1–SE15.  
`source/README.md`: complete original 424-line research dossier with references.  
`source/secomber.json`: complete structured input as originally supplied.  
`source/secomber-sketch.svg`: supplied working schematic.  
`reference_maps/`: user-supplied reference graphics.  
`generated_maps/`: prior generated maps/scenes, retained for visual comparison only; **not GIS-verified**.
