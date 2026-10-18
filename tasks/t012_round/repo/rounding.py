"""Rounding helpers for invoices. All functions return ints unless noted."""

import math


def ceil_div(a, b):
    """Integer ceiling of a / b for positive ints."""
    return -(-a // b)


def clamp(x, lo, hi):
    """Limit x to [lo, hi]."""
    return max(lo, min(hi, x))


def to_cents(dollars):
    """Dollar float to whole cents."""
    return int(round_half_up(dollars * 100))


def floor_to(x, step):
    """Largest multiple of step that is <= x."""
    return math.floor(x / step) * step


def snap(x, step):
    """Nearest multiple of step (halves go up)."""
    return round_half_up(x / step) * step


def round_half_up(x):
    """Round to the nearest int, with exact halves going up (2.5 -> 3)."""
    return round(x)
