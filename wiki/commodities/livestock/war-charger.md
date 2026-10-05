# War-charger

[Commodity index](../README.md) · [Livestock](README.md)

**Status:** In the engine  
**Engine ID:** `war_charger`  
**Category:** livestock  
**Trade unit:** head (20 lb)  
**Base price:** 650 gp per head (about 32.5 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A named bloodline bred only in Chessenta's plains studs.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_war_charger` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.4 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 0 days capacity, 0% stock loss a day, 0 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_war_charger` 1 (of 325 stored settlements).

**Dedicated `tag_war_charger` industry at:** Mordulkin (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
