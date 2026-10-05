# Cloves

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `cloves`  
**Category:** luxury  
**Trade unit:** pound (1 lb)  
**Base price:** 14 gp per pound (about 14 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Cloves is a luxury good in Faerûn, traded in pound lots for daily use, craft, and commerce. A refined luxury good sought by elites, merchants, and collectors.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `orchard` |
| Demand index | 0.1 |
| Luxury (wealth elasticity) | 0.85 |
| Perishable | 0 |
| Demand traits | `noble` 2.2, `mercantile` 1.4 |
| Requires | `jungle` |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Mirtul 5%, Kythorn 10%, Flamerule 20%, Eleasis 30%, Eleint 20%, Marpenoth 10%, Uktar 5% |
| Regional calendar (cold) | Flamerule 10%, Eleasis 30%, Eleint 40%, Marpenoth 20% |
| Regional calendar (arid) | Hammer 5%, Alturiak 10%, Ches 20%, Tarsakh 20%, Mirtul 5%, Eleint 5%, Marpenoth 10%, Uktar 20%, Nightal 5% |
| Regional calendar (tropical) | Hammer 5%, Alturiak 11%, Ches 16%, Tarsakh 11%, Mirtul 5%, Kythorn 3%, Flamerule 5%, Eleasis 11%, Eleint 16%, Marpenoth 11%, Uktar 5%, Nightal 3% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `orchard` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 38 | Clove | 4 oz | 1 sp | 0.4 gp |
| Aurora's Larder | 117 |  | oz | 35 gp | 560 gp |

Engine price per lb is **0.025 times** the median catalogue price per lb for this entry (engine 14 gp/lb; catalogue median 560 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
