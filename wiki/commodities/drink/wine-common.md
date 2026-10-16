# Table wine

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `wine_common`  
**Category:** drink  
**Trade unit:** cask (100 lb)  
**Base price:** 4 gp per cask (about 0.04 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Table wine is a drink good in Faerûn, traded in cask lots for daily use, craft, and commerce. A prepared beverage prized for hospitality, ceremony, and everyday refreshment.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `vint` |
| Demand index | 1.4 |
| Luxury (wealth elasticity) | 0.3 |
| Perishable | 0.2 |
| Demand traits | `cosmopolitan` 1.4 |
| Legacy season multipliers | `autumn` 0.8 |
| Storage | 365 days capacity, 0.05% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one cask: 6 crates (180 lb) of wine grapes (`grapes`), harvested from `vint` vineyards in late summer/autumn. Grapes are provisionally 0.55 gp per crate (3.30 gp input per cask); fermentation and warehousing continue all year. The historical formulation and observed quotes below predate this change.

Used as an input for: [Brandy and firewine](../drink/brandy.md) (0.08 per unit), [Fine vintage wine](../luxury/wine-fine.md) (0.03 per unit).

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine cask is 100 lb, read as **12 gallons** at 8.34 lb a gallon, the same size as the catalogue cask; the cask is returned.

| Line | Input | Quantity per cask | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Grapes | 6 crates (180 lb) | [`fruit`](../food/fruit.md) (no grape commodity) | 6.00 gp | About 15 lb of grapes a gallon of wine after pressing |
| 2 | Yeast | wild, on the fruit | none | 0.00 gp | Not bought |

| Line | Conversion cost | Basis | Cost per cask |
| --- | --- | --- | --- |
| 3 | Labour | Two cellarmen at 0.65 gp and two labourers at 0.325 gp press about 10 casks a day | 0.20 gp |
| 4 | Equipment and cask wear | Mill, press and cask float | 0.05 gp |

**Rolled-up cost: about 6.25 gp per cask** (materials 6.00 gp, conversion 0.25 gp). The engine base price is 4 gp, so at a realistic grape weight **table wine costs more to make than it sells for**.

The engine recipe uses 3.5 crates (105 lb), enough for about 7 gallons, not 12. Even that short recipe costs 3.50 gp in fruit, 88% of the price, and 3.75 gp rolled up. The deeper issue: vineyards (`vint`) do not grow fruit in the engine. Fruit comes from `orchard` and `farm`, so wine towns import their grapes. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

One vintage a year. The engine has a harvest calendar for fruit but none for wine, so wine is made evenly all year from fruit that is only picked in late summer and autumn.

**Route: Table wine**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Harvest and sort | vintage season (Eleint to Marpenoth) | Farm labour |  |
| 20 | Crush | hours | Cellarman | [Fruit mill](../../equipment/vinting/fruit-mill.md) or treading in a vat |
| 30 | Ferment on the skins | 5 to 10 days | Cellarman | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 40 | Press | 1 day | Cellarman | [Fruit press](../../equipment/vinting/fruit-press.md) |
| 50 | Finish fermenting and settle | 3 to 6 weeks | none | [Aging tun](../../equipment/vinting/aging-tun.md) |
| 60 | Rack into casks | hours | Labourer | [Wine cask](../../equipment/vinting/wine-cask.md) |

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Fruit mill](../../equipment/vinting/fruit-mill.md) | 6 gp | 20 |
| [Fermenting vat](../../equipment/brewing/fermenting-vat.md) | 8 gp | 30 |
| [Fruit press](../../equipment/vinting/fruit-press.md) | 19 gp | 40 |
| [Aging tun](../../equipment/vinting/aging-tun.md) | 8 gp | 50 |
| [Wine cask](../../equipment/vinting/wine-cask.md) | 1.2 gp | 60 |
| [Brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) | 2 gp | 20, 60 |

## Cost Roll-up Cross-check

Observed output, 3 Marpenoth 1492 DR, live server, standard quality; inputs at the asking price in the same market, the drink at its producer gate price before merchant markup.

| Market | Fruit asking price | Fruit per cask (3.5 crates) | Wine producer gate | Fruit share | Wine retail |
| --- | --- | --- | --- | --- | --- |
| Berdusk | 1.074 gp | 3.76 gp | 4.875 gp | 77% | 4.638 gp |
| Darromar | 1.110 gp | 3.89 gp | 5.228 gp | 74% | 5.262 gp |
| Saerloon | 1.304 gp | 4.56 gp | 5.919 gp | 77% | 6.801 gp |
| Crimmor | 2.675 gp | 9.36 gp | 11.841 gp | 79% | 10.686 gp |
| Hlath | 3.155 gp | 11.04 gp | 13.854 gp | 80% | 14.427 gp |
| Arrabar | 4.785 gp | 16.75 gp | 23.760 gp | 70% | 20.548 gp |
| Hlondeth | 5.078 gp | 17.77 gp | 24.736 gp | 72% | 22.289 gp |
| Tashluta | 13.855 gp | 48.49 gp | 65.687 gp | 74% | 60.682 gp |
| Zazesspur | 14.053 gp | 49.19 gp | 67.101 gp | 73% | 65.388 gp |
| Nimbral | 3.378 gp | 11.82 gp | 4.000 gp | 296% | 54.005 gp |
| Base prices | 1 gp | 3.50 gp | 4 gp | 88% | |

- **Wine passes fruit cost through**: gate prices run from 4.9 gp at Berdusk to 67 gp at Zazesspur, tracking fruit at 70% to 80% of the gate. That is the opposite of ale at Ravens Bluff (C2), so the engine treats the two differently.
- **Every major wine town imports most of its fruit**: Hlondeth grows 1%, Hlath 8%, Arrabar 14%, Crimmor and Zazesspur 16%. Hlondeth's cask sells for 22 gp against a 4 gp book price (C8).
- **Nimbral is the exception**: gate 4.0 gp although fruit costs 11.82 gp a cask, so there the input cost is ignored, as at Ravens Bluff.
- **Retail is below the producer gate** in six of ten markets (Berdusk, Crimmor, Arrabar, Hlondeth, Tashluta, Zazesspur). Wine's autumn season factor of 0.8 appears to discount the shelf price but not the gate, so merchants sell under cost every autumn (C12).
- *Aurora's* sells table wine at 12 sp a 12-gallon cask; the engine's 4 gp is 3.3 times that.
<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `vint` 13 (of 325 stored settlements).

**Specialty at:** [Arrabar](../../../locations/arrabar.md) (1), Crimmor (2), Hlath (1), [Hlondeth](../../../locations/hlondeth.md) (1).

**Configured shortage at:** Bryn Shander, Citadel Adbar, Menzoberranzan, [Phandalin](../../../locations/phandalin.md), Port Nyanzaru, Ruathym, Sundabar.

## Aurora's Whole Realms Catalogue

Bulk red or white provisioning wine from local vintners; cheap because it travels short distances, uneven in quality.

**Origin given:** Numerous local suppliers.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wines and Ales | 131 |  | hand keg (2 gal) | 3 sp | 0.018 gp |
| Wines and Ales | 131 |  | cask (12 gal) | 12 sp | 0.012 gp |
| Wines and Ales | 131 |  | barrel (30 gal) | 25 sp | 0.01 gp |
| Wines and Ales | 131 |  | butt (100 gal) | 8 gp | 0.0096 gp |
| Wines and Ales | 131 |  | tun (250 gal) | 20 gp | 0.0096 gp |

Engine price per lb is **3.98 times** the median catalogue price per lb for this entry (engine 0.04 gp/lb; catalogue median 0.01 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
