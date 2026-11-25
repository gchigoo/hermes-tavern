import json
import sqlite3
from copy import deepcopy
from pathlib import Path

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.personas import ImportedPersona, import_persona_file
from plugins.hermes_tavern.importers import MAX_LOCAL_IMPORT_BYTES
from plugins.hermes_tavern.runtime import TavernRuntime


SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"
    user_name = "Steven"


class Event:
    source = Source()
    text = ""


class RecordingAdapter:
    def __init__(self):
        self.messages = []

    def generate(self, messages, profile):
        del profile
        self.messages = messages
        return "recorded reply"


def _extract_export_paths(response: str) -> tuple[str, str]:
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split('MEDIA:"', 1)[1].split('"', 1)[0]
    return file_path, media_path


def _runtime_with_home(tmp_path: Path, store: TavernStore, monkeypatch) -> TavernRuntime:
    monkeypatch.setattr("plugins.hermes_tavern.runtime_persona.get_hermes_home", lambda: tmp_path)
    return TavernRuntime(store)


def _count_sessions(store: TavernStore) -> int:
    with store.connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]


def test_persona_schema_migration_and_store_helpers(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)
    store.migrate()
    store.migrate()

    with sqlite3.connect(db_path) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        session_cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)")}

    assert "personas" in tables
    assert "persona_id" in session_cols

    path = tmp_path / "pilot.json"
    path.write_text(
        json.dumps(
            {
                "name": "Pilot",
                "persona": "I am {{user}}, a careful pilot.",
                "api_key": "must-not-persist",
            }
        ),
        encoding="utf-8",
    )
    persona = import_persona_file(path)
    persona_id = store.save_persona(persona)

    assert store.count_personas() == 1
    assert store.get_persona(persona_id[:8])["name"] == "Pilot"
    assert store.get_persona("Pilot")["id"] == persona_id
    assert "api_key" not in store.get_persona("Pilot")["raw_json"]

    store.start_session(SESSION_KEY)
    assert store.set_session_persona(SESSION_KEY, persona_id)
    assert store.get_active_session(SESSION_KEY)["persona_id"] == persona_id
    assert store.set_session_persona(SESSION_KEY, None)
    assert store.get_active_session(SESSION_KEY)["persona_id"] is None


def test_persona_import_supports_raw_text(tmp_path):
    path = tmp_path / "traveler.txt"
    path.write_text("I am {{user}}, a patient traveler.", encoding="utf-8")

    persona = import_persona_file(path)

    assert persona.name == "traveler"
    assert persona.content == "I am {{user}}, a patient traveler."
    assert persona.source_path == str(path)
    assert persona.raw_json["format"] == "raw_text"


@pytest.mark.parametrize(
    ("names", "expected"),
    [
        (
            {"name": " Primary  Name ", "persona_name": "Persona", "user_name": "User"},
            "Primary Name",
        ),
        (
            {"name": " \t", "persona_name": " 林  薇 ", "user_name": "User"},
            "林 薇",
        ),
        ({"persona_name": "\u3000", "user_name": " User Name "}, "User Name"),
        ({"name": "", "persona_name": " \t", "user_name": "\n"}, "filename"),
        ({}, "filename"),
        ({"name": 42, "persona_name": "Persona"}, "42"),
        ({"name": 0, "persona_name": "Persona"}, "Persona"),
        ({"name": True, "persona_name": "Persona"}, "Persona"),
        ({"name": False, "persona_name": True, "user_name": "User"}, "User"),
        ({"name": False, "persona_name": False, "user_name": "User"}, "User"),
        ({"name": True, "persona_name": False, "user_name": True}, "filename"),
        ({"name": {"label": "Object"}, "persona_name": ["List"], "user_name": "User"}, "User"),
        ({"name": ["List"], "persona_name": {"label": "Object"}}, "filename"),
    ],
    ids=[
        "priority", "blank-name", "blank-persona-name", "all-blank", "absent",
        "truthy-number", "falsy-number", "true-name", "false-name-true-persona-name",
        "false-aliases", "boolean-only", "structured-aliases", "structured-without-name",
    ],
)
def test_persona_import_json_name_priority(tmp_path, names, expected):
    payload = {
        **names,
        "description": "  Unicode · 内容  ",
        "extensions": {"tags": ["extra"]},
    }
    path = tmp_path / "filename.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    persona = import_persona_file(path)

    assert persona.name == expected
    assert persona.content == "Unicode · 内容"
    assert persona.source_path == str(path)
    assert persona.raw_json == payload


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_persona_import_unicode_json_sanitizes_secrets(tmp_path, encoding):
    """UTF-8 and UTF-8-SIG JSON keep Unicode name/content and drop secrets."""
    payload = {
        "name": "林薇",
        "persona": "我是 {{user}}，学者 · Élodie。",
        "api_key": "must-not-persist",
        "token": "must-not-show",
        "password": "must-not-keep",
    }
    path = tmp_path / "lin.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding=encoding)

    persona = import_persona_file(path)
    stored = json.dumps(persona.raw_json, ensure_ascii=False)

    assert persona.name == "林薇"
    assert persona.content == "我是 {{user}}，学者 · Élodie。"
    assert persona.source_path == str(path)
    assert persona.raw_json["name"] == "林薇"
    assert persona.raw_json["persona"] == persona.content
    assert persona.raw_json.get("format") != "raw_text"
    for secret_key in ("api_key", "token", "password"):
        assert secret_key not in persona.raw_json
    assert "must-not-persist" not in stored
    assert "must-not-show" not in stored
    assert "must-not-keep" not in stored
    assert "\ufeff" not in persona.name
    assert "\ufeff" not in persona.content


def test_persona_import_removes_nested_credential_aliases(tmp_path):
    path = tmp_path / "observer.json"
    path.write_text(json.dumps({
        "name": "Observer",
        "description": "Keeps a field journal.",
        "apiKey": "fake-root-key",
        "extensions": [{
            "accessToken": "fake-nested-token",
            "API_KEY": "fake-nested-key",
            "accessTokenLabel": "keep this label",
        }],
    }), encoding="utf-8")

    persona = import_persona_file(path)

    assert persona.content == "Keeps a field journal."
    assert persona.raw_json == {
        "name": "Observer",
        "description": "Keeps a field journal.",
        "extensions": [{"accessTokenLabel": "keep this label"}],
    }


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
@pytest.mark.parametrize(
    ("filename", "body"),
    [
        ("traveler.txt", "我是 {{user}}，耐心的旅人 · Élodie。"),
        ("broken.json", '{"name": "林薇", "persona": "未闭合'),
    ],
    ids=["raw-text", "malformed-json"],
)
def test_persona_import_raw_text_and_malformed_json_fallback(tmp_path, encoding, filename, body):
    """UTF-8 and UTF-8-SIG raw text or malformed JSON stay on the raw-text path."""
    path = tmp_path / filename
    path.write_text(body, encoding=encoding)

    persona = import_persona_file(path)

    assert persona.name == path.stem
    assert persona.content == body.strip()
    assert persona.source_path == str(path)
    assert persona.raw_json == {"format": "raw_text", "source_path": str(path)}
    assert "\ufeff" not in persona.name
    assert "\ufeff" not in persona.content


def test_persona_import_rejects_oversize_json(tmp_path):
    path = tmp_path / "oversize-persona.json"
    payload = {"name": "Pilot", "persona": "A" * (MAX_LOCAL_IMPORT_BYTES + 1)}
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="too large"):
        import_persona_file(path)


def test_persona_import_rejects_oversize_text(tmp_path):
    path = tmp_path / "oversize-persona.txt"
    path.write_text("A" * (MAX_LOCAL_IMPORT_BYTES + 1), encoding="utf-8")

    with pytest.raises(ValueError, match="too large"):
        import_persona_file(path)


@pytest.mark.asyncio
async def test_persona_runtime_commands_import_list_inspect_use_debug_clear(tmp_path):
    path = tmp_path / "navigator.json"
    path.write_text(
        json.dumps({"name": "Navigator", "persona": "I am {{user}}, a star navigator."}),
        encoding="utf-8",
    )
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    imported = await runtime.handle_command(
        RPCommand("persona", ["import", str(path)], "/rp persona import"),
        Event(),
    )
    listed = await runtime.handle_command(RPCommand("persona", ["list"], "/rp persona list"), Event())
    inspected = await runtime.handle_command(
        RPCommand("persona", ["inspect", "Navigator"], "/rp persona inspect Navigator"),
        Event(),
    )
    bound = await runtime.handle_command(
        RPCommand("persona", ["use", "Navigator"], "/rp persona use Navigator"),
        Event(),
    )
    debug = await runtime.handle_command(RPCommand("persona", ["debug"], "/rp persona debug"), Event())
    cleared = await runtime.handle_command(RPCommand("persona", ["clear"], "/rp persona clear"), Event())

    assert "Imported Hermes Tavern persona: Navigator" in imported
    assert "Navigator" in listed
    assert "preview:" in inspected
    assert "raw_json" not in inspected
    assert '"name"' not in inspected
    assert "persona bound" in bound
    assert "module: persona:Navigator" in debug
    assert "I am {{user}}, a star navigator." in debug
    assert "persona cleared" in cleared
    assert store.get_active_session(SESSION_KEY)["persona_id"] is None


@pytest.mark.parametrize("suffix", [".txt", ".json"])
def test_persona_import_reports_invalid_utf8_without_saving(tmp_path, suffix):
    path = tmp_path / f"invalid{suffix}"
    path.write_bytes(b"Persona text\xff")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    result = runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], "/rp persona import"), Event()
    )

    assert result == "Persona import failed: save the file as UTF-8 and try again."
    assert store.list_personas() == []


@pytest.mark.asyncio
async def test_persona_new_creates_reusable_persona(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    created = await runtime.handle_command(
        RPCommand("persona", ["new", "Pilot", "I", "am", "{{user}},", "a", "careful", "pilot."], "/rp persona new"),
        Event(),
    )
    listed = await runtime.handle_command(RPCommand("persona", ["list"], "/rp persona list"), Event())

    assert "persona created: Pilot" in created
    assert "use: /rp persona use" in created
    assert "Pilot" in listed
    assert "careful pilot" in listed


@pytest.mark.asyncio
async def test_persona_temp_creates_and_binds_to_active_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    bound = await runtime.handle_command(
        RPCommand("persona", ["temp", "I", "am", "{{user}},", "the", "pilot."], "/rp persona temp"),
        Event(),
    )
    debug = await runtime.handle_command(RPCommand("persona", ["debug"], "/rp persona debug"), Event())

    assert "temporary persona bound" in bound
    assert store.get_active_session(SESSION_KEY)["persona_id"]
    assert "module: persona:temporary" in debug
    assert "I am {{user}}, the pilot." in debug


@pytest.mark.asyncio
async def test_persona_prompt_injection_macro_expansion_and_clear(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    persona_id = store.save_persona(
        import_persona_file(
            _write_text(tmp_path / "pilot.txt", "I am {{user}}, a careful pilot for {{char}}.")
        )
    )
    store.set_session_persona(SESSION_KEY, persona_id)

    prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    store.set_session_persona(SESSION_KEY, None)
    cleared_prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "persona:" in prompt
    assert "persona:pilot" in prompt
    assert "I am Steven, a careful pilot for Alice." in prompt
    assert "persona:pilot" not in cleared_prompt


@pytest.mark.asyncio
async def test_persona_active_generation_receives_module(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    adapter = RecordingAdapter()
    runtime = TavernRuntime(store, hermes_adapter=adapter)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    persona_id = store.save_persona(
        import_persona_file(_write_text(tmp_path / "pilot.txt", "I am {{user}}, the pilot."))
    )
    store.set_session_persona(SESSION_KEY, persona_id)
    store.set_session_adapter_mode(SESSION_KEY, "hermes")
    store.set_session_live_confirmed(SESSION_KEY, True)

    event = Event()
    event.text = "Hello"
    reply = await runtime.handle_active_message(event)

    assert reply == "recorded reply"
    assert any(m["role"] == "system" and "I am Steven, the pilot." in m["content"] for m in adapter.messages)


@pytest.mark.asyncio
async def test_persona_pagination_and_inspect_do_not_emit_raw_json(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    for idx in range(3):
        path = tmp_path / f"persona-{idx}.json"
        path.write_text(
            json.dumps(
                {
                    "name": f"Persona {idx}",
                    "persona": f"Persona body {idx}",
                    "token": "must-not-show",
                }
            ),
            encoding="utf-8",
        )
        store.save_persona(import_persona_file(path))

    page_1 = await runtime.handle_command(RPCommand("persona", ["list", "2", "1"], "/rp persona list 2 1"), Event())
    page_2 = await runtime.handle_command(RPCommand("persona", ["list", "2", "2"], "/rp persona list 2 2"), Event())
    inspected = await runtime.handle_command(
        RPCommand("persona", ["inspect", "Persona", "0"], "/rp persona inspect Persona 0"),
        Event(),
    )

    assert "page 1/2" in page_1
    assert "next: /rp persona list 2 2" in page_1
    assert "page 2/2" in page_2
    assert "prev: /rp persona list 2 1" in page_2
    assert "raw_json" not in inspected
    assert "token" not in inspected
    assert "must-not-show" not in inspected
    assert "{" not in inspected and "}" not in inspected


def test_persona_runtime_export_uses_stored_raw_json_when_available(tmp_path, monkeypatch):
    path = tmp_path / "pilot.json"
    path.write_text(
        json.dumps(
            {
                "format": "raw_text",
                "name": "Pilot",
                "persona": "I am {{user}}, a careful pilot.",
                "api_key": "must-not-persist",
            }
        ),
        encoding="utf-8",
    )
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], f"/rp persona import {path}"),
        Event(),
    )
    response = runtime.handle_command_sync(
        RPCommand("persona", ["export", "Pilot"], "/rp persona export Pilot"),
        Event(),
    )

    file_path, media_path = _extract_export_paths(response)
    payload = json.loads(Path(file_path).read_text(encoding="utf-8"))

    assert media_path == file_path
    assert "Persona exported as JSON." in response
    assert payload == json.loads(store.get_persona("Pilot")["raw_json"])


def test_persona_runtime_export_falls_back_for_invalid_or_missing_raw_json(tmp_path, monkeypatch):
    path = tmp_path / "fallback.txt"
    path.write_text("I am {{user}}, a careful pilot.", encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], f"/rp persona import {path}"),
        Event(),
    )
    persona = store.get_persona("fallback")
    assert persona is not None
    with store.connect() as conn:
        conn.execute(
            "UPDATE personas SET raw_json = ? WHERE id = ?",
            (json.dumps(["not", "an", "object"]), persona["id"]),
        )
        conn.execute(
            "UPDATE personas SET source_path = ? WHERE id = ?",
            ("", persona["id"]),
        )

    response = runtime.handle_command_sync(
        RPCommand("persona", ["export", persona["id"]], f"/rp persona export {persona['id']}"),
        Event(),
    )
    file_path, _ = _extract_export_paths(response)
    payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
    person = store.get_persona(persona["id"])
    assert person is not None

    assert payload == {
        "name": person["name"],
        "content": person.get("content") or "",
        "source_path": "unknown",
        "created_at": person.get("created_at", ""),
    }


@pytest.mark.parametrize(
    ("aliases", "expected_name", "needs_name", "legacy_name"),
    [
        ({}, "林薇", True, None),
        ({"name": " ", "persona_name": "\t", "user_name": "\u3000"}, "林薇", True, None),
        ({"name": " ", "user_name": "  远洋\t 航海员  "}, "远洋 航海员", False, None),
        ({"name": 42}, "42", False, None),
        ({"name": ["List"], "persona_name": {"label": "Object"}}, "林薇", True, None),
        ({"name": {"label": "Object"}, "user_name": "航海员"}, "航海员", False, None),
        ({"name": True, "persona_name": False, "user_name": "航海员"}, "航海员", False, None),
        ({"name": True, "persona_name": False, "user_name": True}, "林薇", True, None),
        ({"name": True, "user_name": "航海员"}, "航海员", True, "True"),
        ({"name": True}, "林薇", True, "True"),
    ],
)
def test_persona_runtime_export_round_trips_json_name(
    tmp_path, monkeypatch, aliases, expected_name, needs_name, legacy_name,
):
    path = tmp_path / "林薇.json"
    original = {**aliases, "description": "我是 {{user}}。", "extensions": {"tags": ["航海"]}}
    path.write_text(json.dumps(original, ensure_ascii=False), encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], f"/rp persona import {path}"), Event(),
    )
    before = store.get_persona(expected_name)
    assert before is not None
    if legacy_name is not None:
        with store.connect() as conn:
            conn.execute("UPDATE personas SET name = ? WHERE id = ?", (legacy_name, before["id"]))
        expected_name = legacy_name
        before = store.get_persona(expected_name)
        assert before is not None
    assert json.loads(before["raw_json"]) == original

    response = runtime.handle_command_sync(
        RPCommand("persona", ["export", expected_name], f"/rp persona export {expected_name}"), Event(),
    )
    exported_path, _ = _extract_export_paths(response)
    assert Path(exported_path).stem != expected_name
    expected_payload = {**original, "name": expected_name} if needs_name else original
    assert json.loads(Path(exported_path).read_text(encoding="utf-8")) == expected_payload

    fresh_store = TavernStore(tmp_path / "reimport.sqlite3")
    TavernRuntime(fresh_store).handle_command_sync(
        RPCommand("persona", ["import", exported_path], f"/rp persona import {exported_path}"), Event(),
    )
    reimported = fresh_store.get_persona(expected_name)
    assert reimported is not None
    assert reimported["content"] == before["content"] == original["description"]
    assert store.get_persona(expected_name) == before


@pytest.mark.parametrize(
    ("raw_json", "stored_content", "expected_updates", "expected_content"),
    [
        pytest.param({}, "我是 {{user}}。", {"persona": "我是 {{user}}。"}, "我是 {{user}}。", id="empty-json"),
        pytest.param(
            {"persona_name": "Old name", "extensions": {"tags": ["航海"]}},
            "我是 {{user}}。",
            {"persona": "我是 {{user}}。"},
            "我是 {{user}}。",
            id="metadata-only",
        ),
        pytest.param(
            {"persona": {"legacy": True}, "description": " \t", "content": ["legacy"]},
            "Stored persona",
            {"persona": "Stored persona"},
            "Stored persona",
            id="unusable-aliases",
        ),
        pytest.param({"extensions": {}}, " \t", {}, "", id="blank-stored-content"),
        pytest.param(
            {"persona": {"legacy": True}, "description": " \t", "profile": "  Existing alias  "},
            "Different stored content",
            {},
            "Existing alias",
            id="valid-alias",
        ),
    ],
)
def test_persona_runtime_export_round_trips_legacy_content(
    tmp_path, monkeypatch, raw_json, stored_content, expected_updates, expected_content,
):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    name = "Legacy"
    persona_id = store.save_persona(
        ImportedPersona(
            id="legacy-id", name=name, content=stored_content, source_path="legacy.json", raw_json=raw_json,
        ),
    )
    before = store.get_persona(persona_id)
    assert before is not None

    response = runtime.handle_command_sync(
        RPCommand("persona", ["export", name], f"/rp persona export {name}"), Event(),
    )
    exported_path, _ = _extract_export_paths(response)

    fresh_store = TavernStore(tmp_path / "reimport.sqlite3")
    result = TavernRuntime(fresh_store).handle_command_sync(
        RPCommand("persona", ["import", exported_path], f"/rp persona import {exported_path}"), Event(),
    )
    reimported = fresh_store.get_persona(name)
    if expected_content:
        assert reimported is not None
        assert reimported["content"] == expected_content
    else:
        assert result == "Persona import failed: empty persona content."
        assert reimported is None
    assert json.loads(Path(exported_path).read_text(encoding="utf-8")) == {
        **raw_json, **expected_updates, "name": name,
    }
    assert store.get_persona(persona_id) == before


def test_persona_runtime_export_round_trips_raw_text(tmp_path, monkeypatch):
    """Plain Unicode text exports as JSON and re-imports with the same name and content."""
    original = "我是 {{user}}，耐心的旅人 · Élodie。"
    path = tmp_path / "traveler.txt"
    path.write_text(original, encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], f"/rp persona import {path}"),
        Event(),
    )
    response = runtime.handle_command_sync(
        RPCommand("persona", ["export", "traveler"], "/rp persona export traveler"),
        Event(),
    )
    file_path = _extract_export_paths(response)[0]

    fresh_store = TavernStore(tmp_path / "reimport.sqlite3")
    fresh_runtime = TavernRuntime(fresh_store)
    reimported = fresh_runtime.handle_command_sync(
        RPCommand("persona", ["import", file_path], f"/rp persona import {file_path}"),
        Event(),
    )
    imported = fresh_store.get_persona("traveler")

    assert "Imported Hermes Tavern persona: traveler" in reimported
    assert imported is not None
    assert imported["name"] == path.stem
    assert imported["content"] == original


def test_persona_runtime_export_usage_with_last_and_not_found(tmp_path, monkeypatch):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("I am {{user}}, first.", encoding="utf-8")
    second.write_text("I am {{user}}, second.", encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(first)], f"/rp persona import {first}"),
        Event(),
    )
    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(second)], f"/rp persona import {second}"),
        Event(),
    )
    response = runtime.handle_command_sync(
        RPCommand("persona", ["export", "last"], "/rp persona export last"),
        Event(),
    )
    usage = runtime.handle_command_sync(RPCommand("persona", ["export"], "/rp persona export"), Event())
    not_found = runtime.handle_command_sync(
        RPCommand("persona", ["export", "Missing"], "/rp persona export Missing"),
        Event(),
    )

    path = _extract_export_paths(response)[0]
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    stored = store.get_persona("last")
    assert stored is not None
    assert payload == {
        "name": stored["name"],
        "content": stored.get("content") or "",
        "source_path": stored.get("source_path") or "unknown",
        "created_at": stored.get("created_at", ""),
    }
    assert usage == "Usage: /rp persona export <persona>"
    assert not_found == "Persona not found: Missing"


def test_persona_runtime_export_quotes_media_path_with_spaces(tmp_path, monkeypatch):
    path = tmp_path / "spacing.txt"
    path.write_text("I am {{user}}, spaced.", encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home with spaces", store, monkeypatch)

    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], f"/rp persona import {path}"),
        Event(),
    )
    response = runtime.handle_command_sync(
        RPCommand("persona", ["export", "spacing"], "/rp persona export spacing"),
        Event(),
    )
    file_path, media_path = _extract_export_paths(response)
    exports_dir = tmp_path / "hermes home with spaces" / "plugins" / "hermes-tavern" / "exports" / "personas"

    assert media_path == file_path
    assert f'MEDIA:"{file_path}"' in response
    assert " " in file_path
    assert Path(file_path).exists()
    assert str(Path(file_path)).startswith(str(exports_dir))


def test_persona_runtime_export_path_is_within_persona_exports_directory(tmp_path, monkeypatch):
    path = tmp_path / "path.json"
    path.write_text(
        json.dumps({"name": "Path", "persona": "I am {{user}}, a pilot."}),
        encoding="utf-8",
    )
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], f"/rp persona import {path}"),
        Event(),
    )
    persona = store.get_persona("Path")
    assert persona is not None
    with store.connect() as conn:
        conn.execute("UPDATE personas SET id = ? WHERE id = ?", ("../../../../outside", persona["id"]))
        conn.execute(
            "UPDATE personas SET raw_json = ? WHERE id = ?",
            (json.dumps({"name": "Injected", "persona": "I am {{user}}"}), "../../../../outside"),
        )

    response = runtime.handle_command_sync(
        RPCommand("persona", ["export", "../../../../outside"], "/rp persona export ../../../../outside"),
        Event(),
    )
    file_path = _extract_export_paths(response)[0]
    export_dir = tmp_path / "hermes home" / "plugins" / "hermes-tavern" / "exports" / "personas"
    export_path = Path(file_path)

    assert export_path.parent == export_dir
    assert export_path.resolve().is_relative_to(export_dir.resolve())


def test_persona_runtime_export_does_not_create_or_alter_sessions_or_messages(tmp_path, monkeypatch):
    path = tmp_path / "stable.txt"
    path.write_text("I am {{user}}, stable.", encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], f"/rp persona import {path}"),
        Event(),
    )
    persona = store.get_persona("stable")
    assert persona is not None

    store.start_session(SESSION_KEY)
    store.append_message(store.get_active_session(SESSION_KEY)["id"], "user", "before export")
    session_count_before = _count_sessions(store)
    session_before = deepcopy(store.get_active_session(SESSION_KEY))
    messages_before = deepcopy(store.get_recent_messages(session_before["id"]))

    runtime.handle_command_sync(
        RPCommand("persona", ["export", persona["name"]], f"/rp persona export {persona['name']}"),
        Event(),
    )

    session_after = store.get_active_session(SESSION_KEY)
    assert session_after is not None
    messages_after = deepcopy(store.get_recent_messages(session_after["id"]))
    session_count_after = _count_sessions(store)

    assert session_count_before == session_count_after
    assert session_before == session_after
    assert messages_before == messages_after


def test_persona_runtime_export_does_not_mutate_stored_persona_row(tmp_path, monkeypatch):
    path = tmp_path / "immutable.txt"
    path.write_text("I am {{user}}, immutable.", encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    runtime.handle_command_sync(
        RPCommand("persona", ["import", str(path)], f"/rp persona import {path}"),
        Event(),
    )
    persona = store.get_persona("immutable")
    assert persona is not None
    before = deepcopy(persona)

    runtime.handle_command_sync(
        RPCommand("persona", ["export", "immutable"], "/rp persona export immutable"),
        Event(),
    )

    after = store.get_persona("immutable")
    assert after is not None
    assert before == after


def _write_text(path, text):
    path.write_text(text, encoding="utf-8")
    return path
