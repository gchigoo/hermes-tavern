---
doc_type: feature-design
feature: "2026-06-06-hermes-tavern-phase141-metadata-inertness-matrix"
status: approved
date: "2026-06-06"
summary: >
  Add a test-only co-presence regression proving current inert novel metadata
  families remain excluded from debug prompt/context output when they coexist on
  one linked project/chapter/scene. No source, command, export, prompt,
  provider, generation, retrieval, credential, docs, architecture, or product
  behavior changes are in scope.
tags: [novel, metadata, no-leak, regression, test-only, offline]
---

# Phase 141: Metadata Inertness Matrix Regression

## 0. Terms

| Term | Meaning | Conflict guard |
|---|---|---|
| Metadata Inertness Matrix | One runtime regression that creates current inert metadata families together and asserts their distinctive markers do not appear in debug prompt/context output. | Not a new metadata family, command, export format, prompt feature, graph, alias, merge/split, extraction, or generation behavior. |
| Inert Novel Metadata | User-authored local metadata that is command/export-visible only: project brief premise, outline, chapter/scene summaries, relationship state/renamed label, character state, location, organization, plot thread, style sample, default binding asset content, revision note, and scene beat. | Excludes prompt-active project style guide, canon, scene narration, scene goal, persona, note, memory, lore, card, and preset-use modules. |
| Prompt-Active Sentinel | A small existing prompt-active marker used only to prove the test session is linked and exercising prompt assembly. | Not a new prompt behavior and not asserted absent. |

## 1. Decisions And Constraints

Need:

Recent metadata phases are accepted and already have per-family no-leak tests. The risk now is regression drift when many metadata families coexist in one linked session. A single co-presence no-leak test guards the contract without choosing new relationship graph, alias, merge/split, automatic extraction, or export semantics.

Success:

- One new runtime test creates a card-backed active session linked to a project/chapter/scene.
- The test adds distinctive marker text for all current inert metadata families.
- The test may add one existing prompt-active sentinel, such as a scene goal, and assert that sentinel appears in `/rp debug prompt` so absence assertions are meaningful.
- `/rp debug prompt` and `/rp debug context` omit every inert marker.
- The implementation edits tests only and should pass against current source. If it exposes a source bug, S1 stops and reports the bug candidate instead of widening scope.

Hard constraints:

- No source changes.
- No README/docs changes.
- No CodeStable acceptance/status/writeback changes during S1.
- No provider/network calls, generation calls, credential handling, safety bypass, underage/minor bypass, graph behavior, aliases, merge/split, automatic extraction, vectorization, retrieval, summarization, archive import/export, or SillyTavern asset compatibility changes.
- Never edit `run_agent.py`, `cli.py`, `gateway/run.py`, `src/hermes_tavern/runtime.py`, `plugins/**`, or `build/lib/**`.

## 2. Names And Flow

### 2.1 Noun Layer

Current:

- `tests/test_hermes_tavern_novel_runtime.py` has per-family no-leak tests for project brief/outline, chapter/scene summaries, scene beats, relationships, character state, default bindings, locations, organizations, revision notes, plot threads, and style samples.
- `tests/test_hermes_tavern_novel_db.py` and `tests/test_hermes_tavern_novel_runtime.py` already include all-current metadata export matrix tests.
- Architecture states Project Brief, Project Outline, Relationship State, Character State, Location, Organization, Plot Thread, Style Sample, Default Bindings, Revision Notes, and Scene Beat metadata are excluded from prompt assembly, debug prompt/context payloads, and context-budget reporting.

Change:

Add one runtime test, expected name:

`test_all_current_inert_metadata_markers_do_not_leak_to_debug_prompt_or_context`

The test should place distinctive inert markers in:

- Project brief premise.
- Project outline.
- Chapter summary.
- Scene summary.
- Relationship state text and renamed relationship label.
- Character state.
- Location description.
- Organization description.
- Plot thread description.
- Style sample text.
- Revision note text.
- Scene beat text.
- Default binding asset content or a distinctive default-binding marker.

### 2.2 Orchestration Layer

Test flow:

```text
create TavernStore + TavernRuntime
  -> save local card
  -> /rp start card
  -> create project, chapter, scene
  -> link scene to active session
  -> add one prompt-active sentinel through existing behavior
  -> add all inert metadata markers
  -> run /rp debug prompt
  -> run /rp debug context
  -> assert prompt-active sentinel appears in prompt
  -> assert every inert marker is absent from prompt and context
```

Flow constraints:

- The test must not call provider adapters or generation.
- The test must not inspect or change export behavior.
- The test must not mutate source behavior to make assertions pass.
- The test should use neutral adult-fiction/RP-compatible fictional examples and avoid age, underage, school-grade, or safety-classifier examples.

### 2.3 Mount Points

Allowed S1 file:

| File | Purpose |
|---|---|
| `tests/test_hermes_tavern_novel_runtime.py` | Add the co-presence no-leak regression beside existing no-leak/runtime metadata tests. |

Prohibited S1 files:

- `src/**`
- `README.md`
- `docs/**`
- `design/HERMES_TAVERN_DESIGN.md`
- `design/codestable/**`
- `tests/test_hermes_tavern_novel_db.py`
- `run_agent.py`
- `cli.py`
- `gateway/**`
- `plugins/**`
- `build/lib/**`

### 2.4 Slicing

S1 only: add the single runtime no-leak matrix test and run focused verification.

No acceptance artifact, checklist finalization, architecture writeback, root-design writeback, docs update, README update, source fix, or product behavior change belongs to S1.

### 2.5 Structure Health

No pre-feature micro-refactor.

`tests/test_hermes_tavern_novel_runtime.py` is large, but it already owns runtime command, debug prompt/context, and metadata no-leak regressions. A new helper module would add indirection for one test. Any helper should stay local to the test file and only reduce repeated marker assertions.

## 3. Acceptance Criteria

1. Exactly one implementation file changes: `tests/test_hermes_tavern_novel_runtime.py`.
2. The new test creates one linked project/chapter/scene active session and verifies the prompt path is active with an existing prompt-active sentinel.
3. The new test adds distinctive markers for all current inert metadata families listed in this design.
4. `/rp debug prompt` omits every inert marker.
5. `/rp debug context` omits every inert marker.
6. Focused runtime tests pass offline without provider/network/generation calls.
7. Plugin-wide Tavern tests pass offline.
8. Reverse-scope checks show no source, README/docs, architecture/root-design, CodeStable status/acceptance, protected core, gateway, plugin shim, build artifact, prompt/provider/model/content/generation/retrieval/vectorization/memory/media/importer/archive/graph/extraction/credential/safety-bypass files changed.
9. If the test exposes a source bug, executor reports it and does not widen S1 into a source fix.

## 4. Architecture/Root Design Relationship

This phase is pure regression hardening for the current architecture contract. It does not make any deferred metadata current, does not add command surface, and does not require architecture or root-design writeback. It reinforces the existing statement that recent metadata families are command/export-visible only and excluded from prompt/debug/context/provider/generation paths.
