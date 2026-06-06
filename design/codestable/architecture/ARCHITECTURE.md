# Hermes Agent — Architecture

> Status: current snapshot
> Last updated: 2026-06-07

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
db_novel.py           Novel domain mixins for project/chapter/scene/scene-goal/canon/timeline/relationship/character-state/location/organization CRUD and export
runtime_novel.py      Novel command family handlers for /rp project/chapter/scene/scene-goal/canon/timeline/relationship/character-state/location/organization
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
- Phase 127: Project Brief v1 metadata (`/rp project brief` + `/rp project info`, and `## Project Brief` export) backed by `novel_project_briefs`; metadata-only, no prompt/provider/routing/generation behavior changes
- Phase 128: Project Outline v1 metadata (`/rp project outline` + `## Outline`) backed by `novel_project_outlines`; metadata-only, no prompt/provider/routing/content-mode/generation behavior changes
- Phase 129: Chapter and Scene Summary metadata (`/rp chapter summary`, `/rp scene summary`) backed by existing `novel_chapters.summary` / `novel_scenes.summary`; metadata-only, no prompt/provider/routing/content-mode/generation changes
- Phase 130: Relationship State Metadata v1 (`/rp relationship ...`) backed by `novel_relationship_states`; metadata-only, no prompt/provider/routing/content-mode/generation changes.
- Phase 131: Character State Metadata v1 (`/rp character state ...`) backed by `novel_character_states`; metadata-only, no prompt/debug/context-budget/vectorization/retrieval/provider/model-routing/content-mode/generation/credential side effects. Export is optional and local-only as `## Characters`.
- Phase 132: Location Metadata v1 (`/rp location ...`) backed by `novel_locations`; metadata-only, no prompt/provider/model-routing/content-mode/generation side effects. Export is optional and local-only as `## Locations`.
- Phase 133: Organization Metadata v1 (`/rp organization ...`) backed by `novel_organizations`; metadata-only, no prompt/provider/model-routing/content-mode/generation side effects. Export is optional and local-only as `## Organizations`.
- Phase 134: Plot Thread Metadata v1 (`/rp plot thread ...`) backed by `novel_plot_threads`; metadata-only, no prompt/provider/model-routing/content-mode/generation side effects. Export is optional and local-only as `## Plot Threads`.
- Phase 135: Style Sample Metadata v1 (`/rp style sample ...`) backed by `novel_style_samples`; metadata-only, no prompt/provider/model-routing/content-mode/generation side effects. Export is optional and local-only as `## Style Samples`.
- Phase 137: Default Bindings Metadata v1 (`/rp binding set/list/inspect/clear`) backed by `novel_default_bindings`; metadata-only, command/export visible only. Unique scope constraint uses `UNIQUE(scope_type, scope_id, asset_type)` with `idx_novel_default_bindings_scope`. No prompt/debug/context/provider/model/content/generation/media/archival/graph/safety behavior changes.
- Phase 138: Scene Beat Metadata v1 (`/rp scene beat add/list/inspect/update/delete`) backed by `novel_scene_beats`; metadata-only, command/export visible only for owning scene. No prompt/debug/context/provider/model/content/credential/retrieval/vectorization/generation/media/archive/graph/extraction/safety behavior changes.
- Phase 139: Revision Notes Metadata v1 (`/rp project revision add/list/inspect/update/delete`) backed by `novel_revision_notes`; metadata-only, command/export-visible only, and no prompt/debug/context/provider/model/content/credential/retrieval/vectorization/generation/media/archive/graph/extraction/safety behavior changes.
- Phase 140: Relationship Label Rename (`/rp relationship rename <relationship-id> <label>`) backed by
  `novel_relationship_states` metadata; metadata-only, command/export-visible only, and no prompt/debug/context/provider/model/content/credential/retrieval/vectorization/generation/media/archive/graph/extraction/safety behavior changes.
- Phase 143: Canon Inspect Surface (`/rp canon inspect <canon-id>`) reads one existing
  `novel_canon` row by id for command-visible inspection only; no schema, ordering,
  prompt/module, provider/model, generation, retrieval/vectorization, archive/import,
  credential, safety behavior, or deferred `/rp canon check` / `/rp canon conflict` /
  `/rp canon pin` tooling changes.
- Phase 144: Timeline Inspect Surface (`/rp timeline inspect <timeline-id>`) reads one existing
  `novel_timeline` row by id for command-visible inspection only; no schema, ordering,
  export, prompt/module, provider/model, generation, retrieval/vectorization,
  archive/import, credential, safety behavior, or deferred timeline tooling changes.
- Phase 145: Chapter Inspect Surface (`/rp chapter inspect <chapter-id>`) reads one
  existing `novel_chapters` row by id for command-visible inspection only; no
  schema, ordering, summary mutation, export, prompt/module, provider/model,
  generation, retrieval/vectorization, archive/import, credential, safety behavior,
  or deferred chapter-editing tooling changes.
- Phase 146: Scene Inspect Surface (`/rp scene inspect <scene-id>`) reads one
  existing `novel_scenes` row by id for command-visible inspection only; no
  schema, ordering, summary mutation, scene mutation, scene start/linking, export,
  prompt/module, provider/model, generation, retrieval/vectorization, archive/import,
  credential, content-mode, minors/underage, safety behavior, or deferred scene-editing
  tooling changes.
- Phase 147: Project Inspect Alias (`/rp project inspect <project-id>`) reads one
  existing `novel_projects` row by id via the existing `/rp project info <id>`
  rendering/getter path; no schema, project mutation, export, prompt/module,
  provider/model, generation, retrieval/vectorization, credential, content-mode,
  minors/underage, safety behavior, or deferred project lifecycle/tooling changes.
- Phase 148: Card Greeting Inspect (`/rp card greeting <card>`) reads one existing
  stored card row via the existing `get_card(card_id_or_name)` resolver (including
  `last`) and existing greeting normalization. It renders one bounded `first_mes`
  row plus nonblank `alternate_greetings` rows as indexed options; no schema,
  card/session/message mutation, prompt/module, provider/model/generation,
  retrieval/vectorization, credential, archive/import/export, content-mode,
  minors/underage, or safety-bypass behavior changes.
- Phase 149: Card JSON Export (`/rp card export <card>`) reads one existing stored
  card via the same `get_card(card_id_or_name)` resolver (including `last`) and
  writes one UTF-8 JSON file under
  `get_hermes_home()/plugins/hermes-tavern/exports/cards` with quoted `MEDIA`
  attachment output. It prefers `cards.data_json.raw` if it is JSON, otherwise
  normalizes an ST-compatible fallback payload from existing card fields; no schema
  or table/index migrations are added and no prompt/provider/model/generation,
  retrieval/vectorization, content-mode, minors/underage, or safety-bypass behavior
  changes occur.
- Phase 150: Lorebook JSON Export (`/rp lore export <lorebook>`) reads one existing
  stored lorebook via the same resolver behavior (`get_lorebook(lorebook_id_or_name)`,
  including `last`) and writes one UTF-8 JSON file under
  `get_hermes_home()/plugins/hermes-tavern/exports/lorebooks` with quoted `MEDIA`
  attachment output. It prefers `lorebooks.raw_json` if it parses to a JSON object;
  otherwise it normalizes ST-compatible fallback payload fields from existing
  lorebook and `lorebook_entries` rows; no schema/table/index migrations are added
  and no prompt/provider/model/generation, retrieval/vectorization, content-mode,
  minors/underage, safety-bypass, project archive, or ST importer/exporter behavior
  changes occur.

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

Project Brief, Project Outline, Relationship State, Character State, Location,
Organization, Plot Thread, Style Sample, Default Bindings, Revision Notes, and
Scene Beat metadata are
explicitly excluded from prompt assembly, session prompt module selection, debug
prompt/context payloads, and context-budget reporting. Relationship, character-state,
location, organization, plot-thread, style-sample, default-binding,
revision-note, and scene-beat metadata are also excluded
from vectorization/retrieval, provider/model routing, content mode,
credentials, automation, summarization, and generation; they are visible only
through command output and Markdown export.

### /rp command surface (current through Phase 150)

```
/rp help | status | assets
/rp cards [limit] [page]                    ← paginated (Phase 17)
/rp card import <file> | inspect <card> | use <card> | export <card> | greeting <card>     ← `last` resolves to the session-lifetime most recently imported card
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
/rp lore import [file] | list | inspect <lorebook> | export <lorebook> | use <lorebook> | test <msg> | debug  ← `last` resolves to the session-lifetime most recently imported lorebook
/rp persona import [file] | list [limit] [page] | inspect <persona> | use <persona> | clear | debug  ← `last` resolves to the session-lifetime most recently imported persona
/rp note set <text> | clear | inspect | position [before_char|after_history|before_user] | frequency [always|every_n [n]]
/rp memory add <fact> | list [limit] [page] | summary [set <text>|summarize [limit]] | debug
/rp content mode [safe|adult-fiction]
/rp model status | profiles | seed apiyi | use <profile> | mode [fake|hermes] | live [status|confirm|off] | test
/rp project create/list/info/set/export
/rp project inspect <project-id>
/rp project style [project-id]
/rp project style inspect [project-id]
/rp project style set [project-id] <text>
/rp project style clear [project-id]
/rp project brief [project-id]
/rp project brief inspect [project-id]
/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>
/rp project brief type clear <project-id>
/rp project brief premise set <project-id> <text>
/rp project brief premise clear <project-id>
/rp project outline [project-id]
/rp project outline inspect [project-id]
/rp project outline set [project-id] <text>
/rp project outline clear [project-id]
/rp chapter create/list
/rp chapter inspect <chapter-id>
/rp chapter summary <chapter-id> [text]
/rp chapter summary clear <chapter-id>
/rp scene create/list/start
/rp scene inspect <scene-id>
/rp scene summary <scene-id> [text]
/rp scene summary clear <scene-id>
/rp scene goal <scene-id> [text]
/rp scene goal clear <scene-id>
/rp scene narration <scene-id>
/rp scene narration clear <scene-id>
/rp scene narration pov <scene-id> <label>
/rp scene narration tense <scene-id> <past|present>
/rp scene beat add <scene-id> <label> <beat...>
/rp scene beat list <scene-id>
/rp scene beat inspect <beat-id>
/rp scene beat update <beat-id> <beat...>
/rp scene beat delete <beat-id>
/rp project revision add <project-id> <label> <note...>
/rp project revision list [project-id]
/rp project revision inspect <note-id>
/rp project revision update <note-id> <note...>
/rp project revision delete <note-id>
/rp canon add/list/group | /rp canon inspect <canon-id>
/rp timeline add/list | /rp timeline inspect <timeline-id>
/rp character state add <project-id> <label> <state...>
/rp character state list [project-id]
/rp character state inspect <character-state-id>
/rp character state update <character-state-id> <state...>
/rp character state delete <character-state-id>
/rp location add <project-id> <label> <description...>
/rp location list [project-id]
/rp location inspect <location-id>
/rp location update <location-id> <description...>
/rp location delete <location-id>
/rp organization add <project-id> <label> <description...>
/rp organization list [project-id]
/rp organization inspect <organization-id>
/rp organization update <organization-id> <description...>
/rp organization delete <organization-id>
/rp plot thread add <project-id> <label> <description...>
/rp plot thread list [project-id]
/rp plot thread inspect <plot-thread-id>
/rp plot thread update <plot-thread-id> <description...>
/rp plot thread delete <plot-thread-id>
/rp style sample add <project-id> <label> <sample...>
/rp style sample list [project-id]
/rp style sample inspect <style-sample-id>
/rp style sample update <style-sample-id> <sample...>
/rp style sample delete <style-sample-id>
/rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id>
/rp binding list <project|chapter|scene> <scope-id>
/rp binding inspect <binding-id>
/rp binding clear <binding-id>
/rp relationship add <project-id> <label> <state...>
/rp relationship list [project-id]
/rp relationship inspect <relationship-id>
/rp relationship rename <relationship-id> <label>
/rp relationship update <relationship-id> <state...>
/rp relationship delete <relationship-id>
```

### DB schema (current through Phase 150; unchanged by Phase 150)

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
novel_project_briefs(id, project_id, project_type, premise_text, created_at, updated_at)
-- project_id REFERENCES novel_projects(id) ON DELETE CASCADE, unique per project
-- project_type in {novel, serial, rp, worldbuilding, other}
CREATE INDEX idx_novel_project_briefs_project ON novel_project_briefs(project_id)
novel_project_outlines(id, project_id, outline_text, created_at, updated_at)
-- project_id REFERENCES novel_projects(id) ON DELETE CASCADE, unique per project
CREATE INDEX idx_novel_project_outlines_project ON novel_project_outlines(project_id)
novel_chapters(id, project_id, title, chapter_number, summary, status, created_at, updated_at)
novel_scenes(id, chapter_id, session_id TEXT, title, summary, scene_number, status, created_at, updated_at)
novel_scene_goals(id, scene_id, goal_text, created_at, updated_at)
novel_scene_narration_controls(id, scene_id, pov_label, tense, created_at, updated_at)
novel_canon(id, project_id, title, content, canon_group, importance, created_at, updated_at)
novel_timeline(id, project_id, event_date, title, description, chapter_id, sort_key, created_at)
novel_relationship_states(id, project_id, label, state_text, created_at, updated_at)
-- project_id REFERENCES novel_projects(id) ON DELETE CASCADE
CREATE INDEX idx_novel_relationship_states_project ON novel_relationship_states(project_id)
novel_character_states(id, project_id, label, state_text, created_at, updated_at)
-- project_id REFERENCES novel_projects(id) ON DELETE CASCADE
CREATE INDEX idx_novel_character_states_project ON novel_character_states(project_id)

novel_locations(id, project_id, label, description_text, created_at, updated_at)
-- project_id REFERENCES novel_projects(id) ON DELETE CASCADE
CREATE INDEX idx_novel_locations_project ON novel_locations(project_id)
novel_organizations(id, project_id, label, description_text, created_at, updated_at)
-- project_id REFERENCES novel_projects(id) ON DELETE CASCADE
CREATE INDEX idx_novel_organizations_project ON novel_organizations(project_id)
novel_plot_threads(id, project_id, label, description_text, created_at, updated_at)
-- project_id REFERENCES novel_projects(id) ON DELETE CASCADE
CREATE INDEX idx_novel_plot_threads_project ON novel_plot_threads(project_id)
novel_style_samples(id, project_id, label, sample_text, created_at, updated_at)
-- project_id REFERENCES novel_projects(id) ON DELETE CASCADE
CREATE INDEX idx_novel_style_samples_project ON novel_style_samples(project_id)
novel_revision_notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    note_text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
)
CREATE INDEX idx_novel_revision_notes_project
    ON novel_revision_notes(project_id, id)

novel_default_bindings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scope_type TEXT NOT NULL,
    scope_id INTEGER NOT NULL,
    asset_type TEXT NOT NULL,
    asset_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
)
-- UNIQUE(scope_type, scope_id, asset_type)
CREATE INDEX idx_novel_default_bindings_scope
    ON novel_default_bindings(scope_type, scope_id)
novel_scene_beats(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scene_id INTEGER NOT NULL,
    label TEXT NOT NULL,
    beat_text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
)
-- scene_id REFERENCES novel_scenes(id) ON DELETE CASCADE
CREATE INDEX idx_novel_scene_beats_scene ON novel_scene_beats(scene_id, id)
```

Phase 129 adds explicit semantics on existing summary columns:

- `novel_chapters.summary` is reused as chapter summary metadata for command-driven
  chapter summaries.
- `novel_scenes.summary` is reused as scene summary metadata for command-driven
  scene summaries.
- Both columns can store raw DB text; UI/runtime treats blank or whitespace-only
  summary text as not-visible and omits it from getters and Markdown export.

Phase 130 adds `novel_relationship_states` as project-scoped relationship-state
metadata. Relationship-state rows are managed through `/rp relationship ...` and
exported as optional `## Relationships` Markdown metadata; they are not selected
for prompt modules, debug/context-budget payloads, vectorization/retrieval,
provider/model routing, content mode, credentials, or generation.
Phase 140 adds `/rp relationship rename <relationship-id> <label>`. It updates only
`novel_relationship_states.label` and `updated_at`, preserves row identity and
`state_text`, and keeps existing deterministic ordering.

Phase 143 adds `get_canon(canon_id)` as a read-only helper used only by `/rp canon
inspect <canon-id>`. It returns one existing `novel_canon` row or `None`, is
command-visible only, and has no prompt/module selection, provider/model,
generation, retrieval/vectorization, archive/import, credential, or safety side
effects.

Phase 144 adds `get_timeline_event(timeline_event_id)` as a read-only helper used
only by `/rp timeline inspect <timeline-id>`. It returns one existing
`novel_timeline` row or `None`, is command-visible only, and has no schema,
ordering, export, prompt/module selection, provider/model, generation,
retrieval/vectorization, archive/import, credential, or safety side effects.

Phase 145 uses existing `get_chapter(chapter_id)` as a read-only helper for
`/rp chapter inspect <chapter-id>`. It returns one existing `novel_chapters` row
or `None`, is command-visible only, and has no schema, ordering, summary
mutation, export, prompt/module selection, provider/model, generation,
retrieval/vectorization, archive/import, credential, or safety side effects.
Phase 146 uses existing `get_scene(scene_id)` as a read-only helper for
`/rp scene inspect <scene-id>`. It returns one existing `novel_scenes` row or
`None`, is command-visible only, and has no schema, ordering, summary mutation,
scene mutation, scene start/linking, export, prompt/module selection, provider/model,
generation, retrieval/vectorization, archive/import, credential, content-mode,
minors/underage, or safety side effects.
Phase 147 uses the existing `/rp project info <id>` rendering/getter path for
`/rp project inspect <project-id>`. It reads one existing `novel_projects` row via
`get_project(project_id)`, includes current brief/outline preview helpers when
present, is command-visible only, and has no schema, project mutation, export,
prompt/module selection, provider/model, generation, retrieval/vectorization,
credential, content-mode, minors/underage, or safety side effects.

Phase 148 uses the existing stored-card lookup plus
`runtime_turns.greeting_options(data)` for `/rp card greeting <card>`. It reads
`cards.data_json` fields (`first_mes` and nonblank `alternate_greetings`) and
renders bounded command output only; it adds no schema/table/index migration and
has no card/session/message mutation, prompt/module selection, provider/model,
generation, import/export, retrieval/vectorization, credential, content-mode,
minors/underage, or safety side effects.

Phase 149 exports one existing stored character card through `/rp card export <card>`.
It uses `TavernStore.get_card(card_id_or_name)` including `last` resolution, and
returns one UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/cards`.
It prefers `data_json.raw` when present as a JSON object and otherwise writes a
normalized fallback payload from existing stored card fields. It makes no schema,
index, or migration changes, does not mutate sessions/messages, and leaves prompt,
provider/model, generation, retrieval/vectorization, content-mode, minors/underage,
and safety-bypass behavior unchanged.

Phase 131 adds `novel_character_states` as project-scoped character metadata.
Character-state rows are managed through `/rp character state ...` and emitted as
optional `## Characters` Markdown metadata; they are not selected for prompt
modules, debug/context-budget payloads, vectorization/retrieval,
provider/model routing, content mode, credentials, or generation.

Phase 132 adds `novel_locations` as project-scoped location metadata.
Location rows are managed through `/rp location add/list/inspect/update/delete`
and emitted as optional `## Locations` Markdown metadata; they are not selected
for prompt modules, debug/context payloads, context-budget payloads,
vectorization/retrieval, provider/model routing, content mode, credentials,
automation, summarization, generation, or retrieval.

Phase 133 adds `novel_organizations` as project-scoped organization metadata.
Organization rows are managed through `/rp organization add/list/inspect/update/delete`
and emitted as optional `## Organizations` Markdown metadata; they are not selected
for prompt modules, debug/context payloads, context-budget payloads,
vectorization/retrieval, provider/model routing, content mode, credentials,
automation, summarization, and generation.

Phase 134 adds `novel_plot_threads` as project-scoped plot-thread metadata.
Plot threads are managed through `/rp plot thread add/list/inspect/update/delete`
and emitted as optional `## Plot Threads` Markdown metadata in this order:
after `## Organizations`, before `## Characters`, `## Relationships`,
and `## Chapters`. They are not selected for prompt modules, debug/context
payloads, context-budget payloads, vectorization/retrieval,
provider/model routing, content mode, credentials, automation,
summarization, or generation.

Phase 135 adds `novel_style_samples` as project-scoped style-sample metadata.
Style samples are managed through `/rp style sample add/list/inspect/update/delete`
and emitted as optional `## Style Samples` Markdown metadata after `## Style Guide`
when present, or after `## Project Brief`/`## Outline` when no style guide exists.
The section appears before `## Locations`, `## Organizations`, `## Plot Threads`,
`## Characters`, `## Relationships`, and `## Chapters`, and is omitted when no
style-sample rows exist. They are not selected for prompt modules,
debug/context payloads, context-budget reporting, vectorization/retrieval,
provider/model routing, content mode, credentials, automation, summarization,
or generation.

Phase 137 adds `novel_default_bindings` and `/rp binding ...` command-family metadata
for `project`, `chapter`, and `scene` scopes with `card`, `preset`, `lorebook`,
or `persona` asset refs. These bindings are metadata-only and command/export
visible only (metadata marker text never appears in prompt/debug/context payloads).
Binding rows are constrained by `UNIQUE(scope_type, scope_id, asset_type)` and
indexed by `idx_novel_default_bindings_scope` for scoped export discovery. Phase
137 scope is explicitly command/export visible only and does not alter prompt
compiler, prompt modules, debug prompt/context, context budget reporting,
provider/model routing, content mode, credentials, generation, retrieval/vectorization,
media/TTS/image, archive, ST importer/exporter, graph, or safety-bypass behavior.
Phase 138 adds `novel_scene_beats` and `/rp scene beat ...` command-family metadata
for scene-scoped beats (`label`, `beat_text`). These rows are metadata-only and
command/export visible only for the owning scene. Scene-beat rows are excluded from
prompt/compiler, prompt modules, debug prompt/context, context-budget reporting,
provider/model routing, content mode, credentials, generation, retrieval/vectorization,
media/TTS/image, archive, ST importer/exporter, graph, or safety-bypass behavior.

Phase 139 adds `novel_revision_notes` and `/rp project revision ...`
command-family metadata for local project-scoped revision notes (`label`,
`note_text`). These rows are metadata-only and command/export visible only.
Revision-note rows are excluded from prompt/compiler, prompt modules, debug
prompt/context, context-budget reporting, provider/model routing, content mode,
credentials, generation, retrieval/vectorization, media/TTS/image, archive, ST
importer/exporter, graph, or safety-bypass behavior.

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
- **Tavern export MEDIA contract**: `/rp export`, `/rp card export <card>`, and
  `/rp lore export <lorebook>` return quoted `MEDIA:"<path>"` markers so gateway
  adapters preserve attachment paths with spaces. Exports must not include raw event
  JSON or raw message metadata blobs.
- **Phase 121 reverse-scope constraints**: no cloud sync, no collaboration/multi-user workflow, no novel import, no timeline graphics, no DB credential persistence.
- **Tavern DB never persists `api_key` / `access_token`**: credentials resolved at runtime via `HermesRuntimeProviderResolver`, discarded after use.
- **Phase 129 summary metadata boundary**: chapter/scene summary text is metadata-only and export-visible but not injected into prompt modules, context budgeting, vectorization, retrieval, provider routing, or generation.
- **Phase 130 relationship-state boundary**: relationship-state metadata is export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget payloads, vectorization/retrieval, provider/model selection, content mode decisions, credentials, and generation.
- **Phase 131 character-state boundary**: character-state metadata is export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget payloads, vectorization/retrieval, provider/model routing, content mode decisions, credentials, and generation.
- **Phase 132 location boundary**: location metadata is export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget payloads, vectorization/retrieval, provider/model routing, content mode decisions, credentials, automation, summarization, and generation.
- **Phase 133 organization boundary**: organization metadata is export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget payloads, vectorization/retrieval, provider/model routing, content mode decisions, credentials, automation, summarization, and generation.
- **Phase 134 plot-thread boundary**: plot-thread metadata is export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget payloads, vectorization/retrieval, provider/model routing, content mode decisions, credentials, automation, summarization, and generation.
- **Phase 135 style-sample boundary**: style-sample metadata is export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget reporting, vectorization/retrieval, provider/model routing, content mode decisions, credentials, automation, summarization, and generation.
- **Phase 137 default binding boundary**: default-binding metadata is command/export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget reporting, vectorization/retrieval, provider/model routing, content mode decisions, credentials, generation, media/TTS/image flow, archive, ST importer/exporter, graph, and safety-bypass behavior.
- **Phase 138 scene-beat boundary**: scene-beat metadata is command/export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget reporting, vectorization/retrieval, provider/model routing, content mode decisions, credentials, generation, media/TTS/image flow, archive, ST importer/exporter, graph, and safety-bypass behavior.
- **Phase 139 revision-notes boundary**: revision-note metadata is command/export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget reporting, vectorization/retrieval, provider/model routing, content mode decisions, credentials, generation, media/TTS/image flow, archive, ST importer/exporter, graph, and safety-bypass behavior.
- **Phase 140 relationship label rename boundary**: relationship-label rename updates only `label` and `updated_at`, preserves `id`, `project_id`, `state_text`, `created_at`, and row order, and is command/export-visible only. It is excluded from prompt modules, debug prompt/context output, context-budget reporting, vectorization/retrieval, provider/model routing, content-mode decisions, credentials, generation, media/TTS/image flow, archive, ST importer/exporter, graph/alias/merge-split/automatic extraction behaviors, and safety-bypass behavior.
- **Phase 144 timeline inspect boundary**: `/rp timeline inspect <timeline-id>` is command-visible metadata inspection only for existing `novel_timeline` rows. It keeps timeline schema, ordering, ordering-based export, prompt/module coupling, provider/model routing, generation, retrieval/vectorization, archive/import, credential persistence, automatic extraction, and safety bypass unchanged and deferred.
- **Phase 145 chapter inspect boundary**: `/rp chapter inspect <chapter-id>` is command-visible metadata inspection only for existing `novel_chapters` rows. It keeps chapter schema, ordering, summary storage/mutation, markdown export, prompt/provider/generation/retrieval/vectorization coupling, archive/import, credential persistence, automatic extraction, and safety bypass unchanged and deferred.
- **Phase 146 scene inspect boundary**: `/rp scene inspect <scene-id>` is command-visible metadata inspection only for existing `novel_scenes` rows. It keeps scene schema, ordering, summary mutation, scene mutation, scene start/linking, markdown export, prompt/provider/generation/retrieval/vectorization coupling, archive/import, credential persistence, content-mode behavior, minors/underage handling, automatic extraction, and safety bypass unchanged and deferred.
- **Phase 147 project inspect boundary**: `/rp project inspect <project-id>` is command-visible metadata inspection only for existing `novel_projects` rows. It reuses existing `/rp project info <id>` rendering/getter behavior (`get_project(project_id)` and existing brief/outline getters for the preview blocks) and keeps project schema/mutations/export, prompt/provider/generation coupling, retrieval/vectorization, credentials, content-mode, minors/underage handling, and safety-bypass behavior unchanged and deferred.
- **Phase 148 card greeting inspect boundary**: `/rp card greeting <card>` reads one
  existing stored card row and renders bounded `first_mes` + nonblank
  `alternate_greetings` rows through existing `get_card(...)` and
  `greeting_options(...)` behavior. It keeps card schema, card/session/message
  mutation, table/index migration, prompt/module coupling, provider/model routing,
  generation, retrieval/vectorization, credentials, content-mode, minors/underage,
  and safety-bypass behavior unchanged.
- **Phase 149 card export boundary**: `/rp card export <card>` reads one existing
  stored card and writes one UTF-8 JSON file under profile-safe exports. It keeps
  `cards` schema, table/index shape, migrations, card/session/message mutation,
  prompt/module coupling, provider/model routing, generation, retrieval/vectorization,
  credentials, content-mode, minors/underage, other archive/import/export boundaries,
  and safety-bypass behavior unchanged.
- **Phase 150 lorebook export boundary**: `/rp lore export <lorebook>` reads one
  existing stored lorebook and writes one UTF-8 JSON file under profile-safe exports.
  It keeps `lorebooks` and `lorebook_entries` schema/table shape, migrations,
  lorebook/session/message mutation, prompt/debug/context behavior, provider/model
  routing, generation, retrieval/vectorization, content-mode, credentials,
  minors/underage, project archive, ST importer/exporter, and safety-bypass behavior
  unchanged.
- **Tavern lore regex complexity guard**: lorebook regex keys are screened locally before matching. Entries with patterns longer than 256 characters or nested quantified groups (for example `(a+)+`, `(.+)*`, `([a-z]+){2,}`) are excluded with bounded reasons (`regex rejected: ...`), preserving raw imported lore data while preventing unbounded local matching behavior.
