# Copper

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `copper_ingot`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 4.8 gp per ingot (about 0.48 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Copper is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mineral or refined metal traded for tools, industry, and coinage.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_copper`, `smith` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `mine_copper` 1, `smith` 33 (of 325 stored settlements).

## Coin Standard

Minting assumption (see [method](../README.md#coin-standard)): a pound of metal strikes 50 coins in principle; 4% is assumed lost to casting scrap, blank trimming and assay, leaving **48 copper pieces per lb**.

| Measure | Value |
| --- | --- |
| Ingot weight | 10 lb |
| Coins in principle | 500 cp |
| Coins minted (net of 4% loss) | 480 cp |
| Bullion value of one ingot | 4.8 gp |
| Bullion value per lb | 0.48 gp |
| Engine base price | 4.8 gp (1.00 times bullion value) |

The engine price equals minted value: a mint would not pay more than the coins an ingot strikes, and a seller would not take less. Set on 2026-10-04 (C1).

Aurora's bar and ingot prices are not used for this metal: they value it well below the coins it would strike, so a buyer could mint the bars at a profit. They are kept below for reference only.

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 48 | square | 2 in | 2 cp |  |
| Wizards' Laboratory (components cache) | 48 | wire | 1 ft | 1 sp |  |
| Laborers' List (metals) | 60 | bar | 1 lb | 6 cp | 0.06 gp |
| Laborers' List (metals) | 60 | ingot | 7 lb | 25 cp | 0.036 gp |
| Laborers' List (metals) | 60 | sheet | 16 in sq | 1 sp |  |
| Laborers' List (metals) | 60 | strip | 8 by 1 in | 3 cp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 3 cp |  |

Catalogue bars and ingots run 0.036 gp to 0.06 gp per lb, against a bullion value of 0.48 gp per lb (7% to 12% of minted value).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
