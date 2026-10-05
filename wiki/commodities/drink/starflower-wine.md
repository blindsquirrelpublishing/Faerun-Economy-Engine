# Starflower wine

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `starflower_wine`  
**Category:** drink  
**Trade unit:** bottle (3 lb)  
**Base price:** 18 gp per bottle (about 6 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A pale, glowing vintage from vineyards that only fruit under Halruaa's controlled weather-magic.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_starflower_wine` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0.05 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine bottle is 3 lb, read as about **0.2 gallon** of drink in 1.3 lb of glass; the bottle is sold with it.

| Line | Input | Quantity per bottle | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Grapes | 3 lb (0.1 crate) | [`fruit`](../food/fruit.md) (no grape commodity) | 0.10 gp | 15 lb a gallon, as for table wine |
| 2 | Glass bottle and cork | 1 bottle | [`glassware`](../product/glassware.md) | 1.64 gp | As for brandy |
| 3 | Halruaan weather-magic | vineyard overhead, not per bottle | none (arcane service) | not priced | The engine description says the vines only fruit under it |

| Line | Conversion cost | Basis | Cost per bottle |
| --- | --- | --- | --- |
| 4 | Labour | Vineyard-scale making and careful bottling, about 0.05 gp a bottle | 0.05 gp |
| 5 | Equipment and aging wear | Press, vats, tuns | 0.02 gp |

**Rolled-up cost: about 1.81 gp per bottle** (materials 1.74 gp, conversion 0.07 gp). Against the 18 gp base price that leaves about 16 gp a bottle for the weather-magic and the margin.

No engine recipe: it comes from `tag_starflower_wine` at Halarahh. Physically it is a small, careful wine; nearly all of its price is the magic and the name. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

**Route: Starflower wine**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 05 | Hold the vineyard weather through the season | season-long | Halruaan weather mages (arcane service) |  |
| 10 | Harvest and sort | vintage season | Farm labour |  |
| 20 | Crush | hours | Cellarman | [Fruit mill](../../equipment/vinting/fruit-mill.md) |
| 30 | Ferment | 1 to 3 weeks | Cellarman | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 40 | Press | 1 day | Cellarman | [Fruit press](../../equipment/vinting/fruit-press.md) |
| 50 | Age | months | none | [Aging tun](../../equipment/vinting/aging-tun.md) |
| 60 | Bottle, cork and seal | hours | Labourer | [Glass bottle](../../equipment/distilling/glass-bottle.md) |

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Fruit mill](../../equipment/vinting/fruit-mill.md) | 6 gp | 20 |
| [Fermenting vat](../../equipment/brewing/fermenting-vat.md) | 8 gp | 30 |
| [Fruit press](../../equipment/vinting/fruit-press.md) | 19 gp | 40 |
| [Aging tun](../../equipment/vinting/aging-tun.md) | 8 gp | 50 |
| [Glass bottle](../../equipment/distilling/glass-bottle.md) | 1.6 gp, sold with the drink | 60 |

## Cost Roll-up Cross-check

- **No engine recipe to check**; output is the flat 6,972.86 bottles a day at Halarahh against demand of 92 (C10).
- Material cost is under 2 gp, about a tenth of the price. The rest stands for weather-magic, which no engine commodity or wage represents.
### Multi-level roll-up

Added 2026-10-04. The table above costs made inputs at their engine price. Here each made input is costed at its own rolled-up make cost instead: [table wine](wine-common.md#formulation-proposed) at 6.25 gp a cask, [brandy](brandy.md#formulation-proposed) at its liquid cost before bottling, and [glassware](../product/glassware.md#formulation-proposed) at 2.66 gp a 20 lb crate.

| Line | Single-level (engine price) | Multi-level (make cost) | Change |
| --- | --- | --- | --- |
| Glass bottle and cork | 1.64 gp | 0.18 gp | -1.46 gp |
| Grapes, labour and wear (unchanged) | 0.17 gp | 0.17 gp | +0.00 gp |
| **Rolled-up cost per bottle** | **1.81 gp** | **0.35 gp** | **-1.46 gp** |

Against the 18 gp base price the multi-level cost leaves 17.65 gp (98%).

- The bottle was 90% of the single-level cost; at its make cost the physical drink costs well under half a gold piece. Nearly the whole 18 gp is weather-magic and margin.

<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `tag_starflower_wine` 1 (of 325 stored settlements).

**Dedicated `tag_starflower_wine` industry at:** Halarahh (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
