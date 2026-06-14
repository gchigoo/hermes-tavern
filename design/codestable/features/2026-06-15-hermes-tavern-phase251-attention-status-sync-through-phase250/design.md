---
doc_type: feature-design
status: approved
feature: "2026-06-15-hermes-tavern-phase251-attention-status-sync-through-phase250"
date: "2026-06-15"
created: "2026-06-15"
updated: "2026-06-15"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 250, without changing runtime/source behavior,
  protected product documentation, plugin architecture, or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 251: CodeStable Attention Status Sync Through Phase 250

## Read-Only Precheck

Inspected as read-only input:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/phase250-acceptance.md`

Observed readiness:

- Phase 250 acceptance has `status: accepted`.
- Phase 250 checklist has `status: accepted`, `workflow_status: completed`, and `implementation_ready: true`.
- Phase 250 design is approved and implementation-ready.
- `design/codestable/attention.md` currently reports `Current status (2026-06-14): All phases 1-249 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards terminal range 1-249, stale 1-248 markers, Phase 168 through Phase 249 labels, final suffix through Phase 249, and `range(168, 250)`.
- Controller precheck reports git clean on `main` at `924d247`.
- Local tick date is 2026-06-15 CST.

## Gap

`design/codestable/attention.md` is the mandatory CodeStable startup read. Phase 250 is accepted, but the startup status and focused static regression still stop at Phase 249.

This is a docs/test/status-only maintenance slice. It is not runtime, source, plugin, provider, prompt, import/export, schema, root-design, architecture, README, roadmap, requirements, compound, build, or Hermes-core work.

## Scope

Create exactly one bounded CodeStable status-sync phase:

- Feature directory: `design/codestable/features/2026-06-15-hermes-tavern-phase251-attention-status-sync-through-phase250/`

S1 is executor-owned and may edit exactly two files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 is controller-only and may edit exactly these new Phase 251 feature artifacts:

- `design/codestable/features/2026-06-15-hermes-tavern-phase251-attention-status-sync-through-phase250/design.md`
- `design/codestable/features/2026-06-15-hermes-tavern-phase251-attention-status-sync-through-phase250/checklist.yaml`
- `design/codestable/features/2026-06-15-hermes-tavern-phase251-attention-status-sync-through-phase250/phase251-acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-249 accepted` to `All phases 1-250 accepted`, update the status date to `2026-06-15`, preserve all existing labels from Phase 168 through Phase 249 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 250 attention status sync through Phase 249`

The attention status bullet must remain exactly one bullet.

The focused static regression must advance together:

- `expected_status_prefix`: `Current status (2026-06-15): All phases 1-250 accepted`
- `stale_status_prefix`: `Current status (2026-06-14): All phases 1-249 accepted`
- stale standalone terminal markers: `1-249` and `1–249`
- valid internal range remains: `Phase 121-167`
- append label exactly: `Phase 250 attention status sync through Phase 249`
- final suffix exactly: `Phase 248 attention status sync through Phase 247, Phase 249 attention status sync through Phase 248, and Phase 250 attention status sync through Phase 249.`
- phase range assertion: `range(168, 251)`
- stale phase range assertion: `range(168, 250)`
- exactly one `CURRENT_STATUS_PREFIX` assignment
- focused test remains static and explicit: no `glob`, `rglob`, `iterdir`, `os.walk`, or generated discovery

## Main Flow

Phase 250 accepted -> S1 advances the attention status to 1-250 -> S1 advances the focused static regression -> S2 controller records Phase 251 acceptance closeout.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 250 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 250 with the 2026-06-15 tick date.
- The focused regression explicitly guards Phase 168 through Phase 250, stale terminal 1-249 rejection, valid `Phase 121-167` preservation, final suffix through Phase 250, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 251)`.
- Phase 251 artifacts are the only controller closeout artifacts.

## Orchestration Layer

S1 is the only executor implementation slice. It edits the two allowed S1 files and must not create acceptance output, edit feature artifacts, or mark final accepted statuses.

S2 is controller-only closeout after the controller reruns validators, py_compile, the focused status pytest, full pytest, static marker guard, changed-path guard, protected-path guard, overlap guard, `git diff --check`, and `git diff --cached --check`. S2 records acceptance evidence in `phase251-acceptance.md` and may update only the new Phase 251 design/checklist/acceptance artifacts.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, aggregate range assertion, and no-discovery guard.
- New Phase 251 feature directory: design/checklist/acceptance closeout metadata.

Removing these mount points removes the phase from startup context and its focused regression.

## Structure Health

No micro-refactor is needed.

`design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 251 directory follows the established recurring status-sync artifact pattern. No new directory convention, source-file split, architecture writeback, roadmap writeback, requirement writeback, or compound decision is needed.

## Non-Goals And Prohibited Paths

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling, automatic extraction, credentials, content mode, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, adult-fiction/RP compatibility, or safety-bypass behavior.

Do not run service lifecycle commands.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, `design/codestable/compound/**`, any Phase 250 feature artifact, or any older accepted feature artifact during S1 or S2 except the new Phase 251 feature directory.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-15-hermes-tavern-phase251-attention-status-sync-through-phase250/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-15-hermes-tavern-phase251-attention-status-sync-through-phase250/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-15-hermes-tavern-phase251-attention-status-sync-through-phase250/phase251-acceptance.md --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static marker guard for one current-status line, terminal 1-250, Phase 168-250 labels, stale 1-249 rejection, valid Phase 121-167 preservation, final suffix through Phase 250, exactly one CURRENT_STATUS_PREFIX assignment, range(168, 251), stale range rejection, and no generated discovery.
- S1 changed-path guard for exactly `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`.
- Final changed-path guard for the two S1 files plus the three new Phase 251 feature artifacts.
- Protected-path guard for runtime/source/plugin/provider/prompt/import/export/schema/root-design/architecture/README/roadmap/requirements/compound/build/Hermes-core paths and older accepted feature artifacts.
- Allowed/prohibited overlap guard.
- `git diff --check`
- `git diff --cached --check`

## Acceptance Contract

Phase 251 is acceptable when the single current-status bullet reports all phases 1-250 accepted with date 2026-06-15, preserves prior labels through Phase 249, appends exactly `Phase 250 attention status sync through Phase 249`, ends with the required final suffix through Phase 250, rejects stale terminal `1-249` and `1–249` markers while preserving valid `Phase 121-167`, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files across S1 and S2, allowed/prohibited overlap is empty, Phase 250 and older accepted feature artifacts remain untouched except the new Phase 251 feature directory, and S2 acceptance closeout is performed by the controller only.

## Risks

- The date, stale-negative checks, and aggregate range must advance together.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 249 to Phase 250 without rewriting older accepted labels.
- Avoid duplicate `CURRENT_STATUS_PREFIX` assignments in the focused regression.
- Do not let this status-sync slice drift into runtime, source, plugin, provider, prompt, import/export, schema, root-design, architecture, README, roadmap, requirements, compound, build, Hermes core, provider safety, minors/underage, adult-fiction/RP compatibility, or SillyTavern/Hermes plugin compatibility work.
