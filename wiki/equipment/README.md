# Equipment Wiki

[Wiki index](../README.md)

Things used to make goods or to do work: brewhouse vessels now, and later the gear people carry and ride with.
An equipment page records what the item is, what it is built from at engine prices, its capacity and service life,
and which production routes need it. Nothing here is in the engine; equipment enters the simulation only through a
separate, validated data change.

Where the same item is also traded (a sword, a saddle, a coil of rope), the equipment page links to its
[commodity page](../commodities/README.md) for prices and market data rather than repeating them. The commodity
page answers "what does it sell for and where"; the equipment page answers "what does it take, and what is it
used for".

## Groups

| Group | Items | Status |
| --- | --- | --- |
| [Brewing](brewing/README.md) | 9 | Proposed 2026-10-04 for the [ale](../commodities/drink/ale.md) routes; used by every beer, the meads, wine and fire-wine |
| [Vinting and cider](vinting/README.md) | 4 | Proposed 2026-10-04 for mead, wines, ciders, lagering and brandy aging |
| [Distilling and bottling](distilling/README.md) | 2 | Proposed 2026-10-04 for [brandy](../commodities/drink/brandy.md) |
| [Glassmaking](glassmaking/README.md) | 4 | Proposed 2026-10-04 for [glassware](../commodities/product/glassware.md) |
| Arms | | Planned. Traded weapons already have commodity pages, for example [Sword](../commodities/arms/sword.md); see [Arms and armour](../commodities/arms/README.md) |
| Tack and harness | | Planned. Commodity pages exist for [Saddle and tack](../commodities/product/saddle.md), [Harness](../commodities/product/harness.md), [Saddle bags](../commodities/product/saddle-bags.md) and [Yoke](../commodities/product/yoke.md) |
| Rope and rigging | | Planned. Commodity page exists for [Hemp rope](../commodities/product/rope.md) |

## Page Conventions

- **Status, group, kind** (fixed vessel, machine, container, tool set, structure) and **used in**, linking each
  route and operation number.
- **Build estimate:** inputs at engine base prices and baseline wages (`list_wages`), shown line by line so the
  arithmetic can be checked. A model assumption, not canon.
- **Capacity and service life**, which a production page uses to work out how many it needs and what wear costs
  per unit of output.
- **Sources.** Say plainly when quantities come from general historical practice rather than a Realms source.

Structures (a malt kiln, a forge) get a page when a route depends on them, but are priced with the building.
