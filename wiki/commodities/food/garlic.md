# Garlic

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `garlic`  
**Category:** food  
**Trade unit:** bundle (2 lb)  
**Base price:** 0.3 gp per bundle (about 0.15 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> (none set)

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_garlic` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_garlic` 1 (of 325 stored settlements).

**Dedicated `tag_garlic` industry at:** Baldur's Gate (2).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 38 | Garlic bud | 1 lg | 5 cp |  |
| Wizards' Laboratory (components cache) | 50 | Garlic clove | 1 lg | 3 cp |  |
| Aurora's Larder | 115 |  | oz | 1 cp | 0.16 gp |

Engine price per lb is **0.938 times** the median catalogue price per lb for this entry (engine 0.15 gp/lb; catalogue median 0.16 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
