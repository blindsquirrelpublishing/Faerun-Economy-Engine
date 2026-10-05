# Platinum

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `platinum_ingot`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 2,400 gp per ingot (about 240 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Platinum bullion in 10 lb ingots. Priced at bullion value under the coin standard: 50 coins to the pound, 4% minting loss, so 480 platinum pieces (5 gp each) per ingot.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_platinum_ore` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0.5 |
| Perishable | 0 |
| Demand traits | `noble` 1.3 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `tag_platinum_ore` 1 (of 325 stored settlements).

## Coin Standard

Minting assumption (see [method](../README.md#coin-standard)): a pound of metal strikes 50 coins in principle; 4% is assumed lost to casting scrap, blank trimming and assay, leaving **48 platinum pieces per lb**.

| Measure | Value |
| --- | --- |
| Ingot weight | 10 lb |
| Coins in principle | 500 pp |
| Coins minted (net of 4% loss) | 480 pp |
| Bullion value of one ingot | 2,400 gp |
| Bullion value per lb | 240 gp |
| Engine base price | 2,400 gp (1.00 times bullion value) |

The engine price equals minted value: a mint would not pay more than the coins an ingot strikes, and a seller would not take less. Set on 2026-10-04 (C1).

Aurora's bar and ingot prices are not used for this metal: they value it well below the coins it would strike, so a buyer could mint the bars at a profit. They are kept below for reference only.

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 | chunk | 1 oz | 15 gp | 240 gp |
| Priests' Alcove (spell components) | 36 | coin | 1 | 5 gp |  |
| Priests' Alcove (spell components) | 36 | die | 1/2 in | 35 gp |  |
| Priests' Alcove (spell components) | 36 | mirror | 3 in sq | 40 gp |  |
| Priests' Alcove (spell components) | 36 | tissue | 1 in sq | 10 gp |  |
| Priests' Alcove (spell components) | 36 | wire | 1 ft | 8 gp |  |
| Laborers' List (metals) | 60 | bar | 1/4 lb | 10 gp | 40 gp |
| Laborers' List (metals) | 60 | ingot | 2 lb | 50 gp | 25 gp |
| Laborers' List (metals) | 60 | sheet | 2 in sq | 15 gp |  |
| Laborers' List (metals) | 60 | strip | 2 by 1 in | 10 gp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 5 gp |  |

Catalogue bars and ingots run 25 gp to 40 gp per lb, against a bullion value of 240 gp per lb (10% to 17% of minted value).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
