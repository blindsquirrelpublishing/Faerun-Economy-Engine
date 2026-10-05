# Crossbow

[Commodity index](../README.md) · [Arms and armour](README.md)

**Status:** In the engine  
**Engine ID:** `crossbow`  
**Category:** arms  
**Trade unit:** crossbow (5 lb)  
**Base price:** 25 gp per crossbow (about 5 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Crossbow is a arms good in Faerûn, traded in crossbow lots for daily use, craft, and commerce. A weapon or protective item forged for war, hunting, and martial service.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `weapon`, `smith`, `craft` |
| Demand index | 0.12 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `military` 2.5, `dwarven` 2, `gnome` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one crossbow: [Steel billet](../metal/steel-ingot.md) 0.2, [Sawn planks](../material/planks.md) 0.01, [Hemp rope](../product/rope.md) 0.01.

## Where the Engine Places It

Settlements carrying each producer tag: `weapon` 15, `smith` 33, `craft` 82 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
