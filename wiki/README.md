# Location Wiki

A project-local reference for Forgotten Realms locations, starting with
[Phandalin](locations/phandalin/README.md). Entries bring together sourced lore,
dated history, engine inputs, observed simulation outputs, and unresolved questions.
These pages are Markdown documentation, not a new application screen. Reviewed
summaries are also curated in [the runtime lore catalogue](../faerun/data/lore.py)
and returned in the location-detail API and MCP response's `lore` field.

## Canon Source Policy

**[Forgotten Realms Wiki](https://forgottenrealms.fandom.com/) is the project's
preferred secondary reference for canonical setting information.** Use reviewed,
cited information from it to supplement details unavailable through the economy engine.
The project wiki records that research; it is not an independent canon authority.

Engine inputs and calculated outputs remain authoritative for the running
simulation, not for establishing canon. Lore never silently replaces population,
prices, production, staffing, routes, or other model values. Preserve discrepancies
for review, and prefer directly verified published sources for the relevant era
when sources conflict. Keep disputed and unknown dates explicit.

Runtime summaries include source URLs, access dates, primary/secondary-source labels,
era notes, and a `source_policy`. They are curated locally, not fetched live.
Locations without reviewed entries remain unresearched; approving a source does
not mean every location or every claim on that source has been checked.

**Sources not to use:** [Forgotten Maps](https://forgottenmaps.com/) (fan-made
interactive maps whose location text is copied from the Forgotten Realms Wiki;
noted 2026-10-16 at Murray's request). Do not cite it or take marker positions from it.

## Demographics Standard

Every location records its racial makeup. The runtime record lives in
[the demographics catalogue](../faerun/data/demographics.py), is returned in the
location-detail API and MCP response's `demographics` field, and is shown under
**Racial makeup** on the location page. Each wiki page records the same under its
population section, with the reference period, scope, races, ethnic subgroups
and sources.

- Status is `quantified` (sourced percentages), `estimated` (explicitly illustrative
  scenario shares, stored as `estimated_share_pct` rather than `share_pct`),
  `qualitative` (sourced descriptions only) or `unresearched`. Never present an
  estimate as a sourced number or turn "mostly" or "some" into a verified share.
- Say whether a figure covers the city or its environs, and the year it describes.
  A mix from an earlier edition is not assumed to hold in 1492 DR.
- A race that is not named is not evidence of absence.
- Demographics are reference text. The model's population is not divided by race,
  and nothing here changes workers, demand, production or prices.
- Every researched lore entry must have a record, enforced by
  `tests/test_demographics.py`. A location researched without a demographic source
  gets an `unresearched` record with a note, not an invented one.

## Locations

| Location | Region | Reference period | Status |
| --- | --- | --- | --- |
| [Phandalin](locations/phandalin/README.md) | Sword Coast North, Lost Hills of the Sword Mountains | 1491 DR snapshot, early 1490s DR; 1496 DR noted as later; 1492 DR unverified | Reviewed lore 2026-10-09 (replacing the 2026-10-01 cross-reference); gold mine, logging and hunting industries, description and six 1491 DR businesses applied; orchard tried and reverted (olives); ruler, population, silver and routes proposed |
| [Griffon's Nest](locations/griffons-nest/README.md) | Savage Frontier, Surbrin Hills | 1485 DR, latest documented snapshot before the 1492 baseline | Reviewed lore; historical notes retained |
| [Triboar](locations/triboar/README.md) | Dessarin Valley, Evermoor Way and Long Road crossing | 1357 to 1370 DR lore; after 1485 DR snapshot (1491 DR ruler); 1492 DR unverified | Reviewed lore 2026-10-08 from the wiki (replacing the 2026-10-01 limited review); horse and tan industries, wagon, saddle, riding horse, pony and nails specialties, description and seven businesses applied; ruler, population evidence and routes proposed |
| [Waterdeep](locations/waterdeep/README.md) | Sword Coast North | 1372 to 1492 DR; 1492 DR baseline | Engine, lore and Volo directory reviewed; changes proposed |
| [Neverwinter](locations/neverwinter/README.md) | Sword Coast North, High Road at the mouth of the Neverwinter River | 1357 to 1372 DR lore; 1451 DR destruction; 1479 DR and circa 1491 DR snapshots; 1492 DR unverified | Reviewed lore 2026-10-13 from the wiki (replacing the 2026-10-01 limited review); lantern specialty and description applied; ruler, population evidence, orchard, guild limits, farm-export anomaly and High Road links proposed |
| [Hlondeth](locations/hlondeth/README.md) | Vilhon Reach | 1357 to 1373 DR lore; 1492 DR unverified | Reviewed lore; engine record rebuilt from a surveyed market |
| [Arrabar](locations/arrabar/README.md) | Chondath, Vilhon Reach | 1357 to 1373 DR lore, plus late-15th-century restoration note | Reviewed lore (inhabitants, places and organizations mined 2026-10-13); population updated to the 1372 DR count; sketch and metadata |
| [Amphail](locations/amphail/README.md) | Dessarin Valley, Long Road | Circa 1372 DR lore, 1485 DR ruler; 1492 DR unverified | Reviewed lore; fixes and Murray's decisions applied 2026-10-04 (ruler, population 850, Stag-Horned Flagon, Mintarn salt); engine follow-ups open |
| [Goldenfields](locations/goldenfields/README.md) | Dessarin Valley, west bank of the Dessarin | 1355 to 1372 DR lore; circa 1485 to 1491 DR snapshot; 1492 DR unverified | Reviewed lore 2026-10-05; herb industry, corn and rice specialties, description and Goldengulp Brewery applied; population, ruler and river proposed |
| [Red Larch](locations/red-larch/README.md) | Dessarin Valley, Long Road waystop | Circa 1366 to 1372 DR lore; 1491 DR snapshot; 1492 DR unverified | Reviewed lore 2026-10-06; tan industry, wagon, saddle, chicken and eggs specialties, description and four 1491 DR businesses applied; population, ruler and cattle proposed |
| [Daggerford](locations/daggerford/README.md) | Delimbiyr Vale, Trade Way at the Delimbiyr crossing | 1347 to 1372 DR lore; circa 1485 to 1489 DR snapshot; 1492 DR unverified | Reviewed lore 2026-10-07; region, description, hunt, ship, tan, brew and fish industries, furs and clothing specialties and six late-15th-century businesses applied; population, ruler, timber shortage and river port proposed |
| [Stone Bridge](locations/stone-bridge/README.md) | Dessarin Valley, River Dessarin on the Stone Trail | Circa 1368 DR description (Dwarves Deep); legendary history; 1492 DR unverified | Reviewed lore 2026-10-10; a dwarven bridge and temple to Moradin, not a settlement; description applied; replacing the surveyed market with Westbridge or Beliard, population, position and routes proposed |
| [Leilon](locations/leilon/README.md) | Sword Coast North, High Road on the Sea of Swords coast | 1357 to 1370 DR lore; circa 1491 DR resettlement snapshot; 1492 DR unverified | Reviewed lore 2026-10-11; copper and silver mining, fishing and description applied; population, ruler, iron, port and the missing High Road link proposed |
| [Yartar](locations/yartar/README.md) | Dessarin Valley, Surbrin crossing on the Evermoor Way | 1361 to 1372 DR lore; circa 1491 DR snapshot; 1492 DR unverified | Reviewed lore 2026-10-12; ship industry, river boat specialty, description and the Lionshield Coster (HQ) applied; population, ruler, food imports versus farm output, temple and river lane proposed |
| [Secomber](locations/secomber/README.md) | Delimbiyr Vale, Delimbiyr Route at the Unicorn Run confluence | 1358 to 1372 DR lore; 1479 DR and circa 1491 DR notes; 1492 DR unverified | Reviewed lore 2026-10-14; quarry industry, region and description applied; population, ruler, unsourced gem mining, routes and the Moon Mountain Brewery proposed; sketch and metadata added 2026-10-15; sourced climate (The North) shown on the location page, and Singing Sprite, Seven-Stringed Harp, Samril's Fine Blades and Gleskur's Finemetals businesses added 2026-10-15 (1492 DR operation unverified) |
| [Orlumbor](locations/orlumbor/README.md) | Sea of Swords, island off the Sword Coast west of the Trollbark Forest | 1358 to 1372 DR lore; circa 1491 DR Lords' Alliance listing; 1492 DR unverified | Reviewed lore 2026-10-15; herd industry and description applied; seagoing shipbuilding, timber shortage, population, ruler, sea lanes and position proposed |
| [Longsaddle](locations/longsaddle/README.md) | Savage Frontier (Sword Coast North), Long Road between the Crags and the Evermoors | 1357 to 1376 DR lore; 1479 to 1489 DR snapshot (1489 DR spokesman); 1492 DR unverified | Reviewed lore 2026-10-16; herd industry and description applied; ruler, population scope, harness tag output, Long Road businesses and routes proposed |

## Routes

| Route | Mode | Status |
| --- | --- | --- |
| [Hlondeth to Arrabar Sea Lane](routes/hlondeth-arrabar-sea-lane.md) | Sea lane | Engine record, carriers and endpoint settlements reviewed 2026-10-03; Arrabar operating by the late 15th century DR |

## Commodities

[The commodity wiki](commodities/README.md) has a page for each of the engine's 278
commodities and for 371 proposed goods taken from *Aurora's Whole Realms Catalogue*
(1992), grouped by category. Engine pages record stored model inputs; proposed pages
record catalogue prices, a labelled scaled estimate and the closest engine good.
None of it changes the simulation.

## Equipment

[The equipment wiki](equipment/README.md) records items used to make goods or do work:
build estimate at engine prices, capacity, service life and the production routes that
need them. It starts with [brewing](equipment/brewing/README.md), the equipment behind
the [ale formulation](commodities/drink/ale.md#formulation-proposed); arms, tack and rope
groups are planned. Nothing in it is in the engine.

## Location Inventory

The location-by-location review, its queue, proposed engine changes, proposed
commodities and lore follow-ups are tracked in [inventory.md](inventory.md).

## Evidence Conventions

- **Sourced lore:** paraphrased information with a source link and its applicable period. A secondary wiki is not independent verification of the publications it cites.
- **Engine input:** a configured value, not automatically a canonical fact.
- **Observed output:** a dated simulation result; it can change with inputs, routes, calendar, and software revisions.
- **Unknown or unresolved:** missing evidence, disputed dates, or a mismatch awaiting review. Unknown does not mean zero.

Keep historical and later developments separate from the 1492 DR planning baseline.
Record source access dates and distinguish directly consulted sources from publications
cited by those sources. Paraphrase; do not reproduce source articles, illustrations,
maps, or book text.

## Adding a Location

Add a lowercase, hyphenated folder under `locations/` (for example
`locations/phandalin/`) with the page as `README.md`, and link it in the table
above. Keep every file about that location in the same folder: maps, sketches,
images and the structured `<name>.json`. Follow the Phandalin entry's sections: overview, geography,
population, economy, government, infrastructure, named places and people,
chronology, engine record, discrepancies, and sources. Every location page
also tracks **Notable Inhabitants** (people dated nearest to 1492 DR first,
then historical, then legendary or loosely tied, then families and
organizations; see [Amphail](locations/amphail/README.md)) and, where any map
exists, a **Maps** list preferring 2nd-edition versions. To generate a map that
can be measured for housing and population, use the
[map prompt template](locations/map-prompt-template.md). Omit sections for which
there is no evidence rather than inventing details.

Link engine claims to the owning project files. Clearly distinguish archived
exports from current route edits and baseline coordinates from live map positions.
When research is reviewed, add its concise, dated summary and citations to the
runtime lore catalogue as well as this wiki. Do not copy engine estimates into
the sourced-lore paragraphs. Documentation does not change the simulation: changing production, population,
water, named businesses, or routing requires a separate validated data/code change.

[Project README](../README.md)