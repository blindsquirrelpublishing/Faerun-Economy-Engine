# Hlondeth to Arrabar Sea Lane

[Location index](../README.md)

**Endpoints:** Hlondeth (`hlondeth`) and Arrabar (`arrabar`), both in engine zone `vilhon`  
**Mode:** Sea lane (`sea`), single mode, no transfers  
**Route ID:** `custom:343d910f-2412-49c1-9f67-f9c5f90eab67`  
**Evidence reviewed:** 2026-10-03  
**Review scope:** Engine route record and mode settings; limited Forgotten Realms Wiki check on the endpoints and the Reach

## Overview

This is the only modeled connection between Hlondeth and Arrabar. Both the
fastest-route (`days`) and cheapest-route (`cost`) queries return this single
leg. It was originally entered as a portage and was changed to a sea lane on
2026-10-03 (see [Change History](#change-history)).

## Engine Record

| Field | Value |
| --- | --- |
| Name (`via`) | Hlondeth to Arrabar Sea Lane |
| Mode | `sea` (label "sea lane"), `multimodal: false` |
| Stops | Arrabar, Hlondeth |
| Distance | 68.3 miles |
| Path | Straight line of 8 evenly spaced points, map (2029.6, 1943.9) to (2077.5, 1992.6) |
| Route quality | 1.0 (the neighbouring named roads are 0.85) |

The path endpoints match the stored settlement coordinates for Hlondeth and
Arrabar. A straight line is acceptable for a crossing of open water; it was
not acceptable for the original portage.

## Mode Settings

From `list_travel_modes` on 2026-10-03. These are engine inputs, not canon.

| Mode | Freight factor | Miles per day | Hazard factor |
| --- | --- | --- | --- |
| sea (current) | 0.3 | 72 | 0.9 |
| portage (original) | 2.2 | 10 | 1.6 |
| road (reference) | 1.0 | 24 | 1.0 |
| ferry (rejected) | 0.7 | 30 | 0.8 |
| barge (rejected) | 0.45 | 28 | 0.6 |
| river (rejected) | 0.55 | 40 | 0.7 |

## Observed Output

Observed 2026-10-03 through the MCP `get_trade_route` tool. Results can change
with inputs, events, calendar, and software revisions.

| Metric | Value |
| --- | --- |
| Transit time | 0.9 days |
| Freight | 0.14 gp per 100 lb (about 2.8 gp per ton) |
| Hazard | 0.16 |
| `caravan_days` | 2.8 |

Transit time is consistent with 68.3 miles at 72 miles per day. Hazard moved from
0.29 to 0.16, which matches the ratio of the sea and portage hazard factors
(0.9 / 1.6). Freight fell from 1.16 to 0.14 gp; the exact freight formula was not
reviewed here.

## Mode Choice

**Sea lane over portage.** A portage is a carry between two waterways. The
straight path between these two harbor cities crosses the Reach, so a 68-mile
overland carry was not a plausible model.

**Sea lane over ferry, barge, or river.** The Forgotten Realms Wiki describes the
Vilhon Reach as part of the Sea of Fallen Stars and as a trade hub linking the
inner sea with the Lake of Steam and the Shining Sea. [Source][reach] That is
seagoing traffic, not a river crossing or towed inland barge work. The engine's
`ferry` mode (30 miles a day) reads as a short crossing, not a 68-mile run.

**Inland but still sea.** The Reach is inland in the sense that the whole Sea of
Fallen Stars is inland. Whether its water is salt or sheltered was not
established by the reviewed article; treat that as unverified.

**No portage fallback.** If the old portage were kept as an alternative, events
that worsen the sea lane would divert freight onto an implausible path. A future
fallback should be a road around the shore built from real segments. The engine
currently has no road path between the two cities.

## Sourced Lore

- **Vilhon Reach:** part of the Sea of Fallen Stars; its port cities made it a
  trade center between the southern waters and the inner sea. [Source][reach],
  citing *Forgotten Realms Campaign Setting* 3rd edition (2001), p. 215.
- **Hazards:** coastal areas of the Reach are subject to koalinth and merrow
  attacks. [Source][reach], citing *Sea of Fallen Stars* (1999), p. 11. The reviewed
  article does not mention piracy; an earlier suggestion to raise this lane's
  hazard for piracy is unsupported.
- **Hlondeth:** southwest of Turmish at the end of the Reach; an independent
  city-state ruled by House Extaminos, having broken from Chondath in 614 DR.
  Dediana Extaminos is named as matriarch in 1373 DR. [Source][hlondeth], citing
  *Serpent Kingdoms* (2004), pp. 94 to 95. Which shore it sits on was not stated.
- **Arrabar:** capital of Chondath; residents engaged in trade, crafting, fishing,
  and mercenary work; terminus of the Golden Road and the Emerald Way. Lord Eles
  Wianar ruled around 1372 DR. [Source][arrabar] The fetched page did not expose
  its reference list, so underlying citations were not recorded.

## Carriers

Created 2026-10-03 with the MCP `create_business` tool, then given carrier fields by
hand-editing [businesses.json](../../faerun/data/store/businesses.json) and running
`reload_catalog`. These are **invented engine records, not canon**; the reviewed
Forgotten Realms Wiki articles name no shipping company on the Reach. Each
description says so.

| ID | Name | HQ | Service ID | Bound vessel | Equipment | Capacity |
| --- | --- | --- | --- | --- | --- | --- |
| `greenscale_reach_packets` | Greenscale Reach Packets | Hlondeth | `hlondeth-arrabar-packet` | Merchant caravel | 2 packet caravels, 2 ship's boats | 120,000 lb / 3,000 ft3 |
| `arrabar_watermens_lighterage` | Arrabar Watermen's Lighterage | Arrabar | `arrabar-watermens-lighterage` | Coasting cog | 2 coasting cogs, 6 cargo lighters | 160,000 lb / 4,000 ft3 |
| `red_cask_hulls` | Red Cask Hulls | Arrabar | `red-cask-wine-run` | None (own cargo only) | 1 coasting cog, 1 ship's boat | 60,000 lb / 1,500 ft3 |

**Common fields.** All three are `location_mode: rolling` with `carrier_modes:
["sea"]` and a single itinerary entry on this lane. Itinerary progress is an authored
map snapshot: Greenscale 0.25 out of Hlondeth, the Lighterage 0.6 out of Arrabar,
Red Cask 0.45 out of Arrabar.

**Roles.** Greenscale runs scheduled packets for mixed consignments, passengers and
post (16 staff; crew of 2 captains and 14 sailors). The Lighterage is framed as
chartered under Arrabar's Fishers' and Watermen's Guild, an engine guild whose
domains include `ship`, and handles harbor lighterage and bulk cargo (23 staff;
12 lightermen). Red Cask is a merchant-carrier moving Arrabar's common wine (an
engine specialty) to a dockside cellar in Hlondeth; it stocks `wine_common` at
standard quality (9 staff).

**Route binding.** Shippers see carriers through `Edge.carrier_options()` in
[world.py](../../faerun/world.py), which looks up the route name in
`MULTILEG_CARRIER_SERVICES`. That table allowed one service per route, so it was
changed on 2026-10-03 to accept a list as well as a single entry. The sea lane now
lists two services: Greenscale replaces the generic Merchant caravel option and the
Lighterage replaces the generic Coasting cog. The Deep-water galleon remains a
generic option. Red Cask is deliberately not listed, because it carries only its
own goods; it still appears as a rolling carrier on the map.

**Capacity basis.** Shipment quotes use the bound vessel's modeled load (100,000 lb
for a cog, 180,000 lb for a caravel), not the business `capacity_lb`, which is
reported as metadata. The existing Sword Coast carriers follow the same pattern.

## Discrepancies and Open Questions

- **1492 DR applicability.** The Arrabar article states the city was destroyed
  during the Spellplague. The Vilhon Reach article states the Reach splintered
  into small lakes after the Spellplague and returned to its former terrain after
  the 1480s DR. Arrabar's condition in 1492 DR, and whether its harbor was
  operating, are unresolved. Underlying citations for both statements were not
  recorded.
- **Hlondeth engine record.** The engine places Hlondeth in region Chondath with
  1,680 residents (small town), no industries, and a description saying its
  profile is inferred from Arrabar. The reviewed lore describes an independent
  city-state since 614 DR. Population was not established by the reviewed
  article. Preserved for review, not changed.
- **Hlondeth port field.** Hlondeth carries the `port` trait but its `port`
  field is null, while Arrabar's is "Sea of Fallen Stars". Check whether any
  engine logic reads the field rather than the trait.
- **`caravan_days`.** Reports 2.8 under both the portage and sea modes, which
  matches road pace (68.3 / 24). It appears to ignore leg mode. Likely an engine
  issue rather than a route issue; check what consumes the field.
- **Lane hazard.** Uses the default sea factor. Any adjustment for sheltered
  water or coastal monsters needs sourcing first.
- **Hlondeth trade balance.** On 2026-10-03 (2 Marpenoth 1492 DR) the engine
  reported goods imports of about 78,350 gp per day against about 41 gp of
  exports for a town of 1,680, plus about 13,370 gp per day of unassigned inbound
  freight. Arrabar reported about 361,640 gp per day unassigned. Likely a side
  effect of Hlondeth's profile being inferred from Arrabar; preserved for review.
- **Carrier capacity.** Engine "Carriers and warehouses" counts (4 establishments
  and 25 workers in Hlondeth; 158 and 1,260 in Arrabar) are population-based
  estimates of local handling and storage. The engine states they are not route
  capacity.
- **Route storage.** The project file that stores this custom route was not
  inspected in this review. The carrier binding depends on the route name; renaming
  the lane breaks it until `MULTILEG_CARRIER_SERVICES` is updated to match.

## Change History

| Date | Change | Observed result |
| --- | --- | --- |
| Before 2026-10-03 | Created as "Hlondeth to Arrabar Portage", mode `portage` | 6.8 days, 1.16 gp per 100 lb, hazard 0.29 |
| 2026-10-03 | Mode changed to `sea` | 0.9 days, 0.14 gp per 100 lb, hazard 0.16 |
| 2026-10-03 | Renamed "Hlondeth to Arrabar Sea Lane" | No change to metrics |
| 2026-10-03 | Three invented carrier businesses created | Carrier fields empty; no change to route metrics checked |
| 2026-10-03 | Carrier fields filled; two services bound to the lane in `world.py` | Isolated check of `carrier_options()` lists Greenscale and the Lighterage; MCP server restart pending |

## Sources

**Engine (observed 2026-10-03):** MCP `get_trade_route`, `get_settlement`, `get_location_detail`, `create_business`, `update_business`, `reload_catalog`; [world.py](../../faerun/world.py)
(Hlondeth, Arrabar), `list_travel_modes`, and `list_named_routes`; the
[stored settlements](../../faerun/data/store/settlements.json).

**Directly consulted, secondary:** Forgotten Realms Wiki articles
[Vilhon Reach][reach], [Hlondeth][hlondeth], and [Arrabar][arrabar], accessed
2026-10-03. The underlying publications were not consulted directly.

[reach]: https://forgottenrealms.fandom.com/wiki/Vilhon_Reach
[hlondeth]: https://forgottenrealms.fandom.com/wiki/Hlondeth
[arrabar]: https://forgottenrealms.fandom.com/wiki/Arrabar
