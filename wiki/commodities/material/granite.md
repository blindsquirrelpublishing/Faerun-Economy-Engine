# Dressed granite

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `granite`  
**Category:** material  
**Trade unit:** block (800 lb)  
**Base price:** 15 gp per block (about 0.019 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Dressed granite is a material good in Faerûn, traded in block lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `quarry` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `dwarven` 1.6, `temple` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `quarry` 8 (of 325 stored settlements).

**Specialty at:** Airspur (3), Red Larch (2), Yhaunn (3).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 49 | block | 1 in cu | 2 gp |  |
| Wizards' Laboratory (components cache) | 49 | dust | 6 oz | 1 gp | 2.67 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
