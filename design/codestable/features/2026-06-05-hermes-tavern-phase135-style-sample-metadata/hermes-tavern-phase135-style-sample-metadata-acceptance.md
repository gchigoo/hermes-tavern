---
doc_type: feature-acceptance
feature: "2026-06-05-hermes-tavern-phase135-style-sample-metadata"
status: accepted
date: "2026-06-05"
summary: >
  Style Sample Metadata v1 is accepted as local project-scoped style-sample
  metadata backed by `novel_style_samples`, `/rp style sample` CRUD/list
  commands, help/README visibility from S1, optional `## Style Samples`
  Markdown export placement, and architecture/root-design writeback. It remains
  offline/export-only and excluded from prompt, debug-context, context-budget,
  provider, routing, generation, credential, retrieval, vectorization,
  automation, media, and safety-bypass paths.
tags: [novel, style-sample, metadata, export, offline, acceptance]
---

# Phase 135 Style Sample Metadata Acceptance

> Phase: S2 verify/accept/write architecture
> Controller verification date: 2026-06-05
> Design: `design/codestable/features/2026-06-05-hermes-tavern-phase135-style-sample-metadata/design.md`
> Checklist: `design/codestable/features/2026-06-05-hermes-tavern-phase135-style-sample-metadata/checklist.yaml`

## 1. Interface and schema contract

Accepted implementation surface:

- Schema: `novel_style_samples(id, project_id, label, sample_text, created_at, updated_at)`.
- Index: `idx_novel_style_samples_project` on `novel_style_samples(project_id)`.
- Project ownership: `project_id REFERENCES novel_projects(id) ON DELETE CASCADE`.
- Helpers:
  - `create_style_sample(project_id, label, sample_text)`
  - `list_style_samples(project_id)`
  - `get_style_sample(style_sample_id)`
  - `update_style_sample(style_sample_id, sample_text)`
  - `delete_style_sample(style_sample_id)`

Contract checks from S1 and S2 controller verification:

- [x] Migration creates the table and project index.
- [x] CRUD/list helpers work for valid project/ID inputs.
- [x] Missing project/ID behavior remains bounded (`No novel project found: <id>` / `No style sample found: <id>`).
- [x] Blank labels and blank sample text are rejected.
- [x] `get_style_sample()` runs migration before selecting, matching the store accessor pattern.

## 2. Behavior and command contract

Accepted command surface:

- `/rp style sample add <project-id> <label> <sample...>`
- `/rp style sample list [project-id]`
- `/rp style sample inspect <style-sample-id>`
- `/rp style sample update <style-sample-id> <sample...>`
- `/rp style sample delete <style-sample-id>`

Behavior checks:

- [x] `add` requires an explicit project ID, compact one-token label, and freeform sample text.
- [x] `list` supports explicit project ID and active-project fallback only.
- [x] `inspect`, `update`, and `delete` operate by style-sample ID.
- [x] `/rp help` and README Core command guards expose the command literals.
- [x] `/rp project style ...` remains the separate Phase 124 prompt-injected project style guide; style samples do not feed or replace it.

## 3. Markdown export contract

Accepted export behavior:

- [x] Project Markdown export emits optional `## Style Samples` only when style-sample rows exist.
- [x] When `## Style Guide` exists, `## Style Samples` appears immediately after it.
- [x] When no style guide exists, `## Style Samples` appears after optional Project Brief / Outline placement.
- [x] `## Style Samples` appears before `## Locations`, `## Organizations`, `## Plot Threads`, `## Characters`, `## Relationships`, and `## Chapters`.
- [x] The section is omitted for projects without style-sample rows.

## 4. No-leak and reverse-scope contract

Style samples are accepted as local/offline metadata only. They are visible
through command output and local Markdown export, not through automatic prompt or
model behavior.

Controller verification confirms style-sample text remains excluded from:

- prompt assembly and session prompt module selection;
- `/rp debug prompt` and `/rp debug context` output;
- context-budget reporting payloads;
- retrieval/vectorization and automatic memory extraction/update cycles;
- provider/model routing, content mode decisions, credentials, and generation;
- automation/summarization, media/TTS/image, and ST importer/exporter paths;
- protected core files: `run_agent.py`, `cli.py`, and `gateway/run.py`.

The S2 diff is docs/status-only: no README, source, test, core, or build-artifact
changes were present in the controller reverse-scope diff guard.

## 5. Architecture and root-design writeback

Writeback completed in:

- `design/codestable/architecture/ARCHITECTURE.md`
  - Phase 135 capability summary added.
  - Command surface and DB-schema headings updated to current through Phase 135.
  - `/rp style sample ...` command literals added.
  - `novel_style_samples` schema/index added.
  - Prompt/debug/context-budget/provider/routing/generation/retrieval/vectorization/automation exclusion language now includes style-sample metadata.
  - Phase 135 known-constraint boundary added.
- `design/HERMES_TAVERN_DESIGN.md`
  - Stale wording that listed style samples as deferred was removed from current sections.
  - Style samples are now listed as current project/novel sub-objects.
  - Schema, command surface, memory/update-cycle exclusion, Novel Engine behavior, and Markdown export placement were updated.
  - Current Markdown export range was updated from Phase 121–134 to Phase 121–135.
  - Deferred relationship graph/rename/automatic extraction, default bindings, canon/content-mode metadata, archive import/export, retrieval/vectorization/automation integration, provider routing/generation coupling, cloud/collab/accounts, and safety boundaries remain explicit.

## 6. Requirement and roadmap writeback

- Requirement: no `requirement` frontmatter target was declared in the feature design; no `cs-req` writeback is required.
- Roadmap: no `roadmap` / `roadmap_item` frontmatter target was declared; no roadmap item update is required.

## 7. Controller verification evidence

Controller-run commands after Codex architect/executor docs/writeback:

- [x] `codex --profile architect exec --json --color never --disable image_generation --sandbox read-only --cd /Users/steven/Projects/hermes-tavern <Phase 135 S2 artifact prompt>` → exit 0; JSONL `/tmp/hermes-tavern-architect-phase135-s2.jsonl`; `RESULT: S2_ARTIFACT`; no failed command-execution records.
- [x] `codex --profile executor exec --json --color never --disable image_generation --sandbox read-only --cd /Users/steven/Projects/hermes-tavern <executor smoke prompt>` → exit 0; JSONL `/tmp/hermes-tavern-executor-phase135-s2-smoke.jsonl`; `EXECUTOR_SMOKE_OK`.
- [x] `codex --profile executor exec --json --color never --disable image_generation --sandbox workspace-write --cd /Users/steven/Projects/hermes-tavern <Phase 135 S2 docs/status prompt>` → exit 0; JSONL `/tmp/hermes-tavern-executor-phase135-s2.jsonl`; executor drafted S2 docs/writeback. JSONL had recoverable failed probes/patch attempts, but final summary reported only allowed docs/status changes.
- [x] `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` → `267 passed in 8.72s` after final S2 docs/status patch.
- [x] `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` → `958 passed in 44.70s` after final S2 docs/status patch.
- [x] `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` → `958 passed in 48.37s` after final S2 docs/status patch.
- [x] `python design/codestable/tools/validate-yaml.py --file <design.md> --require doc_type --require status --require feature` → passed after final S2 status update.
- [x] `python design/codestable/tools/validate-yaml.py --file <acceptance.md> --require doc_type --require status --require feature` → passed after final S2 status update.
- [x] `python design/codestable/tools/validate-yaml.py --yaml-only --file <checklist.yaml>` → passed after final S2 status update.
- [x] `git diff --name-only -- README.md src tests run_agent.py cli.py gateway/run.py build/lib` → empty.
- [x] stale current-doc wording scan for style samples deferred/current-through-Phase-134 → empty for `ARCHITECTURE.md` and root design after controller patch.
- [x] deferred-boundary preservation scan → intended remaining deferred boundaries still documented.
- [x] `git diff --check` → passed.

## 8. Attention candidates

No new `attention.md` candidate. This phase reused existing startup rules: keep
Tavern plugin work inside plugin files/docs, never touch protected Hermes core
files, and keep local metadata out of prompt/provider/generation paths.

## 9. Residual deferred work

Still intentionally deferred/out of scope:

- style-sample prompt injection, style imitation/scoring/selection/blending/enforcement, rewrite/generation workflows, and automatic style extraction;
- relationship graph/rename/automatic extraction;
- default card/preset/lorebook/style bindings;
- canon-policy/content-mode metadata behavior;
- project archive ZIP import/export and Markdown import;
- retrieval/vectorization/automation integration;
- provider routing/generation coupling;
- cloud collaboration, backend accounts, or credential persistence;
- minors/underage fields, tests, commands, safety-classification behavior, or provider-safety-bypass behavior.
