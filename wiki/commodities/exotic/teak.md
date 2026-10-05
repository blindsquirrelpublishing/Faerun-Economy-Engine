# Chultan teak

[Commodity index](../README.md) · [Exotic goods](README.md)

**Status:** In the engine  
**Engine ID:** `teak`  
**Category:** exotic  
**Trade unit:** load (400 lb)  
**Base price:** 25 gp per load (about 0.062 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Chultan teak is a exotic good in Faerûn, traded in load lots for daily use, craft, and commerce. A rare and often imported good prized for its scarcity and prestige.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `log` |
| Demand index | 0.1 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `port` 2, `noble` 2, `jungle` 0.4 |
| Requires | `jungle` |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `log` 15 (of 325 stored settlements).

**Specialty at:** Port Nyanzaru (3).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
