# Amber

[Commodity index](../README.md) · [Gems](README.md)

**Status:** In the engine  
**Engine ID:** `amber`  
**Category:** gem  
**Trade unit:** stone (0.1 lb)  
**Base price:** 100 gp per stone (about 1,000 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Amber is a gem good in Faerûn, traded in stone lots for daily use, craft, and commerce. A prized mineral or gemstone traded for ornament, wealth, and arcane study.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `amber` |
| Demand index | 0.05 |
| Luxury (wealth elasticity) | 0.95 |
| Perishable | 0 |
| Demand traits | `noble` 2, `arcane` 1.6 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `amber` 1 (of 325 stored settlements).

**Specialty at:** Ruathym (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 48 | block | 1 in cu | 8 sp |  |
| Wizards' Laboratory (components cache) | 48 | powder | 12 oz | 1 gp | 1.33 gp |
| Wizards' Laboratory (components cache) | 48 | rod | 6 in | 10 gp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
