---
doc_type: feature-design
status: approved
feature: "2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224"
date: "2026-06-14"
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 224, without changing runtime/source behavior
  or protected product documentation.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-14"
updated: "2026-06-14"
owner: codestable-cron
implementation_ready: true
---

# Phase 225: CodeStable Attention Status Sync Through Phase 224

## Read-Only Precheck

Required startup/status files were read before selecting work:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-14-hermes-tavern-phase224-attention-status-sync-through-phase223/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase224-attention-status-sync-through-phase223/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase224-attention-status-sync-through-phase223/phase224-acceptance.md`

Phase 224 is accepted: `phase224-acceptance.md` has `status: accepted`, the checklist has `status: accepted` and `workflow_status: completed`, and the accepted report confirms Phase 224 synced the startup status and focused static regression through accepted Phase 223.

`design/codestable/attention.md` currently reports `Current status (2026-06-14): All phases 1-223 accepted` and ends with `Phase 221 attention status sync through Phase 220, Phase 222 attention status sync through Phase 221, and Phase 223 attention status sync through Phase 222.`

`tests/test_hermes_tavern_codestable_status.py` currently guards terminal range 1-223, stale 1-222 markers, Phase 168 through Phase 223 labels, and `range(168, 224)`.

The target Phase 225 feature directory had no files in the read-only precheck.

## Gap

`design/codestable/attention.md` is the mandatory startup read for CodeStable work in this repository. Phase 224 is accepted in the feature archive, but the startup status and focused static regression still stop at Phase 223. The mandatory startup status and focused regression are therefore one accepted phase behind.

This is CodeStable startup-context metadata drift, not a runtime, source, plugin, provider/model routing, prompt/generation, import/export, schema, root-design, architecture, reference, README, roadmap, requirement, compound, build, Hermes core, adult-fiction/RP compatibility, minors, safety, or SillyTavern compatibility feature gap.

## Scope

Create the new feature directory exactly:

`design/codestable/features/2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224/`

Update only the current-status bullet in `design/codestable/attention.md` so it reports accepted phases through Phase 224. Advance only the terminal range to `All phases 1-224 accepted`, preserve all existing labels through Phase 223, adjust the final-list punctuation, and append exactly:

`Phase 224 attention status sync through Phase 223`

Use this replacement status text as the single current-status bullet:

- Current status (2026-06-14): All phases 1-224 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, Phase 171 root-design export parity, Phase 172 attention status sync through Phase 171, Phase 173 root-design section 17 import/export summary parity, Phase 174 attention status sync through Phase 173, Phase 175 attention status sync through Phase 174, Phase 176 attention status sync through Phase 175, Phase 177 attention status sync through Phase 176, Phase 178 attention status sync through Phase 177, Phase 179 attention status sync through Phase 178, Phase 180 attention status sync through Phase 179, Phase 181 attention status sync through Phase 180, Phase 182 attention status sync through Phase 181, Phase 183 attention status sync through Phase 182, Phase 184 attention status sync through Phase 183, Phase 185 attention status sync through Phase 184, Phase 186 attention status sync through Phase 185, Phase 187 attention status sync through Phase 186, Phase 188 attention status sync through Phase 187, Phase 189 attention status sync through Phase 188, Phase 190 attention status sync through Phase 189, Phase 191 attention status sync through Phase 190, Phase 192 attention status sync through Phase 191, Phase 193 attention status sync through Phase 192, Phase 194 attention status sync through Phase 193, Phase 195 attention status sync through Phase 194, Phase 196 attention status sync through Phase 195, Phase 197 attention status sync through Phase 196, Phase 198 attention status sync through Phase 197, Phase 199 attention status sync through Phase 198, Phase 200 attention status sync through Phase 199, Phase 201 attention status sync through Phase 200, Phase 202 attention status sync through Phase 201, Phase 203 attention status sync through Phase 202, Phase 204 attention status sync through Phase 203, Phase 205 attention status sync through Phase 204, Phase 206 attention status sync through Phase 205, Phase 207 attention status sync through Phase 206, Phase 208 attention status sync through Phase 207, Phase 209 attention status sync through Phase 208, Phase 210 attention status sync through Phase 209, Phase 211 attention status sync through Phase 210, Phase 212 attention status sync through Phase 211, Phase 213 attention status sync through Phase 212, Phase 214 attention status sync through Phase 213, Phase 215 attention status sync through Phase 214, Phase 216 attention status sync through Phase 215, Phase 217 attention status sync through Phase 216, Phase 218 attention status sync through Phase 217, Phase 219 attention status sync through Phase 218, Phase 220 attention status sync through Phase 219, Phase 221 attention status sync through Phase 220, Phase 222 attention status sync through Phase 221, Phase 223 attention status sync through Phase 222, and Phase 224 attention status sync through Phase 223.

Update `tests/test_hermes_tavern_codestable_status.py` as the focused static regression. The test must assert:

- `CURRENT_STATUS_PREFIX` is `Current status (2026-06-14): All phases 1-224 accepted`;
- `STALE_STATUS_PREFIX` is `Current status (2026-06-14): All phases 1-223 accepted`;
- stale standalone markers are `1-223` and `1–223`;
- `REQUIRED_PHASE_LABELS` includes Phase 168 through Phase 224;
- `FINAL_STATUS_SUFFIX` is `Phase 222 attention status sync through Phase 221, Phase 223 attention status sync through Phase 222, and Phase 224 attention status sync through Phase 223.`;
- the aggregate phase range assertion is `range(168, 225)`;
- the valid internal `Phase 121-167` range remains allowed;
- the test remains static and explicit, with no generated phase discovery using `glob`, `rglob`, `iterdir`, or `os.walk`.

## Allowed Files

Executor S1 implementation may edit exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Controller artifact materialization before S1 may create exactly:

- `design/codestable/features/2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224/checklist.yaml`

Controller S2 acceptance/writeback may edit exactly:

- `design/codestable/features/2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224/phase225-acceptance.md`

Before implementation, the controller must confirm the overall allowed-file set has no overlap with prohibited exact paths or prohibited path prefixes. Any non-empty overlap blocks S1 and S2.

## Non-Goals

Do not change runtime command handlers, source package files, plugin files, gateway or Hermes core files, provider/model routing files, prompt/generation behavior, import/export behavior or payloads, schema files, README text, root design, architecture docs, reference docs, roadmap or requirement docs, compound docs, build artifacts, file layout, database schemas, retrieval/vectorization, archive/ZIP/cloud sync behavior, graph tooling, automatic extraction, credentials, content mode, adult-fiction/RP compatibility, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, or safety-bypass behavior.

Do not modify `run_agent.py`, `cli.py`, `gateway/**`, `src/**`, `plugins/**`, `build/**`, `build/lib/**`, `README.md`, `design/HERMES_TAVERN_DESIGN.md`, `design/codestable/architecture/**`, `design/codestable/reference/**`, `design/codestable/roadmap/**`, `design/codestable/requirements/**`, or `design/codestable/compound/**`.

Do not edit Phase 224 artifacts or any older accepted phase artifacts during S1. S2 may edit only the new Phase 225 artifacts listed above.

S1 must not mark final accepted statuses and must not create `phase225-acceptance.md`. S2 is controller-only acceptance closeout.

## Execution Plan

S1 is the only executor implementation slice. It replaces the single attention current-status bullet and updates the focused static regression to guard the Phase 1-224 terminal status, Phase 168-224 explicit labels, stale 1-223 rejection, valid Phase 121-167 preservation, final-list punctuation, and `range(168, 225)` aggregate assertion.

S2 is controller-only closeout. It records acceptance evidence in `phase225-acceptance.md` and finalizes the Phase 225 checklist/design statuses without touching attention, tests, runtime/source/plugin/provider/prompt/generation/import/export/schema files, Hermes core files, or protected documentation/build paths. S2 must not ask the executor to mark final accepted statuses.

## Structure Health

`design/codestable/attention.md` already owns recurring CodeStable startup context. Replacing one stale status bullet is its existing responsibility.

`tests/test_hermes_tavern_codestable_status.py` already owns the static current-status guard. Updating that existing test avoids a parallel status regression file.

No directory organization, file ownership, naming convention, or micro-refactor change is needed.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224/design.md --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-14-hermes-tavern-phase225-attention-status-sync-through-phase224/checklist.yaml --yaml-only --require doc_type --require status --require feature --require implementation_ready`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- static marker guard must confirm: exactly one current-status line, terminal `1-224`, explicit Phase 168 through Phase 224 labels, `range(168, 225)`, final punctuation through Phase 224, stale terminal `1-223` / `1–223` rejection, valid `Phase 121-167` preservation, and no generated phase-discovery calls.
- changed-path allowlist guard must confirm only the five allowed files changed.
- protected-path guard must report no changes under runtime/source/plugin/provider/prompt/generation/import/export/schema/root-design/architecture/reference/README/roadmap/requirement/compound/build/Hermes core paths.
- allowed/prohibited overlap guard must report an empty overlap before S1 and S2.
- `git diff --check`
- `git diff --cached --check`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` when feasible.

## Acceptance

Phase 225 is acceptable when:

- the single current-status bullet reports all phases 1-224 accepted;
- the status bullet preserves prior labels through Phase 223 and appends exactly `Phase 224 attention status sync through Phase 223`;
- the final suffix is exactly `Phase 222 attention status sync through Phase 221, Phase 223 attention status sync through Phase 222, and Phase 224 attention status sync through Phase 223.`;
- stale terminal 1-223 markers are rejected while valid internal `Phase 121-167` remains allowed;
- `REQUIRED_PHASE_LABELS` includes Phase 168 through Phase 224;
- the aggregate assertion is `range(168, 225)`;
- the focused static regression passes and remains explicit/static;
- changed paths are limited to the five allowed files;
- protected paths and prohibited change categories remain untouched;
- S2 acceptance closeout is performed by the controller only.

## Risks

- The stale-negative checks and aggregate range must advance together: stale prefixes/markers move from 1-222 to 1-223 while the aggregate assertion moves from `range(168, 224)` to `range(168, 225)`.
- The current status line is long; keep it as one bullet and do not split it into generated summaries or multiple current-status bullets.
- The final-list punctuation must move the `and` from Phase 223 to Phase 224 without rewriting older accepted labels.
