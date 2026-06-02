"""Direct unit tests for hermes_tavern.utils."""

from hermes_tavern.utils import estimate_tokens


def test_estimate_tokens_empty_returns_one():
    assert estimate_tokens("") == 1


def test_estimate_tokens_single_char_returns_one():
    assert estimate_tokens("x") == 1


def test_estimate_tokens_four_chars_returns_one():
    assert estimate_tokens("abcd") == 1


def test_estimate_tokens_eight_chars_returns_two():
    assert estimate_tokens("12345678") == 2


def test_estimate_tokens_hundred_chars():
    assert estimate_tokens("x" * 100) == 25


def test_estimate_tokens_never_zero():
    # Contract: always at least 1, never 0 — callers safe to divide by result
    for text in ("", "a", "ab", "abc"):
        assert estimate_tokens(text) >= 1
