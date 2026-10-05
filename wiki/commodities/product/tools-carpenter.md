# Artisan's tools

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `tools_carpenter`  
**Category:** product  
**Trade unit:** kit (15 lb)  
**Base price:** 8 gp per kit (about 0.533 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Artisan's tools is a product good in Faerûn, traded in kit lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `craft`, `smith` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `frontier` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one kit: [Steel billet](../metal/steel-ingot.md) 1, [Sawn planks](../material/planks.md) 0.02.

## Where the Engine Places It

Settlements carrying each producer tag: `craft` 82, `smith` 33 (of 325 stored settlements).

**Specialty at:** Procampur (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
