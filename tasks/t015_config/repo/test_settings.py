from settings.parser import parse
from settings.defaults import with_defaults, as_bool


def test_values_with_equals_signs():
    cfg = parse("# comment\nurl = http://x/?a=1&b=2\ndebug=true\n")
    assert cfg["url"] == "http://x/?a=1&b=2"
    assert cfg["debug"] == "true"


def test_defaults_still_work():
    assert with_defaults({"port": "9"})["port"] == "9"
    assert as_bool("Yes")
