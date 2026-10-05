# Ink

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `ink`  
**Category:** product  
**Trade unit:** vial (0.5 lb)  
**Base price:** 8 gp per vial (about 16 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Ink is a product good in Faerûn, traded in vial lots for daily use, craft, and commerce. A written or scholarly good valued by scribes, mages, and record-keepers.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `craft`, `alch` |
| Demand index | 0.2 |
| Luxury (wealth elasticity) | 0.4 |
| Perishable | 0 |
| Demand traits | `academic` 3.5, `arcane` 2.5, `mercantile` 2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one vial: [Charcoal](../material/charcoal.md) 0.01, [Olive oil](../food/olive-oil.md) 0.01.

Used as an input for: [Antitoxin](../arcane/antitoxin.md) (0.02 per unit), [Bound book](../luxury/book.md) (0.25 per unit), [Blank spellbook](../arcane/spellbook-blank.md) (1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `craft` 82, `alch` 17 (of 325 stored settlements).

**Specialty at:** Candlekeep (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 | Ink (black) | 4 oz | 5 sp | 2 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
