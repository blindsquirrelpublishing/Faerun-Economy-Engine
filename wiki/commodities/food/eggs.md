# Eggs

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `eggs`  
**Category:** food  
**Trade unit:** crate (15 lb)  
**Base price:** 0.5 gp per crate (about 0.033 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Eggs is a food good in Faerûn, traded in crate lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm` |
| Demand index | 1.3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.9 |
| Legacy season multipliers | `winter` 1.4 |
| Storage | 21 days capacity, 2.5% stock loss a day, 3 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
