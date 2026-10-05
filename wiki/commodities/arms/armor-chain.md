# Chain mail

[Commodity index](../README.md) · [Arms and armour](README.md)

**Status:** In the engine  
**Engine ID:** `armor_chain`  
**Category:** arms  
**Trade unit:** suit (55 lb)  
**Base price:** 75 gp per suit (about 1.36 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Chain mail is a arms good in Faerûn, traded in suit lots for daily use, craft, and commerce. A weapon or defensive item made for war, hunting, and personal protection.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `armor`, `smith` |
| Demand index | 0.1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `military` 3, `mercenary` 3, `dwarven` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one suit: [Steel billet](../metal/steel-ingot.md) 5.5.

## Where the Engine Places It

Settlements carrying each producer tag: `armor` 16, `smith` 33 (of 325 stored settlements).

**Specialty at:** Darromar (1), Melvaunt (1), Mithral Hall (2), Sundabar (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
