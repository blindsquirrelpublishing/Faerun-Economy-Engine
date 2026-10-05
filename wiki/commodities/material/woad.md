# Woad

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `woad`  
**Category:** material  
**Trade unit:** pound (1 lb)  
**Base price:** 13 gp per pound (about 13 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Sacred blue war-dye; loses its color if dried anywhere but the Moonshaes.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_woad` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.3 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_woad` 1 (of 325 stored settlements).

**Dedicated `tag_woad` industry at:** Caer Calidyrr (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
