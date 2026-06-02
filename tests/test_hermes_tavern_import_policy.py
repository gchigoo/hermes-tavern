"""Direct unit tests for hermes_tavern.import_policy."""

from __future__ import annotations

import types
from pathlib import Path

import pytest

from hermes_tavern.import_policy import (
    ImportPathDecision,
    is_gateway_event,
    is_local_media_path,
    resolve_import_path,
)

# ── helpers ───────────────────────────────────────────────────────────────────


def _gateway_event(*media_urls, platform=None, chat_id=None, user_id=None):
    return types.SimpleNamespace(
        media_urls=list(media_urls),
        platform=platform,
        chat_id=chat_id,
        user_id=user_id,
    )


def _resolve(event, explicit=None, *, suffixes=None, allow_remote_urls=False):
    return resolve_import_path(
        event,
        explicit,
        label="card",
        suffixes=suffixes or {".png", ".jpg", ".json"},
        usage="No card file provided.",
        attach_tip="a .png or .json file",
        allow_remote_urls=allow_remote_urls,
    )


# ── is_local_media_path ───────────────────────────────────────────────────────


def test_local_media_path_bare_filename():
    assert is_local_media_path("card.png") is True


def test_local_media_path_absolute():
    assert is_local_media_path("/tmp/cards/card.json") is True


def test_local_media_path_relative():
    assert is_local_media_path("./cards/example.png") is True


def test_local_media_path_tilde():
    assert is_local_media_path("~/.hermes/card.json") is True


def test_local_media_path_http_is_false():
    assert is_local_media_path("http://example.com/card.png") is False


def test_local_media_path_https_is_false():
    assert is_local_media_path("https://cdn.example.com/file.json") is False


def test_local_media_path_double_slash_netloc_is_false():
    assert is_local_media_path("//cdn.example.com/file.png") is False


# ── is_gateway_event ──────────────────────────────────────────────────────────


def test_is_gateway_event_no_media_urls_attr_is_false():
    event = types.SimpleNamespace(platform="telegram", chat_id="c1")
    assert is_gateway_event(event) is False


def test_is_gateway_event_platform_set_is_true():
    event = _gateway_event("/tmp/f.png", platform="telegram")
    assert is_gateway_event(event) is True


def test_is_gateway_event_chat_id_set_is_true():
    event = _gateway_event("/tmp/f.png", chat_id="c1")
    assert is_gateway_event(event) is True


def test_is_gateway_event_user_id_set_is_true():
    event = _gateway_event("/tmp/f.png", user_id="u1")
    assert is_gateway_event(event) is True


def test_is_gateway_event_all_identity_none_is_false():
    event = _gateway_event("/tmp/f.png")
    assert is_gateway_event(event) is False


def test_is_gateway_event_source_platform_is_true():
    source = types.SimpleNamespace(platform="discord", chat_id=None, user_id=None)
    event = types.SimpleNamespace(media_urls=["/tmp/f.png"], source=source)
    assert is_gateway_event(event) is True


def test_is_gateway_event_source_all_none_is_false():
    source = types.SimpleNamespace(platform=None, chat_id=None, user_id=None)
    event = types.SimpleNamespace(media_urls=["/tmp/f.png"], source=source)
    assert is_gateway_event(event) is False


# ── resolve_import_path ───────────────────────────────────────────────────────


def test_resolve_no_explicit_no_attachments_returns_error():
    event = types.SimpleNamespace()  # no media_urls attribute
    decision = _resolve(event, explicit=None)
    assert decision.value is None
    assert decision.error is not None
    assert "attach" in decision.error.lower()


def test_resolve_no_explicit_one_matching_attachment_returns_path():
    event = types.SimpleNamespace(media_urls=["/example/card.png"])
    decision = _resolve(event, explicit=None)
    assert decision.error is None
    assert decision.value == Path("/example/card.png")


def test_resolve_no_explicit_multiple_attachments_returns_error():
    event = types.SimpleNamespace(media_urls=["/example/a.png", "/example/b.png"])
    decision = _resolve(event, explicit=None)
    assert decision.value is None
    assert decision.error is not None
    assert "Multiple" in decision.error


def test_resolve_no_explicit_attachment_wrong_suffix_is_ignored():
    # .txt is not in SUFFIXES, so no matching attachments → error
    event = types.SimpleNamespace(media_urls=["/example/notes.txt"])
    decision = _resolve(event, explicit=None)
    assert decision.value is None
    assert decision.error is not None


def test_resolve_explicit_local_trusted_caller_returns_path():
    event = types.SimpleNamespace()  # no media_urls → not a gateway event
    decision = _resolve(event, explicit="/example/card.json")
    assert decision.error is None
    assert decision.value == Path("/example/card.json").expanduser()


def test_resolve_explicit_gateway_event_not_in_attachments_rejected(tmp_path):
    attachment = tmp_path / "other.png"
    attachment.touch()
    target = tmp_path / "card.png"
    target.touch()
    event = _gateway_event(str(attachment), platform="telegram")
    decision = _resolve(event, explicit=str(target))
    assert decision.value is None
    assert "rejected" in decision.error.lower()
    assert str(target) not in decision.error


def test_resolve_explicit_gateway_event_in_attachments_accepted(tmp_path):
    f = tmp_path / "card.png"
    f.touch()
    event = _gateway_event(str(f), platform="telegram")
    decision = _resolve(event, explicit=str(f))
    assert decision.error is None
    assert decision.value == Path(str(f)).expanduser()


def test_resolve_explicit_gateway_event_normalized_attachment_match_is_accepted(
    tmp_path, monkeypatch
):
    f = tmp_path / "card.json"
    f.touch()
    monkeypatch.chdir(tmp_path)
    event = _gateway_event(str(f.resolve()), platform="telegram")

    decision = _resolve(event, explicit="./card.json")

    assert decision.error is None
    assert decision.value == Path("./card.json").expanduser()


def test_resolve_explicit_gateway_event_existing_allowed_suffix_without_attachment_rejected(
    tmp_path,
):
    target = tmp_path / "card.json"
    target.touch()
    event = _gateway_event(platform="telegram")

    decision = _resolve(event, explicit=str(target))

    assert decision.value is None
    assert "rejected" in decision.error.lower()
    assert str(target) not in decision.error


def test_resolve_explicit_remote_url_gateway_event_rejected():
    event = _gateway_event(platform="telegram")
    decision = _resolve(event, explicit="https://example.com/card.png")
    assert decision.value is None
    assert "rejected" in decision.error.lower()


def test_resolve_explicit_remote_url_local_trusted_with_flag():
    event = types.SimpleNamespace()
    decision = _resolve(
        event, explicit="https://example.com/card.png", allow_remote_urls=True
    )
    assert decision.error is None
    assert decision.value == "https://example.com/card.png"


def test_resolve_explicit_wrong_suffix_gateway_rejected(tmp_path):
    f = tmp_path / "card.txt"
    f.touch()
    event = _gateway_event(str(f), platform="telegram")
    decision = _resolve(event, explicit=str(f))
    assert decision.value is None
    assert "rejected" in decision.error.lower()
