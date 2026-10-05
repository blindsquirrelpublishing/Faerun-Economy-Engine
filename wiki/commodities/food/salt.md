# Salt

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `salt`  
**Category:** food  
**Trade unit:** sack (50 lb)  
**Base price:** 2.5 gp per sack (about 0.05 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Preserves the harvest; whoever holds the salt pans holds the winter.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `salt` |
| Demand index | 1.4 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Storage | 730 days capacity, 0.005% stock loss a day, 45 reserve days |

## Recipe Links

Used as an input for: [Bread](../food/bread.md) (0.001 per unit), [Salted fish](../food/fish-salt.md) (0.2 per unit), [Salt meat](../food/meat-salt.md) (0.2 per unit), [Smokepowder](../exotic/smokepowder.md) (0.1 per unit), [Soap](../product/soap.md) (0.03 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `salt` 2 (of 325 stored settlements).

**Specialty at:** Innarlith (2).

**Configured shortage at:** Silverymoon.

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 37 | block | 1 lb | 1 sp | 0.1 gp |
| Priests' Alcove (spell components) | 37 | granular | 5 lb | 5 sp | 0.1 gp |
| Wizards' Laboratory (components cache) | 49 | block | 1 lb | 1 sp | 0.1 gp |
| Wizards' Laboratory (components cache) | 49 | granular | 5 lb | 5 sp | 0.1 gp |
| Aurora's Larder | 115 |  | oz | 1 cp | 0.16 gp |

Engine price per lb is **0.312 times** the median catalogue price per lb for this entry (engine 0.05 gp/lb; catalogue median 0.16 gp/lb). The two are within a factor of five.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
