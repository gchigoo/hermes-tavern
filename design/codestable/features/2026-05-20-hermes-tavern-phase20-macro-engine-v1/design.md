---
doc_type: feature-design
feature: 2026-05-20-hermes-tavern-phase20-macro-engine-v1
status: approved
summary: Add deterministic SillyTavern-compatible template macro expansion before Hermes Tavern prompt rendering.
tags: [hermes-tavern, prompt-fidelity, macros, security]
---

# Phase 20 — ST Macro Engine v1 + Prompt Fidelity

## 0. Decisions & Constraints

**Not doing:**
- No Python expression evaluation, imports, shell execution, JavaScript, or network access from imported assets.
- No recursive macro expansion; one pass only.
- No new DB schema or persistent settings.
- No broad `runtime.py` refactor.
- No real provider calls in tests.

**Resolved behavior:**
- Unknown macros stay unchanged so imported assets retain fidelity.
- Macro names are case-insensitive and whitespace-tolerant.
- Date/time macros are deterministic in tests via injectable `datetime`.
- Runtime derives user name from gateway event fields when present, otherwise uses `User`.

## 1. Where this fits

| File | Role |
|---|---|
| `plugins/hermes_tavern/macros.py` | New template-only macro engine and `MacroContext` |
| `plugins/hermes_tavern/prompt.py` | Expands card system text, prompt modules, history, user message before returning `CompiledContext` |
| `plugins/hermes_tavern/runtime.py` | Builds runtime macro context for active messages, retry/edit fallback, and `/rp debug prompt` |
| `tests/plugins/test_hermes_tavern_macros.py` | Macro engine unit coverage |
| Existing compiler/runtime/E2E tests | Prompt fidelity integration coverage |

## 2. Noun Layer

```python
@dataclass(frozen=True)
class MacroContext:
    char_name: str = ""
    user_name: str = "User"
    session_title: str = ""
    content_mode: str = "safe"
    now: datetime | None = None

def expand_macros(text: str, context: MacroContext) -> str:
    ...
```

Supported macros: `{{char}}`, `{{user}}`, `{{time}}`, `{{date}}`, `{{datetime}}`, `{{weekday}}`, `{{content_mode}}`, `{{session_title}}`.

## 3. Orchestration Layer

```
handle_active_message_sync(event)
  -> _run_generation_pipeline(session, user_text, history, event=event)
      -> _build_macro_context(card, session, event)
      -> _session_prompt_modules(...)
      -> PromptCompiler.compile(..., macro_context=context)
          -> expand card system text
          -> expand preset/lore/memory modules
          -> expand history rows
          -> expand current user message
      -> ChatRenderer.render(ctx)
      -> adapter.generate(...)

/rp debug prompt
  -> build same MacroContext from card/session/event
  -> compile preview
  -> show char/user/session/content_mode summary, never raw event JSON
```

## 4. Acceptance Scenarios

- Basic macros expand with deterministic date/time.
- Case and whitespace variants expand.
- Unknown macros are preserved.
- Nested-looking macro output is not recursively expanded.
- Execution-looking macro text is not executed and remains inert.
- Compiler expands card, preset/lore/memory module text, history, and user message.
- Runtime active-message pipeline uses event-derived user name and session/card context.
- `/rp debug prompt` shows macro context summary without raw event JSON.
