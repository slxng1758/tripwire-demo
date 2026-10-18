"""Billing helpers. All amounts are integer cents."""


def to_cents(dollars):
    """Convert a dollar amount to integer cents."""
    return round(dollars * 100)


def fmt(cents):
    """Format cents as a dollar string."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"


def add_tax(cents, rate):
    """Cents plus tax, rounded to the nearest cent."""
    return cents + round(cents * rate)


def split_evenly(total, n):
    """Split total cents into n parts that add up to the total."""
    if n <= 0:
        raise ValueError("n must be positive")
    return [total // n] * n
