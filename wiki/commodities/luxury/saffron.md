# Saffron

[Commodity index](../README.md) · [Luxury goods](README.md)

**Status:** In the engine  
**Engine ID:** `saffron`  
**Category:** luxury  
**Trade unit:** pound (1 lb)  
**Base price:** 35 gp per pound (about 35 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Saffron is a luxury good in Faerûn, traded in pound lots for daily use, craft, and commerce. A refined luxury good sought by elites, merchants, and collectors.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `herb` |
| Demand index | 0.035 |
| Luxury (wealth elasticity) | 1 |
| Perishable | 0 |
| Demand traits | `noble` 3.5, `temple` 1.6 |
| Requires | `desert` |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Eleint 10%, Marpenoth 50%, Uktar 40% |
| Regional calendar (arid) | Eleint 20%, Marpenoth 50%, Uktar 30% |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `herb` 8 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 50 | Saffron (ground) | 4 oz | 4 gp | 16 gp |
| Aurora's Larder | 117 |  | oz | 45 gp | 720 gp |

Engine price per lb is **0.0486 times** the median catalogue price per lb for this entry (engine 35 gp/lb; catalogue median 720 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
