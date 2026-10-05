# Tanned leather

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `leather`  
**Category:** material  
**Trade unit:** hide (10 lb)  
**Base price:** 2 gp per hide (about 0.2 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Tanned leather is a material good in Faerûn, traded in hide lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tan`, `cattle`, `herd` |
| Demand index | 1.3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Used as an input for: [Leather armor](../arms/armor-leather.md) (1 per unit), [Plate armor](../arms/armor-plate.md) (0.5 per unit), [Bound book](../luxury/book.md) (0.25 per unit), [Dagger](../arms/dagger.md) (0.03 per unit), [Parchment](../material/parchment.md) (0.005 per unit), [Saddle and tack](../product/saddle.md) (2 per unit), [Shield](../arms/shield.md) (0.1 per unit), [Blank spellbook](../arcane/spellbook-blank.md) (1 per unit), [Longsword](../arms/sword.md) (0.08 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `tan` 3, `cattle` 7, `herd` 11 (of 325 stored settlements).

**Specialty at:** Crimmor (3).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 75 |  | hide | 2 gp |  |

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
