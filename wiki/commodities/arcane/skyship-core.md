# Skyship elemental core

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `skyship_core`  
**Category:** arcane  
**Trade unit:** core (40 lb)  
**Base price:** 2,200 gp per core (about 55 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A bound air or fire elemental, the heart of every Halruaan skyship. Made only in Halarahh's binding-towers.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_skyship_core` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 1 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_skyship_core` 1 (of 325 stored settlements).

**Dedicated `tag_skyship_core` industry at:** Halarahh (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
