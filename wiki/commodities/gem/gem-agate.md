# Agate and quartz

[Commodity index](../README.md) · [Gems](README.md)

**Status:** In the engine  
**Engine ID:** `gem_agate`  
**Category:** gem  
**Trade unit:** stone (0.1 lb)  
**Base price:** 10 gp per stone (about 100 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Agate and quartz is a gem good in Faerûn, traded in stone lots for daily use, craft, and commerce. A prized mineral or gemstone traded for ornament, wealth, and arcane study.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_gem` |
| Demand index | 0.15 |
| Luxury (wealth elasticity) | 0.7 |
| Perishable | 0 |
| Demand traits | `mercantile` 1.5, `arcane` 1.4 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Recipe Links

Used as an input for: [Arcane focus](../arcane/arcane-focus.md) (0.1 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `mine_gem` 9 (of 325 stored settlements).

**Specialty at:** Blingdenstone (3), Esmeltaran (2), Mirabar (2), Secomber (2), Termalaine (1).

**Configured shortage at:** Goldenfields.

## Aurora's Whole Realms Catalogue

### Catalogue entry: Quartz

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Priests' Alcove (spell components) | 37 | clear chunk | 1 ct | 1 sp |  |
| Priests' Alcove (spell components) | 37 | other chunk | 1 ct | 5 cp |  |
| Priests' Alcove (spell components) | 37 | powder | 1 oz | 3 cp | 0.48 gp |
| Wizards' Laboratory (components cache) | 49 | clear rough | 1 ct | 1 sp |  |
| Wizards' Laboratory (components cache) | 49 | other rough | 1 ct | 5 cp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

### Catalogue entry: Agate

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 48 |  | 1 ct | 1 gp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
