# Neverwinter

[Location index](../../README.md)

**Region:** Sword Coast North; on the High Road between Leilon and Port Llast, at the mouth of the Neverwinter River (engine region `Sword Coast North`, zone `swordcoast_north`)  
**Settlement type:** Coastal city and port; Lords' Alliance member; ruled by a self-styled Lord Protector  
**Reference period:** 1357 to 1372 DR lore (1st to 3rd-edition sources); 1451 DR destruction; 1479 DR snapshot (4th-edition *Neverwinter Campaign Setting*); circa 1491 DR snapshot (5th-edition sources); 1492 DR planning baseline, not verified  
**Evidence reviewed:** 2026-10-13 (replacing the 2026-10-01 limited review)  
**Engine ID:** `neverwinter`

This entry paraphrases the [Forgotten Realms Wiki article][frwiki] (a secondary
source; read directly on 2026-10-13, after the 2026-10-01 attempt was blocked)
and the wiki's person, map and category pages. The article mixes 1st and
2nd-edition material (*Cyclopedia of the Realms*, 1987; *Waterdeep and the North*,
1987; *The Savage Frontier*, 1988; *Volo's Guide to the North*, 1993; *The North*,
1996), the 3rd-edition *Forgotten Realms Campaign Setting* (2001), the
4th-edition *Neverwinter Campaign Setting* (2011, set in 1479 DR) and 5th-edition
books set around 1491 DR (*Sword Coast Adventurer's Guide*, 2015; *Princes of
the Apocalypse*, 2015; *Storm King's Thunder*, 2016). Several details come only
from video games (*Neverwinter Nights*, *Neverwinter Nights 2: Storm of Zehir*,
the *Neverwinter* MMO) and are marked as such. Publications named below are the
wiki's references and were not independently consulted. Nothing here is verified
for 1492 DR unless stated.

## Overview

Neverwinter, the Jewel of the North, is a coastal city on the High Road whose
river, warmed by fire elementals beneath Mount Hotenow, keeps the harbour from
freezing and its gardens green through winter. In the 14th century DR it was a
prosperous craft and learning centre under the Alagondar line, famed for glass
lamps, water clocks and jewellery. The eruption of Mount Hotenow in 1451 DR
destroyed most of the city and killed the Alagondar family. From 1467 DR Dagult
Neverember, then Open Lord of Waterdeep, styled himself Lord Protector and
financed the rebuilding; by about 1491 DR merchants were returning, though walls
and neighbourhoods around the sealed Chasm still lay in ruins. [Source][frwiki],
citing *Neverwinter Campaign Setting*, pp. 86 to 88, 138; *Sword Coast
Adventurer's Guide*, pp. 51 to 53; *Storm King's Thunder*, p. 101.

## Geography

- On the northern Sword Coast, on the High Road between Waterdeep and Luskan,
  specifically between Leilon and Port Llast ([Source][frwiki], citing
  *Cyclopedia of the Realms*, *Waterdeep and the North* and *The Savage
  Frontier*).
- The Neverwinter Wood and the volcanic Mount Hotenow lie to the east. The
  river's supernatural warmth keeps river and harbour ice-free and creates a
  permanently mild climate in the immediate area (*Waterdeep and the North*,
  pp. 3, 6, 9; *The Savage Frontier*, pp. 31 to 32; *Neverwinter Campaign
  Setting*, p. 138).
- Nearby places named in the article: the monastery of Helm's Hold to the
  south-east, the village of Vilnask further south on the High Road, and the
  village of Floodblest to the east on the Neverwinter River. None is in the
  engine.
- Three named bridges cross the river: the Dolphin, the Winged Wyvern and the
  Sleeping Dragon. After the 1451 DR eruption only the Winged Wyvern remained
  in use by 1479 DR (*Neverwinter Campaign Setting*, p. 8).
- Districts: in 1372 DR the City Core, Peninsula, Docks (the main port),
  Blacklake, River and Beggar's Nest districts (layout largely from the video
  game *Neverwinter Nights*); after 1451 DR the Protector's Enclave, Blacklake,
  Neverdeath Graveyard and the River District, with the Chasm (sealed around
  1484 or 1485 DR; the article gives both years).
- Engine: neighbours are Luskan by road (128.2 miles, 6.3 days) and Waterdeep by
  road (284 miles, 13.9 days) and by sea (354.1 miles, 4.9 days). Leilon (61.9
  miles) and Port Llast (59.8 miles), the nearest High Road towns, have no
  direct link.

## Population

| Figure | Scope | Year | Source |
| --- | --- | --- | --- |
| 23,192 | City | Nasher-era account; circa 1372 DR inferred, not stated | [Realms Helps: The North][north] (secondary, read 2026-10-01); appears to follow the 3rd-edition *Forgotten Realms Campaign Setting* (not checked) |
| About 23,200 | City | Undated | [Wikipedia: Neverwinter][wp], citing a fan page for the *Neverwinter Nights* video game; not independent evidence |
| No figure | City | 1479 DR and circa 1491 DR | The wiki article gives no total; only troop sizes (400 Graycloaks in the 14th century DR) |

The only figures predate the 1451 DR eruption, which destroyed most of the
city; the rebuilt city of 1479 to 1491 DR is unlikely to match them, but no
later count was found. Unknown is not zero.

Demographics review (2026-10-15): the [Neverwinter wiki article][frwiki]
actually records human and half-elf families and a dwarf minority circa
1370–1372 DR; eladrin and tieflings are described circa 1479 DR, as is a
hired dragonborn mercenary delegation (not a measured resident population).
A few orcs and half-orcs are documented circa 1491 DR. These are **qualitative,
separately dated** observations, not percentages or a single 1492 DR mix.
Runtime demographics is `qualitative` in `faerun/data/demographics.py`.
The post-eruption distribution and dragonborn resident status remain open.

**Engine:** 23,000 residents, an undated estimate retained for 1492 DR planning,
not a rebuilt-city census. [populations.py](../../../faerun/data/populations.py)
now dates the pre-eruption 23,192 comparison; no population change (N4).

## Economy and Trade

The wiki article has no infobox import or export list. Its Trade and Business
section gives:

| Period | Trade and production | Source cited by the wiki |
| --- | --- | --- |
| Mid to late 14th century DR | Controlled much of the mining trade from dwarf and gnome outposts in the Underdark, through hidden ways in city warehouses; a large fishing economy; logging from the Neverwinter Wood | *Volo's Guide to the North*, pp. 132 to 134 |
| 14th century DR | Water clocks, multicoloured glass lamps and fine jewellery, found across Faerun; traded mostly through Waterdeep's merchants | *Cyclopedia of the Realms*, pp. 66 to 67; *Waterdeep and the North*; *Forgotten Realms Campaign Setting* (2nd and 3rd editions) |
| 14th century DR | Gardeners raised plants in hothouses through winter; the gardens supplied fruit to the city's markets | *The Savage Frontier*, pp. 31 to 32 |
| 14th century DR | Craftwork, learning and magical innovation were the city's main asset; crafters worked in dedicated buildings and street vendors were rare | *Volo's Guide to the North* |
| Late 14th century DR | Three trade cartels (Circle of Friends, Forgotten Lords, Fated Winds) operating from the Temple of Waukeen; a Thayan enclave allowed after the war with Luskan | *Neverwinter Nights 2: Storm of Zehir* (video game only) |
| 1451 DR | Trade halted after the eruption | *Neverwinter Campaign Setting*, p. 138 |
| After 1461 DR | Neverember spent heavily to restore trade and hired crafters to rebuild infrastructure | *Neverwinter Campaign Setting*, p. 88 |
| Before 1479 DR | Traders from Tarmalune in Laerakond sought permanent routes (Laerakond is not part of the 1492 DR world) | *Neverwinter Campaign Setting*, p. 147 |
| Circa 1491 DR | Merchants from north and south returning; Neverember forging a trading alliance with the restored Gauntlgrym; no guilds restricting trade or building, so food traders prospered and workers and apprentices found ready demand | *Sword Coast Adventurer's Guide*, pp. 52 to 53 |
| Circa 1491 DR | Neverember's laws barred new guilds and limited existing ones | *Storm King's Thunder*, p. 101 |

These describe trade character, not volumes, prices or workforce. The 14th
century crafts are not shown to have been restored after 1451 DR.

## Government

- 14th century DR: Lord Nasher Alagondar, then the Alagondar royal line (Bann
  Alagondar late in the century); the wizards of the Many-Starred Cloak held
  real influence. The Graycloaks, 400 archers and spearmen, guarded the walls,
  harbour and High Road, and the city kept a navy (*Waterdeep and the North*;
  *The Savage Frontier*, pp. 9, 61; *Volo's Guide to the North*, pp. 130 to 131).
- 1467 DR onward: Dagult Neverember created the title Lord Protector for
  himself, claiming Alagondar descent, and brought workers and Mintarn
  mercenaries (the Neverwinter Guard) to rebuild (*Neverwinter Campaign
  Setting*, pp. 86 to 88, 138). After his removal as Open Lord of Waterdeep in
  1489 DR he concentrated on Neverwinter and governed more harshly, taxing
  nobles and limiting guilds (*The Rise of Tiamat*, pp. 14 to 15; *Storm King's
  Thunder*, p. 101).
- Late 1480s DR: a locally recruited watch, the Wintershield Watchmen, was
  added (*Sword Coast Adventurer's Guide*, p. 145).
- A Lords' Alliance member since before 1356 DR (*Cyclopedia of the Realms*,
  p. 57; *Volo's Guide to the North*, pp. 130 to 131). The official 5th-edition
  [Basic Rules (2014), Appendix C][factions], read directly on 2026-10-01, names
  Neverwinter with Waterdeep and Silverymoon among the Alliance's leading
  cities, without a ruler's name or a year.
- Rivals for control around 1491 DR included the Sons of Alagondar (mostly
  disbanded by then), the Ashmadai, a Thayan cell, the Abolethic Sovereignty and
  a Bregan D'aerthe cell ([Source][frwiki]).

## Notable Inhabitants

From the wiki's [Category: Inhabitants of Neverwinter][inh] (511 person pages and
12 subcategories, read 2026-10-13). All 511 pages were screened for
5th-edition citations (40 matched) and a selection with economic, civic or
dated roles was read. Paraphrased; sources are those the wiki cites, not
independently checked. Nearest to 1492 DR first.

### Late 15th century DR (closest to the 1492 baseline)

| Person | Role | Dated | Source cited by the wiki |
| --- | --- | --- | --- |
| Dagult Neverember | Lord Protector, wealthy former Open Lord of Waterdeep, Lords' Alliance member | 1467 DR onward; in office circa 1491 DR | *Sword Coast Adventurer's Guide*, pp. 7, 51 to 52; *Neverwinter Campaign Setting*, p. 86; *The Rise of Tiamat*, pp. 14 to 15 |
| Soman Galt | Mayor of Neverwinter | Late 15th century DR (1479 DR setting) | *Neverwinter Campaign Setting*, pp. 89 to 90, 138 |
| Sabine | Mercenary general, later commander of the Neverwinter Guard | Late 15th century DR | *Neverwinter Campaign Setting*, pp. 16, 87, 143 to 144; *Lost Crown of Neverwinter*, p. 20 |
| Sildar Hallwinter | Knight and Lords' Alliance agent from Neverwinter; later on Phandalin's town council | 1491 DR and early 1490s DR | *Lost Mine of Phandelver* |
| Voss Anderton | Absolution Council member representing Neverwinter at Revel's End prison | Late 15th century DR (year not checked) | *Icewind Dale: Rime of the Frostmaiden*, pp. 156, 159 |
| Silvarren Loomshank | Priest of Helm from Neverwinter | Late 15th century DR | *Storm King's Thunder*, pp. 56, 232 |
| Silla Scalesweep | Halfling fisherwoman; later moved to the rebuilding town of Leilon | Late 15th century DR | *Storm Lord's Wrath* (*Essentials Kit*) |
| Valindra Shadowmantle | Arcane Brotherhood overwizard leading the Thayan cell in the city | Late 15th century DR | *Neverwinter Campaign Setting*, p. 108; *Tomb of Annihilation*, p. 58 |
| Rohini | Succubus serving the Abolethic Sovereignty in Neverwinter and Helm's Hold | Late 15th century DR | *Sword Coast Adventurer's Guide* (page not checked) |
| Feldon Strongbeard | Dwarf living in the Protector's Enclave | 1484 DR | *Neverwinter* (video game only) |
| Belast Messandar | Retired elven adventurer turned merchant | Late 15th century DR | *Neverwinter: Tyranny of Dragons* (video game only) |

### 14th century DR (historical)

| Person | Role | Dated | Source cited by the wiki |
| --- | --- | --- | --- |
| Nasher Alagondar | Former adventurer, ruler through much of the 14th century DR, founder of the Alagondar line | 14th century DR (ruling by 1357 DR) | *Waterdeep and the North*, p. 9; *The North*, Cities and Civilization, p. 16; *Neverwinter Campaign Setting*, p. 138 |
| Bann Alagondar | King of Neverwinter | Late 14th century DR | *Neverwinter Campaign Setting*, pp. 20, 86, 138, 148 |
| Tanamere Alagondar | Royal scion of the Alagondar family | Late 14th century DR | Sources not checked |
| Aribeth de Tylmarande | Half-elf paladin of Tyr | Circa 1372 DR | *Neverwinter Nights* (video game); *Lost Crown of Neverwinter*, p. 7 |

### Legendary and loosely tied

| Person | Note |
| --- | --- |
| Halueth Never | Sun elf warrior of Iliyanbruen, the city's legendary namesake (*Volo's Guide to the North*, p. 134; *The North*, p. 16) |
| Gallio Elibro | Leilon's town mage, listed under Neverwinter (*Storm Lord's Wrath*); tie not checked |
| Jarlaxle Baenre | Leader of the Bregan D'aerthe cell named in the article; date not checked |

### Families and organizations

The Alagondar royal family; the Neverember family; the Neverwinter Nine (Lord
Nasher's bodyguards); the Many-Starred Cloak (wizards); the Graycloaks (14th
century army); the Neverwinter Guard (Mintarn mercenaries, then a standing
army); the Wintershield Watchmen (late 1480s DR); New Neverwinter (Neverember's
rebuilding movement); the Sons of Alagondar; the Ashmadai; the Dead Rats of
Luskan; a Thayan cell; a Bregan D'aerthe cell; an Order of the Gauntlet cell;
the Abolethic Sovereignty; the Circle of Friends, Forgotten Lords and Fated
Winds trade cartels (late 14th century DR, video game only). Sources as in the
article.

## Businesses

### In the live market (engine `businesses.json`)

| Business | Type | Offers | Note |
| --- | --- | --- | --- |
| Ironstar Forge Company (`ironstar_forge_company`) | Forge company (HQ Sundabar; branches Silverymoon, Waterdeep, Neverwinter) | Steel ingots, swords, battleaxes, chain armour, shields, carpenter's tools | Engine-authored; no source names it. Offers valid |
| North Coast High Road Freight (`carrier_north_coast_high_road`) | Carrier (HQ Waterdeep; Neverwinter, Luskan) | None (freight service) | Engine-authored carrier; carriers phase |

All offers were checked against `commodities.json`; none names a missing
commodity. `get_city_directory` reports no historical directory for Neverwinter.

### Named in the source, not in the market

Dates are those of the article's lists; individual business articles were not
read, so operation in 1492 DR is not verified.

| Name | Kind | Dated | Modeled goods it suggests |
| --- | --- | --- | --- |
| Moonstone Mask | Festhall | 14th century DR onward (not checked for 1491 DR) | Lodging, `ale`, `wine_common` |
| Driftwood Tavern; Beached Leviathan; Shining Serpent Inn; Fallen Tower | Taverns and inns | Mixed eras (not checked) | Lodging, `ale` |
| Temple of Waukeen | Temple housing three trade cartels | Built after 1374 DR (video game only) | None |
| House of Knowledge; Hall of Justice | Temples of Oghma and Tyr | 14th century DR onward | None |

## Maps and Village Layout

### Maps

Preferred edition: 2nd. No 2nd-edition city plan was found on the article or in
[Category: Maps of Neverwinter][mapcat]; the 2nd-edition images found are an
illustration and regional maps. Published images are linked, not stored in the
repo.

| Map | Edition and date | Shows | Where |
| --- | --- | --- | --- |
| Street scene, *Volo's Guide to the North*, p. 132 | 2nd edition (1993); 1360s DR | Illustration, not a map | [File:Neverwinter VGttN.jpg][mapvgttn] |
| Neverwinter Wood and vicinity, *Dungeon* #28, "Visitors from Above", p. 52 | 2nd edition era (1991) | Region east of the city | [File:Neverwinter and vicinity.png][mapdungeon] |
| Neverwinter Wood (2nd edition) | 2nd edition; source not read | Region | [File:Neverwinter Wood2e.jpg][mapwood2e] |
| Regional excerpt | 3rd edition | Neverwinter, Luskan, Neverwinter Wood, Mere of Dead Men | [File:Neverwinter location.JPG][map3e] |
| Labelled city map by Mike Schley, *Neverwinter Campaign Setting*, p. 139 | 4th edition (2011); 1479 DR | Whole city, districts, Chasm | [File:Mike Schley Neverwinter vertical.png][mapschleyv]; also [File:Mike Schley Neverwinter.jpg][mapschley] |
| City map by Jared Blando, *Sword Coast Adventurer's Guide*, p. 52 | 5th edition (2015); circa 1491 DR | Whole city | [File:Neverwinter R 72dpi.jpg][mapscag] |
| City map from *Cold Steel and Secrets* | Edition and date not checked | City | [File:Cold Steel and Secrets map.png][mapcss] |
| Environs map | *Neverwinter Nights* (AOL game, 1991 to 1997) | Environs | [File:Neverwinter AOL.png][mapaol] |
| Interactive map | Base image `Neverwinter-Map-Horizontal.jpg` from *Neverwinter Campaign Setting* (4th edition, 1479 DR) | 18 markers (below) | [Map:Neverwinter][mapint] |

### Interactive map markers

[Map:Neverwinter][mapint] (read 2026-10-13) places 18 markers on a 1440 by 1015
image, coordinates x then y with the origin at the bottom left. Orientation is
inferred, not stated: the harbour features (Fisher's Float, Pirates' Skyhold) sit
at the left edge and the Neverwinter River enters from the right, so west is
probably left and north up.

| Marker | x | y | Kind |
| --- | --- | --- | --- |
| Protector's Enclave | 453 | 291 | District |
| Blacklake District | 442 | 647 | District |
| River District | 827 | 595 | District |
| Castle Never | 451 | 515 | Castle |
| Chasm | 1027 | 327 | Natural feature |
| Blacklake | 588 | 739 | Natural feature |
| Neverwinter River | 1348 | 525 | Natural feature |
| Pirates' Skyhold | 104 | 926 | Harbour feature |
| Fisher's Float | 83 | 74 | Harbour feature |
| Moonstone Mask | 171 | 442 | Festhall |
| Hall of Justice | 341 | 411 | Temple |
| House of Knowledge | 690 | 495 | Temple |
| Dolphin Bridge | 411 | 436 | Bridge |
| Winged Wyvern Bridge | 507 | 440 | Bridge |
| Sleeping Dragon Bridge | 554 | 499 | Bridge |
| The Wall | 733 | 386 | Landmark |
| Cloak Tower | 1252 | 605 | Landmark |
| Shard of Night | 900 | 767 | Landmark |

No working sketch was drawn in this run.

## Engine Record

| Field | Value |
| --- | --- |
| Population | 23,000 (gazetteer estimate, no year) |
| Wealth / tax / security | 1.1 / 0.06 / 0.7 |
| Port / river | Sea of Swords / yes |
| Terrain | Coast |
| Position | x 439.7, y 1012.6 (stored and `coords.json` control point agree) |
| Traits | `port`, `cosmopolitan`, `craft`, `frontier` |
| Industries | `craft` 3, `fish` 2, `glass` 2, `log` 1, `ship` 2, `smith` 2, `trade` 2, `tag_volcanic_ash` 2, `tag_wolfsbane` 2 |
| Specialties | `glassware` 2, `clothing_fine` 1, `lantern` 1 (added 2026-10-13) |
| Shortages | None |
| Ruler | Lord Protector Neverember |
| Size category | Small city |
| Guilds (inferred) | Merchant; Fishers' and Watermen's; Smiths' and Armorers'; Artisans' |

Observed 2026-10-13 before this run's changes (`get_trade_summary`, 12
Marpenoth 1492 DR): gross local product 3.36 million gp a year (146 gp per
resident); goods exports 2,827 gp a day against imports of 1,062,351 gp a day
(about 376 times); 147,415 gp a day of inbound freight assigned to no carrier.
Leading export volumes are grain (895 bushels a day), fruit (354 crates) and
vegetables (328 crates), although the city has no `farm` or `orchard` industry;
fresh fish shows 754 barrels a day of uncommitted supply but no exports. Tin
(18 ingots a day) and copper (26) are in surplus with no mines, and wolfsbane
and volcanic ash (about 43 a day each) come from the two tag industries.
Glassware exports are about 2.1 crates a day. The import list is led by
unavailable goods (citrus, pears, pineapple, deep rothe cheese, remorhaz chitin
plate, clockwork mechanism, woolly mammoth, llama) each with a flat 46-a-day
need (0.2% of residents).

After this run's change the city makes about 11.8 hooded lanterns a day from
iron ingots and glassware, uses 3.3 locally and has about 8.5 a day to export.

## Discrepancies and Proposed Engine Changes

| # | Issue | Proposal | Status |
| --- | --- | --- | --- |
| N1 | Glass lamps are a named product of the city's crafters (*Cyclopedia of the Realms*, pp. 66 to 67; *Volo's Guide to the North*, pp. 132 to 134); no lamp good was produced | Add specialty `lantern` 1 (hooded lantern, the nearest commodity, made by `smith` and `glass`) | Applied 2026-10-13 |
| N2 | Description was a single line | Set description from the sources (High Road port, warm river and ice-free harbour, crafts, 1451 DR destruction, Neverember's rebuilding, Gauntlgrym trade, ruins around the Chasm) | Applied 2026-10-13 |
| N3 | Ruler "Lord Protector Neverember" omitted the forename | Set ruler to "Lord Protector Dagult Neverember" (circa 1491 DR, *Sword Coast Adventurer's Guide*, pp. 51 to 52); 1492 succession not independently verified | Applied 2026-10-15; 1492 DR unverified |
| N4 | Engine 23,000 has no source count; 23,192 predates the 1451 DR destruction and no rebuilt-city total is known | `populations.py` now records 23,192 as historical evidence while retaining 23,000 as an undated 1492 planning estimate, not a census | Evidence applied 2026-10-15; new count unresolved |
| N5 | Grain (895 bushels a day), fruit (354 crates) and vegetables (328 crates) were previously reported as city exports despite no `farm` or `orchard` industry | The raw-resource floor explicitly represents the city **and inferred accessible mainland hinterland**, not city-field yields. Keep this inference pending a separate local-versus-hinterland trade-account distinction; historical figures above predate this clarification | Clarified 2026-10-15; provenance distinction still proposed |
| N6 | Imports about 376 times exports, driven by the flat 46-a-day need for unavailable exotic goods; 147,415 gp a day of inbound freight has no carrier | Review with W5, W6, L14, Y12 | Proposed (engine-wide) |
| N7 | Tin and copper ingots in surplus with no mines | Review with D17 | Proposed (engine-wide) |
| N8 | Hothouse gardens supplied fruit and winter flowers (*The Savage Frontier*, pp. 31 to 32), but `orchard` has no climate gate and would start an olive chain (P18) | Add `orchard` 1 after P18 is fixed | Proposed |
| N9 | Water clocks are a named product, but `lantan_clockwork` is made only by `tag_lantan_clockwork` | Add a water clock commodity or let `craft` make clockwork after W4 | Proposed |
| N10 | `tag_volcanic_ash` 2 and `tag_wolfsbane` 2 have no source in the article; volcanic ash is plausible near Mount Hotenow, wolfsbane is unsourced | Review both with W4 | Proposed |
| N11 | Specialty `clothing_fine` 1 has no source | Review | Proposed |
| N12 | The engine infers four guilds with real power; sources say no guilds restricted trade around 1491 DR (*Sword Coast Adventurer's Guide*, pp. 52 to 53) and that Neverember barred new guilds and limited existing ones (*Storm King's Thunder*, p. 101) | Lower guild power and enforcement for Neverwinter, or mark the guilds as limited by law | Proposed |
| N13 | Ruins and monster-plagued neighbourhoods around the Chasm in 1491 DR (*Storm King's Thunder*, p. 101; *Princes of the Apocalypse*, p. 36) | Consider lower security or wealth during the rebuilding; no change without a model rule | Proposed |
| N14 | High Road neighbours Leilon and Port Llast (about 60 miles) have no direct link; Luskan has a road but no sea lane; the harbour is ice-free in winter | Add High Road stops (with L5), check the Luskan sea lane, keep the sea lane open year-round | Proposed (routes phase) |
| N15 | Gauntlgrym trade alliance forming circa 1491 DR (*Sword Coast Adventurer's Guide*, pp. 52 to 53); 14th century Underdark mining trade through city warehouses | Add Gauntlgrym as a settlement and route when the Underdark links are reviewed | Proposed (routes phase) |
| N16 | Ironstar Forge Company and North Coast High Road Freight are engine-authored | Leave | No change |
| N17 | Laerakond traders (before 1479 DR) and the Thayan enclave (video game) belong to periods before 1492 DR | Do not model | No change |
| N18 | Moonstone Mask and the taverns are named but not dated for 1491 DR | Add once lodging or services exist and a late source is found | Proposed |
| N19 | `reload_catalog` moved Amphail again (A12, eleventh time; x 621.7, y 1126); Neverwinter unaffected because its stored position equals its control point | Restored Amphail by hand to x 648.5289, y 1161.7169; decide L12 | Historical observation; local fix validated 2026-10-15, live server pending |

## Proposed New Commodities

| Candidate | Evidence | Producers |
| --- | --- | --- |
| Jewelry (existing candidate) | Fine jewellery famed across Faerun (14th century DR, *Cyclopedia of the Realms*, pp. 66 to 67) | `craft` |
| Water clock | Accurate water clocks, a named product (14th century DR, same sources) | `craft`, `smith` |
| Decorative glass lamp | Multicoloured glass lamps (same sources); `lantern` stands in | `glass`, `smith` |
| Cut flowers (existing candidate) | Hothouse gardens kept flowers through winter (*The Savage Frontier*, pp. 31 to 32) | `farm` |

## Lore Follow-ups

1. **Population of the rebuilt city.** No figure for 1479 or 1491 DR; check
   *Neverwinter Campaign Setting*, pp. 86 to 90, and *Sword Coast Adventurer's
   Guide*, pp. 51 to 53 (N4).
2. **2nd-edition city plan.** Check *Volo's Guide to the North*, pp. 130 to 134,
   and *The North* (Cities and Civilization) for a city map, and identify the
   edition of the *Cold Steel and Secrets* map.
3. **Crafts after 1451 DR.** Whether the glass lamp, water clock and jewellery
   trades were restored by 1491 DR (N1, N9).
4. **Gauntlgrym.** What the trade alliance exchanged, and whether it was in force
   in 1492 DR (N15).
5. **Guilds.** Reconcile "no guilds restricting trade" with Neverember's guild
   limits, and their dates (N12).
6. **Chasm.** Sealed around 1484 or 1485 DR; the article gives both.
7. **Neighbouring places.** Helm's Hold, Vilnask and Floodblest positions and
   size; none is in the engine.
8. **Earlier leads kept from the 2026-10-01 review.** Paul Joyce's 2018 fan
   overview (unfrozen harbour, Protector's Enclave markets, Hall of Justice)
   remains a lead only; its harbour and markets claims now agree with the wiki,
   but it was not used as evidence. A Wikipedia claim of a slave market has no
   citation and was not used.

## Sources

**Directly consulted, secondary:** [Forgotten Realms Wiki: Neverwinter][frwiki],
accessed 2026-10-13 by direct fetch and through the browser; also
[Category: Inhabitants of Neverwinter][inh] (all 511 page records screened, a
selection of person articles read), [Category: Maps of Neverwinter][mapcat], the
map file pages linked above and [Map:Neverwinter][mapint], all accessed
2026-10-13. Publications named above are the wiki's references, not
independently checked: *Cyclopedia of the Realms* (1987), pp. 57, 66 to 67;
*Waterdeep and the North* (1987), pp. 3, 6, 9; *The Savage Frontier* (1988),
pp. 9, 31 to 32, 61; *Forgotten Realms Campaign Setting*, 2nd edition (1993),
p. 114, and 3rd edition (2001), pp. 176 to 177; *Volo's Guide to the North*
(1993), pp. 130 to 134; *The North* (1996), Cities and Civilization, pp. 14, 16;
*Neverwinter Campaign Setting* (2011), pp. 8, 16, 20, 86 to 90, 108, 138 to 139,
143 to 148; *The Rise of Tiamat* (2014), pp. 14 to 15; *Lost Mine of Phandelver*
(2014); *Sword Coast Adventurer's Guide* (2015), pp. 7, 51 to 53, 145;
*Princes of the Apocalypse* (2015), p. 36; *Storm King's Thunder* (2016), pp. 56,
101, 232; *Tomb of Annihilation* (2017), p. 58; *Storm Lord's Wrath* (2019);
*Icewind Dale: Rime of the Frostmaiden* (2020), pp. 156, 159; *Dungeon* #28
(1991), p. 52; video games *Neverwinter Nights* (2002), *Neverwinter Nights 2:
Storm of Zehir* (2008) and *Neverwinter* (2013).

**Directly consulted, secondary:** [Wikipedia: Neverwinter][wp], accessed
2026-10-13, for its population figure and citations only.

**Kept from the 2026-10-01 review:** [Realms Helps: The North][north] (secondary;
Nasher-era crafts, gardens, bridges and 23,192 inhabitants); [D&D Beyond: Basic
Rules (2014), Appendix C][factions] (primary; Lords' Alliance); [Paul Joyce: The
city of Neverwinter][joyce] (fan compilation, provenance assessment only).

**Engine:** `get_settlement`, `get_trade_summary`, `get_price` (`lantern`),
`get_city_directory`, [businesses.json](../../../faerun/data/store/businesses.json)
and [commodities.json](../../../faerun/data/store/commodities.json), observed
2026-10-13.

[frwiki]: https://forgottenrealms.fandom.com/wiki/Neverwinter
[inh]: https://forgottenrealms.fandom.com/wiki/Category:Inhabitants_of_Neverwinter
[mapcat]: https://forgottenrealms.fandom.com/wiki/Category:Maps_of_Neverwinter
[mapint]: https://forgottenrealms.fandom.com/wiki/Map:Neverwinter
[mapvgttn]: https://forgottenrealms.fandom.com/wiki/File:Neverwinter_VGttN.jpg
[mapdungeon]: https://forgottenrealms.fandom.com/wiki/File:Neverwinter_and_vicinity.png
[mapwood2e]: https://forgottenrealms.fandom.com/wiki/File:Neverwinter_Wood2e.jpg
[map3e]: https://forgottenrealms.fandom.com/wiki/File:Neverwinter_location.JPG
[mapschleyv]: https://forgottenrealms.fandom.com/wiki/File:Mike_Schley_Neverwinter_vertical.png
[mapschley]: https://forgottenrealms.fandom.com/wiki/File:Mike_Schley_Neverwinter.jpg
[mapscag]: https://forgottenrealms.fandom.com/wiki/File:Neverwinter_R_72dpi.jpg
[mapcss]: https://forgottenrealms.fandom.com/wiki/File:Cold_Steel_and_Secrets_map.png
[mapaol]: https://forgottenrealms.fandom.com/wiki/File:Neverwinter_AOL.png
[wp]: https://en.wikipedia.org/wiki/Neverwinter
[north]: https://www.realmshelps.net/faerun/north.shtml
[factions]: https://www.dndbeyond.com/sources/dnd/basic-rules-2014/appendix-c-the-five-factions
[joyce]: https://www.pauljoyce.co.uk/2018/neverwinter-city-facts-features-timline-dnd-forgotten-realms/
