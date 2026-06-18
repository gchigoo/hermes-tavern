---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-18-hermes-tavern-phase302-attention-status-sync-through-phase301"
date: "2026-06-18"
created: "2026-06-18"
updated: "2026-06-18"
owner: company-boost
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 301 only, without changing runtime behavior.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase302]
---

# Phase 302: CodeStable Attention Status Sync Through Phase 301

## Gate

Phase 301 is accepted: `design/codestable/features/2026-06-18-hermes-tavern-phase301-attention-status-sync-through-phase300/acceptance.md` has `status: accepted`.

Current state:
- `design/codestable/attention.md` reports `All phases 1-300 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces Phase 300 current state.
- No Phase 302 status-sync artifact exists.

## Goal

Advance the recurring status-sync lane by exactly one phase: sync `design/codestable/attention.md` and the focused static regression through accepted Phase 301 only.

## Scope

Allowed files:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-18-hermes-tavern-phase302-attention-status-sync-through-phase301/design.md`
- `design/codestable/features/2026-06-18-hermes-tavern-phase302-attention-status-sync-through-phase301/checklist.yaml`

Do not create `acceptance.md` in executor S1 unless the parent explicitly asks for closeout.

## Non-Goals

Do not modify runtime/source/plugin/provider/gateway/CLI files; `run_agent.py`; `cli.py`; `gateway/run.py`; plugin runtime files; credentials; root design; README; architecture; roadmap; requirements; compound docs; build outputs; assets/fixtures/schemas; service lifecycle commands; commits; staging; pushes; or `~/.hermes/project-progress/state.json`.

Preserve Hermes-native plugin architecture and SillyTavern asset compatibility. Preserve adult-fiction/RP compatibility while forbidding minors/CSAM work and provider safety bypasses.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-300 accepted`
- To: `Current status (2026-06-18): All phases 1-301 accepted`

Append exactly:
- `Phase 301 attention status sync through Phase 300`

Preserve:
- `Phase 121-167`
- Every explicit label from Phase 168 through Phase 300

Do not add:
- `Phase 302 attention/status sync` label to `attention.md`

Final suffix must be exactly:

`Phase 299 attention status sync through Phase 298, Phase 300 attention status sync through Phase 299, and Phase 301 attention status sync through Phase 300.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-301 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-300 accepted"`
- `STALE_PHASE_MARKER = "1-300"`
- `STALE_PHASE_MARKER_EN_DASH = "1–300"`
- Append `Phase 301 attention status sync through Phase 300` to `REQUIRED_PHASE_LABELS`, preserving prior labels through Phase 300.
- `FINAL_STATUS_SUFFIX` equals the Phase 299/300/301 suffix above.
- Runtime aggregate range becomes `range(168, 302)`.
- Source self-check aggregate literal becomes `aggregate_range = "range(168, 302)"`.
- Add split-string stale aggregate guard for `range(168, 301)` and retain older stale ranges including 300, 299, 298, and earlier existing guards.
- Preserve anchored `CURRENT_STATUS_PREFIX` assignment-count regex.
- Preserve split discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.

## Static Guard Strategy

Use `git diff --name-only`, `git diff --cached --name-only`, and `git ls-files --others --exclude-standard` to assert the exact changed/untracked path set.

Fail if any runtime/plugin/provider/gateway/root design/architecture/roadmap/requirements/compound/README/build/asset/fixture/schema/progress-state path changes.

Assert exactly one current-status bullet and exactly one anchored `CURRENT_STATUS_PREFIX` assignment.

Assert stale terminal values are absent from `attention.md`; in the test source, allow only intentional `STALE_*` constants/assertions and split-constructed stale aggregate guards.

Assert all Phase 168..301 required labels are present, `Phase 121-167` is preserved, the final suffix is exact, and discovery tokens are not directly embedded.

## Structure Health

No micro-refactor. This is a bounded docs/static-test/status-only slice.

## Verification

Run:
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-18-hermes-tavern-phase302-attention-status-sync-through-phase301 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static protected-path/status guard
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`
- `git diff --check`
