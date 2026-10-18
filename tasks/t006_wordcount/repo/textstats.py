"""Tiny text statistics used by the editor sidebar."""


def char_count(text):
    """Number of characters excluding newlines."""
    return len(text.replace("\n", ""))


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
