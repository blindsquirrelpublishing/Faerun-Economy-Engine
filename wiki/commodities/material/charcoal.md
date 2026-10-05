# Charcoal

[Commodity index](../README.md) · [Materials](README.md)

**Status:** In the engine  
**Engine ID:** `charcoal`  
**Category:** material  
**Trade unit:** sack (40 lb)  
**Base price:** 1 gp per sack (about 0.025 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Charcoal is a material good in Faerûn, traded in sack lots for daily use, craft, and commerce. A bulk material that serves as the foundation of building, crafting, and repair.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `log`, `craft` |
| Demand index | 1.2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Legacy season multipliers | `winter` 1.35 |
| Storage | 400 days capacity, 0.01% stock loss a day, 45 reserve days |
| Demand calendar | Hammer 12%, Alturiak 11%, Ches 9%, Tarsakh 8%, Mirtul 7%, Kythorn 6%, Flamerule 5%, Eleasis 6%, Eleint 7%, Marpenoth 9%, Uktar 10%, Nightal 11% |

## Recipe Links

Inputs for one sack: [Timber](../material/timber.md) 0.12.

Used as an input for: [Incense](../luxury/incense.md) (0.01 per unit), [Ink](../product/ink.md) (0.01 per unit), [Wrought iron](../metal/iron-ingot.md) (0.04 per unit), [Smokepowder](../exotic/smokepowder.md) (0.2 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `log` 15, `craft` 82 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 |  | 1 lb | 1 gp | 1 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
