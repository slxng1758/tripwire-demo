"""Time slot helpers. A slot is a (start, end) pair with start < end."""


def duration(slot):
    """Length of a slot."""
    return slot[1] - slot[0]


def contains(slot, t):
    """True if moment t is inside the slot."""
    return slot[0] <= t < slot[1]


def shift(slot, by):
    """Slot moved later by `by`."""
    return (slot[0] + by, slot[1] + by)


def total_booked(slots):
    """Sum of durations (assumes the slots do not overlap)."""
    return sum(duration(s) for s in slots)


def overlaps(a, b):
    """True if the two slots overlap."""
    return a[0] < b[0] < a[1]
