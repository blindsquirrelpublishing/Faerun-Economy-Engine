# Illusionist's veil

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `illusionists_veil`  
**Category:** arcane  
**Trade unit:** bolt (8 lb)  
**Base price:** 190 gp per bolt (about 23.75 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Cloth treated with a permanent minor-illusion weave, a Nimbral specialty.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_illusionists_veil` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.85 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_illusionists_veil` 1 (of 325 stored settlements).

**Dedicated `tag_illusionists_veil` industry at:** Nimbral (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
