# Ivory

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `ivory`  
**Category:** luxury  
**Trade unit:** tusk (40 lb)  
**Base price:** 100 gp per tusk (about 2.5 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Ivory is a luxury good in Faerûn, traded in tusk lots for daily use, craft, and commerce. A refined luxury good sought by elites, merchants, and collectors.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `ivory` |
| Demand index | 0.05 |
| Luxury (wealth elasticity) | 0.95 |
| Perishable | 0 |
| Demand traits | `noble` 2.5, `cosmopolitan` 1.6 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Used as an input for: [Knucklehead scrimshaw](../exotic/scrimshaw.md) (0.1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `ivory` 1 (of 325 stored settlements).

**Specialty at:** Port Nyanzaru (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
