---
doc_type: feature-design
status: approved
feature: "2026-06-15-hermes-tavern-phase258-attention-status-sync-through-phase257"
date: "2026-06-15"
created: "2026-06-15"
updated: "2026-06-15"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 257, without changing runtime/source behavior,
  plugin architecture, provider safety behavior, adult-fiction/RP compatibility,
  or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 258: CodeStable Attention Status Sync Through Phase 257

## Read-Only Precheck

Controller-supplied context:

- Branch/head at precheck: `main` at `9732a3d`.
- Latest accepted feature: `design/codestable/features/2026-06-15-hermes-tavern-phase257-attention-status-sync-through-phase256/`.
- Phase 257 checklist and acceptance are accepted/complete.
- `design/codestable/attention.md` currently reports accepted phases through Phase 256.
- `tests/test_hermes_tavern_codestable_status.py` currently guards Phase 168 through Phase 256, stale terminal `1-255` markers, final suffix through Phase 256, and `range(168, 257)`.
- No Phase 258 feature directory exists.
- This phase is docs/test/status-only and does not require service lifecycle commands.

## Gap

Phase 257 is accepted, but the mandatory CodeStable startup status and focused static regression still stop at Phase 256.

## Scope

Create exactly one bounded CodeStable status-sync phase:

- Feature directory: `design/codestable/features/2026-06-15-hermes-tavern-phase258-attention-status-sync-through-phase257/`

S1 is executor-owned and may edit exactly two files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 is controller-only and may edit exactly these new Phase 258 feature artifacts:

- `design/codestable/features/2026-06-15-hermes-tavern-phase258-attention-status-sync-through-phase257/design.md`
- `design/codestable/features/2026-06-15-hermes-tavern-phase258-attention-status-sync-through-phase257/checklist.yaml`
- `design/codestable/features/2026-06-15-hermes-tavern-phase258-attention-status-sync-through-phase257/phase258-acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-256 accepted` to `All phases 1-257 accepted`, preserve the status date `2026-06-15`, preserve all existing labels from Phase 168 through Phase 256 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 257 attention status sync through Phase 256`

The attention status bullet must remain exactly one bullet.

The focused static regression must advance together:

- `expected_status_prefix`: `Current status (2026-06-15): All phases 1-257 accepted`
- `stale_status_prefix`: `Current status (2026-06-15): All phases 1-256 accepted`
- stale standalone terminal markers: `1-256` and `1–256`
- valid internal range remains: `Phase 121-167`
- append label exactly: `Phase 257 attention status sync through Phase 256`
- final suffix exactly: `Phase 255 attention status sync through Phase 254, Phase 256 attention status sync through Phase 255, and Phase 257 attention status sync through Phase 256.`
- `REQUIRED_PHASE_LABELS` must explicitly include Phase 168 through Phase 257
- required aggregate phase coverage: `range(168, 258)`
- stale aggregate range to reject in test source: `range(168, 257)`, avoiding direct literal false positives where necessary
- exactly one `CURRENT_STATUS_PREFIX` assignment
- focused test remains static and explicit: no `glob`, `rglob`, `iterdir`, `os.walk`, or generated filesystem discovery

## Main Flow

Phase 257 accepted -> S1 advances the attention status to 1-257 -> S1 advances the focused static regression -> controller verifies -> S2 records Phase 258 acceptance closeout.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 257 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 257 with the 2026-06-15 tick date.
- The focused regression explicitly guards Phase 168 through Phase 257, stale terminal 1-256 rejection, valid `Phase 121-167` preservation, final suffix through Phase 257, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 258)`.
- Phase 258 artifacts are the only controller closeout artifacts.

## Orchestration Layer

S1 is the only executor implementation slice. It edits the two allowed S1 files and must not create acceptance output, edit feature artifacts, or mark final accepted statuses.

S2 is controller-only closeout after validators, py_compile, the focused status pytest, full pytest when feasible, static marker guard, changed-path guard, protected-path guard, overlap guard, `git diff --check`, and `git diff --cached --check` pass. S2 records acceptance evidence in `phase258-acceptance.md` and may update only the new Phase 258 design/checklist/acceptance artifacts.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, aggregate range assertion, stale aggregate range rejection, and no-discovery guard.
- New Phase 258 feature directory: design/checklist/acceptance closeout metadata.

## Structure Health

No micro-refactor is needed.

`design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 258 directory follows the established recurring status-sync artifact pattern. No source split, directory reorganization, architecture writeback, roadmap writeback, requirement writeback, root-design writeback, or compound decision is needed.

## Non-Goals And Prohibited Paths

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, credentials, content mode, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, adult-fiction/RP compatibility, or safety-bypass behavior.

Do not run service lifecycle commands.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, `design/codestable/compound/**`, any Phase 257 or older accepted feature artifact, or any feature artifact outside the new Phase 258 directory.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-15-hermes-tavern-phase258-attention-status-sync-through-phase257/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-15-hermes-tavern-phase258-attention-status-sync-through-phase257/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-15-hermes-tavern-phase258-attention-status-sync-through-phase257/phase258-acceptance.md --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static marker guard for one current-status line, terminal 1-257, Phase 168-257 labels, stale 1-256 rejection, valid Phase 121-167 preservation, final suffix through Phase 257, exactly one CURRENT_STATUS_PREFIX assignment, range(168, 258), stale range rejection, and no generated discovery.
- S1 changed-path guard for exactly `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`.
- Final changed-path guard for the two S1 files plus the three new Phase 258 feature artifacts.
- Protected-path guard for runtime/source/plugin/provider/prompt/import/export/schema/root-design/architecture/README/roadmap/requirements/compound/build/Hermes-core paths and Phase 257 or older accepted feature artifacts.
- Allowed/prohibited overlap guard.
- `git diff --check`
- `git diff --cached --check`

## Acceptance Contract

Phase 258 is acceptable when the single current-status bullet reports all phases 1-257 accepted with date 2026-06-15, preserves prior labels through Phase 256, appends exactly `Phase 257 attention status sync through Phase 256`, ends with the required final suffix through Phase 257, rejects stale terminal `1-256` and `1–256` markers while preserving valid `Phase 121-167`, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files across S1 and S2, allowed/prohibited overlap is empty, Phase 257 and older accepted feature artifacts remain untouched except the new Phase 258 feature directory, and S2 acceptance closeout is performed by the controller only.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The stale status prefix intentionally uses the same 2026-06-15 date as the expected prefix; only the terminal accepted range differs.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 256 to Phase 257 without rewriting older accepted labels.
- Avoid duplicate `CURRENT_STATUS_PREFIX` assignments.
- Avoid embedding the stale aggregate range as a direct literal in self-inspecting test source.
- Do not let this status-sync slice drift into runtime, source, plugin, provider, prompt, import/export, schema, root-design, architecture, README, roadmap, requirements, compound, build, Hermes core, provider safety, minors/underage handling, adult-fiction/RP compatibility, or SillyTavern/Hermes plugin compatibility work.
