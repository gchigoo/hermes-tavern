---
doc_type: feature-design
status: approved
feature: "2026-06-06-hermes-tavern-phase148-card-greeting-inspect"
date: "2026-06-06"
summary: >
  Phase 148 S1 adds a read-only /rp card greeting <card> surface that lists
  first_mes and alternate greetings for one stored character card without
  requiring an active session or mutating chat history. S2 acceptance/writeback
  remains planned.
tags: [hermes-tavern, card, greeting, command-surface, read-only, offline]
created: "2026-06-06"
updated: "2026-06-06"
owner: codestable-cron
---

# Phase 148: Card Greeting Inspect

## Background

No planned or in-progress checklist remains after Phase 147. The root design still
lists `/rp card greeting <card>` in the character-card command vision, while the
current implementation exposes only active-session `/rp greeting list/use <n>` and
`/rp card inspect <card>` only reports the greeting count.

This is a small SillyTavern asset-compatibility gap: users can inspect whether a
card has greetings, but cannot list those greetings before starting or rebinding a
session.

## Scope

Add one local, offline, read-only command:

- `/rp card greeting <card>` under the existing card command family.
- Resolve `<card>` through the same stored-card reference behavior used by
  `/rp card inspect <card>`, including `last`.
- Render `first_mes` as index `0` and nonblank `alternate_greetings` as indexes
  `1..N`, using bounded mobile previews.
- Return a bounded no-greetings message when the stored card has no greetings.
- Generated `/rp help` and README Core commands include the new literal.

## Non-goals / Boundaries

This phase does not add `/rp card greeting use`, does not select a greeting, does
not append assistant messages, does not start or bind a session, and does not change
`/rp greeting list/use <n>` active-session behavior.

No schema, import/export, prompt/debug/context-budget, provider/model routing,
generation, credentials, retrieval/vectorization, content-mode, media/TTS/image,
archive/import, automatic extraction, minors/underage, safety-bypass, plugin
registration, or protected Hermes core behavior changes are in scope.

Do not edit `run_agent.py`, `cli.py`, `gateway/run.py`, `src/hermes_tavern/runtime.py`,
provider/prompt/generation/importer files, `plugins/**`, or `build/lib/**`.

## Proposed Design

Current noun layer:

- Stored cards already persist `first_mes` and `alternate_greetings` in `cards.data_json`.
- `TavernStore.get_card(card_id_or_name)` already resolves card ids, short ids, names,
  and the process-local `last` card reference.
- `runtime_turns.greeting_options(data)` already normalizes first and alternate
  greetings into indexed options.

Change:

- Extend `card_command` with a `greeting` subcommand.
- Add a card-family read renderer in `runtime_assets.py` that loads one card,
  parses stored JSON, calls the existing greeting option normalization through the
  runtime, and formats bounded preview rows.
- Extend card usage/help literals and README Core commands.

Flow:

```text
/rp card greeting <card>
  -> TAVERN_COMMAND_TABLE["card"]
  -> runtime_assets.card_command
  -> card_greeting
  -> TavernStore.get_card(ref)
  -> existing greeting_options(data)
  -> bounded read-only mobile output
```

No micro-refactor is needed. `runtime_assets.py` already owns card subcommands,
and `runtime_turns.py` already owns greeting normalization.

## S1 Allowed Files

- `src/hermes_tavern/runtime_assets.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_mobile_browsers.py`
- `tests/test_hermes_tavern_commands.py`
- `tests/test_hermes_tavern_readme_docs.py`

## S1 Prohibited Files

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime.py`
- `src/hermes_tavern/db.py`
- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/prompt.py`
- `src/hermes_tavern/runtime_prompt_modules.py`
- `src/hermes_tavern/model_router.py`
- `src/hermes_tavern/provider_bridge.py`
- `src/hermes_tavern/adapters.py`
- `src/hermes_tavern/runtime_generation.py`
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`
- `design/**` during S1 implementation, except controller-owned materialization

## S1 Implementation Plan

1. Add `/rp card greeting <card>` to the card command table help lines and card usage text.
2. Add read-only `card_greeting` handling under `runtime_assets.card_command`.
3. Render greeting rows with bounded previews and no session/message mutation.
4. Add focused tests for normal, missing-card, no-greetings, `last`, help, and README visibility.
5. Run focused tests and Tavern-wide pytest offline.

## S1 Controller Verification

S1 was implemented on 2026-06-06 by Codex executor with Hermes controller
verification. S2 acceptance/writeback remains a separate planned slice.

- Architect artifact: `/tmp/hermes-tavern-architect-phase148-s1.jsonl` —
  `RESULT: READY_TO_IMPLEMENT`, `IMPLEMENTATION_READY=true`.
- Executor smoke artifact: `/tmp/hermes-tavern-executor-smoke-phase148-s1.jsonl` —
  `EXECUTOR_SMOKE_OK`; no files edited.
- Executor artifact: `/tmp/hermes-tavern-executor-phase148-s1.jsonl` — implemented
  the nested card greeting inspect surface in allowed files. Executor JSONL had
  harmless failed discovery/sed probes and an executor-sandbox Tavern-wide
  image-provider failure; the controller reran verification successfully.
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/commands.py src/hermes_tavern/runtime_assets.py tests/test_hermes_tavern_mobile_browsers.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_mobile_browsers.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` — 145 passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` — 1065 passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` — 1065 passed.
- Protected-path diff guard for core/DB/prompt/provider/importer/plugin/build/design
  paths was empty before controller-owned status synchronization; final diff remains scoped.
- `git diff --check` passed.

## S2 Acceptance / Writeback

S2 is separate. It may update only the Phase 148 CodeStable artifacts plus
architecture/root-design current-state docs to record that `/rp card greeting <card>`
is now current read-only card metadata inspection. S2 must not edit source, tests,
README, protected core files, provider/prompt/generation files, importer files,
plugin files, or build outputs.

## Acceptance Criteria

1. `/rp card greeting <card>` returns bounded indexed greetings for one stored card.
2. The command works without an active session and does not create, start, bind, or mutate a session.
3. `last` resolves consistently with existing card inspect/use behavior.
4. Missing cards return the existing card-not-found style response.
5. Cards with no `first_mes` and no nonblank alternates return a bounded no-greetings message.
6. Generated help and README Core commands include `/rp card greeting <card>`.
7. No schema, prompt/debug/context-budget, provider/model, generation, credential,
   retrieval/vectorization, content-mode, media/TTS/image, import/export, archive,
   automatic extraction, minors/underage, safety-bypass, plugin registration, or
   protected core behavior changes occur.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/commands.py src/hermes_tavern/runtime_assets.py tests/test_hermes_tavern_mobile_browsers.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_mobile_browsers.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`

## Risks / Rollback

Risk: card greeting inspection could accidentally reuse `/rp greeting use` behavior
and append messages. Mitigation: keep the handler in `runtime_assets.py`, do not
call `runtime_turns.greeting`, and test that no active session/history mutation is
required.

Rollback is simple: remove the card subcommand branch, help/README literal, and
focused tests. No data migration rollback is needed.
