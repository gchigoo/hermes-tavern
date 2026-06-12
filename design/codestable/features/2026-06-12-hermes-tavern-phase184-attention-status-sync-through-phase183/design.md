---
doc_type: feature-design
status: approved
feature: "2026-06-12-hermes-tavern-phase184-attention-status-sync-through-phase183"
date: "2026-06-12"
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 183, without changing runtime, source,
  plugin, product, import/export, provider, prompt/generation, graph/archive/cloud,
  content-mode, minors/underage, or safety behavior.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-12"
updated: "2026-06-12"
owner: codestable-cron
implementation_ready: true
---

# Phase 184: CodeStable Attention Status Sync Through Phase 183

## Gap

`design/codestable/attention.md` is the mandatory startup read for CodeStable work
in this repository. It currently reports `Current status (2026-06-12): All phases
1-182 accepted`.

Phase 183 is now accepted in the feature archive, so the mandatory startup status
is one accepted phase behind. The focused static regression in
`tests/test_hermes_tavern_codestable_status.py` also still pins the terminal
accepted range to Phase 182.

This is a CodeStable startup-context metadata drift, not a runtime or product
feature gap.

## Scope

Update only the current-status bullet in `design/codestable/attention.md` so it
reports accepted phases through Phase 183.

Use this replacement status text as the single current-status bullet:

    - Current status (2026-06-12): All phases 1-183 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, Phase 171 root-design export parity, Phase 172 attention status sync through Phase 171, Phase 173 root-design section 17 import/export summary parity, Phase 174 attention status sync through Phase 173, Phase 175 attention status sync through Phase 174, Phase 176 attention status sync through Phase 175, Phase 177 attention status sync through Phase 176, Phase 178 attention status sync through Phase 177, Phase 179 attention status sync through Phase 178, Phase 180 attention status sync through Phase 179, Phase 181 attention status sync through Phase 180, Phase 182 attention status sync through Phase 181, and Phase 183 attention status sync through Phase 182.

Update `tests/test_hermes_tavern_codestable_status.py` as the focused static
regression. The test should assert:

- there is exactly one current-status bullet;
- the current-status bullet contains `Current status (2026-06-12): All phases 1-183 accepted`;
- the bullet names Phase 168 through Phase 183 with the same short labels above;
- the bullet no longer contains standalone terminal `1-182` / `1–182` markers;
- the valid internal `Phase 121-167` range remains allowed.

Keep the regression static and explicit. Do not add automatic phase discovery,
feature-tree scanning, metadata extraction, graph tooling, generated status
summaries, runtime bootstrap logic, provider calls, schema changes,
prompt/generation changes, export payload changes, import/archive/cloud tooling,
or safety behavior changes.

## Allowed Files

Controller materialization and closeout may use only:

- `design/codestable/features/2026-06-12-hermes-tavern-phase184-attention-status-sync-through-phase183/design.md`
- `design/codestable/features/2026-06-12-hermes-tavern-phase184-attention-status-sync-through-phase183/checklist.yaml`
- `design/codestable/features/2026-06-12-hermes-tavern-phase184-attention-status-sync-through-phase183/phase184-acceptance.md`

Executor S1 may use only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

## Non-Goals

Do not change runtime command handlers, source package files, plugin files,
gateway or Hermes core files, README text, root design, architecture docs,
reference docs, roadmap or requirement docs, compound docs, export payloads,
file layout, database schemas, providers, model routing, prompt compiler
behavior, generation behavior, retrieval/vectorization, archive/ZIP/cloud sync
behavior, graph tooling, automatic extraction, credentials, content mode,
adult-fiction/RP compatibility, minors/underage handling, provider safety
behavior, plugin assets, build artifacts, SillyTavern asset compatibility,
Hermes-native plugin architecture, or safety-bypass behavior.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `gateway/**`, `src/**`,
`plugins/**`, `build/lib/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`,
`design/codestable/architecture/**`, `design/codestable/reference/**`,
`design/codestable/roadmap/**`, `design/codestable/requirements/**`, or
`design/codestable/compound/**`.

## Structure Health

`design/codestable/attention.md` already owns recurring CodeStable startup
context. Replacing one stale status bullet is its existing responsibility.

`tests/test_hermes_tavern_codestable_status.py` already owns the static
current-status guard. Updating that existing test avoids a parallel status
regression file.

No micro-refactor is needed.

## Acceptance

- `design/codestable/attention.md` reports current status as 2026-06-12 with all
  phases 1-183 accepted.
- The current-status bullet explicitly includes Phase 168 through Phase 183 short
  labels.
- The current-status bullet no longer reports Phase 182 as the terminal accepted
  phase.
- The status regression rejects standalone terminal `1-182` / `1–182` markers.
- The status regression allows the valid `Phase 121-167` internal range.
- Focused CodeStable status docs tests pass.
- Protected runtime/source/plugin/root-design/architecture/reference/README/
  roadmap/requirement/compound/build paths remain unchanged.

## Risks

- The status line is long; keep it as one bullet and do not split it into
  generated summaries or multiple current-status bullets.
- The stale-marker guard must reject only standalone terminal `1-182` / `1–182`
  markers while preserving the valid internal `Phase 121-167` range and the
  Phase 182 and Phase 183 short labels.
- This phase must not update old accepted feature artifacts.
- This phase must not expand into runtime, source, plugin, provider,
  prompt/generation, import/export payload, graph/archive/cloud, content-mode,
  minors/underage, or safety behavior.
