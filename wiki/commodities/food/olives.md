# Olives

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `olives`  
**Category:** food  
**Trade unit:** barrel (60 lb)  
**Base price:** 2.5 gp per barrel (about 0.042 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Olives is a food good in Faerûn, traded in barrel lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `orchard` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.3 |
| Demand traits | `desert` 1.4 |
| Storage | 180 days capacity, 0.15% stock loss a day, 30 reserve days |
| Harvest or production calendar | Hammer 5%, Marpenoth 20%, Uktar 50%, Nightal 25% |
| Regional calendar (cold) | Marpenoth 10%, Uktar 60%, Nightal 30% |
| Regional calendar (arid) | Eleint 10%, Marpenoth 40%, Uktar 40%, Nightal 10% |
| Regional calendar (tropical) | Hammer 8%, Alturiak 8%, Ches 17%, Tarsakh 8%, Mirtul 4%, Kythorn 4%, Flamerule 8%, Eleasis 8%, Eleint 17%, Marpenoth 8%, Uktar 4%, Nightal 4% |

## Recipe Links

Used as an input for: [Olive oil](../food/olive-oil.md) (0.7 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `orchard` 4 (of 325 stored settlements).

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 116 | Chessentan | lb. | 3 gp | 3 gp |
| Aurora's Larder | 116 | Shaarite green | lb. | 10 gp | 10 gp |

Engine price per lb is **0.00641 times** the median catalogue price per lb for this entry (engine 0.042 gp/lb; catalogue median 6.5 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
