# Corn (maize)

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `corn`  
**Category:** food  
**Trade unit:** bushel (56 lb)  
**Base price:** 0.7 gp per bushel (about 0.012 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> A common field crop grown wherever the local climate supports farming.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm` |
| Demand index | 1.4 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.15 |
| Legacy season multipliers | `autumn` 0.8, `winter` 1.15, `spring` 1.2 |
| Storage | 400 days capacity, 0.03% stock loss a day, 75 reserve days |
| Harvest or production calendar | Eleasis 10%, Eleint 40%, Marpenoth 40%, Uktar 10% |
| Regional calendar (cold) | Eleint 10%, Marpenoth 70%, Uktar 20% |
| Regional calendar (arid) | Tarsakh 10%, Mirtul 30%, Kythorn 10%, Marpenoth 10%, Uktar 30%, Nightal 10% |
| Regional calendar (tropical) | Ches 10%, Tarsakh 30%, Mirtul 10%, Eleint 10%, Marpenoth 30%, Uktar 10% |

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 38 | Corn | 1 lb | 1 sp | 0.1 gp |
| Priests' Alcove (spell components) | 38 | Mayz | 1 lb | 2 gp | 2 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
