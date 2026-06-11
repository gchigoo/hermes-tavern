---
doc_type: feature-design
status: approved
feature: "2026-06-11-hermes-tavern-phase172-attention-status-sync"
date: "2026-06-11"
summary: >
  Sync the mandatory CodeStable attention current-status line through accepted
  Phase 171 and add a focused docs regression so the startup context does not
  silently remain pinned to Phase 167.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-11"
updated: "2026-06-11"
owner: codestable-cron
implementation_ready: true
---

# Phase 172: CodeStable Attention Status Sync

## Gap

`design/codestable/attention.md` is the mandatory startup read for CodeStable
work in this repository. It currently says the project status is current as of
2026-06-08 and that all phases 1-167 are complete.

That is stale after accepted Phase 168 image settings export, Phase 169 project
JSON export surface parity, Phase 170 export surface regression, and Phase 171
root-design export parity. Phase 171 acceptance explicitly left a future tick to
select the next bounded doc-parity or local hardening gap, and this status drift
is the smallest confirmed safe slice.

This is a CodeStable context/documentation gap, not a runtime or product feature
gap.

## Scope

Update only the current-status bullet in `design/codestable/attention.md` so it
reports accepted phases through Phase 171. Preserve the surrounding startup
rules, path constraints, credential constraints, plugin architecture notes, and
adult-fiction/safety boundaries.

Use this replacement status text:

```text
- Current status (2026-06-11): All phases 1-171 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, and Phase 171 root-design export parity.
```

Add `tests/test_hermes_tavern_codestable_status.py` as a focused static docs
regression. The test should read `design/codestable/attention.md` directly and
assert:

- there is exactly one current-status bullet;
- the current-status bullet contains `Current status (2026-06-11): All phases 1-171 accepted`;
- the current-status bullet names Phase 168, Phase 169, Phase 170, and Phase 171
  with the same short labels used above;
- the current-status bullet no longer contains `2026-06-08` or standalone
  stale terminal-phase markers `1-167` / `1–167` (while preserving the valid
  `Phase 121-167` range in the current status text).

Keep the test static and explicit. Do not introduce automatic feature-tree
scanning, phase discovery, metadata extraction, or graph tooling.

## Non-Goals

Do not change runtime command handlers, source help, README text, root design,
architecture docs, roadmap or requirement docs, export payloads, database
schemas, providers, model routing, prompt compiler behavior, generation
behavior, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph
tooling, automatic extraction, credentials, content mode, minors/underage
handling, provider safety behavior, plugin assets, build artifacts, or Hermes
core files.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `src/**`,
`plugins/**`, `build/lib/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`,
`design/codestable/architecture/**`, `design/codestable/roadmap/**`, or
`design/codestable/requirements/**`.

## Structure Health

`attention.md` is intentionally small and already owns recurring startup context;
updating one stale status bullet is its existing responsibility. The new test
fits the repository's existing flat `tests/test_hermes_tavern_*.py` docs
regression pattern and does not require moving or splitting files.

No micro-refactor is needed.

## Acceptance

- `design/codestable/attention.md` reports current status as 2026-06-11 with all
  phases 1-171 accepted.
- The current-status bullet explicitly includes Phase 168, Phase 169, Phase 170,
  and Phase 171 short labels.
- The current-status bullet no longer reports Phase 167 as the terminal accepted
  phase.
- Focused CodeStable status docs tests pass.
- Protected runtime/source/plugin/root-design/architecture paths remain
  unchanged.
