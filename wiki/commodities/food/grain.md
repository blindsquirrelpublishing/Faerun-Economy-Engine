# Grain (wheat)

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `grain`  
**Category:** food  
**Trade unit:** bushel (60 lb)  
**Base price:** 0.6 gp per bushel (about 0.01 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> The bread of the Heartlands; the price of everything else follows it.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `farm` |
| Demand index | 3 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.15 |
| Legacy season multipliers | `autumn` 0.8, `winter` 1.15, `spring` 1.25 |
| Storage | 400 days capacity, 0.03% stock loss a day, 75 reserve days |
| Harvest or production calendar | Flamerule 5%, Eleasis 30%, Eleint 50%, Marpenoth 15% |
| Regional calendar (cold) | Eleint 30%, Marpenoth 70% |
| Regional calendar (arid) | Ches 10%, Tarsakh 40%, Mirtul 40%, Kythorn 10% |
| Regional calendar (tropical) | Alturiak 10%, Ches 30%, Tarsakh 10%, Eleasis 10%, Eleint 30%, Marpenoth 10% |

## Recipe Links

Used as an input for: [Ale](../drink/ale.md) (0.8 per unit), [Dwarven spirits](../luxury/dwarven-spirits.md) (0.08 per unit), [Milled flour](../food/flour.md) (0.9 per unit), [Warhorse](../livestock/warhorse.md) (20 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `farm` 50 (of 325 stored settlements).

**Specialty at:** Archenbridge (2), Ashabenford (2), Beregost (1), Daggerford (1), Goldenfields (3), Hlath (2), Iriaebor (1), Myratma (2), Ordulin (1), Ormpetarr (2), Riatavin (2), Shadowdale (1), Skuld (2).

**Configured shortage at:** Athkatla, Baldur's Gate, Blingdenstone, Boareskyr Bridge, Bryn Shander, Calimport, Candlekeep, Citadel Adbar, Citadel Felbarr, Easthaven, Good Mead, Gracklstugh, Lonelywood, Luskan, Mantol-Derith, Memnon, Menzoberranzan, Messemprar, Mirabar, Mithral Hall, Myth Drannor, Nimbral, Orlumbor, Parnast, Port Nyanzaru, Ruathym, Selgaunt, Silverymoon, Sshamath, Sundabar, Targos, Termalaine, [Waterdeep](../../../locations/waterdeep.md), Westgate.

## Aurora's Whole Realms Catalogue

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 115 |  | lb | 2 gp | 2 gp |

Engine price per lb is **0.005 times** the median catalogue price per lb for this entry (engine 0.01 gp/lb; catalogue median 2 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Grain (wheat):

[Barley](../food/barley.md), [Buckwheat](../food/buckwheat.md), [Chick peas](../food/chick-peas.md), [Lentils](../food/lentils.md), [Millet](../food/millet.md), [Oats](../food/oats.md), [Rye](../food/rye.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
