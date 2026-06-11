---
doc_type: feature-design
status: approved
feature: "2026-06-11-hermes-tavern-phase170-export-surface-regression"
date: "2026-06-11"
summary: >
  Add test-only regression coverage that keeps implemented export command
  literals visible in generated /rp help and README Core commands. No command
  handlers, docs text, schemas, providers, prompts, exports, or gateway/core
  behavior change.
tags: [hermes-tavern, codestable, command-surface, export, tests]
created: "2026-06-11"
updated: "2026-06-11"
owner: codestable-cron
implementation_ready: true
---
# Phase 170: Export Command Surface Regression Coverage

## Gap

Phases 149-168 added local JSON/export surfaces, and Phase 169 synchronized the
project JSON export command across root design, architecture, and help tests.
Current source help and README Core commands expose the implemented export
surface, but exact regression coverage is uneven:

- generated `/rp help` tests assert only some export literals directly;
- README Core command tests already cover many exports, but the exact project
  revision, character-state, and relationship export literals are not asserted
  as export-preservation cases.

This is a test-hardening gap, not a runtime feature gap.

## Scope

Add regression tests only:

1. In `tests/test_hermes_tavern_commands.py`, assert exact generated-help
   presence for the currently implemented export literals that lack direct
   coverage, including binding, style sample, character state, relationship,
   location, organization, plot thread, project revision, chapter, scene beat,
   scene, canon, and timeline exports.
2. In `tests/test_hermes_tavern_readme_docs.py`, add exact README Core command
   assertions for `/rp project revision export <note-id>`,
   `/rp character state export <character-state-id>`, and
   `/rp relationship export <relationship-id>`.
3. Keep existing shorthand differences intact. Do not require README syntax to
   become identical to generated help where README intentionally groups commands.

## Non-Goals

No source command table edits, README text edits, root-design edits, architecture
edits, runtime handler changes, export payload changes, schema migrations,
provider/model routing, prompt/compiler behavior, generation behavior,
retrieval/vectorization, archive/ZIP behavior, credential behavior, content-mode
behavior, minors/underage handling, safety-bypass behavior, plugin asset edits,
or gateway/core edits.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `plugins/**`, or
`build/lib/**`.

## Acceptance

- Generated help tests fail if any covered implemented export literal disappears
  from `_build_help_text()`.
- README Core command tests fail if the missing exact export literals disappear
  from README.
- Focused command/README tests pass.
- No source, runtime, README, root-design, architecture, plugin, build artifact,
  gateway/core, provider, prompt, schema, or export implementation files change.
