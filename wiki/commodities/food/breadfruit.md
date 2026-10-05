# Breadfruit

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `breadfruit`  
**Category:** food  
**Trade unit:** crate (30 lb)  
**Base price:** 0.9 gp per crate (about 0.03 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A jungle staple, cheap and filling, distinct from the luxury chultan fruit already in trade.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_breadfruit` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.7 |
| Legacy season multipliers | `autumn` 1.1, `spring` 1.2, `summer` 0.75, `winter` 1.35 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_breadfruit` 1 (of 325 stored settlements).

**Dedicated `tag_breadfruit` industry at:** Port Nyanzaru (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
