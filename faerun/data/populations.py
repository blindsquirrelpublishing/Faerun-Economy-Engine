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
