---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-17-hermes-tavern-phase293-attention-status-sync-through-phase292"
date: "2026-06-17"
created: "2026-06-17"
updated: "2026-06-17"
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 292 only, without changing runtime behavior,
  plugin/provider/gateway internals, root design, architecture, roadmap,
  requirements, compound docs, credentials, or build assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 293: CodeStable Attention Status Sync Through Phase 292

## Exact S1 Contract

- `design/codestable/attention.md` current status must start with:
  `Current status (2026-06-17): All phases 1-292 accepted`.
- Add exactly one new short label to the same status line:
  `Phase 292 attention status sync through Phase 291`.
- Preserve `2026-06-17` exactly in the current-status prefix.
- Preserve `Phase 121-167`.
- Preserve all explicit `Phase 168` through `Phase 292` labels.
- Append only `Phase 292 attention status sync through Phase 291`.
- Do not add any `Phase 293` label to `attention.md`.
- Phase 293 syncs only through accepted Phase 292.
- Do not change runtime/product/source/plugin/provider/gateway behavior.

## Focused Status Regression Contract

Update `tests/test_hermes_tavern_codestable_status.py` so it enforces:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-17): All phases 1-292 accepted"`.
- `STALE_STATUS_PREFIX = "Current status (2026-06-17): All phases 1-291 accepted"`.
- `STALE_PHASE_MARKER = "1-291"` and `STALE_PHASE_MARKER_EN_DASH = "1–291"`.
- `REQUIRED_PHASE_LABELS` includes `Phase 292 attention status sync through Phase 291`.
- `FINAL_STATUS_SUFFIX` is exactly:
  `Phase 290 attention status sync through Phase 289, Phase 291 attention status sync through Phase 290, and Phase 292 attention status sync through Phase 291.`
- The runtime phase range assertion is `range(168, 293)`.
- The source self-check contains `aggregate_range = "range(168, 293)"`.
- Stale aggregate negative guards include split-string construction for stale `range(168, 292)` and retain older stale ranges.
- The single `CURRENT_STATUS_PREFIX` assignment check uses anchored regex:
  `re.findall(r"^CURRENT_STATUS_PREFIX\\s*=", test, re.M) == ["CURRENT_STATUS_PREFIX ="]`.
- Discovery-token guards keep `.glob(`, `.rglob(`, `iterdir(`, and `os.walk` split inside strings.

## Scope

Allowed files only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-17-hermes-tavern-phase293-attention-status-sync-through-phase292/design.md`
- `design/codestable/features/2026-06-17-hermes-tavern-phase293-attention-status-sync-through-phase292/checklist.yaml`
- `design/codestable/features/2026-06-17-hermes-tavern-phase293-attention-status-sync-through-phase292/acceptance.md`

## Prohibited Files/Actions

No changes to runtime, source, provider, plugin, gateway, root design, README,
architecture, roadmap, requirements, compound docs, build outputs, assets,
schemas, credential files, service lifecycle, or provider configuration. Do not
commit, push, or update `.hermes/project-progress/state.json`.

## Validators, Tests, and Guards

Worker-controller verification must run after implementation:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-17-hermes-tavern-phase293-attention-status-sync-through-phase292 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static status guard using anchored regex for `CURRENT_STATUS_PREFIX` assignment count and explicit expected prefix/range/label checks.
- Protected-path diff guard over the five allowed files, including untracked Phase 293 files.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` if feasible; do not disable plugin autoload for the full suite.
- `git diff --check`.
- Rerun YAML validation after any checklist/acceptance evidence patch.

## Architect Review Checklist

- Diff touches only the five allowed files.
- `attention.md` has exactly one current-status bullet.
- Prefix is exactly `All phases 1-292 accepted`.
- Stale `All phases 1-291 accepted`, `1-291`, and `1–291` terminal markers are rejected.
- `Phase 121-167` remains present.
- Explicit `Phase 168` through `Phase 292` labels are present.
- Only new attention label is `Phase 292 attention status sync through Phase 291`.
- No `Phase 293 attention status sync` label appears in `attention.md`.
- Final suffix is exactly the Phase 290/291/292 suffix.
- Focused regression uses `range(168, 293)`.
- Stale aggregate guards are split and include stale `range(168, 292)`.
- Phase 293 artifacts honestly mark parent verification required and no commit/push performed until parent closeout.
- No runtime, plugin, provider, gateway, root-design, README, architecture, roadmap, requirements, compound, build, credential, service lifecycle, commit, push, or state update occurred.
