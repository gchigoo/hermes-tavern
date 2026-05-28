"""Tests for ST-style Hermes Tavern image generation commands."""

from __future__ import annotations

from pathlib import Path
import json

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.images import GeneratedImage, ImagePrompt, compile_image_prompt, expand_image_template_macros
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.runtime import TavernRuntime


class FakeSource:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class FakeEvent:
    source = FakeSource()
    text = ""


SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


def _runtime(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card(
        {
            "name": "Alice",
            "description": "Alice has silver hair and blue eyes.",
            "personality": "calm, observant",
            "scenario": "A moonlit lakeside conversation.",
            "extensions": {
                "sd_character_prompt": {
                    "positive": "silver hair, blue eyes, elegant dress",
                    "negative": "low quality, blurry",
                }
            },
        }
    )
    store.save_card(card)
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    session = store.get_active_session(SESSION_KEY)
    return runtime, store, session, card


def test_compile_image_prompt_uses_st_character_prefix_and_scene_context(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    store.append_message(session["id"], "user", "The lake is bright tonight.")
    store.append_message(session["id"], "assistant", "Alice looks at the moon.")
    store.set_session_summary(SESSION_KEY, "Alice and the user are walking beside the lake.")

    prompt = compile_image_prompt(
        mode="scene",
        card=card,
        session=session,
        history=store.get_recent_messages(session["id"], limit=20),
        memory_summary=store.get_session_summary(SESSION_KEY)["summary"],
    )

    assert prompt.mode == "scenario"
    assert "silver hair" in prompt.prompt
    assert "moonlit lakeside" in prompt.prompt
    assert "Recent chat" in prompt.prompt
    assert "low quality" in prompt.negative_prompt


def test_image_prompt_generates_media_and_persists_job(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)

    response = runtime.handle_command_sync(
        RPCommand("image", ["prompt", "char", "standing", "under", "moonlight"], "/rp image prompt char standing under moonlight"),
        FakeEvent(),
    )

    assert "Hermes Tavern image generated." in response
    assert "mode: free" in response
    assert "MEDIA:" in response
    media_path = response.split("MEDIA:", 1)[1].strip()
    assert Path(media_path).exists()

    last = store.get_last_image_job(session["id"])
    assert last is not None
    assert last["status"] == "completed"
    assert last["provider"] == "mock"
    assert "silver hair" in last["prompt"]
    assert last["file_path"] == media_path


def test_image_scene_retry_and_inspect(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    store.append_message(session["id"], "user", "Alice steps onto the balcony.")

    first = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), FakeEvent())
    assert "mode: scenario" in first

    inspect = runtime.handle_command_sync(RPCommand("image", ["inspect"], "/rp image inspect"), FakeEvent())
    assert "Hermes Tavern image inspect" in inspect
    assert "provider: mock/placeholder-png" in inspect
    assert "cinematic scene" in inspect

    retry = runtime.handle_command_sync(RPCommand("image", ["retry"], "/rp image retry"), FakeEvent())
    assert "Hermes Tavern image generated." in retry
    assert "MEDIA:" in retry


def test_image_settings_and_no_active_session(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    settings = runtime.handle_command_sync(RPCommand("image", ["settings"], "/rp image settings"), FakeEvent())
    assert "modes: scene" in settings
    assert "provider: mock" in settings
    assert "- width: 1024" in settings

    class OtherSource(FakeSource):
        chat_id = "other"

    class OtherEvent:
        source = OtherSource()
        text = ""

    response = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), OtherEvent())
    assert "No active Hermes Tavern session" in response


def test_image_provider_list_use_and_safe_failure(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)

    providers = runtime.handle_command_sync(RPCommand("image", ["provider", "list"], "/rp image provider list"), FakeEvent())
    assert "chatgpt-image2" in providers
    assert "* mock" in providers

    selected = runtime.handle_command_sync(
        RPCommand("image", ["provider", "use", "chatgpt-image2", "gpt-image-1"], "/rp image provider use chatgpt-image2 gpt-image-1"),
        FakeEvent(),
    )
    assert "provider: chatgpt-image2" in selected
    assert "live Image2 HTTP calls are not wired" in selected

    failed = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), FakeEvent())
    assert "Hermes Tavern image generation failed" in failed
    assert "image provider error (details hidden)" in failed
    assert "retry: /rp image retry" in failed
    assert "chatgpt-image2 provider is selected" not in failed

    last = store.get_last_image_job(session["id"])
    assert last is not None
    assert last["status"] == "failed"
    metadata = json.loads(last["metadata_json"])
    assert metadata["error"] == "image provider error (details hidden)"
    assert "chatgpt-image2 provider is selected" not in last["metadata_json"]

    switched = runtime.handle_command_sync(RPCommand("image", ["provider", "use", "mock"], "/rp image provider use mock"), FakeEvent())
    assert "provider: mock" in switched
    ok = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), FakeEvent())
    assert "Hermes Tavern image generated" in ok


def test_image_provider_exception_is_sanitized_in_reply_and_job(tmp_path):
    class ExplodingImageProvider:
        name = "exploding"
        model = "test-model"

        def generate(self, prompt: ImagePrompt, *, output_dir: Path) -> GeneratedImage:
            raise RuntimeError(
                "POST https://api.example.test/v1/images Authorization=fake-token-do-not-persist "
                "/Users/steven/.hermes/.env"
            )

    runtime, store, session, card = _runtime(tmp_path)
    runtime.image_provider = ExplodingImageProvider()

    response = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), FakeEvent())

    assert response == (
        "Hermes Tavern image generation failed.\n"
        "error: image provider error (details hidden)\n"
        "retry: /rp image retry\n"
        "status: /rp image inspect"
    )
    assert "fake-token" not in response
    assert "api.example.test" not in response
    assert ".hermes/.env" not in response
    last = store.get_last_image_job(session["id"])
    assert last is not None
    metadata = json.loads(last["metadata_json"])
    assert metadata["error"] == "image provider error (details hidden)"
    assert "fake-token" not in last["metadata_json"]
    assert "api.example.test" not in last["metadata_json"]
    assert ".hermes/.env" not in last["metadata_json"]


def test_image_history_is_paginated_and_mobile_safe(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    for label in ["first", "second", "third"]:
        runtime.handle_command_sync(RPCommand("image", ["prompt", label], f"/rp image prompt {label}"), FakeEvent())

    page1 = runtime.handle_command_sync(RPCommand("image", ["history", "2", "1"], "/rp image history 2 1"), FakeEvent())
    assert "Hermes Tavern image history page 1/2 (3 total)" in page1
    assert "next: /rp image history 2 2" in page1
    assert "prompt=" in page1

    page2 = runtime.handle_command_sync(RPCommand("image", ["history", "2", "2"], "/rp image history 2 2"), FakeEvent())
    assert "Hermes Tavern image history page 2/2 (3 total)" in page2
    assert "prev: /rp image history 2 1" in page2

    usage = runtime.handle_command_sync(RPCommand("image", ["history", "oops"], "/rp image history oops"), FakeEvent())
    assert "Usage: /rp image history" in usage


def test_image_settings_set_clear_and_apply_to_prompt_and_metadata(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)

    assert "width = 768" in runtime.handle_command_sync(
        RPCommand("image", ["settings", "set", "width", "768"], "/rp image settings set width 768"),
        FakeEvent(),
    )
    assert "height = 1152" in runtime.handle_command_sync(
        RPCommand("image", ["settings", "set", "height", "1152"], "/rp image settings set height 1152"),
        FakeEvent(),
    )
    assert "style_prefix" in runtime.handle_command_sync(
        RPCommand("image", ["settings", "set", "style_prefix", "anime", "key", "visual"], "/rp image settings set style_prefix anime key visual"),
        FakeEvent(),
    )
    assert "negative_prompt" in runtime.handle_command_sync(
        RPCommand("image", ["settings", "set", "negative_prompt", "bad", "hands"], "/rp image settings set negative_prompt bad hands"),
        FakeEvent(),
    )

    shown = runtime.handle_command_sync(RPCommand("image", ["settings"], "/rp image settings"), FakeEvent())
    assert "- width: 768" in shown
    assert "anime key visual" in shown
    assert "bad hands" in shown

    response = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), FakeEvent())
    assert "Hermes Tavern image generated" in response
    last = store.get_last_image_job(session["id"])
    assert last["width"] == 768
    assert last["height"] == 1152
    assert "anime key visual" in last["prompt"]
    assert "bad hands" in last["negative_prompt"]

    assert "cleared: style_prefix" in runtime.handle_command_sync(
        RPCommand("image", ["settings", "clear", "style_prefix"], "/rp image settings clear style_prefix"),
        FakeEvent(),
    )
    cleared = runtime.handle_command_sync(RPCommand("image", ["settings"], "/rp image settings"), FakeEvent())
    assert "- style_prefix: (empty)" in cleared


def test_image_styles_seeded_on_migration(tmp_path):
    """Seed styles are auto-populated by migrate()."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    styles = store.list_image_styles()
    names = {s["name"] for s in styles}
    assert "anime" in names
    assert "realistic" in names
    assert "illustration" in names
    assert "painting" in names
    assert "manga" in names
    assert "pixel-art" in names
    # Re-migration should be idempotent (no duplicates).
    store.migrate()
    assert len(store.list_image_styles()) == len(styles)


def test_image_style_list_use_and_generate(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)

    # Styles already seeded when store was created.
    style_list = runtime.handle_command_sync(RPCommand("image", ["style", "list"], "/rp image style list"), FakeEvent())
    assert "anime:" in style_list
    assert "realistic:" in style_list
    assert "use: /rp image style use" in style_list

    # Use a seed style.
    use = runtime.handle_command_sync(RPCommand("image", ["style", "use", "anime"], "/rp image style use anime"), FakeEvent())
    assert "applied: anime" in use
    assert "anime style" in use

    # Verify settings are updated.
    shown = runtime.handle_command_sync(RPCommand("image", ["settings"], "/rp image settings"), FakeEvent())
    assert "anime style" in shown
    assert "- steps: 28" in shown
    assert "- cfg_scale: 7" in shown

    # Generate — style prefix reaches the prompt.
    response = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), FakeEvent())
    assert "Hermes Tavern image generated" in response
    last = store.get_last_image_job(session["id"])
    assert "anime style" in last["prompt"]


def test_image_style_save_and_delete(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)

    # Set some custom settings first.
    runtime.handle_command_sync(RPCommand("image", ["settings", "set", "style_prefix", "digital sketch"], "/rp image settings set style_prefix digital sketch"), FakeEvent())
    runtime.handle_command_sync(RPCommand("image", ["settings", "set", "width", "768"], "/rp image settings set width 768"), FakeEvent())

    # Save as a style.
    save = runtime.handle_command_sync(RPCommand("image", ["style", "save", "my-sketch"], "/rp image style save my-sketch"), FakeEvent())
    assert "saved: my-sketch" in save

    # Inspect the saved style.
    inspect = runtime.handle_command_sync(RPCommand("image", ["style", "inspect", "my-sketch"], "/rp image style inspect my-sketch"), FakeEvent())
    assert "my-sketch" in inspect
    assert "digital sketch" in inspect
    assert "width: 768" in inspect

    # Delete it.
    delete = runtime.handle_command_sync(RPCommand("image", ["style", "delete", "my-sketch"], "/rp image style delete my-sketch"), FakeEvent())
    assert "deleted: my-sketch" in delete
    assert runtime.handle_command_sync(RPCommand("image", ["style", "inspect", "my-sketch"], "/rp image style inspect my-sketch"), FakeEvent()) == "Unknown image style: my-sketch. Use /rp image style list."


def test_image_style_inspect_and_unknown_errors(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)

    inspect = runtime.handle_command_sync(RPCommand("image", ["style", "inspect", "anime"], "/rp image style inspect anime"), FakeEvent())
    assert "anime" in inspect
    assert "positive_template:" in inspect
    assert "negative_template:" in inspect

    unknown = runtime.handle_command_sync(RPCommand("image", ["style", "inspect", "nope"], "/rp image style inspect nope"), FakeEvent())
    assert "Unknown image style: nope" in unknown

    fail_use = runtime.handle_command_sync(RPCommand("image", ["style", "use", "nope"], "/rp image style use nope"), FakeEvent())
    assert "Unknown image style: nope" in fail_use


def test_image_style_use_then_settings_clear_preserves_style_defaults(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)

    # Apply a seed style (anime sets steps=28, cfg=7, euler_a).
    runtime.handle_command_sync(RPCommand("image", ["style", "use", "anime"], "/rp image style use anime"), FakeEvent())

    # Then manually tweak one setting.
    runtime.handle_command_sync(RPCommand("image", ["settings", "set", "steps", "40"], "/rp image settings set steps 40"), FakeEvent())

    # Clear settings — should reset to DEFAULT (1024x1024, steps=28, cfg=7.0, euler_a, etc).
    runtime.handle_command_sync(RPCommand("image", ["settings", "clear", "all"], "/rp image settings clear all"), FakeEvent())

    shown = runtime.handle_command_sync(RPCommand("image", ["settings"], "/rp image settings"), FakeEvent())
    assert "- width: 1024" in shown
    assert "- steps: 28" in shown
    assert "- style_prefix: (empty)" in shown  # cleared, not anime


def test_expand_image_template_macros_supports_st_subset():
    expanded = expand_image_template_macros(
        "{{prompt}}, {{char}}, {{user}}, {{scenario}}, {{memory}}, {{mode}}, {{random:red|blue}}, {{unknown}}",
        prompt="standing under moonlight",
        char_name="Alice",
        user="Steven",
        scenario="lake",
        memory="old promise",
        mode="scenario",
        seed=42,
    )
    assert "standing under moonlight" in expanded
    assert "Alice" in expanded
    assert "Steven" in expanded
    assert "lake" in expanded
    assert "old promise" in expanded
    assert "scenario" in expanded
    assert "{{" not in expanded
    assert any(color in expanded for color in ["red", "blue"])


def test_style_template_macro_wraps_prompt_without_leaking_macro(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    store.set_session_summary(SESSION_KEY, "Alice remembers a quiet promise.")
    settings = {
        "style_prefix": "{{prompt}}, {{char}}, {{scenario}}, {{memory}}, {{mode}}, {{random:warm|cool}} lighting",
        "style_suffix": "finished detail",
        "negative_prompt": "bad hands, avoid {{char}}, {{random:blur|noise}}",
        "seed": 7,
    }
    prompt = compile_image_prompt(
        mode="scene",
        card=card,
        session=session,
        history=store.get_recent_messages(session["id"], limit=20),
        memory_summary=store.get_session_summary(SESSION_KEY)["summary"],
        settings=settings,
    )
    assert "{{prompt" not in prompt.prompt
    assert "{{char" not in prompt.prompt
    assert "Alice" in prompt.prompt
    assert "moonlit lakeside" in prompt.prompt
    assert "quiet promise" in prompt.prompt
    assert "finished detail" in prompt.prompt
    assert "avoid Alice" in prompt.negative_prompt
    assert "{{" not in prompt.negative_prompt


def test_seed_style_use_expands_prompt_macro_during_generation(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    runtime.handle_command_sync(RPCommand("image", ["style", "use", "anime"], "/rp image style use anime"), FakeEvent())
    response = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), FakeEvent())
    assert "Hermes Tavern image generated" in response
    last = store.get_last_image_job(session["id"])
    assert "anime style" in last["prompt"]
    assert "{{prompt" not in last["prompt"]
    assert "{{" not in last["negative_prompt"]


def test_image_safety_commands_and_safe_mode_block(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)

    inspect = runtime.handle_command_sync(RPCommand("image", ["safety"], "/rp image safety"), FakeEvent())
    assert "mode: safe" in inspect
    assert "hard blocks" in inspect

    blocked = runtime.handle_command_sync(
        RPCommand("image", ["prompt", "nude", "pinup", "portrait"], "/rp image prompt nude pinup portrait"),
        FakeEvent(),
    )
    assert "blocked by safety guard" in blocked
    assert "safe image mode blocks" in blocked
    last = store.get_last_image_job(session["id"])
    assert last["status"] == "failed"
    metadata = json.loads(last["metadata_json"])
    assert metadata["safety"]["allowed"] is False
    assert metadata["safety"]["mode"] == "safe"

    response = runtime.handle_command_sync(
        RPCommand("image", ["safety", "mode", "explicit"], "/rp image safety mode explicit"),
        FakeEvent(),
    )
    assert "set: explicit" in response
    allowed = runtime.handle_command_sync(
        RPCommand("image", ["prompt", "nude", "pinup", "portrait"], "/rp image prompt nude pinup portrait"),
        FakeEvent(),
    )
    assert "Hermes Tavern image generated" in allowed


def test_image_safety_hard_blocks_even_explicit_mode(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    runtime.handle_command_sync(RPCommand("image", ["safety", "mode", "explicit"], "/rp image safety mode explicit"), FakeEvent())

    minor = runtime.handle_command_sync(
        RPCommand("image", ["prompt", "underage", "nude", "portrait"], "/rp image prompt underage nude portrait"),
        FakeEvent(),
    )
    assert "blocked by safety guard" in minor
    assert "minor-or-underage" in minor

    real_person = runtime.handle_command_sync(
        RPCommand("image", ["prompt", "celebrity", "nude", "deepfake"], "/rp image prompt celebrity nude deepfake"),
        FakeEvent(),
    )
    assert "real-person" in real_person

    nonconsent = runtime.handle_command_sync(
        RPCommand("image", ["prompt", "forced", "sexual", "scene"], "/rp image prompt forced sexual scene"),
        FakeEvent(),
    )
    assert "non-consensual" in nonconsent


def test_image_safety_inspect_reports_last_job_safety(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    response = runtime.handle_command_sync(RPCommand("image", ["scene"], "/rp image scene"), FakeEvent())
    assert "Hermes Tavern image generated" in response
    inspect = runtime.handle_command_sync(RPCommand("image", ["inspect"], "/rp image inspect"), FakeEvent())
    assert "safety: safe low allowed=True" in inspect


def test_image_safety_clear_resets_to_safe(tmp_path):
    runtime, store, session, card = _runtime(tmp_path)
    runtime.handle_command_sync(RPCommand("image", ["safety", "mode", "explicit"], "/rp image safety mode explicit"), FakeEvent())
    assert "mode: explicit" in runtime.handle_command_sync(RPCommand("image", ["safety"], "/rp image safety"), FakeEvent())
    reset = runtime.handle_command_sync(RPCommand("image", ["safety", "clear"], "/rp image safety clear"), FakeEvent())
    assert "reset to safe" in reset
    assert "mode: safe" in runtime.handle_command_sync(RPCommand("image", ["safety"], "/rp image safety"), FakeEvent())
