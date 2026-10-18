from text import slugify, title_case


def test_slugify():
    assert slugify("Hello  Wörld Café") == "hello-world-cafe"


def test_title_case_still_works():
    assert title_case("a b") == "A B"
