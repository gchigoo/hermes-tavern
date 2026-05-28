import json

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class GatewayEvent:
    source = Source()
    text = ""

    def __init__(self, media_urls=None):
        self.media_urls = list(media_urls or [])


class LocalEvent:
    text = ""
    media_urls = []


def _runtime(tmp_path):
    return TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))


@pytest.mark.parametrize(
    ("command", "args", "filename", "payload", "rejected"),
    [
        ("card", ["import"], "alice.json", {"name": "Alice"}, "Card import rejected"),
        ("preset", ["import"], "preset.txt", "Keep replies concise.", "Preset import rejected"),
        (
            "lore",
            ["import"],
            "lore.json",
            {"name": "Atlas", "entries": [{"comment": "Moon", "content": "The moon.", "keys": ["moon"]}]},
            "Lore import rejected",
        ),
        ("persona", ["import"], "persona.txt", "I am a local persona.", "Persona import rejected"),
    ],
)
def test_gateway_explicit_unattached_local_path_is_rejected(tmp_path, command, args, filename, payload, rejected):
    import_file = tmp_path / filename
    if isinstance(payload, str):
        import_file.write_text(payload, encoding="utf-8")
    else:
        import_file.write_text(json.dumps(payload), encoding="utf-8")
    runtime = _runtime(tmp_path)

    result = runtime.handle_command_sync(
        RPCommand(command, [*args, str(import_file)], f"/rp {command} import {import_file}"),
        GatewayEvent(),
    )

    assert rejected in result
    assert str(import_file) not in result
    assert "attach the file" in result


@pytest.mark.parametrize(
    ("command", "filename", "payload", "imported"),
    [
        ("card", "alice.json", {"name": "Alice"}, "Imported card: Alice"),
        ("preset", "preset.txt", "Keep replies concise.", "Imported ST preset: preset"),
        (
            "lore",
            "lore.json",
            {"name": "Atlas", "entries": [{"comment": "Moon", "content": "The moon.", "keys": ["moon"]}]},
            "Imported ST lorebook: Atlas",
        ),
        ("persona", "persona.txt", "I am a local persona.", "Imported Hermes Tavern persona: persona"),
    ],
)
def test_gateway_explicit_path_matching_attachment_is_accepted(tmp_path, command, filename, payload, imported):
    import_file = tmp_path / filename
    if isinstance(payload, str):
        import_file.write_text(payload, encoding="utf-8")
    else:
        import_file.write_text(json.dumps(payload), encoding="utf-8")
    runtime = _runtime(tmp_path)

    result = runtime.handle_command_sync(
        RPCommand(command, ["import", str(import_file)], f"/rp {command} import {import_file}"),
        GatewayEvent([str(import_file)]),
    )

    assert imported in result


@pytest.mark.parametrize(
    ("command", "filename", "payload", "imported"),
    [
        ("card", "alice.json", {"name": "Alice"}, "Imported card: Alice"),
        ("preset", "preset.txt", "Keep replies concise.", "Imported ST preset: preset"),
        (
            "lore",
            "lore.json",
            {"name": "Atlas", "entries": [{"comment": "Moon", "content": "The moon.", "keys": ["moon"]}]},
            "Imported ST lorebook: Atlas",
        ),
        ("persona", "persona.txt", "I am a local persona.", "Imported Hermes Tavern persona: persona"),
    ],
)
def test_local_explicit_path_import_still_works(tmp_path, command, filename, payload, imported):
    import_file = tmp_path / filename
    if isinstance(payload, str):
        import_file.write_text(payload, encoding="utf-8")
    else:
        import_file.write_text(json.dumps(payload), encoding="utf-8")
    runtime = _runtime(tmp_path)

    result = runtime.handle_command_sync(
        RPCommand(command, ["import", str(import_file)], f"/rp {command} import {import_file}"),
        LocalEvent(),
    )

    assert imported in result


def test_gateway_explicit_sensitive_path_is_rejected_without_echoing_full_path(tmp_path):
    runtime = _runtime(tmp_path)

    result = runtime.handle_command_sync(
        RPCommand("card", ["import", "/etc/passwd"], "/rp card import /etc/passwd"),
        GatewayEvent(),
    )

    assert "Card import rejected" in result
    assert "/etc/passwd" not in result


def test_gateway_explicit_remote_url_is_rejected(tmp_path):
    runtime = _runtime(tmp_path)

    result = runtime.handle_command_sync(
        RPCommand("card", ["import", "https://example.test/alice.json"], "/rp card import https://example.test/alice.json"),
        GatewayEvent(["https://example.test/alice.json"]),
    )

    assert "Card import rejected" in result
    assert "example.test" not in result
