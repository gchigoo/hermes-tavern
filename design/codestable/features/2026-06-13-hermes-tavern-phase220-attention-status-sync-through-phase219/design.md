---
doc_type: feature-design
status: approved
feature: "2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219"
date: "2026-06-13"
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 219, without changing runtime, source,
  plugin, provider/model routing, prompt/generation, import/export, schema,
  root-design, architecture, reference, README, roadmap, requirement, compound,
  build, or Hermes core behavior.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-13"
updated: "2026-06-13"
owner: codestable-cron
implementation_ready: true
---

# Phase 220: CodeStable Attention Status Sync Through Phase 219

## Read-Only Precheck

Required startup/status files were read before selecting work:

- `design/codestable/attention.md`
- `design/codestable/features/2026-06-13-hermes-tavern-phase219-attention-status-sync-through-phase218/design.md`
- `design/codestable/features/2026-06-13-hermes-tavern-phase219-attention-status-sync-through-phase218/checklist.yaml`
- `design/codestable/features/2026-06-13-hermes-tavern-phase219-attention-status-sync-through-phase218/phase219-acceptance.md`
- `tests/test_hermes_tavern_codestable_status.py`

Phase 219 is accepted: the Phase 219 checklist has `status: accepted` and
`workflow_status: completed`, and `phase219-acceptance.md` has
`status: accepted`.

`design/codestable/attention.md` reports `Current status (2026-06-13): All
phases 1-218 accepted` and ends with `Phase 218 attention status sync through
Phase 217`.

`tests/test_hermes_tavern_codestable_status.py` currently guards terminal range
1-218, stale 1-217 markers, Phase 168 through Phase 218 labels, and
`range(168, 219)`.

No Phase 220 feature directory was found. Read-only changed-path commands
reported no changed path names; any sandbox cache warnings remain non-semantic
for this planning artifact.

## Gap

`design/codestable/attention.md` is the mandatory startup read for CodeStable work
in this repository. Phase 219 is accepted in the feature archive, but the
startup status and focused static regression still stop at Phase 218. The
mandatory startup status and focused regression are therefore one accepted phase
behind.

This is CodeStable startup-context metadata drift, not a runtime, source, plugin,
provider/model routing, prompt/generation, import/export, schema, root-design,
architecture, reference, README, roadmap, requirement, compound, build, or Hermes
core feature gap.

## Scope

Create the new feature directory exactly:

`design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/`

Update only the current-status bullet in `design/codestable/attention.md` so it
reports accepted phases through Phase 219. The update must advance only the
terminal range to `All phases 1-219 accepted` and append `Phase 219 attention
status sync through Phase 218` after the Phase 218 entry.

Use this replacement status text as the single current-status bullet:

- Current status (2026-06-13): All phases 1-219 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, Phase 171 root-design export parity, Phase 172 attention status sync through Phase 171, Phase 173 root-design section 17 import/export summary parity, Phase 174 attention status sync through Phase 173, Phase 175 attention status sync through Phase 174, Phase 176 attention status sync through Phase 175, Phase 177 attention status sync through Phase 176, Phase 178 attention status sync through Phase 177, Phase 179 attention status sync through Phase 178, Phase 180 attention status sync through Phase 179, Phase 181 attention status sync through Phase 180, Phase 182 attention status sync through Phase 181, Phase 183 attention status sync through Phase 182, Phase 184 attention status sync through Phase 183, Phase 185 attention status sync through Phase 184, Phase 186 attention status sync through Phase 185, Phase 187 attention status sync through Phase 186, Phase 188 attention status sync through Phase 187, Phase 189 attention status sync through Phase 188, Phase 190 attention status sync through Phase 189, Phase 191 attention status sync through Phase 190, Phase 192 attention status sync through Phase 191, Phase 193 attention status sync through Phase 192, Phase 194 attention status sync through Phase 193, Phase 195 attention status sync through Phase 194, Phase 196 attention status sync through Phase 195, Phase 197 attention status sync through Phase 196, Phase 198 attention status sync through Phase 197, Phase 199 attention status sync through Phase 198, Phase 200 attention status sync through Phase 199, Phase 201 attention status sync through Phase 200, Phase 202 attention status sync through Phase 201, Phase 203 attention status sync through Phase 202, Phase 204 attention status sync through Phase 203, Phase 205 attention status sync through Phase 204, Phase 206 attention status sync through Phase 205, Phase 207 attention status sync through Phase 206, Phase 208 attention status sync through Phase 207, Phase 209 attention status sync through Phase 208, Phase 210 attention status sync through Phase 209, Phase 211 attention status sync through Phase 210, Phase 212 attention status sync through Phase 211, Phase 213 attention status sync through Phase 212, Phase 214 attention status sync through Phase 213, Phase 215 attention status sync through Phase 214, Phase 216 attention status sync through Phase 215, Phase 217 attention status sync through Phase 216, Phase 218 attention status sync through Phase 217, and Phase 219 attention status sync through Phase 218.

Update `tests/test_hermes_tavern_codestable_status.py` as the focused static
regression. The test must assert:

- `CURRENT_STATUS_PREFIX` is `Current status (2026-06-13): All phases 1-219 accepted`;
- `STALE_STATUS_PREFIX` is `Current status (2026-06-13): All phases 1-218 accepted`;
- stale standalone markers are `1-218` and `1–218`;
- `REQUIRED_PHASE_LABELS` includes Phase 168 through Phase 219;
- `FINAL_STATUS_SUFFIX` ends with `Phase 217 attention status sync through Phase 216, Phase 218 attention status sync through Phase 217, and Phase 219 attention status sync through Phase 218.`;
- the aggregate phase range assertion covers Phase 168 through Phase 219 with `range(168, 220)`;
- the valid internal `Phase 121-167` range remains allowed;
- the test remains static and explicit, with no generated phase discovery using `glob`, `rglob`, `iterdir`, or `os.walk`.

Keep the regression static and explicit. Do not add automatic phase discovery,
feature-tree scanning, metadata extraction, graph tooling, generated status
summaries, runtime bootstrap logic, provider calls, schema changes,
prompt/generation changes, export payload changes, import behavior,
root-design summaries, architecture/reference/README/roadmap/requirement/compound
writeback, build changes, Hermes core changes, adult-fiction/RP behavior changes,
minors/underage handling changes, safety-bypass behavior, Hermes-native plugin
architecture changes, or SillyTavern asset compatibility changes.

## Allowed Files

Overall allowed files for this phase are exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/design.md`
- `design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/checklist.yaml`
- `design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/phase220-acceptance.md`

Executor S1 implementation may use exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Controller S2 acceptance/writeback may use exactly:

- `design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/design.md`
- `design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/checklist.yaml`
- `design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/phase220-acceptance.md`

Before implementation, the controller must confirm the overall allowed-file set
has no overlap with prohibited exact paths or prohibited path prefixes. Any
allowed/prohibited overlap blocks S1 and S2.

## Non-Goals

Do not change runtime command handlers, source package files, plugin files,
gateway or Hermes core files, provider/model routing files, prompt/generation
behavior, import/export behavior or payloads, schema files, README text, root
design, architecture docs, reference docs, roadmap or requirement docs, compound
docs, build artifacts, file layout, database schemas, retrieval/vectorization,
archive/ZIP/cloud sync behavior, graph tooling, automatic extraction,
credentials, content mode, adult-fiction/RP compatibility, minors/underage
handling, provider safety behavior, plugin assets, SillyTavern asset
compatibility, Hermes-native plugin architecture, or safety-bypass behavior.

Do not modify `run_agent.py`, `cli.py`, `gateway/**`, `src/**`, `plugins/**`,
`build/**`, `build/lib/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`,
`design/codestable/architecture/**`, `design/codestable/reference/**`,
`design/codestable/roadmap/**`, `design/codestable/requirements/**`, or
`design/codestable/compound/**`.

Do not edit Phase 219 artifacts or any older accepted phase artifacts during S1.
S2 may edit only the new Phase 220 artifacts listed above.

## Execution Plan

S1 is the only executor implementation slice. It replaces the single attention
current-status bullet and updates the focused static regression to guard the
Phase 1-219 terminal status, Phase 168-219 explicit labels, stale 1-218
rejection, valid Phase 121-167 preservation, final-list punctuation, and
`range(168, 220)` aggregate assertion.

S2 is controller-only closeout. It records acceptance evidence in
`phase220-acceptance.md` and finalizes the Phase 220 checklist/design statuses
without touching attention, tests, runtime/source/plugin/provider/prompt/
generation/import/export/schema files, Hermes core files, or protected
documentation/build paths. S2 must not ask the executor to mark final accepted
statuses, and the executor must not create `phase220-acceptance.md`.

## Structure Health

`design/codestable/attention.md` already owns recurring CodeStable startup
context. Replacing one stale status bullet is its existing responsibility.

`tests/test_hermes_tavern_codestable_status.py` already owns the static
current-status guard. Updating that existing test avoids a parallel status
regression file.

No directory organization, file ownership, naming convention, or micro-refactor
change is needed.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-13-hermes-tavern-phase220-attention-status-sync-through-phase219/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- static marker guard must confirm: exactly one current-status line, terminal `1-219`, explicit Phase 168 through Phase 219 labels, `range(168, 220)`, final punctuation through Phase 219, stale terminal `1-218` / `1–218` rejection, valid `Phase 121-167` preservation, and no generated phase-discovery calls.
- changed-path allowlist guard must confirm only the five allowed files changed.
- protected-path guard must report no changes under runtime/source/plugin/provider/prompt/generation/import/export/schema/root-design/architecture/reference/README/roadmap/requirement/compound/build/Hermes core paths.
- allowed/prohibited overlap guard must report an empty overlap before S1 and S2.
- `git diff --check`
- `git diff --cached --check`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` when feasible.

## Acceptance

Phase 220 is acceptable when:

- the single current-status bullet reports all phases 1-219 accepted;
- the status bullet preserves prior labels through Phase 218 and appends only `Phase 219 attention status sync through Phase 218`;
- stale terminal 1-218 markers are rejected while valid internal `Phase 121-167` remains allowed;
- the focused static regression passes and remains explicit/static;
- changed paths are limited to the five allowed files;
- protected paths and prohibited change categories remain untouched;
- S2 acceptance closeout is performed by the controller only.
