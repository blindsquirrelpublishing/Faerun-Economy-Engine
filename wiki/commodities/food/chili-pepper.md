# Chili pepper

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `chili_pepper`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 3 gp per pound (about 3 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Chili pepper is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `farm` |
| Demand index | 0.38 |
| Luxury (wealth elasticity) | 0.25 |
| Perishable | 0.1 |
| Demand traits | `jungle` 1.5, `cosmopolitan` 1.2 |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Mirtul 2%, Kythorn 8%, Flamerule 16%, Eleasis 25%, Eleint 33%, Marpenoth 16% |
| Regional calendar (cold) | Flamerule 7%, Eleasis 27%, Eleint 53%, Marpenoth 13% |
| Regional calendar (arid) | Hammer 2%, Alturiak 3%, Ches 7%, Tarsakh 13%, Mirtul 13%, Kythorn 7%, Flamerule 1%, Eleasis 3%, Eleint 13%, Marpenoth 20%, Uktar 13%, Nightal 3% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `farm` 50 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

Maztican chili pods, hotter than Malatran pepper; sold whole on strings or ground.

**Origin given:** Maztica.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Exotics | 132 | whole | lb | 100 gp | 100 gp |
| Exotics | 132 | ground | oz | 20 gp | 320 gp |

Engine price per lb is **0.0143 times** the median catalogue price per lb for this entry (engine 3 gp/lb; catalogue median 210 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
