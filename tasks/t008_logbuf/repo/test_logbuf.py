from logbuf import record, render


def test_separate_buffers():
    a = record("info", "first")
    b = record("warn", "second")
    assert a == [("info", "first")]
    assert b == [("warn", "second")]


def test_existing_buffer_is_extended():
    buf = []
    record("info", "x", buf)
    record("error", "y", buf)
    assert render(buf) == "[INFO] x\n[ERROR] y"
