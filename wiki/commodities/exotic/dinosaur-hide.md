# Dinosaur hide

[Commodity index](../README.md) · [Exotic goods](README.md)

**Status:** In the engine  
**Engine ID:** `dinosaur_hide`  
**Category:** exotic  
**Trade unit:** hide (30 lb)  
**Base price:** 60 gp per hide (about 2 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Dinosaur hide is a exotic good in Faerûn, traded in hide lots for daily use, craft, and commerce. A rare and often imported good prized for its scarcity and prestige.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `hunt`, `tan` |
| Demand index | 0.04 |
| Luxury (wealth elasticity) | 0.8 |
| Perishable | 0 |
| Demand traits | `jungle` 0.5, `noble` 2, `military` 1.5 |
| Requires | `jungle` |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `hunt` 6, `tan` 3 (of 325 stored settlements).

**Specialty at:** Port Nyanzaru (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
