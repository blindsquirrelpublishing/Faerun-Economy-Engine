# Cassia bark

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `cassia`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 7 gp per pound (about 7 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Cassia bark is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `orchard` |
| Demand index | 0.2 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `cosmopolitan` 1.4 |
| Requires | `jungle` |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Mirtul 5%, Kythorn 10%, Flamerule 20%, Eleasis 30%, Eleint 20%, Marpenoth 10%, Uktar 5% |
| Regional calendar (cold) | Flamerule 10%, Eleasis 30%, Eleint 40%, Marpenoth 20% |
| Regional calendar (arid) | Hammer 5%, Alturiak 10%, Ches 20%, Tarsakh 20%, Mirtul 5%, Eleint 5%, Marpenoth 10%, Uktar 20%, Nightal 5% |
| Regional calendar (tropical) | Hammer 5%, Alturiak 11%, Ches 16%, Tarsakh 11%, Mirtul 5%, Kythorn 3%, Flamerule 5%, Eleasis 11%, Eleint 16%, Marpenoth 11%, Uktar 5%, Nightal 3% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `orchard` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 38 |  | 4 oz | 1 gp | 4 gp |
| Wizards' Laboratory (components cache) | 50 | bark | 6 oz | 6 sp | 1.6 gp |
| Wizards' Laboratory (components cache) | 50 | buds | 2 spgs | 2 sp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
