from textstats import word_count, line_count


def test_word_count_whitespace():
    assert word_count("one  two\nthree") == 3
    assert word_count("  padded  ") == 1
    assert word_count("") == 0


def test_line_count_still_works():
    assert line_count("a\nb") == 2
