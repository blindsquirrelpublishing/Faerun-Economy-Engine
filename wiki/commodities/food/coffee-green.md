# Green coffee beans

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `coffee_green`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 2 gp per pound (about 2 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Dried, unroasted southern coffee beans for local roasting. Fictional modeling assumptions: 2 gp/lb reference price, one tenth of roasted coffee's transit perishability, and 82 percent roasting yield. Demand is a trade-input proxy, not additional beverage consumption.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `orchard` |
| Demand index | 0.35 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0.01 |
| Demand traits | `cosmopolitan` 1.6, `mercantile` 1.4, `academic` 1.3 |
| Requires | `jungle` |
| Storage | 365 days capacity, 0.05% stock loss a day, 60 reserve days |
| Harvest or production calendar | Flamerule 5%, Eleasis 20%, Eleint 40%, Marpenoth 30%, Uktar 5% |
| Regional calendar (cold) | Eleint 20%, Marpenoth 50%, Uktar 30% |
| Regional calendar (arid) | Hammer 10%, Alturiak 30%, Ches 30%, Tarsakh 10%, Uktar 10%, Nightal 10% |
| Regional calendar (tropical) | Hammer 5%, Alturiak 14%, Ches 19%, Tarsakh 9%, Mirtul 2%, Kythorn 1%, Flamerule 5%, Eleasis 14%, Eleint 19%, Marpenoth 9%, Uktar 2%, Nightal 1% |
| Regional calendar (chult) | Hammer 5%, Alturiak 14%, Ches 19%, Tarsakh 9%, Mirtul 2%, Kythorn 1%, Flamerule 5%, Eleasis 14%, Eleint 19%, Marpenoth 9%, Uktar 2%, Nightal 1% |
| Regional calendar (halruaa) | Hammer 2%, Alturiak 1%, Ches 5%, Tarsakh 14%, Mirtul 19%, Kythorn 9%, Flamerule 2%, Eleasis 1%, Eleint 5%, Marpenoth 14%, Uktar 19%, Nightal 9% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `orchard` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 37 | Coffee beans | 1 lb | 5 gp | 5 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
