# Pitch and tar

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `pitch`  
**Category:** material  
**Trade unit:** barrel (60 lb)  
**Base price:** 4 gp per barrel (about 0.067 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Pitch and tar is a material good in Faerûn, traded in barrel lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `log`, `ship` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `port` 2.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one barrel: [Timber](../material/timber.md) 0.12.

## Where the Engine Places It

Settlements carrying each producer tag: `log` 15, `ship` 48 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

### Catalogue entry: Pitch

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 49 |  | 1 qt | 5 cp | 0.024 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Pine tar

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 50 |  | 1 lb | 1 sp | 0.1 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Pitch (roofing)

Pitch sold for sealing roofs and setting tiles.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Laborers' List | 56 |  | lb | 1 sp | 0.1 gp |

Engine price per lb is **0.667 times** the median catalogue price per lb for this entry (engine 0.067 gp/lb; catalogue median 0.1 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
