from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


class MalformedEvent:
    @property
    def source(self):
        raise RuntimeError("bad event")


def _runtime(tmp_path, tts_renderer=None) -> TavernRuntime:
    return TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"), tts_renderer=tts_renderer)


def _seed_active_session(runtime: TavernRuntime, count: int = 1) -> dict:
    for idx in range(count):
        runtime.store.save_card(
            parse_character_card({"name": f"Alice{idx}", "first_mes": f"Hello {idx}."})
        )
    runtime.handle_command_sync(RPCommand("start", ["Alice0"], "/rp start Alice0"), Event())
    return runtime.store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")


def test_unknown_command_returns_graceful_error(tmp_path):
    runtime = _runtime(tmp_path)

    response = runtime.handle_command_sync(RPCommand("nope", [], "/rp nope"), Event())

    assert response == "Unknown /rp command: nope"


def test_malformed_event_does_not_crash(tmp_path):
    runtime = _runtime(tmp_path)

    response = runtime.handle_command_sync(RPCommand("status", [], "/rp status"), MalformedEvent())

    assert isinstance(response, str)
    assert response


def test_extreme_history_limit_is_clamped_to_50(tmp_path):
    runtime = _runtime(tmp_path)
    session = _seed_active_session(runtime)
    for idx in range(60):
        runtime.store.append_message(session["id"], "user", f"user {idx}")

    response = runtime.handle_command_sync(RPCommand("history", ["999"], "/rp history 999"), Event())

    assert "50 shown, 61 total" in response
    assert "page 1/2" in response


def test_extreme_cards_limit_is_clamped_to_50(tmp_path):
    runtime = _runtime(tmp_path)
    _seed_active_session(runtime, count=60)

    response = runtime.handle_command_sync(RPCommand("cards", ["999"], "/rp cards 999"), Event())

    assert "50 shown" in response
    assert "page 1/2" in response


def test_top_level_command_exceptions_are_caught(tmp_path):
    runtime = _runtime(tmp_path)

    def boom(_event):
        raise RuntimeError("boom")

    runtime._status = boom

    response = runtime.handle_command_sync(RPCommand("status", [], "/rp status"), Event())

    assert response == "[Hermes Tavern: internal error]"


def test_provider_connection_error_returns_retry_hint(tmp_path):
    class BrokenAdapter:
        def generate(self, _messages, _descriptor):
            raise ConnectionError("provider down")

    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"), hermes_adapter=BrokenAdapter())
    response = runtime._generate_with_session_adapter(
        {"adapter_mode": "hermes", "live_confirmed": 1},
        [{"role": "user", "content": "hello"}],
        object(),
    )

    assert response == "[Hermes Tavern: provider unavailable — /rp retry to try again]"


def test_speak_and_voice_commands_are_mobile_safe(tmp_path):
    def fake_tts(text):
        assert text == "A short reply."
        return {
            "success": True,
            "file_path": str(tmp_path / "voice clip.mp3"),
            "media_tag": f"MEDIA:{tmp_path / 'voice clip.mp3'}",
            "provider": "fake-tts",
        }

    runtime = _runtime(tmp_path, tts_renderer=fake_tts)
    session = _seed_active_session(runtime)
    runtime.store.append_message(session["id"], "assistant", "A short reply.")

    speak = runtime.handle_command_sync(RPCommand("speak", [], "/rp speak"), Event())
    on = runtime.handle_command_sync(RPCommand("voice", ["on"], "/rp voice on"), Event())
    status = runtime.handle_command_sync(RPCommand("voice", [], "/rp voice"), Event())
    off = runtime.handle_command_sync(RPCommand("voice", ["off"], "/rp voice off"), Event())

    assert "Hermes Tavern speak: audio ready (fake-tts)." in speak
    assert f'MEDIA:"{tmp_path / "voice clip.mp3"}"' in speak
    assert on == "Hermes Tavern voice: on."
    assert status == "Hermes Tavern voice: on."
    assert off == "Hermes Tavern voice: off."
    assert all(len(item) < 220 for item in (speak, on, status, off))


def test_speak_preserves_voice_media_directive(tmp_path):
    def fake_tts(_text):
        return {
            "success": True,
            "file_path": str(tmp_path / "voice.ogg"),
            "media_tag": f"[[audio_as_voice]]\nMEDIA:{tmp_path / 'voice.ogg'}",
            "provider": "fake-tts",
        }

    runtime = _runtime(tmp_path, tts_renderer=fake_tts)
    session = _seed_active_session(runtime)
    runtime.store.append_message(session["id"], "assistant", "A short reply.")

    speak = runtime.handle_command_sync(RPCommand("speak", [], "/rp speak"), Event())

    assert "[[audio_as_voice]]" in speak
    assert f'MEDIA:"{tmp_path / "voice.ogg"}"' in speak
    from gateway.platforms.base import BasePlatformAdapter

    media_files, cleaned = BasePlatformAdapter.extract_media(speak)
    assert media_files == [(str(tmp_path / "voice.ogg"), True)]
    assert "MEDIA:" not in cleaned
    assert "[[audio_as_voice]]" not in cleaned


def test_speak_handles_tts_failure_without_leaking_details(tmp_path):
    runtime = _runtime(
        tmp_path,
        tts_renderer=lambda _text: {"success": False, "error": "secret provider stack trace"},
    )
    session = _seed_active_session(runtime)
    runtime.store.append_message(session["id"], "assistant", "A short reply.")

    speak = runtime.handle_command_sync(RPCommand("speak", [], "/rp speak"), Event())

    assert speak == "Hermes Tavern speak: TTS unavailable. Check Hermes TTS setup."
    assert "secret" not in speak
