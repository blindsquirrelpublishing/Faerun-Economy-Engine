# Duergar grey ale

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `duergar_grey_ale`  
**Category:** drink  
**Trade unit:** keg (80 lb)  
**Base price:** 5.5 gp per keg (about 0.069 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Gracklstugh's forge-ale, brewed with mineral water found only in that cavern.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_duergar_grey_ale` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.25 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine keg is 80 lb, read as about **9.6 gallons** of contents at 8.34 lb a gallon, with the keg returned and refilled (the same assumption as [Ale](ale.md)).

| Line | Input | Quantity per keg | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Grain, malted | 1 bushel (60 lb raw, about 47 lb after malting) | [`grain`](../food/grain.md) (wheat) | 0.60 gp | About 4.9 lb of malt a gallon |
| 2 | Water | about 15 gallons | none | 0.00 gp | Ale volume plus grain absorption and boil-off |
| 3 | Fuel (coal) | 0.25 sack (about 15 lb) | [`coal`](../metal/coal.md) | 0.12 gp | Half the weight of firewood for the same heat; no timber in the Underdark |
| 4 | Yeast (barm) | from the previous batch | none | 0.00 gp | Repitched |
| 5 | Mineral water | Gracklstugh cavern spring | none | 0.00 gp | The engine description: found only in that cavern |

| Line | Conversion cost | Basis | Cost per keg |
| --- | --- | --- | --- |
| 6 | Labour | Brewers at 0.65 gp a day and a labourer at 0.325 gp, about 0.030 gp a gallon | 0.29 gp |
| 7 | Equipment and cask wear | Brewhouse and keg float written off over their lives | 0.03 gp |

**Rolled-up cost: about 1.04 gp per keg** (materials 0.72 gp, conversion 0.32 gp). Against the 5.5 gp base price that leaves about 4.5 gp (81%).

Assumed a strong ale (6.25 lb of grain a gallon). The engine configures Gracklstugh **short of grain**, so the grain would be imported from the surface at far more than 0.6 gp a bushel; whether duergar brew from grain at all, or from fungus, is unresolved. Coal stands in for firewood in a cavern city known for its forges. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

The [Ale](ale.md) routes, with cavern spring water at op 50 and coal as fuel.

**Route A: Malting**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Steep | 2 days | Maltster | [Steeping cistern](../../equipment/brewing/steeping-cistern.md) |
| 20 | Germinate on the floor | 4 to 5 days | Maltster | Malting floor, [Brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) |
| 30 | Kiln-dry | 1 day | Maltster | [Malt kiln](../../equipment/brewing/malt-kiln.md), fuel |
| 40 | Crush | hours | Miller or brewer | [Malt mill](../../equipment/brewing/malt-mill.md) |

**Route B: Brewing**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 50 | Heat water; mash | 2 to 3 hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md), [Mash tun](../../equipment/brewing/mash-tun.md) |
| 60 | Run off and sparge | 1 hour | Brewer | [Mash tun](../../equipment/brewing/mash-tun.md) |
| 70 | Boil the wort (no herbs recorded) | 1 to 2 hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md) |
| 80 | Cool | 3 to 6 hours | Labourer | [Coolship](../../equipment/brewing/coolship.md) |
| 90 | Pitch barm and ferment | 3 to 5 days | Brewer | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 100 | Rack into kegs and bung | hours | Labourer | [Keg](../../equipment/brewing/keg.md) |
| 110 | Condition in the cellar | about 7 days | none | Cellar, [Keg](../../equipment/brewing/keg.md) |

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Steeping cistern](../../equipment/brewing/steeping-cistern.md) | 3.5 gp | 10 |
| [Malt kiln](../../equipment/brewing/malt-kiln.md) | with the building | 30 |
| [Malt mill](../../equipment/brewing/malt-mill.md) | 6 gp, or toll milling | 40 |
| [Brewing copper](../../equipment/brewing/brewing-copper.md) | 60 gp | 50, 70 |
| [Mash tun](../../equipment/brewing/mash-tun.md) | 9.4 gp | 50, 60 |
| [Coolship](../../equipment/brewing/coolship.md) | 4 gp | 80 |
| [Fermenting vat](../../equipment/brewing/fermenting-vat.md) | 8 gp | 90 |
| [Keg](../../equipment/brewing/keg.md) | 1 gp | 100, 110 |
| [Brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) | 2 gp | 20, 50, 60, 100 |

## Cost Roll-up Cross-check

- **No engine recipe to check**: `tag_duergar_grey_ale` produces a flat 6,972.86 kegs a day at Gracklstugh against demand of 28 (C10).
- At base prices the formulation costs about a fifth of the price. Imported grain is the unknown; at the Waterdeep grain asking price (7.07 gp a bushel) the grain alone would be 7.07 gp a keg, above 5.5 gp.
<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `tag_duergar_grey_ale` 1 (of 325 stored settlements).

**Dedicated `tag_duergar_grey_ale` industry at:** Gracklstugh (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
