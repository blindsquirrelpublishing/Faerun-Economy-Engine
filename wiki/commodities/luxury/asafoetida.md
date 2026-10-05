# Asafoetida

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `asafoetida`  
**Category:** luxury  
**Trade unit:** pound (1 lb)  
**Base price:** 7.5 gp per pound (about 7.5 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Asafoetida is a luxury good in Faerûn, traded in pound lots for daily use, craft, and commerce. A refined luxury good sought by elites, merchants, and collectors.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `herb` |
| Demand index | 0.08 |
| Luxury (wealth elasticity) | 0.65 |
| Perishable | 0 |
| Demand traits | `desert` 1.6, `cosmopolitan` 1.4 |
| Requires | `desert` |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Ches 2%, Tarsakh 7%, Mirtul 16%, Kythorn 25%, Flamerule 25%, Eleasis 16%, Eleint 8%, Marpenoth 2% |
| Regional calendar (cold) | Kythorn 10%, Flamerule 30%, Eleasis 40%, Eleint 20% |
| Regional calendar (arid) | Hammer 4%, Alturiak 7%, Ches 22%, Tarsakh 22%, Mirtul 7%, Kythorn 1%, Flamerule 1%, Eleasis 1%, Eleint 7%, Marpenoth 15%, Uktar 7%, Nightal 4% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `herb` 8 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 49 |  | 3 oz | 5 sp | 2.67 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
