# Earthmother's amber

[Commodity index](../README.md) · [Gems](README.md)

**Status:** In the engine  
**Engine ID:** `earthmothers_amber`  
**Category:** gem  
**Trade unit:** stone (0.1 lb)  
**Base price:** 175 gp per stone (about 1,750 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Amber sacred to the Earthmother faith, gathered only from the Moonshae shore-shrines.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_earthmothers_amber` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.9 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_earthmothers_amber` 1 (of 325 stored settlements).

**Dedicated `tag_earthmothers_amber` industry at:** Caer Calidyrr (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
