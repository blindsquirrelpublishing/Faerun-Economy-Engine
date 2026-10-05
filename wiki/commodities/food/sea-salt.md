# Sea salt

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `sea_salt`  
**Category:** food  
**Trade unit:** sack (50 lb)  
**Base price:** 2 gp per sack (about 0.04 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Pan-evaporated along the coast; the Yuir Isles' shallows make the yield unusually pure. Sword Coast and Moonshae pan-evaporators produce a coarser grade at lower cost; Aglarond's Yuir Isles yield stays the premium pick.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_sea_salt` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_sea_salt` 3 (of 325 stored settlements).

**Dedicated `tag_sea_salt` industry at:** Caer Calidyrr (2), Candlekeep (2), Velprintalar (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
