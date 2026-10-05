# Tea and herbal infusions

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `tea`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 3 gp per pound (about 3 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Tea and herbal infusions is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `herb`, `spice` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `noble` 1.8, `academic` 1.5 |
| Storage | 270 days capacity, 0.15% stock loss a day, 60 reserve days |
| Harvest or production calendar | Ches 2%, Tarsakh 7%, Mirtul 16%, Kythorn 25%, Flamerule 25%, Eleasis 16%, Eleint 8%, Marpenoth 2% |
| Regional calendar (cold) | Kythorn 10%, Flamerule 30%, Eleasis 40%, Eleint 20% |
| Regional calendar (arid) | Hammer 4%, Alturiak 7%, Ches 22%, Tarsakh 22%, Mirtul 7%, Kythorn 1%, Flamerule 1%, Eleasis 1%, Eleint 7%, Marpenoth 15%, Uktar 7%, Nightal 4% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Where the Engine Places It

Settlements carrying each producer tag: `herb` 8, `spice` 4 (of 325 stored settlements).

**Specialty at:** Phsant (2).

## Aurora's Whole Realms Catalogue

Shou teas; Pale Jade is mild, Earth Dragon's Eye stronger.

**Origin given:** Shou Lung.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Exotics | 134 | Pale Jade | lb | 20 gp | 20 gp |
| Exotics | 134 | Earth Dragon's Eye | lb | 50 gp | 50 gp |

Engine price per lb is **0.0857 times** the median catalogue price per lb for this entry (engine 3 gp/lb; catalogue median 35 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
