# Pottery

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `pottery`  
**Category:** product  
**Trade unit:** crate (40 lb)  
**Base price:** 3 gp per crate (about 0.075 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Pottery is a product good in Faerûn, traded in crate lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `pottery` |
| Demand index | 1.1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.05 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `pottery` 3 (of 325 stored settlements).

**Specialty at:** Iriaebor (2), Wheloon (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
