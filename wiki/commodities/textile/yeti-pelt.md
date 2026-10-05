# Yeti pelt

[Commodity index](../README.md) · [Textiles](README.md)

**Status:** In the engine  
**Engine ID:** `yeti_pelt`  
**Category:** textile  
**Trade unit:** bundle (20 lb)  
**Base price:** 55 gp per bundle (about 2.75 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Thick white pelt taken from Icewind Dale's high-country yetis; the fur doesn't hold its loft anywhere warmer.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_yeti_pelt` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_yeti_pelt` 1 (of 325 stored settlements).

**Dedicated `tag_yeti_pelt` industry at:** Bryn Shander (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
