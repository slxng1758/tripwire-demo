"""Generate tasks t004..t020. Each task: a small Python module with ONE planted bug placed in the
later part of the file (so a half-truncated read hides it), plus tests that fail before the fix.
Bug kinds are varied on purpose. Code is original, written for this study."""
import json, os, textwrap
ROOT = os.path.join(os.path.dirname(__file__), "..", "tasks")

T = []  # (id, prompt, {filename: code}, tests{filename: code}, bug_file, (old, new))

def add(tid, kind, prompt, files, tests, bug_file, old, new):
    T.append(dict(id=tid, kind=kind, prompt=prompt, files=files, tests=tests, bug_file=bug_file, old=old, new=new))

add("t004_leap", "wrong condition",
 "Fix the bug: `calendar_utils.is_leap_year` gives wrong answers for some years. The failing test is in test_calendar_utils.py.",
 {"calendar_utils.py": '''"""Calendar helpers for the scheduling tool.

Months are numbered 1-12. All functions are pure.
"""

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


def month_name(m):
    """Name of month number m (1-12)."""
    return MONTH_NAMES[m - 1]


def quarter(m):
    """Quarter (1-4) that month m belongs to."""
    return (m - 1) // 3 + 1


def days_in_month(year, m):
    """Number of days in month m of the given year."""
    if m == 2:
        return 29 if is_leap_year(year) else 28
    return 30 if m in (4, 6, 9, 11) else 31


def days_in_year(year):
    """365 or 366."""
    return 366 if is_leap_year(year) else 365


def is_leap_year(year):
    """True for leap years in the Gregorian calendar."""
    return year % 4 == 0 and year % 100 != 0
'''},
 {"test_calendar_utils.py": '''from calendar_utils import is_leap_year, days_in_month, quarter


def test_leap_years():
    assert is_leap_year(2024)
    assert is_leap_year(2000)
    assert not is_leap_year(1900)
    assert not is_leap_year(2023)


def test_other_helpers_still_work():
    assert quarter(5) == 2
    assert days_in_month(2000, 2) == 29
'''}, "calendar_utils.py",
 "return year % 4 == 0 and year % 100 != 0", "return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)")

add("t005_paginate", "off-by-one",
 "Fix the bug: `listing.paginate` returns the wrong slice of items. The failing test is in test_listing.py.",
 {"listing.py": '''"""Helpers for building list views in the admin screens."""


def sort_by_name(rows):
    """Rows sorted by their 'name' field, case-insensitively."""
    return sorted(rows, key=lambda r: r["name"].lower())


def filter_active(rows):
    """Only rows whose 'active' flag is true."""
    return [r for r in rows if r.get("active")]


def count_pages(total, size):
    """How many pages are needed for `total` items at `size` per page."""
    return (total + size - 1) // size


def page_label(page, pages):
    """Human readable page indicator like 'Page 2 of 5'."""
    return f"Page {page} of {pages}"


def has_next(page, total, size):
    """True when a page after `page` exists (pages are numbered from 1)."""
    return page < count_pages(total, size)


def paginate(items, page, size):
    """Items on the given page. Pages are numbered from 1."""
    start = page * size
    return items[start:start + size]
'''},
 {"test_listing.py": '''from listing import paginate, count_pages, has_next


def test_first_and_later_pages():
    items = list(range(1, 11))
    assert paginate(items, 1, 4) == [1, 2, 3, 4]
    assert paginate(items, 3, 4) == [9, 10]


def test_helpers_still_work():
    assert count_pages(10, 4) == 3
    assert has_next(1, 10, 4)
'''}, "listing.py", "start = page * size", "start = (page - 1) * size")

add("t006_wordcount", "string handling",
 "Fix the bug: `textstats.word_count` miscounts words when the text has extra spaces or newlines. The failing test is in test_textstats.py.",
 {"textstats.py": '''"""Tiny text statistics used by the editor sidebar."""


def char_count(text):
    """Number of characters excluding newlines."""
    return len(text.replace("\\n", ""))


def line_count(text):
    """Number of lines (an empty text has zero lines)."""
    return len(text.splitlines())


def longest_line(text):
    """The longest line, or an empty string for empty text."""
    lines = text.splitlines()
    return max(lines, key=len) if lines else ""


def average_line_length(text):
    """Mean characters per line (0.0 for empty text)."""
    lines = text.splitlines()
    return sum(len(l) for l in lines) / len(lines) if lines else 0.0


def sentence_count(text):
    """Rough count of sentences ending in . ! or ?"""
    return sum(text.count(c) for c in ".!?")


def word_count(text):
    """Number of words separated by any whitespace."""
    return len(text.split(" "))
'''},
 {"test_textstats.py": '''from textstats import word_count, line_count


def test_word_count_whitespace():
    assert word_count("one  two\\nthree") == 3
    assert word_count("  padded  ") == 1
    assert word_count("") == 0


def test_line_count_still_works():
    assert line_count("a\\nb") == 2
'''}, "textstats.py", 'return len(text.split(" "))', "return len(text.split())")

add("t007_interest", "math",
 "Fix the bug: `finance.compound_balance` returns the wrong balance. The failing test is in test_finance.py.",
 {"finance.py": '''"""Small finance helpers for the savings calculator."""


def percent(part, whole):
    """part as a percentage of whole (0.0 if whole is zero)."""
    return 100.0 * part / whole if whole else 0.0


def simple_interest(principal, rate, years):
    """Interest earned with no compounding. rate is a fraction (0.05 = 5%)."""
    return principal * rate * years


def monthly_payment(principal, annual_rate, months):
    """Level monthly payment for a loan (zero-interest loans split evenly)."""
    if annual_rate == 0:
        return principal / months
    r = annual_rate / 12
    return principal * r / (1 - (1 + r) ** -months)


def rule_of_72(rate_percent):
    """Approximate years to double at the given percent rate."""
    return 72 / rate_percent


def future_value_annuity(payment, rate, periods):
    """Future value of equal payments made at the end of each period."""
    return payment * (((1 + rate) ** periods - 1) / rate)


def compound_balance(principal, rate, years):
    """Balance after compounding once per year. rate is a fraction."""
    return principal * (1 + rate * years)
'''},
 {"test_finance.py": '''from finance import compound_balance, simple_interest


def test_compound_balance():
    assert abs(compound_balance(1000, 0.05, 2) - 1102.5) < 1e-9
    assert abs(compound_balance(200, 0.1, 3) - 266.2) < 1e-9


def test_simple_interest_still_works():
    assert simple_interest(1000, 0.05, 2) == 100.0
'''}, "finance.py", "return principal * (1 + rate * years)", "return principal * (1 + rate) ** years")

add("t008_logbuf", "mutable default",
 "Fix the bug: `logbuf.record` leaks entries between unrelated callers. The failing test is in test_logbuf.py.",
 {"logbuf.py": '''"""A minimal in-memory log buffer used by the CLI tools."""

LEVELS = ("debug", "info", "warn", "error")


def level_rank(level):
    """Numeric rank of a level name (debug=0 ... error=3)."""
    return LEVELS.index(level)


def format_entry(level, message):
    """Render one entry as '[LEVEL] message'."""
    return f"[{level.upper()}] {message}"


def at_least(entries, level):
    """Entries (level, message) at or above the given level."""
    return [e for e in entries if level_rank(e[0]) >= level_rank(level)]


def render(entries):
    """All entries rendered, one per line."""
    return "\\n".join(format_entry(l, m) for l, m in entries)


def record(level, message, buffer=[]):
    """Append an entry to `buffer` and return the buffer. A new empty buffer is used when none is given."""
    buffer.append((level, message))
    return buffer
'''},
 {"test_logbuf.py": '''from logbuf import record, render


def test_separate_buffers():
    a = record("info", "first")
    b = record("warn", "second")
    assert a == [("info", "first")]
    assert b == [("warn", "second")]


def test_existing_buffer_is_extended():
    buf = []
    record("info", "x", buf)
    record("error", "y", buf)
    assert render(buf) == "[INFO] x\\n[ERROR] y"
'''}, "logbuf.py", "def record(level, message, buffer=[]):\n    \"\"\"Append an entry to `buffer` and return the buffer. A new empty buffer is used when none is given.\"\"\"\n    buffer.append((level, message))",
 "def record(level, message, buffer=None):\n    \"\"\"Append an entry to `buffer` and return the buffer. A new empty buffer is used when none is given.\"\"\"\n    if buffer is None:\n        buffer = []\n    buffer.append((level, message))")

add("t009_topn", "wrong ordering",
 "Fix the bug: `leaderboard.top_n` does not return the highest scores. The failing test is in test_leaderboard.py.",
 {"leaderboard.py": '''"""Leaderboard helpers for the quiz app. Scores are (name, points) pairs."""


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
'''},
 {"test_leaderboard.py": '''from leaderboard import top_n, rank_of


def test_top_n():
    s = [("a", 5), ("b", 9), ("c", 7), ("d", 1)]
    assert top_n(s, 2) == [("b", 9), ("c", 7)]


def test_rank_still_works():
    assert rank_of([("a", 5), ("b", 9)], "a") == 2
'''}, "leaderboard.py", "return sorted(scores, key=lambda s: s[1])[:n]", "return sorted(scores, key=lambda s: s[1], reverse=True)[:n]")

add("t010_merge", "logic",
 "Fix the bug: `counters.merge_counts` loses counts. The failing test is in test_counters.py.",
 {"counters.py": '''"""Counting helpers for the analytics exporter. Counters are plain dicts of str -> int."""


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
'''},
 {"test_counters.py": '''from counters import merge_counts, total


def test_merge_adds_shared_keys():
    assert merge_counts({"a": 1, "b": 2}, {"b": 5, "c": 1}) == {"a": 1, "b": 7, "c": 1}


def test_inputs_not_mutated_and_total_works():
    a = {"x": 1}
    merge_counts(a, {"x": 2})
    assert a == {"x": 1}
    assert total({"x": 2, "y": 3}) == 5
'''}, "counters.py", "        out[k] = v\n    return out", "        out[k] = out.get(k, 0) + v\n    return out")

add("t011_snake", "string handling",
 "Fix the bug: `naming.camel_to_snake` produces names with a stray leading underscore. The failing test is in test_naming.py.",
 {"naming.py": '''"""Identifier naming helpers for the code generator."""


def is_snake(name):
    """True if name is lower-case words joined by single underscores."""
    return name == name.lower() and "__" not in name and not name.startswith("_")


def snake_to_camel(name):
    """userName from user_name."""
    first, *rest = name.split("_")
    return first + "".join(w.capitalize() for w in rest)


def snake_to_pascal(name):
    """UserName from user_name."""
    return "".join(w.capitalize() for w in name.split("_"))


def pluralize(name):
    """Very small English plural helper."""
    if name.endswith("y"):
        return name[:-1] + "ies"
    return name + "s"


def strip_prefix(name, prefix):
    """Remove prefix if present."""
    return name[len(prefix):] if name.startswith(prefix) else name


def camel_to_snake(name):
    """user_name from userName or UserName."""
    out = []
    for ch in name:
        if ch.isupper():
            out.append("_" + ch.lower())
        else:
            out.append(ch)
    return "".join(out)
'''},
 {"test_naming.py": '''from naming import camel_to_snake, snake_to_camel, pluralize


def test_camel_to_snake():
    assert camel_to_snake("userName") == "user_name"
    assert camel_to_snake("UserName") == "user_name"
    assert camel_to_snake("id") == "id"


def test_other_helpers_still_work():
    assert snake_to_camel("user_name") == "userName"
    assert pluralize("city") == "cities"
'''}, "naming.py", '            out.append("_" + ch.lower())', '            out.append(("_" if out else "") + ch.lower())')

add("t012_round", "math",
 "Fix the bug: `rounding.round_half_up` rounds some halves down. The failing test is in test_rounding.py.",
 {"rounding.py": '''"""Rounding helpers for invoices. All functions return ints unless noted."""

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
'''},
 {"test_rounding.py": '''from rounding import round_half_up, ceil_div, clamp


def test_halves_go_up():
    assert round_half_up(2.5) == 3
    assert round_half_up(0.5) == 1
    assert round_half_up(3.5) == 4
    assert round_half_up(2.4) == 2


def test_helpers_still_work():
    assert ceil_div(7, 2) == 4
    assert clamp(9, 0, 5) == 5
'''}, "rounding.py", "    return round(x)", "    return math.floor(x + 0.5)")

add("t013_moving", "off-by-one",
 "Fix the bug: `series.moving_average` is missing its last value. The failing test is in test_series.py.",
 {"series.py": '''"""Time-series helpers for the metrics dashboard."""


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
'''},
 {"test_series.py": '''from series import moving_average, diffs


def test_moving_average():
    assert moving_average([1, 2, 3, 4, 5], 2) == [1.5, 2.5, 3.5, 4.5]
    assert moving_average([2, 4, 6], 3) == [4.0]


def test_diffs_still_work():
    assert diffs([1, 4, 9]) == [3, 5]
'''}, "series.py", "for i in range(len(xs) - k):", "for i in range(len(xs) - k + 1):")

add("t014_palindrome", "wrong condition",
 "Fix the bug: `wordplay.is_palindrome` rejects phrases that should count. The failing test is in test_wordplay.py.",
 {"wordplay.py": '''"""Word game helpers."""

VOWELS = "aeiou"


def vowel_count(s):
    """Number of vowels (case-insensitive)."""
    return sum(1 for c in s.lower() if c in VOWELS)


def reverse_words(s):
    """Words in reverse order."""
    return " ".join(reversed(s.split()))


def is_anagram(a, b):
    """True if a and b use the same letters, ignoring case and spaces."""
    clean = lambda s: sorted(s.replace(" ", "").lower())
    return clean(a) == clean(b)


def capitalize_words(s):
    """Capitalize each word."""
    return " ".join(w.capitalize() for w in s.split())


def longest_word(s):
    """Longest word (first one wins ties), or empty string."""
    words = s.split()
    return max(words, key=len) if words else ""


def is_palindrome(s):
    """True if s reads the same forwards and backwards, ignoring case, spaces and punctuation."""
    s = s.lower()
    return s == s[::-1]
'''},
 {"test_wordplay.py": '''from wordplay import is_palindrome, is_anagram


def test_palindromes():
    assert is_palindrome("Racecar")
    assert is_palindrome("A man, a plan, a canal: Panama")
    assert not is_palindrome("hello")


def test_anagram_still_works():
    assert is_anagram("Listen", "Silent")
'''}, "wordplay.py", "    s = s.lower()\n    return s == s[::-1]", "    s = [c for c in s.lower() if c.isalnum()]\n    return s == s[::-1]")

add("t015_config", "parsing",
 "Fix the bug: values that contain an equals sign are parsed wrongly. The failing test is in test_settings.py. The code is in settings/parser.py.",
 {"settings/__init__.py": "", "settings/defaults.py": '''"""Default settings and type coercion for the app configuration loader."""

DEFAULTS = {"debug": "false", "port": "8080", "host": "localhost", "workers": "2"}

TRUE_WORDS = {"1", "true", "yes", "on"}


def as_bool(text):
    """Interpret common truthy words."""
    return text.strip().lower() in TRUE_WORDS


def as_int(text, default=0):
    """Parse an int, falling back to default."""
    try:
        return int(text)
    except ValueError:
        return default


def with_defaults(values):
    """Overlay parsed values on the defaults."""
    merged = dict(DEFAULTS)
    merged.update(values)
    return merged
''', "settings/parser.py": '''"""Parse key=value configuration text."""


def clean_lines(text):
    """Non-empty, non-comment lines with surrounding whitespace removed."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def split_pair(line):
    """Split 'key=value' into (key, value), trimming spaces. The value may itself contain '='."""
    key, value = line.split("=")[:2]
    return key.strip(), value.strip()


def parse(text):
    """Parse configuration text into a dict."""
    return dict(split_pair(l) for l in clean_lines(text))
'''},
 {"test_settings.py": '''from settings.parser import parse
from settings.defaults import with_defaults, as_bool


def test_values_with_equals_signs():
    cfg = parse("# comment\\nurl = http://x/?a=1&b=2\\ndebug=true\\n")
    assert cfg["url"] == "http://x/?a=1&b=2"
    assert cfg["debug"] == "true"


def test_defaults_still_work():
    assert with_defaults({"port": "9"})["port"] == "9"
    assert as_bool("Yes")
'''}, "settings/parser.py", 'key, value = line.split("=")[:2]', 'key, _, value = line.partition("=")')

add("t016_duration", "data constant",
 "Fix the bug: `durations.parse_duration` returns wrong totals for strings with minutes. The failing test is in test_durations.py.",
 {"durations.py": '''"""Parse and format short duration strings such as '1h30m' or '45s'."""

import re

_PART = re.compile(r"(\\d+)([hms])")


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
    return bool(re.fullmatch(r"(\\d+[hms])+", text))


def parse_duration(text):
    """Total seconds in a duration string like '1h30m5s'."""
    return total_seconds(_PART.findall(text))


UNITS = {"h": 3600, "m": 6, "s": 1}
'''},
 {"test_durations.py": '''from durations import parse_duration, format_clock, is_valid


def test_parse_duration():
    assert parse_duration("1h30m") == 5400
    assert parse_duration("45s") == 45
    assert parse_duration("2m10s") == 130


def test_other_helpers_still_work():
    assert format_clock(3725) == "1:02:05"
    assert is_valid("1h2m")
'''}, "durations.py", '"m": 6,', '"m": 60,')

add("t017_dedupe", "ordering",
 "Fix the bug: `collections_util.unique` changes the order of the items. The failing test is in test_collections_util.py.",
 {"collections_util.py": '''"""Small collection helpers."""


def chunk(items, size):
    """Split a list into lists of at most `size` items."""
    return [items[i:i + size] for i in range(0, len(items), size)]


def flatten(nested):
    """One level of flattening."""
    return [x for sub in nested for x in sub]


def first(items, default=None):
    """First item or default."""
    return items[0] if items else default


def last(items, default=None):
    """Last item or default."""
    return items[-1] if items else default


def pairwise(items):
    """Consecutive pairs."""
    return list(zip(items, items[1:]))


def partition(items, pred):
    """(matching, non_matching) lists."""
    yes, no = [], []
    for x in items:
        (yes if pred(x) else no).append(x)
    return yes, no


def unique(items):
    """Items with duplicates removed, keeping the first occurrence in original order."""
    return list(set(items))
'''},
 {"test_collections_util.py": '''from collections_util import unique, chunk


def test_unique_keeps_first_occurrence_order():
    assert unique([3, 1, 3, 2, 1, 9]) == [3, 1, 2, 9]
    assert unique(["b", "a", "b"]) == ["b", "a"]


def test_chunk_still_works():
    assert chunk([1, 2, 3], 2) == [[1, 2], [3]]
'''}, "collections_util.py", "return list(set(items))", "return list(dict.fromkeys(items))")

add("t018_bsearch", "off-by-one",
 "Fix the bug: `searching.binary_search` cannot find some values that are in the list. The failing test is in test_searching.py.",
 {"searching.py": '''"""Searching helpers over sorted lists."""


def linear_search(items, target):
    """Index of target by scanning, or -1."""
    for i, x in enumerate(items):
        if x == target:
            return i
    return -1


def is_sorted(items):
    """True if items are in non-decreasing order."""
    return all(a <= b for a, b in zip(items, items[1:]))


def count_in_range(items, lo, hi):
    """How many sorted items fall in [lo, hi]."""
    return sum(1 for x in items if lo <= x <= hi)


def lower_bound(items, target):
    """Index of the first element >= target in a sorted list."""
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def insert_sorted(items, value):
    """New list with value inserted keeping order."""
    i = lower_bound(items, value)
    return items[:i] + [value] + items[i:]


def binary_search(items, target):
    """Index of target in a sorted list, or -1 if absent."""
    lo, hi = 0, len(items) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
'''},
 {"test_searching.py": '''from searching import binary_search, lower_bound


def test_binary_search_finds_every_element():
    items = [1, 3, 5, 7, 9, 11]
    for i, x in enumerate(items):
        assert binary_search(items, x) == i
    assert binary_search(items, 4) == -1
    assert binary_search([], 1) == -1


def test_lower_bound_still_works():
    assert lower_bound([1, 3, 5], 4) == 2
'''}, "searching.py", "while lo < hi:\n        mid = (lo + hi) // 2\n        if items[mid] == target:", "while lo <= hi:\n        mid = (lo + hi) // 2\n        if items[mid] == target:")

add("t019_transpose", "math",
 "Fix the bug: `matrix.transpose` fails or gives wrong results for non-square matrices. The failing test is in test_matrix.py.",
 {"matrix.py": '''"""Tiny matrix helpers. Matrices are lists of equal-length row lists."""


def shape(m):
    """(rows, cols)."""
    return (len(m), len(m[0]) if m else 0)


def identity(n):
    """n x n identity matrix."""
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def add(a, b):
    """Element-wise sum of equal-shaped matrices."""
    return [[x + y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def scale(m, k):
    """Multiply every element by k."""
    return [[x * k for x in row] for row in m]


def row_sums(m):
    """Sum of each row."""
    return [sum(row) for row in m]


def column(m, j):
    """Column j as a list."""
    return [row[j] for row in m]


def dot(a, b):
    """Matrix product a x b."""
    cols = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, c)) for c in cols] for row in a]


def transpose(m):
    """Rows become columns."""
    n = len(m)
    return [[m[i][j] for i in range(n)] for j in range(n)]
'''},
 {"test_matrix.py": '''from matrix import transpose, dot, identity


def test_transpose_rectangular():
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert transpose([[1], [2], [3]]) == [[1, 2, 3]]


def test_square_and_helpers():
    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]
    assert dot(identity(2), [[1, 2], [3, 4]]) == [[1, 2], [3, 4]]
'''}, "matrix.py", "    n = len(m)\n    return [[m[i][j] for i in range(n)] for j in range(n)]", "    rows, cols = len(m), len(m[0]) if m else 0\n    return [[m[i][j] for i in range(rows)] for j in range(cols)]")

add("t020_discount", "wrong condition",
 "Fix the bug: `pricing.discounted_total` applies the bulk discount at the wrong quantity. The failing test is in test_pricing.py. The code is in shop/pricing.py.",
 {"shop/__init__.py": "", "shop/catalog.py": '''"""Product catalog for the demo shop."""

PRICES = {"pen": 1.50, "notebook": 4.00, "bag": 25.00, "lamp": 18.75}


def price_of(item):
    """Unit price of an item."""
    return PRICES[item]


def known(item):
    """True if the catalog has the item."""
    return item in PRICES
''', "shop/pricing.py": '''"""Order pricing rules.

Bulk rule: orders of 10 or more units of a single line get 15% off that line.
"""

from shop.catalog import price_of

BULK_MIN = 10
BULK_RATE = 0.15


def line_total(item, qty):
    """Price of one order line before discounts."""
    return price_of(item) * qty


def apply_bulk(amount, qty):
    """Apply the bulk discount to a line amount when the quantity qualifies."""
    if qty > BULK_MIN:
        return amount * (1 - BULK_RATE)
    return amount


def discounted_total(order):
    """Total for an order given as a list of (item, qty) pairs."""
    return round(sum(apply_bulk(line_total(i, q), q) for i, q in order), 2)
'''},
 {"test_pricing.py": '''from shop.pricing import discounted_total, line_total


def test_bulk_discount_threshold():
    assert discounted_total([("pen", 10)]) == 12.75
    assert discounted_total([("pen", 9)]) == 13.5
    assert discounted_total([("pen", 12), ("bag", 1)]) == 40.3


def test_line_total_still_works():
    assert line_total("notebook", 3) == 12.0
'''}, "shop/pricing.py", "if qty > BULK_MIN:", "if qty >= BULK_MIN:")

for t in T:
    d = os.path.join(ROOT, t["id"], "repo")
    for name, code in {**t["files"], **t["tests"]}.items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(code)
    fix = ("python - <<'P'\nfrom pathlib import Path\np = Path(%r)\ns = p.read_text()\nassert %r in s\np.write_text(s.replace(%r, %r))\nP"
           % (t["bug_file"], t["old"], t["old"], t["new"]))
    meta = {"id": t["id"], "prompt": t["prompt"], "test_cmd": "python -m pytest -q", "source_file": t["bug_file"], "kind": t["kind"],
            "bug_old": t["old"], "bug_new": t["new"], "fake_script": [f"cat {t['bug_file']}", fix, "python -m pytest -q", "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"]}
    json.dump(meta, open(os.path.join(ROOT, t["id"], "task.json"), "w"), indent=1)
print(len(T), "tasks written")
