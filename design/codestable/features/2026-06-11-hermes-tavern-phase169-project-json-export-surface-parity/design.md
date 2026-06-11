---
doc_type: feature-design
status: draft
feature: "2026-06-11-hermes-tavern-phase169-project-json-export-surface-parity"
date: "2026-06-11"
summary: >
  Harden current command-surface docs and help tests so the implemented Phase 167
  project JSON export command is represented consistently.
tags: [hermes-tavern, codestable, command-surface, json-export, docs, tests]
created: "2026-06-11"
updated: "2026-06-11"
owner: codestable-cron
implementation_ready: false
---
# Phase 169: Project JSON Export Surface Parity

## Gap

Phase 167 implemented `/rp project export json [project-id]`. The source command
table and README expose that exact command, and runtime tests cover JSON bundle
export behavior. The current command-surface blocks in `design/HERMES_TAVERN_DESIGN.md`
and `design/codestable/architecture/ARCHITECTURE.md` still list only the generic
project export surface, and `tests/test_hermes_tavern_commands.py` only asserts
a generic `/rp project export` literal.

## Scope

Update only command-surface documentation and exact help-test coverage for
`/rp project export json [project-id]`.

## Non-Goals

Do not change runtime command handlers, export payloads, file layout, provider or
model routing, generation behavior, prompt compiler behavior, gateway/core files,
schema migrations, credentials, plugins, archive/ZIP behavior, vectorization, or
retrieval.

## Implementation Plan

1. Add `/rp project export json [project-id]` beside the existing project export
   command in the root design command surface.
2. Add the same literal beside the project export entry in the CodeStable
   architecture current command surface.
3. Add one exact `_build_help_text()` assertion in `tests/test_hermes_tavern_commands.py`.

## Acceptance

The targeted command/help docs tests pass, and `rg` shows the exact literal in
source help, README, root design, architecture, and regression tests.
