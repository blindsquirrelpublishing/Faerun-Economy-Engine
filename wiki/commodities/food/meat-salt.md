# Salt meat

[Commodity index](../README.md) · [Food](README.md)

**Status:** In the engine  
**Engine ID:** `meat_salt`  
**Category:** food  
**Trade unit:** barrel (100 lb)  
**Base price:** 6 gp per barrel (about 0.06 gp per lb)  
**Production type:** processed or manufactured  
**Aurora's Whole Realms Catalogue:** listed (see below)

## Engine Description

> Voyage rations: the lifeblood of fleets, caravans and armies.

This is a model input stored in the catalogue, not a sourced lore claim.

## Engine Inputs

| Field | Value |
| --- | --- |
| Produced by (industry tags) | `cattle`, `herd`, `salt` |
| Demand index | 1.5 |
| Luxury (wealth elasticity) | 0 |
| Perishable | 0.1 |
| Demand traits | `port` 1.5, `military` 1.8, `cold` 1.4 |
| Storage | 180 days capacity, 0.15% stock loss a day, 30 reserve days |

## Recipe Links

Inputs for one barrel: [Fresh meat](../food/meat-fresh.md) 2.5, [Salt](../food/salt.md) 0.2.

## Where the Engine Places It

Settlements carrying each producer tag: `cattle` 7, `herd` 11, `salt` 2 (of 325 stored settlements).

**Specialty at:** [Triboar](../../../locations/triboar.md) (1).

**Configured shortage at:** Evereska.

## Aurora's Whole Realms Catalogue

### Catalogue entry: Preserved beef

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 118 | corned | lb | 3 gp | 3 gp |
| Aurora's Larder | 118 | dried | lb | 5 gp | 5 gp |
| Aurora's Larder | 118 | jerked | lb | 7 gp | 7 gp |
| Aurora's Larder | 118 | sausage | lb | 2 gp | 2 gp |
| Aurora's Larder | 118 | smoked | lb | 4 gp | 4 gp |

Engine price per lb is **0.015 times** the median catalogue price per lb for this entry (engine 0.06 gp/lb; catalogue median 4 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

### Catalogue entry: Preserved pork

| Catalogue section | Printed page | Variant | Unit | Catalogue price | Price per lb |
| --- | --- | --- | --- | --- | --- |
| Aurora's Larder | 118 | bacon | lb | 4 gp | 4 gp |
| Aurora's Larder | 118 | ham | lb | 5 gp | 5 gp |
| Aurora's Larder | 118 | salted | lb | 3 gp | 3 gp |
| Aurora's Larder | 118 | sausage | lb | 1 gp | 1 gp |

Engine price per lb is **0.0171 times** the median catalogue price per lb for this entry (engine 0.06 gp/lb; catalogue median 3.5 gp/lb). The catalogue is far above the engine here, which is normal for its retail luxury pricing.

## Related Catalogue Goods (Proposed)

Aurora's entries with no engine equivalent whose closest engine commodity is Salt meat:

[Damarite salmon](../food/damarite-salmon.md), [Maztican buffalo](../food/maztican-buffalo.md), [Sardines](../food/sardines.md), [Tadjani](../food/tadjani.md), [Tantran finefish](../food/tantran-finefish.md).

## Sources

- Engine record: [`faerun/data/store/commodities.json`](../../../faerun/data/store/commodities.json), with storage and recipe values as applied at load time by [`faerun/data/commodities.py`](../../../faerun/data/commodities.py). Read 2026-10-04.
- Settlement placements: [`faerun/data/store/settlements.json`](../../../faerun/data/store/settlements.json), read 2026-10-04.
- *Aurora's Whole Realms Catalogue* (TSR 9358, 1992, AD&D 2nd edition), J. Robert King and Co., design concept Anne Brown. Primary source, consulted directly from the project copy in [`.guides/`](../../../.guides/tsr09358%20-%20Aurora's_Whole_Realms_Catalogue.pdf) on 2026-10-04. Page numbers are the printed folios. Prices are the catalogue's retail mail-order prices; descriptions here are paraphrased.
