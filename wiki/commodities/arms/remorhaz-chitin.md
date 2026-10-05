# Remorhaz chitin plate

[Commodity index](../README.md) · [Arms and armour](README.md)

**Status:** In the engine  
**Engine ID:** `remorhaz_chitin`  
**Category:** arms  
**Trade unit:** plate (25 lb)  
**Base price:** 210 gp per plate (about 8.4 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Armor plate from hunted remorhaz; the creatures exist nowhere outside the Dale's ice sheets.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_remorhaz_chitin` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_remorhaz_chitin` 1 (of 325 stored settlements).

**Dedicated `tag_remorhaz_chitin` industry at:** Bryn Shander (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
