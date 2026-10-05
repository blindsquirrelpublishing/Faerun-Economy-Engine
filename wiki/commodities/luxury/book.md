# Bound book

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `book`  
**Category:** luxury  
**Trade unit:** volume (3 lb)  
**Base price:** 25 gp per volume (about 8.33 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Bound book is a luxury good in Faerûn, traded in volume lots for daily use, craft, and commerce. A written or scholarly good valued by scribes, mages, and record-keepers.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `paper`, `craft` |
| Required skill | `paper` 2 |
| Demand index | 0.1 |
| Luxury (wealth elasticity) | 0.85 |
| Perishable | 0 |
| Demand traits | `academic` 4, `arcane` 2.5, `noble` 2, `temple` 1.8 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one volume: [Paper](../material/paper.md) 100, [Tanned leather](../material/leather.md) 0.25, [Ink](../product/ink.md) 0.25.

## Where the Engine Places It

Settlements carrying each producer tag: `paper` 8, `craft` 82 (of 325 stored settlements).

**Specialty at:** Candlekeep (3), Cimbar (2), Silverymoon (2), [Waterdeep](../../../locations/waterdeep.md) (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
