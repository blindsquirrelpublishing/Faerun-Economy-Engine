# Underdark spider silk

[Commodity index](../README.md) · [Exotic goods](README.md)

**Status:** In the engine  
**Engine ID:** `spider_silk`  
**Category:** exotic  
**Trade unit:** bolt (6 lb)  
**Base price:** 90 gp per bolt (about 15 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Underdark spider silk is a exotic good in Faerûn, traded in bolt lots for daily use, craft, and commerce. A woven textile valued for clothing, furnishing, and caravan gear.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `silk` |
| Demand index | 0.03 |
| Luxury (wealth elasticity) | 0.9 |
| Perishable | 0 |
| Demand traits | `drow` 3, `noble` 1.6, `arcane` 1.5 |
| Requires | `cavern`, `drow` |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `silk` 4 (of 325 stored settlements).

**Specialty at:** Menzoberranzan (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
