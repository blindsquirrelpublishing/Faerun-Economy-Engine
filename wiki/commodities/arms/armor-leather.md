# Leather armor

[Commodity index](../README.md) · [Arms and armour](README.md)

**Status:** In the engine  
**Engine ID:** `armor_leather`  
**Category:** arms  
**Trade unit:** suit (10 lb)  
**Base price:** 10 gp per suit (about 1 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Leather armor is a arms good in Faerûn, traded in suit lots for daily use, craft, and commerce. A weapon or protective item forged for war, hunting, and martial service.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tan`, `armor` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `military` 2.5, `mercenary` 2.5, `frontier` 1.8 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one suit: [Tanned leather](../material/leather.md) 1.

## Where the Engine Places It

Settlements carrying each producer tag: `tan` 3, `armor` 16 (of 325 stored settlements).

**Specialty at:** Zhentil Keep (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
