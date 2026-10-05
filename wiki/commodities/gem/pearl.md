# Pearls

[Commodity index](../README.md) · [Gems](README.md)

**Status:** In the engine  
**Engine ID:** `pearl`  
**Category:** gem  
**Trade unit:** pearl (0.1 lb)  
**Base price:** 100 gp per pearl (about 1,000 gp per lb)  
**Production type:** raw  
**Aurora's Whole Realms Catalogue:** no matching entry in the sections reviewed

## Engine Description

> Pearls is a gem good in Faerûn, traded in pearl lots for daily use, craft, and commerce. A prized mineral or gemstone traded for ornament, wealth, and arcane study.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `pearl` |
| Demand index | 0.05 |
| Luxury (wealth elasticity) | 0.95 |
| Perishable | 0 |
| Demand traits | `noble` 2.5, `port` 1.4, `arcane` 1.5 |
| Storage | 365 days capacity, 0.01% stock loss a day, 15 reserve days |

## Where the Engine Places It

Settlements carrying each producer tag: `pearl` 1 (of 325 stored settlements).

**Specialty at:** Velen (1).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
