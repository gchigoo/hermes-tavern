---
doc_type: feature-design
status: draft
feature: "2026-06-11-hermes-tavern-phase171-root-design-export-parity"
date: "2026-06-11"
summary: >
  Bring root-design writing command surfaces back in sync with already-implemented
  local export commands and add a focused design-doc regression test.
tags: [hermes-tavern, codestable, root-design, command-surface, export, docs, tests]
created: "2026-06-11"
updated: "2026-06-11"
owner: codestable-cron
implementation_ready: false
---
# Phase 171: Root Design Export Command Parity

## Gap

Phases 149-168 added local JSON/export command surfaces, and Phases 169-170
hardened source help, README, architecture, and regression coverage around those
surfaces. The root design's long-form writing command block still omits several
already-implemented local export literals even though source help, README, and
architecture expose them.

This is a documentation parity gap, not a runtime feature gap.

## Scope

Update `design/HERMES_TAVERN_DESIGN.md` only where it lists current writing
commands so the root design includes already-implemented local export literals
that are present in source help/README/architecture but absent from the root
writing command block, including:

- `/rp relationship export <relationship-id>`
- `/rp location export <location-id>`
- `/rp organization export <organization-id>`
- `/rp binding export <binding-id>`
- `/rp scene export <scene-id>`
- `/rp scene beat export <beat-id>`
- `/rp project revision export <note-id>`
- `/rp canon export <canon-id>`
- `/rp timeline export <timeline-id>`

Add one focused design-doc regression test that reads the root design and fails
if those current export literals drift out of the writing command surface again.

## Non-Goals

Do not change runtime command handlers, source command tables, README text,
architecture text, export payloads, file layout, database schemas, providers,
model routing, prompt compiler behavior, generation behavior, retrieval or
vectorization, archive/ZIP/import behavior, graph or automatic extraction tools,
credentials, content mode, minors/underage handling, safety-bypass behavior,
plugin assets, build artifacts, or Hermes core files.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `src/**`, `README.md`,
`design/codestable/architecture/ARCHITECTURE.md`, `plugins/**`, or `build/lib/**`.

## Acceptance

- Root design writing command surfaces include the implemented local export
  literals already present in source help/README/architecture.
- A focused design-doc regression test fails if those literals disappear from
  the root design.
- Focused docs tests pass.
- Protected/runtime/source paths remain unchanged.
