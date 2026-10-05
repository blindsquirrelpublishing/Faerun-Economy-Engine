# Saddle and tack

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `saddle`  
**Category:** product  
**Trade unit:** saddle (25 lb)  
**Base price:** 10 gp per saddle (about 0.4 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Saddle and tack is a product good in Faerûn, traded in saddle lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tan`, `craft` |
| Demand index | 0.25 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `military` 1.8, `frontier` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one saddle: [Tanned leather](../material/leather.md) 2, [Wrought iron](../metal/iron-ingot.md) 0.2.

Used as an input for: [Warhorse](../livestock/warhorse.md) (1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `tan` 3, `craft` 82 (of 325 stored settlements).

**Specialty at:** Crimmor (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
