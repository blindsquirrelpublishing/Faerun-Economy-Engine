# Salted fish

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `fish_salt`  
**Category:** food  
**Trade unit:** barrel (100 lb)  
**Base price:** 4 gp per barrel (about 0.04 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Salted fish is a food good in Faerûn, traded in barrel lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `fish`, `salt` |
| Demand index | 1.6 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.1 |
| Demand traits | `port` 1.3, `temple` 1.2 |
| Storage | 180 days capacity, 0.15% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one barrel: [Fresh fish](../food/fish-fresh.md) 1.7, [Salt](../food/salt.md) 0.2.

## Where the Engine Places It

Settlements carrying each producer tag: `fish` 36, `salt` 2 (of 325 stored settlements).

**Specialty at:** Caer Calidyrr (2), Harrowdale Town (1), Luskan (2), Mintarn (1), Mulmaster (1), Murann (2), Port Llast (1), Ruathym (2), Teziir (1), Velen (1).

## Aurora's Whole Realms Catalogue

### Catalogue entry: Preserved cod

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 118 | salted | lb | 5 gp | 5 gp |
| Aurora's Larder | 118 | smoked | lb | 7 gp | 7 gp |

Engine price per lb is **0.00667 times** the median catalogue price per lb for this entry (engine 0.04 gp/lb; catalogue median 6 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

### Catalogue entry: Preserved herring

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 118 | pickled | lb | 3 gp | 3 gp |
| Aurora's Larder | 118 | salted | lb | 5 gp | 5 gp |

Engine price per lb is **0.01 times** the median catalogue price per lb for this entry (engine 0.04 gp/lb; catalogue median 4 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
