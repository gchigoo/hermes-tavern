---
doc_type: feature-design
status: approved
feature: "2026-06-13-hermes-tavern-phase206-attention-status-sync-through-phase205"
date: "2026-06-13"
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 205, without changing runtime, source,
  plugin, product, import/export, provider, prompt/generation, schema,
  root-design, architecture, reference, README, roadmap, requirement, compound,
  or build behavior.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-13"
updated: "2026-06-13"
owner: codestable-cron
implementation_ready: true
---

# Phase 206: CodeStable Attention Status Sync Through Phase 205

## Gap

`design/codestable/attention.md` is the mandatory startup read for CodeStable work
in this repository. It currently reports `Current status (2026-06-13): All phases
1-204 accepted`.

Phase 205 is accepted in the feature archive: its checklist has `status:
accepted` and `workflow_status: completed`, and `phase205-acceptance.md` has
`status: accepted`. No Phase 206 feature directory is present in the feature
tree. The mandatory startup status and focused static regression are therefore
one accepted phase behind.

This is CodeStable startup-context metadata drift, not a runtime, product,
architecture, provider, prompt/generation, import/export, schema, or build
feature gap.

## Scope

Update only the current-status bullet in `design/codestable/attention.md` so it
reports accepted phases through Phase 205.

Use this replacement status text as the single current-status bullet:

- Current status (2026-06-13): All phases 1-205 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, Phase 171 root-design export parity, Phase 172 attention status sync through Phase 171, Phase 173 root-design section 17 import/export summary parity, Phase 174 attention status sync through Phase 173, Phase 175 attention status sync through Phase 174, Phase 176 attention status sync through Phase 175, Phase 177 attention status sync through Phase 176, Phase 178 attention status sync through Phase 177, Phase 179 attention status sync through Phase 178, Phase 180 attention status sync through Phase 179, Phase 181 attention status sync through Phase 180, Phase 182 attention status sync through Phase 181, Phase 183 attention status sync through Phase 182, Phase 184 attention status sync through Phase 183, Phase 185 attention status sync through Phase 184, Phase 186 attention status sync through Phase 185, Phase 187 attention status sync through Phase 186, Phase 188 attention status sync through Phase 187, Phase 189 attention status sync through Phase 188, Phase 190 attention status sync through Phase 189, Phase 191 attention status sync through Phase 190, Phase 192 attention status sync through Phase 191, Phase 193 attention status sync through Phase 192, Phase 194 attention status sync through Phase 193, Phase 195 attention status sync through Phase 194, Phase 196 attention status sync through Phase 195, Phase 197 attention status sync through Phase 196, Phase 198 attention status sync through Phase 197, Phase 199 attention status sync through Phase 198, Phase 200 attention status sync through Phase 199, Phase 201 attention status sync through Phase 200, Phase 202 attention status sync through Phase 201, Phase 203 attention status sync through Phase 202, Phase 204 attention status sync through Phase 203, and Phase 205 attention status sync through Phase 204.

Update `tests/test_hermes_tavern_codestable_status.py` as the focused static
regression. The test should assert:

- there is exactly one current-status bullet;
- the current-status bullet contains `Current status (2026-06-13): All phases 1-205 accepted`;
- the bullet names Phase 168 through Phase 205 with the same short labels above;
- the bullet preserves Phase 168 through Phase 204 labels and appends `Phase 205 attention status sync through Phase 204`;
- the bullet no longer contains `All phases 1-204 accepted`;
- the bullet no longer contains standalone stale terminal `1-204` / `1–204` markers;
- the valid internal `Phase 121-167` range remains allowed;
- the final punctuation ends with `Phase 203 attention status sync through Phase 202, Phase 204 attention status sync through Phase 203, and Phase 205 attention status sync through Phase 204.`;
- the aggregate range assertion covers Phase 168 through Phase 205 with `range(168, 206)`;
- the test remains static and explicit, with no generated phase discovery using `glob`, `rglob`, `iterdir`, or `os.walk`.

Keep the regression static and explicit. Do not add automatic phase discovery,
feature-tree scanning, metadata extraction, graph tooling, generated status
summaries, runtime bootstrap logic, provider calls, schema changes,
prompt/generation changes, export payload changes, import behavior,
root-design summaries, architecture/reference/README/roadmap/requirement/compound
writeback, build changes, adult-fiction/RP behavior changes, minors/underage
handling changes, safety-bypass behavior, Hermes-native plugin architecture
changes, or SillyTavern asset compatibility changes.

## Allowed Files

Overall allowed files for this phase:

- `design/codestable/features/2026-06-13-hermes-tavern-phase206-attention-status-sync-through-phase205/design.md`
- `design/codestable/features/2026-06-13-hermes-tavern-phase206-attention-status-sync-through-phase205/checklist.yaml`
- `design/codestable/features/2026-06-13-hermes-tavern-phase206-attention-status-sync-through-phase205/phase206-acceptance.md`
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Executor S1 implementation may use exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 acceptance/writeback is controller-only and may use exactly:

- `design/codestable/features/2026-06-13-hermes-tavern-phase206-attention-status-sync-through-phase205/design.md`
- `design/codestable/features/2026-06-13-hermes-tavern-phase206-attention-status-sync-through-phase205/checklist.yaml`
- `design/codestable/features/2026-06-13-hermes-tavern-phase206-attention-status-sync-through-phase205/phase206-acceptance.md`

Before implementation, the controller must confirm the allowed-file set has no
overlap with prohibited protected paths. Any overlap blocks S1/S2.

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

Do not edit Phase 205 artifacts or any older accepted phase artifacts during S1.
S2 may edit only the new Phase 206 artifacts listed above.

## Execution Plan

S1 is the only executor implementation slice. It replaces the single attention
current-status bullet and updates the focused static regression to guard the
Phase 1-205 terminal status, Phase 168-205 explicit labels, stale 1-204
rejection, valid Phase 121-167 preservation, final-list punctuation, and
`range(168, 206)` aggregate assertion.

S2 is controller-only closeout. It records acceptance evidence in
`phase206-acceptance.md` and finalizes the Phase 206 design/checklist statuses
without touching attention, tests, runtime/source/plugin files, or protected
documentation/build paths.

## Structure Health

`design/codestable/attention.md` already owns recurring CodeStable startup
context. Replacing one stale status bullet is its existing responsibility.

`tests/test_hermes_tavern_codestable_status.py` already owns the static
current-status guard. Updating that existing test avoids a parallel status
regression file.

No directory organization, file ownership, naming convention, or micro-refactor
change is needed.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- static marker guard must confirm: exactly one current-status line, terminal `1-205`, explicit Phase 168 through Phase 205 labels, `range(168, 206)`, final punctuation through Phase 205, stale terminal `1-204` rejection, valid `Phase 121-167` preservation, and no generated phase-discovery calls.
- changed-path allowlist guard must confirm only the five allowed files changed.
- protected-path status guard must report no changes under runtime/source/plugin/provider/root-design/architecture/reference/README/roadmap/requirement/compound/build paths.
- `git diff --check`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`

## Acceptance

- `design/codestable/attention.md` reports current status as 2026-06-13 with all
  phases 1-205 accepted.
- The current-status bullet preserves the existing Phase 168 through Phase 204
  short labels and appends `Phase 205 attention status sync through Phase 204`.
- The final list punctuation is exactly:
  `Phase 203 attention status sync through Phase 202, Phase 204 attention status sync through Phase 203, and Phase 205 attention status sync through Phase 204.`
- The current-status bullet no longer reports Phase 204 as the terminal accepted
  phase.
- The status regression rejects `All phases 1-204 accepted`.
- The status regression rejects standalone stale terminal `1-204` / `1–204`
  markers.
- The status regression allows the valid `Phase 121-167` internal range.
- The status regression explicitly asserts Phase 168 through Phase 205 labels,
  including `Phase 205 attention status sync through Phase 204`.
- The aggregate phase range assertion uses `range(168, 206)`.
- The status regression remains static and explicit, with no generated phase
  discovery.
- Focused CodeStable status docs tests pass.
- Protected runtime/source/plugin/provider/prompt/generation/import/export/schema/
  root-design/architecture/reference/README/roadmap/requirement/compound/build
  paths remain unchanged.
- Full pytest passes as the registry gate.
- S2 acceptance/writeback remains controller-only.

## Risks

- The stale-negative checks and aggregate range must advance together: stale
  prefixes/markers move from 1-203 to 1-204 while the aggregate assertion moves
  from `range(168, 205)` to `range(168, 206)`.
- Previous Phase 204 wording and the Phase 205 accepted feature label must be
  preserved exactly; do not rewrite accepted phase labels while advancing the
  terminal status.
- The status line is long; keep it as one bullet and do not split it into
  generated summaries or multiple current-status bullets.
- The stale-marker guard must reject only standalone terminal `1-204` / `1–204`
  markers while preserving the valid `Phase 121-167` internal range and the
  Phase 204 and Phase 205 short labels.
- The controller must check allowed/prohibited path overlap before execution; any
  overlap between the five allowed files and protected path patterns blocks the
  phase.
- This phase must not update Phase 205 or older accepted feature artifacts during
  S1.
- This phase must not expand into runtime, source, plugin, provider,
  prompt/generation, import/export payload, schema, architecture, root-design,
  README, roadmap, requirement, compound, graph/archive/cloud, content-mode,
  minors/underage, adult-fiction/RP compatibility, build, SillyTavern asset
  compatibility, Hermes-native plugin architecture, or safety behavior.

## Product / Architecture Decision

No product or architecture decision is needed. This phase is docs/test/status-only
startup metadata synchronization.
