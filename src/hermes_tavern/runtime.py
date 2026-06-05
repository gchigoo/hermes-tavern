"""Hermes Tavern runtime command handling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hermes_tavern.adapters import (
    FakeModelAdapter,
    HermesProviderAdapter,
)
from hermes_tavern.commands import RPCommand, TAVERN_COMMAND_TABLE, dispatch_command
from hermes_tavern.db import TavernStore
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.import_policy import resolve_import_path

from hermes_tavern.images import MockImageProvider, TavernImageProvider
from hermes_tavern.model_router import ModelRouter
from hermes_tavern.prompt import PromptCompiler, PromptModule
from hermes_tavern.renderers import ChatRenderer
from hermes_tavern import (
    runtime_assets,
    runtime_content,
    runtime_debug,
    runtime_lore,
    runtime_novel,
    runtime_images,
    runtime_lifecycle,
    runtime_memory,
    runtime_model,
    runtime_notes,
    runtime_persona,
    runtime_presets,
    runtime_prompt_manager,
    runtime_prompt_modules,
    runtime_generation,
    runtime_sessions,
    runtime_turns,
)
from hermes_tavern.runtime_utils import (
    build_macro_context as _build_macro_context,
    card_row_to_obj as _card_row_to_obj,
    mobile_preview as _mobile_preview,
)

PLACEHOLDER_REPLY = "[Hermes Tavern runtime placeholder]"

_compiler = PromptCompiler()
_router = ModelRouter()
_chat_renderer = ChatRenderer()
_fake_adapter = FakeModelAdapter()


def _attachment_import_path(
    event: Any,
    explicit_value: str | None = None,
    *,
    label: str,
    suffixes: set[str],
    usage: str,
    attach_tip: str,
) -> tuple[Path | str | None, str | None]:
    decision = resolve_import_path(
        event,
        explicit_value,
        label=label,
        suffixes=suffixes,
        usage=usage,
        attach_tip=attach_tip,
    )
    return decision.value, decision.error


def _last_asset_help(asset_type: str) -> str:
    commands = {
        "card": "/rp card import <file>",
        "preset": "/rp preset import <file>",
        "lorebook": "/rp lore import <file>",
        "persona": "/rp persona import <file>",
    }
    return f"No {asset_type} has been imported yet. Import a {asset_type} first: {commands[asset_type]}"


def _asset_not_found(asset_type: str, ref: str) -> str:
    if ref.strip().lower() == "last":
        return _last_asset_help(asset_type)
    labels = {
        "card": "Character card",
        "preset": "Preset",
        "lorebook": "Lorebook",
        "persona": "Persona",
    }
    return f"{labels[asset_type]} not found: {ref}"


class TavernRuntime:
    def __init__(
        self,
        store: TavernStore | None = None,
        hermes_adapter: HermesProviderAdapter | None = None,
        image_provider: TavernImageProvider | None = None,
        tts_renderer: Any | None = None,
    ) -> None:
        self.store = store or TavernStore()
        self.hermes_adapter = hermes_adapter
        self.image_provider = image_provider or MockImageProvider()
        self.tts_renderer = tts_renderer
        self._voice_enabled_session_keys: set[str] = set()
        self._novel_active_projects: dict[str, int] = {}
        self.store.migrate()

    async def handle_command(
        self,
        command: RPCommand,
        event: Any,
        gateway: Any = None,
    ) -> str:
        return self.handle_command_sync(command, event, gateway=gateway)

    def handle_command_sync(
        self,
        command: RPCommand,
        event: Any,
        gateway: Any = None,
    ) -> str:
        try:
            return self._handle_command_sync(command, event, gateway=gateway)
        except Exception:
            return "[Hermes Tavern: internal error]"

    def _handle_command_sync(
        self,
        command: RPCommand,
        event: Any,
        gateway: Any = None,
    ) -> str:
        del gateway
        return dispatch_command(TAVERN_COMMAND_TABLE, self, command, event)

    def _debug_command(self, command: RPCommand, event: Any) -> str:
        """Dispatch /rp debug sub-commands."""
        action = command.args[0].lower() if command.args else "prompt"
        if action == "prompt":
            return self._debug_prompt(command, event)
        if action == "context":
            return self._debug_context(command, event)
        if action == "swipes":
            return self._debug_swipes(event)
        return "Usage: /rp debug [prompt [limit] [page]|context [limit] [page]|swipes]"

    async def handle_active_message(self, event: Any) -> str:
        return self.handle_active_message_sync(event)

    def handle_active_message_sync(self, event: Any) -> str:
        session_key = session_key_from_event(event)
        session = self.store.get_active_session(session_key)
        if session is None:
            return ""

        user_text = getattr(event, "text", "") or ""
        history = self.store.get_recent_messages(session["id"], limit=20)
        reply = self._run_generation_pipeline(session, user_text, history, event=event)

        message_id = getattr(event, "message_id", None)
        metadata = {"message_id": message_id} if message_id else None
        self.store.append_message(session["id"], "user", user_text, metadata=metadata)
        self.store.append_message(session["id"], "assistant", reply)
        return self._with_auto_speak(reply, event)

    def _run_generation_pipeline(
        self,
        session: dict[str, Any],
        user_text: str,
        history: list[dict[str, Any]],
        event: Any = None,
    ) -> str:
        """Compile prompt, resolve model, render, and generate a reply. Does not write to store."""
        card = None
        if session.get("card_id"):
            card_row = self.store.get_card(session["card_id"])
            if card_row:
                card = _card_row_to_obj(card_row)

        if card is None:
            return PLACEHOLDER_REPLY

        prompt_modules = self._session_prompt_modules(session, user_text, history)
        macro_context = _build_macro_context(card, session, event)
        ctx = _compiler.compile(
            card,
            history,
            user_text,
            preset_modules=prompt_modules,
            macro_context=macro_context,
        )
        descriptor = _router.resolve(session_row=session, store=self.store)
        messages = _chat_renderer.render(ctx)
        return self._generate_with_session_adapter(session, messages, descriptor)

    def _debug_prompt(self, command: RPCommand, event: Any) -> str:
        return runtime_debug.debug_prompt(self, command, event)

    def _debug_context(self, command: RPCommand, event: Any) -> str:
        return runtime_debug.debug_context(self, command, event)

    def _debug_swipes(self, event: Any) -> str:
        return runtime_turns.debug_swipes(self, event)

    def _doctor(self, event: Any) -> str:
        return runtime_debug.doctor(self, event)

    def _assets(self, event: Any) -> str:
        return runtime_assets.assets(self, event)

    def _cards(self, command: RPCommand) -> str:
        return runtime_assets.cards(self, command)

    def _card_command(self, command: RPCommand, event: Any) -> str:
        return runtime_assets.card_command(self, command, event)

    def _card_search(self, command: RPCommand) -> str:
        return runtime_assets.card_search(self, command)

    def _card_inspect(self, command: RPCommand) -> str:
        return runtime_assets.card_inspect(self, command)

    def _card_use(self, command: RPCommand, event: Any) -> str:
        return runtime_assets.card_use(self, command, event)

    def _session_preset_modules(self, session: dict[str, Any]) -> list[PromptModule]:
        return runtime_prompt_modules.session_preset_modules(self, session)

    def _session_prompt_modules(
        self,
        session: dict[str, Any],
        user_text: str,
        history: list[dict[str, Any]],
    ) -> list[PromptModule]:
        return runtime_prompt_modules.session_prompt_modules(self, session, user_text, history)

    def _session_persona_modules(self, session: dict[str, Any]) -> list[PromptModule]:
        return runtime_prompt_modules.session_persona_modules(self, session)

    def _session_note_modules(
        self, session: dict[str, Any], history: list[dict[str, Any]]
    ) -> list[PromptModule]:
        return runtime_prompt_modules.session_note_modules(self, session, history)

    def _session_memory_modules(self, session: dict[str, Any]) -> list[PromptModule]:
        return runtime_prompt_modules.session_memory_modules(self, session)

    def _session_lore_modules(
        self,
        session: dict[str, Any],
        user_text: str,
        history: list[dict[str, Any]],
    ) -> list[PromptModule]:
        return runtime_prompt_modules.session_lore_modules(self, session, user_text, history)

    def _active_card_data(self, event: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
        return runtime_turns.active_card_data(self, event)

    def _greeting_options(self, data: dict[str, Any]) -> list[tuple[int, str, str]]:
        return runtime_turns.greeting_options(data)

    def _greeting(self, command: RPCommand, event: Any) -> str:
        return runtime_turns.greeting(self, command, event)

    def _say(self, command: RPCommand, event: Any) -> str:
        return runtime_turns.say(self, command, event)

    def _generate_with_session_adapter(
        self,
        session: dict[str, Any],
        messages: list[dict[str, Any]],
        descriptor: Any,
    ) -> str:
        return runtime_generation.generate_with_session_adapter(self, session, messages, descriptor, _fake_adapter)

    def _last_assistant_reply(self, session: dict[str, Any]) -> str:
        return runtime_turns.last_assistant_reply(self, session)

    def _speak(self, event: Any) -> str:
        return runtime_turns.speak(self, event)

    def _voice(self, command: RPCommand, event: Any) -> str:
        return runtime_turns.voice(self, command, event)

    def _with_auto_speak(self, reply: str, event: Any) -> str:
        return runtime_turns.with_auto_speak(self, reply, event)

    def _history(self, command: RPCommand, event: Any) -> str:
        return runtime_turns.history(self, command, event)

    def _last_user_assistant_turn(
        self, session: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]] | None:
        return runtime_turns.last_user_assistant_turn(self, session)

    def _assistant_swipe_metadata(self, assistant_msg: dict[str, Any]) -> dict[str, Any]:
        return runtime_turns.assistant_swipe_metadata(assistant_msg)

    def _retry(self, event: Any) -> str:
        return runtime_turns.retry(self, event)

    def _swipe(self, command: RPCommand, event: Any) -> str:
        return runtime_turns.swipe(self, command, event)

    def _undo(self, event: Any) -> str:
        return runtime_turns.undo(self, event)

    def _edit(self, command: RPCommand, event: Any) -> str:
        return runtime_turns.edit(self, command, event)

    def _content_command(self, command: RPCommand, event: Any) -> str:
        return runtime_content.content_command(self, command, event)

    def _preset_command(self, command: RPCommand, event: Any) -> str:
        return runtime_presets.preset_command(self, command, event)

    def _preset_import(self, command: RPCommand, event: Any) -> str:
        return runtime_presets.preset_import(self, command, event)

    def _preset_list(self) -> str:
        return runtime_presets.preset_list(self)

    def _preset_inspect(self, command: RPCommand) -> str:
        return runtime_presets.preset_inspect(self, command)

    def _preset_use(self, command: RPCommand, event: Any) -> str:
        return runtime_presets.preset_use(self, command, event)

    def _prompt_command(self, command: RPCommand, event: Any) -> str:
        return runtime_prompt_manager.prompt_command(self, command, event)

    def _lore_command(self, command: RPCommand, event: Any) -> str:
        return runtime_lore.lore_command(self, command, event)

    def _lore_import(self, command: RPCommand, event: Any) -> str:
        return runtime_lore.lore_import(self, command, event)

    def _lore_list(self) -> str:
        return runtime_lore.lore_list(self)

    def _lore_inspect(self, command: RPCommand) -> str:
        return runtime_lore.lore_inspect(self, command)

    def _lore_use(self, command: RPCommand, event: Any) -> str:
        return runtime_lore.lore_use(self, command, event)

    def _lore_test(self, command: RPCommand, event: Any) -> str:
        return runtime_lore.lore_test(self, command, event)

    def _lore_debug(self, event: Any) -> str:
        return runtime_lore.lore_debug(self, event)

    def _memory_command(self, command: RPCommand, event: Any) -> str:
        return runtime_memory.memory_command(self, command, event)

    def _memory_add(self, command: RPCommand, event: Any) -> str:
        return runtime_memory.memory_add(self, command, event)

    def _memory_list(self, command: RPCommand, event: Any) -> str:
        return runtime_memory.memory_list(self, command, event)

    def _memory_summary(self, command: RPCommand, event: Any) -> str:
        return runtime_memory.memory_summary(self, command, event)

    def _memory_debug(self, event: Any) -> str:
        return runtime_memory.memory_debug(self, event)

    def _persona_command(self, command: RPCommand, event: Any) -> str:
        return runtime_persona.persona_command(self, command, event)

    def _persona_import(self, command: RPCommand, event: Any) -> str:
        return runtime_persona.persona_import(self, command, event)

    def _persona_list(self, command: RPCommand) -> str:
        return runtime_persona.persona_list(self, command)

    def _persona_inspect(self, command: RPCommand) -> str:
        return runtime_persona.persona_inspect(self, command)

    def _persona_use(self, command: RPCommand, event: Any) -> str:
        return runtime_persona.persona_use(self, command, event)

    def _persona_clear(self, event: Any) -> str:
        return runtime_persona.persona_clear(self, event)

    def _persona_debug(self, event: Any) -> str:
        return runtime_persona.persona_debug(self, event)

    def _note_command(self, command: RPCommand, event: Any) -> str:
        return runtime_notes.note_command(self, command, event)

    def _note_active_session(self, event: Any) -> tuple[str, dict[str, Any] | None]:
        return runtime_notes.note_active_session(self, event)

    def _note_set(self, command: RPCommand, event: Any) -> str:
        return runtime_notes.note_set(self, command, event)

    def _note_clear(self, event: Any) -> str:
        return runtime_notes.note_clear(self, event)

    def _note_inspect(self, event: Any) -> str:
        return runtime_notes.note_inspect(self, event)

    def _note_position(self, command: RPCommand, event: Any) -> str:
        return runtime_notes.note_position(self, command, event)

    def _note_frequency(self, command: RPCommand, event: Any) -> str:
        return runtime_notes.note_frequency(self, command, event)

    def _format_note_frequency(self, session: dict[str, Any]) -> str:
        return runtime_notes.format_note_frequency(session)

    def _live_memory_summarize(
        self,
        session: dict[str, Any],
        session_key: str,
        messages: list[dict[str, Any]],
        event: Any,
    ) -> str:
        return runtime_memory.live_memory_summarize(
            self, session, session_key, messages, event
        )

    def _model_command(self, command: RPCommand, event: Any) -> str:
        return runtime_model.model_command(self, command, event)

    def _model_status(self, event: Any) -> str:
        return runtime_model.model_status(self, event)

    def _model_profiles(self) -> str:
        return runtime_model.model_profiles(self)

    def _model_seed_apiyi(self) -> str:
        return runtime_model.model_seed_apiyi(self)

    def _model_use(self, command: RPCommand, event: Any) -> str:
        return runtime_model.model_use(self, command, event)

    def _model_mode(self, command: RPCommand, event: Any) -> str:
        return runtime_model.model_mode(self, command, event)

    def _model_live(self, command: RPCommand, event: Any) -> str:
        return runtime_model.model_live(self, command, event)

    def _model_test(self, event: Any) -> str:
        return runtime_model.model_test(self, event)

    def _session_command(self, command: RPCommand, event: Any) -> str:
        return runtime_sessions.session_command(self, command, event)

    def _session_info(self, event: Any) -> str:
        return runtime_sessions.session_info(self, event)

    def _sessions(self, command: RPCommand, event: Any) -> str:
        return runtime_sessions.sessions(self, command, event)

    def _switch(self, command: RPCommand, event: Any) -> str:
        return runtime_sessions.switch(self, command, event)

    def _rename(self, command: RPCommand, event: Any) -> str:
        return runtime_sessions.rename(self, command, event)

    def _archive(self, event: Any) -> str:
        return runtime_sessions.archive(self, event)

    def _clone(self, command: RPCommand, event: Any) -> str:
        return runtime_sessions.clone(self, command, event)

    def _image_command(self, command: RPCommand, event: Any) -> str:
        return runtime_images.image_command(self, command, event)

    def _image_settings(self, command: RPCommand, session: dict[str, Any]) -> str:
        return runtime_images.image_settings(self, command, session)

    def _image_safety(self, command: RPCommand, session: dict[str, Any]) -> str:
        return runtime_images.image_safety(self, command, session)

    def _image_style(self, command: RPCommand, session: dict[str, Any]) -> str:
        return runtime_images.image_style(self, command, session)

    def _image_provider(self, command: RPCommand) -> str:
        return runtime_images.image_provider(self, command)

    def _image_history(self, command: RPCommand, session: dict[str, Any]) -> str:
        return runtime_images.image_history(self, command, session)

    def _image_generate(
        self,
        session: dict[str, Any],
        event: Any,
        *,
        mode: str,
        user_prompt: str = "",
        negative_prompt: str = "",
        source: str = "command",
    ) -> str:
        return runtime_images.image_generate(
            self,
            session,
            event,
            mode=mode,
            user_prompt=user_prompt,
            negative_prompt=negative_prompt,
            source=source,
        )

    def _image_retry(self, session: dict[str, Any]) -> str:
        return runtime_images.image_retry(self, session)

    def _image_inspect(self, session: dict[str, Any]) -> str:
        return runtime_images.image_inspect(self, session)

    def _export(self, command: RPCommand, event: Any) -> str:
        return runtime_lifecycle.export(self, command, event)

    def _project_command(self, command: RPCommand, event: Any) -> str:
        return runtime_novel.project_command(self, command, event)

    def _chapter_command(self, command: RPCommand, event: Any) -> str:
        return runtime_novel.chapter_command(self, command, event)

    def _scene_command(self, command: RPCommand, event: Any) -> str:
        return runtime_novel.scene_command(self, command, event)

    def _canon_command(self, command: RPCommand, event: Any) -> str:
        return runtime_novel.canon_command(self, command, event)

    def _timeline_command(self, command: RPCommand, event: Any) -> str:
        return runtime_novel.timeline_command(self, command, event)

    def _relationship_command(self, command: RPCommand, event: Any) -> str:
        return runtime_novel.relationship_command(self, command, event)

    def _status(self, event: Any) -> str:
        return runtime_lifecycle.status(self, event)

    def _end(self, event: Any) -> str:
        return runtime_lifecycle.end(self, event)

    def _pause(self, event: Any) -> str:
        return runtime_lifecycle.pause(self, event)

    def _resume(self, event: Any) -> str:
        return runtime_lifecycle.resume(self, event)

    def _start(self, command: RPCommand, event: Any) -> str:
        return runtime_lifecycle.start(self, command, event)
