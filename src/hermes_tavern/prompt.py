"""Prompt dataclasses and compiler for Hermes Tavern."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from plugins.hermes_tavern.macros import MacroContext, expand_macros
from plugins.hermes_tavern.utils import estimate_tokens

if TYPE_CHECKING:
    from plugins.hermes_tavern.importers.cards import CharacterCard


@dataclass(frozen=True)
class PromptModule:
    name: str
    role: str           # "system" | "user" | "assistant"
    content: str
    position: str       # "before_char" | "after_char" | "in_chat"
    insertion_order: int = 0
    enabled: bool = True


@dataclass
class CompiledContext:
    modules: list[PromptModule]   # ordered, all enabled
    history: list[dict[str, Any]] # [{"role": ..., "content": ...}]
    user_message: str
    card_name: str
    token_budget: int             # estimate_tokens sum


class PromptCompiler:
    """Assemble a CompiledContext from card fields, preset modules, history, and user message."""

    def compile(
        self,
        card: "CharacterCard",
        history_rows: list[dict[str, Any]],
        user_message: str,
        preset_modules: list[PromptModule] | None = None,
        macro_context: MacroContext | None = None,
    ) -> CompiledContext:
        modules: list[PromptModule] = []
        macros = macro_context or MacroContext(char_name=card.name)

        # Card system prompt: prefer system_prompt_override, fall back to description
        system_text = expand_macros(
            (card.system_prompt_override or card.description or "").strip(),
            macros,
        )
        if system_text:
            modules.append(
                PromptModule(
                    name="char_system",
                    role="system",
                    content=system_text,
                    position="before_char",
                    insertion_order=0,
                )
            )

        # Enabled preset modules sorted by insertion_order
        for pm in sorted(preset_modules or [], key=lambda m: m.insertion_order):
            if pm.enabled:
                modules.append(
                    PromptModule(
                        name=pm.name,
                        role=pm.role,
                        content=expand_macros(pm.content, macros),
                        position=pm.position,
                        insertion_order=pm.insertion_order,
                        enabled=pm.enabled,
                    )
                )

        history = []
        for row in history_rows:
            expanded = dict(row)
            expanded["content"] = expand_macros(str(row.get("content", "")), macros)
            history.append(expanded)
        expanded_user_message = expand_macros(user_message, macros)

        token_budget = sum(estimate_tokens(m.content) for m in modules)
        token_budget += sum(
            estimate_tokens(row.get("content", "")) for row in history
        )
        token_budget += estimate_tokens(expanded_user_message)

        return CompiledContext(
            modules=modules,
            history=history,
            user_message=expanded_user_message,
            card_name=card.name,
            token_budget=token_budget,
        )
