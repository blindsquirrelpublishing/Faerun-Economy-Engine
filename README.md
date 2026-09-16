# Faerûn Economy Engine

An economic model of the Forgotten Realms. It prices **130 commodities and
manufactured products** in **125 towns, cities, citadels, ports and Underdark
enclaves**, and adjusts every price for local industry, terrain, population,
wealth, culture, tariffs, trade-route distance, season and world events.

It ships with a command line browser and an **MCP server**, so an AI assistant
can be asked "what does a bar of mithral cost in Waterdeep, and where does it
come from?" and get a real answer with the supply chain attached.

The live world calendar is anchored at **1 Hammer 1492 DR = 1 January 2026
UTC**. Each new UTC day advances the Calendar of Harptos, changes the
deterministic daily market variation, and updates which dated events are
active. Explicit dates supplied through the CLI, web board, MCP tools, or
`World(date=...)` remain fixed for historical comparisons.

```
$ faerun price "Bryn Shander" grain

Grain (wheat) in Bryn Shander
=============================
buy from merchant 10.21 gp per bushel
sell to merchant  7.15 gp per bushel
base price   60.0 sp  ->  x17.02
availability scarce (about 41 bushels a tenday)
supply 0.08 vs demand 1.62  (scarcity 19.44)
imported from Goldenfields - 1,024 miles, 51 days
```

---

## Waterdeep population scenario

Waterdeep now uses **200,000 city-proper residents** as the user-selected
**1492 DR planning scenario**, with **130,000** retained as the comparison
baseline. This is not a verified census or a statistically derived estimate.
The [shared source](https://dungeonsdragons.fandom.com/wiki/Waterdeep_(city)#General)
gives approximately 130,000 in the city and over one million in its territory.
The [Forgotten Realms Wiki](https://forgottenrealms.fandom.com/wiki/Waterdeep)
suggests about 200,000 for the later city as an editorial interpretation.
Neither establishes a 1492 confidence interval; the previously suggested
180,000-220,000 interval is not used.

The chosen resident input drives household needs, housing, workforce estimates,
services and domestic travel through the existing formulas. At unchanged wealth
and diet, per-person household quantities increase by **53.85%** compared with
130,000. Prices and imports do not increase by that percentage automatically:
finite supply, recipe inputs, trade, staffing rounding and calibration still
determine the result. Five residents per home and a 50% worker pool remain
explicit assumptions, giving 40,000 home-equivalents and 100,000 modeled workers.

Territorial totals are contextual evidence, not additional city consumers;
adding them would double-count the city and potentially other markets.
External and peak-season visitors remain **unknown**, not zero. Visitor reports
separate `residents_at_home` and `modeled_present_population` (residents minus
outbound plus inbound visitors) from `resident_presence`, the existing
food-demand-equivalent measure. Day visits are full visitors but only 0.35
food-days. These are steady-state estimates, not enumerated people.

`GET /api/population?settlement=Waterdeep` and the MCP tool
`get_population_report` return the resident scenario, comparison, assumptions
and source provenance without running a price calculation. Market JSON,
settlement records and requirement profiles expose the same `population_model`.
The city atlas reads its count from the API rather than a hard-coded label.
The location dashboard displays population provenance and the comparison.
Changing the calendar date does **not** interpolate historical populations or
compound annual construction growth.

To run a Python comparison without mutating the shipped settlement:

```python
from dataclasses import replace
from faerun.world import World

baseline = World()
comparison = World(settlements=[
    replace(s, population=s.population_basis.comparison_residents)
    if s.id == "waterdeep" and s.population_basis else s
    for s in baseline.settlements.values()
], date=baseline.date)
```

Both scenarios retain the same settlement network and date.

### Building-based housing census

Open **Building-based census** in `waterdeep.html#housing-census`, or request
`GET /api/census?settlement=Waterdeep`. MCP clients can use `get_housing_census`.
The report and **Download census JSON** include source provenance, individual
roof polygons in original PDF-image pixels, sample locations, unresolved groups,
detector validation, and a ward-level housing calculation when inputs permit it.
Reading or downloading the report never changes the active resident population.

**This historical City System survey is incomplete, and no new population is established.**
The local City System PDF contains ten city sheets split across PDF pages 34-113.
Seven convenience-sampled patches across five sheets now have **156 visually
reviewed roof outlines** (121 more than the initial survey), with five unresolved
roof groups. They are not a representative city sample. Their **1.0504% share of
raw scanned tile pixels is not city-area coverage**: the scans contain overlaps,
sea, legends and example interiors. Review masks are unioned within each tile;
this does not establish citywide seam ownership or complete deduplication.

**26 outlines inside the identified City of the Dead enclosure** have
source-supported ward and Class A assignments. These rely on the enclosure
description (printed 3 / PDF 4), mapped landmarks (printed 12 / PDF 13 and
map PDF 91), and the Class A rule (printed 10 / PDF 11). Occupancy is unknown,
not assumed to be zero. The other **130 ward assignments remain unresolved**.

The scale audit identifies **1 inch = 100 feet** on map PDF 69, but no reliable
scan-pixel-to-foot calibration has been established. PDF 70's five-foot interior
grid must not be applied to city roof maps. All physical areas remain unknown;
**no surveyed record yet supports a resident estimate**, and no ward or citywide
building/population total is inferred. The report exposes overlapping input
readiness counts for verified wards, physical areas and unknown Class A occupancy.

The color-threshold trial found only 3-12 components against 16 reviewed roofs,
depending on threshold, with missed roofs, fragments and a large merged
component. Feature-based sheet registration also failed validation. Those
methods are recorded as rejected, not used to extrapolate a census.

The calculation module uses the guide's printed pages 10-11 for ward-specific
building classes, stories, uses and condition. Its low/central/high scenarios
explicitly assume household sizes 4/5/6, apartment sizes 650/500/350 square feet,
usable-floor fractions .65/.75/.85, occupied-unit fractions .85/.95/1, and
permanent rooming-house shares .25/.50/.75. These are sensitivity assumptions,
not measured occupancy or confidence intervals. Fractional dwelling equivalents
are expected capacities, not enumerated apartments.

Unknown scale, ward, institutional residence, unresolved overlapping footprints,
and incomplete city coverage prevent a citywide result. Even covered subtotals
are withheld if the selected subset is not deduplicated. The Southern Ward's
printed class table omits dice results 3-4; the model requires an explicit
building class there rather than silently repairing the source.
Class A structures require separate occupancy records; visitors are not added
to permanent residents. The source's 1357 DR building stock is not a verified
1492 inventory.

The compact survey is in `faerun/data/waterdeep_buildings.json`; the application
reads it using the standard library and does not require the PDF or image tools.
To check the existing survey:

```powershell
.\.venv\Scripts\python.exe tools\survey_waterdeep.py --check
```

Reproduction requires the local source PDF and the analysis-only dependencies
PyMuPDF, Pillow, NumPy and OpenCV. The recorded source SHA-256 prevents rebuilding
against a different scan accidentally. Rendered source images should stay in a
local artifact folder rather than being added to the application:

```powershell
.\.venv\Scripts\python.exe tools\survey_waterdeep.py --rebuild --render --registration-audit --artifacts ".artifacts\waterdeep-survey"
```

Completing the census requires a registered, deduplicated map survey with
confirmed ward boundaries and physical scale, followed by occupancy assumptions
and separate treatment of unique civic/temple/noble structures. The current
200,000 planning baseline is retained until that evidence exists.

### High-resolution street and roof map layers

The **Streets & building survey** panel at `waterdeep.html#city-survey` keeps
the newer single-image survey separate from the historical City System records.
The agreed boundary includes Field Ward, the City of the Dead, the city proper
and harbor islands, but excludes outlying farms. Neither source is silently
substituted for an enumerated 1492 resident register.

The atlas uses the complete `maps/waterdeep-map-hires.jpg` (3560 x 7256 pixels).
The Bing cache of this image was truncated; the original World Anvil download
decodes completely. Overlay geometry uses **original image pixels, top-left
origin, y increasing downward**, not longitude/latitude. Both axes are scaled
to the existing 768 x 1536 display, preserving the atlas's existing marker and
pan/zoom coordinate system. The distance tool's assumed scale is not evidence
of calibrated building areas.

Load the layers, toggle streets/roof records/boundary, search a street name or
stable segment ID, and select a line or roof to inspect its evidence. The main
atlas search also searches streets when no ward or landmark matches. Name
anchors represented by points are labeled **label only**, not drawn as invented
road routes. The coverage, validation and estimate metadata distinguish machine
candidates from reviewed records; feature counts alone do not establish a
complete street inventory, building count or resident population.

Read-only data endpoints:

- `GET /api/streets?settlement=Waterdeep`
- `GET /api/census/hires?settlement=Waterdeep`

Both support optional `search`, `offset` and positive `limit` parameters.
Pagination describes the selected records without redefining full-layer coverage.
The panel downloads the full loaded layer, including geometry and provenance.
MCP clients can use `get_city_map_survey(layer="streets")` or
`get_city_map_survey(layer="roofs")`; these return metadata by default.
Set `include_features=True` to retrieve geometry, paged using `offset` and
`limit` (100 by default). These operations do not change the active population.

**Current measured progress, not a completed census:** full-image processing
produced 4,835 unverified roof polygons. A seeded stratified sample of 40 out of
659 area cells, with 424 preferred roof-symbol tallies, estimates **7,567 depicted
roof structures**. Its approximate sampling-only 95% interval is **5,967-9,168**,
conditional on the single assistant review and the traced city boundary.
The separate **6,195-9,192 interpretation sensitivity** is neither a confidence
interval nor rigorous bounds. No resident population is inferred.

The street layer contains **7,417 candidate segments**, with 66 local label
associations representing **62 distinct names**. It is **not a complete verified
street network**: text creates splits/loops, and some candidates follow
courtyards, piers or terrain rather than streets. The 361 OCR observations
remain unverified. Neither total segment length nor segment count is a measured
road inventory.

AideDD supplies an external scale of **310 native pixels = 1,000 feet**.
Eight distributed image comparisons establish that its native coordinates
align with this raster. Provenance is in the street report's
`source.distance_scale`; this is an external map calibration, not an
author-certified scale bar or validation of the automatic building outlines.

Reproduce/check the high-resolution evidence using the existing analysis tools:

```powershell
.\.venv\Scripts\python.exe tools\survey_waterdeep_hires.py --check
.\.venv\Scripts\python.exe tools\survey_waterdeep_streets.py --check
```

### Generated building scenarios (not the map survey)

Open **Building scenarios** in `waterdeep.html#building-generator`. Choose a ward,
1-100 buildings, a repeatable seed, a B/C/D class override or the source dice,
an **assumed** footprint per building, and low/central/high occupancy assumptions.
Click **Generate buildings**; **Download scenario JSON** saves the complete
scenario, source references, rolls, assumptions, occupant counts and stable IDs.
The generated URL also retains the settings and recreates that scenario.

Class, stories, basement, possible tower/partial upper level, ward-adjusted
condition and use follow *City System* (TSR, 1988), printed pages **10-11**
(PDF pages **11-12**). Its setting year is **1357 DR**, not 1492.
Class A landmarks and City of the Dead structures require individual authoring.
Southern Ward's unassigned class rolls **3-4 remain unresolved**, with no
occupant result; an explicit class creates a deliberately overridden scenario.

Occupants are **counts only**. No names are invented, and historical people
are not assigned to random buildings: existing names remain attached to their
documented establishments in the historical directory. Residential capacity uses
the shared housing scenarios with explicit floor allocations, rounding and
rooming-house assumptions. Ordinary staff counts are additional modeling
assumptions, not workforce facts supplied by the guide. Staff may also be
residents and must not be added to residents as a population total.

The entered footprint is not a measurement. Cellars and unspecified tower area
add no housing; unavailable buildings have no ordinary occupants under this
scenario, without claiming that squatters or repair crews are absent.
Changing footprint or occupancy scenario preserves the same building dice and
IDs for a given seed/ward/class choice. Increasing batch size preserves its prefix.

Generated records have no map coordinates or historical-business IDs. They never
enter the roof survey, census, historical directory, live merchants, inventory
or active population. Batch totals cover resolved generated records only and are
not extrapolated to Waterdeep.

```powershell
faerun --json --seed 1357 generate-buildings --ward "Dock Ward" --count 20
faerun --seed 42 generate-buildings --ward "South Ward" --building-class C --scenario high
```

Python callers use `faerun.buildinggen.generate_buildings(...)`. HTTP:
`GET /api/generated-buildings?ward=Dock%20Ward&count=20&seed=1357`.
The MCP tool is `generate_city_buildings`. All three accept `building_class`,
`footprint_sqft` and `scenario`; the CLI uses hyphenated option names. CLI
generation, like the historical directory, does not open the live world or ledger.

### Location generation engine

Open `location-generator.html`, or follow **Generate location** from a location
dashboard. Enter any existing or invented place name, choose a profile, and
generate a **1-100 building scenario**. The name labels the scenario; it does not
create a live settlement, resolve an ambiguous catalogue name, or infer local lore.
The form offers seed, assumed footprint, occupancy scenario, and optional custom
class percentages and condition modifier. Download JSON to retain the complete
result; its `parameters` reproduce the scenario.

The following defaults are **engine assumptions**, not destination-specific facts
or tables printed in City System:

| Profile | Class B | Class C | Class D | Condition modifier |
| --- | ---: | ---: | ---: | ---: |
| Village | 0% | 20% | 80% | 0 |
| Town | 10% | 50% | 40% | 0 |
| City | 30% | 50% | 20% | 0 |
| Port | 10% | 50% | 40% | -1 |
| Fortress | 40% | 40% | 20% | +1 |

Custom B/C/D percentages must all be supplied, be integers from 0 to 100,
and total 100. Condition modifiers are -1, 0 or 1. The engine selects a class
using these percentages and reuses the existing source-backed structure, use,
condition and proprietor rules, plus the shared modeled occupancy calculations.
Urban use tables remain urban approximations when applied to villages or forts.
A fortress profile covers ordinary supporting buildings, **not the keep,
fortifications, soldiers or garrison**; unique Class A structures need authoring.

The same normalized name, profile, configuration and seed reproduce the building
dice. Increasing count retains the previous prefix. Changing footprint or
low/central/high occupancy leaves building identities, structure and uses fixed.
Different locations have distinct generated IDs. The original Waterdeep ward
generator retains its version-one results and unresolved Southern Ward rolls.

No occupant names, historical affiliations, street layouts or measured positions
are invented. These generated batches never change the map survey, historical
directory, live merchants, inventory or active population, and are not fitted or
extrapolated to the location's total population.

```powershell
faerun --json --seed 42 generate-location "Neverwinter" --profile port --count 30
faerun --seed 7 generate-location "New Hamlet" --profile village --count 12
faerun --json generate-location "Custom Keep" --profile fortress --class-b-weight 0 --class-c-weight 100 --class-d-weight 0 --condition-modifier 0
```

Python: `faerun.locationgen.generate_location(...)` and `location_profiles()`.
HTTP: `GET /api/generated-location?location=Neverwinter&profile=port&count=30&seed=42`
and `GET /api/location-profiles`. MCP: `generate_location` and
`get_location_generation_profiles`. The CLI uses the global `--seed` option
**before** the subcommand and does not open a live world or trade ledger.

The Waterdeep atlas's 2D/3D map now uses `maps/waterdeep-map-hires.jpg`
(3560 x 7256 pixels). The existing normalized map-plane coordinates are retained
so markers, measurements and orbit controls keep the same coordinate system.

## Daggerford town analysis

Open `daggerford.html` for the source-linked population, roof-group and street
analysis. It is also linked from Daggerford's market population-basis panel.
Use `GET /api/settlement-analysis?settlement=Daggerford` or the MCP tool
`get_settlement_analysis("Daggerford")` for the same read-only report.
The **900-resident model input is unchanged**, and is not validated by counting
map symbols or fitting occupancy assumptions to it.

The cartographer-linked Mike Schley preview has **140 manually indexed roof
groups**, including 59 with explicit grouping caveats and 7 additional unresolved
symbols. The analysis separately identifies **11 approximately traced named
streets**, 8 cisterns, 3 gates and 4 wall towers. Forty landmark keys are not
forty buildings. These observations do not establish an exact building census
or complete unnamed-lane network.

The working boundary includes the walled town, Ducal Castle and immediate
riverfront/quays. It excludes the surrounding duchy, outlying farms, the map's
area inset, caravan grounds and the tannery across the river. **North points
left** in the main source map. Roof markers are representative points, not
footprint polygons.

The printed scale's inner ticks and terminal label imply different conversions,
so street lengths are retained in pixels with separately labeled conditional
feet values. No definitive physical building area is supplied. Occupancy
sensitivity results cover only eligible non-institutional roof groups; castle,
garrison and other institutional residents remain unknown, not zero. The
illustrative components must not be presented as town population totals.

The packaged analysis JSON includes geometry and provenance, not a redistribution
license for the map. The optional author-linked preview remains a local analysis
input. Its hash is checked before the web report displays the associated map.
Without it, the report remains readable and explicitly marks the preview
unavailable. To reproduce the local diagnostics:

```powershell
.\.venv\Scripts\python.exe tools\survey_daggerford.py
# Optional: retrieve the same public preview and render local audit overlays.
.\.venv\Scripts\python.exe tools\survey_daggerford.py --download --annotate
```

## Route Planner

Open `planner.html` from the commodity board or the map's selected-route panel.
The planner compares fastest, lowest line-haul, land-only and water-only routes
for a shipment weight. Identical itineraries are merged. Inferred connections,
active-event risk, and air/teleport links are opt-in. Time optimization uses
elapsed `Edge.days`, without an extra risk weighting.

Default line-haul is an unvalidated shared-cargo estimate, not a carrier quote. Editable
allowances default to zero: each leg can have a minimum charge, each intermediate
connection a handling fee, each travel day an additional charge, plus one fixed
shipment charge. Contingency applies to their combined subtotal. Daily charges
use fractional modeled travel days, not rounded billable days. No intra-edge
handling fee is added separately for mixed-mode legs; their modeled freight
already includes the mode-profile adjustment. The handling input applies only
between graph edges. Lowest line-haul selects by freight, not allowance-adjusted
total; the alternatives are not an exhaustive cost optimization.

Each itinerary includes carrier capacities and shipments required per leg:
shipment weight divided by the existing carrier's capacity, rounded up to whole
loads. Carrier rows are separate scenarios, not quantities to add together.
Mixed-mode rows describe each component mode, not guaranteed through services.
Porter company capacity describes a whole company, not one person; individual
headcounts are not defined.

Expand each itinerary leg's carrier details to compare capacity, loads required,
cost per full load, shipment cost and days. Select a carrier for each component
mode, or retain shared freight. A selected carrier charges all required full
loads, including unused capacity. These model prices reuse the carrier catalog's
rounded full-load price and days, add the current leg risk premium, and retain
mixed-mode cost/time adjustments. Mixed legs allocate distance equally among
component modes, matching the existing mode profile; they do not assume a single
carrier can cover incompatible modes. Minimums still apply once per whole leg.
Loads are assumed concurrent; availability and sequential return trips are not
modeled. Choices update leg costs, duration, daily allowances, and landed totals.
The four route searches still use baseline shared freight, not carrier choices.
Selections are retained in the URL and JSON export via `carrier_choices`, a
mapping of returned leg IDs to mode/carrier-name mappings. They apply to the
same leg wherever it appears in the displayed alternatives, and reset when
endpoints or route-eligibility restrictions change.

Landed cost is cargo purchase price (gp/lb) times shipment weight plus the
transport total, including entered allowances and transport contingency.
The optional `purchase_per_lb` API parameter is user-supplied, not a market quote.
Missing purchase prices leave purchase value and landed costs pending (`null`);
an explicit zero is accepted. The comparison, breakdown and JSON export include
landed totals and the breakdown also shows landed cost per lb. Contingency does
not apply to cargo purchase value. Unbudgeted taxes and losses are excluded.

Cargo name is descriptive only: weight drives freight. Automatic commodity pricing, spoilage,
verified carrier operating costs, schedules and waiting times are
not calculated. Endpoint profiles inferred from another settlement are flagged.
Download estimate exports JSON containing the assumptions, paths and cost items.
The API is `GET /api/transport-plan` and does not mutate the simulation.

## Waterdeep historical city directory

Open `waterdeep.html` and choose **Browse historical businesses & people**.
The atlas now includes a curated directory of **46 establishments and 63 named
people across six wards**, drawn from the locally supplied
`volo/Volo's Guide to Waterdeep.pdf` (Ed Greenwood, TSR, 1992): establishments, their wards, services,
documented addresses where available, and named people with explicit business
affiliations and roles. Both record details and relationship details cite the
guide's printed page and the supplied PDF's **1-based page number**.

Search by name, service, or directly associated person/business; combine ward,
business-category and business/person filters. A person's ward means the ward
of an affiliated establishment, **not a verified home address**. Select a related
name to open its record. **Download results JSON** exports the current filtered
records with source metadata and limitations; clear filters first to export the
whole curated directory.

This is a **historical reference layer**, not an exhaustive census or a claim
that the guide's personnel and establishments are active in **1492 DR**. The
source's era caveat travels with API responses and exports. Service labels and
categories are editorial classifications; prices, inventories, revenue, staffing
totals and exact map coordinates are not invented. Existing illustrative atlas
markers are independent of these records.

The directory never creates live merchants, changes commodity supply, or adds
stock to the existing business offers. The PDF is not redistributed or required
at runtime: the application ships concise curated records, not extracted prose.

```powershell
faerun city-directory Waterdeep --ward "Dock Ward"
faerun --json city-directory Waterdeep --kind person
```

Read-only access is available through:

- Python: `faerun.city.city_directory("Waterdeep", search="inn", kind="business")`.
- HTTP: `GET /api/city-directory?settlement=Waterdeep&kind=person`.
- MCP: `get_city_directory(settlement="Waterdeep", search="", ward="", kind="all", category="")`.

`kind` accepts `all`, `business`, or `person`. Ward and category filters accept
names or underscore IDs; `South Ward` is an alias for the guide's `Southern Ward`.
The response includes full-catalogue totals and facets, filtered counts, business
records, people, bidirectional affiliations, source metadata and scope notes.
Unknown cities and invalid filters return explicit errors. The CLI directory
command does not initialize the live world or open a trade ledger.

## Travelling companies

Open **Travelling companies** from the commodity board or world map
(`mobile.html`). Mobile locations are dated household communities with people,
wagons, animals, carried inventory, daily food/water/fodder requirements,
services and an authored itinerary. The included **Silver Wheel Company**
travels from Daggerford through Waterdeep, Amphail, Red Larch and Triboar.

A company is deliberately not inserted into the permanent settlement trade
graph. While encamped it borrows the host settlement's market access; while
travelling it has only its carried stock. Its diamond map pin resolves from the
current Harptos date and moves along the active route leg without rebuilding or
distorting settlement prices. `GET /api/mobile-locations` lists companies and
`GET /api/mobile-location?id=silver_wheel` returns the full dated profile.
The current profile is descriptive and read-only: purchases, consumption,
losses and itinerary editing are not yet posted back into a persistent ledger.

Use **Generate economic report**, then **Download report JSON** on the company
page to save the full dated profile, economic assessment and assumptions.
`GET /api/mobile-economy?id=silver_wheel` returns the same report;
Python callers can use `mobile_economic_report("silver_wheel", world)`.
Generation is on demand, so ordinary profile and map requests do not calculate
market prices.

The report includes the shared wealth-sensitive household provisioning
benchmark, daily and tenday costs, starting food/water/fodder/fuel cover, tenday
resupply needs and a partial carried-stock replacement valuation. Encamped
companies use host-market consumer prices. In transit, catalogue base prices
are reference values only, with no implied trading access. Generic cargo,
unspecified grades and unknown unit conversions remain unvalued rather than
being treated as free. Of the included scenario's stock, only lamp-oil flasks
have an unambiguous catalogue match.

These are estimates, not actual operating accounts. Stores do not deplete over
time; wages, tolls, camp fees and other operating costs are not fully modeled.
Revenue, profit and gross local product (GLP) remain `null`, not zero, until
production, service deliveries and their inputs are modeled. The JSON includes
the GLP definition and missing inputs, and distinguishes the household
benchmark from the separate caravan ration-weight estimates.

## Buying, selling and uncommitted stock

Price views distinguish **Buy from merchant** (what the consumer pays) from
**Sell to merchant** (what the consumer receives). The engine's existing
market-dependent bid/ask spread supplies the merchant's resale markup; it is
not an additional multiplier applied a second time to the consumer price.

For goods bought at the quoted merchant bid:

```text
merchant markup % = 100 * (consumer buy price - consumer sell price) / consumer sell price
gross margin %    = 100 * (consumer buy price - consumer sell price) / consumer buy price
```

A merchant buying at 8 gp and reselling at 10 gp has a **25% markup** and
**20% gross margin**, before operating costs, taxes and losses. These are not
net-profit figures. A zero purchase bid has no defined markup percentage.
Named-business price modifiers apply to both sides, and quality and bulk
quotes expose their own resulting prices and markup.

The API retains `price` (consumer purchase / merchant ask) and `buy_price`
(merchant purchase / consumer sale), and adds `consumer_buy_price`,
`consumer_sell_price`, `merchant_spread`, `merchant_markup_pct` and
`merchant_margin_pct`. All prices are gp per catalogue trade unit.

**Total demand minus final demand is processing input demand, not surplus.**
The quantity available beyond the current model's requirements is:

```text
uncommitted supply/day =
    max(0, local production + allocated imports - allocated exports - total demand)
```

This protects final-use demand, planned workshop inputs and existing export
commitments. Unused ingredient reservations in closing stock are therefore
not automatically available for another buyer.

With `seasonal_inventory` enabled, local inventory carries forward across dates,
and uncommitted stock also protects the configured storage reserve. Inventory
quantities are modeled physical trade units, **not daily flow multiplied by ten**.
The quote's `inventory.stock_basis` and `uncommitted_basis` explain the applicable
stock and free-pool calculation; neither is a surveyed warehouse count or booking.

In the legacy model (`seasonal_inventory=False`), `uncommitted_stock` is that daily
amount times `stock_horizon_days`, **rounded down to whole trade units** and capped
by modeled retail stock. The horizon is normally ten days; fresh bread uses its
shorter configured freshness window. That is a steady-state stock-window estimate,
**not an immediate on-hand count or reservation**. With the trade ledger attached, public
`uncommitted_stock` instead shows the remaining dated planning quota after
PO claims; `forecast_uncommitted_stock` preserves the underlying estimate.
Buying on the ordinary spot market can still move prices; a confirmed PO
uses its separately locked contract price.
Bulk quotes above the uncommitted estimate carry a warning rather than silently
suggesting that all quoted units are spare.

Quality-offer estimates partition the free pool using the modeled grade
stock mix. Named merchants share that grade pool rather than each promising
the whole amount. Market-wide daily balances remain market-wide even when
a particular quality is quoted; `stock_scope` identifies market versus
grade-specific stock. Alternatives are not additive bookings.

The board, location tables, product/quality views, map price list and CLI
show the two directions and uncommitted quantities. Arbitrage estimates
use the consumer purchase price at origin and merchant purchase bid at
destination, and cap recommended cargo by uncommitted stock and shipment
weight rather than taking supplies reserved for local needs.

## Regional seasons and local storage

Seasonal inventory is **opt-in** for both the running app and library `World()`
instances. The default market and PO workflow uses the legacy baseline, avoiding
a historical stock replay on cold startup. Enable the physical seasonal model
with `.\run.ps1 -SeasonalInventory` or the global CLI flag:

```powershell
python -m faerun.cli --seasonal-inventory serve
```

The CLI also accepts `--no-seasonal-inventory` to explicitly disable it. Library
callers configure the same mode directly:

```python
from faerun.calendar import HarptosDate
from faerun.world import EconomyConfig, World

world = World(
    date=HarptosDate(1492, 9, 1),
    config=EconomyConfig(
        seasonal_inventory=True,
        inventory_epoch="1492-01-01",
        # Optional overrides: (settlement_id, commodity_id) -> trade units.
        initial_inventory={("waterdeep", "grain"): 12000},
        storage_capacity={("waterdeep", "grain"): 50000},
    ),
)
```

Products have separate twelve-month **production** and **demand** curves.
The local climate selects regional production overrides: a cold settlement
need not share a temperate or tropical harvest calendar. These are authored
fictional modeling assumptions, not canonical agronomy or surveyed farm yields.
The curves are normalized against the Harptos calendar to preserve annual
baseline quantities; a production multiplier describes potential, not guaranteed
input-backed output.

Local stored quantities carry forward through the daily balance, with finite
storage capacity, storage loss, overflow and protected reserve targets.
Both **ingredients and finished goods** are tracked. The daily physical
inventory ledger replays from `EconomyConfig.inventory_epoch`, default
**`1492-01-01`**. Initial stocks are seeded to reserve targets as an explicit
**prior-harvest assumption**, not a reconstructed historical harvest. Optional
`initial_inventory` and `storage_capacity` mappings override quantities for
individual `(settlement_id, commodity_id)` pairs in catalogue trade units.

Replay is deterministic. When opted in, the running app saves versioned checkpoints in
`%LOCALAPPDATA%\FaerunEconomyEngine\inventory-checkpoints.sqlite3`, separate from
the order ledger. The first full-world replay can take many minutes; later
queries and restarts reuse checkpoints. Changes to goods, geography, events or
economic settings select a different cache signature rather than reusing stale
stock. Library callers can set `EconomyConfig.inventory_cache_path` to a local
path, or leave it `None` for in-memory checkpoints only. This file is a disposable
cache: removing it reconstructs the same balances from the configured epoch.
Cache errors are surfaced rather than silently replacing stock.
The location page's no-event price comparison is a separate scenario and needs
its own first replay; it does not rewrite the active world's stocks.
Inspecting another date does not itself spend
stock or create an order, and **player purchases do not execute against physical
inventory**. This modeled economic carryover is distinct from the merchant
guild's durable order/planning ledger.

Dates **before the inventory epoch** retain historical steady-state quotes,
explicitly labelled `inventory.enabled=False` with a `reason`. They do not
fabricate a physical inventory ledger before its start. The app singleton
created by `_new_world` and bare `World()` both keep
`seasonal_inventory=False` for compatibility.

### Exact dated allocation windows

Seasonal callers can read an inclusive 1-31-day window without changing the
world date or creating any PO claims:

```python
from faerun.seasonal_economy import inventory_window

window = inventory_window(
    "Berdusk", "grain",
    HarptosDate(1492, 9, 1), HarptosDate(1492, 9, 10),
    world=world,  # seasonal_inventory=True
)
```

`snapshots` contains one row per day: actual `production`, `imports`, `exports`,
`exports_by_destination`, planned `final_demand`, `processing_demand` and `demand`,
actual `final_consumption` and `processing_consumption`, opening/closing/free
stocks, reserves, capacity and losses. `totals` sums the daily flows;
top-level `opening_stock` and `closing_stock` are the endpoints, **not sums**.
`exports_by_destination` sums the actual lane allocations across the window.
These quantities use the commodity's trade unit, not prices or pounds.

The reader omits backup supplier diagnostics and caches detached window results.
Dates before the inventory epoch, disabled inventory mode, reversed dates and
windows longer than 31 days fail explicitly. First reads may still need replay.
Do not extrapolate the end-day flow across the period or sum carryover stocks.
An export takeover replaces an existing modeled delivery; it is not additional
uncommitted stock. Order eligibility, destination limits and overlapping claims
remain the PO ledger's responsibility.

For a **flow-only** planning policy, a conservative daily allowance for new free
supply is `max(0, min(production + imports - demand - exports, uncommitted_stock))`.
The global ceiling for that flow plus export takeovers is its daily allowance
plus that day's existing exports, summed across the actual window. Capping by
free stock matters: positive incoming flow may be replenishing protected reserves.
Carried-stock entitlements need separate persistent claims; these flow totals do
not authorize selling an opening buffer again.

Grain can be harvested seasonally and retained for milling and baking while
ordinary bread demand remains year-round. Bread itself remains short-lived;
storing loaves is not a substitute for a granary. Potion demand and brewing can
also continue year-round, but actual output requires available recipe inputs,
including herbs carried through storage where configured. Neither a flat
demand curve nor a reserve target guarantees that all needs are met.

The product page and each location material's inspection show the **paired
12-month production/demand chart**, exact monthly values, current local
multipliers, opening/closing stock, capacity, reserve target, spoilage, overflow,
stock draw, days of cover and replay epoch. The stock figures are market-wide;
quality offers partition the pool rather than adding independent warehouses.
The commodity board and CLI also distinguish carryover stock from legacy
stock-window estimates.

Quote JSON and location requirement material rows expose `seasonality` and
`inventory` objects. `seasonality` contains `climate`, twelve `months` rows
(`month`, `name`, `production_multiplier`, `demand_multiplier`), the current
multipliers, `storage_days`, `storage_loss` and `reserve_days`. The catalogue
also exposes `production_profile`, `demand_profile` and
`regional_production_profiles`. Enabled inventory includes `opening_stock`,
`closing_stock`, `storage_capacity`, `reserve_target`, `spoilage`, `overflow`,
`stock_draw_per_day`, `days_of_cover`, `epoch`, `stock_basis` and
`inventory.uncommitted_stock`. This nested uncommitted quantity is the physical
model's free-stock pool, not the old ten-day flow estimate; it is distinct from
the public quote's dated PO planning quota. Days of cover is `null` when there is
no demand. Empty objects preserve legacy clients; an explicitly disabled object
can explain the pre-epoch fallback.
`GET /api/product?commodity=grain&settlement=Waterdeep` additionally resolves
the selected market's seasonality rather than a generic global calendar.
Monthly price-history rows include production, demand, stock and the same
inventory/profile objects, so availability can be plotted rather than prescribed.
Pre-trade import requirements use surviving opening stores as well as new output;
exportable supply protects the reserve target. Replenishing those reserves does
not count as newly uncommitted daily supply.

Storage losses are not shipment losses. Trade routes still allocate
**same-day steady-state deliveries**: shipment departure/arrival scheduling and manufacturing
labor ceilings are not modeled. Consumer buy/sell prices, quantity discounts
and merchant-guild contract pricing retain their existing meanings.

## Merchant guild wholesale and customer purchase orders

Open **Merchant guild & POs** from the board, map, product or location page
(`trade.html`). The desk separates four different prices:

- **Producer gate:** estimated local production cost, available only where
  the item is actually produced.
- **Merchant guild (wholesale):** supported supplier inventory cost plus a
  quantity-dependent guild markup. Imported inventory includes its upstream
  purchase/freight cost; merchant buyback is not used as a supplier price.
- **Consumer retail:** the destination's stated grade-specific selling price.
- **Merchant buyback:** the destination merchant's offer to buy from you.

Producer/guild orders require at least 25 gp at the quoted supplier floor.
Bottles additionally require at least 12 units, but **1,000 bottles is valid**:
the lot increment is one, not twelve. Guild tiers reduce only the configured
export margin: by 25% at five minimum lots, 50% at twenty, and 75% at one
hundred. Producer pricing does not invent volume discounts below its floor.
Reference guild rates in price JSON are indicative; the desk supplies the
actual quantity/terms quote. Cost-covering wholesale is not guaranteed to be
cheaper than every distorted local retail price.

### Quote, reserve, record and fulfil

1. Choose supplier, customer location, commodity/grade, quantity and a supply
   date in Harptos `YYYY-MM-DD` format. Choose either **uncommitted supply**
   or an **existing export allocation takeover** to the specified destination.
   A takeover requires authorization and standard grade because modeled
   exports do not carry a separate quality mix.
2. Choose producer or guild procurement, pickup or supplier delivery, and
   owned-caravan or shared-carrier transport. The owned-caravan estimate uses
   one 4,000-lb horse wagon on established roads; an optional empty return
   adds operating days, not another freight invoice. Budget extra loading,
   trading, insurance or other costs explicitly through the fixed allowance.
   Supplier delivery includes shared freight once in the supplier invoice.
3. Set a customer retail, wholesale or agreed unit price, tax-included or
   tax-extra terms, deposit percentage, payment timing and acceptance terms.
   The quote shows net/tax/gross amounts, procurement and transport costs,
   deposit due and estimated profit. Included customer duty is
   `gross - gross / (1 + rate)`; tax is not profit. A supplier duty exemption
   requires a recorded reason and remains an unverified contract assumption.
   Prices are locked to six gp decimals and invoices to copper pieces.
4. Review the quote, enter the customer and their PO reference, and confirm
   terms to reserve. Quotes expire after **24 real-world hours** and reserve
   nothing by themselves. Confirmation rechecks prices, dates and supply.
5. Record actual supplier/customer payments with unique references. A deposit
   is **not automatically received** or counted as profit. Dispatch requires
   procurement payment, the agreed deposit/prepayment, the pickup date and
   sufficient revalidated supply. Delivery requires elapsed travel time
   measured from actual dispatch and explicit customer acceptance. The app
   never advances the world clock to make an order pass these checks.
6. An undispatched order can be cancelled after any recorded supplier and
   customer funds have been refunded. Expenses can remain sunk. Shipped and
   delivered quantities stay consumed against their original supply period.
   Refund entries reverse cash receipts/payments, not contract prices or
   credit notes. Recorded cash remains separate from projected profit.

### Availability and persistence

Planning windows are non-overlapping within each month: normally days 1-10,
11-20 and 21-30, with a separate clipped festival-day window where needed.
Fresh goods use their shorter horizon; pickup is at the window end because
future output is not immediately on hand. Reservations protect the selected
grade/allocation and a shared source-commodity ceiling across both modes.
Daily warehouse snapshots do not shorten the contract period: inventory-mode
contracts use a tenday, or the configured shorter fresh-bread horizon.
Overlap checks also prevent double booking when the horizon changes.
Seasonal-inventory free-stock quotes use modeled uncommitted warehouse stock,
including winter stores with no current production surplus. Free-stock claims
share that stock across **all dates**, grades, destinations and connections;
moving to tomorrow or the next tenday never resets them. Dispatch and delivery
retain the deduction; cancellation releases it. Earlier bookings also respect
the smaller stock/grade budgets of already-reserved later pickups. Growing
modeled stock can increase the remaining balance, but does not erase old claims.
Without inventory-lot provenance or physical replay of PO withdrawals, those
deductions deliberately do not age out or receive inferred replenishment credits.
This conservative overlay can understate availability after stock turnover; it
does not change the physical inventory, production, demand or GDP calculation.
Existing modeled warehouse exports remain dated allocations that can be taken
over through the guild, but not sold a second time. Closing free stock already
excludes these exports. Direct producer quantities are additionally capped by
local output rather than assumed imported-stock provenance.
Seasonal export takeovers and producer limits sum actual daily allocations and
production from `inventory_window`, rather than multiplying the pickup-day rate.
Destination exports are counted only for the selected buyer. A fractional fresh
contract horizon prorates only its last day. Carried stock is a single closing
balance, never a sum of snapshots; imports replenishing protected reserves do
not become free stock. Public free-stock views read that closing balance without
replaying a whole window for every displayed material.
A planning quota still requires a physical stock check.

Board, product/quality, named-merchant, location/material, CLI and arbitrage
availability deduct these claims without changing physical demand, output,
GDP or modeled trade flows a second time. Daily flow fields remain physical
forecasts before dated POs. Current-month location detail uses the current
world day; other selected months are displayed at their first day. Reload a
view to see bookings made elsewhere.

The SQLite ledger is stored by default at
`%LOCALAPPDATA%\FaerunEconomyEngine\trade-ledger.sqlite3`, outside the project
and OneDrive. Set `FAERUN_TRADE_DB` before starting the server/CLI to choose
a different file or isolate a campaign. Back up that database while the app
is stopped. Plain `World()` instances have no ledger unless one is explicitly
attached. SQLite transactions prevent competing app processes from reserving
the same supply. Repeating a quote confirmation or cash reference is
idempotent; conflicting reuse is rejected. Status changes use versions and
all actions retain an audit trail.

Trade APIs are `/api/trade/options`, `/api/trade/quote`, `/api/trade/order`,
`/api/trade/orders`, `/api/trade/payment` and `/api/trade/status`. They are
local-only; mutations require same-origin JSON requests with bounded bodies.
This is a local simulation ledger, not a payment processor, carrier booking,
shared-fleet scheduler, verified stock system or automatic general-wallet
posting service.

## Location requirements and local resources

The location detail page now includes a **requirements dashboard for every
market**, including the smaller surveyed locations. These estimates drive
market demand, production, prices, and finite trade allocation; they are not a
separate, unconstrained shopping list.

The model estimates wealth-sensitive diets (including exotic foods), food
businesses and other trades, mage populations and arcane supplies, standing
forces and militia equipment replacement, and growth-related housing,
builders and carpenters. It also includes household fuel, clothing, hygiene,
health, agriculture and transport needs. Counts are model assumptions, **not
a canonical census or a list of named businesses**. Residents serving as
soldiers, mages or militia are already included in ordinary household food.

Terrain, waterways, population scale and established industries determine
local resource estimates. Large cities can have limited peri-urban farms;
ports and river communities can catch fish; suitable hinterlands provide
timber, stone or common ore. Restricted tropical crops and rare materials
still require their catalogue geography. Surveyed markets remain explicitly
marked as inferred rather than acquiring invented historical industries.

All catalogue recipes now participate in material accounting. For example,
weapons require steel, steel requires iron and fuel, and iron requires ore
and charcoal. Those orders arise at the **manufacturing location**, which
may import the inputs from another producer before exporting the finished
goods. Workshops share scarce ingredients and cannot make goods without them.
Production plans cover local requirements plus allocated export orders, not
every workshop running at an arbitrary maximum every day. Output-equivalent
facility estimates show the implied bakeries, mills, butchers, taverns,
blacksmiths, weapon makers, armorers and sawmills separately from demographic
staffing counts; these two estimates are not additive.

By default, eligible producers represent **supporting production districts**,
not just the people and acreage inside a settlement boundary. Their baseline
raw capacity is scaled to aggregate needs plus reserves: 15% for grain/salt
(`staple_reserve_ratio`) and 10% for other raw goods
(`resource_reserve_ratio`). Export-processing plans are likewise apportioned
among existing capable producers. This is an explicit equilibrium scenario,
not independently surveyed output, accessible land, or workforce capacity.
It does not create a producer where none exists, move tropical plantations
north, or invent rare deposits. Every material exposes its
`hinterland_capacity_multiplier`. Large factors indicate how strongly the
estimate depends on assumed surrounding production districts.

Set `world.config.calibrate_source_districts = False` to use conservative
resource footprints and established capacity without this extrapolation and
see the resulting shortages. In either mode, events apply **after** baseline
planning: the model never rescales supply to replace an active crop failure,
mine closure or other disaster.

The dashboard separates:

- Final-use requirements from intermediate workshop orders.
- Scheduled production capacity from input-backed output (not an idle
  machinery-capacity survey).
- Pre-trade import need and export surplus from allocated imports and exports.
- Actual consumption, unused closing material and remaining unmet demand.
- Supplier quantities and routes from destination export commitments.

Material quantities use each good's **catalogue trade unit per day**, not a
mixture of pounds, barrels, bushels and items in one total. Cross-good freight
totals use pounds. Force equipment is amortized into replacement demand, not
ordered anew for the whole army every day. Growth is an inferred annual
planning rate, not a reconstructed historical population series.

With `seasonal_inventory` enabled, local stocks carry across daily balances;
the legacy mode remains a daily steady-state model. Neither mode adds shipment
arrival scheduling, manufacturing labor ceilings, or physical shipment loss
accounting. Service staffing shares a bounded inferred worker pool. Route
spoilage affects cost; the fresh-bread delivery horizon is
still enforced. Unused ingredient reservations are not re-exported in a
second pass, so unmet workshop plans can coexist with another unused input.

`GET /api/location?settlement=waterdeep` includes the full `requirements`
payload even when its price table is filtered by category. Market reports
expose baseline final requirements and per-sector quantities, and quotes
include `final_demand_per_day`, `final_consumption_per_day`, `demand_sectors`,
processing requirements and consumed inputs. Existing `household_*` quote
fields are retained as compatibility aliases for total final use, including
institutional use, in the expanded model.

The expanded model is enabled by default. Set
`world.config.expanded_requirements = False` to compare with the legacy
demand model and its bread/flour-only recipe accounting. Both price and
location-detail caches distinguish this setting.

The requirements dashboard loads before historical prices. Seven-year price
history is an explicit opt-in in the expanded model because it recomputes 84
monthly material balances. The current month, its imports, and the location's
requirements can be explored without waiting for that calculation.

## Service industries, visitors and local accounts

The expanded model also covers fourteen service sectors: health; religion;
working animals and training; administration and justice; knowledge and
education; commerce and finance; logistics; communications; hospitality;
utilities; civil security; maintenance; culture; and professional/technical
services. These have explicit service units, staffing, demand, capacity,
consumable inputs and estimated valuations. Their staffing reclassifies
existing occupations and draws on the remaining worker pool; it is not an
additional population layered on top of the old establishment counts.

Service providers order inputs for labor-feasible planned work. Actual
delivery is limited by the least supplied input. Unused reservations return
to closing material, just as they do for a factory recipe. The industry
dashboard distinguishes desired, planned and delivered services; an estimated
clinic count is not a promise that all patients can be treated.
The material table's "final demand" means non-manufacturing orders, including
service-provider inputs; it is not GDP final expenditure. Service intermediate
inputs are deducted separately in the local accounts.

### The visitor economy

Domestic leisure, pilgrimage, scholarly, festival, adventure and business
trips connect actual reachable locations. Affinity, wealth, safety, event
risk, season and Harptos festivals affect travel. Overnight stays compete
for fixed lodging beds; unmet lodging demand is not counted as an arrival.
Day visits are separate from overnight visitors. The current bounded search
uses the best eight overnight or three day destinations per origin/segment,
with a configurable maximum of 14 risk-adjusted travel days; day visits
require a route within half a risk-adjusted day.

Monthly arrivals use a 30-day Harptos month, while average visitors present
use arrivals and length of stay. A day trip represents .35 of a food-day.
Visitors retain origin/segment spending preferences, so affluent guests can
demand exotic food in a poor destination. Their food is removed from their
origin's variable household requirements and added at the destination.
Lodging, healthcare and other service inputs create additional demand.
Municipal water and sanitation requirements also reflect net visitor-days.

Baseline source districts are **not** resized to erase a monthly visitor
surge. Resident staffing and lodging capacity do not automatically expand
when visitor demand increases. Permanent housing, clothing and other fixed
origin needs remain; this is not a complete simulation of travelers in transit.

Visitor receipts price allocated visitor goods and delivered paid services.
The exact same payment is debited to the visitor's origin. Domestic visitors
bring gold into the host economy but do not create gold for the world as a
whole. Imputed public services are not treated as tourist cash payments.
No external tourists, traveler wallets, credit limits, fares, or persistent
treasury balances are modeled yet.

### Domestic water: sources, access and essential needs

Water is reported in **gallons**, for both quantities and capacities. The
location's `requirements.water` assessment separates:

- Estimated natural freshwater from its estimated usable/potable fraction.
- Municipal distribution capacity from input-backed municipal delivery.
- Household/private collection, sharing the same finite water pool.
- Essential drinking/cooking needs from other domestic uses.
- Source/quality gaps, collection/distribution gaps, and operational/input gaps.

An inhabited settlement with no recorded water infrastructure receives an
explicitly **unverified** groundwater and household-collection allowance,
not a claim that particular wells exist. Terrain and season modify inferred
wells/springs and rain-capture yields; river/wetland metadata can add surface
freshwater. A seaport does not supply fresh water by itself. Cistern
replenishment is counted once, not added to an assumed full cistern every day.

The planning targets are approximately **1.321 gallons/person-day for
essential drinking and cooking**, within **5.283 gallons/person-day total
domestic use**. These preserve the previous model's volumes by conversion;
they are scenario targets, not clinical survival thresholds.
Essential use is allocated first. A routine-use gap is not presented as a
failure to meet drinking-water needs.

Municipal and private collection cannot withdraw the same water twice.
Utility-service plans are limited by usable water as well as workforce and
materials. Household self-provision is not counted as additional paid
service revenue. Source footprints do not expand to accommodate visitors.
The old municipal-water staffing indicator remains in the API with
`scope: municipal_water_reference`, but is replaced on screen by this
complete assessment; it is not an additional water source.

Explicit location scenarios can override the estimates:

```python
world.config.water_overrides["yallasch"] = {
    "natural_gallons_per_day": 12000,
    "potable_fraction": 0.9,
    "household_gallons_per_person_day": 2.5,
    "municipal_collection_multiplier": 1.0,
}
```

Alternatively, `source_multiplier` scales the inferred sources; zero models
a complete source failure. `potable_fraction: 0` models no usable domestic
water despite raw water being present. Changes invalidate caches, including
edits inside an existing location scenario. Unknown locations/fields,
negative amounts and non-finite values are rejected. Overrides are scenario
inputs, not automatically verified observations, and are applied after the
baseline allowance rather than triggering replacement water.

This is domestic water accounting, not a river-basin, irrigation, livestock,
or industrial-water model. Water imports, aqueduct connections, treatment
plants, storage inventories, shortage duration and mortality are not
simulated. Generic crop failures are not automatically interpreted as dry
wells; water-specific failure or contamination should be configured
explicitly. Neither a missing municipal workforce nor an inferred daily
gap is a prediction that a settlement will die.

### Trade balances and estimated gross local product

The location's accounts separate:

- **Merchandise balance:** export shipment invoices minus import shipment
  invoices, valued at matching current producer-gate prices plus export margin.
- **Net visitor receipts:** receipts from visiting nonresidents minus residents'
  spending in other modeled locations.
- **Partial external balance:** the sum of those two balances, not profit or
  a full balance of payments. Freight, tariffs, investment, remittances and
  other financial flows are not assigned to counterparties here.
- **Estimated gross local product (GLP):** local goods output less production
  ingredients, plus delivered service output less service intermediate inputs.

GLP uses **constant catalogue commodity prices and baseline service
valuations**, unlike the current-price trade invoices and retail visitor
receipts. Nonmarket public services are imputed. Named durable service assets
are capital acquisitions rather than intermediate consumption; depreciation
is not deducted from gross product. Output includes modeled production into
closing material. Source-district calibration means this is a settlement-and-
hinterland proxy, not independently surveyed city GDP.

Exports and tourist receipts are **not added again to GLP**: the underlying
goods and services already enter production. Annual and per-resident figures
are the current daily run rate multiplied by 365, not historical annual totals.
Reading accounts does not mutate wealth, population or a gold balance.

These sections are included under `requirements.economy` in the location
API and its JSON download. Market and trade reports expose the same
`accounts`; Python callers can use `economic_report`. Comparison switches are
`world.config.service_economy` and `world.config.visitor_economy` (both default
true); visitors also require the service and expanded-requirements models.
`visitor_scale` defaults to 1 and can be set to 0 or increased for scenarios.
`visitor_max_days` controls route eligibility. Cache keys include these
settings, the month, events/revision and all other economy configuration.

## Daily supply allocation

Markets reserve local production for their own daily demand first. Remaining
export surplus is shared across buyers, so it cannot be promised twice.
Eligible deliveries are allocated in deterministic order by delivered unit cost,
travel days, source ID and destination ID. A buyer may receive several suppliers;
diversification is not forced when one supplier can cover the requirement.
This greedy order is neither a fairness policy nor a global cost optimizer.

Quotes expose `sources` (local use and active imports), `imports_per_day`,
`exports_per_day`, `local_consumption_per_day`, `unmet_demand_per_day`, and
`backup_sources`. Backups show unreserved remaining capacity, not deliveries;
the same backup capacity can appear for several buyers. Legacy `source`,
`source_distance`, and `source_days` summarize the largest active import supplier.
Unit costs in source rows are before destination retail adjustments.
The board and product detail provide expandable supplier breakdowns.

Bread and flour have baseline local processing capacity sufficient for ordinary
local needs. Other processed necessities receive this floor where the producing
industry exists. Explicit shortages and events can still reduce supply.
The grain -> flour -> bread chain now reserves and consumes daily recipe inputs,
including salt. Actual milling and baking output is limited by the least
available ingredient. Household demand is reserved before processing, and
competing recipes share remaining inputs proportionally to planned capacity.
Ingredient delivered costs set a floor on local production costs. With the expanded requirements model, all other catalogue recipes also
reserve and consume their inputs. Establishment counts are estimates; no
individual bakery, mill or granary inventory is simulated: seasonal storage
is aggregated by local market and commodity.

Flour capacity includes baseline baking requirements. Existing grain and salt
producers represent their surrounding hinterlands: their baseline output is
scaled to at least total household and planned processing demand times
`world.config.staple_reserve_ratio` (default 1.15). This is an explicit modeling
assumption, not a surveyed farm count. The multiplier is exposed in quote
`factors.hinterland_capacity_multiplier`. Events apply after this calibration,
so crop failures do not automatically generate replacement capacity. Aggregate
reserves do not guarantee delivery to every disconnected or capacity-limited town.

For this chain, `demand_per_day` includes households plus planned processing.
Quotes separately expose `household_demand_per_day`,
`household_consumption_per_day`, `processing_demand_per_day`,
`processing_consumption_per_day`, `production_capacity_per_day`, and
`production_inputs` (required, reserved and consumed quantities in each input's
trade unit). Unused reservations remain in `material_closing_stock`; they are
not re-exported in a second pass. Upstream planning can therefore exceed actual
use when another ingredient limits output. Seasonal inventory carries retained
stock into subsequent daily balances; disabling that model restores the legacy
single-day balance. Shipment arrivals are not scheduled in either mode.

Bread imports must arrive within `world.config.fresh_bread_days` (default 3).
In legacy mode, modeled bread stock uses that horizon, capped at ten days;
other stock uses ten days of post-export supply, excluding inputs consumed in
production. That legacy stock is a window estimate, not persistent inventory.
Seasonal mode instead reports local opening and closing quantities with
commodity-specific storage limits, loss and reserves.
Finite supply can leave connected cities underserved or out of stock, and prices
already at the shortage ceiling need not rise further under a supply shock.

Optional delivery-lane limits use trade units per day:

```python
world.config.delivery_limits[("grain", "daggerford", "waterdeep")] = 100.0
```

Limits are non-negative and commodity/source/destination specific. Unspecified
lanes are unbounded apart from supplier surplus. There is no inferred fleet
capacity or shared road-edge throughput model. Configuration changes above
invalidate the quote cache automatically.

## Quick start

From this folder:

```powershell
.\run.ps1
```

That checks the code compiles, runs the smoke test, then opens the market
board in your browser. From there, **World map** opens a single map with a
**Poster map / 3D terrain** selector. Switching views preserves the camera,
selected settlement, commodity, and route. The poster is the default;
terrain provides a poster-free view with optional 3D perspective controls.
Existing `terrain.html` bookmarks still open the terrain view. Click any
settlement pin to price its market. If
Windows blocks the script, use
`powershell -ExecutionPolicy Bypass -File .\run.ps1`.

Other switches: `-Map` (open the world map instead of the board), `-Check`
(checks only, no server), `-SkipCheck` (straight to the board), `-Port 9000`,
`-NoBrowser`.

Prefer to do it by hand? See [Install](#install) and the sections below.

---

## Install

No third-party packages are needed for the engine, the CLI or the web UI. The
MCP server needs the `mcp` package.

```powershell
pip install -e ".[mcp]"        # editable install with the MCP server
# or just run it in place:
python -m faerun.cli market Waterdeep
```

Python 3.10+.

---

## How a price is made

For each commodity the engine runs three passes over the whole world.

### 1. Local balance — supply vs demand

**Supply** comes from a settlement's industry tags (`farm3`, `mine_iron2`,
`smith3`, `weave2`, ...), modified by terrain, then scaled by size:

```
supply = 0.35 x SUM(industry level x terrain modifier) x size scale
       + 1.20 x specialty bonus
```

* Terrain matters: `mine` is x1.35 in mountains, `farm` is x0.4 in a desert and
  x0.12 in an Underdark cavern, `spice` is x1.55 in the jungles of Chult.
* Primary industries (farms, mines, herds) get a rural bonus; secondary crafts
  (smithies, weavers, alchemists) get an urban bonus.
* A **specialty** is a settlement's signature export — Mithral Hall's mithral,
  Ruathym's amber, Port Nyanzaru's ivory.
* A **shortage** cuts local production to 12%.
* Some goods are region-locked: Chultan teak only grows in the jungle,
  faerzress crystal only forms in the Underdark, camels only come from the
  desert. Everyone else must import them.

**Demand** is per-capita appetite relative to a balanced market:

```
demand = min(PROD(cultural trait factors) ^ 0.7, 5.0)
       x (per-capita demand) ^ 0.5
       x wealth ^ (0.6 + 1.8 x luxury)
```

Dwarves want ale and iron, elves want wine and silk, drow want spider silk and
poison, temples want incense, a wartorn city wants steel. Wealthy markets pay
far more for luxuries than for staples — that is what the `luxury` exponent
does.

Fourteen necessities also have explicit per-person daily baselines covering
food, drink, clothing, fuel, light, hygiene and household goods. The engine
interpolates between poor (wealth 0.65), common (1.00) and rich (1.40)
profiles, then multiplies those quantities by the settlement population.
This anchors essential demand to the number of souls in a location while
leaving cultural traits, events and shortages free to apply market pressure.
The staple allowance is divided among raw grain, flour and bread according to
local craft and trade access. Existing recipe conversions preserve the same
grain-equivalent nutrition, avoiding double-counting processed food.
Call `settlement_daily_requirements("Daggerford")` for the complete baseline
in catalogue units per person and per settlement.

### 2. Export pricing

Any settlement with `supply / demand > 1.02` is a **source**. It sells at

```
producer price = base x max(surplus floor, (demand/supply) ^ surplus elasticity)
                 + export margin
```

so a glut drops the price to at most 45% of book value, and the merchant who
buys it takes a 12% cut.

### 3. Landed cost — the trade network

The world is a weighted graph of **skyways, sea lanes, rivers, ferries, barge
runs, roads, trails, wilderness tracks, Underdark tunnels and portages**, built
from the great named routes of the Realms (the Trade Way, the Long Road, the
Golden Way, the Dragon Reach, the Sword Coast Run, the Halruaan Skyroad,
Mantol-Derith's tunnels...) plus short local links.

| Mode | Freight cost | Speed | Hazard | |
| --- | --- | --- | --- | --- |
| air | x3.20 | 110 mi/day | x0.85 | Halruaan skyships; ruinous, but nothing is faster |
| sea | x0.30 | 72 mi/day | x0.90 | deep-water hulls |
| river | x0.55 | 40 mi/day | x0.70 | river craft |
| ferry | x0.70 | 30 mi/day | x0.80 | estuaries, lakes, island hops |
| barge | x0.45 | 28 mi/day | x0.60 | slow bulk haulage on still water |
| road | x1.00 | 24 mi/day | x1.00 | maintained and drained |
| trail | x1.30 | 19 mi/day | x1.30 | unpaved but established |
| track | x1.45 | 18 mi/day | x1.40 | wilderness caravan going |
| tunnel | x1.90 | 12 mi/day | x2.20 | Underdark passages |
| portage | x2.20 | 10 mi/day | x1.60 | hauling overland between waters |

#### Routes that are several things at once

Many real arteries are not one mode. The Delimbiyr is a river until the Shining
Falls, where everything comes out of the water and goes round on waggons. The
Underdark smugglers' ways are deep passage *and* a furtive surface trail. Such
a route is written `river+portage` or `tunnel+trail`, most prominent mode
first, and the engine prices the awkwardness of it:

- **cost** is the mean of the member modes plus **+18% per extra mode** — the
  cargo covers part of the distance by each, then pays for every transhipment;
- **speed** is the harmonic mean (distance splits, so *durations* add), slowed
  a further **12% per extra mode** for loading and waiting;
- **risk** takes the worst mode in full plus **35% of every other**, because a
  chain is exposed everywhere it is handled.

So a multimodal leg is always dearer, slower and more dangerous than its parts
suggest. Routes report `modes`, `mode_label` and a `transfers` count; the 3D
map draws them as **broken lines**. Note this is not the same as two parallel
routes between one pair of towns — where those exist, traders simply take the
cheaper, and the engine keeps only that one.

A single **multi-source Dijkstra** pushes every producer's goods outward at
once. Edge weight is `freight units x rate x pounds + spoilage x days`, so
heavy goods (grain, coal, bricks) become expensive with distance while light
valuable ones (gems, spices, silk) barely notice; perishables rot on long
hauls; and dangerous roads add a risk premium. Each importing market therefore
learns the **cheapest landed price** and **who supplies it**.

An importer blends local and landed prices:

```
core  = local share x base + (1 - local share) x landed
core  = core x (1 + (1 - local share) x scarcity elasticity x 0.4)
core  = min(core, base x 18)
```

### 4. Finishing the number

```
price = core x (1 + market markup) x (1 + tariff) x season x events x wobble
```

* **Markup** is competition: a thorp with one trader charges up to 45% more
  than Waterdeep's crowded markets.
* **Tariff** is the local duty, from Mintarn's 3% to Amn's 12%.
* **Season** follows the Calendar of Harptos. In legacy mode, grain is x1.25 in
  spring and x0.8 at harvest, furs spike in winter, and fresh fish is cheap in
  summer. Seasonal inventory instead makes availability respond to separate
  local production/demand curves and carried stock; it does not stack the
  legacy harvest price multiplier onto those quantity changes.
* **Events** are wars, blockades, droughts, festivals and gold rushes.
* **Wobble** is a small deterministic hash-based jitter (±7%) so two markets
  never look mechanically identical. Same world state, same seed, same price.

The merchant's **buy-back bid** applies a spread that widens where the good is
abundant and narrows where it is scarce.

---

## Command line

Global flags work on every subcommand:

```
--json                emit raw JSON instead of tables
--year 1493           set the Dale Reckoning year
--month Flamerule     set the Harptos month (name or number)
--seed 7777           reroll the market wobble
--event siege@"Baldur's Gate"     apply an event (repeatable)
--event drought@region:Amn
--event pirates@zone:sword_coast
```

| Command | What it does |
| --- | --- |
| `faerun market Waterdeep` | every price in one settlement |
| `faerun price "Bryn Shander" grain --quantity 20` | one good in one market |
| `faerun compare mithral_ingot --dearest` | one good across the Realms |
| `faerun route Waterdeep "Baldur's Gate"` | the trade road, leg by leg |
| `faerun arbitrage Waterdeep --category metal` | what to buy here and sell elsewhere |
| `faerun history Waterdeep grain` | a year of prices, month by month |
| `faerun trade Mithral Hall` | what a market exports and imports |
| `faerun settlements --region Amn` | list markets |
| `faerun commodities --category gem` | list goods |
| `faerun regions` | regions and their populations |
| `faerun events` | active events and available templates |
| `faerun chronicle` | the standing history, in full or for one place |
| `faerun timeline Neverwinter` | a basket priced through all seven years |
| `faerun calendar` | the Calendar of Harptos |
| `faerun serve` | open the commodity board in a browser |
| `faerun map` | open the poster map (with a link to 3D terrain) |
| `faerun location "Bryn Shander"` | open the location detail screen |

Examples:

```powershell
python -m faerun.cli market "Bryn Shander" --sort multiplier
python -m faerun.cli compare silk --region "Sword Coast"
python -m faerun.cli --month Nightal history Luskan fur_wolf
python -m faerun.cli --event blockade@Luskan market Luskan --category food
python -m faerun.cli arbitrage "Port Nyanzaru" --max-days 90 --json
```

Settlement and commodity arguments are fuzzy: `waterdeep`, `Waterdeep`,
`bryn shander`, `mithral`, `mithral_ingot` all resolve.

---

## Web UI — the commodity board

A commodity board you can click through, one settlement at a time.

```powershell
python -m faerun.cli serve        # or: python -m faerun.web
```

It prints a URL (default <http://127.0.0.1:8765>) and opens your browser.
Use `--port 0` to grab any free port, `--host 0.0.0.0` to expose it on the
LAN, and `--no-browser` to skip the auto-open.

There are **no third-party dependencies** — it is `http.server` plus a
single page whose HTML, CSS and JS live in `faerun/webassets.py`. Nothing
is fetched from a CDN, so it works offline.

What you get:

- a sidebar of all 125 settlements grouped by region, with a filter box
- the full price board for the selected market: every commodity with its
  price, buy-back price, multiplier against base, availability, stock and
  where the goods were hauled from
- click any column heading to re-sort (done in the browser, so it is instant)
- filter by category, search by name, or hide imported goods
- click a row for location-specific basic, standard, fine and masterwork
  offers, including each grade's price, availability and stock
- crafted goods also show their simple bill of materials per output unit,
  from bread and swords to carts, ships and trained warhorses
- the detail panel lists the cheapest markets in Faerûn for that good.
  **Load twelve-month price forecast** explicitly calculates prices from the
  selected month forward; it is not requested automatically when opening a row
  or following **Open full product detail**. With seasonal inventory, the
  forecast can require many daily allocations and hold up other API requests.
  The production/demand curves are separate and do not require that forecast
- set the Harptos month, year and wobble seed at the top and the whole board
  recomputes
- fire off events (siege, blockade, blight, gold rush …) against a settlement
  or region and watch the prices move; clear them again in one click

The page talks to a small JSON API, which is also useful on its own:

| Method | Endpoint | Notes |
| --- | --- | --- |
| GET | `/api/bootstrap` | date, seasons, seasonal-inventory flag, regions, settlements (with map coordinates), commodity profiles/storage metadata, event templates |
| GET | `/api/map` | terrain heightfield, settlement pins and trade legs for the 3D map |
| GET | `/api/market?settlement=…&category=…` | the full price board |
| GET | `/api/product?commodity=…&settlement=…` | catalogue, recipe and sourcing; optional settlement resolves local seasonal curves |
| GET | `/api/compare?commodity=…&region=…&limit=…&order=cheap\|dear` | one good across markets |
| GET | `/api/history?settlement=…&commodity=…&months=12` | twelve-month series |
| GET | `/api/trade?settlement=…&top=10` | exports and imports |
| GET | `/api/route?origin=…&destination=…&optimise=days\|cost` | caravan/ship routing |
| GET | `/api/arbitrage?origin=…&max_days=…&cargo=…` | trade runs worth making |
| POST | `/api/world` | `{"year":1492,"month":6,"seed":7}` |
| POST | `/api/event` | `{"template":"siege","settlements":["Neverwinter"]}` |
| POST | `/api/events/clear` | drop all active events |

The engine caches per world instance and is not thread-safe, so the server
serialises engine calls behind a lock. It is a single-table, single-DM tool —
please do not put it on the open internet.

---

## Poster and 3D terrain maps

The same server serves two focused views:

- <http://127.0.0.1:8765/map.html> is a top-down surveyed poster overlay.
- <http://127.0.0.1:8765/terrain.html> is an oblique, poster-free 3D relief map.

The commodity board and location page link to both views.

Optional traced transport geometry can be supplied through
`maps/road-geometries.json` (or `maps/road-geometries.path`) and
`maps/sea-air-routes.json` (or `maps/sea-air-routes.path`). Sea legs use the
export's water-mask-constrained waypoints; blocked sea legs are omitted rather
than replaced by straight lines. Air legs remain explicitly schematic.

Optional `maps\road-geometries.json` data can provide poster-traced FPS
polylines for roads and trails. When present, these curves replace straight
road/trail chords on both map pages; untraced transport modes retain their
engine geometry.

An optional `maps\location-terrain.json` survey can refine the terrain. The
`faerun-terrain-simple-v1` format supplies contiguous 10-mile cells across the
poster and becomes the authoritative terrain classification; unknown or
excluded cells retain the generated fallback. The older named-location survey
format remains supported. Neither format invents measured elevation. Set
`FAERUN_TERRAIN_SURVEY` to use a file from another location.

To start the server and land straight on the map:

```powershell
.\run.ps1 -Map                    # launcher
python -m faerun.cli map          # or the CLI
python -m faerun.web --map        # or the web entry point
```

The map is a **page on the server**, not a standalone file. Opening it from
disk will not work — the terrain, pins and prices all arrive over `/api/map`
and `/api/bootstrap`, so the server has to be running.

Every one of the 125 settlements is planted on the terrain as a pin whose
size follows its population. Click one and its full market opens in the
right-hand panel, so the map is a spatial front end for the same price
engine the board uses.

Controls:

| Action | Result |
| --- | --- |
| Drag | Orbit — turn the world and change the viewing angle |
| Scroll | Zoom in and out |
| Shift-drag or right-drag | Pan across the map |
| Arrow keys / `+` / `-` | Orbit and zoom from the keyboard |
| Hover a pin | Tooltip with region, size and the current heat-map price |
| Click a pin | Load that settlement's market into the side panel |
| Click a price row | Recolour every pin by that commodity |

The HUD adds a **commodity heat map** (pins run green → amber → red from
the cheapest market in the Realms to the dearest), toggles for trade roads
and labels, Reset / Top down / 3D oblique camera presets, a relief slider for
vertical exaggeration, and smooth, square-grid, or three hex-grid tile modes.
Grid strokes are drawn above an enabled poster overlay so the reference map
cannot hide them. The 3D preset also restores poster draping after map
realignment, and the poster uses the relief hill shading rather than masking it.

How it is built:

- `faerun/mapdata.py` holds the geography — a coastline for the mainland
  and Chult, four inland seas, fifteen mountain ranges and fifteen terrain
  zones — and rasterises it into a heightfield of roughly 21-mile cells in
  miles-space (96 × 146 for the shipped frame, more once it grows to cover a
  poster), the same coordinate space the gazetteer and the trade graph use. A
  land blob is stamped around every settlement afterwards, so no town can
  ever end up in the ocean. The raster is cached, so only the first request
  pays for it.
- `faerun/mapassets.py` holds the page. The renderer is **plain Canvas 2D**
  — a projected vertex heightfield drawn back-to-front with the painter's
  algorithm, with fixed-light shading precomputed per cell. No WebGL, no
  three.js, no CDN, no build step: it works offline like the rest of the
  tool, and it degrades to a lower level of detail while you are dragging
  so the camera stays smooth.

### Overlaying a published poster map

You can drape your own copy of a printed Faerûn map over the engine's terrain
and compare the two directly. Tick **Poster map** in the map's control panel,
then use **Fade** to blend between the artwork and the engine's own relief.

**No artwork is shipped with this project, and none is ever copied into it.**
Published Realms maps are Wizards of the Coast property. What this feature does
is *find* a copy you already own, on your own machine, and stream it to your own
browser while the server is running. Delete the file and the overlay disappears.

**The simplest way is to drop the image into the `maps\` folder** next to this
README. That folder is searched first, and a world-poster-shaped filename works —
you do not have to rename anything:

```
Faerun Economy Engine\
  maps\
    Faerun Map.jpg      <- put it here
```

The full resolution order, first hit wins:

1. `-Underlay <path>` on `run.ps1`, or `--underlay <path>` on the CLI:

   ```powershell
   .\run.ps1 -Map -Underlay ".\maps\Faerun Map.jpg"
   ```

2. the `FAERUN_MAP_UNDERLAY` environment variable,
3. a file called `underlay.jpg` (or `.png` / `.webp`) in `maps\`, the project
   root, or the current folder,
4. a world/region poster name such as `Faerun map.jpg`, `Faerun Hires.jpg`,
   `Forgotten Realms Map.png`, `Sword Coast Map.png` or `Toril Hi-Res.webp`,
   in `maps\`, the project root, the current folder, `Downloads`, `Pictures`
   or `Desktop`. The first folder with matches wins; within it, the newest
   matching world poster wins.

City maps and unrelated images are excluded from automatic selection, even
inside `maps\`. In this workspace, the world background is `maps\Faerun Hires.jpg`;
the Waterdeep atlas independently uses `maps\waterdeep-map-hires.jpg`. Adding or
updating a city map cannot replace the world background. Explicit overrides,
the environment variable, and the reserved `underlay.*` filename still take
precedence when you intentionally select a differently named image.

The startup banner tells you which file it settled on, and the map page says so
too. If nothing is found, the overlay controls stay hidden and a note appears
explaining where to put the image.

#### Lining it up

**If you have a `maps\locations.json` survey, this is already done for you.** The
survey records which pixel of the poster is Waterdeep and how many miles a poster
pixel covers, and Waterdeep has a world coordinate — which is enough to work out
exactly which patch of the Realms the image covers. The overlay is placed from
that automatically, in world miles, the moment it loads. The readout under the
sliders says so when it has.

One consequence surprises people, so it is worth stating plainly: **a correctly
placed poster will still not sit on the town dots until you have realigned the
markets too.** Before `faerun atlas --apply` the poster is right and the markets
are wrong, and seeing that gap is the entire reason the overlay exists. Run the
realignment in the next section and the two snap together.

Without a survey the first fit is a guess and you finish it by eye. Click
**Align…** for:

| Control | What it moves |
| --- | --- |
| East / South | Slides the poster over the world, in miles |
| Scale | Miles of world covered by one poster pixel |
| Stretch | Extra north-south scaling, for posters that are not square-on |
| Drape | Lets the poster follow the relief instead of lying flat |
| Survey fit | Snaps the poster back to the placement the survey computes |

Press **Top down** first — aligning is far easier without the tilt. Match a
coastline you can find on both maps; Waterdeep sits at (600, 1200) in engine
miles, Baldur's Gate at (560, 1800) and Calimport at (660, 2600), and the
readout under the sliders shows you where the poster's corner currently lands.
Your alignment is saved in the browser, so you only ever do this once.

Two things worth knowing. The alignment is stored in **world miles**, not screen
pixels, so it survives panning, zooming and tilting — line it up once and it
stays lined up. And the poster is painted *over* the terrain but *under* the
trade routes and settlement dots, so the engine's own data stays readable on top
of the artwork.

### Realigning the markets to your map

Once the poster is lined up you will notice that the dots do not always sit on
the right towns. That is not a bug in the alignment — the gazetteer's own
coordinates are canonical along the Sword Coast but drift further east, and the
drift changes direction along the way. No amount of sliding, scaling or rotating
the poster can fix a distortion that compresses one region and stretches the
next. So instead you tell the engine where a few markets really belong and it
works out the rest.

#### The fast way: a surveyed location index

Clicking 125 dots onto a poster by hand is honest work, but if you already know
where every label sits on the image you can skip all of it. Drop a survey into
`maps\` as `locations.json` and the map grows an **Align from survey** button
that places every market it recognises in one press.

The file looks like this — a header describing the image and its scale, then one
entry per place:

```json
{
  "coordinate_system": {
    "source_image": "Faerun Hires.jpg",
    "origin_name": "Waterdeep",
    "origin_pixel": { "x": 694, "y": 682 },
    "positive_x": "east",
    "positive_y": "north",
    "miles_per_unit": 120,
    "pixels_per_unit": 150.5,
    "scale_bar": { "start_x": 3644, "end_x": 4246, "miles": 480 }
  },
  "locations": [
    {
      "name": "Baldur's Gate",
      "category": "settlement_or_site",
      "pixel_x": 1036, "pixel_y": 1157,
      "east_miles": 272.7, "north_miles": -378.7
    }
  ]
}
```

Notes on how it is read:

- `east_miles` / `north_miles` are used when present; otherwise they are derived
  from `pixel_x` / `pixel_y` using the scale. A `scale_bar` measured off the
  artwork beats the declared `pixels_per_unit`, because it is the more direct
  measurement.
- The origin town is **pinned**: it stays exactly where the gazetteer already
  has it and everything else is laid out in true miles around it. An alignment
  therefore never slides the whole world sideways.
- Engine coordinates *are* miles, so the survey's distances carry across
  unchanged. This matters more than the picture: distance is freight cost, and
  freight cost is price.
- Only entries whose `category` looks like a place are matched. A
  `geographic_feature` is a label centre for a forest or a mountain range, not
  somewhere to put a market.
- Names are matched case-, accent- and punctuation-insensitively, so
  `Alagh&#244;n`, `Alaghon` and `ALAGHON` are the same town. Markets the survey
  does not mention are listed and left exactly where they were.

#### The frame grows to fit

The hand-drawn terrain was authored into a tall, narrow window — 2000 × 3040
miles. A real poster of the Realms is neither tall nor narrow: the survey puts
`Faerun Hires.jpg` at roughly **3800 × 2540 miles**, reaching about 1600 miles
further east than the hand-placed gazetteer ever did. Laid on the old frame,
most of the image hung off the eastern edge with no ground under it.

So the frame now stretches — it only ever **grows**, never shrinks — to cover
three things at once:

| what | when |
| --- | --- |
| the shipped bounds | always, so the hand-drawn coastline keeps its ground |
| the poster's footprint | whenever the survey can place it, calibrated or not |
| every market plus a margin | once a realignment is in force |

The heightfield is resized with it. Cells are held at about 20.8 miles until the
total runs past `MAX_CELLS` (26 000), and any reduction after that is applied to
**both axes at once** so the cells stay square — capping each axis on its own is
what smears a coastline in one direction only. The continent-wide frame works
out at roughly 178 × 145 cells of 21.3 miles, about 1.8× the shipped field. It
is rasterised once and cached, keyed on the gazetteer *and* the poster footprint,
so dropping a poster into `maps/` resizes the map on the next load.

With no poster and no calibration the frame is byte-for-byte the shipped one.

#### Rebuilding the terrain, not just the markets

Moving the towns without moving the ink would put Waterdeep in the ocean, so the
coastline, the mountain ranges and the climate zones are carried along by the
same warp. Doing that from market positions alone works where markets are dense
and drifts where they are not — and the empty quarters are exactly the ones with
the most map in them. Anauroch, the Great Glacier, Raurin and the open Sea of
Fallen Stars contain no markets at all, so nothing local holds them in place.

The survey names those features too, so they are pinned directly. Every named
sea, desert, forest and mountain range on the map is reduced to one reference
point, looked up in the survey, and added to the warp as an extra anchor.

Two properties make this safe:

- **No market moves.** The warp reproduces every control point it is given
  exactly, so adding scenery anchors refines where the ink goes without nudging
  a single town — which matters, because freight distance is a cost and cost is
  price.
- **A bad match is rejected, not obeyed.** A poster letters a mountain range
  along its spine rather than at its middle, and a name can match the wrong
  feature entirely. So each candidate anchor is checked against where the towns
  alone predict the feature should go, and anything more than
  `TERRAIN_ANCHOR_LIMIT` miles adrift is dropped and left where it was.

`faerun atlas` reports all of this before it changes anything — how many
features were pinned, which were rejected, and which the survey never mentioned:

```
Terrain: 21 of 31 named features pinned to the survey, 2 rejected as too far
out, 8 not in the survey
```

From the command line:

```powershell
python -m faerun atlas              # preview: who moves, and how far
python -m faerun atlas --apply      # commit it
```

Over MCP, the same thing is `get_map_alignment` (with `apply=true` to commit).

#### Surveyed local markets

The gazetteer trades in 125 hand-authored markets, while a poster survey
typically names two or three hundred settlements. Every surveyed town or site
missing from the gazetteer is now promoted to a small local market. It appears
in the commodity board, location timeline, map, HTTP API and MCP tools, and
receives a price for the complete commodity catalogue.

The survey contains coordinates but no population, industries or civic data,
so these markets are deliberately conservative. Each inherits terrain, region,
wealth, tariff and security from its nearest established market, has a small
inferred population, and begins with no authored industry or specialty. The
expanded requirements model also estimates modest local resources and basic
food processing from that inferred environment; these may create an explicitly
modeled surplus, not a claim of documented industry. A single local trail
attaches it to its established hub, carrying imports and any modeled exports
without creating a shortcut that changes established trade routes.

The map's **Surveyed markets** option shows or hides these inferred locations.
Forests, seas, mountain ranges and other geographic labels remain map features
rather than commodity markets. Positions are retained in both shipped and
surveyed coordinate spaces, so applying, replacing or clearing a realignment
does not compound the previous warp.

#### The manual way

If you have no survey — or want to touch up the places it did not name — tick
**Realign markets** in the map HUD, then:

1. Click a market's dot. It gets a dashed ring — that one is now listening.
2. Click the spot on the poster where it actually sits.
3. Repeat for a handful of well-spread landmarks. Three is the minimum for a
   proper fit; six to ten spread across the continent is plenty.
4. Press **Save**.

Every other settlement is carried along by a smooth fit through the points you
placed: a least-squares affine transform for the overall shape, plus a local
correction that makes the result land *exactly* on each of your points. Pick
landmarks in the regions you care about and their neighbours follow.

`Undo` drops the last point. `Clear` forgets them all and restores the shipped
coordinates. Esc cancels a half-finished point, and pressing it again leaves
realign mode.

What gets written is `faerun/data/coords.json`, and it only ever contains the
control points you placed — never all 125 settlements. The gazetteer in
`faerun/data/settlements.py` stays the readable source of truth, the calibration
is a small overlay applied on top of it at import time, and deleting the file
puts everything back exactly as it shipped.

Realigning is not cosmetic. Coordinates are literally miles, and miles drive
caravan distances, freight costs, travel times and therefore landed prices, so
saving a calibration rebuilds the trade graph and re-prices the world. That is
also why saving takes a second or two: the relief is restamped under the new
positions before the page comes back.

### If the map reports an error

The page is built to tell you what went wrong rather than sit there blank.
Any failure shows up as a red banner across the top of the map, and the
server prints a full traceback in the terminal it is running in.

| What you see | What it means |
| --- | --- |
| `invalid choice: 'map'` | An older build without the `map` subcommand — use `python -m faerun.cli serve` and browse to `/map.html` |
| `/api/map -> 500: ...` | The server raised while rasterising. The terminal has the traceback |
| `/api/map -> 404: not found` | You are not on the Faerûn server — something else is already using that port. Try `.\run.ps1 -Map -Port 9000` |
| `Map request failed: Failed to fetch` | The server stopped, or the page was opened from disk instead of over `http://` |
| `Renderer error: ...` | A drawing fault. The message names the cause; the canvas stops rather than flickering |
| Nothing happens for a few seconds | Normal on the very first load: the relief raster and the price cache are both built on demand |

Run `.\run.ps1 -Check` to compile every module and run the smoke test
without starting a server — that isolates a code problem from a browser one.

---

## MCP server

The server speaks **stdio**, which means you do not run it yourself: you tell an
MCP client where it lives and the client launches it as a child process, talking
to it over that process's stdin and stdout. Running it by hand only leaves a
process waiting silently for JSON-RPC on stdin -- useful just to prove it starts:

```powershell
cd "C:\path\to\Faerun Economy Engine"
pip install "mcp[cli]"           # once; or  pip install -e ".[mcp]"
python -m faerun.mcp_server      # Ctrl+C to stop; silence means it is healthy
```

A ready-made configuration sits in **`mcp.json`** in this folder with the
absolute path already filled in; copy out whichever block your client wants:

| Client | File it reads | Top-level key |
| --- | --- | --- |
| VS Code | `.vscode/mcp.json`, or *MCP: Open User Configuration* | `servers` |
| Copilot CLI | `~/.copilot/mcp-config.json`, or run `/mcp add` | `mcpServers` |
| Claude Desktop | `%APPDATA%\Claude\claude_desktop_config.json` | `mcpServers` |

The `cwd` is what lets `python -m faerun.mcp_server` find the package, so it has
to point at this folder unless you have pip-installed the project. Restart the
client after editing its config, then ask it to list its tools: you should see
twenty-seven names, starting with `list_settlements`.

Client configuration (Claude Desktop, VS Code, Copilot CLI, ...):

```json
{
  "mcpServers": {
    "faerun": {
      "command": "python",
      "args": ["-m", "faerun.mcp_server"],
      "cwd": "C:/path/to/Faerun Economy Engine"
    }
  }
}
```

If you installed the package, `"command": "faerun-mcp"` works instead.

### Tools

**Reference**

| Tool | Purpose |
| --- | --- |
| `list_settlements` | markets, filtered by region, name or population |
| `get_settlement` | one market in full, with its road connections |
| `list_commodities` | goods, filtered by category or name |
| `get_commodity` | one good in full |
| `list_commodity_sources` | goods with source regions, exporters and quality centers |
| `get_commodity_sources` | detailed producers and quality centers for one good |
| `list_regions` | regions and their market counts |
| `list_named_routes` | the great roads and sea lanes |
| `list_travel_modes` | every way freight moves, and the multimodal penalties |

**Prices**

| Tool | Purpose |
| --- | --- |
| `get_price` | one good in one market, with the reasoning behind it |
| `get_market_report` | every price in one market |
| `compare_prices` | one good across many markets |
| `get_price_history` | month-by-month prices over the year |
| `get_trade_summary` | what a market exports and imports |

**Trade**

| Tool | Purpose |
| --- | --- |
| `get_trade_route` | fastest or cheapest path between two markets |
| `find_arbitrage` | profitable cargoes, ranked by gp per day |

**World state**

| Tool | Purpose |
| --- | --- |
| `get_world_state` | date, season, seed, active events |
| `set_world_date` | move the calendar |
| `set_market_seed` | reroll the wobble |
| `list_event_templates` | the 21 ready-made events |
| `add_event` | apply an event to a settlement, zone, region or the world |
| `list_events` / `remove_event` / `clear_events` | manage events |

**History**

| Tool | Purpose |
| --- | --- |
| `get_chronicle_summary` | how much standing history the world carries |
| `get_settlement_history` | every recorded event touching one place |
| `get_settlement_timeline` | a basket priced in all 84 months, with analysis |
| `get_location_detail` | one market at one month, against a quiet-world control |
| `reset_chronicle` | regenerate the history, or strip it out |

Things you can now ask an assistant:

* "What does grain cost in Bryn Shander, and where does it come from?"
* "I have 2,000 lb of cargo space in Waterdeep and forty days. What should I carry?"
* "Put Baldur's Gate under siege, then show me its food prices."
* "Where in the Realms is silk cheapest? What about spider silk?"
* "Plot a route from Port Nyanzaru to Suzail and tell me the freight cost."
* "What has been happening to Bryn Shander over the last three years?"
* "Which month was food dearest in Athkatla, and what caused it?"
* "What is the drought currently costing the people of Amn?"

---

## Events

Twenty-one templates: `siege`, `war`, `blockade`, `drought`, `blight`,
`plague`, `famine`, `hard_winter`, `flood`, `monster`, `refugees`,
`bumper_harvest`, `caravan_boom`, `gold_rush`, `festival`, `bandits`,
`pirates`, `dragon`, `boom`, `trade_embargo`, `magical_surge`.

Each multiplies local supply, demand, price and route risk, optionally
restricted to certain categories (a siege hits food, arms and drink). Scope an
event to settlements, zones, regions or the whole world, and give it a
duration in months. Bespoke events can set the multipliers directly.

```python
from faerun.events import apply_event
from faerun.economy import price_for

apply_event(template="drought", regions=["Amn"], duration_months=6)
print(price_for("Athkatla", "grain").price)
```

---

## The chronicle — seven years of standing history

A world with no history prices everything at its calm, average level, which is
not how anywhere actually feels. So the engine ships with a **chronicle**: a
generated but deterministic history spanning **1489–1495 DR**, three years
either side of the 1492 DR "today", 84 months in all. It is installed
automatically, which means *every price the engine already quotes is a price in
a particular month of a particular history*.

Several hundred events sit in that window — droughts in the farm country, hard
winters in the North, pirates on the Sword Coast, orc war-bands out of the
Spine of the World, a gold rush in a mining town, blight, flood, plague,
refugees, festivals and caravan booms.

It is built to be **plausible**, not random:

* **Only where it could happen.** Pirates and blockades need a port. Floods
  need a river or a marsh. Hard winters need cold terrain *and* a northerly
  latitude. Gold rushes need a mine. The Underdark gets no weather at all.
* **Only when it could happen.** Droughts start in summer, hard winters in
  winter, harvest events at harvest. Seasonal events are snapped forward to
  their proper month.
* **Consequences follow causes.** A siege can be followed by famine, a drought
  by refugees, a plague by a labour shortage. These land in the months just
  after the event that caused them.
* **One thing at a time.** Two local episodes never overlap in the same town.
* **Eight curated events** are placed by hand, so regions that ought to be
  troubled in 1492 DR are.

The chronicle is **reproducible**: it is derived by hashing, not by a seeded
random generator, so the same world always yields the same history on any
machine and any Python version.

```python
from faerun.chronicle import chronicle_summary, settlement_timeline
from faerun.world import get_world, World

chronicle_summary()                     # how much history, and of what kind
settlement_timeline("Bryn Shander")     # everything that touches one town

World()                                 # a bare world has NO chronicle
get_world()                             # the shared world does
```

To turn it off entirely, set `faerun.world.USE_CHRONICLE = False` before the
first `get_world()`, or call `faerun.chronicle.clear_chronicle(world)` — which
leaves any events you added by hand alone.

---

## The location detail screen

```
python -m faerun.cli location "Bryn Shander"
```

One settlement, seven years, one price line. The screen shows:

* a **scrubber** across all 84 months, with a chart of the town's
  cost-of-living index, event periods shaded behind it, and click-to-jump;
* **what is happening now** — every event touching the place this month, with
  what it does to supply, demand and road risk;
* an **analysis** — the dearest and cheapest months, volatility, the sharpest
  single move, how many months were troubled versus quiet, and *what each
  event cost the basket* measured against the three months before it began;
* the **full market at the selected month**, priced twice — as history has it,
  and again with every event lifted — so each row can say what the trouble is
  actually costing rather than only what things cost.

The board and the 3D map both carry a **Location history** link that follows
whichever settlement you have selected.

From the command line:

```
python -m faerun.cli chronicle                     # world summary
python -m faerun.cli chronicle "Baldur's Gate"     # one town's history
python -m faerun.cli timeline Neverwinter --commodity grain --only-year 1492
python -m faerun.cli --json timeline Waterdeep     # for scripting
```

And over MCP: `get_chronicle_summary`, `get_settlement_history`,
`get_settlement_timeline`, `get_location_detail`, `reset_chronicle`.

Two notes on cost. The timeline prices a **basket** of about six goods rather
than all 130, because 130 goods across 84 months would be ~11,000 market
solutions; a basket is enough to draw a cost-of-living line and cheap enough to
serve from a web request. And the detail screen's counterfactual means two full
market passes — the same cost as loading the board twice.

### If the location screen looks broken

**Restart the server first.** The pages are baked into the server when it
starts, so a window left running from an earlier session keeps serving the page
set it was born with — and anything added since is simply not there. Symptoms
are a "No page called location.html" notice, or the status line reporting that
an endpoint is not served by this copy of the engine.

`run.ps1` now checks the port before it binds. If an older copy of the server is
still listening it stops it and takes over; if something else owns the port it
says so and suggests `-Port 8766` rather than failing obscurely.

If the page loads but a request fails, the status line under the toolbar carries
the server's own message. `python verify.py` exercises the same endpoints from
the command line, with a traceback instead of a red line in a browser.

### If the prices seem not to follow the date

Pricing one month means valuing all 130 goods across the whole trade network,
and then doing it a second time with the events lifted to get the "without
events" column. That is not instant. The chart, the date and the season are all
drawn from the timeline already in the browser, so they answer the scrubber
immediately; the table has to wait for the server.

Dragging the scrubber therefore used to queue one slow request per step, each
waiting on the one before, and replies for months already scrolled past were
discarded — so the table could sit on its old numbers for a long time. It now
keeps a single request in flight and refetches once for the month you actually
landed on, and the rows dim while a new month is being priced so it is obvious
the table is a month behind the slider. Finished months are cached, so scrubbing
back over ground you have already covered is instant, and a month with no events
running anywhere skips the second pass entirely.

Prices can move without an event: deterministic daily variation
(`EconomyConfig.noise`), monthly production/demand curves and changing storage
balances all affect quotes. Legacy seasonal price multipliers still apply when
seasonal inventory is disabled. Events are listed under **What is happening**
and their contribution is compared in the table's "without events" column;
a large price change is not by itself proof of an event.

---

## Using it as a library

```python
from faerun.world import World
from faerun.economy import price_for, market_report, find_arbitrage
from faerun.calendar import HarptosDate

world = World()
world.set_date(HarptosDate(1492, 11))          # Uktar, the Rotting

quote = price_for("Waterdeep", "mithral_ingot", world=world)
print(quote.price, quote.source, quote.source_distance, quote.notes)

report = market_report("Menzoberranzan", world=world, category="luxury")
deals = find_arbitrage("Baldur's Gate", world=world, max_days=30)
```

Prices are cached per `(commodity, world revision, month, seed)`, so a full
market report costs about half a second cold and is instant afterwards.
Changing the date, seed or events bumps the revision and invalidates the cache.

---

## Layout

```
faerun/
  calendar.py           the Calendar of Harptos and its seasons
  models.py             Commodity, Settlement, Event, PriceQuote
  world.py              the trade graph, routing, events, tunable config
  economy.py            the price engine and the public query API
  events.py             event templates and helpers
  chronicle.py          the generated seven-year standing history
  location.py           the timeline, the basket and the analysis
  cli.py                the command line browser
  mcp_server.py         the MCP server
  web.py                the web UI server and its JSON API
  webassets.py          the single-page commodity board (HTML/CSS/JS)
  mapdata.py            Faerun's geography, rasterised into a heightfield
  mapassets.py          the 3D world map page and its Canvas renderer
  mobile.py             dated mobile locations and itinerary resolution
  mobileassets.py       travelling-company profile page
  locationassets.py     the location detail screen and its timeline chart
  data/
    commodities.py      130 goods
    settlements.py      125 markets
    routes.py           named roads, trails, rivers, skyways, tunnels, sea lanes
tests/
  test_economy.py       data integrity and directional price checks
  test_modes.py         multimodal trade routes
  test_chronicle.py     the standing history and the location timeline
mcp.json                drop-in MCP client configuration
run.ps1                 one-click: compile, smoke test, open the board
verify.py               end-to-end smoke test
```

Run the tests with `pytest`.

For a quick end-to-end smoke test of the engine, every CLI subcommand, the web
API and the MCP tool surface in one go:

```
python verify.py
```

It prints an `ok`/`FAIL` line per check and exits non-zero on any failure, so
it doubles as a CI gate. The full-coverage check walks all 130 commodities
across all 125 settlements, so allow it a minute.

---

## Notes on the model

* Prices are in gold pieces per unit and are calibrated so that a balanced
  market sits near the D&D book price. Every good is purchasable somewhere in
  every market — nothing is priced into the void.
* The Sea of Fallen Stars and the Sword Coast are deliberately separate
  basins; goods travelling between them go overland or the long way round,
  which is exactly why Amn and Sembia grew rich.
* This is a plausible simulation for play, not canon. Populations, distances
  and industries are drawn from published sources where they exist and
  reasoned from geography where they do not.
