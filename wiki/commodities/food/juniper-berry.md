# Juniper berries

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `juniper_berry`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 2 gp per pound (about 2 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Juniper berries is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `herb`, `orchard` |
| Demand index | 0.2 |
| Luxury (wealth elasticity) | 0.2 |
| Perishable | 0 |
| Demand traits | `cold` 1.5, `frontier` 1.3 |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Mirtul 2%, Kythorn 8%, Flamerule 16%, Eleasis 25%, Eleint 33%, Marpenoth 16% |
| Regional calendar (cold) | Flamerule 7%, Eleasis 27%, Eleint 53%, Marpenoth 13% |
| Regional calendar (arid) | Hammer 2%, Alturiak 3%, Ches 7%, Tarsakh 13%, Mirtul 13%, Kythorn 7%, Flamerule 1%, Eleasis 3%, Eleint 13%, Marpenoth 20%, Uktar 13%, Nightal 3% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Where the Engine Places It

Settlements carrying each producer tag: `herb` 8, `orchard` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 115 |  | oz | 3 sp | 4.8 gp |

Engine price per lb is **0.417 times** the median catalogue price per lb for this entry (engine 2 gp/lb; catalogue median 4.8 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
