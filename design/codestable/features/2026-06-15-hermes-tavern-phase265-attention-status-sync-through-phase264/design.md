---
doc_type: feature-design
status: approved
feature: "2026-06-15-hermes-tavern-phase265-attention-status-sync-through-phase264"
date: "2026-06-15"
created: "2026-06-15"
updated: "2026-06-15"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 264, without changing runtime/source behavior,
  plugin architecture, provider safety behavior, adult-fiction/RP compatibility,
  or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 265: CodeStable Attention Status Sync Through Phase 264

## Read-Only Architect Precheck

Controller and Codex architect observed:

- Branch/head before materialization: `main` at `cced5ff`, with a clean worktree.
- Latest accepted feature: `design/codestable/features/2026-06-15-hermes-tavern-phase264-attention-status-sync-through-phase263/`.
- Phase 264 design is `status: approved`, checklist top-level is `status: accepted`, S1/S2 are completed, and `phase264-acceptance.md` is `status: accepted`.
- `design/codestable/attention.md` currently reports accepted phases through Phase 263.
- `tests/test_hermes_tavern_codestable_status.py` currently guards Phase 168 through Phase 263 labels, stale terminal `1-262` markers, final suffix through Phase 263, and `range(168, 264)`.
- No Phase 265 feature directory existed before this controller materialization.
- Codex architect selected this slice in `/tmp/hermes-tavern-architect-phase265-status-sync.jsonl`.
- This phase is docs/test/status-only and does not require service lifecycle commands.

## Gap

Phase 264 is accepted, but the mandatory CodeStable startup status and focused static regression still stop at Phase 263.

## Scope

Create exactly one bounded CodeStable status-sync phase:

- Feature directory: `design/codestable/features/2026-06-15-hermes-tavern-phase265-attention-status-sync-through-phase264/`

S1 is the bounded implementation slice and may change exactly two existing files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 is controller closeout after verification and may change only these new Phase 265 feature artifacts:

- `design/codestable/features/2026-06-15-hermes-tavern-phase265-attention-status-sync-through-phase264/design.md`
- `design/codestable/features/2026-06-15-hermes-tavern-phase265-attention-status-sync-through-phase264/checklist.yaml`
- `design/codestable/features/2026-06-15-hermes-tavern-phase265-attention-status-sync-through-phase264/acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-263 accepted` to `All phases 1-264 accepted`, preserve the status date `2026-06-15`, preserve all existing labels from Phase 168 through Phase 263 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 264 attention status sync through Phase 263`

The attention status bullet must remain exactly one bullet. Do not add Phase 265 to the attention status.

The focused static regression must advance together:

- `expected_status_prefix`: `Current status (2026-06-15): All phases 1-264 accepted`
- `stale_status_prefix`: `Current status (2026-06-15): All phases 1-263 accepted`
- stale standalone terminal markers: `1-263` and `1–263`
- valid internal range remains: `Phase 121-167`
- append label exactly: `Phase 264 attention status sync through Phase 263`
- final suffix exactly: `Phase 262 attention status sync through Phase 261, Phase 263 attention status sync through Phase 262, and Phase 264 attention status sync through Phase 263.`
- `REQUIRED_PHASE_LABELS` must explicitly include Phase 168 through Phase 264, preserving the non-uniform Phase 168-173 labels from the current test and appending the new Phase 264 label.
- required aggregate phase coverage: `range(168, 265)`
- stale aggregate range to reject in test source: `range(168, 264)`, avoiding direct literal false positives where necessary
- exactly one `CURRENT_STATUS_PREFIX` assignment
- focused test remains static and explicit: no `glob`, `rglob`, `iterdir`, `os.walk`, or generated filesystem discovery

## Main Flow

Phase 264 accepted -> S1 advances the attention status to 1-264 -> S1 advances the focused static regression -> controller verifies -> S2 records Phase 265 acceptance closeout.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 264 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 264 with the 2026-06-15 tick date.
- The focused regression explicitly guards Phase 168 through Phase 264, stale terminal 1-263 rejection, valid `Phase 121-167` preservation, final suffix through Phase 264, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 265)`.
- Phase 265 artifacts are the only closeout artifacts.

## Orchestration Layer

S1 edits the two allowed S1 files and must not touch runtime/source/plugin behavior or protected project surfaces. The controller is responsible for inspecting the diff and rerunning verification.

S2 records acceptance evidence in `acceptance.md` and finalizes `checklist.yaml` only after validators, py_compile, the focused status pytest, static marker guards, changed-path guards, full pytest if feasible, and `git diff --check` pass.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, aggregate range assertion, stale aggregate range rejection, and no-discovery guard.
- New Phase 265 feature directory: design/checklist/acceptance closeout metadata.

## Structure Health

No micro-refactor is needed. `design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 265 directory follows the established recurring status-sync artifact pattern, except the acceptance report path is `acceptance.md` because this tick's allowed-file contract names that path. No source split, directory reorganization, architecture writeback, roadmap writeback, requirement writeback, root-design writeback, or compound decision is needed.

## Non-Goals And Boundaries

This phase does not change runtime behavior, source behavior, plugin behavior, provider/model routing, prompt/generation behavior, import/export behavior, schema behavior, README text, root design, architecture docs, roadmap docs, requirement docs, compound docs, build outputs, content mode, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, adult-fiction/RP compatibility, or safety-bypass behavior.

Do not run service lifecycle commands. Do not repair unrelated checklist residue in this slice.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-15-hermes-tavern-phase265-attention-status-sync-through-phase264 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- Static marker guard for one current-status line, terminal 1-264, Phase 168-264 labels, stale 1-263 rejection, valid Phase 121-167 preservation, final suffix through Phase 264, exactly one `CURRENT_STATUS_PREFIX` assignment, `range(168, 265)`, stale range rejection, and no generated discovery.
- Changed-path guard for exactly the two S1 files plus the new Phase 265 design/checklist/acceptance artifacts.
- Protected-path guard for changes outside the allowed files and protected runtime/source/plugin/provider/prompt/import/export/schema/root-design/architecture/README/roadmap/requirements/compound/build surfaces.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` if feasible.
- `git diff --check`.

## Acceptance Contract

Phase 265 is acceptable when the single current-status bullet reports all phases 1-264 accepted with date 2026-06-15, preserves prior labels through Phase 263, appends exactly `Phase 264 attention status sync through Phase 263`, ends with the required final suffix through Phase 264, rejects stale terminal `1-263` and `1–263` markers while preserving valid `Phase 121-167`, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files, protected runtime/source/plugin surfaces stay unchanged, Phase 264 and older accepted feature artifacts remain untouched, and final acceptance/checklist closeout is grounded in controller-run verification.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The stale status prefix intentionally uses the same 2026-06-15 date as the expected prefix; only the terminal accepted range differs.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 263 to Phase 264 without rewriting older accepted labels.
- Avoid duplicate `CURRENT_STATUS_PREFIX` assignments.
- Avoid embedding the stale aggregate range as a direct literal in self-inspecting test source.
- Do not add Phase 265 to the attention current-status line; Phase 265 is the sync artifact that records the move through accepted Phase 264.
- Do not let this status-sync slice drift into runtime, source, plugin, provider, prompt, import/export, schema, root-design, architecture, README, roadmap, requirements, compound, build, provider safety, minors/underage handling, adult-fiction/RP compatibility, or SillyTavern/Hermes plugin compatibility work.
