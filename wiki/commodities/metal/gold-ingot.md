# Gold

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `gold_ingot`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 480 gp per ingot (about 48 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Gold is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mineral or refined metal traded for tools, industry, and coinage.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_gold` |
| Demand index | 0.08 |
| Luxury (wealth elasticity) | 0.8 |
| Perishable | 0 |
| Demand traits | `noble` 2.5, `mercantile` 2, `temple` 1.6 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `mine_gold` 2 (of 325 stored settlements).

## Coin Standard

Minting assumption (see [method](../README.md#coin-standard)): a pound of metal strikes 50 coins in principle; 4% is assumed lost to casting scrap, blank trimming and assay, leaving **48 gold pieces per lb**.

| Measure | Value |
| --- | --- |
| Ingot weight | 10 lb |
| Coins in principle | 500 gp |
| Coins minted (net of 4% loss) | 480 gp |
| Bullion value of one ingot | 480 gp |
| Bullion value per lb | 48 gp |
| Engine base price | 480 gp (1.00 times bullion value) |

The engine price equals minted value: a mint would not pay more than the coins an ingot strikes, and a seller would not take less. Set on 2026-10-04 (C1).

Aurora's bar and ingot prices are not used for this metal: they value it well below the coins it would strike, so a buyer could mint the bars at a profit. They are kept below for reference only.

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 | bell | 3 oz | 5 gp | 26.67 gp |
| Priests' Alcove (spell components) | 36 | caltrops | 2 oz | 3 gp | 24 gp |
| Priests' Alcove (spell components) | 36 | chunk | 1 oz | 5 gp | 80 gp |
| Priests' Alcove (spell components) | 36 | dust | 2 oz | 2 sp | 1.6 gp |
| Priests' Alcove (spell components) | 36 | tissue | 5 in sq | 10 gp |  |
| Priests' Alcove (spell components) | 36 | wire | 1 ft | 3 gp |  |
| Wizards' Laboratory (components cache) | 48 | needles | 5 | 15 gp |  |
| Wizards' Laboratory (components cache) | 48 | powder | 1 oz | 1 gp | 16 gp |
| Laborers' List (metals) | 60 | bar | 1 lb | 11 gp | 11 gp |
| Laborers' List (metals) | 60 | ingot | 3 lb | 29 gp | 9.67 gp |
| Laborers' List (metals) | 60 | sheet | 8 in sq | 9 gp |  |
| Laborers' List (metals) | 60 | strip | 4 by 1 in | 4 gp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 1 gp |  |

Catalogue bars and ingots run 9.67 gp to 11 gp per lb, against a bullion value of 48 gp per lb (20% to 23% of minted value).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
