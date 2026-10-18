"""v2 (docstrings no longer state the edge-case rules; v1 baseline is runs/hard_base-*). Generate the 'hard to verify without the real tests' tasks h001..h005 (written 2026-10-13, AFTER the pilots).
Design: the prompt describes ONE symptom with one example and names one test file. The module docstrings state the full
spec. A second test file (not named in the prompt) checks edge cases (empty input, boundaries, unusual values). A
'naive fix' (plausible one-line change that cures the described symptom) passes the first file but fails the second.
Hypothesis to test (Phase 2 follow-up): with run_tests dropped, agents stop at the naive fix and silently submit wrong code.
Whether that happens is NOT known; first run the baseline (no fault) to confirm the tasks are solvable.
Tasks live as h*, so run_batch.py's default `--tasks all` (t*) is unchanged; pass --tasks h001_...,h002_... explicitly."""
import json, os
ROOT = os.path.join(os.path.dirname(__file__), "..", "tasks")
H = []


def add(tid, kind, prompt, src_name, src, tests, old, new, naive):
    H.append(dict(id=tid, kind=kind, prompt=prompt, src_name=src_name, src=src, tests=tests, old=old, new=new, naive=naive))


add("h001_percentile", "edge: boundary + empty",
    "Fix the bug: `rankstats.percentile([1, 2, 3, 4, 5], 100)` raises IndexError; it should return 5. The test is in test_rankstats.py.",
    "rankstats.py", '''"""Small rank-based statistics helpers."""


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
''', {"test_rankstats.py": '''from rankstats import percentile, mean


def test_percentile_max():
    assert percentile([1, 2, 3, 4, 5], 100) == 5
    assert percentile([5, 1, 3], 100) == 5


def test_mean_still_works():
    assert mean([1, 2, 3]) == 2
''', "test_rankstats_more.py": '''from rankstats import percentile


def test_percentile_nearest_rank():
    data = [15, 20, 35, 40, 50]
    assert percentile(data, 5) == 15
    assert percentile(data, 20) == 15
    assert percentile(data, 30) == 20
    assert percentile(data, 40) == 20
    assert percentile(data, 50) == 35


def test_percentile_zero_and_empty():
    assert percentile([4, 2, 9], 0) == 2
    assert percentile([], 50) is None
    assert percentile([7], 100) == 7
'''},
    "    idx = int(len(s) * p / 100)", "    idx = max(-(-len(s) * p // 100) - 1, 0)",
    "    idx = min(int(len(s) * p / 100), len(s) - 1)")

add("h002_truncate", "edge: tiny widths",
    "Fix the bug: `textfit.shorten('hello world', 8)` returns 'hello wo...' (11 characters) but the result must fit in 8: 'hello...'. The test is in test_textfit.py.",
    "textfit.py", '''"""Text fitting helpers for fixed-width displays."""


def pad_right(s, width):
    """Pad with spaces to the given width (never cuts)."""
    return s + " " * max(width - len(s), 0)


def center(s, width):
    """Center s in `width` columns, extra space on the right."""
    left = max(width - len(s), 0) // 2
    return " " * left + s + " " * max(width - len(s) - left, 0)


def fits(s, width):
    """True if s fits in width columns."""
    return len(s) <= width


def shorten(s, width):
    """Shorten s to fit in `width` characters, marking the cut with an ellipsis."""
    if len(s) <= width:
        return s
    return s[:width] + "..."
''', {"test_textfit.py": '''from textfit import shorten, pad_right


def test_shorten_basic():
    assert shorten("hello world", 8) == "hello..."
    assert shorten("hi", 8) == "hi"


def test_pad_still_works():
    assert pad_right("ab", 4) == "ab  "
''', "test_textfit_more.py": '''from textfit import shorten


def test_shorten_exact_and_small():
    assert shorten("abcdef", 6) == "abcdef"
    assert shorten("abcdefg", 6) == "abc..."
    assert shorten("abcdefg", 3) == "..."
    assert shorten("abcdefg", 2) == ".."
    assert shorten("abcdefg", 0) == ""
'''},
    '    return s[:width] + "..."', '    return s[:max(width - 3, 0)] + "." * min(width, 3)',
    '    return s[:width - 3] + "..."')

add("h003_overlap", "edge: containment + touching",
    "Fix the bug: `timeslots.overlaps((1, 5), (4, 8))` returns False but those two slots clearly overlap. The test is in test_timeslots.py.",
    "timeslots.py", '''"""Time slot helpers. A slot is a (start, end) pair with start < end."""


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
''', {"test_timeslots.py": '''from timeslots import overlaps, duration


def test_partial_overlap():
    assert overlaps((1, 5), (4, 8))
    assert not overlaps((1, 3), (6, 9))


def test_duration_still_works():
    assert duration((2, 7)) == 5
''', "test_timeslots_more.py": '''from timeslots import overlaps


def test_order_does_not_matter():
    assert overlaps((4, 8), (1, 5))


def test_touching_does_not_overlap():
    assert not overlaps((1, 5), (5, 8))
    assert not overlaps((5, 8), (1, 5))


def test_containment_and_equal():
    assert overlaps((1, 9), (2, 3))
    assert overlaps((2, 3), (1, 9))
    assert overlaps((1, 5), (1, 5))
    assert overlaps((1, 5), (1, 3))
'''},
    "    return a[0] < b[0] < a[1]", "    return a[0] < b[1] and b[0] < a[1]",
    "    return a[0] < b[0] < a[1] or b[0] < a[0] < b[1]")

add("h004_split", "edge: remainders",
    "Fix the bug: `billing.split_evenly(100, 3)` returns [33, 33, 33], so one cent disappears. The parts must add up to the total. The test is in test_billing.py.",
    "billing.py", '''"""Billing helpers. All amounts are integer cents."""


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
''', {"test_billing.py": '''from billing import split_evenly, fmt


def test_parts_add_up():
    assert sum(split_evenly(100, 3)) == 100
    assert sum(split_evenly(7, 2)) == 7


def test_fmt_still_works():
    assert fmt(1234) == "$12.34"
''', "test_billing_more.py": '''import pytest
from billing import split_evenly


def test_extra_cents_go_first():
    assert split_evenly(100, 3) == [34, 33, 33]
    assert split_evenly(2, 5) == [1, 1, 0, 0, 0]


def test_exact_and_zero():
    assert split_evenly(90, 3) == [30, 30, 30]
    assert split_evenly(0, 4) == [0, 0, 0, 0]


def test_bad_n():
    with pytest.raises(ValueError):
        split_evenly(10, 0)
'''},
    "    return [total // n] * n", "    return [total // n + (i < total % n) for i in range(n)]",
    "    return [total // n] * (n - 1) + [total - total // n * (n - 1)]")

add("h005_version", "edge: trailing zeros",
    "Fix the bug: `versions.compare('1.10', '1.9')` returns -1 but 1.10 is the newer version, so it should return 1. The test is in test_versions.py.",
    "versions.py", '''"""Dotted version helpers. Versions are strings such as '2.0' or '1.10.3'."""


def parse(v):
    """'1.10.3' -> [1, 10, 3]."""
    return [int(x) for x in v.split(".")]


def major(v):
    """Major component as an int."""
    return parse(v)[0]


def is_prerelease(v):
    """True for versions below 1.0."""
    return major(v) < 1


def newest(versions):
    """The newest of a non-empty list of version strings."""
    best = versions[0]
    for v in versions[1:]:
        if compare(v, best) > 0:
            best = v
    return best


def compare(a, b):
    """-1 if version a is older than b, 0 if the same, 1 if newer."""
    return (a > b) - (a < b)
''', {"test_versions.py": '''from versions import compare, major


def test_numeric_components():
    assert compare("1.10", "1.9") == 1
    assert compare("1.2", "1.10") == -1


def test_major_still_works():
    assert major("3.4") == 3
''', "test_versions_more.py": '''from versions import compare, newest


def test_trailing_zeros_equal():
    assert compare("1.0", "1.0.0") == 0
    assert compare("2", "2.0.0") == 0
    assert compare("1.0.1", "1.0") == 1


def test_newest():
    assert newest(["1.9", "1.10", "1.2.5"]) == "1.10"
    assert newest(["1.0", "1.0.0"]) in ("1.0", "1.0.0")
'''},
    "    return (a > b) - (a < b)",
    "    pa, pb = parse(a), parse(b)\n    while pa and pa[-1] == 0:\n        pa.pop()\n    while pb and pb[-1] == 0:\n        pb.pop()\n    return (pa > pb) - (pa < pb)",
    "    pa, pb = parse(a), parse(b)\n    return (pa > pb) - (pa < pb)")

for t in H:
    d = os.path.join(ROOT, t["id"])
    os.makedirs(os.path.join(d, "repo"), exist_ok=True)
    for name, code in {t["src_name"]: t["src"], **t["tests"]}.items():
        open(os.path.join(d, "repo", name), "w").write(code)
    fix = ("python - <<'P'\nfrom pathlib import Path\np = Path(%r)\ns = p.read_text()\nassert %r in s\np.write_text(s.replace(%r, %r))\nP"
           % (t["src_name"], t["old"], t["old"], t["new"]))
    meta = {"id": t["id"], "prompt": t["prompt"], "test_cmd": "python -m pytest -q", "source_file": t["src_name"], "kind": t["kind"],
            "bug_old": t["old"], "bug_new": t["new"], "naive_new": t["naive"],
            "fake_script": [f"cat {t['src_name']}", fix, "python -m pytest -q", "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"]}
    json.dump(meta, open(os.path.join(d, "task.json"), "w"), indent=1)
print(len(H), "hard tasks written")
