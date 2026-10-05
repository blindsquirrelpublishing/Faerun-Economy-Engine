# Oak timber

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `oak_timber`  
**Category:** material  
**Trade unit:** load (500 lb)  
**Base price:** 3.75 gp per load (about 0.0075 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Old-growth hardwood from two unrelated stands: common Vilhon Reach lumber out of Chondath, and higher-priced Cormanthor-edge oak cut under elven-treaty limits out of the Dalelands.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_oak_timber` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.05 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_oak_timber` 2 (of 325 stored settlements).

**Dedicated `tag_oak_timber` industry at:** [Arrabar](../../../locations/arrabar.md) (2), Highmoon (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
