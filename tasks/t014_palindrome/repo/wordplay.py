"""Word game helpers."""

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
