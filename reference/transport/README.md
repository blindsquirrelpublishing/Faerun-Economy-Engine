# Direct-Leg Transportation Reference

## Airline-Style Transport Options

`transport-options.csv` lists distinct itinerary alternatives for the 13-location
reference: fastest overall, lowest freight cost, fastest land-only (road, trail,
track), and fastest water-only (sea, river, barge, ferry). Identical itineraries
are merged, retaining all selection labels. This is a curated set, not every
possible route or every carrier. Land-only excludes tunnels and portage.
Fastest and lowest-freight searches allow all engine modes, including magical
transport and inferred connections. Each row identifies its connections, full
path, ordered leg modes, duration, distance, and gp per 100 lb. These are freight
itineraries, not passenger fares or carrier-specific bookings.

There are no scheduled departures, arrival clock times, frequencies, layover
allowances, or guaranteed service availability in the model. Option IDs are
reference IDs, not flight numbers. Travel durations sum modeled leg times.
Generate with `python -m tools.export_transport_reference --schedule`.

## Separate Fastest-Route Matrices

`fastest-time-days-matrix.csv`, `fastest-distance-miles-matrix.csv`, and
`fastest-cost-gp-per-100lb-matrix.csv` have the same 13 locations across the top
and down the left: Waterdeep and its direct neighbors. `fastest-routes.csv`
records each cell's complete path, leg modes, connections, and inferred status.
Generate these separately with `python -m tools.export_transport_reference --fastest`.
This does not overwrite the direct-leg exports.

These matrices minimize the sum of `Edge.days` across the entire engine network,
including intermediate locations outside the 13 displayed locations. Every pair
is optimized, even where a direct edge exists. All modes and inferred links are
eligible. Distance and risk-adjusted freight cost describe that SAME fastest
path, not independently shortest or cheapest paths. Equal-time ties use the
engine's Dijkstra traversal order. Unlike `World.route(optimise="days")`, no
risk penalty is added to the time objective. Carrier schedules, waiting times
between edges, service availability, and passenger costs are not modeled.
Costs use the event-free baseline described below. Diagonal cells are zero;
unreachable pairs remain blank rather than receiving invented connections.

Generated from the primary Faerun Economy Engine on 2026-09-11.

## Tables

- `direct-legs.csv`: sparse origin/destination matrix in filterable row form.
  Each row is exactly one directed engine edge, including parallel connections.
  Missing pairs have no direct edge; no shortest paths or compound legs are calculated.
  Reverse edges are retained so either origin can be filtered independently.
- `direct-leg-carriers.csv`: carrier options attached to each direct leg, joined
  by `leg_id`. No multileg carrier service is aggregated.

## Basis

This is a static, event-free `World()` snapshot, not the active browser scenario.
Distances are engine graph distances in miles, not newly surveyed measurements.
`inferred=True` identifies modeled connections rather than mapped routes.
`mixed_mode=True` means the engine defines one direct edge with multiple modes;
it does not mean a route through intermediate settlements was calculated.
Filter it to False for strictly single-mode connections.

Travel days are `Edge.days`: distance divided by quality-adjusted mode speed.
They are elapsed model days, not assumed eight-hour travel shifts. Mixed-mode
edge estimates include the engine's transfer penalties.

Direct-leg freight is `Edge.freight_units(World.edge_risk(edge)) * FREIGHT_RATE`
times the load in pounds. Columns use 100 lb and a 2,000 lb short ton. The base
rate is 0.00006 gp per effective pound-mile. Baseline settlement-security risk
is included; commodity value, spoilage, merchant markup, tariffs, and transient
events are not. These are freight estimates, not passenger ticket prices.

Carrier figures come from `Edge.carrier_options()`: full-load base cost, load
capacity, effective speed, duration, and gp per short-ton-mile. Those carrier
prices exclude the direct-leg risk premium and preserve the engine's rounding.
For mixed-mode edges, carrier rows are component-mode estimates applied to the
edge distance, NOT guaranteed end-to-end alternatives. Filter
`mixed_edge_component=False` for independently interpretable carrier estimates.

The model formulas are owned by `faerun/world.py` (`Edge`, `MODES`, `CARRIERS`,
`FREIGHT_RATE`, and `World.edge_risk`). CSV values are calculated snapshots;
regenerate after changes to coordinates, network geometry, modes or prices:

```powershell
python -m tools.export_transport_reference
```

Run this from the primary engine root. No changes to the other workspace engines
are required. IDs identify rows within a snapshot and can change on regeneration.