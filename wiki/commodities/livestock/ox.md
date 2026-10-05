# Ox

[Commodity index](../README.md) · [Livestock](README.md)

**Status:** In the engine  
**Engine ID:** `ox`  
**Category:** livestock  
**Trade unit:** head (15 lb)  
**Base price:** 15 gp per head (about 1 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Ox is a livestock good in Faerûn, traded in head lots for daily use, craft, and commerce. A living herd animal traded for labor, food, and transport.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `cattle`, `farm` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `agrarian` 2, `frontier` 1.5 |
| Storage | 0 days capacity, 0% stock loss a day, 0 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `cattle` 7, `farm` 50 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
