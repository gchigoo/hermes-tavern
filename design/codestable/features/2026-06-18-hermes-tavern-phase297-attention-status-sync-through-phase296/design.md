---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-18-hermes-tavern-phase297-attention-status-sync-through-phase296"
date: "2026-06-18"
created: "2026-06-18"
updated: "2026-06-18"
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 296 only, without changing runtime behavior,
  plugin/provider/gateway internals, root design, architecture, roadmap,
  requirements, compound docs, credentials, or build assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 297: CodeStable Attention Status Sync Through Phase 296

## Current State

Read-only architect verification confirmed that Phase 296 is accepted: the Phase
296 feature design is approved, its checklist is accepted, and its acceptance
report is accepted. The mandatory startup attention line still reports only
`All phases 1-295 accepted`, and the focused static regression still enforces the
Phase 295 status line. No Phase 297 artifact or `All phases 1-296 accepted`
status line exists yet.

## Goal

Advance the recurring status-sync family by exactly one accepted phase: sync
`design/codestable/attention.md` and the focused static regression through
accepted Phase 296 only, and create the Phase 297 CodeStable artifacts for this
bounded docs/test-only slice.

## Non-Goals

- Do not change runtime, source, plugin, provider, gateway, CLI, root design,
  README, architecture, roadmap, requirements, compound docs, build outputs,
  fixtures, assets, schemas, credentials, model/provider routing, or service
  lifecycle behavior.
- Do not modify `run_agent.py`, `cli.py`, or `gateway/run.py`.
- Do not create minors/CSAM functionality, bypass provider safety systems, or
  change adult-fiction/RP boundaries.
- Do not commit, push, stage files, or update `.hermes/project-progress/state.json`.

## Exact S1 Contract

- `design/codestable/attention.md` current status must start with:
  `Current status (2026-06-18): All phases 1-296 accepted`.
- Add exactly one new short label to the same status line:
  `Phase 296 attention status sync through Phase 295`.
- Preserve `Phase 121-167`.
- Preserve all explicit `Phase 168` through `Phase 295` labels exactly.
- Append only `Phase 296 attention status sync through Phase 295`.
- Do not add any `Phase 297` label to `attention.md`.
- Phase 297 syncs only through accepted Phase 296.
- Do not change runtime/product/source/plugin/provider/gateway behavior.

## Focused Status Regression Contract

Update `tests/test_hermes_tavern_codestable_status.py` so it enforces:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-296 accepted"`.
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-295 accepted"`.
- `STALE_PHASE_MARKER = "1-295"` and `STALE_PHASE_MARKER_EN_DASH = "1–295"`.
- `REQUIRED_PHASE_LABELS` preserves every prior explicit short label through
  Phase 295 and includes `Phase 296 attention status sync through Phase 295`.
- `FINAL_STATUS_SUFFIX` is exactly:
  `Phase 294 attention status sync through Phase 293, Phase 295 attention status sync through Phase 294, and Phase 296 attention status sync through Phase 295.`
- The runtime phase range assertion is `range(168, 297)`.
- The source self-check contains `aggregate_range = "range(168, 297)"`.
- Stale aggregate negative guards include split-string construction for stale
  `range(168, 296)` and retain older stale ranges.
- The single `CURRENT_STATUS_PREFIX` assignment check uses anchored regex:
  `re.findall(r"^CURRENT_STATUS_PREFIX\\s*=", test, re.M) == ["CURRENT_STATUS_PREFIX ="]`.
- Discovery-token guards keep `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`
  split inside strings.

## Scope

Allowed files only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-18-hermes-tavern-phase297-attention-status-sync-through-phase296/design.md`
- `design/codestable/features/2026-06-18-hermes-tavern-phase297-attention-status-sync-through-phase296/checklist.yaml`
- `design/codestable/features/2026-06-18-hermes-tavern-phase297-attention-status-sync-through-phase296/acceptance.md`

## Prohibited Files/Actions

No changes to runtime, source, provider, plugin, gateway, root design, README,
architecture, roadmap, requirements, compound docs, build outputs, assets,
schemas, credential files, service lifecycle, provider configuration, prior phase
artifacts, or `.hermes/project-progress/state.json`. Do not commit, push, stage,
or run destructive git commands.

## Validators, Tests, and Guards

Worker-controller verification must run after implementation:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-18-hermes-tavern-phase297-attention-status-sync-through-phase296 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static status guard using anchored regex for `CURRENT_STATUS_PREFIX` assignment
  count and exact prefix/suffix/range/label/stale marker/discovery-token checks.
- Protected-path diff guard over the five allowed files, including untracked
  Phase 297 files.
- `git diff --check`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` if feasible; do
  not disable plugin autoload for the full suite.
- Rerun YAML validation after any checklist/acceptance evidence patch.

## Architect Review Checklist

- Diff touches only the five allowed files.
- `attention.md` has exactly one current-status bullet.
- Prefix is exactly `Current status (2026-06-18): All phases 1-296 accepted`.
- Stale `All phases 1-295 accepted`, `1-295`, and `1–295` terminal markers are rejected.
- `Phase 121-167` remains present.
- Explicit `Phase 168` through `Phase 295` labels are preserved exactly.
- Only new attention label is `Phase 296 attention status sync through Phase 295`.
- No `Phase 297 attention status sync` label appears in `attention.md`.
- Final suffix is exactly the Phase 294/295/296 suffix.
- Focused regression uses `range(168, 297)`.
- Stale aggregate guards are split and include stale `range(168, 296)`.
- Phase 297 artifacts remain non-final until parent-controller verification.
- No runtime, plugin, provider, gateway, root-design, README, architecture,
  roadmap, requirements, compound, build, credential, service lifecycle, commit,
  push, or state update occurred.
