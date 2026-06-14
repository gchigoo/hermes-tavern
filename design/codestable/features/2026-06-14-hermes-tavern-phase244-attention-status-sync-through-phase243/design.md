---
doc_type: feature-design
status: approved
feature: "2026-06-14-hermes-tavern-phase244-attention-status-sync-through-phase243"
date: "2026-06-14"
created: "2026-06-14"
updated: "2026-06-14"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 243, without changing runtime/source behavior
  or protected product documentation.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 244: CodeStable Attention Status Sync Through Phase 243

## Read-Only Precheck

Controller prechecks found the git tree clean on `main` at `40a3027`.

Inspected as read-only input:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-14-hermes-tavern-phase243-attention-status-sync-through-phase242/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase243-attention-status-sync-through-phase242/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase243-attention-status-sync-through-phase242/phase243-acceptance.md`
- Phase 244 feature-directory probe

Phase 243 is accepted: its acceptance artifact has `status: accepted`, and its checklist has `status: accepted` plus `workflow_status: completed`.

`design/codestable/attention.md` currently reports `Current status (2026-06-14): All phases 1-242 accepted`, ends through `Phase 242 attention status sync through Phase 241`, and does not include `Phase 243 attention status sync through Phase 242`.

`tests/test_hermes_tavern_codestable_status.py` currently guards terminal range 1-242, stale 1-241 markers, Phase 168 through Phase 242 labels, final suffix through Phase 242, and `range(168, 243)`.

No Phase 244 feature directory was found. The next bounded slice is therefore Phase 244: attention status sync through accepted Phase 243.

## Gap

`design/codestable/attention.md` is the mandatory CodeStable startup read for this repository. Phase 243 is accepted, but the startup status and focused static regression still stop at Phase 242.

This is CodeStable startup-context metadata drift only. It is not a runtime, source, plugin, provider/model routing, prompt/generation, import/export, schema, root-design, architecture, reference, README, roadmap, requirement, compound, build, Hermes core, adult-fiction/RP compatibility, minors/underage, provider safety, safety-bypass, or SillyTavern compatibility feature gap.

## Scope

Create exactly one docs/test/status-only phase:

- Feature directory: `design/codestable/features/2026-06-14-hermes-tavern-phase244-attention-status-sync-through-phase243/`

S1 executor implementation may edit exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 controller acceptance closeout may edit exactly:

- `design/codestable/features/2026-06-14-hermes-tavern-phase244-attention-status-sync-through-phase243/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase244-attention-status-sync-through-phase243/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase244-attention-status-sync-through-phase243/phase244-acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-242 accepted` to `All phases 1-243 accepted`, preserve all existing labels from Phase 168 through Phase 242 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 243 attention status sync through Phase 242`

The attention status bullet must remain exactly one bullet.

The focused static regression must advance together:

- `CURRENT_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-243 accepted`
- `STALE_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-242 accepted`
- stale standalone markers: `1-242` and `1–242`
- required labels: existing Phase 168 through Phase 242 labels plus `Phase 243 attention status sync through Phase 242`
- after implementation, required labels cover Phase 168 through Phase 243
- `FINAL_STATUS_SUFFIX`: `Phase 241 attention status sync through Phase 240, Phase 242 attention status sync through Phase 241, and Phase 243 attention status sync through Phase 242.`
- aggregate assertion: `range(168, 244)`
- stale aggregate range rejection for `range(168, 243)`
- preserve valid internal `Phase 121-167`
- exactly one `CURRENT_STATUS_PREFIX` assignment
- no generated discovery via `glob`, `rglob`, `iterdir`, or `os.walk`

## Main Flow

Phase 243 accepted -> S1 advances the attention status to 1-243 -> S1 advances the focused static regression -> S2 controller records Phase 244 acceptance closeout.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 243 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 243.
- The focused regression explicitly guards Phase 168 through Phase 243, stale terminal 1-242 rejection, valid `Phase 121-167` preservation, final suffix through Phase 243, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 244)`.
- Phase 244 artifacts are the only controller closeout artifacts.

## Orchestration Layer

S1 is the only executor implementation slice. It edits the two allowed S1 files and must not create acceptance output or mark final accepted statuses.

S2 is controller-only closeout after the controller reruns validators, tests, static guards, changed-path guards, protected-path guards, overlap guards, and whitespace checks. It records acceptance evidence in `phase244-acceptance.md` and may update only the new Phase 244 design/checklist/acceptance artifacts.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, and aggregate range assertion.
- New Phase 244 feature directory: design/checklist/acceptance closeout metadata.

Removing these mount points removes the phase from startup context and its focused regression.

## Structure Health

No micro-refactor is needed.

`design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 244 directory follows the established recurring status-sync artifact pattern.

## Non-Goals

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling, automatic extraction, credentials, content mode, adult-fiction/RP compatibility, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, or safety-bypass behavior.

Do not run service lifecycle commands.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, `design/codestable/compound/**`, `design/codestable/features/2026-06-14-hermes-tavern-phase243-attention-status-sync-through-phase242/**`, or any older accepted feature artifact during S1 or S2 except the new Phase 244 feature directory.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase244-attention-status-sync-through-phase243/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase244-attention-status-sync-through-phase243/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase244-attention-status-sync-through-phase243/phase244-acceptance.md --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static marker guard for one current-status line, terminal 1-243, Phase 168-243 labels, stale 1-242 rejection, valid Phase 121-167 preservation, final suffix through Phase 243, exactly one CURRENT_STATUS_PREFIX assignment, range(168, 244), stale range rejection, and no generated discovery.
- Allowed/prohibited overlap guard.
- Changed-path allowlist guard for the five allowed files.
- Protected-path guard for prohibited paths, Phase 243 artifacts, and older accepted feature artifacts.
- `git diff --check`
- `git diff --cached --check`

## Acceptance

Phase 244 is acceptable when the single current-status bullet reports all phases 1-243 accepted, preserves prior labels through Phase 242, appends exactly `Phase 243 attention status sync through Phase 242`, the final suffix is updated through Phase 243, stale terminal 1-242 markers are rejected while valid `Phase 121-167` remains allowed, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files, allowed/prohibited overlap is empty, Phase 243 and older accepted feature artifacts remain untouched except the new Phase 244 feature directory, and S2 acceptance closeout is performed by the controller only.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 242 to Phase 243 without rewriting older accepted labels.
- Avoid the recurring duplicate `CURRENT_STATUS_PREFIX` pitfall in the focused regression.
