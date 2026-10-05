# Hemp rope

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `rope`  
**Category:** product  
**Trade unit:** coil (10 lb)  
**Base price:** 1 gp per coil (about 0.1 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Hemp rope is a product good in Faerûn, traded in coil lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `rope`, `farm` |
| Demand index | 0.9 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `port` 2, `mining` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Used as an input for: [Longbow](../arms/bow-long.md) (0.012 per unit), [Shortbow](../arms/bow-short.md) (0.01 per unit), [Crossbow](../arms/crossbow.md) (0.01 per unit), [Fishing net](../product/fishing-net.md) (2 per unit), [Sailcloth and canvas](../product/sailcloth.md) (0.5 per unit), [River boat](../product/ship-boat.md) (5 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `rope` 4, `farm` 50 (of 325 stored settlements).

**Specialty at:** Baldur's Gate (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 75 |  |  | 1 cp |  |

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
