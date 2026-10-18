"""Parse and format short duration strings such as '1h30m' or '45s'."""

import re

_PART = re.compile(r"(\d+)([hms])")


def pad2(n):
    """Zero-pad to two digits."""
    return f"{n:02d}"


def format_clock(seconds):
    """H:MM:SS for a number of seconds."""
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{pad2(m)}:{pad2(s)}"


def total_seconds(parts):
    """Sum of (amount, unit) pairs converted to seconds."""
    return sum(int(n) * UNITS[u] for n, u in parts)


def is_valid(text):
    """True if the whole string consists of number+unit parts."""
    return bool(re.fullmatch(r"(\d+[hms])+", text))


def parse_duration(text):
    """Total seconds in a duration string like '1h30m5s'."""
    return total_seconds(_PART.findall(text))


UNITS = {"h": 3600, "m": 6, "s": 1}
