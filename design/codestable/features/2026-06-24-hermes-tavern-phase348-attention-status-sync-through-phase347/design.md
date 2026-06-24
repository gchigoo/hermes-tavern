---
doc_type: feature-design
feature: 2026-06-24-hermes-tavern-phase348-attention-status-sync-through-phase347
status: approved
implementation_ready: true
date: "2026-06-24"
owner: company_boost_lane
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready Phase 348 attention/status sync through accepted Phase 347."
tags:
  - hermes-tavern
  - codestable
  - attention
  - status-sync
  - docs
  - tests
  - phase348
---

# Phase 348: Attention Status Sync Through Phase 347

## Background / Current Status

Phase 347 is the latest accepted phase. Its acceptance report is at:

`design/codestable/features/2026-06-24-hermes-tavern-phase347-attention-status-sync-through-phase346/acceptance.md`

The acceptance frontmatter has `status: accepted`.

Current live CodeStable status contract before S1:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-347 accepted`.
- Terminal suffix is `Phase 345 attention status sync through Phase 344, Phase 346 attention status sync through Phase 345, and Phase 347 attention status sync through Phase 346.`
- `tests/test_hermes_tavern_codestable_status.py` has:
  - `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-347 accepted"`
  - `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-346 accepted"`
  - `STALE_PHASE_MARKER = "1-346"`
  - `STALE_PHASE_MARKER_EN_DASH = "1–346"`
  - `phase_range = range(168, 348)`
  - `aggregate_range = "range(168, 348)"`
- No Phase 348 feature directory existed before this slice.

## Goals

- Create the Phase 348 feature design/checklist artifacts as non-final S1 parent-handoff artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-347 to 1-348.
- Append `Phase 348 attention status sync through Phase 347` exactly once.
- Update `tests/test_hermes_tavern_codestable_status.py` so the focused status regression guards the Phase 348 live status contract.
- Preserve all historical labels exactly, including `Phase 121-167` and every explicit Phase 168 through Phase 348 label.
- Keep Hermes-native plugin architecture and SillyTavern asset compatibility unchanged.
- Preserve adult-fiction/RP compatibility without minors-related work or provider-safety bypasses.

## Non-Goals

- No runtime/source/plugin/provider/gateway/CLI/config/dependency/root README/root design/architecture/roadmap/requirements/compound/build updates.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No service lifecycle commands.
- No dependency installation.
- No acceptance.md creation or acceptance finalization in this S1 slice.
- No commits, staging, or pushes.
- No Phase 349 work.

## Exact Allowed Files

Executor S1 may touch exactly these files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-24-hermes-tavern-phase348-attention-status-sync-through-phase347/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase348-attention-status-sync-through-phase347/checklist.yaml`

## Prohibited Files / Areas

All files not listed above are prohibited for executor S1, including:

- `plugins/`
- `hermes/`
- runtime, source, provider, gateway, CLI, config, dependency, compound, build files
- root `README.md`
- root `HERMES_TAVERN_DESIGN.md`
- root design docs outside the allowed Phase 348 feature directory
- `design/codestable/architecture/`
- `design/codestable/roadmap/`
- `design/codestable/requirements/`
- `design/codestable/compound/`
- generated cache or service lifecycle artifacts
- `acceptance.md`

## Exact Status Line Change

Update the single current status line in `design/codestable/attention.md`:

- from prefix `Current status (2026-06-18): All phases 1-347 accepted`
- to prefix `Current status (2026-06-18): All phases 1-348 accepted`

Preserve all existing labels exactly, append `Phase 348 attention status sync through Phase 347` exactly once, and replace the terminal suffix:

- from `Phase 345 attention status sync through Phase 344, Phase 346 attention status sync through Phase 345, and Phase 347 attention status sync through Phase 346.`
- to `Phase 346 attention status sync through Phase 345, Phase 347 attention status sync through Phase 346, and Phase 348 attention status sync through Phase 347.`

## Test Contract Changes

Update `tests/test_hermes_tavern_codestable_status.py`:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-348 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-347 accepted"`
- `STALE_PHASE_MARKER = "1-347"`
- `STALE_PHASE_MARKER_EN_DASH = "1–347"`
- Add `"Phase 348 attention status sync through Phase 347"` to `REQUIRED_PHASE_LABELS` exactly once, after Phase 347.
- `FINAL_STATUS_SUFFIX = "Phase 346 attention status sync through Phase 345, Phase 347 attention status sync through Phase 346, and Phase 348 attention status sync through Phase 347."`
- `phase_range = range(168, 349)`
- `aggregate_range = "range(168, 349)"`
- Add split stale aggregate guard for `range(168, 348)` without leaving that contiguous stale literal in source:
  `stale_aggregate_range_348 = "".join(["range(168, ", "34", "8", ")"])`
- Include `stale_aggregate_range_348` in the stale aggregate tuple.
- Keep existing split stale aggregate guards.
- Keep no-discovery-token guards for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.
- Keep the anchored `CURRENT_STATUS_PREFIX` assignment guard:
  `assert re.findall(r"^CURRENT_STATUS_PREFIX\s*=", test, re.M) == ["CURRENT_STATUS_PREFIX ="]`

## Verification Commands

```bash
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-24-hermes-tavern-phase348-attention-status-sync-through-phase347 --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider
git diff --check
```

Static guard checks:

```bash
rg -n '^CURRENT_STATUS_PREFIX = "Current status \(2026-06-18\): All phases 1-348 accepted"$' tests/test_hermes_tavern_codestable_status.py
rg -n 'Phase 348 attention status sync through Phase 347' design/codestable/attention.md tests/test_hermes_tavern_codestable_status.py
rg -n 'phase_range = range\(168, 349\)|aggregate_range = "range\(168, 349\)"' tests/test_hermes_tavern_codestable_status.py
rg -n 'range\(168, 348\)' tests/test_hermes_tavern_codestable_status.py
```

Expected for the final `rg 'range\(168, 348\)'` guard: no output.

Optional broader check when feasible:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider
```

## Executor Prompt

Implement only Phase 348 S1 for `2026-06-24-hermes-tavern-phase348-attention-status-sync-through-phase347`. Touch exactly the four allowed files listed in this design. Preserve all prior phase labels by copying literal text from current files; do not formula-generate labels. Update attention and the focused status test from Phase 347 to Phase 348, add the split stale aggregate guard for `range(168, 348)`, move only the terminal conjunction, keep checklist/root workflow non-final with parent verification required, and do not create `acceptance.md` or Phase 349. Run the listed verification commands and report real results. Do not commit, stage, or push.
