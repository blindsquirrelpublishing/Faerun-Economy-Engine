# Parchment

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `parchment`  
**Category:** material  
**Trade unit:** sheet (0.05 lb)  
**Base price:** 0.1 gp per sheet (about 2 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Parchment is a material good in Faerûn, traded in sheet lots for daily use, craft, and commerce. A written or scholarly good valued by scribes, mages, and record-keepers.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tan`, `craft` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `academic` 3, `arcane` 2.5, `mercantile` 1.8, `temple` 1.6 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one sheet: [Tanned leather](../material/leather.md) 0.005.

## Where the Engine Places It

Settlements carrying each producer tag: `tan` 3, `craft` 82 (of 325 stored settlements).

**Specialty at:** Candlekeep (2), Skuld (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
