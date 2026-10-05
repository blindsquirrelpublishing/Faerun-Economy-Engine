# Lamp oil

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `lamp_oil`  
**Category:** product  
**Trade unit:** flask (2 lb)  
**Base price:** 0.1 gp per flask (about 0.05 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Lamp oil is a product good in Faerûn, traded in flask lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `whale`, `orchard`, `craft` |
| Demand index | 1.2 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `mining` 1.8, `academic` 1.5 |
| Legacy season multipliers | `winter` 1.4, `summer` 0.85 |
| Storage | 365 days capacity, 0.08% stock loss a day, 30 reserve days |
| Demand calendar | Hammer 11%, Alturiak 10%, Ches 9%, Tarsakh 8%, Mirtul 7%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 8%, Marpenoth 9%, Uktar 10%, Nightal 11% |

## Recipe Links

Inputs for one flask: [Olive oil](../food/olive-oil.md) 0.07.

## Where the Engine Places It

Settlements carrying each producer tag: `whale` 1, `orchard` 4, `craft` 82 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

### Catalogue entry: Oil (component)

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 48 | flammable | 1 gal | 6 sp | 0.072 gp |
| Wizards' Laboratory (components cache) | 48 | nonflammable | 1 gal | 6 sp | 0.072 gp |
| Wizards' Laboratory (components cache) | 48 | spiced | 1 gal | 1 gp | 0.12 gp |
| Wizards' Laboratory (components cache) | 48 | sweet | 1 gal | 7 sp | 0.084 gp |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Scented lamp oil

Imported perfumed lamp oils in several scents.

**Origin given:** Calimshan.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Illuminations | 107 |  | 2 pt flask | 4 sp | 0.193 gp |

Engine price per lb is **0.259 times** the median catalogue price per lb for this entry (engine 0.05 gp/lb; catalogue median 0.193 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
