"""Leaderboard helpers for the quiz app. Scores are (name, points) pairs."""


def total_points(scores):
    """Sum of all points."""
    return sum(p for _, p in scores)


def average(scores):
    """Mean points (0.0 for no scores)."""
    return total_points(scores) / len(scores) if scores else 0.0


def names(scores):
    """Player names in input order."""
    return [n for n, _ in scores]


def rank_of(scores, name):
    """1-based rank of a player by points (1 = best), or None if absent."""
    ordered = sorted(scores, key=lambda s: s[1], reverse=True)
    for i, (n, _) in enumerate(ordered, start=1):
        if n == name:
            return i
    return None


def top_n(scores, n):
    """The n highest-scoring entries, best first."""
    return sorted(scores, key=lambda s: s[1])[:n]
