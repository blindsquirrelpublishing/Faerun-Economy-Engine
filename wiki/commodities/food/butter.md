# Butter

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `butter`  
**Category:** food  
**Trade unit:** firkin (25 lb)  
**Base price:** 2 gp per firkin (about 0.08 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Butter is a food good in Faerûn, traded in firkin lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `cattle` |
| Demand index | 0.9 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.7 |
| Legacy season multipliers | `summer` 0.85, `winter` 1.3 |
| Storage | 14 days capacity, 4% stock loss a day, 2 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `cattle` 7 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
