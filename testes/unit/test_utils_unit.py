import re


def is_strong_password(pwd: str) -> bool:
    return (
        len(pwd) >= 8
        and re.search(r"[A-Z]", pwd)
        and re.search(r"[a-z]", pwd)
        and re.search(r"\d", pwd)
    )


def test_password_strength_rules():
    assert is_strong_password("Abcdefg1")
    assert not is_strong_password("abcdefg1")
    assert not is_strong_password("ABCDEFG1")
    assert not is_strong_password("Abcdefgh")
