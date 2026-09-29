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


def test_calendar_tracks_lunar_phases_in_order():
    new_moon = HarptosDate(1492, 1, 1)
    waxing_crescent = new_moon.add_days(4)
    first_quarter = new_moon.add_days(7)
    waxing_gibbous = new_moon.add_days(11)
    full_moon = new_moon.add_days(14)
    waning_gibbous = new_moon.add_days(18)
    last_quarter = new_moon.add_days(22)
    waning_crescent = new_moon.add_days(25)

    assert new_moon.moon_phase == "Moonless Night"
    assert waxing_crescent.moon_phase == "Silver Sliver"
    assert first_quarter.moon_phase == "Moonrise"
    assert waxing_gibbous.moon_phase == "Silver Wake"
    assert full_moon.moon_phase == "Full Silver"
    assert waning_gibbous.moon_phase == "Silver Fade"
    assert last_quarter.moon_phase == "Moonfall"
    assert waning_crescent.moon_phase == "Dimming Halo"


def test_explicit_date_disables_real_date_tracking():
    world = World(date=HarptosDate(1492, 2, 10))
    assert not world.follows_real_date
    assert not world.sync_real_date()
    assert world.date == HarptosDate(1492, 2, 10)
