# Raw amber

[Commodity index](../README.md) · [Gems](README.md)

**Status:** In the engine  
**Engine ID:** `raw_amber`  
**Category:** gem  
**Trade unit:** stone (0.1 lb)  
**Base price:** 40 gp per stone (about 400 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Uncut coastal amber, cheaper than the polished amber already in trade; Sembian jewelers keep the best pieces home.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_raw_amber` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.4 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_raw_amber` 1 (of 325 stored settlements).

**Dedicated `tag_raw_amber` industry at:** Selgaunt (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
