import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.lorebooks import (
    ImportedLorebook,
    ImportedLorebookEntry,
    import_st_lorebook_json,
)
from plugins.hermes_tavern.runtime import TavernRuntime
from plugins.hermes_tavern.hermes_home import get_hermes_home


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


def _extract_export_path(response: str) -> Path:
    line = next(line for line in response.splitlines() if line.startswith("file: "))
    return Path(line.split("file: ", 1)[1])


def _parse_session_from_runtime(runtime: TavernRuntime, session_key: str) -> dict:
    session = runtime.store.get_active_session(session_key)
    assert session is not None
    return deepcopy(session)


@pytest.mark.asyncio
async def test_lore_runtime_import_list_use_test_debug(tmp_path):
    path = tmp_path / "atlas.json"
    path.write_text(json.dumps({
        "name": "Atlas",
        "entries": [{"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"]}],
    }), encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    imported = await runtime.handle_command(RPCommand("lore", ["import", str(path)], "/rp lore import"), Event())
    listed = await runtime.handle_command(RPCommand("lore", ["list"], "/rp lore list"), Event())
    bound = await runtime.handle_command(RPCommand("lore", ["use", "Atlas"], "/rp lore use Atlas"), Event())
    tested = await runtime.handle_command(RPCommand("lore", ["test", "moon"], "/rp lore test moon"), Event())
    debug = await runtime.handle_command(RPCommand("lore", ["debug"], "/rp lore debug"), Event())
    cleared = await runtime.handle_command(RPCommand("lore", ["clear"], "/rp lore clear"), Event())

    assert "Imported ST lorebook" in imported
    assert "Atlas" in listed
    assert "lorebook bound" in bound
    assert "Moon" in tested and "matched:" in tested
    assert "+ Moon: key match: moon" in tested
    assert "debug: /rp lore debug" in tested
    assert "keys=['moon']" in debug
    assert "lorebook cleared" in cleared
    assert store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["lorebook_id"] is None


@pytest.mark.asyncio
async def test_lore_runtime_export_usage_and_not_found(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    event = Event()

    usage = await runtime.handle_command(RPCommand("lore", ["export"], "/rp lore export"), event)
    not_found = await runtime.handle_command(RPCommand("lore", ["export", "missing"], "/rp lore export missing"), event)

    assert usage == "Usage: /rp lore export <lorebook>"
    assert not_found == "Lorebook not found: missing"


@pytest.mark.asyncio
async def test_lore_runtime_export_uses_raw_json(monkeypatch, tmp_path):
    home = tmp_path / "home with space"
    monkeypatch.setenv("HERMES_HOME", str(home))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    event = Event()

    raw_payload = {
        "title": "raw-lorebook",
        "entries": [
            {"comment": "Moon", "content": "The moon is present.", "keys": ["moon"], "id": "x"},
        ],
    }
    lorebook = ImportedLorebook(
        name="AtlasRaw",
        source="raw-json",
        raw=raw_payload,
        entries=(
            ImportedLorebookEntry(
                id="entry-1",
                title="Moon",
                content="The moon is present.",
                keys=("moon",),
                secondary_keys=("lunar",),
            ),
        ),
        id="AtlasRaw-id",
    )
    store.save_lorebook(lorebook)

    response = await runtime.handle_command(RPCommand("lore", ["export", "AtlasRaw"], "/rp lore export AtlasRaw"), event)
    path = _extract_export_path(response)
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data == raw_payload
    assert path.exists()
    assert str(path).startswith(str(home))
    assert f'file: {path}' in response
    assert f'MEDIA:"{path}"' in response


@pytest.mark.asyncio
async def test_lore_runtime_export_fallback_payload_last_and_no_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes_home"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    event = Event()
    session_key = "telegram:chat:chat-1:thread:main:user:user-1"
    store.start_session(session_key)
    session_before = _parse_session_from_runtime(runtime, session_key)

    lorebook = ImportedLorebook(
        name="FallbackBook",
        source="fallback-source",
        raw=["legacy", "json", "list"],
        entries=(
            ImportedLorebookEntry(
                id="..//escape/me",
                title="FallbackEntry",
                content="Fallback content",
                keys=("moon", "star"),
                secondary_keys=("alt",),
                enabled=False,
                constant=True,
                regex=True,
                position="before_char",
                insertion_order=7,
                priority=3,
                probability=0.42,
                raw={"legacy": True},
            ),
        ),
        id="../evil/lorebook",
    )
    lorebook_id = store.save_lorebook(lorebook)
    store.append_message(store.get_active_session(session_key)["id"], "user", "hello")

    messages_before = deepcopy(store.get_messages_page(store.get_active_session(session_key)["id"], 200, 0))
    lorebooks_before = deepcopy(store.list_lorebooks())
    entries_before = deepcopy(store.list_lorebook_entries(lorebook_id))
    lorebook_before = deepcopy(store.get_lorebook(lorebook_id))

    response = await runtime.handle_command(RPCommand("lore", ["export", lorebook_id], f"/rp lore export {lorebook_id}"), event)
    path = _extract_export_path(response)
    data = json.loads(path.read_text(encoding="utf-8"))
    session_after = _parse_session_from_runtime(runtime, session_key)
    messages_after = deepcopy(store.get_messages_page(store.get_active_session(session_key)["id"], 200, 0))
    lorebooks_after = deepcopy(store.list_lorebooks())
    entries_after = deepcopy(store.list_lorebook_entries(lorebook_id))
    lorebook_after = deepcopy(store.get_lorebook(lorebook_id))

    assert data["name"] == "FallbackBook"
    assert data["source"] == "fallback-source"
    assert len(data["entries"]) == 1
    assert data["entries"][0]["title"] == "FallbackEntry"
    assert data["entries"][0]["content"] == "Fallback content"
    assert data["entries"][0]["keys"] == ["moon", "star"]
    assert data["entries"][0]["secondary_keys"] == ["alt"]
    assert data["entries"][0]["enabled"] is False
    assert data["entries"][0]["constant"] is True
    assert data["entries"][0]["regex"] is True
    assert data["entries"][0]["position"] == "before_char"
    assert data["entries"][0]["insertion_order"] == 7
    assert data["entries"][0]["priority"] == 3
    assert data["entries"][0]["probability"] == 0.42

    assert session_before == session_after
    assert messages_before == messages_after
    assert lorebooks_before == lorebooks_after
    assert entries_before == entries_after
    assert lorebook_before == lorebook_after


@pytest.mark.asyncio
async def test_lore_runtime_export_fallback_defaults_nonfinite_and_overflow_numbers(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes_home"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    lorebook = ImportedLorebook(
        name="LegacyNumbers",
        source="legacy",
        raw=["legacy"],
        entries=(
            ImportedLorebookEntry(
                id="entry-1",
                title="Legacy entry",
                content="Legacy content",
                keys=("legacy",),
                insertion_order=3,
                priority=7,
                probability=0.5,
            ),
        ),
        id="legacy-numbers",
    )
    lorebook_id = store.save_lorebook(lorebook)
    with store.connect() as conn:
        conn.execute(
            "UPDATE lorebook_entries SET insertion_order = ?, priority = ?, probability = ? WHERE lorebook_id = ?",
            (float("inf"), 7, "Infinity", lorebook_id),
        )

    response = await runtime.handle_command(
        RPCommand("lore", ["export", lorebook_id], f"/rp lore export {lorebook_id}"),
        Event(),
    )
    data = json.loads(_extract_export_path(response).read_text(encoding="utf-8"))

    assert data["entries"][0]["insertion_order"] == 0
    assert data["entries"][0]["priority"] == 7
    assert data["entries"][0]["probability"] == 1.0


@pytest.mark.asyncio
async def test_lore_runtime_export_uses_last_reference(monkeypatch, tmp_path):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes_home"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    raw_one = {"name": "First", "entries": [{"comment": "One", "content": "One content", "keys": ["one"]}]}
    raw_two = {"name": "Second", "entries": [{"comment": "Two", "content": "Two content", "keys": ["two"]}]}
    store.save_lorebook(ImportedLorebook(name="First", source="test", raw=raw_one, entries=(ImportedLorebookEntry(id="1", title="First", content="One", keys=("one",)),)))
    store.save_lorebook(ImportedLorebook(name="Second", source="test", raw=raw_two, entries=(ImportedLorebookEntry(id="2", title="Second", content="Two", keys=("two",)),)))
    response = await runtime.handle_command(RPCommand("lore", ["export", "last"], "/rp lore export last"), Event())
    path = _extract_export_path(response)
    data = json.loads(path.read_text(encoding="utf-8"))

    assert data["name"] == "Second"


@pytest.mark.asyncio
async def test_lore_runtime_export_path_is_within_lorebook_exports_directory(monkeypatch, tmp_path):
    home = tmp_path / "home with escape"
    monkeypatch.setenv("HERMES_HOME", str(home))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    lorebook = ImportedLorebook(
        name="Path",
        source="test",
        raw=["legacy"],
        entries=(ImportedLorebookEntry(id="1", title="Path", content="Path", keys=("path",)),),
        id="../../../../outside",
    )
    lorebook_id = store.save_lorebook(lorebook)
    response = await runtime.handle_command(RPCommand("lore", ["export", lorebook_id], f"/rp lore export {lorebook_id}"), Event())
    path = _extract_export_path(response)

    export_dir = get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "lorebooks"
    assert path.exists()
    assert path.parent == export_dir
    assert path.resolve().is_relative_to(export_dir.resolve())


@pytest.mark.asyncio
async def test_lore_modules_appear_in_debug_prompt(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    lorebook_id = store.save_lorebook(import_st_lorebook_json({
        "name": "Atlas",
        "entries": [{"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"]}],
    }))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    store.set_session_lorebook("telegram:chat:chat-1:thread:main:user:user-1", lorebook_id)
    active = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.append_message(active["id"], "user", "Tell me about the moon")

    prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "lorebook:" in prompt
    assert "lore:Moon" in prompt
    assert "The moon is cracked" in prompt


@pytest.mark.asyncio
async def test_lore_enable_disable_entry_affects_matching(tmp_path):
    path = tmp_path / "atlas.json"
    path.write_text(json.dumps({
        "name": "Atlas",
        "entries": [
            {"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"]},
            {"comment": "Sun", "content": "The sun is blue.", "keys": ["sun"], "disable": True},
        ],
    }), encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    await runtime.handle_command(RPCommand("lore", ["import", str(path)], "/rp lore import"), Event())
    await runtime.handle_command(RPCommand("lore", ["use", "Atlas"], "/rp lore use Atlas"), Event())

    before = await runtime.handle_command(RPCommand("lore", ["test", "moon", "sun"], "/rp lore test moon sun"), Event())
    disabled = await runtime.handle_command(RPCommand("lore", ["disable", "Moon"], "/rp lore disable Moon"), Event())
    after_disable = await runtime.handle_command(RPCommand("lore", ["test", "moon", "sun"], "/rp lore test moon sun"), Event())
    enabled = await runtime.handle_command(RPCommand("lore", ["enable", "Sun"], "/rp lore enable Sun"), Event())
    after_enable = await runtime.handle_command(RPCommand("lore", ["test", "moon", "sun"], "/rp lore test moon sun"), Event())

    assert "+ Moon: key match: moon" in before
    assert "+ Sun: key match: sun" not in before
    assert "lore entry disabled: Moon" in disabled
    assert "+ Moon: key match: moon" not in after_disable
    assert "lore entry enabled: Sun" in enabled
    assert "+ Sun: key match: sun" in after_enable


@pytest.mark.asyncio
async def test_lore_runtime_export_preserves_unknown_flag_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes_home"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    lorebook_id = store.save_lorebook(
        ImportedLorebook(
            name="LegacyFlags",
            source="test",
            raw=["legacy"],
            entries=(ImportedLorebookEntry(id="entry", title="Entry", content="Content", keys=("moon",)),),
            id="legacy-unknown-flags",
        )
    )
    with store.connect() as conn:
        conn.execute(
            "UPDATE lorebook_entries SET enabled = ?, constant = ?, regex = ? WHERE lorebook_id = ?",
            ("unknown", "unknown", "unknown", lorebook_id),
        )

    response = await runtime.handle_command(
        RPCommand("lore", ["export", lorebook_id], f"/rp lore export {lorebook_id}"), Event()
    )
    entry = json.loads(_extract_export_path(response).read_text(encoding="utf-8"))["entries"][0]

    assert entry["enabled"] is False
    assert entry["constant"] is False
    assert entry["regex"] is False


@pytest.mark.asyncio
async def test_lore_runtime_normalizes_legacy_false_flags_in_status_output(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session_key = "telegram:chat:chat-1:thread:main:user:user-1"
    store.start_session(session_key)
    runtime = TavernRuntime(store)
    lorebook_id = store.save_lorebook(
        ImportedLorebook(
            name="LegacyFlags",
            source="test",
            raw={"name": "LegacyFlags"},
            entries=(
                ImportedLorebookEntry(
                    id="entry",
                    title="Legacy entry",
                    content="Legacy content",
                    keys=("moon",),
                ),
            ),
            id="legacy-flags",
        )
    )
    with store.connect() as conn:
        conn.execute(
            "UPDATE lorebook_entries SET enabled = ?, constant = ?, regex = ? WHERE lorebook_id = ?",
            ("false", "false", "false", lorebook_id),
        )

    bound = await runtime.handle_command(
        RPCommand("lore", ["use", lorebook_id], f"/rp lore use {lorebook_id}"), Event()
    )
    inspected = await runtime.handle_command(
        RPCommand("lore", ["inspect", lorebook_id], f"/rp lore inspect {lorebook_id}"), Event()
    )
    debugged = await runtime.handle_command(RPCommand("lore", ["debug"], "/rp lore debug"), Event())
    tested = await runtime.handle_command(RPCommand("lore", ["test", "moon"], "/rp lore test moon"), Event())

    assert "enabled entries: 0" in bound
    assert "entries: 1 total, 0 enabled, 0 constant, 0 regex" in inspected
    assert "Legacy entry [disabled]: keys=[moon]" in inspected
    assert "Legacy entry: disabled, keys=['moon']" in debugged
    assert "Lorebook test: 0 matched, 1 excluded, tokens: 0" in tested


@pytest.mark.asyncio
async def test_lore_runtime_rejects_nested_quantifier_without_crash(tmp_path):
    path = tmp_path / "atlas.json"
    path.write_text(json.dumps({
        "name": "Atlas",
        "entries": [{"comment": "Nested", "content": "Nested lore", "keys": ["(a+)+"], "regex": True}],
    }), encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    await runtime.handle_command(RPCommand("lore", ["import", str(path)], "/rp lore import"), Event())
    await runtime.handle_command(RPCommand("lore", ["use", "Atlas"], "/rp lore use Atlas"), Event())
    tested = await runtime.handle_command(RPCommand("lore", ["test", "aaa"], "/rp lore test aaa"), Event())

    assert "regex rejected: nested quantifier" in tested
    assert "Nested lore" not in tested


@pytest.mark.asyncio
async def test_lore_runtime_inspect_and_debug_tolerate_bad_key_json(tmp_path):
    """Inspect and debug keep a healthy entry when stored key JSON is unusable."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session_key = "telegram:chat:chat-1:thread:main:user:user-1"
    store.start_session(session_key)
    runtime = TavernRuntime(store)
    lorebook = ImportedLorebook(
        name="KeyGuard",
        source="test",
        raw={"name": "KeyGuard"},
        entries=(
            ImportedLorebookEntry(
                id="HealthyMoon",
                title="HealthyMoon",
                content="HealthyMoon content",
                keys=("HealthyMoon",),
            ),
            ImportedLorebookEntry(
                id="MalformedKeys",
                title="MalformedKeys",
                content="MalformedKeys content",
                keys=("malformed-key",),
                secondary_keys=("malformed-secondary",),
            ),
            ImportedLorebookEntry(
                id="NonArrayKeys",
                title="NonArrayKeys",
                content="NonArrayKeys content",
                keys=("nonarray-key",),
                secondary_keys=("nonarray-secondary",),
            ),
        ),
        id="key-guard",
    )
    lorebook_id = store.save_lorebook(lorebook)
    with store.connect() as conn:
        malformed = conn.execute(
            "UPDATE lorebook_entries SET keys_json = ?, secondary_keys_json = ? WHERE lorebook_id = ? AND keys_json LIKE ?",
            ("{malformed", "[malformed-secondary", lorebook_id, "%malformed-key%"),
        )
        nonarray = conn.execute(
            "UPDATE lorebook_entries SET keys_json = ?, secondary_keys_json = ? WHERE lorebook_id = ? AND keys_json LIKE ?",
            ('{"ok":true}', '"nonarray-token"', lorebook_id, "%nonarray-key%"),
        )
        assert malformed.rowcount == 1
        assert nonarray.rowcount == 1
    store.set_session_lorebook(session_key, lorebook_id)

    inspected = await runtime.handle_command(
        RPCommand("lore", ["inspect", lorebook_id], f"/rp lore inspect {lorebook_id}"),
        Event(),
    )
    debug = await runtime.handle_command(RPCommand("lore", ["debug"], "/rp lore debug"), Event())

    assert "HealthyMoon" in inspected
    assert "HealthyMoon" in debug
    assert "Traceback" not in inspected
    assert "Traceback" not in debug
    assert "secondary=" not in inspected
    assert "keys=['HealthyMoon']" in debug
    for title in ("MalformedKeys", "NonArrayKeys"):
        assert f"{title} [enabled]: keys=[none]" in inspected
        assert f"{title}: enabled, keys=[]" in debug


@pytest.mark.asyncio
async def test_lore_runtime_inspect_handles_numeric_refs_pagination_and_invalid_decimals(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    numeric_name_id = store.save_lorebook(
        ImportedLorebook(
            name="Archive ²",
            source="test",
            raw={"name": "Archive ²"},
            entries=(ImportedLorebookEntry(id="numeric-ref", title="Numeric reference", content="content", keys=("ref",)),),
            id="numeric-reference",
        ),
    )
    paged_id = store.save_lorebook(
        ImportedLorebook(
            name="Paged",
            source="test",
            raw={"name": "Paged"},
            entries=tuple(
                ImportedLorebookEntry(id=f"entry-{index}", title=f"Entry {index}", content="content", keys=("page",))
                for index in range(1, 4)
            ),
            id="paged-reference",
        ),
    )

    numeric_name = await runtime.handle_command(
        RPCommand("lore", ["inspect", "Archive", "²"], "/rp lore inspect Archive ²"), Event()
    )
    unicode_decimal_page = await runtime.handle_command(
        RPCommand("lore", ["inspect", paged_id, "٢", "٢"], f"/rp lore inspect {paged_id} ٢ ٢"), Event()
    )
    clamped_page = await runtime.handle_command(
        RPCommand("lore", ["inspect", paged_id, "99", "99"], f"/rp lore inspect {paged_id} 99 99"), Event()
    )
    digit_limit = sys.int_info.str_digits_check_threshold
    too_long_decimal = "9" * (digit_limit + 1)
    original_digit_limit = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(digit_limit)
    try:
        invalid_limit = await runtime.handle_command(
            RPCommand("lore", ["inspect", paged_id, too_long_decimal], "/rp lore inspect"), Event()
        )
        invalid_page = await runtime.handle_command(
            RPCommand("lore", ["inspect", paged_id, "1", too_long_decimal], "/rp lore inspect"), Event()
        )
    finally:
        sys.set_int_max_str_digits(original_digit_limit)

    assert numeric_name_id == "numeric-reference"
    assert "Lorebook: Archive ²" in numeric_name
    assert "showing entries 3-3 of 3 (page 2/2)" in unicode_decimal_page
    assert "showing entries 1-3 of 3 (page 1/1)" in clamped_page
    assert invalid_limit == "Usage: /rp lore inspect <lorebook> [limit] [page]"
    assert invalid_page == "Usage: /rp lore inspect <lorebook> [limit] [page]"


@pytest.mark.asyncio
async def test_lore_runtime_inspect_hides_legacy_blob_content_preview(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    lorebook_id = store.save_lorebook(
        ImportedLorebook(
            name="BlobPreview",
            source="legacy",
            raw={"name": "BlobPreview"},
            entries=(
                ImportedLorebookEntry(
                    id="blob-entry",
                    title="Blob entry",
                    content="Text that will be replaced by a legacy blob.",
                    keys=("blob",),
                ),
                ImportedLorebookEntry(
                    id="text-entry",
                    title="Text entry",
                    content="Valid preview text",
                    keys=("text",),
                ),
            ),
            id="blob-preview",
        )
    )
    with store.connect() as conn:
        updated = conn.execute(
            "UPDATE lorebook_entries SET content = ? WHERE lorebook_id = ? AND id = ?",
            (b"\x80legacy-preview", lorebook_id, f"{lorebook_id}:blob-entry"),
        )
        assert updated.rowcount == 1

    inspected = await runtime.handle_command(
        RPCommand("lore", ["inspect", lorebook_id], f"/rp lore inspect {lorebook_id}"), Event()
    )

    assert "Blob entry [enabled]: keys=[blob] — " in inspected
    assert "b'\\x80legacy-preview'" not in inspected
    assert "Text entry [enabled]: keys=[text] — Valid preview text" in inspected
