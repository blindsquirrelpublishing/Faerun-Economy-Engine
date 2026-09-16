"""The Calendar of Harptos, used to drive seasonality in the market engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone

MONTHS = [
    ("Hammer", "Deepwinter", "winter"),
    ("Alturiak", "The Claw of Winter", "winter"),
    ("Ches", "The Claw of the Sunsets", "spring"),
    ("Tarsakh", "The Claw of the Storms", "spring"),
    ("Mirtul", "The Melting", "spring"),
    ("Kythorn", "The Time of Flowers", "summer"),
    ("Flamerule", "Summertide", "summer"),
    ("Eleasis", "Highsun", "summer"),
    ("Eleint", "The Fading", "autumn"),
    ("Marpenoth", "Leaffall", "autumn"),
    ("Uktar", "The Rotting", "autumn"),
    ("Nightal", "The Drawing Down", "winter"),
]

FESTIVALS = {
    1: "Midwinter (after Hammer)",
    4: "Greengrass (after Tarsakh)",
    7: "Midsummer (after Flamerule)",
    9: "Highharvestide (after Eleint)",
    11: "The Feast of the Moon (after Uktar)",
}

REAL_DATE_EPOCH = date(2026, 1, 1)
HARPTOS_EPOCH_YEAR = 1492
HARPTOS_DAYS_PER_YEAR = 365
FESTIVAL_MONTHS = frozenset(FESTIVALS)

MONTH_INDEX = {name.lower(): i + 1 for i, (name, _, _) in enumerate(MONTHS)}
MONTH_INDEX.update({common.lower(): i + 1 for i, (_, common, _) in enumerate(MONTHS)})


def season_of(month: int) -> str:
    """Return the season name for a month number (1-12)."""
    return MONTHS[(int(month) - 1) % 12][2]


def month_name(month: int) -> str:
    return MONTHS[(int(month) - 1) % 12][0]


def parse_month(value) -> int:
    """Accept a month number, Harptos month name or common name."""
    if value is None:
        return 0
    if isinstance(value, int):
        return ((value - 1) % 12) + 1
    text = str(value).strip().lower()
    if text.isdigit():
        return ((int(text) - 1) % 12) + 1
    if text in MONTH_INDEX:
        return MONTH_INDEX[text]
    for key, idx in MONTH_INDEX.items():
        if key.startswith(text):
            return idx
    raise ValueError(f"Unknown Harptos month: {value!r}")


@dataclass(frozen=True)
class HarptosDate:
    """A date in the Calendar of Harptos (Dalereckoning)."""

    year: int = 1492
    month: int = 1
    day: int = 1

    def __post_init__(self) -> None:
        if not 1 <= self.month <= 12:
            raise ValueError("Harptos month must be between 1 and 12")
        max_day = 31 if self.month in FESTIVAL_MONTHS else 30
        if not 1 <= self.day <= max_day:
            raise ValueError(
                f"{month_name(self.month)} has days 1 through {max_day}"
            )

    @classmethod
    def from_gregorian(cls, value: date) -> "HarptosDate":
        """Convert a civil date using 1 January 2026 = 1 Hammer 1492 DR."""
        elapsed = (value - REAL_DATE_EPOCH).days
        year_delta, day_of_year = divmod(elapsed, HARPTOS_DAYS_PER_YEAR)
        year = HARPTOS_EPOCH_YEAR + year_delta

        for month in range(1, 13):
            if day_of_year < 30:
                return cls(year, month, day_of_year + 1)
            day_of_year -= 30
            if month in FESTIVAL_MONTHS:
                if day_of_year == 0:
                    return cls(year, month, 31)
                day_of_year -= 1
        raise AssertionError("Harptos day conversion exceeded one year")

    @classmethod
    def today(cls) -> "HarptosDate":
        """Return today's Harptos date, using the current UTC civil date."""
        return cls.from_gregorian(datetime.now(timezone.utc).date())

    @classmethod
    def parse(cls, text: str) -> "HarptosDate":
        """Parse strings such as '15 Kythorn 1492 DR' or '1492-06-15'."""
        raw = str(text).replace("DR", "").replace(",", "").strip()
        if "-" in raw and raw.replace("-", "").isdigit():
            parts = [int(p) for p in raw.split("-")]
            while len(parts) < 3:
                parts.append(1)
            return cls(parts[0], ((parts[1] - 1) % 12) + 1, parts[2])
        tokens = raw.split()
        day, month, year = 1, 6, 1492
        for token in tokens:
            if token.isdigit():
                number = int(token)
                if number > 40:
                    year = number
                else:
                    day = number
            else:
                try:
                    month = parse_month(token)
                except ValueError:
                    continue
        return cls(year, month, day)

    @property
    def season(self) -> str:
        return season_of(self.month)

    @property
    def month_name(self) -> str:
        return month_name(self.month)

    @property
    def month_common_name(self) -> str:
        return MONTHS[(self.month - 1) % 12][1]

    @property
    def festival(self) -> str | None:
        return FESTIVALS.get(self.month) if self.day == 31 else None

    def absolute_month(self) -> int:
        """A monotonically increasing month counter, useful for seeding noise."""
        return self.year * 12 + self.month

    def absolute_day(self) -> int:
        """A monotonically increasing day counter for caches and daily prices."""
        days = (self.year * HARPTOS_DAYS_PER_YEAR
                + (self.month - 1) * 30
                + self.day - 1)
        days += sum(1 for month in FESTIVAL_MONTHS if month < self.month)
        return days

    @classmethod
    def from_absolute_day(cls, absolute_day: int) -> "HarptosDate":
        if isinstance(absolute_day, bool) or not isinstance(absolute_day, int):
            raise ValueError("Absolute Harptos day must be an integer")
        year, offset = divmod(absolute_day, HARPTOS_DAYS_PER_YEAR)
        for month in range(1, 13):
            length = 31 if month in FESTIVAL_MONTHS else 30
            if offset < length:
                return cls(year, month, offset + 1)
            offset -= length
        raise AssertionError("Harptos day conversion exceeded one year")

    def add_days(self, days: int = 1) -> "HarptosDate":
        return self.from_absolute_day(self.absolute_day() + days)

    def advance(self, months: int = 1) -> "HarptosDate":
        total = (self.year * 12 + (self.month - 1)) + months
        month = (total % 12) + 1
        day = self.day if self.day <= 30 or month in FESTIVAL_MONTHS else 30
        return HarptosDate(total // 12, month, day)

    def __str__(self) -> str:  # pragma: no cover - display helper
        if self.festival:
            return f"{self.festival.split(' (', 1)[0]}, {self.year} DR"
        return f"{self.day} {self.month_name} {self.year} DR"
