# Coal

[Commodity index](../README.md) · [Metals](README.md)

**Status:** In the engine  
**Engine ID:** `coal`  
**Category:** metal  
**Trade unit:** sack (60 lb)  
**Base price:** 0.5 gp per sack (about 0.0083 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Coal is a metal good in Faerûn, traded in sack lots for daily use, craft, and commerce. A mined or refined metal valued for armor, tools, and industry.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `mine_coal` |
| Demand index | 1.4 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0 |
| Demand traits | `dwarven` 1.6, `cold` 1.5 |
| Legacy season multipliers | `winter` 1.5, `autumn` 1.15 |
| Storage | 400 days capacity, 0.01% stock loss a day, 45 reserve days |
| Demand calendar | Hammer 12%, Alturiak 11%, Ches 9%, Tarsakh 8%, Mirtul 7%, Kythorn 6%, Flamerule 5%, Eleasis 6%, Eleint 7%, Marpenoth 9%, Uktar 10%, Nightal 11% |

## Recipe Links

Used as an input for: [Glassware](../product/glassware.md) (0.05 per unit), [Steel billet](../metal/steel-ingot.md) (0.04 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `mine_coal` 5 (of 325 stored settlements).

**Specialty at:** Gracklstugh (3), Mulmaster (3).

**Configured shortage at:** Calimport, Evereska, Myth Drannor, Nimbral, Port Nyanzaru.

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Wizards' Laboratory (components cache) | 48 | chunk | 1 lb | 1 gp | 1 gp |
| Wizards' Laboratory (components cache) | 48 | dust | 1 lb | 8 sp | 0.8 gp |
| Wizards' Laboratory (components cache) | 48 | crystal |  | no price printed |  |
| Wizards' Laboratory (components cache) | 48 | bead/marble | 10 | 7 gp |  |
| Wizards' Laboratory (components cache) | 48 | rod | 1 ft | 15 gp |  |
| Wizards' Laboratory (components cache) | 48 | square | 1 in | 3 gp |  |
| Wizards' Laboratory (components cache) | 48 | sphere | 6 in | 20 gp |  |

Component rows are priced for small laboratory or altar quantities, so they are not compared with the engine's bulk price.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
