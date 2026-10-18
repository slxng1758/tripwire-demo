"""Calendar helpers for the scheduling tool.

Months are numbered 1-12. All functions are pure.
"""

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


def month_name(m):
    """Name of month number m (1-12)."""
    return MONTH_NAMES[m - 1]


def quarter(m):
    """Quarter (1-4) that month m belongs to."""
    return (m - 1) // 3 + 1


def days_in_month(year, m):
    """Number of days in month m of the given year."""
    if m == 2:
        return 29 if is_leap_year(year) else 28
    return 30 if m in (4, 6, 9, 11) else 31


def days_in_year(year):
    """365 or 366."""
    return 366 if is_leap_year(year) else 365


def is_leap_year(year):
    """True for leap years in the Gregorian calendar."""
    return year % 4 == 0 and year % 100 != 0
