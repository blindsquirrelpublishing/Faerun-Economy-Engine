# Walrus ivory

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `walrus_ivory`  
**Category:** material  
**Trade unit:** tusk (8 lb)  
**Base price:** 30 gp per tusk (about 3.75 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Raw ivory, unworked; the finished scrimshaw already in the catalog is carved from stock like this. Trackless Sea whaling and sealing crews bring in a smaller supplementary haul.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_walrus_ivory` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.3 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_walrus_ivory` 2 (of 325 stored settlements).

**Dedicated `tag_walrus_ivory` industry at:** Bryn Shander (2), Ruathym (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
