---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase150-lorebook-json-export"
date: "2026-06-07"
summary: >
  ACCEPTED - Adds one offline `/rp lore export <lorebook>` JSON export surface for
  stored lorebooks, with help/README visibility, focused tests, and completed
  architecture/root-design acceptance writeback.
tags: [hermes-tavern, lorebook, offline]
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
---

# Phase 150: Lorebook JSON Export

## Background

Phase 149 accepted single-card JSON export. Before S1 implementation, current
architecture was recorded through Phase 149, and recent Phase 143-149 checklists
were accepted. The root design still listed `lorebook export JSON` as a required
exporter, while source and README exposed lorebook import/list/inspect/use/clear/
enable/disable/test/debug only.

The safe next slice is one stored-lorebook JSON export command. It is local,
offline, command-visible, and follows the Phase 149 export pattern without
touching providers, prompts, retrieval, generation, project archives, schema, or
gateway/core files.

## Scope

Add `/rp lore export <lorebook>` under the existing lore command family.

Behavior:

- resolve `<lorebook>` with existing `TavernStore.get_lorebook(...)`, including
  `last`;
- export one stored lorebook to
  `get_hermes_home()/plugins/hermes-tavern/exports/lorebooks`;
- prefer stored `lorebooks.raw_json` when it parses as a JSON object;
- otherwise build a normalized fallback object from the lorebook row and existing
  `list_lorebook_entries(...)` rows;
- write pretty UTF-8 JSON;
- return a bounded success message with `file:` and quoted `MEDIA:"<path>"`;
- return existing bounded not-found messaging for missing lorebooks;
- return `Usage: /rp lore export <lorebook>` for missing/blank args;
- add generated help and README Core command visibility;
- add focused offline tests.

## Non-goals / Boundaries

Do not change lore import parsing, lore matching, regex safety guards, prompt
assembly, debug prompt/context output, context-budget reporting, provider/model
routing, generation, retrieval/vectorization, credential behavior, content-mode
behavior, minors/underage handling, safety-bypass behavior, project archive ZIP
import/export, schema/index/migration code, gateway/core files, plugin shims, or
build artifacts.

This phase does not implement preset export, card PNG export, bulk export,
project archive export/import, or automatic lore extraction.

## Proposed Design

The existing `lore_command(...)` dispatcher in `runtime_lore.py` already owns
nested lorebook commands. Add an `export` branch there, backed by a local helper
that renders the export payload and writes the file.

Payload selection:

1. Parse `lorebook["raw_json"]`.
2. If it is a JSON object, write it unchanged apart from pretty formatting.
3. If missing, invalid, or not an object, emit a normalized fallback:
   `name`, `source`, and `entries`, where entries are derived from current
   stored rows using title/content/keys/secondary_keys/enabled/constant/regex/
   position/insertion_order/priority/probability.

The command writes only under the profile-safe Hermes home path from
`get_hermes_home()`. File names must sanitize the lorebook id so path-like ids
cannot escape the export directory.

Help and docs should add `/rp lore export <lorebook>` next to existing lorebook
commands.

## S1 Allowed Files

- `src/hermes_tavern/runtime_lore.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_lore_runtime.py`
- `tests/test_hermes_tavern_commands.py`
- `tests/test_hermes_tavern_readme_docs.py`

## S1 Prohibited Files

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime.py`
- `src/hermes_tavern/prompt.py`
- `src/hermes_tavern/runtime_prompt_modules.py`
- `src/hermes_tavern/model_router.py`
- `src/hermes_tavern/provider_bridge.py`
- `src/hermes_tavern/adapters.py`
- `src/hermes_tavern/runtime_generation.py`
- `src/hermes_tavern/db.py`
- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`

## S1 Implementation Plan

1. Add `/rp lore export <lorebook>` dispatch and usage in `runtime_lore.py`.
2. Add local export helpers for safe filename construction, raw JSON preference,
   normalized fallback payload construction, and file writing under
   `get_hermes_home()`.
3. Add `/rp lore export <lorebook>` to `TAVERN_COMMAND_TABLE` help lines.
4. Add the command literal to README Core commands.
5. Add focused tests for raw export, normalized fallback, `last` resolution,
   missing/usage behavior, quoted `MEDIA` path with spaces, path containment, and
   no active-session/message mutation.
6. Add help and README docs tests for the literal.

## Acceptance Criteria

- AC1: `/rp lore export <lorebook>` writes one UTF-8 JSON file under
  `get_hermes_home()/plugins/hermes-tavern/exports/lorebooks`.
- AC2: Stored `raw_json` object exports unchanged except formatting.
- AC3: Invalid/missing/non-object raw JSON falls back to a normalized lorebook
  JSON object derived from existing stored lorebook and entry rows.
- AC4: `last` resolves through existing lorebook lookup behavior.
- AC5: Missing/blank args and missing lorebooks return bounded messages.
- AC6: The returned response includes `file:` and quoted `MEDIA:"<path>"`, and
  sanitized filenames cannot escape the lorebook export directory.
- AC7: Generated help and README Core commands include `/rp lore export <lorebook>`.
- AC8: Export does not mutate sessions, messages, lorebook rows, lorebook entry
  rows, prompt/debug/context behavior, or provider/generation state.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_lore.py src/hermes_tavern/commands.py tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/db.py src/hermes_tavern/db_novel.py src/hermes_tavern/importers plugins build/lib`

## Risks / Rollback

Primary risk is export-shape ambiguity between raw round-trip and current
entry-row state after `/rp lore enable/disable`. This phase resolves that by
matching Phase 149 card export: prefer preserved raw JSON when valid, otherwise
emit a normalized fallback. If the behavior is wrong, rollback is limited to
removing the `export` branch, helper, help/README literal, and focused tests.

## S1 Implementation Result

Codex architect returned `RESULT: READY_TO_IMPLEMENT` for S1 in
`/tmp/hermes-tavern-architect-phase150-s1.jsonl`. Codex executor implemented the
bounded slice in `/tmp/hermes-tavern-executor-phase150-s1.jsonl`, limited to the
S1 allowed runtime/help/README/test files. Controller verification passed:

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_lore.py src/hermes_tavern/commands.py tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` (`105 passed`)
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` (`1080 passed`)
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` (`1080 passed`)
- protected-file reverse-scope guard: empty output
- `git diff --check`

## S2 Acceptance Result

Codex architect returned `RESULT: READY_FOR_EXECUTOR` for the docs/status-only S2
closeout in `/tmp/hermes-tavern-architect-phase150-s2.jsonl`. Codex executor
drafted acceptance/writeback artifacts in `/tmp/hermes-tavern-executor-phase150-s2.jsonl`,
limited to CodeStable/current-state documentation. Controller verification passed:

- CodeStable frontmatter/YAML validators for this design, checklist, and acceptance report
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_lore.py src/hermes_tavern/commands.py tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` (`105 passed`)
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` (`1080 passed`)
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` (`1080 passed`)
- protected-path diff guard: empty output
- stale/current wording guards for Phase 150 docs
- `git diff --check`

Phase 150 is accepted. Broader lorebook bulk export, preset export, project archive
ZIP import/export, retrieval/vectorization coupling, provider/model/generation
behavior, content-mode/minors handling, and safety-bypass changes remain deferred.
