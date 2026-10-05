# Cattle horn

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `cattle_horn`  
**Category:** material  
**Trade unit:** bundle (10 lb)  
**Base price:** 1.5 gp per bundle (about 0.15 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Horn and bone for tool handles and glue, a byproduct of the Vast's grazing economy. Western Heartlands ranches contribute a comparable byproduct stream.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_cattle_horn` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_cattle_horn` 2 (of 325 stored settlements).

**Dedicated `tag_cattle_horn` industry at:** Ravens Bluff (2), Scornubel (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
