# Holy water

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `holy_water`  
**Category:** arcane  
**Trade unit:** flask (1 lb)  
**Base price:** 25 gp per flask (about 25 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Holy water is a arcane good in Faerûn, traded in flask lots for daily use, craft, and commerce. A magical trade good used by spellcasters, scholars, and ritualists.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `temple` |
| Demand index | 0.05 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `temple` 4, `frontier` 1.5 |
| Storage | 730 days capacity, 0.01% stock loss a day, 30 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `temple` 16 (of 325 stored settlements).

**Specialty at:** Bezantur (2), Elturel (3), Tantras (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
