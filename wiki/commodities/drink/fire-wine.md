# Fire-wine

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `fire_wine`  
**Category:** drink  
**Trade unit:** bottle (3 lb)  
**Base price:** 11 gp per bottle (about 3.67 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Spiced, fortified wine brewed hot; the recipe doesn't survive transit without Red Wizard preservation charms.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_fire_wine` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.4 |
| Perishable | 0.1 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine bottle is 3 lb, read as about **0.2 gallon** of drink in 1.3 lb of glass; the bottle is sold with it.

| Line | Input | Quantity per bottle | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Table wine | 0.17 gallon (0.014 cask) | [`wine_common`](wine-common.md) | 0.06 gp | Base of the drink |
| 2 | Brandy | 0.03 gallon (0.15 bottle) | [`brandy`](brandy.md) | 1.20 gp | Fortifying spirit, at the brandy base price |
| 3 | Spices | 0.05 lb | [`spices_common`](../food/spices-common.md) | 0.10 gp | "Spiced"; which spices is unrecorded |
| 4 | Honey | 0.1 lb | [`honey`](../food/honey.md) | 0.01 gp | Assumed, to balance the spirit |
| 5 | Fuel (firewood) | about 2 lb | [`timber`](../material/timber.md) | 0.01 gp | "Brewed hot" |
| 6 | Glass bottle and cork | 1 bottle | [`glassware`](../product/glassware.md) | 1.64 gp | As for brandy |
| 7 | Red Wizard preservation charm | 1 per bottle | none (arcane service) | not priced | The engine description says the drink does not survive transit without it |

| Line | Conversion cost | Basis | Cost per bottle |
| --- | --- | --- | --- |
| 8 | Labour | Heating, fortifying and bottling, about 0.05 gp a bottle | 0.05 gp |
| 9 | Equipment wear | Copper and bottling tools | 0.01 gp |

**Rolled-up cost: about 3.08 gp per bottle** (materials 3.02 gp, conversion 0.06 gp). Against the 11 gp base price that leaves about 7.9 gp before the charm. Whatever a Red Wizard charges for a preservation charm comes out of that.

No engine recipe: fire-wine comes from the industry tag `tag_fire_wine` at Eltabbar. *Aurora's* Old Empires fire wine is sold in bulk (18 sp a 12-gallon cask); the engine sells a preserved, bottled Thayan luxury, which the existing page notes. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

Wine and brandy come in from their own routes.

**Route: Fire-wine**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Heat wine with spices and honey | 2 to 3 hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md) |
| 20 | Fortify with brandy | hours | Brewer | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 30 | Bottle, cork and seal | hours | Labourer | [Glass bottle](../../equipment/distilling/glass-bottle.md) |
| 40 | Lay the preservation charm | per batch | Red Wizard (arcane service) |  |

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Brewing copper](../../equipment/brewing/brewing-copper.md) | 60 gp | 10 |
| [Fermenting vat](../../equipment/brewing/fermenting-vat.md) | 8 gp | 20 |
| [Glass bottle](../../equipment/distilling/glass-bottle.md) | 1.6 gp, sold with the drink | 30 |
| [Brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) | 2 gp | 10, 30 |

## Cost Roll-up Cross-check

- **No engine recipe to check**; output is the flat 6,972.86 bottles a day at Eltabbar against demand of 124 (C10).
- Brandy is the largest input; at base prices the formulation leaves room for the charm. A source for what a preservation charm costs would settle the margin.
### Multi-level roll-up

Added 2026-10-04. The table above costs made inputs at their engine price. Here each made input is costed at its own rolled-up make cost instead: [table wine](wine-common.md#formulation-proposed) at 6.25 gp a cask, [brandy](brandy.md#formulation-proposed) at its liquid cost before bottling, and [glassware](../product/glassware.md#formulation-proposed) at 2.66 gp a 20 lb crate.

| Line | Single-level (engine price) | Multi-level (make cost) | Change |
| --- | --- | --- | --- |
| Table wine (0.014 cask) | 0.06 gp | 0.09 gp | +0.03 gp |
| Brandy (0.15 bottle) | 1.20 gp | 0.15 gp | -1.05 gp |
| Glass bottle and cork | 1.64 gp | 0.18 gp | -1.46 gp |
| Spices, honey, fuel, labour and wear (unchanged) | 0.18 gp | 0.18 gp | +0.00 gp |
| **Rolled-up cost per bottle** | **3.08 gp** | **0.60 gp** | **-2.48 gp** |

Against the 11 gp base price the multi-level cost leaves 10.40 gp (95%).

- Two price layers fall away: brandy bought at 8 gp a bottle becomes brandy made for about 1 gp, and the bottle drops from glassware price to glassware cost.
- The Red Wizard preservation charm is still unpriced; at multi-level cost there is about 10.4 gp a bottle for it and the margin.

<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `tag_fire_wine` 1 (of 325 stored settlements).

**Dedicated `tag_fire_wine` industry at:** Eltabbar (2).

## Aurora's Whole Realms Catalogue

**Note:** The engine trades fire-wine by the 3 lb bottle as a preserved Thayan luxury; the catalogue sells Old Empires fire wine in bulk containers. The large ratio reflects that difference in trade unit and market.

Thick, near-black, very strong spiced wine with a reputation as a remedy.

**Origin given:** Old Empires.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wines and Ales | 130 |  | hand keg (2 gal) | 38 cp | 0.023 gp |
| Wines and Ales | 130 |  | cask (12 gal) | 18 sp | 0.018 gp |
| Wines and Ales | 130 |  | barrel (30 gal) | 46 sp | 0.018 gp |
| Wines and Ales | 130 |  | butt (100 gal) | 15 gp | 0.018 gp |
| Wines and Ales | 130 |  | tun (250 gal) | 38 gp | 0.018 gp |

Engine price per lb is **200 times** the median catalogue price per lb for this entry (engine 3.67 gp/lb; catalogue median 0.018 gp/lb). The catalogue is below the engine here; worth a look during the commodity review.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
