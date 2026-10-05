# Deep runestone

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `deep_runestone`  
**Category:** arcane  
**Trade unit:** stone (5 lb)  
**Base price:** 95 gp per stone (about 19 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Pre-inscribed enchanting stone from Citadel Adbar's forge-priests; the method is a clan secret.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_deep_runestone` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_deep_runestone` 1 (of 325 stored settlements).

**Dedicated `tag_deep_runestone` industry at:** Silverymoon (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
