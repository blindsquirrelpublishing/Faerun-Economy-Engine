# Mule

[Commodity index](../README.md) · [Livestock](README.md)

**Status:** In the engine  
**Engine ID:** `mule`  
**Category:** livestock  
**Trade unit:** head (10 lb)  
**Base price:** 8 gp per head (about 0.8 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Mule is a livestock good in Faerûn, traded in head lots for daily use, craft, and commerce. A living herd animal traded for labor, food, and transport.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm`, `horse` |
| Demand index | 0.6 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `mining` 2, `mercantile` 1.8, `frontier` 1.6 |
| Storage | 0 days capacity, 0% stock loss a day, 0 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50, `horse` 3 (of 325 stored settlements).

**Specialty at:** Scornubel (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
