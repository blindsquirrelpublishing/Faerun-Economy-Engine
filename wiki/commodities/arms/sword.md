# Longsword

[Commodity index](../README.md) · [Arms and armour](README.md)

**Status:** In the engine  
**Engine ID:** `sword`  
**Category:** arms  
**Trade unit:** blade (3 lb)  
**Base price:** 15 gp per blade (about 5 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Longsword is a arms good in Faerûn, traded in blade lots for daily use, craft, and commerce. A weapon or protective item forged for war, hunting, and martial service.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `weapon`, `smith` |
| Demand index | 0.25 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `military` 3, `mercenary` 3, `frontier` 1.8, `noble` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one blade: [Steel billet](../metal/steel-ingot.md) 0.3, [Tanned leather](../material/leather.md) 0.08.

## Where the Engine Places It

Settlements carrying each producer tag: `weapon` 15, `smith` 33 (of 325 stored settlements).

**Specialty at:** Arabel (2), Luthcheq (2), Saradush (1), Sundabar (2), Suzail (2), Zhentil Keep (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
