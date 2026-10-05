# Coffee beans

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `coffee`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 4 gp per pound (about 4 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Roasted southern beans brewed into a dark, stimulating drink.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `orchard` |
| Demand index | 0.35 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0.1 |
| Demand traits | `cosmopolitan` 1.6, `mercantile` 1.4, `academic` 1.3 |
| Requires | `jungle` |
| Storage | 60 days capacity, 1.2% stock loss a day, 7 reserve days |
| Harvest or production calendar | Flamerule 5%, Eleasis 20%, Eleint 40%, Marpenoth 30%, Uktar 5% |
| Regional calendar (cold) | Eleint 20%, Marpenoth 50%, Uktar 30% |
| Regional calendar (arid) | Hammer 10%, Alturiak 30%, Ches 30%, Tarsakh 10%, Uktar 10%, Nightal 10% |
| Regional calendar (tropical) | Hammer 5%, Alturiak 14%, Ches 19%, Tarsakh 9%, Mirtul 2%, Kythorn 1%, Flamerule 5%, Eleasis 14%, Eleint 19%, Marpenoth 9%, Uktar 2%, Nightal 1% |
| Regional calendar (chult) | Hammer 5%, Alturiak 14%, Ches 19%, Tarsakh 9%, Mirtul 2%, Kythorn 1%, Flamerule 5%, Eleasis 14%, Eleint 19%, Marpenoth 9%, Uktar 2%, Nightal 1% |
| Regional calendar (halruaa) | Hammer 2%, Alturiak 1%, Ches 5%, Tarsakh 14%, Mirtul 19%, Kythorn 9%, Flamerule 2%, Eleasis 1%, Eleint 5%, Marpenoth 14%, Uktar 19%, Nightal 9% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `orchard` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

Roasted and ground coffee imported from Durpar, almost unknown in the North.

**Origin given:** Durpar.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Exotics | 132 |  | lb | 50 gp | 50 gp |

Engine price per lb is **0.08 times** the median catalogue price per lb for this entry (engine 4 gp/lb; catalogue median 50 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
