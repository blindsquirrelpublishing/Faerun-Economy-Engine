# Wine cask

[Equipment index](../README.md) · [Vinting and cider](README.md)

**Status:** Proposed; not in the engine  
**Group:** Vinting and cider  
**Kind:** Container, returnable  
**Used in:** [Table wine](../../commodities/drink/wine-common.md), op 60; [Brandy](../../commodities/drink/brandy.md) (incoming wine); [Knee-cracker cider](../../commodities/drink/knee-cracker-cider.md), op 60; [Purple Hill cider](../../commodities/drink/purple-hill-cider.md), op 60; [Vilhon cider](../../commodities/drink/vilhon-cider.md), op 60

## What It Is

The engine's `cask` trade unit: 100 lb full, which at 8.34 lb a gallon is 12 gallons, the same size as the catalogue's cask. Goes out full and comes back empty, like the [keg](../brewing/keg.md).

## Build Estimate

Model assumption at engine base prices and baseline wages; not canon and not an engine value.

| Input | Quantity | Engine source | Cost |
| --- | --- | --- | --- |
| Sawn planks | 0.05 load | [`planks`](../../commodities/material/planks.md) | 0.25 gp |
| Iron hoops | 0.2 ingot | [`iron_ingot`](../../commodities/metal/iron-ingot.md) | 0.20 gp |
| Cooper | 0.8 day | `carpenters` wage 0.975 gp | 0.78 gp |

**Estimated cost:** about 1.2 gp.

## Capacity and Life

- **Capacity:** 12 gallons
- **Service life:** 5 years, about 20 to 40 fills

## Sources

- Build quantities, capacities and lives are model assumptions from general pre-industrial practice, not a Realms source. Prices use engine base prices and baseline wages (`list_wages`), read 2026-10-04.
- Engine catalogue: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), read 2026-10-04.
