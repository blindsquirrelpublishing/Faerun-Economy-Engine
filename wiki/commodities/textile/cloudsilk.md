# Cloudsilk

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `cloudsilk`  
**Category:** textile  
**Trade unit:** bolt (8 lb)  
**Base price:** 105 gp per bolt (about 13.12 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Sail-cloth for cloud ships; Nimbral's isolationism keeps the technique off the mainland.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_cloudsilk` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.85 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_cloudsilk` 1 (of 325 stored settlements).

**Dedicated `tag_cloudsilk` industry at:** Nimbral (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
