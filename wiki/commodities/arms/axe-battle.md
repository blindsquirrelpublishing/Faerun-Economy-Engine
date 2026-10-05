# Battleaxe

[Commodity index](../README.md) · [Arms and armour](README.md)

**Status:** In the engine  
**Engine ID:** `axe_battle`  
**Category:** arms  
**Trade unit:** axe (4 lb)  
**Base price:** 10 gp per axe (about 2.5 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Battleaxe is a arms good in Faerûn, traded in axe lots for daily use, craft, and commerce. A weapon or protective item forged for war, hunting, and martial service.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `weapon`, `smith` |
| Demand index | 0.2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `military` 2.5, `dwarven` 2.5, `orc` 2.5, `mercenary` 2.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one axe: [Steel billet](../metal/steel-ingot.md) 0.35, [Sawn planks](../material/planks.md) 0.01.

## Where the Engine Places It

Settlements carrying each producer tag: `weapon` 15, `smith` 33 (of 325 stored settlements).

**Specialty at:** Citadel Adbar (3), Citadel Felbarr (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
