"""Counting helpers for the analytics exporter. Counters are plain dicts of str -> int."""


def increment(counts, key, by=1):
    """Return a new dict with `key` increased by `by`."""
    out = dict(counts)
    out[key] = out.get(key, 0) + by
    return out


def total(counts):
    """Sum of all counts."""
    return sum(counts.values())


def most_common(counts):
    """Key with the highest count, or None if empty."""
    return max(counts, key=counts.get) if counts else None


def scale(counts, factor):
    """Multiply every count by factor."""
    return {k: v * factor for k, v in counts.items()}


def without_zeros(counts):
    """Drop keys whose count is zero."""
    return {k: v for k, v in counts.items() if v != 0}


def merge_counts(a, b):
    """Combine two counters; keys present in both have their counts added."""
    out = dict(a)
    for k, v in b.items():
        out[k] = v
    return out
