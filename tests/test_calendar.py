"""Real-world anchoring for the Calendar of Harptos."""

from datetime import date

from faerun.calendar import HarptosDate
from faerun.economy import price_for
from faerun.world import World


def test_real_date_epoch_begins_hammer_1492():
    assert HarptosDate.from_gregorian(date(2026, 1, 1)) == HarptosDate(1492, 1, 1)


def test_current_reference_date_maps_to_eleint():
    assert HarptosDate.from_gregorian(date(2026, 9, 13)) == HarptosDate(1492, 9, 13)


def test_festival_days_are_part_of_daily_conversion():
    midwinter = HarptosDate.from_gregorian(date(2026, 1, 31))
    assert str(midwinter) == "Midwinter, 1492 DR"
    assert midwinter.festival == "Midwinter (after Hammer)"
    assert HarptosDate.from_gregorian(date(2026, 2, 1)) == HarptosDate(1492, 2, 1)


def test_year_rolls_after_365_days():
    assert HarptosDate.from_gregorian(date(2027, 1, 1)) == HarptosDate(1493, 1, 1)


def test_daily_date_changes_market_prices():
    first = World(date=HarptosDate(1492, 9, 13))
    second = World(date=HarptosDate(1492, 9, 14))

    first_price = price_for("Waterdeep", "grain", world=first).price
    second_price = price_for("Waterdeep", "grain", world=second).price

    assert first.economy_state_key() != second.economy_state_key()
    assert first_price != second_price


def test_explicit_date_disables_real_date_tracking():
    world = World(date=HarptosDate(1492, 2, 10))
    assert not world.follows_real_date
    assert not world.sync_real_date()
    assert world.date == HarptosDate(1492, 2, 10)
