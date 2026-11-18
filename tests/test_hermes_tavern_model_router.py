"""Tests for ModelRouter and ModelProfileDescriptor."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.model_router import ModelProfileDescriptor, ModelRouter


def test_resolve_no_session_returns_anthropic_opus():
    d = ModelRouter().resolve()
    assert d.provider == "anthropic"
    assert d.model_id == "claude-opus-4-6"
    assert d.source.startswith("default")


def test_resolve_session_row_without_profile_id_returns_default():
    d = ModelRouter().resolve(session_row={"id": "s1", "card_id": "c1"}, store=None)
    assert d.provider == "anthropic"
    assert d.source.startswith("default")


def test_descriptor_has_no_secret_fields():
    d = ModelRouter().resolve()
    assert not hasattr(d, "api_key")
    assert not hasattr(d, "access_token")
    assert not hasattr(d, "secret")


def test_descriptor_is_frozen():
    d = ModelRouter().resolve()
    with pytest.raises((AttributeError, TypeError)):
        d.provider = "other"  # type: ignore[misc]


def test_descriptor_mode_and_context_window():
    d = ModelRouter().resolve()
    assert d.mode == "chat"
    assert d.context_window > 0


class _ProfileStore:
    """Fake store that returns one model profile row."""

    def __init__(self, row):
        self._row = row

    def get_model_profile(self, _profile_id):
        """Return the prepared profile row unchanged."""
        return self._row


_PROFILE_ROW = {
    "id": "profile-1",
    "provider": "openrouter",
    "model_id": "custom/model-1",
    "name": "profile-x",
    "context_window": 4096,
}


def _assert_resolved_profile(row, expected_mode):
    """Resolve a profile row and require a stable db descriptor."""
    original = dict(row)
    descriptor = ModelRouter().resolve(
        session_row={"model_profile_id": "profile-1"},
        store=_ProfileStore(row),
    )
    assert descriptor == ModelProfileDescriptor(
        provider="openrouter",
        model_id="custom/model-1",
        mode=expected_mode,
        context_window=4096,
        source="db_profile",
        profile_name="profile-x",
    )
    assert row == original


@pytest.mark.parametrize(
    "raw_json",
    (
        pytest.param("null", id="null"),
        pytest.param("[]", id="empty-array"),
        pytest.param('["completion"]', id="array"),
        pytest.param("true", id="true"),
        pytest.param("false", id="false"),
        pytest.param("0", id="zero"),
        pytest.param("1.5", id="number"),
        pytest.param('"completion"', id="string"),
        pytest.param('""', id="empty-json-string"),
    ),
)
@pytest.mark.parametrize(
    ("row_mode", "expected_mode"),
    (
        pytest.param("completion", "completion", id="row-mode"),
        pytest.param(None, "chat", id="absent-mode"),
    ),
)
def test_resolve_non_object_raw_json_uses_row_mode_or_chat(
    raw_json, row_mode, expected_mode
):
    """Valid non-object metadata resolves; an explicit row mode wins."""
    row = {**_PROFILE_ROW, "raw_json": raw_json}
    if row_mode is not None:
        row["mode"] = row_mode
    _assert_resolved_profile(row, expected_mode)


@pytest.mark.parametrize(
    ("raw_json", "row_mode", "expected_mode"),
    (
        pytest.param(
            '{"mode": "completion"}',
            None,
            "completion",
            id="metadata-fallback",
        ),
        pytest.param(
            '{"mode": "chat"}',
            "completion",
            "completion",
            id="row-mode-wins",
        ),
    ),
)
def test_resolve_object_metadata_mode_fallback_and_row_precedence(
    raw_json, row_mode, expected_mode
):
    """Object metadata supplies mode only when the profile row has none."""
    row = {**_PROFILE_ROW, "raw_json": raw_json}
    if row_mode is not None:
        row["mode"] = row_mode
    _assert_resolved_profile(row, expected_mode)


@pytest.mark.parametrize(
    "metadata",
    (
        pytest.param({"raw_json": ""}, id="empty"),
        pytest.param({"raw_json": "{}"}, id="empty-object"),
        pytest.param({"raw_json": "{"}, id="malformed"),
        pytest.param({"raw_json": "not-json"}, id="malformed-text"),
        pytest.param({"raw_json": None}, id="none"),
        pytest.param({}, id="missing"),
    ),
)
def test_resolve_empty_malformed_none_or_missing_metadata_defaults_to_chat(metadata):
    """Empty, malformed, None, or missing metadata falls back to chat."""
    _assert_resolved_profile({**_PROFILE_ROW, **metadata}, "chat")
