# Anise seed

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `anise`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 2.4 gp per pound (about 2.4 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Anise seed is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `herb`, `spice` |
| Demand index | 0.25 |
| Luxury (wealth elasticity) | 0.35 |
| Perishable | 0 |
| Demand traits | `cosmopolitan` 1.3 |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Kythorn 10%, Flamerule 20%, Eleasis 30%, Eleint 30%, Marpenoth 10% |
| Regional calendar (cold) | Eleasis 10%, Eleint 50%, Marpenoth 40% |
| Regional calendar (arid) | Alturiak 10%, Ches 30%, Tarsakh 40%, Mirtul 20% |
| Regional calendar (tropical) | Alturiak 10%, Ches 20%, Tarsakh 20%, Eleasis 10%, Eleint 20%, Marpenoth 20% |

## Where the Engine Places It

Settlements carrying each producer tag: `herb` 8, `spice` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 115 |  | oz | 3 cp | 0.48 gp |

Engine price per lb is **5 times** the median catalogue price per lb for this entry (engine 2.4 gp/lb; catalogue median 0.48 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
