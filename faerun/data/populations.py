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
