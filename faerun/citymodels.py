"""Historical directory records, deliberately independent of market actors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Citation:
    printed_page: int
    pdf_page: int
    source_id: str = "volos_guide_to_waterdeep"


@dataclass(frozen=True)
class HistoricalBusiness:
    id: str
    name: str
    ward: str
    category: str
    services: tuple[str, ...]
    summary: str
    citations: tuple[Citation, ...]
    address: str | None = None


@dataclass(frozen=True)
class Affiliation:
    business_id: str
    role: str
    citations: tuple[Citation, ...]


@dataclass(frozen=True)
class HistoricalPerson:
    id: str
    name: str
    summary: str
    citations: tuple[Citation, ...]
    affiliations: tuple[Affiliation, ...]
