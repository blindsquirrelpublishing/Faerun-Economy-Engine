# River lotus oil

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `river_lotus_oil`  
**Category:** luxury  
**Trade unit:** vial (0.5 lb)  
**Base price:** 48 gp per vial (about 96 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Perfume oil from the sacred lotus, harvested under priesthood control.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_river_lotus_oil` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.85 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_river_lotus_oil` 1 (of 325 stored settlements).

**Dedicated `tag_river_lotus_oil` industry at:** Skuld (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
