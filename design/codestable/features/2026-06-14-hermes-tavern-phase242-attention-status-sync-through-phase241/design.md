---
doc_type: feature-design
status: approved
feature: "2026-06-14-hermes-tavern-phase242-attention-status-sync-through-phase241"
date: "2026-06-14"
created: "2026-06-14"
updated: "2026-06-14"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 241, without changing runtime/source behavior
  or protected product documentation.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 242: CodeStable Attention Status Sync Through Phase 241

## Read-Only Precheck

Controller prechecks found the git tree clean on `main` at `1af1837`.

Inspected as read-only input:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-14-hermes-tavern-phase241-attention-status-sync-through-phase240/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase241-attention-status-sync-through-phase240/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase241-attention-status-sync-through-phase240/phase241-acceptance.md`
- Phase 242 feature-directory probe

Phase 241 is accepted: its acceptance artifact has `status: accepted`, and its checklist has `status: accepted` plus `workflow_status: completed`.

`design/codestable/attention.md` currently reports `Current status (2026-06-14): All phases 1-240 accepted`, ends through `Phase 240 attention status sync through Phase 239`, and does not include `Phase 241 attention status sync through Phase 240`.

`tests/test_hermes_tavern_codestable_status.py` currently guards terminal range 1-240, stale 1-239 markers, Phase 168 through Phase 240 labels, final suffix through Phase 240, and `range(168, 241)`.

No Phase 242 feature directory was found. The next bounded slice is therefore Phase 242: attention status sync through accepted Phase 241.

## Gap

`design/codestable/attention.md` is the mandatory CodeStable startup read for this repository. Phase 241 is accepted, but the startup status and focused static regression still stop at Phase 240.

This is CodeStable startup-context metadata drift only. It is not a runtime, source, plugin, provider/model routing, prompt/generation, import/export, schema, root-design, architecture, reference, README, roadmap, requirement, compound, build, Hermes core, adult-fiction/RP compatibility, minors/underage, provider safety, safety-bypass, or SillyTavern compatibility feature gap.

## Scope

Create exactly one docs/test/status-only phase:

- Feature directory: `design/codestable/features/2026-06-14-hermes-tavern-phase242-attention-status-sync-through-phase241/`

S1 executor implementation may edit exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 controller acceptance closeout may edit exactly:

- `design/codestable/features/2026-06-14-hermes-tavern-phase242-attention-status-sync-through-phase241/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase242-attention-status-sync-through-phase241/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase242-attention-status-sync-through-phase241/phase242-acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-240 accepted` to `All phases 1-241 accepted`, preserve all existing labels from Phase 168 through Phase 240 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 241 attention status sync through Phase 240`

The attention status bullet must remain exactly one bullet.

The focused static regression must advance together:

- `CURRENT_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-241 accepted`
- `STALE_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-240 accepted`
- stale standalone markers: `1-240` and `1–240`
- required labels: existing Phase 168 through Phase 240 labels plus `Phase 241 attention status sync through Phase 240`
- `FINAL_STATUS_SUFFIX`: `Phase 239 attention status sync through Phase 238, Phase 240 attention status sync through Phase 239, and Phase 241 attention status sync through Phase 240.`
- aggregate assertion: `range(168, 242)`
- stale aggregate range rejection for `range(168, 241)`
- preserve valid internal `Phase 121-167`
- exactly one `CURRENT_STATUS_PREFIX` assignment
- no generated discovery via `glob`, `rglob`, `iterdir`, or `os.walk`

## Main Flow

Phase 241 accepted -> S1 advances the attention status to 1-241 -> S1 advances the focused static regression -> S2 controller records Phase 242 acceptance closeout.

## Noun Layer

Current:

- The attention status is a single `- Current status ...` bullet in `design/codestable/attention.md`.
- The focused regression is `tests/test_hermes_tavern_codestable_status.py`.
- Phase 241 artifacts are accepted and complete.

Change:

- The attention bullet becomes current through Phase 241.
- The focused regression explicitly guards Phase 168 through Phase 241, stale terminal 1-240 rejection, valid `Phase 121-167` preservation, final suffix through Phase 241, exactly one `CURRENT_STATUS_PREFIX` assignment, and `range(168, 242)`.
- Phase 242 artifacts are the only controller closeout artifacts.

## Orchestration Layer

S1 is the only executor implementation slice. It edits the two allowed S1 files and must not create acceptance output or mark final accepted statuses.

S2 is controller-only closeout after the controller reruns validators, tests, static guards, changed-path guards, protected-path guards, overlap guards, and whitespace checks. It records acceptance evidence in `phase242-acceptance.md` and may update only the new Phase 242 design/checklist/acceptance artifacts.

## Mount Points

- `design/codestable/attention.md`: the single startup status bullet.
- `tests/test_hermes_tavern_codestable_status.py`: static constants, required labels, stale-marker checks, final suffix, assignment-count guard, and aggregate range assertion.
- New Phase 242 feature directory: design/checklist/acceptance closeout metadata.

Removing these mount points removes the phase from startup context and its focused regression.

## Structure Health

No micro-refactor is needed.

`design/codestable/attention.md` already owns CodeStable startup context. `tests/test_hermes_tavern_codestable_status.py` already owns the focused static status guard. The new Phase 242 directory follows the established recurring status-sync artifact pattern.

## Non-Goals

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling, automatic extraction, credentials, content mode, adult-fiction/RP compatibility, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, or safety-bypass behavior.

Do not run service lifecycle commands.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, `design/codestable/compound/**`, `design/codestable/features/2026-06-14-hermes-tavern-phase241-attention-status-sync-through-phase240/**`, or any older accepted feature artifact during S1 or S2 except the new Phase 242 feature directory.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase242-attention-status-sync-through-phase241/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase242-attention-status-sync-through-phase241/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase242-attention-status-sync-through-phase241/phase242-acceptance.md --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static marker guard for one current-status line, terminal 1-241, Phase 168-241 labels, stale 1-240 rejection, valid Phase 121-167 preservation, final suffix through Phase 241, exactly one CURRENT_STATUS_PREFIX assignment, range(168, 242), stale range rejection, and no generated discovery.
- Allowed/prohibited overlap guard.
- Changed-path allowlist guard for the five allowed files.
- Protected-path guard for prohibited paths, Phase 241 artifacts, and older accepted feature artifacts.
- `git diff --check`
- `git diff --cached --check`

## Acceptance

Phase 242 is acceptable when the single current-status bullet reports all phases 1-241 accepted, preserves prior labels through Phase 240, appends exactly `Phase 241 attention status sync through Phase 240`, the final suffix is updated through Phase 241, stale terminal 1-240 markers are rejected while valid `Phase 121-167` remains allowed, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files, allowed/prohibited overlap is empty, Phase 241 and older accepted feature artifacts remain untouched except the new Phase 242 feature directory, and S2 acceptance closeout is performed by the controller only.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The current status line is long; keep it as one bullet.
- The final-list punctuation must move the `and` from Phase 240 to Phase 241 without rewriting older accepted labels.
- Avoid the recurring duplicate `CURRENT_STATUS_PREFIX` pitfall in the focused regression.
