# Keg

[Equipment index](../README.md) · [Brewing](README.md)

**Status:** Proposed; not in the engine  
**Group:** Brewing  
**Kind:** Container, returnable  
**Used in:** [Ale](../../commodities/drink/ale.md) route B, ops 100 and 110; [Mead](../../commodities/drink/mead.md), op 50; [Reghed frost mead](../../commodities/drink/reghed-frost-mead.md), op 50; also trade; [Duergar grey ale](../../commodities/drink/duergar-grey-ale.md), ops 100 and 110; [Kelp ale](../../commodities/drink/kelp-ale.md), ops 100 and 110; [Bitter black](../../commodities/drink/bitter-black.md), ops 100 and 110; [Dragon's Breath beer](../../commodities/drink/dragons-breath-beer.md), ops 100 and 110; [Elminster's Choice](../../commodities/drink/elminsters-choice.md), ops 100 and 110; [Golden Sands lager](../../commodities/drink/golden-sands-lager.md), ops 100 and 110; [Iriaeboran North Brew](../../commodities/drink/iriaeboran-north-brew.md), ops 100 and 110; [Luiren's Best](../../commodities/drink/luirens-best.md), ops 100 and 110; [Old One Eye](../../commodities/drink/old-one-eye.md), ops 100 and 110; [Shadowdark ale](../../commodities/drink/shadowdark-ale.md), ops 100 and 110; [Suzale (Purple Dragon ale)](../../commodities/drink/suzale-purple-dragon-ale.md), ops 100 and 110; [Tanagyr's stout](../../commodities/drink/tanagyrs-stout.md), ops 100 and 110

## What It Is

The cask the engine's ale is traded in: about 9.6 gallons of ale, roughly 13 lb empty. Kegs go out full and come back empty, so a brewery owns about a month of output in circulation. That float costs more than the rest of the brewhouse put together. The engine's [Barrel (empty)](../../commodities/product/barrel.md) is a larger cask from the same trade.

## Build Estimate

Model assumption at engine base prices and baseline wages; not canon and not an engine value.

| Input | Quantity | Engine source | Cost |
| --- | --- | --- | --- |
| Sawn planks | 0.04 load (12 lb) | [`planks`](../../commodities/material/planks.md) | 0.20 gp |
| Iron hoops | 0.15 ingot | [`iron_ingot`](../../commodities/metal/iron-ingot.md) | 0.15 gp |
| Cooper | 0.66 day | `carpenters` wage 0.975 gp | 0.64 gp |

**Estimated cost:** about 1 gp. For comparison the engine barrel is 2 gp, of which its recipe materials are 1.10 gp.

## Capacity and Life

- **Capacity:** One engine keg of ale
- **Service life:** 5 years, or about 20 to 40 fills

## Sources

- Build quantities, capacities and lives are model assumptions from general pre-industrial brewing practice, not a Realms source. Prices use engine base prices and baseline wages (`list_wages`), read 2026-10-04.
- Engine catalogue: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), read 2026-10-04.
