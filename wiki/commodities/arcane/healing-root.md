# Healing root

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `healing_root`  
**Category:** arcane  
**Trade unit:** bundle (2 lb)  
**Base price:** 3.5 gp per bundle (about 1.75 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A woodland root used in salves; it doesn't take well to transplanting outside Cormanthor's soil.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_healing_root` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.15 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_healing_root` 1 (of 325 stored settlements).

**Dedicated `tag_healing_root` industry at:** Highmoon (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
