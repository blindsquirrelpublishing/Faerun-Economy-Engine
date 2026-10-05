# Black pepper

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `black_pepper`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 6 gp per pound (about 6 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Black pepper is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice` |
| Demand index | 0.35 |
| Luxury (wealth elasticity) | 0.55 |
| Perishable | 0 |
| Demand traits | `cosmopolitan` 1.5, `mercantile` 1.3 |
| Requires | `jungle` |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Mirtul 5%, Kythorn 10%, Flamerule 20%, Eleasis 30%, Eleint 20%, Marpenoth 10%, Uktar 5% |
| Regional calendar (cold) | Flamerule 10%, Eleasis 30%, Eleint 40%, Marpenoth 20% |
| Regional calendar (arid) | Hammer 5%, Alturiak 10%, Ches 20%, Tarsakh 20%, Mirtul 5%, Eleint 5%, Marpenoth 10%, Uktar 20%, Nightal 5% |
| Regional calendar (tropical) | Hammer 5%, Alturiak 11%, Ches 16%, Tarsakh 11%, Mirtul 5%, Kythorn 3%, Flamerule 5%, Eleasis 11%, Eleint 16%, Marpenoth 11%, Uktar 5%, Nightal 3% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 38 |  | 4 oz | 2 sp | 0.8 gp |
| Aurora's Larder | 117 | Marsembian | oz | 15 gp | 240 gp |
| Aurora's Larder | 117 | Durparian black | oz | 30 gp | 480 gp |
| Aurora's Larder | 117 | Malatran | oz | 40 gp | 640 gp |

Engine price per lb is **0.0125 times** the median catalogue price per lb for this entry (engine 6 gp/lb; catalogue median 480 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
