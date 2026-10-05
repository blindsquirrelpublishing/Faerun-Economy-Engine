# Dwarven spirits

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `dwarven_spirits`  
**Category:** luxury  
**Trade unit:** jack (5 lb)  
**Base price:** 10 gp per jack (about 2 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Dwarven spirits is a luxury good in Faerûn, traded in jack lots for daily use, craft, and commerce. A refined luxury good sought by elites, merchants, and collectors.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `distill`, `brew` |
| Demand index | 0.2 |
| Luxury (wealth elasticity) | 0.7 |
| Perishable | 0 |
| Demand traits | `dwarven` 3, `military` 1.4 |
| Storage | 730 days capacity, 0.01% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one jack: [Grain (wheat)](../food/grain.md) 0.08.

## Where the Engine Places It

Settlements carrying each producer tag: `distill` 0, `brew` 18 (of 325 stored settlements).

**Specialty at:** Citadel Adbar (2), Mithral Hall (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
