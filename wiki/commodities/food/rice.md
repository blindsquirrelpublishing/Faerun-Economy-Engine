# Rice

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `rice`  
**Category:** food  
**Trade unit:** bushel (60 lb)  
**Base price:** 0.9 gp per bushel (about 0.015 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Staple of Halruaa, Mulhorand and the southern river deltas.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm` |
| Demand index | 1.2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.1 |
| Demand traits | `jungle` 2, `desert` 0.6 |
| Legacy season multipliers | `spring` 1.15 |
| Requires | `jungle`, `marsh`, `desert` |
| Storage | 400 days capacity, 0.03% stock loss a day, 75 reserve days |
| Harvest or production calendar | Eleint 40%, Marpenoth 50%, Uktar 10% |
| Regional calendar (cold) | Eleint 20%, Marpenoth 80% |
| Regional calendar (arid) | Tarsakh 8%, Mirtul 33%, Kythorn 8%, Marpenoth 8%, Uktar 33%, Nightal 8% |
| Regional calendar (tropical) | Ches 10%, Tarsakh 30%, Mirtul 10%, Eleasis 10%, Eleint 30%, Marpenoth 10% |

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50 (of 325 stored settlements).

**Specialty at:** Halarahh (3).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 115 |  | lb | 5 gp | 5 gp |

Engine price per lb is **0.003 times** the median catalogue price per lb for this entry (engine 0.015 gp/lb; catalogue median 5 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
