---
doc_type: feature-design
status: approved
feature: "2026-06-14-hermes-tavern-phase240-attention-status-sync-through-phase239"
date: "2026-06-14"
created: "2026-06-14"
updated: "2026-06-14"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 239, without changing runtime/source behavior
  or protected product documentation.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 240: CodeStable Attention Status Sync Through Phase 239

## Read-Only Precheck

Controller prechecks found the git tree clean on `main` at `296c6ea`.

Inspected or received as read-only controller input:

- `design/codestable/attention.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase239-attention-status-sync-through-phase238/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase239-attention-status-sync-through-phase238/phase239-acceptance.md`
- `tests/test_hermes_tavern_codestable_status.py`
- Phase 240 feature-directory probe

Phase 239 is accepted: its acceptance artifact has `status: accepted`, and its checklist has `status: accepted` plus `workflow_status: completed`.

`design/codestable/attention.md` currently reports `Current status (2026-06-14): All phases 1-238 accepted`, ends through `Phase 238 attention status sync through Phase 237`, and does not include `Phase 239 attention status sync through Phase 238`.

`tests/test_hermes_tavern_codestable_status.py` currently guards terminal range 1-238, stale 1-237 markers, Phase 168 through Phase 238 labels, final suffix through Phase 238, and `range(168, 239)`.

No Phase 240 feature directory was found. The next bounded slice is therefore Phase 240: attention status sync through accepted Phase 239.

## Gap

`design/codestable/attention.md` is the mandatory CodeStable startup read for this repository. Phase 239 is accepted, but the startup status and focused static regression still stop at Phase 238.

This is CodeStable startup-context metadata drift only. It is not a runtime, source, plugin, provider/model routing, prompt/generation, import/export, schema, root-design, architecture, reference, README, roadmap, requirement, compound, build, Hermes core, adult-fiction/RP compatibility, minors/underage, provider safety, safety-bypass, or SillyTavern compatibility feature gap.

## Scope

Create exactly one docs/test/status-only phase:

- Feature directory: `design/codestable/features/2026-06-14-hermes-tavern-phase240-attention-status-sync-through-phase239/`

S1 executor implementation may edit exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 controller acceptance closeout may edit exactly:

- `design/codestable/features/2026-06-14-hermes-tavern-phase240-attention-status-sync-through-phase239/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase240-attention-status-sync-through-phase239/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase240-attention-status-sync-through-phase239/phase240-acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-238 accepted` to `All phases 1-239 accepted`, preserve all existing labels from Phase 168 through Phase 238 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 239 attention status sync through Phase 238`

The attention status bullet must remain exactly one bullet.

The focused static regression must advance together:

- `CURRENT_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-239 accepted`
- `STALE_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-238 accepted`
- stale standalone markers: `1-238` and `1–238`
- required labels: existing Phase 168 through Phase 238 labels plus `Phase 239 attention status sync through Phase 238`
- `FINAL_STATUS_SUFFIX`: `Phase 237 attention status sync through Phase 236, Phase 238 attention status sync through Phase 237, and Phase 239 attention status sync through Phase 238.`
- aggregate assertion: `range(168, 240)`
- stale aggregate range rejection for `range(168, 239)`
- exactly one `CURRENT_STATUS_PREFIX` assignment
- no generated discovery via `glob`, `rglob`, `iterdir`, or `os.walk`

## Main Flow

Phase 239 accepted -> S1 advances the attention status to 1-239 -> S1 advances the focused static regression -> S2 controller records Phase 240 acceptance closeout.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 239 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 239.
- The focused regression explicitly guards Phase 168 through Phase 239, stale terminal 1-238 rejection, valid `Phase 121-167` preservation, final suffix through Phase 239, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 240)`.
- Phase 240 artifacts are the only controller closeout artifacts.

## Orchestration Layer

S1 is the only executor implementation slice. It edits the two allowed S1 files and must not create acceptance output or mark final accepted statuses.

S2 is controller-only closeout. It records acceptance evidence in `phase240-acceptance.md` and may update only the new Phase 240 design/checklist/acceptance artifacts.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, and aggregate range assertion.
- New Phase 240 feature directory: design/checklist/acceptance closeout metadata.

Removing these mount points removes the phase from startup context and its focused regression.

## Structure Health

No micro-refactor is needed.

`design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 240 directory follows the established recurring status-sync artifact pattern.

## Non-Goals

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling, automatic extraction, credentials, content mode, adult-fiction/RP compatibility, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, or safety-bypass behavior.

Do not run service lifecycle commands.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, `design/codestable/compound/**`, `design/codestable/features/2026-06-14-hermes-tavern-phase239-attention-status-sync-through-phase238/**`, or any older accepted feature artifact during this phase.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase240-attention-status-sync-through-phase239/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase240-attention-status-sync-through-phase239/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase240-attention-status-sync-through-phase239/phase240-acceptance.md --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static marker guard for one current-status line, terminal 1-239, Phase 168-239 labels, stale 1-238 rejection, valid Phase 121-167 preservation, final suffix through Phase 239, exactly one CURRENT_STATUS_PREFIX assignment, range(168, 240), stale range rejection, and no generated discovery.
- Allowed/prohibited overlap guard.
- Changed-path allowlist guard for the five allowed files.
- Protected-path guard for prohibited paths, Phase 239 artifacts, and older accepted feature artifacts.
- `git diff --check`
- `git diff --cached --check`

## Acceptance

Phase 240 is acceptable when the single current-status bullet reports all phases 1-239 accepted, preserves prior labels through Phase 238, appends exactly `Phase 239 attention status sync through Phase 238`, the final suffix is updated through Phase 239, stale terminal 1-238 markers are rejected while valid `Phase 121-167` remains allowed, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files, allowed/prohibited overlap is empty, Phase 239 and older accepted feature artifacts remain untouched, and S2 acceptance closeout is performed by the controller only.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 238 to Phase 239 without rewriting older accepted labels.
- Avoid the recurring duplicate `CURRENT_STATUS_PREFIX` pitfall in the focused regression.
