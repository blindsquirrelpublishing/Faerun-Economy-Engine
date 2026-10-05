# Bricks

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `bricks`  
**Category:** material  
**Trade unit:** load (500 lb)  
**Base price:** 2 gp per load (about 0.004 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Bricks is a material good in Faerûn, traded in load lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `pottery`, `quarry` |
| Demand index | 0.9 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `pottery` 3, `quarry` 8 (of 325 stored settlements).

**Specialty at:** Memnon (2), Red Larch (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
