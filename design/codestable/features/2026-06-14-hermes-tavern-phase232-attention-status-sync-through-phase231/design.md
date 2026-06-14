---
doc_type: feature-design
status: approved
feature: "2026-06-14-hermes-tavern-phase232-attention-status-sync-through-phase231"
date: "2026-06-14"
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 231, without changing runtime/source behavior
  or protected product documentation.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-14"
updated: "2026-06-14"
owner: codestable-cron
implementation_ready: true
---

# Phase 232: CodeStable Attention Status Sync Through Phase 231

## Read-Only Precheck

Required startup/status files were inspected:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-14-hermes-tavern-phase231-attention-status-sync-through-phase230/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase231-attention-status-sync-through-phase230/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase231-attention-status-sync-through-phase230/phase231-acceptance.md`

Phase 231 is accepted: `phase231-acceptance.md` has `status: accepted`, and the Phase 231 checklist has `status: accepted` plus `workflow_status: completed`.

`design/codestable/attention.md` currently reports `Current status (2026-06-14): All phases 1-230 accepted`, includes `Phase 230 attention status sync through Phase 229`, and does not include `Phase 231 attention status sync through Phase 230`.

`tests/test_hermes_tavern_codestable_status.py` currently guards terminal range 1-230, stale 1-229 markers, Phase 168 through Phase 230 labels, final suffix through Phase 230, and `range(168, 231)`.

No Phase 232 feature directory was present during precheck.

## Gap

`design/codestable/attention.md` is the mandatory startup read for CodeStable work in this repository. Phase 231 is accepted in the feature archive, but the startup status and focused static regression still stop at Phase 230. The mandatory startup status and focused regression are therefore one accepted phase behind.

This is CodeStable startup-context metadata drift only. It is not a runtime, source, plugin, provider/model routing, prompt/generation, import/export, schema, root-design, architecture, reference, README, roadmap, requirement, compound, build, Hermes core, adult-fiction/RP compatibility, minors/underage, provider safety, safety-bypass, or SillyTavern compatibility feature gap.

## Scope

Create and close exactly one docs/test/status-only phase:

- Feature directory: `design/codestable/features/2026-06-14-hermes-tavern-phase232-attention-status-sync-through-phase231/`

S1 executor implementation may edit exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 controller acceptance closeout may edit exactly:

- `design/codestable/features/2026-06-14-hermes-tavern-phase232-attention-status-sync-through-phase231/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase232-attention-status-sync-through-phase231/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase232-attention-status-sync-through-phase231/phase232-acceptance.md`

S1 must advance only the terminal current-status range from `All phases 1-230 accepted` to `All phases 1-231 accepted`, preserve all existing labels from Phase 168 through Phase 230 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 231 attention status sync through Phase 230`

The focused static regression must advance together:

- `CURRENT_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-231 accepted`
- `STALE_STATUS_PREFIX`: `Current status (2026-06-14): All phases 1-230 accepted`
- stale standalone markers: `1-230` and `1–230`
- required labels: existing Phase 168 through Phase 230 labels plus `Phase 231 attention status sync through Phase 230`
- `FINAL_STATUS_SUFFIX`: `Phase 229 attention status sync through Phase 228, Phase 230 attention status sync through Phase 229, and Phase 231 attention status sync through Phase 230.`
- aggregate assertion: `range(168, 232)`
- no generated discovery via `glob`, `rglob`, `iterdir`, or `os.walk`

## Non-Goals

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling, automatic extraction, credentials, content mode, adult-fiction/RP compatibility, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, or safety-bypass behavior.

Do not run service lifecycle commands.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `build/lib/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, `design/codestable/compound/**`, `design/codestable/features/2026-06-14-hermes-tavern-phase231-attention-status-sync-through-phase230/**`, or any older accepted feature artifact.

Do not edit Phase 231 artifacts or any older accepted phase artifacts during S1. S2 may edit only the new Phase 232 artifacts listed above.

S1 must not mark final accepted statuses and must not create `phase232-acceptance.md`. S2 is controller-only acceptance closeout.

## Execution Plan

S1 is the only executor implementation slice. It replaces the single attention current-status bullet and updates the focused static regression to guard the Phase 1-231 terminal status, Phase 168-231 explicit labels, stale 1-230 rejection, valid Phase 121-167 preservation, final-list punctuation, and `range(168, 232)` aggregate assertion.

S2 is controller-only closeout. It records acceptance evidence in `phase232-acceptance.md` and finalizes the Phase 232 checklist/design statuses without touching attention, tests, runtime/source/plugin/provider/prompt/generation/import/export/schema files, Hermes core files, protected documentation/build paths, Phase 231 artifacts, or older accepted feature artifacts.

## Structure Health

`design/codestable/attention.md` already owns recurring CodeStable startup context. Replacing one stale status bullet is its existing responsibility.

`tests/test_hermes_tavern_codestable_status.py` already owns the static current-status guard. Updating that existing test avoids a parallel status regression file.

No directory organization, file ownership, naming convention, or micro-refactor change is needed.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase232-attention-status-sync-through-phase231/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase232-attention-status-sync-through-phase231/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase232-attention-status-sync-through-phase231/phase232-acceptance.md --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- static marker guard for exactly one current-status line, terminal `1-231`, explicit Phase 168 through Phase 231 labels, `range(168, 232)`, final punctuation through Phase 231, stale terminal `1-230` / `1–230` rejection, valid `Phase 121-167` preservation, and no generated phase-discovery calls
- allowed/prohibited overlap guard confirms no file appears in both allowed and prohibited sets
- changed-path allowlist guard for the five allowed files
- protected-path guard for prohibited paths
- `git diff --check`
- `git diff --cached --check`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` when feasible

## Acceptance

Phase 232 is acceptable when the single current-status bullet reports all phases 1-231 accepted, preserves prior labels through Phase 230, appends exactly `Phase 231 attention status sync through Phase 230`, the final suffix is updated through Phase 231, stale terminal 1-230 markers are rejected while valid `Phase 121-167` remains allowed, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files, allowed/prohibited overlap is empty, and S2 acceptance closeout is performed by the controller only.

## Risks

- The stale-negative checks and aggregate range must advance together: stale prefixes/markers move from 1-229 to 1-230 while the aggregate assertion moves from `range(168, 231)` to `range(168, 232)`.
- The current status line is long; keep it as one bullet and do not split it into generated summaries or multiple current-status bullets.
- The final-list punctuation must move the `and` from Phase 230 to Phase 231 without rewriting older accepted labels.
