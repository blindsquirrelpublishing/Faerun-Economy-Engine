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
        "reference_period": "1358 to 1485 DR descriptions; latest documented snapshot is 1485 DR (about 300 inhabitants); not a 1492 DR census",
        "scope": "Settlement of Griffon's Nest (the Griffon tribe's permanent village)",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "Inhabitants described as human Uthgardt of the Griffon tribe who worship Uthgar",
             "subgroups": [{"name": "Uthgardt (Griffon tribe)", "share_pct": None}]},
        ],
        "notes": [
            "No other race is named; that is not evidence that none lives there.",
            "The half-orc bandits under Azglyn who held the site before the Uthgardt were destroyed by them and are not a resident group.",
        ],
        "era_note": "The wiki infobox and person pages describe the inhabitants as human Uthgardt who worship Uthgar, in sources dated 1358 to 1485 DR. No percentages exist. Not verified for 1492 DR.",
        "sources": [{
            "title": "Forgotten Realms Wiki: Griffon's Nest",
            "url": WIKI + "Griffon%27s_Nest",
            "accessed": "2026-10-21",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Halric Bonesnapper",
            "url": WIKI + "Halric_Bonesnapper",
            "accessed": "2026-10-21",
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
    "port_llast": {
        "status": "qualitative",
        "reference_period": "Circa 1365 to 1374 DR (infobox); 1463 DR resettlement and 1480s DR description",
        "scope": "Town of Port Llast",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "The wiki infobox says mostly humans; by the 1480s DR most humans of the town were fishers"},
        ],
        "notes": [
            "Named individuals of other races (the dwarf smith Haljal Throndor, circa 1365 DR; a half-elf herbalist in 1374 DR from a video game) are not treated as population shares.",
            "Settlers from the northern Neverwinter Wood and the farmland around Luskan joined the town in 1463 DR; their race is not stated.",
            "No percentages were found. A race that is not named is not evidence of absence.",
        ],
        "era_note": (
            "The infobox description of mostly humans cites City of Splendors (1994), Volo's Guide to the North (1993), "
            "The Savage Frontier (1988), The Last Threshold (2013), Realms of the Deep (2000) and Neverwinter Nights (2002). "
            "No later description of the population was found."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Port Llast",
            "url": WIKI + "Port_Llast",
            "accessed": "2026-10-17",
            "kind": "secondary",
        }],
    },
    "warlock_s_crypt": {
        "status": "qualitative",
        "reference_period": "Circa 1351 to 1374 DR (infobox and article); Orbedal before -339 DR noted as former",
        "scope": "Warlock's Crypt (city of undead in the Troll Hills)",
        "groups": [
            {"race": "Undead", "share_pct": None, "descriptor": "Liches (about sixty by 1374 DR, many Netherese survivors), vampires, wraiths, wights, crawling claws, zombies and other undead"},
            {"race": "Troll", "share_pct": None, "descriptor": "A troop of trolls guarding the city"},
        ],
        "notes": [
            "Kastighur demons were sometimes summoned by Larloch; they are not treated as residents.",
            "Netherese humans lived in Orbedal before it fell in -339 DR; no living residents are recorded at the crypt.",
            "No percentages were found. A race that is not named is not evidence of absence.",
        ],
        "era_note": (
            "The infobox lists liches, vampires, wraiths, wights, crawling claws, zombies and other undead, and trolls, "
            "citing the Forgotten Realms Campaign Setting, 2nd edition revised (1993), Volo's Guide to the Sword Coast (1994), "
            "Lords of Darkness (2001) and the 3rd-edition Forgotten Realms Campaign Setting (2001). "
            "No description later than 1374 DR was found."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Warlock's Crypt",
            "url": WIKI + "Warlock%27s_Crypt",
            "accessed": "2026-10-18",
            "kind": "secondary",
        }],
    },
    "dragonspear_castle": {
        "status": "qualitative",
        "reference_period": "1255 to circa 1485 DR (infobox occupants and article); 1492 DR not described",
        "scope": "Occupants of Dragonspear Castle (a ruined fortress, not a settled community)",
        "groups": [
            {"race": "Undead", "share_pct": None, "descriptor": "Undead led by the boneclaw Born held the castle some time before 1479 DR; a coven of Shar-worshipping vampires (the Szarlnaxi) laired there around 1484 to 1485 DR"},
            {"race": "Human", "share_pct": None, "descriptor": "Soldiers and mercenaries of the Shining Crusade occupied the castle in 1368 DR (historical; from a video game)"},
            {"race": "Goblinoid", "share_pct": None, "descriptor": "Hobgoblins held the castle from 1305 to 1315 DR; orcs, goblins, kobolds, bugbears and ogres formed the Hordes of Dragonspear in 1363 DR (historical)"},
            {"race": "Devil", "share_pct": None, "descriptor": "Devils from Avernus held the castle in 1354 to 1356 DR and again in 1363 DR (historical)"},
            {"race": "Dwarf", "share_pct": None, "descriptor": "Dwarves sheltered there under the half-dwarf Daeros Dragonspear, 1255 to 1290 DR (historical)"},
        ],
        "notes": [
            "The infobox lists the notable occupants as dwarves and a dragon, goblinoids and devils; the undead and vampires come from the article's history.",
            "No living residents are recorded after 1368 DR. The groups describe successive occupiers, not a population mix.",
            "No percentages were found. A race that is not named is not evidence of absence.",
        ],
        "era_note": (
            "The infobox cites the Sword Coast Adventurer's Guide (2015), p. 83; the vampires come from Ghosts of Dragonspear Castle (2013), "
            "the undead under Born from the Forgotten Realms Campaign Guide (2008), p. 36, and the earlier occupiers from Volo's Guide to the "
            "Sword Coast (1994), Hordes of Dragonspear (1992), The Grand History of the Realms (2007) and Baldur's Gate: Siege of Dragonspear (2016). "
            "No description later than about 1485 DR was found."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Dragonspear Castle",
            "url": WIKI + "Dragonspear_Castle",
            "accessed": "2026-10-19",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Szarlnaxi",
            "url": WIKI + "Szarlnaxi",
            "accessed": "2026-10-19",
            "kind": "secondary",
        }],
    },
    "loudwater": {
        "status": "quantified",
        "reference_period": "1372 DR (Forgotten Realms Campaign Setting, 3rd edition, p. 169, and Legacy of the Green Regent: Extermination, pp. 20 to 21, as cited by the wiki); not valid for 1492 DR",
        "scope": "Town of Loudwater, 8,137 residents in 1372 DR; whether the figure covers the town alone or its claimed lands is not stated",
        "groups": [
            {"race": "Human", "share_pct": 37.0, "descriptor": "3,010 people in 1372 DR"},
            {"race": "Half-elf", "share_pct": 20.0, "descriptor": "1,627 people; almost a quarter of the 4,000 people in 1357 to 1370 DR were half-elves, mostly descended from Eaerlann"},
            {"race": "Elf", "share_pct": 18.0, "descriptor": "1,465 people, mostly moon elf ancestry; the nine chief elven families formed the noble houses"},
            {"race": "Halfling", "share_pct": 10.0, "descriptor": "814 people"},
            {"race": "Gnome", "share_pct": 7.0, "descriptor": "570 people"},
            {"race": "Dwarf", "share_pct": 5.0, "descriptor": "407 people"},
            {"race": "Half-orc", "share_pct": 3.0, "descriptor": "244 people; High Forest orcs also settled outside the Forestview Gate in 1372 DR"},
        ],
        "notes": [
            "Shares are the wiki infobox percentages for 1372 DR and match its counts.",
            "By 1479 DR about 2,000 people remained, the majority humans and half-elves (Forgotten Realms Campaign Guide, 2008); by the late 1480s DR the town was largely human and the elves long gone (Storm King's Thunder, 2016, p. 97). No later percentages were found, so the 1372 DR mix is not a 1492 DR census.",
        ],
        "era_note": (
            "The 1372 DR counts come from the 3rd-edition Forgotten Realms Campaign Setting (2001) and Legacy of the Green Regent: "
            "Extermination (2003), cited by the Forgotten Realms Wiki and not independently consulted. The 1479 DR and late 1480s DR "
            "descriptions are qualitative."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Loudwater",
            "url": WIKI + "Loudwater",
            "accessed": "2026-10-22",
            "kind": "secondary",
        }],
    },
    "grandfather_tree": {
        "status": "quantified",
        "reference_period": "1372 DR (Silver Marches, 2002, p. 27, as cited by the wiki); not valid for 1492 DR",
        "scope": "Ghostand, the Tree Ghost hamlet beside the Grandfather Tree, 224 residents in mid-1372 DR; the tree itself has no residents",
        "groups": [
            {"race": "Human", "share_pct": 86.0, "descriptor": "Uthgardt barbarians of the Tree Ghost tribe (Illuskan descent), joined in the late 15th century DR by Uthgardt from other tribes"},
            {"race": "Elf", "share_pct": 9.0, "descriptor": "Wood elves; wild elves are also described around the village", "subgroups": [{"name": "Wood elf", "share_pct": None}]},
            {"race": "Half-elf", "share_pct": 4.0, "descriptor": "Half-elves found around the village"},
            {"race": "Other", "share_pct": 1.0, "descriptor": "Not specified"},
        ],
        "notes": [
            "Shares are the wiki infobox percentages for Ghostand, citing Silver Marches, p. 27; Mintiper's Chapbook part 8 gives more than 350 people in the same year.",
            "No later breakdown was found; the 1372 DR mix is not a 1492 DR census.",
        ],
        "era_note": (
            "The 1372 DR figures come from Silver Marches (2002) and Mintiper's Chapbook (2001), cited by the Forgotten Realms Wiki "
            "and not independently consulted. Storm King's Thunder (2016) adds Uthgardt from other tribes living with the Tree Ghosts "
            "in the late 15th century DR, without numbers."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Ghostand",
            "url": WIKI + "Ghostand",
            "accessed": "2026-10-23",
            "kind": "secondary",
        }, {
            "title": "Forgotten Realms Wiki: Grandfather Tree",
            "url": WIKI + "Grandfather_Tree",
            "accessed": "2026-10-23",
            "kind": "secondary",
        }],
    },
    "mintarn": {
        "status": "qualitative",
        "reference_period": "Late 14th century DR descriptions (Races of Faerun, 2003; Realms of the Deep, 2000) with 15th century DR individuals; not a 1492 DR census",
        "scope": "Island of Mintarn as a whole; no population figure is recorded for any period",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "Illuskan humans, listed as the island's people (Races of Faerun, p. 92)"},
            {"race": "Merfolk", "share_pct": None, "descriptor": "A merfolk population, fond of imported Mabadann oysters (Realms of the Deep, 2000)"},
            {"race": "Dwarf", "share_pct": None, "descriptor": "A small dwarven population at Mintarn Mountain with remnants of Clan Ironstar (Crown of Fire; Dwarves Deep, p. 13, as a rumour of a secret cave hold)"},
        ],
        "notes": [
            "No percentages or counts were found. Individuals tied to the island in the 15th century DR include a red dragonborn White Sails sailor (Rayonde) and a dwarf soldier in Neverwinter (Muln Horan); single people are not evidence of a community.",
        ],
        "era_note": (
            "Groups come from the Mintarn article's infobox and text on the Forgotten Realms Wiki, citing Races of Faerun (2003), "
            "Realms of the Deep (2000), Dwarves Deep (1990) and Crown of Fire; not independently consulted. "
            "Nothing describes the island's makeup in 1492 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Mintarn",
            "url": WIKI + "Mintarn",
            "accessed": "2026-10-24",
            "kind": "secondary",
        }],
    },
    "luskan": {
        "status": "qualitative",
        "reference_period": "Circa 1360s to 1370 DR descriptions (A Reader's Guide to R. A. Salvatore's The Legend of Drizzt, 2008; Volo's Guide to the North, 1993) with late 15th century DR drow (Night of the Hunter, 2014); not a 1492 DR census",
        "scope": "City of Luskan; 15,000 to 16,000 people in the 1360s and 1370 DR, 4,000 in 1480 DR, no later figure",
        "groups": [
            {"race": "Human", "share_pct": None, "descriptor": "Mostly humans (A Reader's Guide, pp. 142 to 143); the city was hostile to non-humans and let few past its gates around 1370 DR"},
            {"race": "Drow", "share_pct": None, "descriptor": "Drow of Bregan D'aerthe and visitors at One-Eyed Jax in the late 15th century DR (Night of the Hunter, pp. 309 to 310)"},
        ],
        "notes": [
            "No percentages or counts by race were found. After the Spellplague the city also sheltered goblins, kobolds and aquatic monsters in the bog; these are not counted as residents here.",
        ],
        "era_note": (
            "Groups come from the Luskan article's infobox and text on the Forgotten Realms Wiki, citing A Reader's Guide to R. A. Salvatore's "
            "The Legend of Drizzt (2008), Volo's Guide to the North (1993) and Night of the Hunter (2014); not independently consulted. "
            "Nothing describes the city's makeup in 1492 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Luskan",
            "url": WIKI + "Luskan",
            "accessed": "2026-10-25",
            "kind": "secondary",
        }],
    },
    "nesme": {
        "status": "quantified",
        "reference_period": "1372 DR (The City of Nesme, 2001), with a circa 1371 DR table in the notes; not a 1492 DR census",
        "scope": "Town of Nesme; 6,140 or 1,966 people in 1372 DR depending on the source; in ruins in 1485 DR",
        "groups": [
            {"race": "Human", "share_pct": 79, "descriptor": "79% in 1372 DR"},
            {"race": "Halfling", "share_pct": 9, "descriptor": "9% in 1372 DR"},
            {"race": "Dwarf", "share_pct": 5, "descriptor": "5% in 1372 DR"},
            {"race": "Half-elf", "share_pct": 4, "descriptor": "4% in 1372 DR"},
            {"race": "Gnome", "share_pct": 2, "descriptor": "2% in 1372 DR"},
            {"race": "Elf", "share_pct": 1, "descriptor": "1% in 1372 DR"},
        ],
        "notes": [
            "A second table, given by the wiki for 1371 DR from Dungeon 144, p. 19, reads humans 67%, halflings 10%, half-elves 8%, shield dwarves 6%, moon elves 5%, rock gnomes 3%, others 1%.",
            "Neither table describes the town after it fell to Many-Arrows in 1484 DR; the 600 survivors were held prisoner and the town was a ruin in 1485 DR.",
        ],
        "era_note": (
            "Both tables come from the Nesme article's infobox on the Forgotten Realms Wiki, citing The City of Nesme (2001) and "
            "Dungeon 144 (2007); not independently consulted. Nothing describes who, if anyone, lives in Nesme in 1492 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Nesme",
            "url": WIKI + "Nesm%C3%A9",
            "accessed": "2026-10-26",
            "kind": "secondary",
        }],
    },
    "jalanthar": {
        "status": "quantified",
        "reference_period": "Circa 1372 DR (Silver Marches, 2002, p. 19); not a 1492 DR census",
        "scope": "Hamlet of Jalanthar, 226 residents, not counting the Argent Legion company stationed there",
        "groups": [
            {"race": "Human", "share_pct": 89, "descriptor": "89% circa 1372 DR"},
            {"race": "Halfling", "share_pct": 6, "descriptor": "6% circa 1372 DR",
             "subgroups": [{"name": "Lightfoot", "share_pct": 100}]},
            {"race": "Half-elf", "share_pct": 4, "descriptor": "4% circa 1372 DR"},
            {"race": "Other", "share_pct": 1, "descriptor": "1% circa 1372 DR"},
        ],
        "notes": [
            "Storm King's Thunder (2016), p. 94, as cited by the wiki, names two Damaran human residents after 1485 DR (Quinn Nardrosz and Myles Heldruin); it gives no proportions.",
        ],
        "era_note": (
            "The table comes from the Jalanthar article's infobox on the Forgotten Realms Wiki, citing Silver Marches (2002), "
            "p. 19; not independently consulted. Nothing gives the hamlet's makeup in 1492 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Jalanthar",
            "url": WIKI + "Jalanthar",
            "accessed": "2026-10-27",
            "kind": "secondary",
        }],
    },
    "everlund": {
        "status": "quantified",
        "reference_period": "As of 1372 DR (Silver Marches, 2002, pp. 74 to 78); not a 1492 DR census",
        "scope": "City of Everlund, 21,388 residents in 1372 DR",
        "groups": [
            {"race": "Human", "share_pct": 48, "descriptor": "48% in 1372 DR"},
            {"race": "Elf", "share_pct": 21, "descriptor": "21% in 1372 DR (subrace not stated)"},
            {"race": "Half-elf", "share_pct": 14, "descriptor": "14% in 1372 DR"},
            {"race": "Halfling", "share_pct": 9, "descriptor": "9% in 1372 DR",
             "subgroups": [{"name": "Lightfoot", "share_pct": 100}]},
            {"race": "Dwarf", "share_pct": 7, "descriptor": "7% in 1372 DR",
             "subgroups": [{"name": "Shield", "share_pct": 100}]},
            {"race": "Other", "share_pct": 1, "descriptor": "1% in 1372 DR"},
        ],
        "notes": [
            "Storm King's Thunder (2016), pp. 81 to 82, as cited by the wiki, names human, sun elf, shield dwarf and half-orc residents in the late 15th century DR; it gives no proportions.",
            "The same shares appear in the Silver Marches web excerpt (2002), read in a fan-site copy on 2026-10-28.",
        ],
        "era_note": (
            "The table comes from the Everlund article's infobox on the Forgotten Realms Wiki, citing Volo's Guide to the North "
            "(1993), pp. 165 to 167, and Silver Marches (2002), pp. 74 to 78; not independently consulted. Nothing gives the "
            "city's makeup in 1492 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Everlund",
            "url": WIKI + "Everlund",
            "accessed": "2026-10-28",
            "kind": "secondary",
        }, {
            "title": "Silver Marches (2002), Everlund web excerpt, fan-site copy at RealmsHelps",
            "url": "https://www.realmshelps.net/faerun/everlund.shtml",
            "accessed": "2026-10-28",
            "kind": "primary",
        }],
    },
    "mirabar": {
        "status": "quantified",
        "reference_period": "As of 1358 DR (Dwarves Deep, 1990, p. 61); 1370 DR dwarven count from The Thousand Orcs (2002); not a 1492 DR census",
        "scope": "City of Mirabar, 23,700 residents in 1358 DR, of whom 4,100 were dwarves",
        "groups": [
            {"race": "Dwarf", "share_pct": 17.3, "descriptor": "4,100 of 23,700 in 1358 DR (share computed from the two figures); about 1,600 shield dwarves in 1370 DR, before about 400 left",
             "subgroups": [{"name": "Shield", "share_pct": None}]},
            {"race": "Human", "share_pct": None, "descriptor": "Most of the rest in 1358 DR; no share stated"},
        ],
        "notes": [
            "The infobox lists humans and shield dwarves only. The Council of Sparkling Stones had 10 shield dwarves and 32 humans in 1368 DR (Volo's Guide to the North, pp. 153 to 154); that is a council, not the city.",
            "A gnome alchemist and Illuskan and Damaran humans appear among named residents; a race not named is not evidence of absence.",
            "A fan paraphrase of Storm King's Thunder (2016), p. 98, read in a deep research pass on 2026-10-29, describes the council after 1485 DR as dwarf elders and the Axe of Mirabar as all shield dwarves; that is not a population share.",
        ],
        "era_note": (
            "The 1358 DR figures come from the Mirabar article's infobox on the Forgotten Realms Wiki, citing Dwarves Deep (1990), p. 61, "
            "and the 1370 DR dwarven count from The Thousand Orcs (2002), pp. 55 and 289; not independently consulted. The 3rd edition "
            "figure of 10,307 (1372 DR) has no racial breakdown in the article. Nothing gives the city's makeup in 1492 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Mirabar",
            "url": WIKI + "Mirabar",
            "accessed": "2026-10-29",
            "kind": "secondary",
        }],
    },
    "silverymoon": {
        "status": "quantified",
        "reference_period": "Circa 1372 DR (the infobox's society reference is Silver Marches, 2002, p. 54; the year of the table is inferred from that citation); not a 1492 DR census",
        "scope": "City of Silverymoon, 37,073 residents in 1372 DR (Silver Marches, p. 54)",
        "groups": [
            {"race": "Human", "share_pct": 41, "descriptor": "41% (circa 1372 DR)"},
            {"race": "Elf", "share_pct": 29, "descriptor": "29% (circa 1372 DR; subrace not stated)"},
            {"race": "Half-elf", "share_pct": 12, "descriptor": "12% (circa 1372 DR)"},
            {"race": "Dwarf", "share_pct": 10, "descriptor": "10% (circa 1372 DR)",
             "subgroups": [{"name": "Shield", "share_pct": 100}]},
            {"race": "Halfling", "share_pct": 5, "descriptor": "5% (circa 1372 DR)",
             "subgroups": [{"name": "Lightfoot", "share_pct": 100}]},
            {"race": "Gnome", "share_pct": 2, "descriptor": "2% (circa 1372 DR)"},
            {"race": "Other", "share_pct": 1, "descriptor": "1% (circa 1372 DR)"},
        ],
        "notes": [
            "Dwarves Deep (1990), p. 61, as cited by the wiki, gives 4,200 dwarves among 29,990 residents in the late 1350s DR (about 14%).",
            "The wiki notes that Netherese descent was common, giving many residents fair skin and dark hair; that is a description, not a share.",
            "Named residents of the late 15th century DR include humans, half-elves (Methrammar Aerasume, Dlaarvos Fyredram), elves and a half-orc; a race not named is not evidence of absence.",
        ],
        "era_note": (
            "The percentage table comes from the Silverymoon article's infobox on the Forgotten Realms Wiki, whose society "
            "reference is Silver Marches (2002), p. 54; not independently consulted. Nothing gives the city's makeup in 1479 DR "
            "(about 40,000 residents) or 1492 DR."
        ),
        "sources": [{
            "title": "Forgotten Realms Wiki: Silverymoon",
            "url": WIKI + "Silverymoon",
            "accessed": "2026-10-30",
            "kind": "secondary",
        }],
    },
}
