# Blank spellbook

[Commodity index](../README.md) · [Arcane goods](README.md)

**Status:** In the engine  
**Engine ID:** `spellbook_blank`  
**Category:** arcane  
**Trade unit:** book (3 lb)  
**Base price:** 50 gp per book (about 16.67 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> A durable vellum or prepared-paper volume made by specialist binders in major scribal and magical centers.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `paper` |
| Demand index | 0.02 |
| Luxury (wealth elasticity) | 0.7 |
| Perishable | 0 |
| Demand traits | `arcane` 4, `academic` 3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one book: [Paper](../material/paper.md) 150, [Tanned leather](../material/leather.md) 1, [Ink](../product/ink.md) 1.

## Where the Engine Places It

Settlements carrying each producer tag: `paper` 8 (of 325 stored settlements).

**Specialty at:** Candlekeep (1), Eltabbar (3), Halarahh (3), Silverymoon (2), Sshamath (2), [Waterdeep](../../../locations/waterdeep.md) (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
