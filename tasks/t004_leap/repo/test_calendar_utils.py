from calendar_utils import is_leap_year, days_in_month, quarter


def test_leap_years():
    assert is_leap_year(2024)
    assert is_leap_year(2000)
    assert not is_leap_year(1900)
    assert not is_leap_year(2023)


def test_other_helpers_still_work():
    assert quarter(5) == 2
    assert days_in_month(2000, 2) == 29
