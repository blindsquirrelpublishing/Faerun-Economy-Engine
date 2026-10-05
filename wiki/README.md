# Location Wiki

A project-local reference for Forgotten Realms locations, starting with
[Phandalin](locations/phandalin.md). Entries bring together sourced lore,
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

## Locations

| Location | Region | Reference period | Status |
| --- | --- | --- | --- |
| [Phandalin](locations/phandalin.md) | Sword Coast North | 1492 DR, with separately dated history | Initial source cross-reference |
| [Griffon's Nest](locations/griffons-nest.md) | Savage Frontier, Surbrin Hills | 1485 DR, latest documented snapshot before the 1492 baseline | Reviewed lore; historical notes retained |
| [Triboar](locations/triboar.md) | Dessarin Valley (engine classification) | After 1485 DR; exact year unresolved | Limited alternative-source business and civic review |
| [Waterdeep](locations/waterdeep.md) | Sword Coast North | 1372 to 1492 DR; 1492 DR baseline | Engine, lore and Volo directory reviewed; changes proposed |
| [Neverwinter](locations/neverwinter.md) | Sword Coast North | Circa 1372 DR history; fifth-edition institutions, exact year unstated | Historical economy and primary-source Alliance reference reviewed; modern infrastructure unresolved |
| [Hlondeth](locations/hlondeth.md) | Vilhon Reach | 1357 to 1373 DR lore; 1492 DR unverified | Reviewed lore; engine record rebuilt from a surveyed market |
| [Arrabar](locations/arrabar.md) | Chondath, Vilhon Reach | 1357 to 1373 DR lore, plus late-15th-century restoration note | Reviewed lore; population updated to the 1372 DR count |
| [Amphail](locations/amphail.md) | Dessarin Valley, Long Road | Circa 1372 DR lore, 1485 DR ruler; 1492 DR unverified | Reviewed lore; fixes and Murray's decisions applied 2026-10-04 (ruler, population 850, Stag-Horned Flagon, Mintarn salt); engine follow-ups open |
| [Goldenfields](locations/goldenfields.md) | Dessarin Valley, west bank of the Dessarin | 1355 to 1372 DR lore; circa 1485 to 1491 DR snapshot; 1492 DR unverified | Reviewed lore 2026-10-05; herb industry, corn and rice specialties, description and Goldengulp Brewery applied; population, ruler and river proposed |

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

Add a lowercase, hyphenated Markdown page under `locations/` and link it in the
table above. Follow the Phandalin entry's sections: overview, geography,
population, economy, government, infrastructure, named places and people,
chronology, engine record, discrepancies, and sources. Every location page
also tracks **Notable Inhabitants** (people dated nearest to 1492 DR first,
then historical, then legendary or loosely tied, then families and
organizations; see [Amphail](locations/amphail.md)) and, where any map
exists, a **Maps** list preferring 2nd-edition versions. Omit sections for which
there is no evidence rather than inventing details.

Link engine claims to the owning project files. Clearly distinguish archived
exports from current route edits and baseline coordinates from live map positions.
When research is reviewed, add its concise, dated summary and citations to the
runtime lore catalogue as well as this wiki. Do not copy engine estimates into
the sourced-lore paragraphs. Documentation does not change the simulation: changing production, population,
water, named businesses, or routing requires a separate validated data/code change.

[Project README](../README.md)