---
doc_type: feature-design
status: pending_parent_verification
feature: "2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331"
date: "2026-06-23"
owner: company_boost_lane
lane: "company-boost/parent-verified-artifact"
implementation_ready: true
parent_verification_required: true
bounded_phase: "docs/static-test/status-only"
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase332]
summary: >
  Materialize the Phase 332 S1 parent-handoff artifact while preserving the
  mandatory CodeStable attention/status contract through accepted Phase 331.
---

# Phase 332: CodeStable Attention Status Sync Through Phase 331

## Gate

Phase 331 is accepted at `design/codestable/features/2026-06-23-hermes-tavern-phase331-attention-status-sync-through-phase330/acceptance.md`.

Current state before this slice:
- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-331 accepted`.
- `attention.md` already includes `Phase 331 attention status sync through Phase 330` exactly once.
- `tests/test_hermes_tavern_codestable_status.py` enforces the Phase 331 prefix, required labels through Phase 331, `phase_range = range(168, 332)`, `aggregate_range = "range(168, 332)"`, and the split stale aggregate guard for `range(168, 331)`.
- No `phase332` feature artifact files existed before this controller materialization.

Selected slice: recurring status-only Phase 332 artifact lane, syncing attention/status through accepted Phase 331 only and leaving final closeout to the parent controller.

## Goals

- Materialize the Phase 332 `design.md` and `checklist.yaml` artifacts for a bounded S1 parent-handoff lane.
- Preserve the live Phase 331 attention/status contract exactly.
- Allow `attention.md` or the focused status test to be edited only if drift is found and only to restore the exact Phase 331 contract.
- Preserve Hermes-native plugin architecture, SillyTavern asset compatibility, and all runtime behavior.
- Keep adult-fiction/RP compatibility while making no content-policy, safety-bypass, provider-routing, minors, or CSAM-related changes.
- Leave acceptance, commit, and push closeout to the parent controller after verification.

## Non-Goals

- Do not advance the status line to `Current status (2026-06-18): All phases 1-332 accepted` during S1.
- Do not append `Phase 332 attention status sync through Phase 331` to `attention.md` or `REQUIRED_PHASE_LABELS` during S1.
- Do not regenerate the focused test's `REQUIRED_PHASE_LABELS`; use the live exact list.
- Do not create `acceptance.md` or finalize Phase 332 as accepted in this worker lane.
- Do not touch runtime/source/plugin/provider/gateway/CLI files, root design, README, architecture, requirements, roadmap, compound docs, assets, fixtures, schemas, dependency/config/build files, or service lifecycle behavior.
- Do not change model/provider routing, credentials, provider safety behavior, network behavior, dependency files, or configuration files.
- Do not edit existing prior phase feature directories.
- Executor must not stage, commit, push, send messages, update progress state, or perform broad rewrites; parent-controller commit/push closeout is allowed after verification.

## Exact Status Contract

Preserve the `attention.md` current-status prefix exactly:
- Required prefix: `Current status (2026-06-18): All phases 1-331 accepted`
- Forbidden prefix: `Current status (2026-06-18): All phases 1-332 accepted`

Preserve exactly once:
- `Phase 331 attention status sync through Phase 330`

Do not add:
- `Phase 332 attention status sync through Phase 331`

Preserve:
- `Phase 121-167`
- Every explicit Phase 168 through Phase 331 short label exactly as the live status/test define them.

Final attention suffix must remain:
`Phase 329 attention status sync through Phase 328, Phase 330 attention status sync through Phase 329, and Phase 331 attention status sync through Phase 330.`

Full focused-test suffix must remain exactly:
`Phase 307 attention status sync through Phase 306, Phase 308 attention status sync through Phase 307, Phase 309 attention status sync through Phase 308, Phase 310 attention status sync through Phase 309, Phase 311 attention status sync through Phase 310, Phase 312 attention status sync through Phase 311, Phase 313 attention status sync through Phase 312, Phase 314 attention status sync through Phase 313, Phase 315 attention status sync through Phase 314, Phase 316 attention status sync through Phase 315, Phase 317 attention status sync through Phase 316, Phase 318 attention status sync through Phase 317, Phase 319 attention status sync through Phase 318, Phase 320 attention status sync through Phase 319, Phase 321 attention status sync through Phase 320, Phase 322 attention status sync through Phase 321, Phase 323 attention status sync through Phase 322, Phase 324 attention status sync through Phase 323, Phase 325 attention status sync through Phase 324, Phase 326 attention status sync through Phase 325, Phase 327 attention status sync through Phase 326, Phase 328 attention status sync through Phase 327, Phase 329 attention status sync through Phase 328, Phase 330 attention status sync through Phase 329, and Phase 331 attention status sync through Phase 330.`

## Focused Test Contract

Preserve `tests/test_hermes_tavern_codestable_status.py` unless drift must be corrected:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-331 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-330 accepted"`
- `STALE_PHASE_MARKER = "1-330"`
- `STALE_PHASE_MARKER_EN_DASH = "1–330"`
- `Phase 331 attention status sync through Phase 330` appears exactly once in `REQUIRED_PHASE_LABELS`.
- No `Phase 332 attention status sync through Phase 331` label appears in the focused test.
- `FINAL_STATUS_SUFFIX` remains the Phase 307 through Phase 331 suffix above, with final punctuation and only one final `and` before Phase 331.
- Runtime `phase_range` remains `range(168, 332)`.
- Source self-check literal remains `aggregate_range = "range(168, 332)"`.
- Split stale aggregate guard for `range(168, 331)` remains split-string compatible, e.g. `"".join(["range(168, ", "33", "1", ")"])`.
- Older split stale aggregate guards remain.
- Preserve the anchored single `CURRENT_STATUS_PREFIX` assignment guard.
- Preserve no-discovery-token guards: no `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` tokens in focused test source.

## Allowed Files

Executor S1 may edit only:
- `design/codestable/attention.md` (only if needed to restore the exact Phase 331 status/label contract)
- `tests/test_hermes_tavern_codestable_status.py` (only if needed to restore the exact Phase 331 test contract)
- `design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331/design.md`
- `design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331/checklist.yaml`

## Prohibited Files and Actions

Protected/prohibited: `run_agent.py`, `cli.py`, `gateway/run.py`, runtime/source/plugin/provider/gateway/CLI files, `plugins/`, provider files, gateway files, plugin runtime files, credentials, root design, README, architecture, roadmap, requirements, compound docs, assets, fixtures, schemas, build outputs, dependency/config files, provider/model/network behavior, SillyTavern asset compatibility behavior, RP content-policy behavior, minor-related features, service lifecycle commands, edits to prior phase directories, `acceptance.md`, broad rewrites, staging, commit/push, messages, and progress-state updates.

## Implementation Steps

S1: Executor status-contract preservation and artifact-only handoff.
1. Read this design, the checklist, `attention.md`, the focused status test, and Phase 331 acceptance.
2. Confirm `attention.md` and the focused test already match the Phase 331 contract above.
3. If they match, leave `attention.md` and the focused test unchanged.
4. If drift is found, restore only the allowed portions to the exact Phase 331 contract.
5. Keep Phase 332 checklist status non-final with parent verification required.
6. Do not create `acceptance.md`.
7. Run the focused verification commands if feasible and report results.

S2: Parent verification and closeout.
1. Parent reruns the YAML, py_compile, focused pytest, static guard, diff, and optional full-suite gates.
2. Parent decides whether to create/finalize `acceptance.md` and advance any status after authoritative verification.
3. If any gate fails, keep Phase 332 non-final and report the first concrete mismatch.

## Acceptance and Verification Commands

Run from repo root:

```bash
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331 --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider
git diff --check
```

Static guard requirements:
- Changed/untracked paths are limited to the allowed files.
- No `acceptance.md` exists in the Phase 332 directory.
- Current status prefix remains `Current status (2026-06-18): All phases 1-331 accepted`.
- `Phase 331 attention status sync through Phase 330` appears exactly once in attention and focused required labels.
- No `Phase 332 attention status sync through Phase 331` appears in attention or the focused test.
- `phase_range = range(168, 332)` and `aggregate_range = "range(168, 332)"` remain.
- Split stale aggregate guard for `range(168, 331)` remains.
- Exactly one anchored `CURRENT_STATUS_PREFIX` assignment remains.
- No discovery tokens (`.glob(`, `.rglob(`, `iterdir(`, `os.walk`) are introduced.
- No protected/runtime/source/plugin/provider/gateway/config/dependency/root-doc/prior-phase paths change.

Optional full baseline if feasible:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider
```

## Risks and Pitfalls

- Off-by-one drift: Phase 332 is the artifact title, but S1 must preserve attention/test through accepted Phase 331 only.
- Do not add a Phase 332 status label to attention or `REQUIRED_PHASE_LABELS`.
- Do not advance to `All phases 1-332 accepted` until a later parent-controlled finalization explicitly requires it.
- Do not regenerate `REQUIRED_PHASE_LABELS`; preserve the live exact list.
- Keep stale aggregate guards split-string compatible; direct stale literal bans can false-fail if written naively.
- Avoid duplicate `CURRENT_STATUS_PREFIX` assignments.
- Do not finalize acceptance or create `acceptance.md` in this S1 lane.
- `git diff --check` does not catch untracked file whitespace until paths are staged; run direct file whitespace/final-newline checks for new artifacts.

## Executor Prompt

```text
You are the CodeStable executor for Hermes Tavern. Implement only Phase 332 attention/status sync through Phase 331 as an S1 parent-handoff lane.

Allowed files only:
- design/codestable/attention.md only if needed to restore the exact Phase 331 status/label contract
- tests/test_hermes_tavern_codestable_status.py only if needed to restore the exact Phase 331 test contract
- design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331/design.md
- design/codestable/features/2026-06-23-hermes-tavern-phase332-attention-status-sync-through-phase331/checklist.yaml

Do not create acceptance.md. Do not finalize Phase 332 as accepted. Do not stage, commit, push, run service lifecycle commands, or touch any protected/runtime/source/plugin/provider/gateway/CLI/config/dependency/root-doc/prior-phase path.

Exact contract: preserve `Current status (2026-06-18): All phases 1-331 accepted`; preserve `Phase 331 attention status sync through Phase 330` exactly once in attention and REQUIRED_PHASE_LABELS; do not add `Phase 332 attention status sync through Phase 331`; do not advance to `All phases 1-332 accepted`; preserve live REQUIRED_PHASE_LABELS exactly; keep `phase_range = range(168, 332)`, `aggregate_range = "range(168, 332)"`, and the split stale guard for `range(168, 331)`; keep exactly one anchored `CURRENT_STATUS_PREFIX` assignment and no discovery tokens.

If attention.md and the focused test already match this contract, leave them unchanged and update only the Phase 332 checklist to record S1 implementation pending parent verification. If drift is found, restore only the allowed portions to the exact Phase 331 contract.

Run YAML validation, py_compile, focused pytest, a static allowed-path/status guard, and git diff --check if feasible. Report changed files and verification results only.
```
