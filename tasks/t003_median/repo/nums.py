"""Numeric helpers for the data cleaning scripts.

Inputs are plain lists of ints or floats; none of these functions mutate their input.
"""


def clamp(x, lo, hi):
    """Limit x to the range [lo, hi]."""
    return max(lo, min(hi, x))


def normalize(xs):
    """Scale a list so its values sum to 1."""
    t = sum(xs)
    return [x / t for x in xs]


def running_sum(xs):
    """Cumulative sums of a list."""
    out, acc = [], 0
    for x in xs:
        acc += x
        out.append(acc)
    return out


def percentile_rank(xs, v):
    """Fraction of values in xs that are below v."""
    return sum(1 for x in xs if x < v) / len(xs)


def median(xs):
    """Middle value of a non-empty list (average of the two middle values if even length)."""
    s = sorted(xs)
    return s[len(s) // 2]
