# Zurkhwood

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `zurkhwood`  
**Category:** material  
**Trade unit:** load (350 lb)  
**Base price:** 45 gp per load (about 0.129 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Petrified fungus-wood used in drow architecture; forms only in the deep fungal groves near Menzoberranzan.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_zurkhwood` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.3 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_zurkhwood` 1 (of 325 stored settlements).

**Dedicated `tag_zurkhwood` industry at:** Menzoberranzan (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
