# Barrel (empty)

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `barrel`  
**Category:** product  
**Trade unit:** barrel (70 lb)  
**Base price:** 2 gp per barrel (about 0.029 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Barrel (empty) is a product good in Faerûn, traded in barrel lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `craft`, `log` |
| Demand index | 0.9 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `port` 1.6, `mercantile` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one barrel: [Sawn planks](../material/planks.md) 0.2, [Wrought iron](../metal/iron-ingot.md) 0.1.

## Where the Engine Places It

Settlements carrying each producer tag: `craft` 82, `log` 15 (of 325 stored settlements).

**Specialty at:** Yartar (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
