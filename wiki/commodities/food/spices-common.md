# Common spices

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `spices_common`  
**Category:** food  
**Trade unit:** pound (1 lb)  
**Base price:** 2 gp per pound (about 2 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Common spices is a food good in Faerûn, traded in pound lots for daily use, craft, and commerce. A staple trade good prized for daily sustenance and household use.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `spice`, `farm` |
| Demand index | 0.5 |
| Luxury (wealth elasticity) | 0.4 |
| Perishable | 0 |
| Demand traits | `cosmopolitan` 1.5, `noble` 1.8 |
| Storage | 365 days capacity, 0.08% stock loss a day, 45 reserve days |
| Harvest or production calendar | Ches 2%, Tarsakh 7%, Mirtul 16%, Kythorn 25%, Flamerule 25%, Eleasis 16%, Eleint 8%, Marpenoth 2% |
| Regional calendar (cold) | Kythorn 10%, Flamerule 30%, Eleasis 40%, Eleint 20% |
| Regional calendar (arid) | Hammer 4%, Alturiak 7%, Ches 22%, Tarsakh 22%, Mirtul 7%, Kythorn 1%, Flamerule 1%, Eleasis 1%, Eleint 7%, Marpenoth 15%, Uktar 7%, Nightal 4% |
| Regional calendar (tropical) | Hammer 6%, Alturiak 6%, Ches 12%, Tarsakh 12%, Mirtul 6%, Kythorn 6%, Flamerule 6%, Eleasis 6%, Eleint 12%, Marpenoth 12%, Uktar 6%, Nightal 6% |

## Recipe Links

Used as an input for: [Incense](../luxury/incense.md) (0.5 per unit).

## Where the Engine Places It

Settlements carrying each producer tag: `spice` 4, `farm` 50 (of 325 stored settlements).

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Common spices:

[Angelica](../food/angelica.md), [Bergamot](../food/bergamot.md), [Borage](../food/borage.md), [Calendula](../food/calendula.md), [Caraway](../food/caraway.md), [Chervil](../food/chervil.md), [Chives](../food/chives.md), [Clary](../food/clary.md), [Costmary](../food/costmary.md), [Dillweed](../food/dillweed.md), [Faggot of sweet herbs](../food/faggot-of-sweet-herbs.md), [Horehound](../food/horehound.md), [Horseradish](../food/horseradish.md), [Hyssop](../food/hyssop.md), [Laurel](../food/laurel.md), [Lemon balm](../food/lemon-balm.md), [Liquorice root](../food/liquorice-root.md), [Lovage](../food/lovage.md), [Marigold](../food/marigold.md), [Marjoram](../food/marjoram.md), [Mint](../food/mint.md), [Oregano](../food/oregano.md), [Parsley](../food/parsley.md), [Poppy seed](../food/poppy-seed.md), [Rose hips](../food/rose-hips.md), [Rosemary](../food/rosemary.md), [Sage](../food/sage.md), [Savory](../food/savory.md), [Sweet cicely](../food/sweet-cicely.md), [Tarragon](../food/tarragon.md), [Thyme](../food/thyme.md), [Woodruff](../food/woodruff.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
