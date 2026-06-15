---
doc_type: feature-design
status: approved
feature: "2026-06-15-hermes-tavern-phase264-attention-status-sync-through-phase263"
date: "2026-06-15"
created: "2026-06-15"
updated: "2026-06-15"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 263, without changing runtime/source behavior,
  plugin architecture, provider safety behavior, adult-fiction/RP compatibility,
  or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 264: CodeStable Attention Status Sync Through Phase 263

## Read-Only Architect Precheck

Controller and Codex architect observed:

- Branch/head before materialization: `main` at `5d50aa9`, with a clean worktree.
- Latest accepted feature: `design/codestable/features/2026-06-15-hermes-tavern-phase263-attention-status-sync-through-phase262/`.
- Phase 263 design is `status: approved`, checklist top-level is `status: accepted`, S1/S2 are completed, and `phase263-acceptance.md` is `status: accepted`.
- `design/codestable/attention.md` currently reports accepted phases through Phase 262.
- `tests/test_hermes_tavern_codestable_status.py` currently guards Phase 168 through Phase 262, stale terminal `1-261` markers, final suffix through Phase 262, and `range(168, 263)`.
- No Phase 264 feature directory existed before this controller materialization.
- Codex architect selected this slice in `/tmp/hermes-tavern-architect-phase264-status-sync.jsonl`.
- This phase is docs/test/status-only and does not require service lifecycle commands.

## Gap

Phase 263 is accepted, but the mandatory CodeStable startup status and focused static regression still stop at Phase 262.

## Scope

Create exactly one bounded CodeStable status-sync phase:

- Feature directory: `design/codestable/features/2026-06-15-hermes-tavern-phase264-attention-status-sync-through-phase263/`

S1 is executor-owned and may change exactly two files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 is parent/controller-only closeout and may change only these new Phase 264 feature artifacts:

- `design/codestable/features/2026-06-15-hermes-tavern-phase264-attention-status-sync-through-phase263/design.md`
- `design/codestable/features/2026-06-15-hermes-tavern-phase264-attention-status-sync-through-phase263/checklist.yaml`
- `design/codestable/features/2026-06-15-hermes-tavern-phase264-attention-status-sync-through-phase263/phase264-acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-262 accepted` to `All phases 1-263 accepted`, preserve the status date `2026-06-15`, preserve all existing labels from Phase 168 through Phase 262 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 263 attention status sync through Phase 262`

The attention status bullet must remain exactly one bullet. Do not add Phase 264 to the attention status.

The focused static regression must advance together:

- `expected_status_prefix`: `Current status (2026-06-15): All phases 1-263 accepted`
- `stale_status_prefix`: `Current status (2026-06-15): All phases 1-262 accepted`
- stale standalone terminal markers: `1-262` and `1–262`
- valid internal range remains: `Phase 121-167`
- append label exactly: `Phase 263 attention status sync through Phase 262`
- final suffix exactly: `Phase 261 attention status sync through Phase 260, Phase 262 attention status sync through Phase 261, and Phase 263 attention status sync through Phase 262.`
- `REQUIRED_PHASE_LABELS` must explicitly include Phase 168 through Phase 263, preserving the non-uniform Phase 168-173 labels from the current test and appending the new Phase 263 label.
- required aggregate phase coverage: `range(168, 264)`
- stale aggregate range to reject in test source: `range(168, 263)`, avoiding direct literal false positives where necessary
- exactly one `CURRENT_STATUS_PREFIX` assignment
- focused test remains static and explicit: no `glob`, `rglob`, `iterdir`, `os.walk`, or generated filesystem discovery

## Main Flow

Phase 263 accepted -> S1 advances the attention status to 1-263 -> S1 advances the focused static regression -> parent/controller verifies -> parent/controller S2 records Phase 264 acceptance closeout later.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 263 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 263 with the 2026-06-15 tick date.
- The focused regression explicitly guards Phase 168 through Phase 263, stale terminal 1-262 rejection, valid `Phase 121-167` preservation, final suffix through Phase 263, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 264)`.
- Phase 264 artifacts are the only closeout artifacts.

## Orchestration Layer

S1 is the only executor implementation slice. It edits the two allowed S1 files and must not create acceptance output, edit Phase 264 artifacts, or mark final accepted statuses.

S2 is parent/controller-only closeout after validators, py_compile, the focused status pytest, full pytest if feasible, static marker guard, changed-path guard, protected-path guard, overlap guard, and `git diff --check` pass. S2 records acceptance evidence in `phase264-acceptance.md` and may update only the new Phase 264 design/checklist/acceptance artifacts.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, aggregate range assertion, stale aggregate range rejection, and no-discovery guard.
- New Phase 264 feature directory: design/checklist/acceptance closeout metadata.

## Structure Health

No micro-refactor is needed.

`design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 264 directory follows the established recurring status-sync artifact pattern. No source split, directory reorganization, architecture writeback, roadmap writeback, requirement writeback, root-design writeback, or compound decision is needed.

## Non-Goals And Boundaries

This phase does not change runtime behavior, source behavior, plugin behavior, provider/model routing, prompt/generation behavior, import/export behavior, schema behavior, README text, root design, architecture docs, roadmap docs, requirement docs, compound docs, build outputs, content mode, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, adult-fiction/RP compatibility, or safety-bypass behavior.

Do not run service lifecycle commands. Do not repair unrelated checklist residue in this slice.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-15-hermes-tavern-phase264-attention-status-sync-through-phase263/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-15-hermes-tavern-phase264-attention-status-sync-through-phase263/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`
- Static marker guard for one current-status line, terminal 1-263, Phase 168-263 labels, stale 1-262 rejection, valid Phase 121-167 preservation, final suffix through Phase 263, exactly one CURRENT_STATUS_PREFIX assignment, range(168, 264), stale range rejection, and no generated discovery.
- S1 changed-path guard for exactly `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`.
- Final changed-path guard for the two S1 files plus the new Phase 264 design/checklist artifacts; acceptance closeout is deferred unless parent performs S2.
- Protected-path guard for changes outside the allowed files and protected runtime/source/plugin/provider/prompt/import/export/schema/root-design/architecture/README/roadmap/requirements/compound/build surfaces.
- Allowed/prohibited overlap guard.
- `git diff --check`

## Acceptance Contract

Phase 264 S1 is acceptable when the single current-status bullet reports all phases 1-263 accepted with date 2026-06-15, preserves prior labels through Phase 262, appends exactly `Phase 263 attention status sync through Phase 262`, ends with the required final suffix through Phase 263, rejects stale terminal `1-262` and `1–262` markers while preserving valid `Phase 121-167`, the focused static regression passes and remains explicit/static, changed paths are limited to the S1 files plus this feature's planned artifacts, allowed/prohibited overlap is empty, Phase 263 and older accepted feature artifacts remain untouched, and final acceptance closeout remains parent/controller-only.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The stale status prefix intentionally uses the same 2026-06-15 date as the expected prefix; only the terminal accepted range differs.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 262 to Phase 263 without rewriting older accepted labels.
- Avoid duplicate `CURRENT_STATUS_PREFIX` assignments.
- Avoid embedding the stale aggregate range as a direct literal in self-inspecting test source.
- Do not let this status-sync slice drift into runtime, source, plugin, provider, prompt, import/export, schema, root-design, architecture, README, roadmap, requirements, compound, build, provider safety, minors/underage handling, adult-fiction/RP compatibility, or SillyTavern/Hermes plugin compatibility work.
