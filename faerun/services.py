"""Estimated service workloads and labor-limited plans, never actual delivery.

All rates below are scenario assumptions, not Faerun census or canonical prices.
Inputs are final-use trade units per service unit; the material engine, not this
module, expands their recipes and determines input-supported delivery.
"""

from __future__ import annotations

import math
from typing import Iterable

from .models import Commodity, Settlement


DAYS_PER_YEAR = 365.0
WORKDAYS_PER_YEAR = 240.0
SERVICE_SECTOR_IDS = frozenset({
    "health", "religion", "animals", "administration", "knowledge", "commerce",
    "logistics", "communications", "hospitality", "utilities", "civil_security",
    "maintenance", "culture", "professional",
})

# id, name, examples, unit, units/workday, team FTE, estimated gp/unit, market
_SECTORS = (
    ("health", "Health and healing", ("mundane healers", "apothecaries", "clerical healing"),
     "consultation", 4.0, 3, .6, True),
    ("religion", "Religious services", ("clergy", "shrines", "ceremonies", "lay officiants"),
     "attendance", 30.0, 6, .04, False),
    ("animals", "Animal care and training", ("horse trainers", "stables", "farriers", "herd care"),
     "animal-care-hour", 6.0, 3, .15, True),
    ("administration", "Administration and justice", ("officials", "courts", "record clerks"),
     "case", 5.0, 5, .3, False),
    ("knowledge", "Knowledge and education", ("cartographers", "librarians", "schools", "scribes"),
     "learner-hour", 20.0, 4, .04, True),
    ("commerce", "Commerce and finance", ("brokers", "moneychangers", "bankers", "accountants"),
     "transaction", 20.0, 4, .06, True),
    ("logistics", "Transport and storage", ("carriers", "porters", "warehouse keepers", "boatmen"),
     "consignment", 8.0, 8, .2, True),
    ("communications", "Communications", ("couriers", "messengers", "postal clerks"),
     "message", 12.0, 3, .1, True),
    ("hospitality", "Hospitality and personal services",
     ("inns", "baths", "laundry", "barbers", "domestic help"),
     "guest-night equivalent", 6.0, 5, .4, True),
    ("utilities", "Water, sanitation and fire services",
     ("water carriers", "sanitation crews", "fire watches"), "resident-service-day", 0.0, 5, .01, False),
    ("civil_security", "Civilian security", ("civilian guards", "watch patrols", "gate keepers"),
     "protected-person-day", 250.0, 6, .008, False),
    ("maintenance", "Repair and reclamation", ("repairers", "cobblers", "reclaimers", "tinkers"),
     "repair-hour", 6.0, 3, .15, True),
    ("culture", "Culture and entertainment", ("performers", "musicians", "storytellers", "festivals"),
     "audience-hour", 40.0, 4, .025, True),
    ("professional", "Professional services", ("surveyors", "engineers", "appraisers"),
     "professional-hour", 6.0, 3, .5, True),
)

# Pounds/service unit. Package weights come from the caller's catalogue.
_INPUT_MASS = {
    "health": {"herbs_healing": .2, "soap": .3, "linen": .05},
    "religion": {"incense": .002, "candles": .004},
    "animals": {"iron_ingot": .02, "charcoal": .05, "leather": .005},
    "administration": {"lamp_oil": .015},
    "knowledge": {"lamp_oil": .004},
    "commerce": {"lamp_oil": .005},
    "logistics": {},
    "communications": {"wax": .0005},
    "hospitality": {"linen": .03, "soap": .08, "charcoal": .5, "lamp_oil": .02},
    "utilities": {"soap": .0003, "charcoal": .001},
    "civil_security": {"lamp_oil": .001, "linen": .0003},
    "maintenance": {"iron_ingot": .03, "leather": .02, "linen": .01, "charcoal": .03},
    "culture": {"lamp_oil": .002, "linen": .0005},
    "professional": {"lamp_oil": .005},
}
_INPUT_UNITS = {
    "health": {},
    "religion": {},
    "animals": {"tools_carpenter": .0001},
    "administration": {"paper": .08, "ink": .0015},
    "knowledge": {"paper": .03, "ink": .0005},
    "commerce": {"paper": .04, "ink": .0007},
    "logistics": {},
    "communications": {"paper": .1, "ink": .0005},
    "hospitality": {"pottery": .00005},
    "utilities": {"barrel": .000002, "rope": .000002, "tools_carpenter": .000001},
    "civil_security": {"lantern": .000002, "rope": .000001},
    "maintenance": {"tools_carpenter": .0001},
    "culture": {"paper": .001, "ink": .00001},
    "professional": {"paper": .1, "ink": .002, "tools_carpenter": .0002},
}


def _number(value: float, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite nonnegative number, not a boolean")
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{label} must be finite and nonnegative, got {value!r}")
    return number


def _catalogue(commodities: Iterable[Commodity]) -> dict[str, Commodity]:
    goods = {}
    for c in commodities:
        if not isinstance(c.id, str) or not c.id or c.id in goods:
            raise ValueError(f"Commodity ids must be nonempty and unique: {c.id!r}")
        if _number(c.weight, f"{c.id}.weight") == 0:
            raise ValueError(f"{c.id}.weight must be positive")
        _number(c.base_price, f"{c.id}.base_price")
        _number(c.demand, f"{c.id}.demand")
        for cid, amount in c.bom.items():
            _number(amount, f"{c.id}.bom[{cid!r}]")
        goods[c.id] = c
    return goods


def _workers(profile: dict, population: float) -> tuple[dict[str, float], float]:
    """Validate the base labor ledger; missing fields are errors, not defaults."""
    pool = _number(profile["worker_population"], "worker_population")
    free = _number(profile["unallocated_workers"], "unallocated_workers")
    buckets = {}
    for row in profile["establishments"]:
        cid = row["id"]
        if cid in buckets:
            raise ValueError(f"Duplicate occupation {cid!r}")
        buckets[cid] = _number(row["workers"], f"establishments[{cid}].workers")
    assigned = math.fsum(buckets.values())
    if pool > population * .5 or not math.isclose(
        assigned + free, pool, rel_tol=1e-12, abs_tol=1e-9
    ):
        raise ValueError("Base profile occupations and unallocated workers must partition the worker pool")
    for bucket, field in (
        ("health", "health_workers"), ("temples", "temple_workers"),
        ("logistics", "logistics_workers"), ("sanitation", "sanitation_workers"),
        ("arcane", "mage_population"), ("garrison", "standing_army"),
    ):
        if buckets[bucket] != _number(profile[field], field):
            raise ValueError(f"{field} disagrees with establishment {bucket!r}")
    return buckets, free


def _utility_productivity(s: Settlement, profile: dict) -> float:
    parameters = profile["formula_assumptions"]["service_parameters"]
    factors = parameters["water_collection_factors"]
    source = ("river" if s.river else "oasis" if s.has_trait("oasis")
              else "cavern" if s.underdark else s.terrain)
    factor = _number(factors[source] if source in factors else factors["default"], "water source factor")
    water_need = _number(parameters["water_gallons_per_resident_day"], "water need")
    waste_need = _number(parameters["waste_lb_per_resident_day"], "waste need")
    water_rate = _number(parameters["water_gallons_per_worker_day"], "water productivity")
    waste_rate = _number(parameters["waste_lb_per_worker_day"], "waste productivity")
    if min(water_need, waste_need, water_rate, waste_rate) == 0:
        raise ValueError("Municipal needs and worker productivities must be positive")
    if factor == 0:
        return 0.0
    # Both physical tasks need labor; 10% of utility time is fire readiness.
    return .9 / (water_need / (water_rate * factor) + waste_need / waste_rate)


def service_sector_plans(
    s: Settlement, commodities: Iterable[Commodity], profile: dict, *,
    visitor_days: float = 0.0, overnight_visitors: float = 0.0,
) -> list[dict]:
    """Return all fourteen estimated sectors using an *unextended* base profile.

    ``visitor_days`` is visiting person-days/day, ``overnight_visitors`` occupied
    guest-nights/day. Hospitality combines lodging and paid personal services;
    neither visitor argument changes staffing, establishments or baseline beds.
    Missing catalogue goods are omitted, not fabricated or substituted; sparse
    catalogues model only their supplied inputs. No recipe inputs are expanded.
    """
    pop = _number(s.population, "population")
    if pop != int(pop) or pop != _number(profile["population"], "profile.population"):
        raise ValueError("Service plans require matching integral settlement/profile populations")
    wealth = _number(s.wealth, "wealth")
    _number(s.security, "security")
    visitors = _number(visitor_days, "visitor_days")
    overnight = _number(overnight_visitors, "overnight_visitors")
    growth = _number(profile["annual_growth_rate"], "annual_growth_rate")
    for tag, level in s.industries.items():
        _number(level, f"industries[{tag!r}]")
    goods = _catalogue(commodities)
    buckets, free = _workers(profile, pop)
    utility_productivity = _utility_productivity(s, profile)
    share = min(1.0, max(0.0, (wealth - .65) / .75))
    trade = min(3.0, s.industry_level("trade"))
    carrier_factor = 1 + .25 * trade + .5 * s.is_port
    resources = profile["resource_assumptions"]
    draft = _number(resources["draft_oxen"], "draft_oxen")
    cattle = _number(resources["dairy_stock"], "dairy_stock")
    horses = _number(profile["mounted_troops"], "mounted_troops")
    cargo_animals = pop / 500 * carrier_factor
    owned_training_stock = horses + cargo_animals + draft
    training_per_year = owned_training_stock * (.25 + growth)
    stabled_stock = horses + cargo_animals
    animal_hours = (
        stabled_stock * .1 + training_per_year * 12 / DAYS_PER_YEAR
        + (horses + cargo_animals + draft) * 6 / DAYS_PER_YEAR
        + cattle * .05 / DAYS_PER_YEAR
    )

    # Fractional FTE are disjoint slices of existing mixed occupations. The
    # remainder stays in goods production; builders, farmers, mages and soldiers
    # are never borrowed. Temple healing is a slice, not a second cleric census.
    sources = {cid: {} for cid in SERVICE_SECTOR_IDS}
    for sector, bucket, fraction in (
        ("health", "health", 1.0), ("health", "temples", .25),
        ("religion", "temples", .75), ("logistics", "logistics", .8),
        ("communications", "logistics", .2), ("hospitality", "brewers", .4),
        ("utilities", "sanitation", 1.0), ("animals", "smiths", .15),
        ("maintenance", "smiths", .1), ("maintenance", "textiles", .1),
    ):
        sources[sector][bucket] = buckets[bucket] * fraction
    targets = {
        "health": pop * .0025, "religion": pop * .0015,
        "animals": animal_hours / (6 * WORKDAYS_PER_YEAR / DAYS_PER_YEAR),
        "administration": pop * .0025,
        "knowledge": pop * (.003 + .004 * s.has_trait("academic")),
        "commerce": pop * (.003 + .001 * trade),
        "logistics": pop * (.015 + .005 * trade),
        "communications": pop * .002,
        "hospitality": pop * (.005 + .002 * trade + .002 * s.is_port),
        "utilities": pop * .005, "civil_security": pop * .003,
        "maintenance": pop * .003, "culture": pop * (.002 + .002 * share),
        "professional": pop * (.0015 + .001 * share),
    }
    deficits = {
        cid: max(0.0, target - math.fsum(sources[cid].values()))
        for cid, target in targets.items()
    }
    desired = _number(math.fsum(deficits.values()), "desired service FTE")
    ratio = min(1.0, free / desired) if desired else 0.0
    for cid in sources:
        sources[cid]["unallocated_workers"] = deficits[cid] * ratio
    reused = {}
    for allocations in sources.values():
        for bucket, amount in allocations.items():
            reused[bucket] = reused.get(bucket, 0.0) + amount
    for bucket, amount in reused.items():
        available = free if bucket == "unallocated_workers" else buckets[bucket]
        if amount > available + 1e-9:
            raise ValueError(f"Service allocation exceeds source worker bucket {bucket!r}")

    demand_rates = {
        "health": .008 + .004 * share, "religion": .04,
        "administration": .008, "knowledge": .06 + .06 * s.has_trait("academic"),
        "commerce": .05 * carrier_factor, "logistics": .035 * carrier_factor,
        "communications": .015, "utilities": 1.0, "civil_security": 1.0,
        "hospitality": .004 + .004 * share,
        "maintenance": .012, "culture": .06 + .08 * share,
        "professional": .006 + growth * .1,
    }
    visitor_rates = {
        **demand_rates, "animals": .003, "administration": .002,
        "knowledge": .01, "commerce": .1, "logistics": .025,
        "hospitality": .02, "maintenance": .004, "professional": .001,
    }
    rows = []
    for cid, name, examples, unit, productivity, team, fee, market in _SECTORS:
        if cid == "utilities":
            productivity = utility_productivity
        labor = math.fsum(sources[cid].values())
        capacity = labor * productivity * WORKDAYS_PER_YEAR / DAYS_PER_YEAR
        resident = animal_hours if cid == "animals" else pop * demand_rates[cid]
        visitor = visitors * visitor_rates[cid] + (overnight if cid == "hospitality" else 0.0)
        units = dict(_INPUT_UNITS[cid])
        masses = dict(_INPUT_MASS[cid])
        if cid == "health":
            units["antitoxin"] = (
                (.02 if s.terrain == "jungle" or s.has_trait("jungle") else .003)
                / DAYS_PER_YEAR / demand_rates[cid]
            )
            units["potion_healing"] = .005 * (.5 + share) / DAYS_PER_YEAR / demand_rates[cid]
        elif cid == "religion":
            # Only existing clergy make holy-water use, not inferred lay staff.
            units["holy_water"] = sources[cid]["temples"] * .04 / resident if resident else 0.0
        elif cid == "logistics" and resident:
            units.update({
                "cart": pop / 250 * carrier_factor * .12 / DAYS_PER_YEAR / resident,
                "wagon": pop / 1000 * carrier_factor * .12 / DAYS_PER_YEAR / resident,
                "barrel": pop * .25 * .25 / DAYS_PER_YEAR / resident,
                "mule": cargo_animals * .1 / DAYS_PER_YEAR / resident,
                "rope": profile["logistics_workers"] * .5 * .3 / DAYS_PER_YEAR / resident,
            })
        inputs = {key: float(amount) for key, amount in units.items()
                  if key in goods and amount > 0}
        for key, pounds in masses.items():
            if key in goods:
                inputs[key] = inputs.get(key, 0.0) + pounds / goods[key].weight
        basis = (
            "Estimated economic scenario, not canon or a business census. "
            f"One {unit} is the service unit; {productivity:g} units/worker-workday "
            f"at {WORKDAYS_PER_YEAR:g} workdays/{DAYS_PER_YEAR:g}-day year. "
            "Worker sources are disjoint FTE reclassifications plus a proportional "
            "allocation from the base unallocated pool; unclaimed fractions remain "
            "in other occupations. Counts round up part-time teams, not hospitals "
            "or guaranteed enterprises. Fees are estimated valuations"
            + ("." if market else ", imputed public/nonmarket value, not tax receipts.")
            + " Plans are labor-limited, not proof of commodity-supported delivery. "
            "Missing catalogue inputs are omitted; no substitutions are assumed."
        )
        row = {
            "id": cid, "name": name, "examples": list(examples), "unit": unit,
            "workers": float(labor), "establishments": math.ceil(labor / team),
            "resident_demand_per_day": float(resident),
            "visitor_demand_per_day": float(visitor), "demand_per_day": resident + visitor,
            "capacity_per_day": float(capacity),
            "planned_per_day": float(min(resident + visitor, capacity)),
            "fee_gp_per_unit": float(fee * (.8 + .4 * share)),
            "market_service": market, "inputs_per_unit": inputs,
            "visitor_units_per_person_day": float(visitor_rates[cid]), "basis": basis,
            "worker_sources": sources[cid],
            "reclassified_workers": labor - sources[cid]["unallocated_workers"],
            "newly_allocated_workers": sources[cid]["unallocated_workers"],
            "units_per_worker_workday": productivity,
            "workdays_per_year": WORKDAYS_PER_YEAR,
        }
        if cid == "health":
            row["mundane_healer_workers"] = sources[cid]["health"] + sources[cid]["unallocated_workers"]
            row["clerical_healer_workers"] = sources[cid]["temples"]
            row["basis"] += " Clerical healers use 25% of existing temple FTE; other healing is mundane."
        elif cid == "religion":
            row["clergy_workers"] = sources[cid]["temples"]
            row["lay_workers"] = sources[cid]["unallocated_workers"]
            row["basis"] += " Remaining 75% of temple FTE serve religion; new staff are lay, not extra clergy."
        elif cid == "animals":
            row.update({
                "owned_horse_stock": horses, "owned_training_stock": owned_training_stock,
                "animal_training_per_year": training_per_year,
                "stabled_animal_stock": stabled_stock,
                "stabling_capacity_head": capacity * .6 / .1,
                "training_capacity_per_year": capacity * .25 * DAYS_PER_YEAR / 12,
                "farrier_capacity_per_day": capacity * .15,
            })
            row["basis"] += (
                " Owned training stock is mounted horses, cargo mules and farm oxen; "
                "annual refresher events = stock*(.25+annual growth), 12 hours/event. "
                "This is owner-side refresher/handling training, never initial training "
                "embodied in newly sold warhorses. Farriery is six hours/head/year; "
                "stabling/grooming is .1 hours/mount-or-mule/day; cattle specialty care "
                "is .05 hours/head/year. Farm husbandry and all fodder stay agriculture. "
                "Illustrative stable/training/farrier capacity shares are 60/25/15%, "
                "not three separate uses of the whole workforce."
            )
        elif cid == "hospitality":
            resident_reserve = min(resident, capacity)
            row["lodging_beds"] = (capacity - resident_reserve) / (1 + visitor_rates[cid])
            row["resident_personal_service_units_per_person_day"] = demand_rates[cid]
            row["visitor_personal_service_units_per_day"] = visitors * visitor_rates[cid]
            row["lodging_demand_per_day"] = overnight
            row["basis"] += (
                " One guest-night equivalent is one overnight lodging service OR "
                "one staff-hour of paid baths, laundry, barbering or domestic help; "
                "six productive staff-hours/workday. Resident paid extras beyond "
                "household self-care require .004..008 equivalents/person/day by "
                "wealth. Every visiting person-day adds .02 personal-service "
                "equivalents; each overnight guest adds one lodging equivalent. "
                "Day visitors therefore pay only the personal-service share, not "
                "a whole guest-night. Inputs are an estimated average basket per "
                "equivalent; no meals or additional household food ration. Fixed "
                "lodging beds = (capacity-min(resident demand,capacity))/(1+.02), "
                "reserving baseline resident work and overnight guests' personal "
                "services even with zero visitors. Additional day-visitor personal "
                "services compete for the same finite labor and inputs; they never "
                "create beds or capacity. Beds are average serviceable bed-nights, "
                "not a surveyed count of physical rooms."
            )
        elif cid == "logistics":
            row["basis"] += (
                " Consignments represent local handling/storage, not intersettlement "
                "route capacity. Carrier stock replacement is amortized per consignment; "
                "fishing boats, fishing rope and nets remain agricultural requirements."
            )
        elif cid == "utilities":
            row["basis"] += (
                " A resident-service-day bundles about 5.283 gallons water, 4 lb waste removal "
                "and fire readiness. Ten percent of labor is fire readiness; the rest "
                "covers both physical tasks at base-profile water/waste rates, including "
                "freshwater source factors. The older water/waste indicators are legacy "
                "reference capacities for the original sanitation workforce, not "
                "additional workers, additive output or actual service delivery."
            )
        elif cid == "maintenance":
            row["basis"] += (
                " Repair labor and small spare materials cover movable household goods "
                "and reclamation only, without creating recovered goods. Building/roof "
                "repairs stay wholly in construction; no timber, planks, masonry or "
                "construction nails are charged here a second time."
            )
        elif cid == "civil_security":
            row["basis"] += " Civilian watch is disjoint from standing troops; militia remains a reserve."
        elif cid == "professional":
            row["basis"] += " Survey/design/appraisal fees exclude construction labor and building materials."
        for key, value in row.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                _number(value, f"{cid}.{key}")
        for key, amount in inputs.items():
            _number(amount, f"{cid}.inputs_per_unit[{key!r}]")
        rows.append(row)
    return rows
