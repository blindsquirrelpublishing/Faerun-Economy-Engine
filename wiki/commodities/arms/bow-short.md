# Shortbow

[Commodity index](../README.md) · [Arms and armour](README.md)

**Status:** In the engine  
**Engine ID:** `bow_short`  
**Category:** arms  
**Trade unit:** bow (2 lb)  
**Base price:** 25 gp per bow (about 12.5 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Shortbow is a arms good in Faerûn, traded in bow lots for daily use, craft, and commerce. A weapon or protective item forged for war, hunting, and martial service.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `weapon`, `craft` |
| Demand index | 0.15 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `military` 2, `elven` 2.5, `hunt` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one bow: [Sawn planks](../material/planks.md) 0.005, [Hemp rope](../product/rope.md) 0.01.

## Where the Engine Places It

Settlements carrying each producer tag: `weapon` 15, `craft` 82 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
