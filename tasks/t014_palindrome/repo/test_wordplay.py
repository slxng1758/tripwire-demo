from wordplay import is_palindrome, is_anagram


def test_palindromes():
    assert is_palindrome("Racecar")
    assert is_palindrome("A man, a plan, a canal: Panama")
    assert not is_palindrome("hello")


def test_anagram_still_works():
    assert is_anagram("Listen", "Silent")
