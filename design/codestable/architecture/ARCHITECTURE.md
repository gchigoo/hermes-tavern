# Hermes Agent — Architecture

> Status: current snapshot
> Last updated: 2026-06-04

## 1. Project Summary

Hermes Agent is a self-improving AI agent by Nous Research. It runs as a CLI or a persistent gateway process that bridges Telegram, Discord, Slack, WhatsApp, Signal, Feishu, and others to any OpenAI-compatible LLM provider. It has a closed learning loop: skill creation, memory, session search, and a cron scheduler.

## 2. Core Concepts / Glossary

| Term | Meaning |
|---|---|
| AIAgent | Core conversation loop class (`run_agent.py`, ~12k LOC) |
| HermesCLI | Interactive CLI orchestrator (`cli.py`, ~11k LOC) |
| Gateway | Messaging bridge process (`gateway/run.py`); dispatches to per-platform adapters |
| Platform adapter | One file per messaging platform under `gateway/platforms/` |
| `pre_gateway_dispatch` hook | Plugin extension point: intercept or modify events before AIAgent sees them |
| Plugin | Directory under `plugins/` with `plugin.yaml` + `__init__.py` exposing `register(ctx)` |
| Skill | Markdown instruction file; user-invocable via `/skill-name` in CLI or gateway |
| SessionDB | SQLite FTS5 session store (`hermes_state.py`); indexed per-profile |
| `get_hermes_home()` | Profile-aware home path resolver (`hermes_constants.py`); never hard-code `~/.hermes` |
| Hermes Tavern | Plugin for SillyTavern-compatible RP/novel/adult-fiction (`plugins/hermes_tavern/`) |

## 3. Subsystem / Module Index

```
run_agent.py          AIAgent — conversation loop, tool dispatch, memory, compression
cli.py                HermesCLI — interactive CLI, slash commands, skin engine
model_tools.py        Tool orchestration, discover_builtin_tools(), handle_function_call()
toolsets.py           Toolset definitions
hermes_state.py       SessionDB — SQLite session store (FTS5 search)
hermes_constants.py   get_hermes_home(), display_hermes_home()
hermes_logging.py     setup_logging() — agent.log / errors.log / gateway.log

gateway/
  run.py              Gateway entry point; platform dispatch, pre_gateway_dispatch hook
  session.py          Per-chat session context
  platforms/          One adapter per messaging platform

plugins/
  hermes_tavern/      Hermes Tavern RP/novel runtime (see §5)
  memory/             Memory provider plugins (honcho, mem0, supermemory)
  context_engine/     Context engine plugins
  model-providers/    Inference backend plugins (openrouter, anthropic, gmi, …)
  kanban/             Multi-agent board dispatcher
  observability/      Metrics/traces/logs

tools/                Tool implementations — auto-discovered via tools/registry.py
agent/                Provider adapters, memory, caching, compression
hermes_cli/           CLI subcommands, plugin loader, skin engine
cron/                 Cron scheduler — jobs.py, scheduler.py
```

## 4. Hermes Tavern Plugin Architecture

Plugin path: `plugins/hermes_tavern/`

```
plugin.yaml           Plugin metadata + kind: backend
__init__.py           register(ctx) → ctx.register_hook("pre_gateway_dispatch", handler)
gateway_hook.py       pre_gateway_dispatch(**kwargs) — route /rp commands and active sessions
commands.py           parse_rp_command(text) → RPCommand | None
identity.py           session_key_from_event(event) → str  (platform+chat+thread+user)
db.py                 TavernStore — SQLite CRUD for cards, sessions, messages, presets, lorebooks, memory; read-only pagination helpers (count_messages, get_messages_page, count_sessions_for_scope, count_session_memory_facts)
runtime.py            TavernRuntime — command handler, active session message handler, macro-context wiring, prompt pipeline
prompt.py             PromptCompiler — assemble system prompt from card + preset modules + lore + memory; expands safe ST template macros before rendering
macros.py             MacroContext + expand_macros() — deterministic ST-compatible template-only macro expansion, no execution semantics
renderers.py          ChatRenderer, StoryRenderer — convert compiled prompt to provider messages
preset_safety.py      PresetRiskLevel, classify_preset_text — risk classification for imported modules
lorebook.py           match_lorebook_entries — keyword/regex match, local regex complexity guard, token-budget enforcement
memory.py             Memory fact / summary management helpers
db_novel.py           Novel domain mixins for project/chapter/scene/scene-goal/canon/timeline CRUD and export
runtime_novel.py      Novel command family handlers for /rp project/chapter/scene/scene-goal/canon/timeline
runtime_prompt_modules.py  Scene-goal, scene narration, project-style, and canon prompt module resolvers for linked novel sessions
model_router.py       resolve model descriptor from session row and store
provider_bridge.py    resolve_runtime_provider + validate_provider_base_url — runtime credential resolution (no DB persistence); URL safety validator rejects non-https and private/loopback hosts
adapters.py           FakeModelAdapter, HermesChatCompletionAdapter, HermesProviderAdapter
importers/
  cards.py            parse_card(raw_json) → CharacterCard  (ST V2 + direct style)
  presets.py          import_st_preset_json / import_preset_file → ImportedPreset
  lorebooks.py        import_st_lorebook_json / import_lorebook_file → Lorebook
```

**Phases 1–28 and 30–38 complete (2026-05-25).** Capability summary:
- Phases 1–3: skeleton, SQLite, card import, session CRUD, gateway hook
- Phase 4: Prompt Compiler (chat + story renderers, card/persona assembly)
- Phase 5–6: Provider bridge, live model routing
- Phase 7: Live chat adapter (Hermes provider)
- Phase 8: Preset safety classification
- Phase 9–10: ST preset import, preset use in compiler
- Phase 11: Content mode manager (safe / adult-fiction)
- Phase 12: Lorebook import, keyword/regex matching, token budget
- Phase 13: Memory summary (auto-summarize, set, debug)
- Phase 14: Turn controls (retry, undo, edit last)
- Phase 15: Session browser (list, switch, rename, archive, clone)
- Phase 16: Mobile asset browser (/rp assets, /rp cards, /rp card inspect/use)
- Phase 17: Mobile inspect parity (/rp cards pagination, /rp preset inspect improved, /rp lore inspect, /rp session info)
- Phase 18: Paginated history + session browser (mobile browse pagination)
- Phase 19: Live provider hardening + E2E generation pipeline (base_url safety, error envelope, /rp model test, E2E test)
- Phase 20: ST Macro Engine v1 + Prompt Fidelity (template-only macro expansion for `{{char}}`, `{{user}}`, date/time, content mode, and session title across card/preset/lore/memory/history/user message)
- Phase 21: Persona v1 (SillyTavern-like user personas imported as session-scoped `persona:<name>` prompt modules)
- Phase 22: Author's Note / Scene Note v1 (session-scoped `note:author` prompt module with position and frequency controls)
- Phase 23: Mobile Export Delivery (`/rp export` writes under `get_hermes_home()` and returns quoted `MEDIA:"<path>"` for gateway attachment delivery)
- Phase 24: Mobile Attachment Import v1 (`/rp preset import`, `/rp lore import`, and `/rp persona import` can import exactly one local attachment from `event.media_urls` when no path is supplied)
- Phase 25: Mobile Import Follow-up Actions v1 (successful card, preset, lorebook, and persona imports return compact inspect/use/start command hints using short IDs)
- Phase 26: Session Quick Actions v1 (`last` resolves to the session-lifetime most recently imported card, preset, lorebook, or persona)
- Phase 27: Mobile Turn Controls Polish v1 (`/rp retry`, `/rp undo`, and `/rp edit last` return compact action headers plus repeat-command hints)
- Phase 28: Provider Error Recovery (connection/timeout provider failures return compact retryable messages while the generic provider error boundary remains intact)
- Phase 30: RP Speech Command Surface (`/rp speak` placeholder and in-memory `/rp voice [on|off]` flag; no real TTS calls yet)
- Phase 31: Plugin Hardening (top-level command exception boundary, malformed event/session-key guards, and 50-item browse limits)
- Phase 32: Gateway Security and Session Isolation (gateway attachment import trust policy and scoped session switching)
- Phase 33: Provider and Media Safety Hardening (sanitized image provider failures, recursive provider debug redaction, and quoted MEDIA export regressions)
- Phases 34–38: SQLite performance hardening plus runtime command-family refactors for presets/content, lore, notes, and memory; command surface and prompt semantics unchanged
- Phase 121: Novel project layer (projects/chapters/scenes/canon/timeline/export)
- Phase 122: Scene goals (`/rp scene goal` set/inspect/clear), linked-session scene-goal prompt injection (before author note), and Markdown goal export visibility
- Phase 123: Scene narration controls (`/rp scene narration` inspect/clear/pov/tense), linked-session scene-narration prompt injection (before scene goal), and Markdown narration visibility
- Phase 124: Project style guide (`/rp project style` inspect/set/clear), linked-session project-style prompt injection, and Markdown style-guide export
- Phase 125: Lore Regex Complexity Guard (regex lore keys longer than 256 chars or with nested quantified groups are excluded before Python `re.search`; bounded rejection reasons available via `/rp lore test`/debug; no importer, schema, command, provider, or postprocessor behavior changes)
- Phase 126: Context Budget Report v1 (`/rp debug context [limit] [page]` renders a read-only prompt/context composition report with estimated tokens, omitted-layer summary, renderer/model/context-window metadata, and paginated rows; no prompt trimming, summarization, vectorization, provider tokenization/routing, storage, provider calls, or generation behavior changes)

### Plugin flow

```
Gateway event
  → pre_gateway_dispatch (gateway_hook.py)
      ├── /rp command? → TavernRuntime.handle_command_sync → reply → {"action": "skip"}
      ├── active session? → TavernRuntime.handle_active_message_sync → prompt pipeline → {"action": "skip"}
      └── otherwise → {"action": "allow"} → normal AIAgent dispatch
```

### Prompt pipeline (Phases 4–22 plus Phase 121–124 novel injections)

```
handle_active_message_sync
      → _run_generation_pipeline(session, user_text, history, event)
      → _build_macro_context      (char from card; user from event; session/content mode from session)
      → _session_prompt_modules  (preset + project_style + canon + persona + scene_narration + scene_goal + note + memory + lore modules)
      → PromptCompiler.compile   (card + modules + history + user message → macro-expanded CompiledPrompt)
      → ModelRouter.resolve      (session row → ModelDescriptor)
      → ChatRenderer.render      (CompiledPrompt → messages list)
      → adapter.generate         (FakeAdapter | HermesAdapter)
```

Macro expansion is one-pass and allowlist-based. Supported Phase 20 macros are
`{{char}}`, `{{user}}`, `{{time}}`, `{{date}}`, `{{datetime}}`, `{{weekday}}`,
`{{content_mode}}`, and `{{session_title}}`; names are case/whitespace tolerant,
unknown macros are preserved, and replacement text is not recursively expanded.

### /rp command surface (current through Phase 126)

```
/rp help | status | assets
/rp cards [limit] [page]                    ← paginated (Phase 17)
/rp card import <file> | inspect <card> | use <card>     ← `last` resolves to the session-lifetime most recently imported card
/rp start <card> | end | retry | undo | edit last <text> ← `/rp start last` starts the most recently imported card; retry/undo/edit replies include mobile repeat hints
/rp speak | voice [on|off]                   ← placeholder speech surface; no real TTS/network call yet
/rp history [limit] [page]                  ← paginated chronological (Phase 18)
/rp debug prompt                              ← includes macro context summary; never raw event JSON
/rp debug context [limit] [page]             ← read-only context budget report with estimated tokens, omitted-layer summary, and paginated rows (Phase 126)
/rp export [markdown|st-json]                ← returns file path + quoted MEDIA attachment (Phase 23)
/rp session info                            ← new (Phase 17)
/rp sessions [all] [limit] [page]           ← paginated (Phase 18)
/rp switch <id> | rename <name> | archive | clone [name]
/rp preset import [file] | list | inspect <preset> | use <preset>      ← `last` resolves to the session-lifetime most recently imported preset
/rp lore import [file] | list | inspect <lorebook> | use <lorebook> | test <msg> | debug  ← `last` resolves to the session-lifetime most recently imported lorebook
/rp persona import [file] | list [limit] [page] | inspect <persona> | use <persona> | clear | debug  ← `last` resolves to the session-lifetime most recently imported persona
/rp note set <text> | clear | inspect | position [before_char|after_history|before_user] | frequency [always|every_n [n]]
/rp memory add <fact> | list [limit] [page] | summary [set <text>|summarize [limit]] | debug
/rp content mode [safe|adult-fiction]
/rp model status | profiles | seed apiyi | use <profile> | mode [fake|hermes] | live [status|confirm|off] | test
/rp project create/list/info/set/export
/rp project style [project-id]
/rp project style inspect [project-id]
/rp project style set [project-id] <text>
/rp project style clear [project-id]
/rp chapter create/list
/rp scene create/list/start
/rp scene goal <scene-id> [text]
/rp scene goal clear <scene-id>
/rp scene narration <scene-id>
/rp scene narration clear <scene-id>
/rp scene narration pov <scene-id> <label>
/rp scene narration tense <scene-id> <past|present>
/rp canon add/list/group
/rp timeline add/list
```

### DB schema (current through Phase 124)

```sql
cards(id, name, data_json, source_path, created_at)
sessions(id, session_key UNIQUE, scope_key, card_id, status, title,
         preset_id, lorebook_id, persona_id, content_mode,
         note_text, note_position, note_frequency, note_every_n,
         adapter_mode, live_confirmed, created_at, updated_at)
messages(id, session_id, role, content, created_at, metadata_json)
presets(id, name, source, raw_json, created_at)
prompt_modules(id, preset_id, name, role, content, enabled,
               position, insertion_order, raw_json, created_at)
lorebooks(id, name, source, raw_json, created_at)
lorebook_entries(id, lorebook_id, title, content, keys_json, secondary_keys_json,
                 enabled, constant, regex, position, insertion_order,
                 priority, probability, raw_json, created_at)
personas(id, name, content, raw_json, source_path, created_at)
session_memory_facts(id, session_key, content, importance, source, created_at)
session_summaries(id, session_key, content, created_at, updated_at)
novel_projects(id, title, summary, status, created_at, updated_at)
novel_project_style_guides(id, project_id, style_text, created_at, updated_at)
novel_chapters(id, project_id, title, chapter_number, summary, status, created_at, updated_at)
novel_scenes(id, chapter_id, session_id TEXT, title, summary, scene_number, status, created_at, updated_at)
novel_scene_goals(id, scene_id, goal_text, created_at, updated_at)
novel_scene_narration_controls(id, scene_id, pov_label, tense, created_at, updated_at)
novel_canon(id, project_id, title, content, canon_group, importance, created_at, updated_at)
novel_timeline(id, project_id, event_date, title, description, chapter_id, sort_key, created_at)
```

Phase 26 adds in-memory quick-action tracking on `TavernStore` only:
`_last_card_id`, `_last_preset_id`, `_last_lorebook_id`, and
`_last_persona_id`. These IDs are not persisted and reset when the runtime
process restarts.

Phase 27 is output-only for turn controls. Phases 28, 31, 32, and 33 add error
boundaries, bounds checks, trust policy, session-scope, and sanitization only.
Phase 30 adds an in-memory voice flag on `TavernRuntime`; it is not persisted.
These phases do not change schema or core prompt/generation assembly.

## 5. Key Architectural Decisions

- See `.codestable/compound/decisions/` for recorded decisions.
- **Plugins are Python-only entrypoints.** Rust requires a Python shim (subprocess/PyO3). See `2026-05-18-hermes-plugin-language.md`.
- Core files (`run_agent.py`, `cli.py`, `gateway/run.py`) must not be modified by the Tavern plugin.

## 6. Known Constraints / Hard Limits

- Never hard-code `~/.hermes` — use `get_hermes_home()`.
- All API keys in `~/.hermes/.env`, never in source.
- `pre_gateway_dispatch` return contract: `{"action": "skip"}` or `{"action": "allow"}` or `None`.
- Adult-fiction non-negotiable boundaries: see `HERMES_TAVERN_DESIGN.md §12.3`.
- Macro expansion is template-only — no Python/shell execution from imported assets.
- **Tavern provider base_url must pass `validate_provider_base_url()`**: only `https://` scheme allowed; private/loopback IPv4 ranges (127.x, 10.x, 192.168.x, 169.254.x, 172.16–31.x) and all IPv6 rejected. Error message never echoes the rejected URL.
- **Tavern live provider error envelope**: `_generate_with_session_adapter` catches all exceptions and returns a fixed bounded message — `str(exc)` is never forwarded to users.
- **Tavern image provider error envelope**: `/rp image ...` catches provider exceptions and returns a fixed bounded message with retry/status hints. Failed image jobs persist only sanitized generic error text, never `str(exc)`.
- **Tavern provider debug sanitizer**: provider/debug dicts must pass recursive, case-insensitive secret-key filtering before display. Secret-like keys include `api_key`, `access_token`, `password`, `secret`, and `token`.
- **Tavern export MEDIA contract**: `/rp export` returns quoted `MEDIA:"<path>"` markers so gateway adapters preserve attachment paths with spaces. Exports must not include raw event JSON or raw message metadata blobs.
- **Phase 121 reverse-scope constraints**: no cloud sync, no collaboration/multi-user workflow, no novel import, no timeline graphics, no DB credential persistence.
- **Tavern DB never persists `api_key` / `access_token`**: credentials resolved at runtime via `HermesRuntimeProviderResolver`, discarded after use.
- **Tavern lore regex complexity guard**: lorebook regex keys are screened locally before matching. Entries with patterns longer than 256 characters or nested quantified groups (for example `(a+)+`, `(.+)*`, `([a-z]+){2,}`) are excluded with bounded reasons (`regex rejected: ...`), preserving raw imported lore data while preventing unbounded local matching behavior.
