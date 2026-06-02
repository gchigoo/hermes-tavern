"""Phase 54: direct unit tests for hermes_tavern.db_utils utility functions.

db_utils.py provides three helpers used throughout db.py:
  utc_now()             — ISO-format UTC timestamp string
  row_to_dict()         — sqlite3.Row → dict (None-safe)
  assert_no_secret_keys() — security guard against persisting credentials
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pytest

from hermes_tavern.db_utils import assert_no_secret_keys, row_to_dict, utc_now


# ---------------------------------------------------------------------------
# utc_now
# ---------------------------------------------------------------------------


def test_utc_now_returns_string():
    result = utc_now()
    assert isinstance(result, str)
    assert result  # non-empty


def test_utc_now_is_parseable_iso_datetime():
    result = utc_now()
    dt = datetime.fromisoformat(result)
    assert dt is not None


def test_utc_now_is_utc():
    result = utc_now()
    dt = datetime.fromisoformat(result)
    # Produced by datetime.now(timezone.utc) so tzinfo must be UTC (+00:00)
    assert dt.tzinfo is not None
    assert dt.utcoffset().total_seconds() == 0


# ---------------------------------------------------------------------------
# row_to_dict
# ---------------------------------------------------------------------------


def _make_row(data: dict) -> sqlite3.Row:
    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(f"CREATE TABLE _t ({cols})")
    conn.execute(f"INSERT INTO _t VALUES ({placeholders})", list(data.values()))
    return conn.execute(f"SELECT {cols} FROM _t").fetchone()


def test_row_to_dict_none_returns_none():
    assert row_to_dict(None) is None


def test_row_to_dict_converts_row_to_dict():
    row = _make_row({"name": "Alice", "score": 99})
    result = row_to_dict(row)
    assert isinstance(result, dict)
    assert result == {"name": "Alice", "score": 99}


def test_row_to_dict_preserves_all_columns():
    row = _make_row({"a": 1, "b": "two", "c": None})
    result = row_to_dict(row)
    assert result == {"a": 1, "b": "two", "c": None}


# ---------------------------------------------------------------------------
# assert_no_secret_keys — happy paths
# ---------------------------------------------------------------------------


def test_assert_no_secret_keys_passes_empty_dict():
    assert_no_secret_keys({})  # must not raise


def test_assert_no_secret_keys_passes_clean_dict():
    assert_no_secret_keys({"provider": "anthropic", "model_id": "claude-opus-4-6"})


def test_assert_no_secret_keys_passes_nested_clean_dict():
    assert_no_secret_keys({"config": {"provider": "openrouter", "base_url": "https://example.com"}})


def test_assert_no_secret_keys_passes_list_of_clean_dicts():
    assert_no_secret_keys([{"provider": "anthropic"}, {"provider": "openrouter"}])


def test_assert_no_secret_keys_passes_non_dict_scalar():
    assert_no_secret_keys("just a string")
    assert_no_secret_keys(42)
    assert_no_secret_keys(None)


# ---------------------------------------------------------------------------
# assert_no_secret_keys — blocked field names
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field_name",
    ["api_key", "access_token", "secret", "token", "password"],
)
def test_assert_no_secret_keys_blocks_direct_secret_field(field_name: str):
    with pytest.raises(ValueError, match="must not persist secret field"):
        assert_no_secret_keys({field_name: "some-value"})


@pytest.mark.parametrize(
    "field_name",
    ["API_KEY", "ACCESS_TOKEN", "SECRET", "TOKEN", "PASSWORD"],
)
def test_assert_no_secret_keys_is_case_insensitive(field_name: str):
    # key.lower() comparison means uppercase variants are also blocked.
    with pytest.raises(ValueError, match="must not persist secret field"):
        assert_no_secret_keys({field_name: "some-value"})


def test_assert_no_secret_keys_blocks_nested_secret():
    with pytest.raises(ValueError, match="must not persist secret field"):
        assert_no_secret_keys({"profile": {"api_key": "sk-secret"}})


def test_assert_no_secret_keys_blocks_secret_inside_list():
    with pytest.raises(ValueError, match="must not persist secret field"):
        assert_no_secret_keys([{"provider": "anthropic"}, {"api_key": "sk-secret"}])


def test_assert_no_secret_keys_error_message_contains_path():
    with pytest.raises(ValueError) as exc_info:
        assert_no_secret_keys({"profile": {"credentials": {"api_key": "x"}}})
    assert "api_key" in str(exc_info.value)
