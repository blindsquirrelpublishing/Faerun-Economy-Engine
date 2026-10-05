# Adamantine

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `adamantine_ingot`  
**Category:** metal  
**Trade unit:** ingot (5 lb)  
**Base price:** 800 gp per ingot (about 160 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Adamantine is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mined or refined metal valued for armor, tools, and industry.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_adamantine` |
| Demand index | 0.02 |
| Luxury (wealth elasticity) | 0.7 |
| Perishable | 0 |
| Demand traits | `dwarven` 3, `military` 2.2, `drow` 2.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `mine_adamantine` 1 (of 325 stored settlements).

**Specialty at:** Gracklstugh (2), Menzoberranzan (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
