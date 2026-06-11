---
doc_type: feature-design
status: draft
feature: "2026-06-12-hermes-tavern-phase174-attention-status-sync-through-phase173"
date: "2026-06-12"
summary: >
  Sync the mandatory CodeStable attention current-status line and its static
  regression through accepted Phase 173, without changing runtime or product docs.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-12"
updated: "2026-06-12"
owner: codestable-cron
implementation_ready: false
---

# Phase 174: CodeStable Attention Status Sync Through Phase 173

## Gap

`design/codestable/attention.md` is the mandatory startup read for CodeStable work
in this repository. It currently reports `Current status (2026-06-11): All phases
1-171 accepted`.

That was correct after Phase 172, but Phase 173 is now accepted. Phase 173 was a
root-design section-17 import/export parity slice and intentionally did not update
attention status. The existing static regression in
`tests/test_hermes_tavern_codestable_status.py` also still pins the current-status
line to Phase 171.

This is a CodeStable startup-context drift, not a runtime feature gap.

## Scope

Update only the current-status bullet in `design/codestable/attention.md` so it
reports accepted phases through Phase 173.

Use this replacement status text as the single current-status bullet:

    - Current status (2026-06-12): All phases 1-173 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, Phase 171 root-design export parity, Phase 172 attention status sync through Phase 171, and Phase 173 root-design section 17 import/export summary parity.

Update `tests/test_hermes_tavern_codestable_status.py` as the focused static
regression. The test should read `design/codestable/attention.md` directly and
assert:

- there is exactly one current-status bullet;
- the current-status bullet contains `Current status (2026-06-12): All phases 1-173 accepted`;
- the current-status bullet names Phase 168, Phase 169, Phase 170, Phase 171,
  Phase 172, and Phase 173 with the same short labels used above;
- the current-status bullet no longer contains `2026-06-11` or standalone stale
  terminal-phase markers for `1-171` with either hyphen or en-dash spelling;
- the valid internal `Phase 121-167` range remains allowed.

Keep the regression static and explicit. Do not add automatic phase discovery,
feature-tree scanning, metadata extraction, graph tooling, or generated status
summaries.

## Non-Goals

Do not change runtime command handlers, source help, README text, root design,
architecture docs, roadmap or requirement docs, export payloads, file layout,
database schemas, providers, model routing, prompt compiler behavior, generation
behavior, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling,
automatic extraction, credentials, content mode, minors/underage handling,
provider safety behavior, plugin assets, build artifacts, or Hermes core files.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`,
`plugins/**`, `build/lib/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`,
`design/codestable/architecture/**`, `design/codestable/roadmap/**`,
`design/codestable/requirements/**`, or `design/codestable/compound/**`.

## Structure Health

`design/codestable/attention.md` is intentionally small and owns recurring
startup context. Replacing one stale status bullet is its existing responsibility.

`tests/test_hermes_tavern_codestable_status.py` already owns the static
current-status guard from Phase 172. Updating that existing test is the correct
test placement and avoids adding a parallel status-regression file.

No micro-refactor is needed.

## Acceptance

- `design/codestable/attention.md` reports current status as 2026-06-12 with all
  phases 1-173 accepted.
- The current-status bullet explicitly includes Phase 168 through Phase 173 short
  labels.
- The current-status bullet no longer reports Phase 171 as the terminal accepted
  phase.
- The status regression allows the valid `Phase 121-167` internal range and does
  not treat old accepted feature artifacts as active blockers.
- Focused CodeStable status docs tests pass.
- Protected runtime/source/plugin/root-design/architecture/README/roadmap/
  requirement/compound/build paths remain unchanged.
