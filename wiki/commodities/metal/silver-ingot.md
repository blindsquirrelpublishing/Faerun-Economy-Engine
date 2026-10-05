# Silver

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `silver_ingot`  
**Category:** metal  
**Trade unit:** ingot (10 lb)  
**Base price:** 48 gp per ingot (about 4.8 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Silver is a metal good in Faerûn, traded in ingot lots for daily use, craft, and commerce. A mineral or refined metal traded for tools, industry, and coinage.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_silver` |
| Demand index | 0.2 |
| Luxury (wealth elasticity) | 0.6 |
| Perishable | 0 |
| Demand traits | `temple` 1.8, `noble` 1.6, `mercantile` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Used as an input for: [Arcane focus](../arcane/arcane-focus.md) (0.02 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `mine_silver` 3 (of 325 stored settlements).

**Specialty at:** Deadsnows (2), Llorkh (1), [Phandalin](../../../locations/phandalin.md) (1).

## Coin Standard

Minting assumption (see [method](../README.md#coin-standard)): a pound of metal strikes 50 coins in principle; 4% is assumed lost to casting scrap, blank trimming and assay, leaving **48 silver pieces per lb**.

| Measure | Value |
| --- | --- |
| Ingot weight | 10 lb |
| Coins in principle | 500 sp |
| Coins minted (net of 4% loss) | 480 sp |
| Bullion value of one ingot | 48 gp |
| Bullion value per lb | 4.8 gp |
| Engine base price | 48 gp (1.00 times bullion value) |

The engine price equals minted value: a mint would not pay more than the coins an ingot strikes, and a seller would not take less. Set on 2026-10-04 (C1).

Aurora's bar and ingot prices for this metal sit close to the bullion value, which supports the assumption. They are kept below for reference.

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 36 | chunk | 1 oz | 3 sp | 4.8 gp |
| Priests' Alcove (spell components) | 36 | die | 1/2 in | 6 sp |  |
| Priests' Alcove (spell components) | 36 | mirror | 2 in sq | 3 gp |  |
| Priests' Alcove (spell components) | 36 | wire | 1 ft | 4 sp |  |
| Wizards' Laboratory (components cache) | 48 | pin | 5 | 5 sp |  |
| Wizards' Laboratory (components cache) | 48 | powder | 1 oz | 1 sp | 1.6 gp |
| Wizards' Laboratory (components cache) | 48 | wire | 1 ft | 4 sp |  |
| Laborers' List (metals) | 60 | bar | 1/2 lb | 3 gp | 6 gp |
| Laborers' List (metals) | 60 | ingot | 2 lb | 11 gp | 5.5 gp |
| Laborers' List (metals) | 60 | sheet | 5 in sq | 9 gp |  |
| Laborers' List (metals) | 60 | strip | 6 by 1 in | 3 gp |  |
| Laborers' List (metals) | 60 | wire | 1 ft | 2 gp |  |

Catalogue bars and ingots run 5.5 gp to 6 gp per lb, against a bullion value of 4.8 gp per lb (115% to 125% of minted value).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
