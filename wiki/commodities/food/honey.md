# Honey

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `honey`  
**Category:** food  
**Trade unit:** crock (10 lb)  
**Base price:** 1.5 gp per crock (about 0.15 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Honey is a food good in Faerûn, traded in crock lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm`, `orchard` |
| Demand index | 0.6 |
| Luxury (wealth elasticity) | 0.2 |
| Perishable | 0.05 |
| Storage | 730 days capacity, 0.005% stock loss a day, 45 reserve days |

## Recipe Links

Used as an input for: [Mead](../drink/mead.md) (0.6 per unit), [Potion of healing](../arcane/potion-healing.md) (0.02 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50, `orchard` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

### Catalogue entry: Honeycomb

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 49 |  | 6 in sq | 1 gp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Honey

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 117 | Neverwinter | Pt. | 1 sp | 0.096 gp |
| Aurora's Larder | 117 | rose petal | Pt. | 5 sp | 0.482 gp |
| Aurora's Larder | 117 | parsley | Pt. | 3 sp | 0.289 gp |
| Aurora's Larder | 117 | Sembian lavender | Pt. | 1 gp | 0.964 gp |

Engine price per lb is **0.389 times** the median catalogue price per lb for this entry (engine 0.15 gp/lb; catalogue median 0.386 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
