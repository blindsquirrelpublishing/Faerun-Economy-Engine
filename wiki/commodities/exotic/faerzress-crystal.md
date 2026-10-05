# Faerzress crystal

[Commodity index](../README.md) · [Exotic goods](README.md)

**Status:** In the engine  
**Engine ID:** `faerzress_crystal`  
**Category:** exotic  
**Trade unit:** crystal (3 lb)  
**Base price:** 220 gp per crystal (about 73.33 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Faerzress crystal is a exotic good in Faerûn, traded in crystal lots for daily use, craft, and commerce. A magical trade good used for ritual practice, scholarship, and spellcraft.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_gem`, `arcane` |
| Demand index | 0.015 |
| Luxury (wealth elasticity) | 0.85 |
| Perishable | 0 |
| Demand traits | `drow` 3, `arcane` 3, `magocracy` 2.5 |
| Requires | `cavern`, `drow` |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `mine_gem` 9, `arcane` 24 (of 325 stored settlements).

**Specialty at:** Menzoberranzan (2), Sshamath (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
