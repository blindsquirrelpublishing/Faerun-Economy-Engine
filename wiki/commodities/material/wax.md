# Beeswax

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `wax`  
**Category:** material  
**Trade unit:** block (10 lb)  
**Base price:** 3 gp per block (about 0.3 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Beeswax is a material good in Faerûn, traded in block lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm`, `orchard` |
| Demand index | 0.4 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `temple` 1.8 |
| Storage | 400 days capacity, 0.01% stock loss a day, 45 reserve days |

## Recipe Links

Used as an input for: [Candles](../product/candles.md) (1.5 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50, `orchard` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

### Catalogue entry: Wax

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 37 | common | 1 lb | 3 gp | 3 gp |
| Priests' Alcove (spell components) | 37 | white | 1/2 lb | 4 gp | 8 gp |
| Wizards' Laboratory (components cache) | 49 |  | 1 lb | 2 sp | 0.2 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Beeswax

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 49 |  | 1 lb | 1 sp | 0.1 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Scented beeswax

Beeswax treated to remove the honey smell and perfumed instead, in about a dozen scents.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Illuminations | 106 |  | lb | 14 sp | 1.4 gp |

Engine price per lb is **0.214 times** the median catalogue price per lb for this entry (engine 0.3 gp/lb; catalogue median 1.4 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
