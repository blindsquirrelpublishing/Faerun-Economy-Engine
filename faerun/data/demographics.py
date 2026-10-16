"""Reviewed racial makeup of settlements, separate from modeled population and workers.

Every settlement with a researched lore entry must have a record here, even when the
honest answer is "unresearched". A record never feeds the economy: it describes who
the sources say live in a place, not how many workers the model assumes.

Statuses:
  quantified   at least one group carries a sourced ``share_pct``
  estimated    groups carry illustrative ``estimated_share_pct`` values, not sourced shares
  qualitative  groups and descriptors are sourced but no usable percentages are
  unresearched no reviewed source has been checked for this location yet
"""

DEMOGRAPHICS_STATUSES = ("quantified", "estimated", "qualitative", "unresearched")

WIKI = "https://forgottenrealms.fandom.com/wiki/"


def unresearched(note: str = "") -> dict:
    return {
        "status": "unresearched",
        "reference_period": "",
        "scope": "",
        "groups": [],
        "notes": [note] if note else [],
        "era_note": "No racial or ethnic breakdown has been reviewed for this location yet.",
        "sources": [],
    }


SETTLEMENT_DEMOGRAPHICS = {
    "secomber": {
        "status": "estimated",
        "reference_period": "Illustrative 1492 DR planning mix, informed by 14th-century descriptions (Volo's Guide to the Sword Coast, 1367 DR)",
        "scope": "Town of Secomber; model scenario, not a historical census",
        "groups": [
            {"race": "Human", "share_pct": None, "estimated_share_pct": 49, "descriptor": "Described as the majority, or about half of the town"},
            {"race": "Halfling", "share_pct": None, "estimated_share_pct": 45,
             "descriptor": "Almost as numerous as humans; some sources say they dominated the town"},
            {"race": "Dwarf", "share_pct": None, "estimated_share_pct": 3, "descriptor": "A small group (Ironeater clan)"},
            {"race": "Gnome", "share_pct": None, "estimated_share_pct": 2, "descriptor": "A few"},
            {"race": "Elf", "share_pct": None, "estimated_share_pct": 1, "descriptor": "A few (moon elves)"},
        ],
        "notes": [
            "Illustrative planning assumption only: human 49%, halfling 45%, dwarf 3%, gnome 2%, moon elf 1% (total 100%). No source supplies these percentages or confirms this mix for 1492 DR.",
            "The historical descriptions of human majority versus halfling predominance conflict; these values choose one near-even scenario, not a resolved historical finding.",
        ],
        "era_note": (
            "Descriptions come from 14th-century material cited by the Forgotten Realms Wiki; "
            "Volo's Guide to the Sword Coast (1994, set 1367 DR) was read directly on 2026-10-15. "
            "Nothing shows how the mix changed after hobgoblin raids and tribute (1479 DR) or the "
            "poverty recorded circa 1491 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Secomber",
            "url": WIKI + "Secomber",
            "accessed": "2026-10-14",
            "kind": "secondary",
        }, {
            "title": "Volo's Guide to the Sword Coast (1994), Secomber, pp. 79 to 85",
            "url": "https://housegriffon.com/RPG/Games/DnD/add2/ForgottenRealms/Volo%27s%20Guide%20to%20the%20Sword%20Coast.pdf",
            "accessed": "2026-10-15",
            "kind": "primary",
        }],
    },
    "hlondeth": {
        "status": "quantified",
        "reference_period": "1372 DR (Forgotten Realms Campaign Setting, 3rd edition, as cited by the wiki; The Vilhon Reach, 1996, p. 21); not verified for 1492 DR",
        "scope": "Hlondeth population profile; racial mix's city-versus-50-mile-territory coverage is not independently established",
        "groups": [
            {"race": "Human", "share_pct": 84.0, "descriptor": "",
             "subgroups": [
                 {"name": "Chondathan", "share_pct": 56.0},
                 {"name": "Turami", "share_pct": 41.0},
                 {"name": "Shaaran", "share_pct": 3.0},
             ]},
            {"race": "Kobold", "share_pct": 15.0, "descriptor": "Described as an enslaved population"},
            {"race": "Yuan-ti", "share_pct": 1.0, "descriptor": ""},
            {"race": "Halfling", "share_pct": None, "descriptor": "Small presence; proportion uncertain (secondary reference says >1%, inconsistent with rounded 84% + 15% + 1%)"},
        ],
        "notes": [
            "Subgroup shares are percentages of the human population, not of the whole.",
            "The source's halfling >1% notation conflicts with the rounded group totals of 100%; no reliable halfling share is assigned.",
            "The 453,600 population counts city and environs; the scope of the independently cited racial percentages is not established by that count.",
        ],
        "era_note": (
            "The breakdown is cited by the wiki to The Vilhon Reach (1996), p. 21 and was not read "
            "directly for its numerical breakdown. The separate 453,600 population figure "
            "counts the city and environs in 1372 DR; it does not establish the racial mix's "
            "geographic scope or apply to the engine's 60,000-resident planning scenario."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Hlondeth",
            "url": WIKI + "Hlondeth",
            "accessed": "2026-10-03",
            "kind": "secondary",
        }],
    },
    "arrabar": {
        "status": "qualitative",
        "reference_period": "1357 to 1373 DR lore; restoration noted for the late 15th century DR",
        "scope": "City of Arrabar",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "Mostly human",
             "subgroups": [
                 {"name": "Chondathan", "share_pct": None},
                 {"name": "Blade Kingdomer", "share_pct": None},
             ]},
        ],
        "notes": [
            "No other race is named and no percentages were found.",
        ],
        "era_note": (
            "The wiki infobox lists the Arrabarrans as mostly human (Chondathans and Blade "
            "Kingdomers). It does not date the description, and the city was destroyed in the "
            "Spellplague and restored by the late 15th century DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Arrabar",
            "url": WIKI + "Arrabar",
            "accessed": "2026-10-03",
            "kind": "secondary",
        }],
    },
    "daggerford": {
        "status": "qualitative",
        "reference_period": "Undated infobox; population figures run 1368 to 1485 DR",
        "scope": "Town of Daggerford",
        "groups": [
            {"race": "Dwarf", "share_pct": None, "descriptor": "Present; share not stated"},
            {"race": "Halfling", "share_pct": None, "descriptor": "Present; share not stated"},
            {"race": "Human", "share_pct": None, "descriptor": "Present; share not stated"},
        ],
        "notes": [
            "The infobox lists the races alphabetically, so the order is not a ranking.",
        ],
        "era_note": (
            "Taken from the wiki infobox, which cites its references as a group, so the book "
            "behind the list is not confirmed."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Daggerford",
            "url": WIKI + "Daggerford",
            "accessed": "2026-10-07",
            "kind": "secondary",
        }],
    },
    "griffon_s_nest": {
        "status": "qualitative",
        "reference_period": "Undated in the reviewed summary; latest documented snapshot is 1485 DR",
        "scope": "Settlement of Griffon's Nest",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "Described inhabitants are human Uthgardt",
             "subgroups": [{"name": "Uthgardt", "share_pct": None}]},
        ],
        "notes": [
            "No other race is named; that is not evidence that none lives there.",
        ],
        "era_note": "The wiki describes the inhabitants as human Uthgardt who worship Uthgar. Not verified for 1492 DR.",
        "sources": [{
            "title": "Forgotten Realms Wiki: Griffon's Nest",
            "url": WIKI + "Griffon%27s_Nest",
            "accessed": "2026-10-01",
            "kind": "secondary",
        }],
    },
    "neverwinter": {
        "status": "qualitative",
        "reference_period": "1370 to circa 1372 DR, 1479 DR, and circa 1491 DR; not a single 1492 DR census",
        "scope": "City of Neverwinter; different historical snapshots",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "Among the principal residents circa 1370 DR; common families in 1479 DR"},
            {"race": "Half-elf", "share_pct": None, "descriptor": "Among the principal residents circa 1370 DR; common families in 1479 DR"},
            {"race": "Dwarf", "share_pct": None, "descriptor": "Minority circa 1370 DR"},
            {"race": "Eladrin", "share_pct": None, "descriptor": "Described among residents circa 1479 DR"},
            {"race": "Tiefling", "share_pct": None, "descriptor": "Described among residents circa 1479 DR"},
            {"race": "Dragonborn", "share_pct": None, "descriptor": "Mercenary delegation hired by 1479 DR; not a resident share"},
            {"race": "Orc", "share_pct": None, "descriptor": "A few remained circa 1491 DR after most left"},
            {"race": "Half-orc", "share_pct": None, "descriptor": "A few lived in the city circa 1491 DR"},
        ],
        "notes": ["1479 DR mercenaries do not establish permanent residents; no percentages or unified 1492 DR mix were found."],
        "era_note": "The wiki's dated historical passages cross the 1451 DR destruction and rebuilding; group presence at different times must not be combined into one 1492 DR share.",
        "sources": [{
            "title": "Forgotten Realms Wiki: Neverwinter, Inhabitants and infobox",
            "url": WIKI + "Neverwinter",
            "accessed": "2026-10-15",
            "kind": "secondary",
        }],
    },
    "triboar": unresearched(
        "Checked Forgotten Realms Wiki: Triboar and Category: Inhabitants of Triboar (accessed 2026-10-08); no settlement-level racial or ethnic breakdown found."
    ),
    "phandalin": {
        "status": "qualitative",
        "reference_period": "Late 15th century DR infobox description; not numerically dated to 1492 DR",
        "scope": "Town of Phandalin",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "Mainly humans"},
            {"race": "Dwarf", "share_pct": None, "descriptor": "Present; share not stated"},
            {"race": "Elf", "share_pct": None, "descriptor": "Present; share not stated"},
            {"race": "Gnome", "share_pct": None, "descriptor": "Present; share not stated"},
            {"race": "Half-elf", "share_pct": None, "descriptor": "Present; share not stated"},
            {"race": "Halfling", "share_pct": None, "descriptor": "Present; share not stated"},
        ],
        "notes": [
            "The source gives wording only (mainly/present) and no percentages.",
        ],
        "era_note": (
            "The reviewed Phandalin page records a late-15th-century race description in the infobox. "
            "No source in the reviewed set gives percentages or a 1492 DR-specific breakdown."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Phandalin",
            "url": WIKI + "Phandalin",
            "accessed": "2026-10-09",
            "kind": "secondary",
        }],
    },
    "waterdeep": {
        "status": "quantified",
        "reference_period": "1372 DR (Forgotten Realms Campaign Setting 3e, as cited by the wiki); not verified for 1492 DR",
        "scope": "Waterdeep (city versus surrounding territory not explicit in the reviewed percentage source)",
        "groups": [
            {"race": "Human", "share_pct": 64.0, "descriptor": ""},
            {"race": "Dwarf", "share_pct": 10.0, "descriptor": ""},
            {"race": "Elf", "share_pct": 10.0, "descriptor": ""},
            {"race": "Halfling", "share_pct": 5.0, "descriptor": ""},
            {"race": "Half-elf", "share_pct": 5.0, "descriptor": ""},
            {"race": "Gnome", "share_pct": 3.0, "descriptor": ""},
            {"race": "Half-orc", "share_pct": 2.0, "descriptor": ""},
            {"race": "Other", "share_pct": 1.0, "descriptor": "Unspecified races"},
        ],
        "notes": [
            "The reviewed wiki includes 1% other races, completing its listed total to 100%.",
            "The reference also reports a much larger territorial population; which population the racial percentages describe is unverified.",
        ],
        "era_note": (
            "The percentages appear beside a 1372 DR snapshot on the Waterdeep wiki page, "
            "but the city-versus-territory scope is not confirmed by the directly consulted text. "
            "No reviewed source gives a 1492 DR racial breakdown."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Waterdeep",
            "url": WIKI + "Waterdeep",
            "accessed": "2026-09-11",
            "kind": "secondary",
        }],
    },
    "amphail": {
        "status": "quantified",
        "reference_period": "Circa 1372 DR (Environs of Waterdeep web enhancement, 2006, as cited by the wiki); not verified for 1492 DR",
        "scope": "Village of Amphail and outlying farms",
        "groups": [
            {"race": "Human", "share_pct": 64.0, "descriptor": ""},
            {"race": "Dwarf", "share_pct": 10.0, "descriptor": "", "subgroups": [{"name": "Shield dwarf", "share_pct": None}]},
            {"race": "Elf", "share_pct": 10.0, "descriptor": ""},
            {"race": "Halfling", "share_pct": 5.0, "descriptor": "", "subgroups": [{"name": "Lightfoot", "share_pct": None}]},
            {"race": "Half-elf", "share_pct": 5.0, "descriptor": ""},
            {"race": "Gnome", "share_pct": 3.0, "descriptor": ""},
            {"race": "Half-orc", "share_pct": 2.0, "descriptor": ""},
            {"race": "Other", "share_pct": 1.0, "descriptor": "Unspecified races"},
        ],
        "notes": [
            "The cited mix is tied to the circa-1372 DR population snapshot and may not hold in 1492 DR.",
        ],
        "era_note": (
            "The percentages come from the Amphail wiki page's citation to Environs of Waterdeep (2006). "
            "The source was not independently re-read in this pass."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Amphail (village)",
            "url": WIKI + "Amphail_(village)",
            "accessed": "2026-10-04",
            "kind": "secondary",
        }],
    },
    "goldenfields": {
        "status": "qualitative",
        "reference_period": "Infobox race list across 14th- to late-15th-century references; no 1492 DR-specific breakdown",
        "scope": "Settlement/abbey complex of Goldenfields",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "Present; ordering does not imply rank"},
            {"race": "Halfling", "share_pct": None, "descriptor": "Present; ordering does not imply rank"},
            {"race": "Half-orc", "share_pct": None, "descriptor": "Present; ordering does not imply rank"},
        ],
        "notes": [
            "The reviewed source lists races but provides no percentages or majority wording.",
        ],
        "era_note": (
            "The Goldenfields wiki infobox names humans, halflings and half-orcs without percentages. "
            "No reviewed source in this pass dates a fuller mix to 1492 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Goldenfields",
            "url": WIKI + "Goldenfields",
            "accessed": "2026-10-05",
            "kind": "secondary",
        }],
    },
    "red_larch": unresearched(
        "Checked Forgotten Realms Wiki: Red Larch and Category: Inhabitants of Red Larch (accessed 2026-10-06). The collected research (2026-10-15) repeats these findings without a settlement-level racial or ethnic breakdown; no race shares can be inferred from named inhabitants."
    ),
    "stone_bridge": unresearched(
        "Checked Forgotten Realms Wiki: Stone Bridge, plus linked Westbridge and Beliard pages (accessed 2026-10-10); Stone Bridge is documented as a bridge/temple site with no resident racial mix."
    ),
    "leilon": unresearched(
        "Checked Forgotten Realms Wiki: Leilon and Category: Inhabitants of Leilon (accessed 2026-10-11); no settlement-level racial or ethnic breakdown found for the town."
    ),
    "yartar": unresearched(
        "Checked Forgotten Realms Wiki: Yartar and Category: Inhabitants of Yartar (accessed 2026-10-12); no settlement-level racial or ethnic breakdown found."
    ),
    "orlumbor": unresearched(
        "Checked Forgotten Realms Wiki: Orlumbor and Category: Inhabitants of Orlumbor (accessed 2026-10-15); no settlement-level racial or ethnic breakdown found."
    ),
    "longsaddle": {
        "status": "qualitative",
        "reference_period": "1358 to 1368 DR (infobox and article); individuals recorded to the late 1490s DR",
        "scope": "Hamlet of Longsaddle",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "The only race the wiki infobox names"},
        ],
        "notes": [
            "Named individuals of other races (a half-elf in the 14th century DR from the video game Dungeon Hack; a halfling in the late 1490s DR from the 2023 film Honor Among Thieves) are not treated as population shares.",
            "No percentages were found. A race that is not named is not evidence of absence.",
        ],
        "era_note": (
            "The wiki infobox lists humans, citing Volo's Guide to the North (1993), p. 52, and "
            "The Savage Frontier (1988), p. 30, both describing the hamlet between 1358 and 1368 DR. "
            "No later description of the population was found."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Longsaddle",
            "url": WIKI + "Longsaddle",
            "accessed": "2026-10-16",
            "kind": "secondary",
        }],
    },
}
