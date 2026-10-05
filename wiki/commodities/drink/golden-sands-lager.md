# Golden Sands lager

[Commodity index](../README.md) · [Drink](README.md)

**Status:** Proposed; not in the engine  
**Suggested engine category:** drink  
**Closest engine commodity:** [Ale](../drink/ale.md)  
**Catalogue group:** Ales and beers  
**Source:** *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition)

## Catalogue Description

Light, fizzy southern lager in several flavoured versions (basic, Gold with cactus and nettle, Orange with orange and currant). Imported only through Baldur's Gate and Waterdeep.

**Origin given:** Calimport, Calimshan (via Baldur's Gate and Waterdeep).

## Catalogue Prices

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb | Scaled estimate |
| --- | --- | --- | --- | --- | --- | --- |
| Wines and Ales | 127 |  | hand keg (2 gal) | 2 sp | 0.012 gp | 0.747 gp |
| Wines and Ales | 127 |  | cask (12 gal) | 1 gp | 0.01 gp | 3.74 gp |
| Wines and Ales | 127 |  | barrel (30 gal) | 25 sp | 0.01 gp | 9.34 gp |
| Wines and Ales | 127 |  | butt (100 gal) | 8 gp | 0.0096 gp | 29.88 gp |
| Wines and Ales | 127 |  | tun (250 gal) | 16 gp | 0.0077 gp | 59.76 gp |

**Scaled estimate** multiplies the catalogue price by 3.74, the median engine-to-catalogue price ratio for ales, beers and ciders (see [method](../README.md#price-scaling)). It is an illustrative starting point for review, not an engine value and not canon.

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** Costed per **catalogue cask (12 gallons)** so it lines up with the catalogue price table above; the cask is returned.

| Line | Input | Quantity per cask | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Grain, malted | 0.88 bushel (53 lb raw, about 42 lb after malting) | [`grain`](../food/grain.md) (wheat) | 0.53 gp | About 3.5 lb of malt a gallon |
| 2 | Water | about 19 gallons | none | 0.00 gp | Ale volume plus grain absorption and boil-off |
| 3 | Fuel (firewood) | 0.074 load (about 37 lb) | [`timber`](../material/timber.md) | 0.22 gp | Kilning plus mash and boil |
| 4 | Bittering herbs or hops | about 0.6 lb | none (C6) | 0.02 gp | Placeholder price; no engine commodity |
| 5 | Yeast (barm) | from the previous batch | none | 0.00 gp | Repitched |
| 6 | Flavouring (Orange version) | 0.25 crate citrus and some currants | [`citrus`](../food/citrus.md) | 0.35 gp | Gold version uses cactus and nettle, which have no commodity |

| Line | Conversion cost | Basis | Cost per cask |
| --- | --- | --- | --- |
| 7 | Labour | Brewers at 0.65 gp a day and a labourer at 0.325 gp, about 0.030 gp a gallon plus cellar handling while it lagers | 0.42 gp |
| 8 | Equipment and cask wear | Brewhouse and keg float written off over their lives, plus aging tuns tied up for the lagering months | 0.08 gp |

**Rolled-up cost: about 1.63 gp per cask** (materials 1.13 gp, conversion 0.50 gp). The catalogue cask is 1 gp; the scaled estimate is 3.74 gp.

A light lager: 4.4 lb of grain a gallon, fermented and stored cold. The flavoured versions are costed for the Orange one. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

The [Ale](ale.md) routes with a cold ferment and months of lagering. Lager needs a cold cellar; how Calimport keeps one is a lore follow-up.

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
| 70 | Boil the wort with herbs or hops | 1 to 2 hours | Brewer | [Brewing copper](../../equipment/brewing/brewing-copper.md) |
| 80 | Cool | 3 to 6 hours | Labourer | [Coolship](../../equipment/brewing/coolship.md) |
| 90 | Pitch and ferment cold | 7 to 14 days | Brewer | [Fermenting vat](../../equipment/brewing/fermenting-vat.md) |
| 100 | Rack into kegs and bung | hours | Labourer | [Keg](../../equipment/brewing/keg.md) |
| 110 | Lager in the cold cellar | 1 to 3 months | none | Cold cellar, [Aging tun](../../equipment/vinting/aging-tun.md) |

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
| [Aging tun](../../equipment/vinting/aging-tun.md) | 8 gp | 110 |

## Cost Roll-up Cross-check

| Measure | Per 12-gallon cask |
| --- | --- |
| Rolled-up cost at engine base prices | 1.63 gp |
| *Aurora's* catalogue price (retail, mail order) | 1 gp |
| Scaled estimate (catalogue times the group factor) | 3.74 gp |

- **The roll-up is 44% of the scaled estimate**, so the estimate covers the cost of making it at engine prices.
- The unscaled catalogue price (1 gp) is below the roll-up: *Aurora's* sells this beer for less than the engine's grain, fuel and wages can make it.
<!-- formulation:end -->

## Before It Enters the Engine

- Decide whether it is a separate commodity or a variant of the closest engine good.
- Choose a trade unit, weight and base price; the scaled estimate above is only a starting point.
- Assign producer tags and any regional sources supported by evidence beyond this catalogue.
- Record the decision in [the location inventory](../../inventory.md#proposed-new-commodities) when one is made.

## Sources

- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
