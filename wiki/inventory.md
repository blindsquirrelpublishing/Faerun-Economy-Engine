# Location Inventory

[Location index](README.md)

Working tracker for the location-by-location review that started 2026-10-03.
Each location gets a folder under `locations/` (page in `README.md`, with its
maps, sketches and metadata alongside) with its engine record, lore,
businesses, discrepancies and proposed changes. Nothing in the proposal lists is
applied until it is approved. Routes, feasibility and carriers come in a later
phase.

## Queue

Ordered by straight-line distance from Waterdeep. "S" marks a surveyed
(auto-generated) market rather than an established settlement.

| # | Location | Miles | Engine pop. | Status |
| --- | --- | --- | --- | --- |
| 1 | [Waterdeep](locations/waterdeep/README.md) | 0 | 200,000 | Done 2026-10-03 |
| 2 | [Amphail](locations/amphail/README.md) | 62 | 850 | Done 2026-10-04 |
| 3 | [Goldenfields](locations/goldenfields/README.md) | 90 | 3,000 | Done 2026-10-05 |
| 4 | [Red Larch](locations/red-larch/README.md) | 109 | 1,100 | Done 2026-10-06 |
| 5 | [Daggerford](locations/daggerford/README.md) | 123 | 900 | Done 2026-10-07 |
| 6 | [Triboar](locations/triboar/README.md) | 156 | 2,500 | Done 2026-10-08 |
| 7 | [Phandalin](locations/phandalin/README.md) | 159 | 500 | Done 2026-10-09 (existing page reviewed) |
| 8 | [Stone Bridge](locations/stone-bridge/README.md) (S) | 160 | 80 | Done 2026-10-10 (a landmark bridge and temple, not a settlement; see SB2) |
| 9 | [Leilon](locations/leilon/README.md) | 192 | 900 | Done 2026-10-11 (stored position is 186 miles; see L13) |
| 10 | [Yartar](locations/yartar/README.md) | 213 | 3,800 | Done 2026-10-12 |
| 11 | [Neverwinter](locations/neverwinter/README.md) | 247 | 23,000 | Done 2026-10-13 (existing page reviewed) |
| 12 | [Secomber](locations/secomber/README.md) | 248 | 1,300 | Done 2026-10-14 |
| 13 | [Orlumbor](locations/orlumbor/README.md) | 268 | 3,000 | Done 2026-10-15 |
| 14 | [Longsaddle](locations/longsaddle/README.md) | 270 | 700 | Done 2026-10-16 |
| 15 | Port Llast | 304 | 800 | Next |

Further out: Warlock's Crypt (S), Dragonspear Castle (S), [Griffon's Nest](locations/griffons-nest/README.md) (S),
Loudwater, Grandfather Tree (S), Mintarn, Luskan, Nesme, Jalanthar, Everlund,
Mirabar, Silverymoon, Mithral Hall, Llorkh, Baldur's Gate, Boareskyr Bridge.

## Proposed Economy Changes

Collected from each page's discrepancy table; see the page for evidence.

| ID | Location | Proposal | Status |
| --- | --- | --- | --- |
| W1 | Waterdeep | Add `fish` 2 | Proposed |
| W2 | Waterdeep | Add `tan` 1, `pottery` 1 | Proposed |
| W3 | Waterdeep | Add `weapon` 1, `armor` 1 | Proposed |
| W4 | Engine-wide | Review tag-industry output scaling (5,382 a day surplus per tag at Waterdeep) | Proposed |
| W5 | Engine-wide | Review the flat 400-a-day import need for unavailable goods | Partially fixed 2026-10-15: unmodeled livestock and large durable assets no longer receive daily per-capita orders. Generic foods (e.g. Waterdeep citrus, 400 crates/day) still do; commodity-specific diet/substitution evidence needed before changing them |
| W6 | Engine-wide | Review goods output and import valuation | Partially fixed 2026-10-15: spurious durable orders accounted for much of Waterdeep's value; output fell from 2,298,013 to 207,609 gp/day and imports from 1,127,823 to 108,382 gp/day in a fresh local World. Constant-price GLP and matched gate-price invoices remain unchanged. W4 tag scaling and the remaining food demand are open |
| W7 | Waterdeep | Keep or replace the `wool` shortage | Open question |
| W8 | Waterdeep | Fix Helmstar Warehouse's `crate` offer | Proposed |
| W10 | Waterdeep | Promote selected Volo directory businesses to the market | Proposed |
| A1 | Amphail | Add `tan` 1 (Eagleshield tack makers) | Applied 2026-10-04 |
| A2 | Amphail | Add specialty `ale` 1 (Stag-Horned Flagon beer) | Applied 2026-10-04 |
| A3 | Amphail | Set description from the source | Applied 2026-10-04 |
| A4 | Amphail | Set ruler to Lord Warder Dauner Ilzimmer (1485 DR figure) | Applied 2026-10-04 |
| A5 | Amphail | Population 850 (circa 1372 DR, village plus farms), 900 kept as comparison | Applied 2026-10-04 |
| A6 | Amphail | Keep region `Dessarin Valley`: Princes of the Apocalypse p. 31 (via the wiki's Dessarin Valley article) lists it as a Dessarin village; Volo's page numbers place it in The Dessarin chapter; see the Amphail page | No change needed |
| A7 | Amphail | No bread output: active generated famine leaves about 2 sacks of flour a day, all taken by households; `craft` was not the cause. Recheck after the famine | Deferred |
| A8 | Amphail | Remount Company address says High Road: leave; generated addresses are placeholders. Later, consider replacing the firm with a sourced breeder (with A11) | No change |
| A9a | Engine-wide | Draft horses get a world-wide hinterland capacity multiplier of about 134 (riding horses none); trace the rule. Amphail's `horse` level is not the cause | Cause found 2026-10-08: only four towns had the `horse` tag, so source-district calibration scaled them to world demand. Draft horses and ponies now also list `farm` as a producer (as mules and oxen do); Amphail draft horses fall to about 4 a day. Warhorse (A9b) untouched |
| A9b | Engine-wide | Warhorse capacity near zero (about 1.4 a year at Amphail) despite the specialty; trace why. First priority of Amphail's engine fixes | Proposed; recheck after famine |
| A10 | Engine-wide | Cotton grows anywhere with `farm` or `textile` (Waterdeep 214 a day spare). For the commodity review: drop `textile` as a producer; stop cold-region farms producing it | Deferred |
| A11 | Amphail | Stag-Horned Flagon added as a market business (operating circa 1490 DR, Storm King's Thunder p. 72); Eagleshield Fine Horse Leathers waits for a source near 1492 DR | Flagon applied 2026-10-04; Eagleshield proposed |
| A12 | Engine-wide | After `reload_catalog` the live server moved Amphail to x 621.7, y 1126 with no neighbours (disk unchanged); live position restored 2026-10-04 via `update_settlement`. Recurred 2026-10-05 after the Goldenfields run's `reload_catalog` (same x 621.7, y 1126; Goldenfields unaffected) and was restored again the same way; recurred again 2026-10-06 after the Red Larch run's `reload_catalog` (same position) and was restored the same way; recurred again 2026-10-07 after the Daggerford run's `reload_catalog` (same position) and was restored the same way; recurred again 2026-10-08 after the Triboar run's `reload_catalog` (same position) and was restored the same way; recurred twice on 2026-10-09 after both of the Phandalin run's `reload_catalog` calls (same position; stored position on disk confirmed unchanged) and was restored the same way each time; recurred again 2026-10-10 after the Stone Bridge run's `reload_catalog` (same position) and was restored the same way; recurred again 2026-10-11 after the Leilon run's `reload_catalog` and was restored the same way. Recurred again 2026-10-12 after the Yartar run's `reload_catalog` (same position) and was restored the same way. Recurred again 2026-10-13 after the Neverwinter run's `reload_catalog` (same position) and was restored the same way. Recurred again 2026-10-14 after the Secomber run's `reload_catalog` (same position, no neighbours) and was restored the same way to x 648.5289, y 1161.7169. Recurred again 2026-10-15 after the Orlumbor run's `reload_catalog` (same position, no neighbours) and was restored the same way. Cause found 2026-10-11: x 621.7, y 1126 is Amphail's control point in `faerun/data/coords.json`. On 2026-10-15 the local `reload_catalog` fix replayed saved `maps/location-edits.json` positions after catalog calibration; the regression test and a fresh local world reload preserved x 648.5289, y 1161.7169. The running server has not been verified or restarted by this check. | Fixed in local code; live server verification pending |
| A13 | Engine-wide | Innarlith is the only salt producer in the engine; lore says most regions made salt locally. Applied: `salt` 1 at Mintarn (named rock-salt mines; about 112 sacks a day). Moonshae and Anauroch sources to add when reviewed; recheck Waterdeep's 256 a day need after the snapshot refresh | Applied 2026-10-04 |
| C1 | Engine-wide | Coin standard (50 coins to the lb, 4% minting loss, 48 coins per lb). Applied: `platinum_ingot` 550 to 2,400 gp (480 pp), `silver_ingot` 50 to 48 gp, `copper_ingot` 5 to 4.8 gp, `gold_ingot` 500 to 480 gp. Platinum now trades about 1,326 gp at Citadel Adbar (was 304) and about 5,100 gp in non-producing markets (was about 1,170). Price snapshots stale; refresh before relying on cached prices. See [the coin standard](commodities/README.md#coin-standard) | Applied 2026-10-04 |
| C2 | Engine-wide | Ale producer gate price does not follow imported grain: Ravens Bluff sells at 1.19 gp a keg against 3.07 gp of grain per keg; Baldur's Gate clears 0.07 gp. Trace whether gate prices use local rather than blended input cost. See [Ale cross-check](commodities/drink/ale.md#cost-roll-up-cross-check) | Proposed |
| C3 | Waterdeep | Brews 8,093 kegs a day on grain that is 2% local at about 7 gp a bushel, then supplies 61% of Neverwinter's ale at 8.64 gp landed. Review with W4 and W5 | Proposed |
| C4 | Engine-wide | Ale price anchors disagree: engine 0.167 gp a gallon, *Aurora's* 0.045 to 0.175, Waterdeep Trading Company guide 1.50 FSD. Decide the anchor and whether FSD equals gp; confirm the 80 lb keg excludes the cask | Open question |
| C5 | Engine-wide | Ale now consumes `barley` (0.8 bushel/keg); [barley](commodities/food/barley.md) grows via `farm` with the grain harvest calendar. The existing ale price anchor and fuel/malt questions (C4, C6) remain open | Applied to grain substitution 2026-10-15; C4/C6 open |
| C6 | Engine-wide | Proposed ale formulation: keep grain 0.8, add firewood (`timber` 0.06 load); optional `malt` intermediate between two routes. Rolls up to about 1.00 gp against 1.6 gp. See [Ale formulation](commodities/drink/ale.md#formulation-proposed) and [brewing equipment](equipment/brewing/README.md) | Proposed |
| C7 | Engine-wide | Mead recipe uses 0.6 crock of honey a keg, about a fifth of normal strength. At 3 lb a gallon (2.88 crocks) honey alone is 4.32 gp against a 2.5 gp price, and no market breaks even. Decide: call it small mead, or raise honey and price (about 5 to 6 gp; *Aurora's* implies about 4.8 gp a keg). See [Mead](commodities/drink/mead.md#cost-roll-up-cross-check) | Open question |
| C8 | Engine-wide | Table wine now consumes 6 crates of `grapes` (180 lb/cask); vineyards (`vint`) supply grapes with a late-summer/autumn harvest, while cellar work continues year-round. The 0.55 gp/crate grape input totals 3.30 gp before labour against a 4 gp wine base price. This is a model estimate, not a canonical grape price. Baseline plan now makes ~3,689 wine casks/day and ~24,824 grape crates/day across the catalogue (6 × planned wine = ~22,137 crates/day), so annual supply is sufficient in aggregate; local shipment costs and harvest-month bottlenecks still need checking | Applied to input/harvest 2026-10-15; calibration open |
| C9 | Engine-wide | Bottled drinks (brandy, fire-wine, starflower wine) have no bottle in the recipe, though a glass bottle (about 1.6 gp) is their largest material cost. Brandy uses 0.08 cask of wine a bottle, about half of an 8-to-1 still yield. Zazesspur (about 4,000 bottles a day) gates brandy at its wine cost, 5.37 against 5.23 gp | Proposed |
| C10 | Engine-wide | Single-tag drinks (duergar grey ale, kelp ale, Reghed frost mead, fire-wine, starflower wine) have no recipe and each produce a flat 6,972.86 units a day whatever the place (demand 2.4 to 124). Give them recipes; trace the flat output with W4. Kelp ale stores 365 days though its description says it goes flat within a season | Proposed |
| C11 | Engine-wide | Cider deferred: `fruit` and tag-only `apples` each cost 1 gp/30 lb crate; a 5 to 7.2 crate batch already exceeds the 2 gp catalogue and ~4.43 gp scaled cask before conversion. Need a defensible cull price/yield and orchard placement before adding a cider commodity or replacing this recipe with free fruit | Deferred pending evidence 2026-10-15 |
| C12 | Engine-wide | Wine retail falls below the producer gate in six of ten producing markets in autumn; the 0.8 season factor seems to discount the shelf price but not the gate | Proposed |
| C13 | Engine-wide | Glassware recipe is 0.05 sack of coal per crate, about a fiftieth of a furnace's fuel, with no sand, flux or lime. Five of six glassworks (Athkatla, Almraiven, Halarahh, Calimport, Waterdeep) have no local fuel; at real fuel use three of them (Athkatla, Almraiven, Halarahh) would spend 1.5 to 2.8 times their gate price on fuel. See [Glassware](commodities/product/glassware.md#cost-roll-up-cross-check) | Proposed |
| G1 | Goldenfields | Add `herb` 1 (herbs a named export) | Applied 2026-10-05 |
| G2 | Goldenfields | Add specialties `corn` 1, `rice` 1 (named exports) | Applied 2026-10-05 |
| G3 | Goldenfields | Set description from the sources | Applied 2026-10-05 |
| G4 | Goldenfields | Goldengulp Brewery added as a market business (`ale`; about 60 workers, late 15th century DR, Storm King's Thunder, p. 48) | Applied 2026-10-05 |
| G5 | Goldenfields | Set ruler to Abbot Ellardin Darovik (1491 DR, Princes of the Apocalypse, p. 33) | Proposed |
| G6 | Goldenfields | Population 3,000 (no source) to about 5,000 (1491 DR), with a `populations.py` entry | Proposed |
| G7 | Goldenfields | `river` true and a road link: lore puts it on the west side of the Dessarin; engine has one wilderness track | Proposed (routes phase) |
| G8 | Goldenfields | Apples and oranges are named exports but only tag industries make `apples` and `citrus`; add after W4, or let `orchard` make apples | Proposed |
| G9 | Goldenfields | `tag_yoke` 2 makes about 6,967 yokes a day with no source; lower, remove or rescale with W4 | Proposed |
| G10 | Goldenfields | Sources say the food is given away in Chauntea's honour; decide whether to model gifts or tithes; review `tag_surplus_grain` scale with W4 | Open question |
| G11 | Goldenfields | Add `herd` 1 (sheep and pigs in pens, Storm King's Thunder, p. 46) | Proposed |
| G12 | Goldenfields | Unsourced shortages `iron_ingot`, `silk`, `gem_agate`; review or clear | Proposed |
| G13 | Engine-wide | Pears unavailable at Goldenfields despite `orchard` 3 (only `tag_pears` makes them): let `orchard` produce pears. Also trace cattle exports (192 a day) exceeding stock (36 a tenday) | Proposed |
| G14 | Goldenfields | Northfurrow's End (inn) and Earth Mother's Bounty (seeds) operate circa 1485 DR; add when lodging or seed goods exist | Proposed |
| G15 | Goldenfields | Golden Sheaf Provisions is engine-authored; leave, consider renaming later | No change |
| R1 | Red Larch | Add `tan` 1 (Luruth's Tannery, 1491 DR; harness-makers 1366 and 1491 DR) | Applied 2026-10-06 |
| R2 | Red Larch | Add specialties `wagon` 1 and `saddle` 1 (wagonworks and harness-makers) | Applied 2026-10-06 |
| R3 | Red Larch | Add specialties `chicken` 1 and `eggs` 1 (Mhandyvver's Poultry, 1366 and 1491 DR) | Applied 2026-10-06 |
| R4 | Red Larch | Set description from the sources | Applied 2026-10-06 |
| R5 | Red Larch | Add market businesses Mhandyvver's Poultry, Chansyrl Fine Harness, Thelorn's Safe Journeys, Luruth's Tannery (all operating 1491 DR, Princes of the Apocalypse) | Applied 2026-10-06 |
| R6 | Red Larch | Population 1,100 (no source) to 600 (infobox; year unclear), with a `populations.py` entry | Proposed |
| R7 | Red Larch | Set ruler to Constable Harburk Tuthmarillar (1491 DR); Jalessa Ornra "most likely" mayor afterwards | Proposed |
| R8 | Red Larch | Add `cattle` 1 (cattle market circa 1366 DR; Stalnstern ranch circa 1372 DR) | Proposed |
| R9 | Red Larch | Review `granite` 2, `bricks` 1 and marble output: sources never name the stone, and say Lance Rock's granite is unlike local stone | Proposed |
| R10 | Red Larch | Add `smith` 1 (blacksmith 1491 DR; Ironhead Arms 1488 DR) | Proposed |
| R11 | Red Larch | Add `orchard` 1 (Gulther hornapple orchard, circa 1372 DR); low priority | Proposed |
| R12 | Red Larch | Link Red Larch to Amphail on the Long Road (engine runs straight to Waterdeep, 109.7 miles, 5.4 days; source says seven days); Cairn Road to Bargewright Inn; Kheldell trail | Proposed (routes phase) |
| R13 | Red Larch | Add further 1491 DR businesses (Waelvur's Wagonworks, Mellikho stoneworks, Tantur smithy, Ironhead Arms, bakery, butcher, clothier, inns) | Proposed |
| R14 | Engine-wide | Red Larch sheep exports 47 a day against 15 a tenday in stock; imports about 120 times exports; cotton in a hill village. Review with G13, W5, W6, A10 | Proposed |
| R15 | Engine-wide | `harness` is made only by `tag_harness`; let `tan` produce harness (Red Larch, Amphail, Triboar), after W4 | Proposed |
| R16 | Engine-wide | Thelorn's wagons cost about 150 gp circa 1366 DR against the 35 gp catalogue price; compare in the commodity review | Proposed |
| D1 | Daggerford | Add `hunt` 1 and specialty `furs` 1 (furs a named export) | Applied 2026-10-07 |
| D2 | Daggerford | Add specialty `clothing_common` 1 (garments a named export) | Applied 2026-10-07 |
| D3 | Daggerford | Add `ship` 1 (river shipyards: Sullerton, late 15th century DR; Mikitan, Dekoran, 14th century DR) | Applied 2026-10-07 |
| D4 | Daggerford | Add `tan` 1 (tannery and tanners' guild) | Applied 2026-10-07 |
| D5 | Daggerford | Add `brew` 1 (Daggerthrust Ales, late 15th century DR) | Applied 2026-10-07 |
| D6 | Daggerford | Add `fish` 1 (Flying Fish packed fish for the Trade Way, mid 14th century DR) | Applied 2026-10-07 |
| D7 | Daggerford | Set description from the sources | Applied 2026-10-07 |
| D8 | Daggerford | Set region `Delimbiyr Vale` (wiki infobox; matches Loudwater and Llorkh); zone unchanged | Applied 2026-10-07 |
| D9 | Daggerford | Add market businesses Daggerthrust Ales, Miller's Dry Goods, Gublin's Cloth & Cordage, Derval's Smithy, Cromach's Smithy, Sullerton Shipbuilders (all operating circa 1485 DR, Scourge of the Sword Coast) | Applied 2026-10-07 |
| D10 | Daggerford | Population 900 (no source) to 1,200 (1485 DR), 891 (1372 DR) as comparison, with a `populations.py` entry; update the Daggerford analysis evidence | Proposed |
| D11 | Daggerford | Set ruler to Duchess Morwen Daggerford (1489 DR; possibly the succubus Pencheska) | Proposed |
| D12 | Daggerford | River port: docks, river-to-caravan transfer, boats to Secomber; model as a river lane, not a sea basin | Proposed (routes phase) |
| D13 | Daggerford | Add shortage `timber` (lumber imported from Andalor's Mill, Bowshot); river boat output is near zero for lack of planks | Proposed |
| D14 | Daggerford | `vint` 1 for Daggerford clarry (video game source only) | Proposed (low confidence) |
| D15 | Daggerford | Specialty `cheese` 1 for Churlgo Cheese (video game source only) | Proposed (low confidence) |
| D16 | Daggerford | Add further late-15th-century businesses (Jerdan's Smithy, Trade of the Tools, bank, taverns, inns, Clean Chin) | Proposed |
| D17 | Engine-wide | `smith` makes tin and copper ingots without ore (Daggerford shows surpluses); review with W4, W6 | Proposed |
| D18 | Engine-wide | Tea, medicinal herbs and cotton exported from Daggerford with no `herb` or `textile`; trace producers; review with A10 | Proposed |
| D19 | Daggerford | Only neighbour is a 4.8-mile road named "Daggerford Rtoad" (typo) to a junction; check Trade Way links | Proposed (routes phase) |
| D20 | Engine-wide | Carriers Waterdeep-Daggerford Caravan Company and Sword Coast Overland Exchange list `baldurs_gate`; the id is `baldur_s_gate` | Proposed (carriers phase) |
| D21 | Engine-wide | Generated business stock ignores value: Sullerton Shipbuilders holds 21 river boats (about 16,800 gp) | Proposed |
| D22 | Daggerford | Golden Sheaf Provisions and Trade Way Cartwrights are engine-authored; leave | No change |
| T1 | Triboar | Add `horse` 1 and specialties `horse_riding` 1, `pony` 1 (horses a named export; ranches and pony park after 1485 DR) | Applied 2026-10-08 |
| T2 | Triboar | Add `tan` 1 and specialty `saddle` 1 (leatherwork a named export; Othovir's harness) | Applied 2026-10-08 |
| T3 | Triboar | Add specialty `wagon` 1 (wagons a named export; Wainwright's Wagons) | Applied 2026-10-08 |
| T4 | Triboar | Add specialty `nails` 1 (ironware a named export; Uldinath's wagon fittings) | Applied 2026-10-08 |
| T5 | Triboar | Set description from the sources | Applied 2026-10-08 |
| T6 | Triboar | Add market businesses Wainwright's Wagons, Othovir's Harness Shop, Foehammer's Forge, Uldinath's Arms, Happy Horse Ranch, Merivold Pony Park, The Cart and Coin (all after 1485 DR, Storm King's Thunder) | Applied 2026-10-08 |
| T7 | Triboar | Set ruler to Lord Protector Darathra Shendrel (1491 DR) | Proposed |
| T8 | Triboar | Keep population 2,500 (about 2,500 in 1357, 1368 and 1370 DR) and add a `populations.py` entry; nearly half live on outlying farms in the late 15th century DR | Proposed |
| T9 | Triboar | Review `cattle` 3 and `cow` 2 against horses and wagons; `meat_salt` 1 unsourced | Proposed |
| T10 | Triboar | Raise `horse` to 2 after A9a, A9b and G13 (ponies export 174 a day against 15 a tenday in stock; draft horses 130 a day against 25) | Applied 2026-10-08 with the A9a fix: draft horses 24 a day, ponies 24 |
| T11 | Triboar | Raise `smith` to 2 (two smithies selling across the North in both eras) | Proposed |
| T12 | Triboar | Model the Triboar Travelers as a carrier (wagon rental to Waterdeep and Everlund) | Proposed (carriers phase) |
| T13 | Triboar | Add the Triboar Trail to Phandalin (about 225 miles); Yartar road 66 against 60 miles; the wiki's 200 miles to Red Larch conflicts with the engine's 51.2 | Proposed (routes phase) |
| T14 | Triboar | Add further businesses after 1485 DR (apothecary, The Lion's Share, inns and taverns) | Proposed |
| T15 | Engine-wide | Triboar exports medicinal herbs (30.6 a day) with no `herb`, tin and copper without ore, cotton; animal exports far above stock. Review with D17, D18, A10, G13, W4 | Proposed |
| P1 | Phandalin | Add `mine_gold` 1 (gold a named export; mining the main wealth, *Dragon of Icespire Peak*, p. 7) | Applied 2026-10-09 |
| P2 | Phandalin | Add `log` 1 (woodcutters, logging, timber export) | Applied 2026-10-09 |
| P3 | Phandalin | Add `hunt` 1 (trappers; skins export, video game source) | Applied 2026-10-09 |
| P4 | Phandalin | Set description from the sources | Applied 2026-10-09 |
| P5 | Phandalin | Add `orchard` 1 (Edermath Orchard) once olives and olive oil are limited to warm climates: the trial made Phandalin grow olives and import 23.9 barrels a day from Athkatla for an olive press | Proposed (applied and reverted 2026-10-09) |
| P6 | Phandalin | Platinum a named export, but only `tag_platinum_ore` makes platinum; add a source after W4 or a `mine_platinum` tag | Proposed |
| P7 | Phandalin | Remove the unsourced `silver_ingot` specialty and review `mine_silver` | Proposed |
| P8 | Phandalin | Cold iron (before 1374 DR, video game only): commodity candidate, no engine change | No change |
| P9 | Phandalin | Set ruler: Town Council (Harbin Wester, Sildar Hallwinter, Trilena Stonehill), early 1490s DR, year not given; or Townmaster Harbin Wester (1491 DR) | Proposed |
| P10 | Phandalin | Population 500 has no source; about 50 structures in 1491 DR suggest about 160 to 240 in the town core before farms and claims; add a `populations.py` entry or lower toward 250 to 300 | Proposed |
| P11 | Phandalin | Add `herd` 1 or `cattle` 1 (ranching land; Barthen's livestock brokering) | Proposed |
| P12 | Phandalin | Add market businesses Barthen's Provisions, Lionshield Coster post, Phandalin Miner's Exchange, Edermath Orchard, Stonehill Inn, The Sleeping Giant (all operating 1491 DR, *Lost Mine of Phandelver*) | Applied 2026-10-09 |
| P13 | Phandalin | Only link is the 86.5-mile Triboar trail; add Neverwinter and Leilon links and check Phandalin's position (120.5 miles from Neverwinter) with T16 | Proposed (routes phase) |
| P14 | Phandalin | The Smithy (Alger Frakk) recorded only for 1496 DR; add `smith` 1 and the business only with an earlier source | Proposed |
| P15 | Engine-wide | Phandalin makes gold (0.067 ingots a day) and furs (0.17 bundles a day) with no local demand and no exports; trace why, with W4, W6 | Proposed |
| P16 | Phandalin | Lionshield Coster's arms are rare with no stock (supplied from Sundabar); consider an inbound Yartar supply | Proposed (carriers phase) |
| P17 | Phandalin | Tourism after *In Volo's Wake* not modelled (visitor receipts 0.33 gp a day) | Proposed |
| P18 | Engine-wide | `orchard` produces olives and olive oil with no climate gate (`requires` is empty), so any northern orchard grows olives and imports more for pressing; check Goldenfields (`orchard` 3) and the other orchard towns | Proposed |
| SB1 | Stone Bridge | Set description from the source (dwarven bridge and temple to Moradin on the Stone Trail between Westbridge and Beliard; no settlement recorded) | Applied 2026-10-10 |
| SB2 | Stone Bridge | Surveyed market (80, copied from Red Larch) has no settlement basis: replace with a sourced village, Westbridge (450 in 1365 DR, at the west end) or Beliard (cattle-ranchers' trading village to the east); keep the bridge as a map landmark and route node | Proposed |
| SB3 | Stone Bridge | Population 80 is the surveyed-market floor with no source; treat as unknown or remove with SB2 | Proposed |
| SB4 | Stone Bridge | Engine position is about 51 to 56 miles east of the Long Road line (Red Larch x 646.2, Triboar x 641.5); sources put it between Westbridge on the Long Road and Beliard a few miles east. Re-check against the 2nd- and 5th-edition maps | Proposed (map) |
| SB5 | Stone Bridge | Model the Stone Trail (Westbridge, Stone Bridge, Beliard); review the 65.3-mile Triboar trail labelled "Red Larch and Goldenfields branch toward Secomber" | Proposed (routes phase) |
| SB6 | Stone Bridge | Set `river` true (bridge over the River Dessarin) if the market stays | Proposed (routes phase) |
| SB7 | Stone Bridge | `temple` 1 or a pilgrimage visitor flow for the temple to Moradin (1368 DR evidence only) if the market stays | Proposed |
| SB8 | Engine-wide | Stone Bridge exports timber, iron ore and dressed granite with no industries and imports about 3,687 gp a day (about 110 times its output) through flat 0.16-a-day needs for unavailable goods (longship, woolly mammoth). Review with W4, W5, W6, R14, T15 | Proposed |
| SB9 | Engine-wide | Beliard is a route neighbour of Stone Bridge (19.3-mile "Beliard Trail") but has no record in `settlements.json`; trace the node | Proposed |
| L1 | Leilon | Add `mine_copper` 1, `mine_silver` 1 (copper, nickel and silver from the eastern mines sold to Waterdeep, 14th century DR) | Applied 2026-10-11 |
| L2 | Leilon | Add `fish` 1 (fishing revived after the 1485 DR resettlement; the Fishery and Quayside) | Applied 2026-10-11 |
| L3 | Leilon | Set description from the sources | Applied 2026-10-11 |
| L4 | Leilon | Lower or remove `mine_iron` 2 and remove the `iron_ore` specialty (iron never named; "ore" export from a video game only) | Proposed |
| L5 | Leilon | No neighbours and no trade: the Neverwinter to Waterdeep Road bypasses Leilon; add it as a High Road stop, check links with P13 | Proposed (routes phase) |
| L6 | Leilon | Population 900 (no source) to 200 (1491 DR), 3,000 (1357 and 1370 DR) as comparison, with a `populations.py` entry | Proposed |
| L7 | Leilon | Set ruler to Lord Protector Dagult Neverember through a town council (1491 DR) | Proposed |
| L8 | Leilon | `port` Sea of Swords for the barge harbour (sea trade perilous and secondary to caravans); decide with L5 | Proposed (routes phase) |
| L9 | Leilon | Add `log` 1 and `hunt` 1 (timber and animal skins in the infobox, video game source set before 1385 DR) | Proposed (low confidence) |
| L10 | Leilon | Add `herd` 1 (giant goats bred for the town, circa 1491 DR) | Proposed |
| L11 | Leilon | Add late 15th century DR businesses (Torver's Post, the Fishery, barge yard, Zana Taylish's stall, Umber Hulk's Shell Inn, Old Knight's Goblet) after checking the 1492 DR state | Proposed |
| L12 | Engine-wide | `reload_catalog` applies `faerun/data/coords.json` control points over stored positions (Amphail x 621.7, y 1126; Leilon x 488.4, y 1050.8), and `update_settlement` saves the live position to `settlements.json`. Decide which file is authoritative for position (explains A12) | Proposed |
| L13 | Leilon | Live position before the run (x 458.9, y 1069.2) differed from the stored and control-point position (x 488.4, y 1050.8); the run's description update wrote 458.9 to disk and it was restored to 488.4 the same day. Check against the 2nd- and 5th-edition maps | Proposed (map) |
| L14 | Engine-wide | An isolated market still logs unmet needs up to 1.8 a day for exotic goods (llamas, Genasi glass censers); review with W5 | Proposed |
| Y1 | Yartar | Add `ship` 1 and specialty `ship_boat` 1 (barge-building; barges the listed export, Sword Coast Adventurer's Guide, p. 58) | Applied 2026-10-12 |
| Y2 | Yartar | Set description from the sources | Applied 2026-10-12 |
| Y3 | Yartar | Add market business Lionshield Coster (HQ Yartar; operating 1491 DR, Lost Mine of Phandelver, Storm King's Thunder); offers inferred from the Phandalin post | Applied 2026-10-12 |
| Y4 | Yartar | Population 3,800 (no source) to 6,000 (1366 DR, city; "increasingly crowded" in the late 15th century DR), with a `populations.py` entry | Proposed |
| Y5 | Yartar | Set ruler to Waterbaron Nestra Ruthiol (1491 DR) | Proposed |
| Y6 | Yartar | Food is the listed import (grain and produce from Goldenfields) but `farm` 2 exports 690 bushels of grain a day (hinterland multiplier about 4.15); lower `farm` to 1, consider a `grain` shortage, trace with A9a | Proposed |
| Y7 | Yartar | Specialty `barrel` 1 has no source; review | Proposed |
| Y8 | Yartar | Add `temple` 1 (Happy Hall of Tymora); model the Hiring Fair as a periodic visitor or labour event | Proposed |
| Y9 | Yartar | Surbrin and Dessarin river lane for barges and docks; decide with D12 | Proposed (routes phase) |
| Y10 | Yartar | Evermoor Way (Silverymoon 320 miles, Everlund 270), Surbrin Trail to Nesme; Triboar road 66 miles (T13) | Proposed (routes phase) |
| Y11 | Yartar | Add Wink and Kiss tavern (1491 DR, Princes of the Apocalypse, p. 176); the Grand Dame riverboat casino once services exist | Proposed |
| Y12 | Engine-wide | Yartar imports about 90 times exports (174,925 against 1,949 gp a day) through the flat 7.6-a-day need for unavailable goods; cotton and medicinal herbs exported without producers. Review with W5, W6, L14, A10, D18 | Proposed |
| Y13 | Engine-wide | After Y1 Yartar makes about one river boat a year; check `ship` capacity and whether a barge commodity is needed (with D21) | Proposed |
| Y14 | Engine-wide | Lionshield Coster has three unlinked records (Yartar, Phandalin, Triboar); consider one multi-location business | Proposed |
| N1 | Neverwinter | Add specialty `lantern` 1 (glass lamps a named product, 14th century DR; about 11.8 lanterns a day) | Applied 2026-10-13 |
| N2 | Neverwinter | Set description from the sources | Applied 2026-10-13 |
| N3 | Neverwinter | Set ruler to Lord Protector Dagult Neverember (1467 DR onward; circa 1491 DR) | Proposed |
| N4 | Neverwinter | Keep population 23,000 (no year) and add a `populations.py` entry: 23,192 (circa 1372 DR, before the 1451 DR destruction) as comparison, rebuilt-city figure unknown | Proposed |
| N5 | Engine-wide | Neverwinter exports grain (895 bushels a day), fruit and vegetables with no `farm` or `orchard`; trace hinterland farm output for non-farming cities with Y6, A9a, W4 | Proposed |
| N6 | Engine-wide | Neverwinter imports about 376 times exports (1,062,351 against 2,827 gp a day) through the flat 46-a-day need for unavailable goods; 147,415 gp a day of inbound freight unassigned. Review with W5, W6, L14, Y12 | Proposed |
| N7 | Engine-wide | Neverwinter tin and copper ingot surpluses with no mines; review with D17 | Proposed |
| N8 | Neverwinter | Add `orchard` 1 for the hothouse gardens after P18 (olive climate gate) | Proposed |
| N9 | Neverwinter | Water clocks a named product; clockwork made only by `tag_lantan_clockwork`. Add a water clock good or let `craft` make clockwork after W4 | Proposed |
| N10 | Neverwinter | Review unsourced `tag_volcanic_ash` 2 (plausible near Mount Hotenow) and `tag_wolfsbane` 2 with W4 | Proposed |
| N11 | Neverwinter | Specialty `clothing_fine` 1 has no source; review | Proposed |
| N12 | Neverwinter | Inferred guilds have real power, but sources say no guilds restricted trade circa 1491 DR and Neverember barred new guilds; lower guild power and enforcement | Proposed |
| N13 | Neverwinter | Ruins around the Chasm in 1491 DR; consider lower security or wealth during rebuilding | Proposed |
| N14 | Neverwinter | No direct link to Leilon or Port Llast (about 60 miles each on the High Road); no Luskan sea lane; harbour ice-free year-round. With L5 | Proposed (routes phase) |
| N15 | Neverwinter | Gauntlgrym trade alliance forming circa 1491 DR; add Gauntlgrym and a route when Underdark links are reviewed | Proposed (routes phase) |
| N16 | Neverwinter | Ironstar Forge Company and North Coast High Road Freight are engine-authored; leave | No change |
| N17 | Neverwinter | Laerakond traders (before 1479 DR) and the Thayan enclave (video game) predate 1492 DR; do not model | No change |
| N18 | Neverwinter | Moonstone Mask and named taverns not dated for 1491 DR; add once lodging exists and a late source is found | Proposed |
| N19 | Neverwinter | `reload_catalog` moved Amphail again (A12, eleventh time; x 621.7, y 1126); Neverwinter unaffected (stored position equals its control point). Amphail restored by hand to x 648.5289, y 1161.7169 | Open (see A12, L12) |
| SE1 | Secomber | Add `quarry` 1 (stone-cutting a main occupation; The North, p. 63; Forgotten Realms Campaign Setting, 3rd edition, p. 228); about 0.18 marble blocks a day | Applied 2026-10-14 |
| SE2 | Secomber | Set description from the sources | Applied 2026-10-14 |
| SE3 | Secomber | Set region `Delimbiyr Vale` (wiki Delimbiyr Route and Secomber place pages; matches Daggerford, Loudwater, Llorkh); zone unchanged | Applied 2026-10-14 |
| SE4 | Secomber | Retain 1,300 as undated modeled estimate for the 1492 DR planning scenario, not a census; population basis records 900 (1358/1367 DR, including 200 village/700 hamlets) and 1,417 (1372 DR) as historical evidence. No late-15th-century count. | Applied 2026-10-15 (provenance; residents unchanged) |
| SE5 | Secomber | Set ruler to Lord Traskar Selarn (circa 1367 DR) or leave blank; no late 15th century ruler found | Proposed |
| SE6 | Secomber | Removed unsourced `mine_gem` 2, `gem_agate` 2, `gem_moonstone` 1 and `mining` trait; retained sourced `quarry` 1. No local gem production is modeled. | Applied 2026-10-15 |
| SE7 | Secomber | Renamed three existing west/east Delimbiyr Route map legs (Trade Way junction to Secomber to Loudwater to Llorkh), changed track to trail without changing traced geometry, and repaired the Trade Way junction; Daggerford already connects via its saved Trade Way leg. Uluvin/Zelbross lack saved settlement anchors, and no grounded river trace establishes a D12 lane; no new stops, distances or river leg fabricated | Partially applied 2026-10-15 (missing stops and river lane blocked) |
| SE8 | Secomber | Hobgoblin raids/tribute in 1479 DR and poverty circa 1491 DR retained as dated qualitative runtime lore. No unsupported tribute amount or 1492 price, wealth, security or production effect imposed; quantitative model remains future work. | Applied 2026-10-15 (qualitative only) |
| SE9 | Secomber | Moon Mountain Brewery (two days north; ale by the keg in Secomber, Moon Rum only there; circa 1372 DR, Dragon #299): add as a production site, settlement or supplier once shown operating near 1492 DR | Proposed |
| SE10 | Secomber | Samril's Fine Blades and Gleskur's Finemetals (undated, Forging the Realms 2013): added as businesses `samrils_fine_blades` and `gleskurs_finemetals` (1492 DR operation unverified; copper wire has no commodity, so Gleskur's is service-only); a `weapon` specialty is still proposed | Applied 2026-10-15 (businesses) |
| SE11 | Secomber | Add `vint` 1 for the halfling vineyards north-west of town (sour vinegar; undated 2020 and 2022 sources) | Proposed (low confidence) |
| SE12 | Secomber | Singing Sprite inn and Seven-Stringed Harp tavern (1367 and 1396 DR): added as businesses `singing_sprite` and `seven_stringed_harp` with the Windfeather innkeepers, assumed staff and the 1492 DR caveat (Volo's Guide to the Sword Coast, pp. 80 to 85; The North, p. 64) | Applied 2026-10-15 (user request; 1492 DR unverified) |
| SE13 | Engine-wide | Secomber's generic 2.6/day ship-hull orders included 2.6 war galleys and 2.6 trade galleons actually imported (52,416 gp/day at producer-gate prices). Ship hulls now require explicit orders; fishing-boat replacement remains. Fresh default calculation: about 7,376 gp/day imports vs 269 exports, not a calibrated trade balance. Other flat fallback needs (including flying carpets), inferred tea/fruit acreage, cotton capacity (not a current shipped export) and rocky-hill iron ore without `mine_iron` remain to review with W5, W6, Y12, N5, N6, D18, A10 | Partial engine fix 2026-10-15; residual open |
| SE14 | Secomber | Position (x 848, y 1194.4) about 161 miles from Daggerford; check against the 2nd-edition "Map of Interior" and the 5th-edition Delimbiyr Vale map | Proposed (map) |
| SE15 | Secomber | `reload_catalog` moved Amphail again (A12, twelfth time; x 621.7, y 1126); Secomber unaffected (stored position equals its control point). Amphail restored by hand to x 648.5289, y 1161.7169 | Open (see A12, L12) |
| SE16 | Secomber | The North (1996, p. 5) puts the inland area from the Spine of the World to Waterdeep in a subarctic climate (rivers frozen Uktar to early Ches); the model class is `temperate`. Sourced description added to the location page (`SETTLEMENT_CLIMATES`); class unchanged | Description applied 2026-10-15; class review proposed |
| SE17 | Secomber | The North gives 900 as about 200 in the village and 700 in surrounding hamlets (see SE4) | Proposed |
| SE18 | Secomber | Traskar Selarn, Amelior Amanitas and the Klaeverdars have no office or business in the model; add only with a late 15th century source and a model slot | Proposed |
| OR1 | Orlumbor | Add `herd` 1 (goats a named export, goat-herders a main occupation; Forgotten Realms Campaign Setting, 2nd edition, p. 68). `herd` makes sheep, wool, cheese and meat, not goats | Applied 2026-10-15 |
| OR2 | Orlumbor | Set description from the sources | Applied 2026-10-15 |
| OR3 | Engine-wide | `ship` 2+ can now make `merchant_cog` with a material bill; local seagoing hull orders are explicit port fleet replacements (Orlumbor ~0.00016 cog/day). Existing `trade_galleon`/`war_galley` remain separate tag-only records and are not silently converted to cogs; investigate their canon/production independently | Cog applied 2026-10-15; other hulls open |
| OR4 | Orlumbor | Specialty `ship_boat` 3 still labels a river boat; `merchant_cog` is now distinct but no Orlumbor specialty reassignment has been made (settlement catalogue owned by location research) | Proposed |
| OR5 | Orlumbor | Add shortage `timber` (named import; island logged bare by 1367 DR), as D13 | Proposed |
| OR6 | Orlumbor | Population 3,000 has no source and none was found; add a `populations.py` entry recording it as unknown | Proposed |
| OR7 | Orlumbor | Ruler: only Tulgar Wrighttson (1358 DR, video game only); leave blank or set with the date | Proposed |
| OR8 | Engine-wide | Island with `grain`, `vegetables`, `fruit` shortages shows a corn surplus (30.7 bushels a day) and exports fruit, nuts, eggs, tea, spices, medicinal herbs with no `farm`, `orchard` or `herb`; trace hinterland output on island landmasses with N5, Y6, D18 | Proposed |
| OR9 | Engine-wide | Orlumbor imports about 300 times exports (138,316 against 461 gp a day) through the flat 6-a-day need for unavailable goods; review with W5, W6, Y12, N6, SE13 | Proposed |
| OR10 | Engine-wide | After OR1, sheep exports 81.7 a day against 42 a tenday in stock; review with G13, R14, T15 | Proposed |
| OR11 | Orlumbor | Only link is the 263.2-mile Baldur's Gate lane; add lanes to Waterdeep (patron), the Daggerford or Trollbark coast and Mintarn | Proposed (routes phase) |
| OR12 | Orlumbor | Position about 268.6 miles from Waterdeep against "300 miles south" (Reader's Guide, pp. 140 to 141) and about 172 miles south of Daggerford; check against the 2nd-edition campaign setting maps and the 5th-edition Sword Coast map | Proposed (map) |
| OR13 | Orlumbor | Add `temple` 1 or a pilgrimage flow for Stormhaven House (Umberlee) and the temple of Gond once dated near 1492 DR | Proposed |
| OR14 | Engine-wide | Ship repair (most northern ocean vessels repaired at Orlumbor) is not modelled; consider a service | Proposed |
| OR15 | Orlumbor | Inferred Fishers' and Watermen's and Artisans' guilds have no source; docks and warehouses are owned by local families | Proposed |
| OR16 | Orlumbor | The 1358 DR shops and the Swinging Hammock are video game only; do not add | No change |
| OR17 | Orlumbor | `reload_catalog` moved Amphail again (A12, thirteenth time; x 621.7, y 1126); Orlumbor unaffected (stored position equals its control point). Amphail restored by hand to x 648.5289, y 1161.7169 | Open (see A12, L12) |
| LS1 | Longsaddle | Add `herd` 1 (mutton a named export with beef; ranchers on the grassland; *The Savage Frontier*, p. 30; *The North*, p. 11) | Applied 2026-10-16 |
| LS2 | Longsaddle | Set description from the sources | Applied 2026-10-16 |
| LS3 | Longsaddle | Set ruler "Dowell Harpell (spokesman, 1489 DR)" (*Sword Coast Adventurer's Guide*, p. 7) | Proposed |
| LS4 | Longsaddle | Population 700 has no year or evidence; sources give 130 in the hamlet and 1,100 in the area (1358 DR), 130 (1366 DR), about 1,000 with the countryside (1368 DR). Add a `populations.py` entry and choose the scope | Proposed |
| LS5 | Engine-wide | `tag_harness` 2 at Longsaddle makes about 5,594 harness sets a day (gross local product about 33,100 gp per resident a year); `tag_saddle_bags` 2 likewise. Sources name a stirrup and spur smithy, not harness makers. Review with W4; then consider `tan` 1 instead | Proposed |
| LS6 | Engine-wide | Inferred cropland exports (fruit, vegetables, corn, nuts, medicinal herbs) from a ranching hamlet; review with OR8, N5, Y6 | Proposed |
| LS7 | Engine-wide | Flat 1.4-a-day need for unavailable goods (sleigh, clockwork, remorhaz chitin plate); review with W5, W6, OR9 | Proposed |
| LS8 | Longsaddle | Keep region `Sword Coast North` (wiki: Savage Frontier) | No change |
| LS9 | Longsaddle | Add the Gilded Horseshoe, Fuzzy Quarterstaff, Leaping Hooves Trade Stables and Nalathar's Fine Stirrups & Spurs (circa 1367 DR, Volo's Guide to the North, pp. 57 to 62) once shown operating near 1492 DR; check *Storm King's Thunder*, p. 97 | Proposed |
| LS10 | Longsaddle | `horse` 2 and `horse_riding` 1 match the horse trader | No change |
| LS11 | Longsaddle | `arcane` 2 matches the Harpells; inferred Alchemists' and Apothecaries' guild unsourced | No change (guild with OR15) |
| LS12 | Longsaddle | Two Malarite churches (1376 DR, *The Pirate King*); add `temple` 1 only with a later source | Proposed (low confidence) |
| LS13 | Longsaddle | Perfectone Mercantile teleport freight (1360s to 1370 DR) is historical; note for the carriers phase | No change |
| LS14 | Longsaddle | Road links to Triboar (137.8 miles) and Mirabar (160.7 miles) only; check against the 2nd-edition "Map of Interior" (*The North*) and 5th-edition maps | Proposed (routes phase and map) |
| LS15 | Longsaddle | `reload_catalog` after this run did not move Amphail (x 648.5289, y 1161.7169) or Longsaddle; first clean reload recorded since A12 | Observation 2026-10-16 (see A12, L12) |

## Proposed New Commodities

| Commodity | First evidence | Status |
| --- | --- | --- |
| Furniture / furnishings | Waterdeep exports | Proposed |
| Musical instruments | Waterdeep, Halambar Lutes & Harps; `musical_instrument` models an unenchanted stringed instrument (30 gp, craft 2, planks/rope bill); annual cultural replacement is one instrument per 1,000 residents; magical boxes and repairs are not represented | Created 2026-10-15 |
| Locks and fastenings | Waterdeep, The Golden Key; Triboar, Aldenar Uldinath's eyebolts, latches, nails and pins for wagons (14th century DR) | Proposed (Triboar's wagon part created 2026-10-08 as `wagon_fittings`) |
| Animal feed (hay and oats) | Triboar, The Cart and Coin and Ransor's Open Road | Created 2026-10-08 as `animal_feed` |
| Caravan gear and supplies | Triboar infobox export; The Cart and Coin | Created 2026-10-08 as `caravan_supplies` |
| Boots and shoes | Waterdeep, Sulmest's; Thentavva's | Proposed |
| Jewelry | Waterdeep, Olmhazan's Jewels; Daggerford, Korbus Brightjewel and Farrel's (14th century DR); Neverwinter's fine jewellery famed across Faerun (14th century DR, Cyclopedia of the Realms, pp. 66 to 67). `jewelry` models one nonmagical silver/agate piece (65 gp; craft 2), with about one to three pieces purchased annually per 1,000 residents by wealth; other styles/prices remain unmodeled | Created 2026-10-15 |
| Maps and sea charts | Waterdeep, Serpentil Books & Folios; Yartar, Esklindrar's Maps, Books, & Folios (treasure maps, circa 1370 DR) | Proposed |
| Zzar and sluth | Waterdeep, House of Good Spirits | Proposed |
| Malt | [Ale formulation](commodities/drink/ale.md#formulation-proposed) (C6); intermediate between malting and brewing | Proposed |
| Brewing herbs or hops | Ale formulation (C6); Goldenfields grows hops (Storm King's Thunder, p. 48), so hops are grown in the North; whether gruit is also used is still open | Needs reading |
| Keg (empty) | Ale formulation (C6); see [Keg](equipment/brewing/keg.md) | Proposed |
| Grapes | [Table wine formulation](commodities/drink/wine-common.md#formulation-proposed) (C8); `grapes` sold in 30 lb crates at a provisional 0.55 gp; produced by `vint`, used by table wine at 6 crates/cask | Created 2026-10-15 |
| Glass bottle | Bottled drinks (C9); see [Glass bottle](equipment/distilling/glass-bottle.md) | Proposed |
| Cider fruit (windfalls) | Cider formulations (C11) | Open question |
| Crate | Waterdeep, Helmstar Warehouse | Proposed |
| Monster remains | Waterdeep, The Old Monster Shop | Proposed |
| Waterdhavian cheese | Waterdeep wiki note | Needs reading |
| Mushroom wine | Amphail, Stag-Horned Flagon (Volo's Guide to the North, p. 18; Flagon operating circa 1490 DR) | Proposed |
| Cut flowers | Amphail, Ammakyl Flowers and Foods (name only); Neverwinter hothouse gardens kept flowers through winter (14th century DR, The Savage Frontier, pp. 31 to 32) | Needs reading |
| Barley | Goldenfields grows barley (Storm King's Thunder, p. 48); `barley` uses the existing wheat-sized 60 lb bushel at 0.6 gp, `farm` producers, and a harvest calendar; 4% of staple mass is reallocated from wheat to barley without increasing the ration | Created 2026-10-15 |
| Seeds | Goldenfields, Earth Mother's Bounty (circa 1485 DR) | Proposed |
| Cordials | Goldenfields monks (wiki Cordial article; citation broken) | Needs reading |
| Turkeys | Goldenfields pens (Storm King's Thunder, p. 46); Red Larch, Mhandyvver's Poultry sells turkeys and ducks (1366 and 1491 DR); `chicken` nearest | Proposed |
| Crumblecake | Red Larch's named food, 1 to 3 cp a loaf around 1360 DR, served at two inns in 1489 DR (Volo's Guide to the North, p. 79; Dragon+ Travel Talk) | Proposed |
| Smoked meat | Red Larch, Old Angrath's Smokehouse (circa 1372 DR, Dragon #300); `meat_salt` nearest | Needs reading |
| Pickled eggs; fowl preserved in oil | Red Larch, Mhandyvver's Poultry (1491 DR, Princes of the Apocalypse, p. 27) | Proposed |
| Hornapples | Red Larch, Gulther orchard (circa 1372 DR); not yet read | Needs reading |
| Daggerford clarry (blended wine) | Daggerford, popular local wine from grapes grown around Daggerford, Liam's Hold and Gillian's Hill (1372 DR, video game source only); see Grapes | Needs reading |
| Churlgo Cheese | Daggerford, Eastern Farmlands halfling cheese (circa 1372 DR, video game source only); `cheese` nearest | Needs reading |
| Almond beer | Daggerford, Happy Cow under Fulbar Hardcheese (late 14th century DR) | Needs reading |
| Wheels | Daggerford, Cromach's Smithy makes wooden wheels (late 15th century DR, Scourge of the Sword Coast, p. 19) | Proposed |
| Caravan gear and supplies | Triboar, infobox export; the Cart and Coin and Ransor's Open Road (14th century DR and after 1485 DR) | Proposed |
| Animal feed (hay, oats) | Triboar, the Cart and Coin and Ransor's Open Road sold animal feed | Proposed |
| Cider | Phandalin, Edermath Orchard makes cider in winter and the Stonehill Inn serves it (1491 DR, *Lost Mine of Phandelver*, pp. 15 to 16). **Deferred:** existing `apples` is a Highmoon-only tag product at 1 gp/30 lb crate, and generic `fruit` is also 1 gp/crate; 5 to 7.2 crates per cask already cost 5 to 7.2 gp before processing, against a 2 gp catalogue cask (about 4.43 gp scaled). No sourced cull/windfall price, volume or Phandalin apple producer; do not invent a profitable cider recipe or apple industry. Moon Mountain Brewery's moonslake cider (Dragon #299) remains unmodeled | Deferred 2026-10-15 (C11) |
| Cold iron | Phandalin, cold-iron mines of the first resettlement (before 1374 DR, *Neverwinter Nights 2: Storm of Zehir*, video game only) | Needs reading |
| Giant goats | Phandalin, herds sold through Barthen's Provisions for Dagult Neverember (early 1490s DR, *Dragon of Icespire Peak*, p. 34); Leilon, Pinchwit Wigglehoof's herd for the town, milk, meat and goat hair, part sold to a Waterdeep trader through Barthen's (circa 1491 DR, *Storm Lord's Wrath*) | Needs reading |
| Nickel | Leilon's eastern mines (copper, nickel and silver sold to Waterdeep, 14th century DR; *Waterdeep and the North*, pp. 6 to 7) | Proposed |
| Goat hair | Leilon, giant goat hair prized for warmth and tensile strength (circa 1491 DR, *Storm Lord's Wrath*) | Needs reading |
| River barge | Yartar's listed export and barge-building (Sword Coast Adventurer's Guide, p. 58); `ship_boat` stands in | Proposed |
| Crabs and eels | Secomber, green Delimbiyr river crabs in the Singing Sprite's Three Crabs (Volo's Guide to the Sword Coast, p. 83); Yartar's Fishyard (catfish, coldwater crabs, eels, shalass; Volo's Guide to the North, p. 93) and crab and eel catch (Sword Coast Adventurer's Guide, p. 58); `fish_fresh` nearest | Proposed |
| Pickles | Yartar, Dannath's Pickles, Nuts, & Foods (circa 1370 DR, Volo's Guide to the North, p. 100) | Needs reading |
| Water clock | Neverwinter, accurate water clocks a named product (14th century DR, Cyclopedia of the Realms, pp. 66 to 67); `lantan_clockwork` is tag-only (N9) | Proposed |
| Decorative glass lamp | Neverwinter, multicoloured glass lamps (14th century DR, same sources); `lantern` stands in (N1) | Proposed |
| Rum (beet rum) | Secomber, Moon Rum distilled from sugar beets at the Moon Mountain Brewery and sold only there and in Secomber (circa 1372 DR, Dragon #299) | Proposed |
| Vinegar | Secomber sour vinegar from halfling vineyards north-west of town (Heroes' Feast, 2020; undated) | Proposed |
| Copper wire | Secomber, Gleskur's Finemetals' braided copper wire for sword grips (Forging the Realms, 2013; undated) | Proposed |
| Abrasive polish; whetstones | Anastur's Abrasives (Llorkh) and House of Yarthin whetstones used by Samril's Fine Blades, Secomber (Forging the Realms, 2013; undated) | Proposed |
| Chapbooks | Secomber and Waterdeep, The Dancing Dwarf satirical periodical (late 15th century DR, So Saith Ed, 2006); `book` stands in | Needs reading |
| Goats (live) | Orlumbor, goats a named export and goat-herders a main occupation (Forgotten Realms Campaign Setting, 2nd edition, p. 68). `goats` is a 2 gp/head model good produced by `herd`, separate from giant goats; no invented goat hair or dairy byproduct. Explicit `herd` workplaces order 10 replacement heads per industry level per year as a conservative modeling placeholder; no per-capita livestock fallback | Created 2026-10-15; herd size calibration open |
| Seagoing merchant ship (cog, caravel) | Orlumbor builds small merchant vessels in about two months (Forgotten Realms Campaign Setting, 2nd edition, p. 68); Waterdeep cogs 5,000 gp (Waterdeep and the North, pp. 42 to 43). New `merchant_cog` models the 5,000 gp cog only (`ship` 2; 120 plank loads, 40 nail kegs, 60 rope coils, 30 sailcloth bolts, 25 pitch barrels). Estimated 40,000 lb freight weight and bill are model assumptions; coastal demand is explicit fleet replacement, never per capita. Caravels, galleons and warships are separate and unmodeled as craft recipes | Cog created 2026-10-15; other hulls open |
| Ship repair (service) | Orlumbor, most northern ocean vessels repaired there at least once (same source); see OR14 | Proposed |
| Magical boot liners (Farrberjiks) | Farr Windward near Orlumbor (1358 DR, Treasures of the Savage Frontier, video game only) | Needs reading |
| Stirrups and spurs | Longsaddle, Nalathar's Fine Stirrups & Spurs, riding gear sold across Faerun; plain stirrups 1 sp each (circa 1367 DR, Volo's Guide to the North, p. 59); `saddle` nearest | Proposed |
| Bells | Longsaddle, Jaster's Ring of Bells, bell-smith (circa 1367 DR, The North, p. 13) | Proposed |
| Mutton | Longsaddle, named export with beef (The Savage Frontier, p. 30); `meat_fresh` stands in | Proposed |
| Ring of force shield | Said to be first made by the Harpells of Longsaddle (Neverwinter Nights: Shadows of Undrentide, 2003, video game only) | Needs reading |

## Locations Missing from the Engine

| Location | Near | Evidence |
| --- | --- | --- |
| Rassalantar | Waterdeep, Amphail | Belmonder's meat estates (Volo); garrison whose guards patrol Amphail |
| Bargewright Inn | Goldenfields (just north) | Trading post on the Iron Road; a Zhentarim spy at Goldenfields reports to Nalaskur Thaelond there (Storm King's Thunder). Also the east end of the Cairn Road from Red Larch, lined with farms and ranches (Storm King's Thunder, p. 77) |
| Kheldell | Red Larch (west, by trail) | Logging thorp in the Westwood whose timber was hauled to Red Larch for sale (1365 DR, Volo's Guide to the North, pp. 50 to 52); only reached by the Red Larch trail |
| Westbridge, Beliard | Red Larch; Triboar (Westbridge 80 miles south); Stone Bridge (Westbridge at its west end on the Long Road, Beliard a few miles east on the Dessarin Road) | Shown with Red Larch on the 2nd-edition map in Volo's Guide to the North, p. 36; Westbridge 80 miles south of Triboar (Triboar article); to verify. Westbridge: farming village of 450 in 1365 DR with a market, stockyard and warehouses, Harvest Inn in the 15th century DR (Volo's Guide to the North, p. 89; Storm King's Thunder, pp. 113 to 114). Beliard: cattle-ranchers' trading village with stables and warehouses circa 1365 DR, giant raids after about 1485 DR (Volo's Guide to the North, pp. 36 to 37; Storm King's Thunder, p. 76); the engine has a Beliard route node but no settlement record (SB9). Candidates to replace the Stone Bridge surveyed market (SB2) |
| Zelbross, Liam's Hold, Gillian's Hill, Womford, Julkoun, Thornhold, Carnath Roadhouse | Waterdeep hinterland; Liam's Hold and Gillian's Hill are within a day of Daggerford (The North, p. 32), Gillian's Hill and Liam's Hold also grow grapes for Daggerford clarry | To verify one by one |
| Bowshot (Andalor's Mill) | Daggerford | Source of Daggerford's imported lumber (Volo's Guide to the Sword Coast, p. 31) |
| Conyberry, Thundertree | Phandalin, Neverwinter Wood | Villages on the Triboar Trail and in Neverwinter Wood shown on the 5th-edition *Lost Mine of Phandelver* maps; Butterskull Ranch lies east of Conyberry on the trail (*Dragon of Icespire Peak*, pp. 11, 16 to 17) | To verify |
| Wave Echo Cave; Tibor Wester's logging camp; Umbrage Hill | Phandalin | Ancient mine (reopening abandoned in the 1490s DR); logging camp in Neverwinter Wood shipping logs to Neverwinter; windmill of the midwife and apothecary Adabra Gwynn (*Dragon of Icespire Peak*) | Map-only or production sites; to verify |
| Ieirithymbul; Southkrypt | Leilon (western Sword Mountains; east of town) | Gnome village whose traders visit Leilon monthly except in winter (*Dragon* #252); former dwarven silver mine and hall (*Dwarves Deep*, p. 58). Map-only or minor sites; to verify |
| Floshin Estates, Cromm's Hold, Tellum's Hold | Daggerford | Elven estate about two days away; Cromm's Hold where Morwen was imprisoned circa 1485 DR; Tellum's Hold heir circa 1489 DR; shown on the Delimbiyr Vale map (Scourge of the Sword Coast, p. 10) |
| Mornbryn's Shield; Nightstone | Yartar | Mornbryn's Shield occupied by Zhentarim mercenaries from Yartar after a giant attack; Nightstone has a Lionshield Coster post sacked by goblins (Storm King's Thunder, late 1480s to early 1490s DR). Positions not checked | To verify |
| Calling Horns, Olostin's Hold, Noanar's Hold | Yartar to Everlund on the Evermoor Way | Stops listed on the wiki's Evermoor Way article (Silver Marches, 2002; Volo's Guide to the North) | To verify |
| Helm's Hold; Vilnask; Floodblest | Neverwinter (south-east; south on the High Road; east on the Neverwinter River) | Named in the wiki's Neverwinter Geography section; Helm's Hold is a monastery tied to the Abolethic Sovereignty in the late 15th century DR. Positions not checked | To verify |
| Gauntlgrym | Neverwinter (east, beneath the Crags) | Restored dwarven city forming a trading alliance with Neverwinter circa 1491 DR (Sword Coast Adventurer's Guide, pp. 52 to 53, via the wiki); see N15 | To verify |
| Moon Mountain Brewery | Secomber (two days north on the Unicorn Run, near the High Forest) | Halfling brewery and distillery (25 staff) supplying ale to Daggerford, Llorkh, Loudwater and Secomber and Moon Rum to Secomber; Zhentarim smuggling link (circa 1372 DR, Dragon #299). Operation near 1492 DR not checked (SE9) |
| Uluvin | Secomber (north-west, Secomber Trail; on the Iron Road) | Sleepy crossroads village; destroyed 1373 DR, refounded before 1491 DR, sacked by hill giants around 1491 DR (Storm King's Thunder, pp. 74, 112, via the wiki) | To verify |
| Zelbross; Mishka's Warren | Secomber (east on the Delimbiyr Route; hobgoblin lair near Secomber) | Zelbross: hamlet of 120 exporting pottery and pipes circa 1365 DR, halfway between Secomber and Loudwater (wiki infobox). Mishka's Warren: Urshani hobgoblin lair receiving Secomber's tribute (1479 DR). Map-only or minor; to verify |
| Farr Windward; Delmarin Island | Orlumbor (west or south-west by tunnel trail; Delmarin west of Orlumbor, north of Mintarn) | Farr Windward: cliff-top exile colony freed and made a free community of Orlumbor in 1358 DR (Treasures of the Savage Frontier, video game only). Delmarin Island: desolate reef-ringed island of fog giants (A Reader's Guide to R. A. Salvatore's the Legend of Drizzt). Map-only or minor; to verify |
| Mog's Keep; Tower of Twilight | Longsaddle (Mog's Keep nearby; Tower of Twilight east of Neverwinter Wood) | Mog's Keep: base of the Blue Sigil, about 450 ogre mercenaries under Mog the Fist around 1358 DR (Gold & Glory, p. 18). Tower of Twilight: home of Malchor Harpell (The Savage Frontier, p. 58). Map-only or minor; to verify |

## Lore Follow-ups

See each page's "Lore Follow-ups" section. Cross-cutting items:

- From 2026-10-04 every location page records Notable Inhabitants and a Maps list (2nd-edition maps preferred). Earlier pages (Waterdeep, Griffon's Nest, Neverwinter, Hlondeth, Arrabar) need these added when reviewed (Triboar done 2026-10-08, Phandalin 2026-10-09).

- Named guilds of Waterdeep versus the engine's inferred guilds.
- Which 1992 Volo businesses survive into 1492 DR (*Dragon Heist*).
- Goldenfields' grain recovery after the plague of about 1395 DR (the Putrescent Anathema; uncited on the wiki) and after Guh's giant attack in the late 15th century DR.
- Region labels: wiki infoboxes give the broad "Sword Coast North". Use the wiki's Dessarin Valley article (5th edition) and Volo's chapters for the finer grouping, as settled for Amphail (A6).
- Generated business addresses (street, "Trade Quarter" district, zip) are placeholders and cannot be edited through `update_business`; replace with sourced addresses only where a source gives one.
- Bread at Amphail: recheck after the generated famine ends (A7). Households are served flour before bakers, so any flour shortfall stops baking entirely.
- Generated chronicle gives Amphail four food crises in 1489 to 1494 DR; check whether that rate is intended.
- Salt: one producer engine-wide (Innarlith). Mintarn's northern islands (rock salt) added 2026-10-04; still to add: Moonshae Isles (Dwyvach Salt Flats, Korinn Archipelago) and Anauroch's Sword salt pans (A13). Recheck whether Waterdeep and Amphail switch from Innarlith once the price snapshot is refreshed.
- Drinks (2026-10-04): where Reghed honey comes from in Icewind Dale, and what the Reghed burn to brew it; what a Red Wizard preservation charm costs (fire-wine); what Halruaan weather-magic over a vineyard costs (starflower wine); whether duergar brew grey ale from grain or fungus, and what they burn (Gracklstugh is grain-short); how Calimport keeps lager cold (Golden Sands lager).
- Amphail is a Long Road stop in `routes.json` but showed only a track neighbour to a road junction (routes phase).
- Free food: Goldenfields gives its food to Waterdeep and neighbours without payment (G10); decide whether gifts or tithes should be modeled before reviewing Waterdeep food prices.
- Tag industries producing named local goods (apples, citrus, pears) cannot be added safely until the flat tag output (W4, C10) is fixed (G8, G13).
- Harness (2026-10-06): only a tag industry makes harness, so towns known for harness-makers (Red Larch, Amphail, Triboar) sell imports (R15).
- Red Larch after 1491 DR: who governs once the Believers fell, and the Acquisitions Incorporated "Far Realm" event at the Dran & Courtier (year missing on the wiki), both bear on the 1492 DR state.
- `reload_catalog` moved Amphail again on 2026-10-06 (A12, third time); each run so far has restored it by hand.
- Daggerford (2026-10-07): the Sword Hills silver rush of the mid 15th century DR may justify a `mine_silver` site near Daggerford; the wiki's interactive map titled "14th Century DR" is drawn on the 5th-edition Schley map; the engine's Daggerford analysis still lists 1,200 as an unverified lead (D10).
- River ports: Daggerford has docks and river-to-caravan transfer but the `port` field only names sea basins; decide how river ports (Daggerford, Secomber, Loudwater) are modelled in the routes phase (D12).
- `reload_catalog` moved Amphail again on 2026-10-07 (A12, fourth time); restored by hand.
- `reload_catalog` moved Amphail again on 2026-10-08 (A12, fifth time; same x 621.7, y 1126); restored by hand to x 648.5289, y 1161.7169.
- Triboar (2026-10-08): caravan services, guides and wagon rental are central to the town but no service or carrier is modeled (T12); the interactive map's orientation is unconfirmed; the wiki gives 200 miles from Red Larch, which conflicts with other distances (T13).
- `reload_catalog` moved Amphail twice on 2026-10-09 (A12, sixth and seventh times; same x 621.7, y 1126); restored by hand each time. The stored file keeps x 648.5289, y 1161.7169, so the reload path itself is placing it.
- Phandalin (2026-10-09): no population figure in any source read (P10); the council's start year decides the 1492 DR ruler (P9); which gold and platinum mines were working in 1492 DR, and whether silver is ever named (P6, P7); the engine's Phandalin position and its only route need checking against the 5th-edition regional maps (P13, T16).
- Climate gating (2026-10-09): `orchard` makes olives and olive oil anywhere (P18); adding `orchard` to any northern town will create an olive chain and long-distance olive imports until gated.
- Stone Bridge (2026-10-10): the wiki's 2-mile, 400-foot single arch needs checking in *Dwarves Deep*, pp. 53 to 54; whether the temple to Moradin is tended or pilgrims still come in the 1490s DR is unknown; surveyed markets placed on landmarks rather than settlements should be checked as the queue reaches them (Warlock's Crypt, Dragonspear Castle, Grandfather Tree).
- `reload_catalog` moved Amphail again on 2026-10-10 (A12, eighth time; same x 621.7, y 1126, no neighbours); restored by hand to x 648.5289, y 1161.7169.
- Leilon (2026-10-11): whether the copper and silver mines were worked again after the 1485 DR resettlement, and what the Battle of Leilon (early 1490s DR) left standing in 1492 DR, decide L1, L4 and L6; the town has no route at all (L5).
- Positions (2026-10-11): `reload_catalog` moved Amphail again (A12, ninth time) and moved Leilon to its `coords.json` control point. Cause traced to `faerun/data/coords.json` (L12). Amphail restored by hand to x 648.5289, y 1161.7169 as before; Leilon kept at its stored and control-point position x 488.4, y 1050.8. Until L12 is decided, any `update_settlement` call also writes the live position to disk, so pass the stored x and y with it.
- Yartar (2026-10-12): who is Waterbaron in 1492 DR (Nestra Ruthiol in 1491 DR; Khaspere Drylund's bid) and any population after 1366 DR decide Y4 and Y5; barge-building and river barge traffic need a river model and a barge good (Y1, Y9, Y13); several towns now show a food exporter where sources describe a food importer (Yartar Y6), so check farm output against the Goldenfields supply story when Waterdeep's food is reviewed.
- `reload_catalog` moved Amphail again on 2026-10-12 (A12, tenth time; same x 621.7, y 1126, no neighbours); restored by hand to x 648.5289, y 1161.7169. Yartar's stored position equals its `coords.json` control point, so it did not move.
- Leilon check (2026-10-12): the stored and live Leilon record no longer has the changes marked Applied 2026-10-11 (L1 `mine_copper` 1 and `mine_silver` 1, L2 `fish` 1, L3 description); it shows `mine_iron` 2, `smith` 1, `farm` 1, specialty `iron_ore` 1 and a blank description. Other earlier fixes (Goldenfields, Red Larch, Daggerford, Triboar, Phandalin, Mintarn) are present. Not re-applied in the Yartar run (one location per run); decide whether to re-apply or mark L1 to L3 reverted.
- Neverwinter (2026-10-13): the wiki article is now readable by direct fetch (blocked on 2026-10-01). No population figure exists for the rebuilt city (N4); whether the glass lamp, water clock and jewellery crafts survived 1451 DR, whether the Gauntlgrym alliance was in force in 1492 DR, and how "no guilds" (Sword Coast Adventurer's Guide) fits Neverember's guild limits (Storm King's Thunder) are open. No 2nd-edition city plan was found; check Volo's Guide to the North, pp. 130 to 134. Several large non-farming cities now show farm exports (Neverwinter N5, Yartar Y6).
- Secomber (2026-10-15): climate (The North, p. 5), the Windfeather innkeepers and the two inns' prices were read directly from hosted scans of The North and Volo's Guide to the Sword Coast; the scans' images (town maps) were not inspected, and the inns' 1492 DR operation is unverified (SE12).
- Secomber (2026-10-14): no population or ruler after 1372 DR; the 1479 DR tribute and circa 1491 DR poverty (Forgotten Realms Campaign Guide, p. 37; Storm King's Thunder, p. 107) decide SE4, SE5 and SE8, and the wiki's "twenty years later" does not fit a book set about 1491 DR. No source names gems at Secomber (SE6). The 2013 "Thaelon Morgyr's Map" businesses (Secomber, Beliard, Llorkh, Scornubel, Waterdeep) need an in-world date before any is added. No 2nd-edition town plan was found; check Volo's Guide to the Sword Coast, pp. 79 to 84.
- `reload_catalog` moved Amphail again on 2026-10-14 (A12, twelfth time; same x 621.7, y 1126, no neighbours); restored by hand to x 648.5289, y 1161.7169. Secomber's stored position equals its `coords.json` control point, so it did not move.
- Orlumbor (2026-10-15): no population and no ruler after 1358 DR in any source read; check Storm King's Thunder, p. 80, and the Sword Coast Adventurer's Guide, pp. 8, 70, for the 1490s DR island (OR6, OR7). Seagoing ships are tag-only goods, so the North's main shipyard imports galleons from Westgate and galleys from Memnon (OR3); check other shipbuilding ports (Waterdeep, Baldur's Gate, Luskan) for the same pattern. The wiki's Orlumbor article links Stormhaven House to a Sembian Talos temple of the same name. No 2nd-edition map of the island was found.
- `reload_catalog` moved Amphail again on 2026-10-15 (A12, thirteenth time; same x 621.7, y 1126, no neighbours); restored by hand to x 648.5289, y 1161.7169. Orlumbor's stored position equals its `coords.json` control point, so it did not move.
- Longsaddle (2026-10-16): no population after 1368 DR and no business shown operating near 1492 DR; check Storm King's Thunder, pp. 74, 97, and Volo's Guide to the North, p. 52, for the scope of the 130 and 1,100 figures (LS3, LS4, LS9). Longsaddle's harness output (LS5) is the largest tag-industry distortion seen so far in a village; it belongs with W4. The Honor Among Thieves film and tie-ins are undated on the wiki, so the shops and people they place in Longsaddle may postdate 1492 DR. The 1996 The North village map and the 1999 Interactive Atlas plan were not inspected.
- `reload_catalog` on 2026-10-16 did not move Amphail (stored and live x 648.5289, y 1161.7169) or Longsaddle (x 574.5, y 931.3): the first clean reload recorded since A12.
