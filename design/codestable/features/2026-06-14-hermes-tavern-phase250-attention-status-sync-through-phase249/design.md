---
doc_type: feature-design
status: approved
feature: "2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249"
date: "2026-06-14"
created: "2026-06-14"
updated: "2026-06-14"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 249, without changing runtime/source behavior
  or protected product documentation.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 250: CodeStable Attention Status Sync Through Phase 249

## Read-Only Precheck

Inspected as read-only input:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-14-hermes-tavern-phase249-attention-status-sync-through-phase248/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase249-attention-status-sync-through-phase248/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase249-attention-status-sync-through-phase248/phase249-acceptance.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase248-attention-status-sync-through-phase247/design.md`

Observed readiness:

- Phase 249 acceptance has `status: accepted`.
- Phase 249 checklist has `status: accepted`, `workflow_status: completed`, and `implementation_ready: true`.
- Phase 249 design is approved and implementation-ready.
- `design/codestable/attention.md` currently reports `Current status (2026-06-14): All phases 1-248 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards terminal range 1-248, stale 1-247 markers, Phase 168 through Phase 248 labels, final suffix through Phase 248, and `range(168, 249)`.
- Git clean state is accepted from the controller precheck context; this read-only tick does not require source edits or service lifecycle commands.

## Gap

`design/codestable/attention.md` is the mandatory CodeStable startup read for this repository. Phase 249 is accepted, but the startup status and focused static regression still stop at Phase 248.

This is a docs/test/status-only maintenance slice. It is not runtime, source, plugin, provider, prompt, import/export, schema, root-design, architecture, README, roadmap, requirements, compound, build, or Hermes-core work.

## Scope

Create exactly one bounded CodeStable status-sync phase:

- Feature directory: `design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/`

S1 executor may edit exactly two files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 is controller-only and may edit exactly these new Phase 250 feature artifacts:

- `design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/phase250-acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-248 accepted` to `All phases 1-249 accepted`, preserve all existing labels from Phase 168 through Phase 248 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 249 attention status sync through Phase 248`

The attention status bullet must remain exactly one bullet.

The focused static regression must advance together:

- `expected_status_prefix`: `Current status (2026-06-14): All phases 1-249 accepted`
- `stale_status_prefix`: `Current status (2026-06-14): All phases 1-248 accepted`
- stale standalone terminal markers: `1-248` and `1–248`
- valid internal range remains: `Phase 121-167`
- append label exactly: `Phase 249 attention status sync through Phase 248`
- final suffix exactly: `Phase 247 attention status sync through Phase 246, Phase 248 attention status sync through Phase 247, and Phase 249 attention status sync through Phase 248.`
- phase range assertion: `range(168, 250)`
- stale phase range assertion: `range(168, 249)`
- exactly one `CURRENT_STATUS_PREFIX` assignment
- focused test remains static and explicit: no `glob`, `rglob`, `iterdir`, `os.walk`, or generated discovery

## Main Flow

Phase 249 accepted -> S1 advances the attention status to 1-249 -> S1 advances the focused static regression -> S2 controller records Phase 250 acceptance closeout.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 249 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 249.
- The focused regression explicitly guards Phase 168 through Phase 249, stale terminal 1-248 rejection, valid `Phase 121-167` preservation, final suffix through Phase 249, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 250)`.
- Phase 250 artifacts are the only controller closeout artifacts.

## Orchestration Layer

S1 is the only executor implementation slice. It edits the two allowed S1 files and must not create acceptance output or mark final accepted statuses.

S2 is controller-only closeout after the controller reruns validators, py_compile, the focused status pytest, full pytest, static marker guard, changed-path guard, protected-path guard, overlap guard, `git diff --check`, and `git diff --cached --check`. It records acceptance evidence in `phase250-acceptance.md` and may update only the new Phase 250 design/checklist/acceptance artifacts.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, aggregate range assertion, and no-discovery guard.
- New Phase 250 feature directory: design/checklist/acceptance closeout metadata.

Removing these mount points removes the phase from startup context and its focused regression.

## Structure Health

No micro-refactor is needed.

`design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 250 directory follows the established recurring status-sync artifact pattern. No new directory convention, source-file split, architecture writeback, or compound decision is needed.

## Non-Goals And Prohibited Paths

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling, automatic extraction, credentials, content mode, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, or safety-bypass behavior.

Do not run service lifecycle commands.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, `design/codestable/compound/**`, any Phase 249 feature artifact, or any older accepted feature artifact during S1 or S2 except the new Phase 250 feature directory.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase250-attention-status-sync-through-phase249/phase250-acceptance.md --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static marker guard for one current-status line, terminal 1-249, Phase 168-249 labels, stale 1-248 rejection, valid Phase 121-167 preservation, final suffix through Phase 249, exactly one CURRENT_STATUS_PREFIX assignment, range(168, 250), stale range rejection, and no generated discovery.
- S1 changed-path guard for exactly `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`.
- Final changed-path guard for the two S1 files plus the three new Phase 250 feature artifacts.
- Protected-path guard for runtime/source/plugin/provider/prompt/import/export/schema/root-design/architecture/README/roadmap/requirements/compound/build/Hermes-core paths and older accepted feature artifacts.
- Allowed/prohibited overlap guard.
- `git diff --check`
- `git diff --cached --check`

## Acceptance Contract

Phase 250 is acceptable when the single current-status bullet reports all phases 1-249 accepted, preserves prior labels through Phase 248, appends exactly `Phase 249 attention status sync through Phase 248`, ends with the required final suffix through Phase 249, rejects stale terminal `1-248` and `1–248` markers while preserving valid `Phase 121-167`, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files across S1 and S2, allowed/prohibited overlap is empty, Phase 249 and older accepted feature artifacts remain untouched except the new Phase 250 feature directory, and S2 acceptance closeout is performed by the controller only.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 248 to Phase 249 without rewriting older accepted labels.
- Avoid duplicate `CURRENT_STATUS_PREFIX` assignments in the focused regression.
- Do not let this status-sync slice drift into runtime, source, plugin, provider, prompt, import/export, schema, root-design, architecture, README, roadmap, requirements, compound, build, Hermes core, provider safety, minors/underage, or compatibility work.
