# Singing crystal

[Commodity index](../README.md) · [Gems](README.md)

**Status:** In the engine  
**Engine ID:** `singing_crystal`  
**Category:** gem  
**Trade unit:** crystal (0.5 lb)  
**Base price:** 240 gp per crystal (about 480 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Resonant crystal grown in Evereska's hidden vale, used as a bardic and arcane focus.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_singing_crystal` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.9 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_singing_crystal` 1 (of 325 stored settlements).

**Dedicated `tag_singing_crystal` industry at:** Scornubel (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
