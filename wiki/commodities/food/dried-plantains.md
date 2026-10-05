# Dried plantains

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `dried_plantains`  
**Category:** food  
**Trade unit:** crate (18 lb)  
**Base price:** 2.2 gp per crate (about 0.122 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Sliced and sun-dried on the Tashalar docks before the crate ever goes to sea.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_dried_plantains` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.05 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_dried_plantains` 1 (of 325 stored settlements).

**Dedicated `tag_dried_plantains` industry at:** Tashluta (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
