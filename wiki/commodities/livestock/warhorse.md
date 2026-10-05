# Warhorse

[Commodity index](../README.md) · [Livestock](README.md)

**Status:** In the engine  
**Engine ID:** `warhorse`  
**Category:** livestock  
**Trade unit:** head (20 lb)  
**Base price:** 400 gp per head (about 20 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Warhorse is a livestock good in Faerûn, traded in head lots for daily use, craft, and commerce. A living herd animal traded for labor, food, and transport.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `horse` |
| Demand index | 0.08 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `military` 3.5, `noble` 2.5, `mercenary` 2.5 |
| Storage | 0 days capacity, 0% stock loss a day, 0 reserve days |

## Recipe Links

Inputs for one head: [Riding horse](../livestock/horse-riding.md) 1, [Grain (wheat)](../food/grain.md) 20, [Saddle and tack](../product/saddle.md) 1.

## Where the Engine Places It

Settlements carrying each producer tag: `horse` 3 (of 325 stored settlements).

**Specialty at:** [Amphail](../../../locations/amphail.md) (1), Arabel (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
