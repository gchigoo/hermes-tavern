---
doc_type: feature-design
feature: 2026-07-02-hermes-tavern-phase413-attention-status-sync-through-phase412
title: "Phase 413 attention/status sync through Phase 412"
status: approved
implementation_ready: true
date: "2026-07-02"
owner: company-boost
summary: approved S1 docs/static-test status-sync only.
---

# Phase 413 attention/status sync through Phase 412

## Selected gap

Phase 412 is the last accepted status reflected by the focused CodeStable status artifacts. Phase 413 is the next bounded docs/static-test sync slice, limited to advancing the startup attention status line and the dedicated regression test through accepted Phase 412.

## Allowed scope

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-02-hermes-tavern-phase413-attention-status-sync-through-phase412/design.md`
- `design/codestable/features/2026-07-02-hermes-tavern-phase413-attention-status-sync-through-phase412/checklist.yaml`

## Prohibited scope

- No runtime, source, plugin, provider, gateway, CLI, config, dependency, root-design, README, or architecture behavior changes.
- No edits to `run_agent.py`, `cli.py`, `gateway/run.py`, or `plugins/hermes_tavern` runtime files.
- No credentials, secrets, provider-safety bypass, minors-related work, or CSAM-related work.
- No `acceptance.md` creation in this phase; parent/controller owns final acceptance.

## Exact status contract

- `design/codestable/attention.md` must advance the current-status prefix to `Current status (2026-06-18): All phases 1-413 accepted`.
- The attention current-status bullet must preserve every existing label and append exactly one terminal label: `Phase 413 attention status sync through Phase 412`.
- The final attention suffix must end exactly with `Phase 411 attention status sync through Phase 410, Phase 412 attention status sync through Phase 411, and Phase 413 attention status sync through Phase 412.`
- `tests/test_hermes_tavern_codestable_status.py` must advance the live prefix/ranges to Phase 413, move stale prefix/markers to Phase 412, append the Phase 413 required label, keep the placement guard intact, and add a split stale aggregate guard for stale `range(168, 413)` without embedding that stale literal contiguously in source.

## Verification commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-02-hermes-tavern-phase413-attention-status-sync-through-phase412 --require doc_type --require status --require feature`
- `PYTHONPYCACHEPREFIX=/tmp/hermes-tavern-pycache-phase413-exec python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `env -u HERMES_SESSION_KEY -u HERMES_SESSION_ID HERMES_HOME=/Users/steven/.hermes PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`

## Parent acceptance boundary

This phase is S1 implementation only. Parent/controller verification owns acceptance finalization, any acceptance artifact creation, and any broader writeback beyond the four allowed files.
