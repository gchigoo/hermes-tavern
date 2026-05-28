"""Session-scoped memory helpers for Hermes Tavern.

This module is intentionally deterministic and mock-first: it never calls an
LLM.  Runtime commands can save explicit user-provided facts, set a manual
summary, or create a compact transcript-style summary from recent messages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from plugins.hermes_tavern.prompt import PromptModule
from plugins.hermes_tavern.utils import estimate_tokens


@dataclass(frozen=True)
class TavernMemoryFact:
    id: str
    content: str
    importance: int = 1
    source: str = "manual"


@dataclass(frozen=True)
class TavernMemoryContext:
    summary: str = ""
    facts: tuple[TavernMemoryFact, ...] = ()


def build_memory_modules(
    context: TavernMemoryContext,
    *,
    fact_budget_tokens: int = 500,
) -> list[PromptModule]:
    """Convert a memory context into prompt modules.

    Summary is injected first, then the highest-importance facts that fit the
    fact token budget.  The caller decides whether the session is eligible for
    memory injection; this function only formats already-approved local state.
    """

    modules: list[PromptModule] = []
    if context.summary.strip():
        modules.append(
            PromptModule(
                name="memory:summary",
                role="system",
                content="Session summary so far:\n" + context.summary.strip(),
                position="before_char",
                insertion_order=-200,
            )
        )

    selected: list[TavernMemoryFact] = []
    used_tokens = 0
    for fact in sorted(context.facts, key=lambda item: (-item.importance, item.content.lower())):
        fact_tokens = estimate_tokens(fact.content)
        if selected and used_tokens + fact_tokens > fact_budget_tokens:
            continue
        selected.append(fact)
        used_tokens += fact_tokens

    if selected:
        lines = [f"- {fact.content.strip()}" for fact in selected if fact.content.strip()]
        if lines:
            modules.append(
                PromptModule(
                    name="memory:facts",
                    role="system",
                    content="Session memory facts:\n" + "\n".join(lines),
                    position="before_char",
                    insertion_order=-190,
                )
            )
    return modules


def summarize_recent_messages(
    messages: list[dict[str, Any]],
    *,
    limit: int = 12,
    max_chars_per_message: int = 140,
) -> str:
    """Build a deterministic, transcript-style summary from recent messages.

    This is deliberately not semantic summarization; Phase 13 uses it as a
    mock-first placeholder that is inspectable and testable without provider
    calls.  Future phases can swap in explicit live-model summarization behind
    the existing provider-live gate.
    """

    usable = [
        row
        for row in messages[-limit:]
        if (row.get("content") or "").strip() and row.get("role") in {"user", "assistant"}
    ]
    if not usable:
        return ""

    lines = []
    for row in usable:
        role = row.get("role", "unknown")
        text = " ".join((row.get("content") or "").split())
        if len(text) > max_chars_per_message:
            text = text[: max_chars_per_message - 1].rstrip() + "…"
        lines.append(f"- {role}: {text}")
    return "Recent session turns:\n" + "\n".join(lines)
