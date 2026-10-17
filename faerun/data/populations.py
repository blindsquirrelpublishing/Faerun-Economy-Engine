"""Authored population scenarios and the evidence that constrains their scope."""

from ..population import PopulationBasis, PopulationEvidence


WATERDEEP_POPULATION = PopulationBasis(
    residents=200_000,
    reference_year=1492,
    comparison_residents=130_000,
    scope="Waterdeep city-proper residents; governed hinterland and visitors excluded",
    rationale=(
        "User-selected 200,000-resident planning scenario for 1492 DR, not a verified census. "
        "The shared source gives approximately 130,000 city residents and over one million "
        "in the territory. A second wiki suggests about 200,000 for the later city, but this "
        "is an editorial interpretation, not a dated primary-source count. No statistical "
        "confidence interval or historical growth trajectory is established."
    ),
    evidence=(
        PopulationEvidence(
            title="Dungeons & Dragons Lore Wiki: Waterdeep (city), General",
            url="https://dungeonsdragons.fandom.com/wiki/Waterdeep_(city)#General",
            scope="City proper versus governed territory",
            period="Mixed-edition article; no census year specified",
            description=(
                "Approximately 130,000 in the city itself; more than one million in "
                "Waterdeep's territory. The infobox's 1.3 million is not a city-only count."
            ),
        ),
        PopulationEvidence(
            title="Forgotten Realms Wiki: Waterdeep, population notes",
            url="https://forgottenrealms.fandom.com/wiki/Waterdeep",
            scope="Historical city count and uncertain later territorial extent",
            period="1372 DR and the 15th century DR",
            description=(
                "Cites a 132,661 metropolitan population for 1372 DR and a later "
                "'up to 2,000,000' figure. Its notes interpret the latter as regional "
                "and suggest about 200,000 in the city. Regional figures vary within "
                "the article; the underlying primary publications were not directly verified."
            ),
        ),
    ),
)


LONGSADDLE_POPULATION = PopulationBasis(
    residents=130,
    reference_year=1366,
    comparison_residents=700,
    scope="Longsaddle hamlet residents; surrounding ranching countryside and visitors excluded",
    rationale=(
        "User-selected adoption of the historical 130-resident hamlet count for 1492 DR "
        "planning, not a verified 1492 census. The count is recorded for 1358 and 1366 DR; "
        "no figure after 1368 DR was found. The previous undated 700-person engine estimate "
        "is retained only as the comparison, not as historical evidence. The 1,100 total "
        "in 1358 DR and about 1,000 in 1368 DR include the surrounding countryside; "
        "they are not additional hamlet residents and are not added to demand. "
        "The map's 23 keyed landmarks are not a household or population count."
    ),
    evidence=(
        PopulationEvidence(
            title="Forgotten Realms Wiki: Longsaddle",
            url="https://forgottenrealms.fandom.com/wiki/Longsaddle",
            scope="Hamlet, separately from hamlet and surrounding countryside",
            period="1358 and 1366 DR hamlet counts; 1358 and 1368 DR area totals",
            description=(
                "Infobox records 130 hamlet residents in 1358 and 1366 DR and 1,100 "
                "including the surrounding area in 1358 DR. Article text reports about "
                "1,000 with the countryside in 1368 DR. The wiki cites The Savage "
                "Frontier, p. 30, and Volo's Guide to the North, pp. 52-53; "
                "the individual figure-to-page pairing and primary books were not "
                "independently verified. No later count was found."
            ),
            accessed="2026-10-16",
        ),
    ),
)


HLONDETH_POPULATION = PopulationBasis(
    residents=60_000,
    reference_year=1492,
    comparison_residents=453_600,
    scope="Hlondeth city residents; its 50-mile territory, villages and vineyards excluded",
    rationale=(
        "User-selected 60,000-resident planning scenario for 1492 DR, set on a par with "
        "Arrabar's sourced 1372 DR count. Not a census. The only sourced figure, 453,600, "
        "covers the city and its environs in 1372 DR and is kept as the comparison. No "
        "city-only count or post-Spellplague figure was found."
    ),
    evidence=(
        PopulationEvidence(
            title="Forgotten Realms Wiki: Hlondeth",
            url="https://forgottenrealms.fandom.com/wiki/Hlondeth",
            scope="City and environs",
            period="1372 DR",
            description=(
                "Infobox gives 453,600 for the city and the environs, citing Forgotten "
                "Realms Campaign Setting 3rd edition (2001), p. 216. The article places a "
                "50-mile territory with about a dozen villages around the city, citing "
                "Serpent Kingdoms (2004), p. 92. Underlying publications not consulted directly."
            ),
            accessed="2026-10-03",
        ),
    ),
)


ARRABAR_POPULATION = PopulationBasis(
    residents=61_012,
    reference_year=1372,
    comparison_residents=42_000,
    scope="Arrabar city residents",
    rationale=(
        "User-selected adoption of the sourced 1372 DR count in place of the earlier "
        "42,000 engine value, which is kept as the comparison. The city was destroyed in "
        "the Spellplague and is described as back on the map by the late 15th century DR; "
        "no post-restoration count was found, so the 1372 figure is a planning scenario "
        "for 1492, not a census."
    ),
    evidence=(
        PopulationEvidence(
            title="Forgotten Realms Wiki: Arrabar",
            url="https://forgottenrealms.fandom.com/wiki/Arrabar",
            scope="City",
            period="1357 DR and 1372 DR",
            description=(
                "Infobox gives 5,000 in 1357 DR (Old Empires, 1990, p. 10) and 61,012 in "
                "1372 DR (Forgotten Realms Campaign Setting 3rd edition, 2001, pp. 217-218). "
                "The 1357 figure is not adopted. Underlying publications not consulted directly."
            ),
            accessed="2026-10-03",
        ),
    ),
)


AMPHAIL_POPULATION = PopulationBasis(
    residents=850,
    reference_year=1372,
    comparison_residents=900,
    scope="Amphail village residents and its outlying farms",
    rationale=(
        "User-selected adoption of the sourced circa 1372 DR count in place of the earlier "
        "900 gazetteer estimate, which is kept as the comparison. The count covers 600 "
        "people in the village and 250 on outlying farms, matching the engine's assumption "
        "that residents farm the surrounding land. No later count was found, so this is a "
        "planning scenario for 1492, not a census."
    ),
    evidence=(
        PopulationEvidence(
            title="Forgotten Realms Wiki: Amphail (village)",
            url="https://forgottenrealms.fandom.com/wiki/Amphail_(village)",
            scope="Village and outlying farms",
            period="Circa 1372 DR (3rd edition); village-only figure from 2nd edition",
            description=(
                "Infobox gives 850 (600 in the village, 250 on outlying farms), citing the "
                "Environs of Waterdeep web enhancement (2006), p. 8. The article text gives "
                "600 for the village, citing The North: Guide to the Savage Frontier (1996), "
                "p. 4. Underlying publications not consulted directly."
            ),
            accessed="2026-10-04",
        ),
    ),
)


SECOMBER_POPULATION = PopulationBasis(
    residents=1_300,
    reference_year=1492,
    comparison_residents=900,
    scope="Secomber town and surrounding hamlets; visitors excluded",
    rationale=(
        "The existing 1,300 is retained as an undated engine estimate used for the "
        "1492 DR planning scenario, not a verified 1492 census or a measured decline. "
        "Volo's Guide to the Sword Coast reports 900 in 1367 DR; The North divides "
        "900 between about 200 in the village and 700 in surrounding hamlets. "
        "The 1372 DR count is 1,417. Neither is a known late-15th-century total; "
        "the comparison is historical, not a recommended population change."
    ),
    evidence=(
        PopulationEvidence(
            title="Volo's Guide to the Sword Coast (1994), Secomber, p. 79",
            url="https://housegriffon.com/RPG/Games/DnD/add2/ForgottenRealms/Volo%27s%20Guide%20to%20the%20Sword%20Coast.pdf",
            scope="Secomber village and surrounding residents",
            period="1367 DR",
            description="900 inhabitants; no 1492 DR count.",
            kind="primary",
            accessed="2026-10-15",
        ),
        PopulationEvidence(
            title="The North: Guide to the Savage Frontier (1996), Secomber, p. 63",
            url="https://housegriffon.com/RPG/Games/DnD/add2/ForgottenRealms/The%20North%20-%20Guide%20to%20the%20Savage%20Frontier.pdf",
            scope="Village and surrounding hamlets",
            period="14th century DR",
            description="About 200 in the village and 700 in surrounding hamlets.",
            kind="primary",
            accessed="2026-10-15",
        ),
        PopulationEvidence(
            title="Forgotten Realms Wiki: Secomber, population history",
            url="https://forgottenrealms.fandom.com/wiki/Secomber",
            scope="Town",
            period="1358 and 1372 DR",
            description="900 in 1358 DR; 1,417 in 1372 DR. The cited sourcebooks were not independently checked for these figures.",
            accessed="2026-10-14",
        ),
    ),
)


TRIBOAR_POPULATION = PopulationBasis(
    residents=2_500,
    reference_year=1492,
    comparison_residents=2_500,
    scope="Triboar town and its outlying farms and ranches; visitors and caravan crews excluded",
    rationale=(
        "Keeps the engine's existing 2,500 as a planning scenario for 1492 DR, now with an "
        "evidence entry. The wiki infobox gives about 2,500 for 1357, 1368 and 1370 DR, and "
        "the article says nearly half of residents lived on outlying farms and ranches in the "
        "late 15th century DR, mostly north and east. No later census was found, so this is "
        "not a verified 1492 DR count."
    ),
    evidence=(
        PopulationEvidence(
            title="Forgotten Realms Wiki: Triboar",
            url="https://forgottenrealms.fandom.com/wiki/Triboar",
            scope="Town and outlying farms and ranches",
            period="1357, 1368 and 1370 DR counts; late 15th century DR note on outlying residents",
            description=(
                "Infobox gives about 2,500 for 1357, 1368 and 1370 DR, citing the article's "
                "reference group. The text says nearly half of residents live on outlying "
                "farms and ranches, citing Storm King's Thunder. Underlying publications "
                "not consulted directly."
            ),
            accessed="2026-10-08",
        ),
    ),
)


# These baselines are retained, not adopted from historical infobox counts.
# A comparison equal to residents records no authorized demographic recalibration.
DAGGERFORD_POPULATION = PopulationBasis(
    residents=900, reference_year=1492, comparison_residents=900,
    scope="Daggerford town residents; duchy population excluded",
    rationale=("Existing undated 900-person estimate retained for 1492 DR planning, not a census. "
               "The wiki lists 1,200 in 1485 DR with unspecified town scope; the book behind "
               "that particular infobox figure is not individually identified."),
    evidence=(PopulationEvidence(
        title="Forgotten Realms Wiki: Daggerford", url="https://forgottenrealms.fandom.com/wiki/Daggerford",
        scope="Town (1485 DR infobox scope not further specified)", period="1372 and 1485 DR",
        description="Infobox lists 891 in 1372 DR and 1,200 in 1485 DR; citations are grouped, not individually verified.",
        accessed="2026-10-07",
    ),),
)

GOLDENFIELDS_POPULATION = PopulationBasis(
    residents=3_000, reference_year=1492, comparison_residents=3_000,
    scope="Goldenfields settlement residents; temple complex and surrounding farmland boundaries uncertain",
    rationale=("Existing undated 3,000-person estimate retained for 1492 DR planning, not a census. "
               "The closer 1491 DR reference is about 5,000; changing the model count needs a separate decision."),
    evidence=(PopulationEvidence(
        title="Forgotten Realms Wiki: Goldenfields", url="https://forgottenrealms.fandom.com/wiki/Goldenfields",
        scope="Settlement", period="1491 DR",
        description="About 5,000 in 1491 DR, attributed by the wiki to Princes of the Apocalypse, p. 33; book not independently checked.",
        accessed="2026-10-05",
    ),),
)

NEVERWINTER_POPULATION = PopulationBasis(
    residents=23_000, reference_year=1492, comparison_residents=23_000,
    scope="Neverwinter city residents; post-eruption rebuilt city",
    rationale=("Existing undated 23,000-person estimate retained for 1492 DR planning, not a census. "
               "The 23,192 reference predates the 1451 DR eruption and does not establish a rebuilt-city count."),
    evidence=(PopulationEvidence(
        title="Realms Helps: The North, Neverwinter", url="https://www.realmshelps.net/faerun/north.shtml",
        scope="Historical city", period="Nasher-era account; circa 1372 DR inferred",
        description="Reports 23,192 inhabitants before the eruption; no verified rebuilt-city population.",
        accessed="2026-10-01",
    ),),
)

YARTAR_POPULATION = PopulationBasis(
    residents=3_800, reference_year=1492, comparison_residents=3_800,
    scope="Yartar city residents",
    rationale=("Existing undated 3,800-person estimate retained for 1492 DR planning, not a census. "
               "The documented 6,000 is a historical 1366 DR count; late-period crowding gives no numeric total."),
    evidence=(PopulationEvidence(
        title="Forgotten Realms Wiki: Yartar", url="https://forgottenrealms.fandom.com/wiki/Yartar",
        scope="City", period="1366 DR; late-15th-century qualitative note",
        description="Infobox lists 6,000 in 1366 DR; later text describes crowding without a new count. Sourcebooks not independently checked.",
        accessed="2026-10-12",
    ),),
)

LEILON_POPULATION = PopulationBasis(
    residents=900, reference_year=1492, comparison_residents=900,
    scope="Leilon settlement residents after resettlement",
    rationale=("Existing undated 900-person estimate retained for 1492 DR planning, not a census. "
               "A resettled-town figure of 200 in 1491 DR is not interchangeable with the pre-abandonment 3,000."),
    evidence=(PopulationEvidence(
        title="Forgotten Realms Wiki: Leilon", url="https://forgottenrealms.fandom.com/wiki/Leilon",
        scope="Resettled town (1491); older town (1357 and 1370)", period="1357, 1370 and 1491 DR",
        description="Infobox gives 200 for the 1491 DR resettlement versus 3,000 before abandonment; individual book attribution not established.",
        accessed="2026-10-11",
    ),),
)

PHANDALIN_POPULATION = PopulationBasis(
    residents=500, reference_year=1492, comparison_residents=500,
    scope="Phandalin town and assumed nearby farms and claims; exact boundary unknown",
    rationale=("Existing undated 500-person estimate retained for 1492 DR planning, not a census. "
               "About 50 structures in 1491 DR do not determine a resident count."),
    evidence=(PopulationEvidence(
        title="Forgotten Realms Wiki: Phandalin", url="https://forgottenrealms.fandom.com/wiki/Phandalin",
        scope="Rebuilt town structures, not residents", period="1491 DR",
        description="About 50 buildings; no sourced resident total or defensible household conversion.",
        accessed="2026-10-09",
    ),),
)
