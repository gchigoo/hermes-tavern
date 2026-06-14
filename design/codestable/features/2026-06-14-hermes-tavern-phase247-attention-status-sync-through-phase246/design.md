---
doc_type: feature-design
status: approved
feature: "2026-06-14-hermes-tavern-phase247-attention-status-sync-through-phase246"
date: "2026-06-14"
created: "2026-06-14"
updated: "2026-06-14"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 246, without changing runtime/source behavior
  or protected product documentation.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 247: CodeStable Attention Status Sync Through Phase 246

## Read-Only Precheck

Inspected as read-only input:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-14-hermes-tavern-phase246-attention-status-sync-through-phase245/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase246-attention-status-sync-through-phase245/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase246-attention-status-sync-through-phase245/phase246-acceptance.md`
- Phase 247 feature-directory probe
- Git porcelain status probe

Phase 246 is accepted: its acceptance artifact has `status: accepted`, and its checklist has `status: accepted` plus `workflow_status: completed`.

`design/codestable/attention.md` currently reports `Current status (2026-06-14): All phases 1-245 accepted`, ends through `Phase 245 attention status sync through Phase 244`, and does not include `Phase 246 attention status sync through Phase 245`.

`tests/test_hermes_tavern_codestable_status.py` currently guards terminal range 1-245, stale 1-244 markers, Phase 168 through Phase 245 labels, final suffix through Phase 245, and `range(168, 246)`.

No Phase 247 feature directory was found. Git porcelain output is clean. No product or architecture decision is needed. The next bounded slice is therefore Phase 247: attention status sync through accepted Phase 246.

## Gap

`design/codestable/attention.md` is the mandatory CodeStable startup read for this repository. Phase 246 is accepted, but the startup status and focused static regression still stop at Phase 245.

This is CodeStable startup-context metadata drift only. It is not a runtime, source, plugin, provider/model routing, prompt/generation, import/export, schema, root-design, architecture, reference, README, roadmap, requirement, compound, build, Hermes core, adult-fiction/RP compatibility, minors/underage, provider safety, safety-bypass, or SillyTavern compatibility feature gap.

## Scope

Create exactly one docs/test/status-only phase:

- Feature directory: `design/codestable/features/2026-06-14-hermes-tavern-phase247-attention-status-sync-through-phase246/`

S1 executor implementation may edit exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 controller acceptance closeout may edit exactly:

- `design/codestable/features/2026-06-14-hermes-tavern-phase247-attention-status-sync-through-phase246/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase247-attention-status-sync-through-phase246/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase247-attention-status-sync-through-phase246/phase247-acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-245 accepted` to `All phases 1-246 accepted`, preserve all existing labels from Phase 168 through Phase 245 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 246 attention status sync through Phase 245`

The attention status bullet must remain exactly one bullet.

The focused static regression must advance together:

- `CURRENT_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-246 accepted`
- `STALE_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-245 accepted`
- stale standalone markers: `1-245` and `1–245`
- required labels: existing Phase 168 through Phase 245 labels plus `Phase 246 attention status sync through Phase 245`
- after implementation, required labels cover Phase 168 through Phase 246
- `FINAL_STATUS_SUFFIX`: `Phase 244 attention status sync through Phase 243, Phase 245 attention status sync through Phase 244, and Phase 246 attention status sync through Phase 245.`
- aggregate assertion: `range(168, 247)`
- stale aggregate range rejection for `range(168, 246)`
- preserve valid internal `Phase 121-167`
- exactly one `CURRENT_STATUS_PREFIX` assignment
- no generated discovery via `glob`, `rglob`, `iterdir`, or `os.walk`

## Main Flow

Phase 246 accepted -> S1 advances the attention status to 1-246 -> S1 advances the focused static regression -> S2 controller records Phase 247 acceptance closeout.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 246 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 246.
- The focused regression explicitly guards Phase 168 through Phase 246, stale terminal 1-245 rejection, valid `Phase 121-167` preservation, final suffix through Phase 246, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 247)`.
- Phase 247 artifacts are the only controller closeout artifacts.

## Orchestration Layer

S1 is the only executor implementation slice. It edits the two allowed S1 files and must not create acceptance output or mark final accepted statuses.

S2 is controller-only closeout after the controller reruns validators, tests, static guards, changed-path guards, protected-path guards, overlap guards, and whitespace checks. It records acceptance evidence in `phase247-acceptance.md` and may update only the new Phase 247 design/checklist/acceptance artifacts.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, and aggregate range assertion.
- New Phase 247 feature directory: design/checklist/acceptance closeout metadata.

Removing these mount points removes the phase from startup context and its focused regression.

## Structure Health

No micro-refactor is needed.

`design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 247 directory follows the established recurring status-sync artifact pattern.

## Non-Goals And Prohibited Paths

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling, automatic extraction, credentials, content mode, adult-fiction/RP compatibility, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, or safety-bypass behavior.

Do not run service lifecycle commands.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, `design/codestable/compound/**`, `design/codestable/features/2026-06-14-hermes-tavern-phase246-attention-status-sync-through-phase245/**`, or any older accepted feature artifact during S1 or S2 except the new Phase 247 feature directory.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase247-attention-status-sync-through-phase246/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase247-attention-status-sync-through-phase246/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase247-attention-status-sync-through-phase246/phase247-acceptance.md --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static marker guard for one current-status line, terminal 1-246, Phase 168-246 labels, stale 1-245 rejection, valid Phase 121-167 preservation, final suffix through Phase 246, exactly one CURRENT_STATUS_PREFIX assignment, range(168, 247), stale range rejection, and no generated discovery.
- Allowed/prohibited overlap guard.
- Changed-path allowlist guard for the five allowed files.
- Protected-path guard for prohibited paths, Phase 246 artifacts, and older accepted feature artifacts.
- `git diff --check`
- `git diff --cached --check`

## Acceptance

Phase 247 is acceptable when the single current-status bullet reports all phases 1-246 accepted, preserves prior labels through Phase 245, appends exactly `Phase 246 attention status sync through Phase 245`, the final suffix is updated through Phase 246, stale terminal 1-245 markers are rejected while valid `Phase 121-167` remains allowed, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files, allowed/prohibited overlap is empty, Phase 246 and older accepted feature artifacts remain untouched except the new Phase 247 feature directory, and S2 acceptance closeout is performed by the controller only.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 245 to Phase 246 without rewriting older accepted labels.
- Avoid duplicate `CURRENT_STATUS_PREFIX` assignments in the focused regression.
- Do not let this status-sync slice drift into runtime, source, provider, prompt, import/export, schema, root-design, architecture, README, or compatibility work.
