"""Time-series helpers for the metrics dashboard."""


def diffs(xs):
    """Differences between consecutive values."""
    return [b - a for a, b in zip(xs, xs[1:])]


def cumulative(xs):
    """Running totals."""
    out, acc = [], 0
    for x in xs:
        acc += x
        out.append(acc)
    return out


def peak(xs):
    """Largest value, or None for an empty series."""
    return max(xs) if xs else None


def normalize(xs):
    """Scale to the 0..1 range (all zeros if the series is constant)."""
    lo, hi = min(xs), max(xs)
    return [0.0 if hi == lo else (x - lo) / (hi - lo) for x in xs]


def downsample(xs, step):
    """Every step-th value starting at index 0."""
    return xs[::step]


def moving_average(xs, k):
    """Average of each window of k consecutive values."""
    out = []
    for i in range(len(xs) - k):
        out.append(sum(xs[i:i + k]) / k)
    return out
