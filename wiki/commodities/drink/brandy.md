# Brandy and firewine

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `brandy`  
**Category:** drink  
**Trade unit:** bottle (3 lb)  
**Base price:** 8 gp per bottle (about 2.67 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Brandy and firewine is a drink good in Faerûn, traded in bottle lots for daily use, craft, and commerce. A prepared beverage prized for hospitality, ceremony, and everyday refreshment.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `distill`, `vint` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `cold` 1.6, `noble` 1.5 |
| Storage | 730 days capacity, 0.01% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one bottle: [Table wine](../drink/wine-common.md) 0.08.

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine bottle is 3 lb, read as about **0.2 gallon** of drink in 1.3 lb of glass; the bottle is sold with it.

| Line | Input | Quantity per bottle | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Table wine | 1.6 gallons (0.13 cask) | [`wine_common`](wine-common.md) | 0.53 gp | About 8 gallons of wine to 1 of brandy, double-distilled |
| 2 | Fuel (firewood) | 0.032 load (about 16 lb) | [`timber`](../material/timber.md) | 0.10 gp | Two runs through the still |
| 3 | Glass bottle and cork | 1 bottle (1.3 lb glass) | [`glassware`](../product/glassware.md) | 1.64 gp | Glassware at 1.25 gp a lb; stoneware would be about 0.16 gp |

| Line | Conversion cost | Basis | Cost per bottle |
| --- | --- | --- | --- |
| 4 | Labour | A distiller (0.65 gp) and a labourer (0.325 gp) fill about 37 bottles a day from two charges, plus bottling | 0.04 gp |
| 5 | Still and aging wear | Pot still and aging tuns held for one to two years | 0.01 gp |

**Rolled-up cost: about 2.32 gp per bottle** (materials 2.27 gp, conversion 0.05 gp). Against the 8 gp base price that leaves about 5.7 gp (71%); brandy carries a luxury margin.

The engine recipe uses 0.08 cask of wine (0.96 gallon), enough for about 0.12 gallon at 8 to 1, so the engine bottle is either smaller or the brandy weaker than this page assumes. The bottle is the largest single cost: a glass bottle costs three times the wine in it. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

Wine comes in by cask from the vintner; see [Table wine](wine-common.md) for that route.

**Route: Brandy**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Stripping run | 1 day a charge | Distiller | [Pot still](../../equipment/distilling/pot-still.md) |
| 20 | Spirit run; cut off the first and last of the flow | 1 day a charge | Distiller | [Pot still](../../equipment/distilling/pot-still.md) |
| 30 | Age in oak | 1 to 2 years | none | [Aging tun](../../equipment/vinting/aging-tun.md) |
| 40 | Bottle, cork and seal | hours | Labourer | [Glass bottle](../../equipment/distilling/glass-bottle.md) |

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Pot still](../../equipment/distilling/pot-still.md) | 72 gp | 10, 20 |
| [Aging tun](../../equipment/vinting/aging-tun.md) | 8 gp | 30 |
| [Glass bottle](../../equipment/distilling/glass-bottle.md) | 1.6 gp, sold with the drink | 40 |
| [Wine cask](../../equipment/vinting/wine-cask.md) | 1.2 gp | incoming wine |

## Cost Roll-up Cross-check

Observed output, 3 Marpenoth 1492 DR, live server, standard quality; inputs at the asking price in the same market, the drink at its producer gate price before merchant markup.

| Market | Wine asking price (cask) | Wine per bottle (0.08 cask) | Brandy producer gate | Wine share | Brandy retail |
| --- | --- | --- | --- | --- | --- |
| Darromar | 5.262 gp | 0.42 gp | 3.770 gp | 11% | 4.647 gp |
| Saerloon | 6.801 gp | 0.54 gp | 5.041 gp | 11% | 5.906 gp |
| Zazesspur | 65.388 gp | 5.23 gp | 5.366 gp | 97% | 6.367 gp |
| Arrabar | 20.548 gp | 1.64 gp | 8.000 gp | 21% | 8.704 gp |
| Crimmor | 10.686 gp | 0.85 gp | 8.000 gp | 11% | 8.705 gp |
| Berdusk | 4.638 gp | 0.37 gp | 7.999 gp | 5% | 8.910 gp |
| Hlondeth | 22.289 gp | 1.78 gp | 8.000 gp | 22% | 9.025 gp |
| Tashluta | 60.682 gp | 4.85 gp | 7.999 gp | 61% | 9.344 gp |
| Nimbral | 54.005 gp | 4.32 gp | 8.000 gp | 54% | 9.551 gp |
| Hlath | 14.427 gp | 1.15 gp | 7.993 gp | 14% | 10.150 gp |
| Base prices | 4 gp | 0.32 gp | 8 gp | 4% | |

- **The engine price ignores the bottle.** No recipe line for glass or stoneware, though the bottle is sold with the brandy. At glassware prices it is the largest material cost (C9).
- **Zazesspur, the biggest producer (about 4,000 bottles a day), clears nothing**: its wine costs 5.23 gp a bottle and its brandy gates at 5.37 gp. Tashluta and Nimbral spend 61% and 54% of the gate on wine before fuel, labour or glass.
- **Gate prices sit at 8 gp (to within 0.01) in seven markets** whatever the wine costs (4.6 to 60.7 gp a cask), so the brandy gate looks pinned to the base price where output is small.
### Multi-level roll-up

Added 2026-10-04. The table above costs made inputs at their engine price. Here each made input is costed at its own rolled-up make cost instead: [table wine](wine-common.md#formulation-proposed) at 6.25 gp a cask, [brandy](brandy.md#formulation-proposed) at its liquid cost before bottling, and [glassware](../product/glassware.md#formulation-proposed) at 2.66 gp a 20 lb crate.

| Line | Single-level (engine price) | Multi-level (make cost) | Change |
| --- | --- | --- | --- |
| Table wine (0.13 cask) | 0.53 gp | 0.83 gp | +0.30 gp |
| Glass bottle and cork | 1.64 gp | 0.18 gp | -1.46 gp |
| Fuel, labour and wear (unchanged) | 0.15 gp | 0.15 gp | +0.00 gp |
| **Rolled-up cost per bottle** | **2.32 gp** | **1.17 gp** | **-1.16 gp** |

Against the 8 gp base price the multi-level cost leaves 6.83 gp (85%).

- Wine at its make cost adds 0.30 gp; the bottle at its make cost saves 1.46 gp. The glass price, not the wine, is what makes engine-priced brandy look expensive.
- Brandy's liquid cost before bottling is 0.98 gp a bottle (4.92 gp a gallon), which [fire-wine](fire-wine.md) uses in its own multi-level roll-up.

<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `distill` 0, `vint` 13 (of 325 stored settlements).

**Specialty at:** Darromar (2), Saerloon (2), Zazesspur (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
