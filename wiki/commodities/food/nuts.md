# Nuts and dried fruit

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `nuts`  
**Category:** food  
**Trade unit:** sack (40 lb)  
**Base price:** 2 gp per sack (about 0.05 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Nuts and dried fruit is a food good in Faerûn, traded in sack lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `orchard` |
| Demand index | 0.7 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.15 |
| Legacy season multipliers | `autumn` 0.8 |
| Storage | 270 days capacity, 0.1% stock loss a day, 30 reserve days |
| Harvest or production calendar | Eleasis 5%, Eleint 30%, Marpenoth 50%, Uktar 15% |
| Regional calendar (cold) | Eleint 10%, Marpenoth 70%, Uktar 20% |
| Regional calendar (arid) | Flamerule 10%, Eleasis 30%, Eleint 40%, Marpenoth 20% |
| Regional calendar (tropical) | Hammer 5%, Alturiak 9%, Ches 18%, Tarsakh 9%, Mirtul 5%, Kythorn 5%, Flamerule 5%, Eleasis 9%, Eleint 18%, Marpenoth 9%, Uktar 5%, Nightal 5% |

## Where the Engine Places It

Settlements carrying each producer tag: `orchard` 4 (of 325 stored settlements).

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Nuts and dried fruit:

[Almonds](../food/almonds.md), [Cashews](../food/cashews.md), [Chestnuts](../food/chestnuts.md), [Currants](../food/currants.md), [Dried apricots](../food/dried-apricots.md), [Dried broad beans](../food/dried-broad-beans.md), [Dried carrots](../food/dried-carrots.md), [Dried cherries](../food/dried-cherries.md), [Dried elderberries](../food/dried-elderberries.md), [Dried green beans](../food/dried-green-beans.md), [Dried green peas](../food/dried-green-peas.md), [Dried mushrooms of Brost](../food/dried-mushrooms-of-brost.md), [Dried onion rings](../food/dried-onion-rings.md), [Hazelnuts](../food/hazelnuts.md), [Palintrike of Calimshan](../food/palintrike-of-calimshan.md), [Pine nuts](../food/pine-nuts.md), [Pistachios](../food/pistachios.md), [Prunes](../food/prunes.md), [Raisins](../food/raisins.md), [Walnuts](../food/walnuts.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
