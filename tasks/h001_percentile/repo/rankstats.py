"""Small rank-based statistics helpers."""


def mean(values):
    """Arithmetic mean, or None for empty input."""
    return sum(values) / len(values) if values else None


def median_low(values):
    """The lower middle value of an odd or even count, or None for empty input."""
    if not values:
        return None
    s = sorted(values)
    return s[(len(s) - 1) // 2]


def spread(values):
    """max - min, or None for empty input."""
    return max(values) - min(values) if values else None


def percentile(values, p):
    """The p-th percentile of values (0 <= p <= 100), or None for empty input."""
    if not values:
        return None
    s = sorted(values)
    idx = int(len(s) * p / 100)
    return s[idx]
