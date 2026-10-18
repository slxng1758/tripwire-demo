from durations import parse_duration, format_clock, is_valid


def test_parse_duration():
    assert parse_duration("1h30m") == 5400
    assert parse_duration("45s") == 45
    assert parse_duration("2m10s") == 130


def test_other_helpers_still_work():
    assert format_clock(3725) == "1:02:05"
    assert is_valid("1h2m")
