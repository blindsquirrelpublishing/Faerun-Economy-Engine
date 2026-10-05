# Paper

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `paper`  
**Category:** material  
**Trade unit:** sheet (0.05 lb)  
**Base price:** 0.2 gp per sheet (about 4 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Paper is a material good in Faerûn, traded in sheet lots for daily use, craft, and commerce. A written or scholarly good valued by scribes, mages, and record-keepers.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `paper`, `craft` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `academic` 3, `arcane` 2, `mercantile` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one sheet: [Timber](../material/timber.md) 0.0002.

Used as an input for: [Bound book](../luxury/book.md) (100 per unit), [Blank spellbook](../arcane/spellbook-blank.md) (150 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `paper` 8, `craft` 82 (of 325 stored settlements).

**Specialty at:** Skuld (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
