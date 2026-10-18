from naming import camel_to_snake, snake_to_camel, pluralize


def test_camel_to_snake():
    assert camel_to_snake("userName") == "user_name"
    assert camel_to_snake("UserName") == "user_name"
    assert camel_to_snake("id") == "id"


def test_other_helpers_still_work():
    assert snake_to_camel("user_name") == "userName"
    assert pluralize("city") == "cities"
