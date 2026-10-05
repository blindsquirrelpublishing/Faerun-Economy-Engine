# Candles

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `candles`  
**Category:** product  
**Trade unit:** box (15 lb)  
**Base price:** 2.5 gp per box (about 0.167 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Candles is a product good in Faerûn, traded in box lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `craft`, `oil`, `temple` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `temple` 2, `academic` 1.5 |
| Legacy season multipliers | `winter` 1.45, `autumn` 1.15, `summer` 0.8 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |
| Demand calendar | Hammer 11%, Alturiak 10%, Ches 9%, Tarsakh 8%, Mirtul 7%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 8%, Marpenoth 9%, Uktar 10%, Nightal 11% |

## Recipe Links

Inputs for one box: [Beeswax](../material/wax.md) 1.5.

## Where the Engine Places It

Settlements carrying each producer tag: `craft` 82, `oil` 0, `temple` 16 (of 325 stored settlements).

**Specialty at:** Elturel (1).

## Aurora's Whole Realms Catalogue

Tallow or beeswax candles priced by size: base price covers up to 1 ft long and 1/2 in thick, with a surcharge for each extra 6 in or 1/2 in.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Illuminations | 106 | tallow, base size | each | 1 cp |  |
| Illuminations | 106 | beeswax, base size | each | 5 cp |  |

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Candles:

[Torches](../product/torches.md), [Wicks](../product/wicks.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
