# Ziggurat clay

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `ziggurat_clay`  
**Category:** material  
**Trade unit:** load (500 lb)  
**Base price:** 6.5 gp per load (about 0.013 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Fired clay for ritual pottery, drawn from Unther's old riverbed deposits.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_ziggurat_clay` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_ziggurat_clay` 1 (of 325 stored settlements).

**Dedicated `tag_ziggurat_clay` industry at:** Messemprar (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
