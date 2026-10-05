# Silver ore

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `silver_ore`  
**Category:** metal  
**Trade unit:** load (100 lb)  
**Base price:** 35 gp per load (about 0.35 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Unsmelted; Mirabar exports the raw ore under strict guild licence rather than finished ingots.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_silver_ore` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.2 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_silver_ore` 1 (of 325 stored settlements).

**Dedicated `tag_silver_ore` industry at:** Mirabar (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
