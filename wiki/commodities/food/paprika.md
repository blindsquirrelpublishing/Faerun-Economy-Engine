# Paprika

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `paprika`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 3.4 gp per pound (about 3.4 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Paprika is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `farm` |
| Demand index | 0.34 |
| Luxury (wealth elasticity) | 0.3 |
| Perishable | 0 |
| Demand traits | `cosmopolitan` 1.3 |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `farm` 50 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Exotics | 134 |  | oz. | 30 gp | 480 gp |

Engine price per lb is **0.00708 times** the median catalogue price per lb for this entry (engine 3.4 gp/lb; catalogue median 480 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
