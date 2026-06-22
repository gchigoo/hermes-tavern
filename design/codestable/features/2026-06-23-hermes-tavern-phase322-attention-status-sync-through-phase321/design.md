---
doc_type: feature-design
status: approved
feature: "2026-06-23-hermes-tavern-phase322-attention-status-sync-through-phase321"
date: "2026-06-23"
owner: standard_lane
lane: "standard/personal"
implementation_ready: true
parent_verification_required: true
bounded_phase: "docs/static-test/status-only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase322]
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 321 only, without changing runtime behavior.
---

# Phase 322: CodeStable Attention Status Sync Through Phase 321

## Gate

Phase 321 is accepted at `design/codestable/features/2026-06-23-hermes-tavern-phase321-attention-status-sync-through-phase320/acceptance.md`.

Current state before this slice:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-321 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 321 prefix, required labels through Phase 321, `phase_range = range(168, 322)`, and `aggregate_range = "range(168, 322)"`.
- Recent sibling status-sync artifacts through Phase 321 are accepted.
- No Phase 322 status-sync feature directory exists before parent-controller materialization.

Selected slice: recurring status-only Phase 322 sync through accepted Phase 321.

## Goals

- Advance exactly one recurring status-sync phase: Phase 322 syncs through accepted Phase 321 only.
- Update only `attention.md`, the focused static status test, and the new Phase 322 feature artifact directory.
- Preserve Hermes-native plugin architecture and SillyTavern asset compatibility by avoiding all runtime and asset changes.
- Keep adult-fiction/RP compatibility unchanged; do not involve minors or bypass provider safety systems.
- Leave checklist/acceptance finalization, staging, commit, push, service lifecycle commands, and progress-state updates outside executor S1.

## Non-Goals

- Do not touch runtime/source/plugin/provider/gateway/CLI files, root design, README, architecture, roadmap, requirements, compound docs, assets, fixtures, schemas, dependency/config/build files, or service lifecycle behavior.
- Do not change model/provider routing, credentials, adult-fiction/RP compatibility, provider safety behavior, network behavior, dependency files, or configuration files.
- Do not add a Phase 323 attention/status label; this slice records Phase 322 as the newly accepted completed phase.
- Do not edit existing prior phase feature directories.
- Do not let the executor finalize checklist/acceptance, stage, commit, push, send messages, update progress state, or perform broad rewrites.

This lane is docs/static-test/status-only. Hermes-native plugin architecture, SillyTavern asset compatibility, and provider/runtime behavior are unaffected and must remain untouched.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-321 accepted`
- To: `Current status (2026-06-18): All phases 1-322 accepted`

Append exactly once after `Phase 321 attention status sync through Phase 320`:
- Convert `Phase 320 attention status sync through Phase 319, and Phase 321 attention status sync through Phase 320.`
- To `Phase 320 attention status sync through Phase 319, Phase 321 attention status sync through Phase 320, and Phase 322 attention status sync through Phase 321.`

Preserve:
- `Phase 121-167`
- Every explicit `Phase 168` through `Phase 321` short label exactly as already written.

Do not add:
- Any `Phase 323` attention/status label to `attention.md` or the focused status label list.

Final attention suffix must end with:
`Phase 320 attention status sync through Phase 319, Phase 321 attention status sync through Phase 320, and Phase 322 attention status sync through Phase 321.`

Full focused-test suffix must become exactly:
`Phase 304 attention status sync through Phase 303, Phase 305 attention status sync through Phase 304, Phase 306 attention status sync through Phase 305, Phase 307 attention status sync through Phase 306, Phase 308 attention status sync through Phase 307, Phase 309 attention status sync through Phase 308, Phase 310 attention status sync through Phase 309, Phase 311 attention status sync through Phase 310, Phase 312 attention status sync through Phase 311, Phase 313 attention status sync through Phase 312, Phase 314 attention status sync through Phase 313, Phase 315 attention status sync through Phase 314, Phase 316 attention status sync through Phase 315, Phase 317 attention status sync through Phase 316, Phase 318 attention status sync through Phase 317, Phase 319 attention status sync through Phase 318, Phase 320 attention status sync through Phase 319, Phase 321 attention status sync through Phase 320, and Phase 322 attention status sync through Phase 321.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-322 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-321 accepted"`
- `STALE_PHASE_MARKER = "1-321"`
- `STALE_PHASE_MARKER_EN_DASH = "1–321"`
- Append `Phase 322 attention status sync through Phase 321` to `REQUIRED_PHASE_LABELS` exactly once.
- Preserve every existing required label through Phase 321.
- `FINAL_STATUS_SUFFIX` equals the Phase 304 through Phase 322 suffix above, including the final period.
- Runtime `phase_range` becomes `range(168, 323)`.
- Source self-check literal becomes `aggregate_range = "range(168, 323)"`.
- Add split stale aggregate guard for `range(168, 322)`.
- Retain older split stale aggregate guards, including `range(168, 321)`, `range(168, 320)`, `range(168, 319)`, and `range(168, 318)`.
- Preserve the anchored single `CURRENT_STATUS_PREFIX` assignment guard.
- Preserve the no-discovery-token guards: no `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` tokens in the focused test source.

## Allowed Files

Executor S1 may edit only:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Parent controller may materialize/finalize only:
- `design/codestable/features/2026-06-23-hermes-tavern-phase322-attention-status-sync-through-phase321/design.md`
- `design/codestable/features/2026-06-23-hermes-tavern-phase322-attention-status-sync-through-phase321/checklist.yaml`
- `design/codestable/features/2026-06-23-hermes-tavern-phase322-attention-status-sync-through-phase321/acceptance.md`

## Prohibited Files and Actions

Prohibited: runtime/source/plugin/provider/gateway/CLI files, `plugins/`, provider files, `gateway/`, `run_agent.py`, `cli.py`, `gateway/run.py`, plugin runtime files, credentials, root design, README, architecture, roadmap, requirements, compound docs, assets/fixtures/schemas, dependency/config/build files, service lifecycle commands, edits to existing prior phase feature directories, broad rewrites, executor staging, commit, push, messages, progress-state updates, and executor checklist or acceptance finalization.

## Structure Health

Compound convention lookup is not needed for this recurring status-only slice because the executor adds no files and may edit only the established attention/status-test pair.

File-level assessment:
- `design/codestable/attention.md`: one long mandatory startup status bullet; the only intended change is a prefix and terminal label update.
- `tests/test_hermes_tavern_codestable_status.py`: focused static regression; intended changes are constants, required label, suffix, ranges, stale guards, and preserved static guards.

Directory-level assessment:
- Executor adds no files.
- Parent may create only the new Phase 322 feature artifact directory.

Conclusion: no micro-refactor. A refactor would increase risk and exceed this status-only slice.

## Implementation Steps

S1: Sync status artifacts.
- Update only `attention.md` prefix and append only the Phase 322 label.
- Update only focused test constants, required label list, suffix, phase range, aggregate range, stale markers, stale split aggregate guards, and existing no-discovery-token guards.
- Do not finalize checklist or acceptance.

S2: Parent verification and artifact-only closeout.
- Parent controller runs required validation commands.
- Confirm changed and untracked paths are limited to allowed files.
- Finalize only the Phase 322 feature artifacts after verification.
- If any gate fails, leave status non-final and report the failing command.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-23-hermes-tavern-phase322-attention-status-sync-through-phase321 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts='`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- Static guard for stale standalone `1-321` patterns in `attention.md` and intentional-only stale values in `tests/test_hermes_tavern_codestable_status.py`.
- Static guard for no Phase 323 attention/status label in `attention.md` or the focused status label list.
- Static guard for exactly one anchored `CURRENT_STATUS_PREFIX` assignment in the focused test.
- Static guard preserving no-discovery-token expectations: no `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` tokens.
- Static allowlist guard for changed/untracked paths.
- `git diff --check`
- `git diff --cached --check`

## Risks and Rollback

Risks:
- Duplicate final `and` placement in the long attention suffix.
- Leaving stale `1-321` markers in the attention current-status bullet.
- Creating duplicate or stale `CURRENT_STATUS_PREFIX` assignments in the focused test.
- Touching runtime/plugin/provider/gateway/source/dependency/config paths outside this status-only slice.

Rollback point: revert only the Phase 322 allowed files to the pre-executor state; because executor must not stage, commit, push, finalize acceptance, or update progress state, rollback is limited to the dirty working tree before parent closeout.

## Executor Prompt

Implement only Phase 322 attention/status sync through accepted Phase 321. Edit only `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`. Advance current status to `All phases 1-322 accepted`, preserve `Phase 121-167` and every explicit Phase 168 through Phase 321 label, append exactly `Phase 322 attention status sync through Phase 321`, and do not add any Phase 323 attention/status label. Update focused test constants, suffix, required labels, `range(168, 323)`, `aggregate_range = "range(168, 323)"`, stale markers for `All phases 1-321 accepted`, and split stale aggregate guard for `range(168, 322)` while retaining older stale guards including `range(168, 321)`, `range(168, 320)`, `range(168, 319)`, and `range(168, 318)`. Preserve no-discovery-token guards and the single `CURRENT_STATUS_PREFIX` assignment guard. Do not commit, push, stage, update state, send messages, touch runtime/protected paths, change dependencies, edit prior phase directories, finalize checklist/acceptance, or run service lifecycle commands.

## Review Criteria

Architect review should output `PASS` only if the current diff matches this artifact, all changed/untracked files are within the allowed list, the current-status prefix/suffix/labels are exact with only one final `and`, the focused status test has exactly one anchored `CURRENT_STATUS_PREFIX` assignment and the required stale/no-discovery guards, verification gates pass or full pytest infeasibility is documented, and acceptance remains parent-pending/non-final until parent verification. Otherwise output `REQUEST_CHANGES` with the first concrete mismatch.
