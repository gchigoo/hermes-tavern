from __future__ import annotations

from hermes_tavern.commands import RPCommand, _build_help_text
from hermes_tavern.db import TavernStore
from hermes_tavern.importers.cards import parse_character_card
from hermes_tavern.importers.lorebooks import import_st_lorebook_json
from hermes_tavern.importers.personas import import_raw_persona_text
from hermes_tavern.importers.presets import import_st_preset_json
from hermes_tavern.runtime import TavernRuntime


SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"
OTHER_SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-2"


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()


def _doctor(runtime: TavernRuntime, event: object = Event()) -> str:
    return runtime.handle_command_sync(RPCommand("doctor", [], "/rp doctor"), event)


def _seed_assets(store: TavernStore) -> str:
    card_id = store.save_card(parse_character_card({"name": "Alice"}))
    store.save_preset(
        import_st_preset_json(
            {"name": "Writer", "prompts": [{"name": "style", "content": "Write plainly."}]}
        )
    )
    store.save_lorebook(
        import_st_lorebook_json(
            {"name": "Library", "entries": {"0": {"key": ["library"], "content": "Old books."}}}
        )
    )
    store.save_persona(import_raw_persona_text("I am the reader.", name="Reader"))
    return card_id


def test_doctor_no_active_session_reports_counts_and_start_hint(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    _seed_assets(store)
    runtime = TavernRuntime(store)

    response = _doctor(runtime)

    assert "Hermes Tavern doctor" in response
    assert f"db path: {tmp_path / 'tavern.sqlite3'}" in response
    assert f"scope key: {SESSION_KEY}" in response
    assert "session status: none" in response
    assert "session id: none" in response
    assert "session card: none" in response
    assert "cards: 1" in response
    assert "presets: 1" in response
    assert "lorebooks: 1" in response
    assert "personas: 1" in response
    assert "model mode: fake (default)" in response
    assert "image provider: MockImageProvider/mock" in response
    assert "tts configured: no" in response
    assert "/rp start <card>" in response
    assert "/rp card import <file>" in response


def test_doctor_active_session_reports_same_scope_only(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    alice_id = store.save_card(parse_character_card({"name": "Alice"}))
    leak_id = store.save_card(parse_character_card({"name": "ScopeLeakBob"}))
    session = store.start_session(SESSION_KEY, alice_id)
    other = store.start_session(OTHER_SESSION_KEY, leak_id)
    store.set_session_adapter_mode(SESSION_KEY, "hermes")
    runtime = TavernRuntime(store)

    response = _doctor(runtime)

    assert "session status: active" in response
    assert f"session id: {session['id'][:8]}" in response
    assert "session card: Alice" in response
    assert "model mode: hermes" in response
    assert "ScopeLeakBob" not in response
    assert other["id"][:8] not in response
    assert OTHER_SESSION_KEY not in response


def test_doctor_paused_session_reports_resume_hint_and_same_scope_only(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    alice_id = store.save_card(parse_character_card({"name": "Alice"}))
    leak_id = store.save_card(parse_character_card({"name": "PausedScopeLeakBob"}))
    session = store.start_session(SESSION_KEY, alice_id)
    other = store.start_session(OTHER_SESSION_KEY, leak_id)
    assert store.pause_session(SESSION_KEY) is True
    assert store.pause_session(OTHER_SESSION_KEY) is True
    runtime = TavernRuntime(store)

    response = _doctor(runtime)

    assert "session status: paused" in response
    assert f"session id: {session['id'][:8]}" in response
    assert "session card: Alice" in response
    assert "next: resume with /rp resume" in response
    assert "PausedScopeLeakBob" not in response
    assert other["id"][:8] not in response
    assert OTHER_SESSION_KEY not in response


def test_doctor_missing_event_and_broken_store_do_not_raise_internal_error(tmp_path):
    class BrokenEvent:
        def __getattr__(self, name):
            raise RuntimeError(f"event field unavailable: {name}")

    class BrokenStore:
        @property
        def db_path(self):
            raise RuntimeError("db path unavailable")

        def get_active_session(self, session_key):
            raise RuntimeError("active lookup failed")

        def list_cards(self):
            raise RuntimeError("cards failed")

        def list_presets(self):
            raise RuntimeError("presets failed")

        def list_lorebooks(self):
            raise RuntimeError("lorebooks failed")

        def count_personas(self):
            raise RuntimeError("personas failed")

    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store = BrokenStore()

    response = _doctor(runtime, BrokenEvent())

    assert "Hermes Tavern doctor" in response
    assert "internal error" not in response
    assert "db path: unknown" in response
    assert "scope key: unknown:chat:unknown:thread:main:user:unknown" in response
    assert "session status: error" in response
    assert "cards: error" in response
    assert "presets: error" in response
    assert "lorebooks: error" in response
    assert "personas: error" in response


def test_help_includes_doctor_command():
    assert "/rp doctor" in _build_help_text()
