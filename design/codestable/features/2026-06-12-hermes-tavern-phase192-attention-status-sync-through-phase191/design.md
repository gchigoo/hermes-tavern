---
doc_type: feature-design
status: approved
feature: "2026-06-12-hermes-tavern-phase192-attention-status-sync-through-phase191"
date: "2026-06-12"
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 191, without changing runtime, source,
  plugin, product, import/export, provider, prompt/generation, schema,
  root-design, architecture, reference, README, roadmap, requirement, compound,
  or build behavior.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-12"
updated: "2026-06-12"
owner: codestable-cron
implementation_ready: true
---

# Phase 192: CodeStable Attention Status Sync Through Phase 191

## Gap

`design/codestable/attention.md` is the mandatory startup read for CodeStable work
in this repository. It currently reports `Current status (2026-06-12): All phases
1-190 accepted`.

Phase 191 is accepted in the feature archive, so the mandatory startup status is
one accepted phase behind. The focused static regression in
`tests/test_hermes_tavern_codestable_status.py` also still pins the terminal
accepted range to Phase 190.

This is CodeStable startup-context metadata drift, not a runtime, product,
architecture, provider, prompt/generation, import/export, schema, or build
feature gap.

## Scope

Update only the current-status bullet in `design/codestable/attention.md` so it
reports accepted phases through Phase 191.

Use this replacement status text as the single current-status bullet:

    - Current status (2026-06-12): All phases 1-191 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, Phase 171 root-design export parity, Phase 172 attention status sync through Phase 171, Phase 173 root-design section 17 import/export summary parity, Phase 174 attention status sync through Phase 173, Phase 175 attention status sync through Phase 174, Phase 176 attention status sync through Phase 175, Phase 177 attention status sync through Phase 176, Phase 178 attention status sync through Phase 177, Phase 179 attention status sync through Phase 178, Phase 180 attention status sync through Phase 179, Phase 181 attention status sync through Phase 180, Phase 182 attention status sync through Phase 181, Phase 183 attention status sync through Phase 182, Phase 184 attention status sync through Phase 183, Phase 185 attention status sync through Phase 184, Phase 186 attention status sync through Phase 185, Phase 187 attention status sync through Phase 186, Phase 188 attention status sync through Phase 187, Phase 189 attention status sync through Phase 188, Phase 190 attention status sync through Phase 189, and Phase 191 attention status sync through Phase 190.

Update `tests/test_hermes_tavern_codestable_status.py` as the focused static
regression. The test should assert:

- there is exactly one current-status bullet;
- the current-status bullet contains `Current status (2026-06-12): All phases 1-191 accepted`;
- the bullet names Phase 168 through Phase 191 with the same short labels above;
- the bullet preserves Phase 168 through Phase 190 labels and appends `Phase 191 attention status sync through Phase 190`;
- the bullet no longer contains `All phases 1-190 accepted`;
- the bullet no longer contains standalone stale terminal `1-190` / `1–190` markers;
- the valid internal `Phase 121-167` range remains allowed.

Keep the regression static and explicit. Do not add automatic phase discovery,
feature-tree scanning, metadata extraction, graph tooling, generated status
summaries, runtime bootstrap logic, provider calls, schema changes,
prompt/generation changes, export payload changes, import/archive/cloud tooling,
root-design summaries, architecture/reference/README/roadmap/requirement/compound
writeback, build changes, or safety behavior changes.

## Allowed Files

Controller materialization for this planning artifact may use only:

- `design/codestable/features/2026-06-12-hermes-tavern-phase192-attention-status-sync-through-phase191/design.md`
- `design/codestable/features/2026-06-12-hermes-tavern-phase192-attention-status-sync-through-phase191/checklist.yaml`

Executor S1 may use only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 acceptance/writeback is controller-only and may use only:

- `design/codestable/features/2026-06-12-hermes-tavern-phase192-attention-status-sync-through-phase191/design.md`
- `design/codestable/features/2026-06-12-hermes-tavern-phase192-attention-status-sync-through-phase191/checklist.yaml`
- `design/codestable/features/2026-06-12-hermes-tavern-phase192-attention-status-sync-through-phase191/phase192-acceptance.md`

## Non-Goals

Do not change runtime command handlers, source package files, plugin files,
gateway or Hermes core files, README text, root design, architecture docs,
reference docs, roadmap or requirement docs, compound docs, export payloads,
import behavior, file layout, database schemas, providers, model routing, prompt
compiler behavior, generation behavior, retrieval/vectorization, archive/ZIP/cloud
sync behavior, graph tooling, automatic extraction, credentials, content mode,
adult-fiction/RP compatibility, minors/underage handling, provider safety
behavior, plugin assets, build artifacts, SillyTavern asset compatibility,
Hermes-native plugin architecture, or safety-bypass behavior.

Do not modify `run_agent.py`, `cli.py`, `gateway/**`, `src/**`, `plugins/**`,
`build/**`, `build/lib/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`,
`design/codestable/architecture/**`, `design/codestable/reference/**`,
`design/codestable/roadmap/**`, `design/codestable/requirements/**`, or
`design/codestable/compound/**`.

Do not edit Phase 191 artifacts or any existing accepted phase artifacts during
S1. S2 may edit only the new Phase 192 artifacts listed above.

## Structure Health

`design/codestable/attention.md` already owns recurring CodeStable startup
context. Replacing one stale status bullet is its existing responsibility.

`tests/test_hermes_tavern_codestable_status.py` already owns the static
current-status guard. Updating that existing test avoids a parallel status
regression file.

No matching compound convention changes are needed for directory organization,
file ownership, or naming. No micro-refactor is needed.

## Acceptance

- `design/codestable/attention.md` reports current status as 2026-06-12 with all
  phases 1-191 accepted.
- The current-status bullet preserves the existing Phase 168 through Phase 190
  short labels and appends `Phase 191 attention status sync through Phase 190`.
- The final list punctuation is exactly:
  `Phase 189 attention status sync through Phase 188, Phase 190 attention status sync through Phase 189, and Phase 191 attention status sync through Phase 190.`
- The current-status bullet no longer reports Phase 190 as the terminal accepted
  phase.
- The status regression rejects `All phases 1-190 accepted`.
- The status regression rejects standalone stale terminal `1-190` / `1–190`
  markers.
- The status regression allows the valid `Phase 121-167` internal range.
- The status regression remains static and explicit, with no generated phase
  discovery.
- Focused CodeStable status docs tests pass.
- Protected runtime/source/plugin/provider/prompt/generation/import/export/schema/
  root-design/architecture/reference/README/roadmap/requirement/compound/build
  paths remain unchanged.
- Full pytest passes as the registry gate.
- S2 acceptance/writeback remains controller-only.

## Risks

- The status line is long; keep it as one bullet and do not split it into
  generated summaries or multiple current-status bullets.
- The stale-marker guard must reject only standalone terminal `1-190` / `1–190`
  markers while preserving the valid internal `Phase 121-167` range and the
  Phase 190 and Phase 191 short labels.
- This phase must not update old accepted feature artifacts.
- This phase must not expand into runtime, source, plugin, provider,
  prompt/generation, import/export payload, schema, architecture, root-design,
  README, roadmap, requirement, compound, graph/archive/cloud, content-mode,
  minors/underage, adult-fiction/RP compatibility, build, or safety behavior.

## Product / Architecture Decision

No product or architecture decision is needed. This phase is docs/test/status-only
startup metadata synchronization.
