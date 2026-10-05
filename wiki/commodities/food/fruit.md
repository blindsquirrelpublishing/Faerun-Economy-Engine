# Fruit

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `fruit`  
**Category:** food  
**Trade unit:** crate (30 lb)  
**Base price:** 1 gp per crate (about 0.033 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Fruit is a food good in Faerûn, traded in crate lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `orchard`, `farm` |
| Demand index | 1.2 |
| Luxury (wealth elasticity) | 0.2 |
| Perishable | 0.85 |
| Legacy season multipliers | `summer` 0.7, `autumn` 0.65, `winter` 1.9, `spring` 1.4 |
| Storage | 10 days capacity, 8% stock loss a day, 1 reserve days |
| Harvest or production calendar | Mirtul 2%, Kythorn 8%, Flamerule 16%, Eleasis 25%, Eleint 33%, Marpenoth 16% |
| Regional calendar (cold) | Flamerule 7%, Eleasis 27%, Eleint 53%, Marpenoth 13% |
| Regional calendar (arid) | Hammer 2%, Alturiak 3%, Ches 7%, Tarsakh 13%, Mirtul 13%, Kythorn 7%, Flamerule 1%, Eleasis 3%, Eleint 13%, Marpenoth 20%, Uktar 13%, Nightal 3% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Recipe Links

Used as an input for: [Table wine](../drink/wine-common.md) (3.5 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `orchard` 4, `farm` 50 (of 325 stored settlements).

**Specialty at:** Goldenfields (2).

**Configured shortage at:** Blingdenstone, Bryn Shander, Citadel Adbar, Citadel Felbarr, Easthaven, Good Mead, Gracklstugh, Lonelywood, Luskan, Mantol-Derith, Memnon, Menzoberranzan, Mirabar, Mithral Hall, Orlumbor, Ruathym, Sshamath, Sundabar, Targos, Termalaine.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Fruit:

[Fruit butters](../food/fruit-butters.md), [Fruit cheeses](../food/fruit-cheeses.md), [Fruit curds](../food/fruit-curds.md), [Jams](../food/jams.md), [Jellies](../food/jellies.md), [Marmalades](../food/marmalades.md), [Preserves](../food/preserves.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
