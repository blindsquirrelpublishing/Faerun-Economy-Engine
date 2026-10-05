# Knee-cracker cider

[Commodity index](../README.md) · [Drink](README.md)

**Status:** Proposed; not in the engine  
**Suggested engine category:** drink  
**Closest engine commodity:** [Ale](../drink/ale.md)  
**Catalogue group:** Ciders  
**Source:** *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition)

## Catalogue Description

Cloudy, sediment-heavy windfall-apple cider sold in bulk; stronger than ale, weaker than wine.

**Origin given:** Local presses (unspecified).

## Catalogue Prices

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb | Scaled estimate |
| --- | --- | --- | --- | --- | --- | --- |
| Wines and Ales | 129 |  | hand keg (2 gal) | 1 sp | 0.006 gp | 0.221 gp |
| Wines and Ales | 129 |  | cask (12 gal) | 4 sp | 0.004 gp | 0.886 gp |
| Wines and Ales | 129 |  | barrel (30 gal) | 1 gp | 0.004 gp | 2.21 gp |
| Wines and Ales | 129 |  | butt (100 gal) | 35 sp | 0.0042 gp | 7.75 gp |
| Wines and Ales | 129 |  | tun (250 gal) | 8 gp | 0.0039 gp | 17.71 gp |

**Scaled estimate** multiplies the catalogue price by 2.21, the median engine-to-catalogue price ratio for wines, meads and ciders (see [method](../README.md#price-scaling)). It is an illustrative starting point for review, not an engine value and not canon.

<!-- formulation:start -->
## Formulation (Proposed)

Proposed 2026-10-04. Documentation only; nothing here changes the engine.

**Batch basis.** Costed per **catalogue cask (12 gallons)** so it lines up with the catalogue price table above; the cask is returned.

| Line | Input | Quantity per cask | Engine commodity | Cost at base price | Basis |
| --- | --- | --- | --- | --- | --- |
| 1 | Apples (windfalls) | 6.4 crate (192 lb) | [`apples`](../food/apples.md) | 6.40 gp | About 16 lb of fruit a gallon of juice |
| 2 | Yeast | wild, on the fruit | none | 0.00 gp | Not bought |

| Line | Conversion cost | Basis | Cost per cask |
| --- | --- | --- | --- |
| 3 | Labour | Two cellarmen at 0.65 gp and two labourers at 0.325 gp press about 10 casks a day | 0.20 gp |
| 4 | Equipment and cask wear | Mill, press and cask float | 0.05 gp |

**Rolled-up cost: about 6.65 gp per cask** (materials 6.40 gp, conversion 0.25 gp). The catalogue cask is 4 sp; the scaled estimate is 0.886 gp.

Windfall-apple cider, cloudy and unfiltered: about 16 lb of apples a gallon, costed at the engine apple price although windfalls would sell for less. Quantities, batch sizes, staffing and equipment lives are model assumptions from general pre-industrial practice, not a Realms source.

## Production Route (Proposed)

Sold cloudy, so no fining.

**Route: Cider**

| Op | Operation | Duration | Resource | Equipment |
| --- | --- | --- | --- | --- |
| 10 | Gather apples; leave in a heap to soften | 1 to 2 weeks | Farm labour |  |
| 20 | Mill | hours | Cellarman | [Fruit mill](../../equipment/vinting/fruit-mill.md) |
| 30 | Press | 1 day | Cellarman | [Fruit press](../../equipment/vinting/fruit-press.md) |
| 40 | Ferment | 2 to 4 weeks | none | [Aging tun](../../equipment/vinting/aging-tun.md) |
| 60 | Rack into casks | hours | Labourer | [Wine cask](../../equipment/vinting/wine-cask.md) |

## Required Equipment

From the [equipment wiki](../../equipment/README.md). None of it is in the engine.

| Equipment | Estimated cost | Ops |
| --- | --- | --- |
| [Fruit mill](../../equipment/vinting/fruit-mill.md) | 6 gp | 20 |
| [Fruit press](../../equipment/vinting/fruit-press.md) | 19 gp | 30 |
| [Aging tun](../../equipment/vinting/aging-tun.md) | 8 gp | 40 |
| [Wine cask](../../equipment/vinting/wine-cask.md) | 1.2 gp | 60 |
| [Brewer's hand tools](../../equipment/brewing/brewers-hand-tools.md) | 2 gp | 20, 60 |

## Cost Roll-up Cross-check

| Measure | Per 12-gallon cask |
| --- | --- |
| Rolled-up cost at engine base prices | 6.65 gp |
| *Aurora's* catalogue price (retail, mail order) | 4 sp |
| Scaled estimate (catalogue times the group factor) | 0.886 gp |

- **The roll-up is 7.5 times the scaled estimate.** Fruit is the whole story: the engine prices a 30 lb crate at 1 gp (0.033 gp a lb, three times grain by weight), and cider needs about 16 lb of fruit a gallon.
- The scaled estimate uses the wines, meads and ciders factor (2.21). Either cider is a far dearer drink in the engine's world than in the catalogue's, or cider fruit (windfalls, culls) needs a much cheaper commodity than table fruit (C11).
<!-- formulation:end -->

## Before It Enters the Engine

- Decide whether it is a separate commodity or a variant of the closest engine good.
- Choose a trade unit, weight and base price; the scaled estimate above is only a starting point.
- Assign producer tags and any regional sources supported by evidence beyond this catalogue.
- Record the decision in [the location inventory](../../inventory.md#proposed-new-commodities) when one is made.

## Sources

- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
