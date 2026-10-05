# Sailcloth and canvas

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `sailcloth`  
**Category:** product  
**Trade unit:** bolt (30 lb)  
**Base price:** 12 gp per bolt (about 0.4 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Sailcloth and canvas is a product good in Faerûn, traded in bolt lots for daily use, craft, and commerce. A woven textile valued for clothing, furnishing, and caravan gear.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `textile`, `rope` |
| Demand index | 0.3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `port` 3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one bolt: [Linen cloth](../textile/linen.md) 1.2, [Hemp rope](../product/rope.md) 0.5.

Used as an input for: [River boat](../product/ship-boat.md) (2 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `textile` 23, `rope` 4 (of 325 stored settlements).

**Specialty at:** Baldur's Gate (2), Marsember (2), Murann (1), Orlumbor (2).

## Aurora's Whole Realms Catalogue

### Catalogue entry: Canvas

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 75 |  | sq yd | 1 sp |  |

### Catalogue entry: Sailcloth

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Tailors' Corner | 75 |  | sq yd | 1 sp |  |

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
