# Kelp ale

[Commodity index](../README.md) · [Drink](README.md)

**Status:** In the engine  
**Engine ID:** `kelp_ale`  
**Category:** drink  
**Trade unit:** keg (80 lb)  
**Base price:** 3.5 gp per keg (about 0.044 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Brewed with shore-kelp by the Ffolk; the brew turns flat within a season if kept off the islands.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `tag_kelp_ale` |
| Demand index | 1 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.2 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** One engine keg is 80 lb, read as about **9.6 gallons** of contents at 8.34 lb a gallon, with the keg returned and refilled (the same assumption as [Ale](ale.md)).

| Line | Input | Quantity per keg | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Grain, malted | 0.8 bushel (48 lb raw, about 38 lb after malting) | [`grain`](../food/grain.md) (wheat) | 0.48 gp | About 4 lb of malt a gallon |
| 2 | Water | about 15 gallons | none | 0.00 gp | Ale volume plus grain absorption and boil-off |
| 3 | Fuel (firewood) | 0.06 load (about 30 lb) | [`timber`](../material/timber.md) | 0.18 gp | Kilning plus mash and boil |
| 4 | Yeast (barm) | from the previous batch | none | 0.00 gp | Repitched |
| 5 | Shore kelp | about 2 lb, gathered | none | 0.01 gp | Gathering time only |

| Line | Conversion cost | Basis | Cost per keg |
| --- | --- | --- | --- |
| 6 | Labour | Brewers at 0.65 gp a day and a labourer at 0.325 gp, about 0.030 gp a gallon | 0.29 gp |
| 7 | Equipment and cask wear | Brewhouse and keg float written off over their lives | 0.03 gp |

**Rolled-up cost: about 0.99 gp per keg** (materials 0.67 gp, conversion 0.32 gp). Against the 3.5 gp base price that leaves about 2.5 gp (72%).

An ordinary-strength ale with kelp in place of bittering herbs. The engine description says it goes flat within a season off the islands, yet stores it 365 days. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

The [Ale](ale.md) routes, with kelp at op 70.

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
| 70 | Boil the wort with shore kelp | 1 to 2 hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md) |
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

- **No engine recipe to check**: `tag_kelp_ale` produces a flat 6,972.86 kegs a day at Caer Calidyrr against demand of 50 (C10).
- Storage: 365 days in the engine against "flat within a season" in its own description. A storage of about 90 days would match (C10).
<!-- formulation:end -->

## Where the Engine Places It

Settlements carrying each producer tag: `tag_kelp_ale` 1 (of 325 stored settlements).

**Dedicated `tag_kelp_ale` industry at:** Caer Calidyrr (2).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
