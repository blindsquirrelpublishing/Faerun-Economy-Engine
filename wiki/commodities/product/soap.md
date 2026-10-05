# Soap

[Commodity index](../README.md) · [Manufactured products](README.md)

**Status:** In the engine  
**Engine ID:** `soap`  
**Category:** product  
**Trade unit:** box (10 lb)  
**Base price:** 2 gp per box (about 0.2 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Soap is a product good in Faerûn, traded in box lots for daily use, craft, and commerce. A practical manufactured good made for everyday trade and labor.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `craft`, `oil` |
| Demand index | 0.6 |
| Luxury (wealth elasticity) | 0.3 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Inputs for one box: [Olive oil](../food/olive-oil.md) 0.25, [Salt](../food/salt.md) 0.03.

## Where the Engine Places It

Settlements carrying each producer tag: `craft` 82, `oil` 0 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

Four-ounce bars in three grades: lye, mild and scented. The Inn and Tavern section separately lists cleaning soap at 8 cp a bar (printed 66).

**Origin given:** Selgaunt.

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Personal Supplies | 101 | lye | 4 oz bar | 1 cp | 0.04 gp |
| Personal Supplies | 101 | mild | 4 oz bar | 1 sp | 0.4 gp |
| Personal Supplies | 101 | scented | 4 oz bar | 1 gp | 4 gp |
| Personal Supplies | 101 | cleaning soap (Inn and Tavern) | bar | 8 cp |  |

Engine price per lb is **0.5 times** the median catalogue price per lb for this entry (engine 0.2 gp/lb; catalogue median 0.4 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
