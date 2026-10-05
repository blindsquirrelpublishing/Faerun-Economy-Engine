# Location Inventory

[Location index](README.md)

Working tracker for the location-by-location review that started 2026-10-03.
Each location gets a page under `locations/` with its engine record, lore,
businesses, discrepancies and proposed changes. Nothing in the proposal lists is
applied until it is approved. Routes, feasibility and carriers come in a later
phase.

## Queue

Ordered by straight-line distance from Waterdeep. "S" marks a surveyed
(auto-generated) market rather than an established settlement.

| # | Location | Miles | Engine pop. | Status |
| --- | --- | --- | --- | --- |
| 1 | [Waterdeep](locations/waterdeep.md) | 0 | 200,000 | Done 2026-10-03 |
| 2 | [Amphail](locations/amphail.md) | 62 | 850 | Done 2026-10-04 |
| 3 | [Goldenfields](locations/goldenfields.md) | 90 | 3,000 | Done 2026-10-05 |
| 4 | Red Larch | 109 | 1,100 | Next |
| 5 | Daggerford | 123 | 900 | Queued |
| 6 | [Triboar](locations/triboar.md) | 156 | 2,500 | Existing page; review |
| 7 | [Phandalin](locations/phandalin.md) | 159 | 500 | Existing page; review |
| 8 | Stone Bridge (S) | 160 | 80 | Queued |
| 9 | Leilon | 192 | 900 | Queued |
| 10 | Yartar | 213 | 3,800 | Queued |
| 11 | [Neverwinter](locations/neverwinter.md) | 247 | 23,000 | Existing page; review |
| 12 | Secomber | 248 | 1,300 | Queued |
| 13 | Orlumbor | 268 | 3,000 | Queued |
| 14 | Longsaddle | 270 | 700 | Queued |
| 15 | Port Llast | 304 | 800 | Queued |

Further out: Warlock's Crypt (S), Dragonspear Castle (S), [Griffon's Nest](locations/griffons-nest.md) (S),
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
| W5 | Engine-wide | Review the flat 400-a-day import need for unavailable goods | Proposed |
| W6 | Engine-wide | Review goods output and import valuation | Proposed |
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
| A9a | Engine-wide | Draft horses get a world-wide hinterland capacity multiplier of about 134 (riding horses none); trace the rule. Amphail's `horse` level is not the cause | Proposed; recheck after famine |
| A9b | Engine-wide | Warhorse capacity near zero (about 1.4 a year at Amphail) despite the specialty; trace why. First priority of Amphail's engine fixes | Proposed; recheck after famine |
| A10 | Engine-wide | Cotton grows anywhere with `farm` or `textile` (Waterdeep 214 a day spare). For the commodity review: drop `textile` as a producer; stop cold-region farms producing it | Deferred |
| A11 | Amphail | Stag-Horned Flagon added as a market business (operating circa 1490 DR, Storm King's Thunder p. 72); Eagleshield Fine Horse Leathers waits for a source near 1492 DR | Flagon applied 2026-10-04; Eagleshield proposed |
| A12 | Engine-wide | After `reload_catalog` the live server moved Amphail to x 621.7, y 1126 with no neighbours (disk unchanged); live position restored 2026-10-04 via `update_settlement`. Recurred 2026-10-05 after the Goldenfields run's `reload_catalog` (same x 621.7, y 1126; Goldenfields unaffected) and was restored again the same way; trace the cause before the next reload; until then pass stored x and y with any `update_settlement` | Open |
| A13 | Engine-wide | Innarlith is the only salt producer in the engine; lore says most regions made salt locally. Applied: `salt` 1 at Mintarn (named rock-salt mines; about 112 sacks a day). Moonshae and Anauroch sources to add when reviewed; recheck Waterdeep's 256 a day need after the snapshot refresh | Applied 2026-10-04 |
| C1 | Engine-wide | Coin standard (50 coins to the lb, 4% minting loss, 48 coins per lb). Applied: `platinum_ingot` 550 to 2,400 gp (480 pp), `silver_ingot` 50 to 48 gp, `copper_ingot` 5 to 4.8 gp, `gold_ingot` 500 to 480 gp. Platinum now trades about 1,326 gp at Citadel Adbar (was 304) and about 5,100 gp in non-producing markets (was about 1,170). Price snapshots stale; refresh before relying on cached prices. See [the coin standard](commodities/README.md#coin-standard) | Applied 2026-10-04 |
| C2 | Engine-wide | Ale producer gate price does not follow imported grain: Ravens Bluff sells at 1.19 gp a keg against 3.07 gp of grain per keg; Baldur's Gate clears 0.07 gp. Trace whether gate prices use local rather than blended input cost. See [Ale cross-check](commodities/drink/ale.md#cost-roll-up-cross-check) | Proposed |
| C3 | Waterdeep | Brews 8,093 kegs a day on grain that is 2% local at about 7 gp a bushel, then supplies 61% of Neverwinter's ale at 8.64 gp landed. Review with W4 and W5 | Proposed |
| C4 | Engine-wide | Ale price anchors disagree: engine 0.167 gp a gallon, *Aurora's* 0.045 to 0.175, Waterdeep Trading Company guide 1.50 FSD. Decide the anchor and whether FSD equals gp; confirm the 80 lb keg excludes the cask | Open question |
| C5 | Engine-wide | Ale recipe uses wheat (`grain`); ale is normally a barley drink. [Barley](commodities/food/barley.md) is a proposed commodity | Proposed |
| C6 | Engine-wide | Proposed ale formulation: keep grain 0.8, add firewood (`timber` 0.06 load); optional `malt` intermediate between two routes. Rolls up to about 1.00 gp against 1.6 gp. See [Ale formulation](commodities/drink/ale.md#formulation-proposed) and [brewing equipment](equipment/brewing/README.md) | Proposed |
| C7 | Engine-wide | Mead recipe uses 0.6 crock of honey a keg, about a fifth of normal strength. At 3 lb a gallon (2.88 crocks) honey alone is 4.32 gp against a 2.5 gp price, and no market breaks even. Decide: call it small mead, or raise honey and price (about 5 to 6 gp; *Aurora's* implies about 4.8 gp a keg). See [Mead](commodities/drink/mead.md#cost-roll-up-cross-check) | Open question |
| C8 | Engine-wide | Table wine recipe (3.5 crates, about 7 gallons of juice) is short for a 12-gallon cask; a realistic 6 crates costs 6 gp against 4 gp. Vineyards (`vint`) grow no fruit, so wine towns import it (Hlondeth 1% local) and casks reach 22 to 67 gp. Consider a `grapes` commodity produced by `vint`, and a vintage calendar for wine | Proposed |
| C9 | Engine-wide | Bottled drinks (brandy, fire-wine, starflower wine) have no bottle in the recipe, though a glass bottle (about 1.6 gp) is their largest material cost. Brandy uses 0.08 cask of wine a bottle, about half of an 8-to-1 still yield. Zazesspur (about 4,000 bottles a day) gates brandy at its wine cost, 5.37 against 5.23 gp | Proposed |
| C10 | Engine-wide | Single-tag drinks (duergar grey ale, kelp ale, Reghed frost mead, fire-wine, starflower wine) have no recipe and each produce a flat 6,972.86 units a day whatever the place (demand 2.4 to 124). Give them recipes; trace the flat output with W4. Kelp ale stores 365 days though its description says it goes flat within a season | Proposed |
| C11 | Engine-wide | Cider at engine fruit prices (1 gp a 30 lb crate) costs 6.65 to 7.65 gp a 12-gallon cask, 1.4 to 7.5 times the scaled catalogue estimates. Decide whether cider fruit (windfalls, culls) needs a cheaper commodity | Open question |
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

## Proposed New Commodities

| Commodity | First evidence | Status |
| --- | --- | --- |
| Furniture / furnishings | Waterdeep exports | Proposed |
| Musical instruments | Waterdeep, Halambar Lutes & Harps | Proposed |
| Locks and fastenings | Waterdeep, The Golden Key | Proposed |
| Boots and shoes | Waterdeep, Sulmest's; Thentavva's | Proposed |
| Jewelry | Waterdeep, Olmhazan's Jewels | Proposed |
| Maps and sea charts | Waterdeep, Serpentil Books & Folios | Proposed |
| Zzar and sluth | Waterdeep, House of Good Spirits | Proposed |
| Malt | [Ale formulation](commodities/drink/ale.md#formulation-proposed) (C6); intermediate between malting and brewing | Proposed |
| Brewing herbs or hops | Ale formulation (C6); Goldenfields grows hops (Storm King's Thunder, p. 48), so hops are grown in the North; whether gruit is also used is still open | Needs reading |
| Keg (empty) | Ale formulation (C6); see [Keg](equipment/brewing/keg.md) | Proposed |
| Grapes | [Table wine formulation](commodities/drink/wine-common.md#formulation-proposed) (C8); produced by `vint` | Proposed |
| Glass bottle | Bottled drinks (C9); see [Glass bottle](equipment/distilling/glass-bottle.md) | Proposed |
| Cider fruit (windfalls) | Cider formulations (C11) | Open question |
| Crate | Waterdeep, Helmstar Warehouse | Proposed |
| Monster remains | Waterdeep, The Old Monster Shop | Proposed |
| Waterdhavian cheese | Waterdeep wiki note | Needs reading |
| Mushroom wine | Amphail, Stag-Horned Flagon (Volo's Guide to the North, p. 18; Flagon operating circa 1490 DR) | Proposed |
| Cut flowers | Amphail, Ammakyl Flowers and Foods (name only) | Needs reading |
| Barley | Goldenfields grows barley (Storm King's Thunder, p. 48); see C5 | Proposed |
| Seeds | Goldenfields, Earth Mother's Bounty (circa 1485 DR) | Proposed |
| Cordials | Goldenfields monks (wiki Cordial article; citation broken) | Needs reading |
| Turkeys | Goldenfields pens (Storm King's Thunder, p. 46); `chicken` nearest | Proposed |

## Locations Missing from the Engine

| Location | Near | Evidence |
| --- | --- | --- |
| Rassalantar | Waterdeep, Amphail | Belmonder's meat estates (Volo); garrison whose guards patrol Amphail |
| Bargewright Inn | Goldenfields (just north) | Trading post on the Iron Road; a Zhentarim spy at Goldenfields reports to Nalaskur Thaelond there (Storm King's Thunder) |
| Kheldell, Zelbross, Westbridge, Liam's Hold, Gillian's Hill, Womford, Julkoun, Thornhold, Carnath Roadhouse | Waterdeep hinterland | To verify one by one |

## Lore Follow-ups

See each page's "Lore Follow-ups" section. Cross-cutting items:

- From 2026-10-04 every location page records Notable Inhabitants and a Maps list (2nd-edition maps preferred). Earlier pages (Waterdeep, Phandalin, Griffon's Nest, Triboar, Neverwinter, Hlondeth, Arrabar) need these added when reviewed.

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
