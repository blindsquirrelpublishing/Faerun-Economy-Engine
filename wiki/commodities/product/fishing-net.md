# Fishing net

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `fishing_net`  
**Category:** product  
**Trade unit:** net (20 lb)  
**Base price:** 4 gp per net (about 0.2 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Fishing net is a product good in Faerûn, traded in net lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `rope`, `textile` |
| Demand index | 0.2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `port` 2.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one net: [Hemp rope](../product/rope.md) 2.

## Where the Engine Places It

Settlements carrying each producer tag: `rope` 4, `textile` 23 (of 325 stored settlements).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
