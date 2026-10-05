# Deep rothe cheese

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `deep_rothe_cheese`  
**Category:** food  
**Trade unit:** wheel (20 lb)  
**Base price:** 9 gp per wheel (about 0.45 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Made from Underdark rothe milk by Blingdenstone's svirfneblin; the herds do not survive on the surface.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_deep_rothe_cheese` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.1 |
| Perishable | 0.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_deep_rothe_cheese` 1 (of 325 stored settlements).

**Dedicated `tag_deep_rothe_cheese` industry at:** Gracklstugh (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
