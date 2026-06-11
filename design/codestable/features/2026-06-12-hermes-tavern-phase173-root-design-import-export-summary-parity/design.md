---
doc_type: feature-design
status: approved
feature: "2026-06-12-hermes-tavern-phase173-root-design-import-export-summary-parity"
date: "2026-06-12"
summary: >
  Sync root design section 17 Import / Export narrative with the accepted local
  import/export surface through Phase 168 and add a focused static design-doc
  regression.
tags: [hermes-tavern, codestable, root-design, import-export, export, docs, tests]
created: "2026-06-12"
updated: "2026-06-12"
owner: codestable-cron
implementation_ready: true
---

# Phase 173: Root Design Import / Export Summary Parity

## Gap

All active CodeStable checklists are accepted, complete/done, or implemented, and
Phase 172 is accepted. No Phase 173 artifact exists.

Root design command surfaces were recently synchronized, but
`design/HERMES_TAVERN_DESIGN.md` section 17 still has stale narrative text:

- it describes the current implementation as `Phase 121-151`;
- it says current export support stops at project Markdown plus card/lore/preset/persona JSON;
- its section-local command sketch still shows old generic commands such as
  `/rp import <attachment|url|path>`, `/rp export chat`, `/rp export project`,
  and `/rp backup`.

Runtime help, README, architecture, and tests already show the accepted export
surface through Phase 168, including session JSON export, novel entity JSON
exports, project JSON bundle export, and image settings JSON export.

This is a root-design documentation parity gap, not a runtime feature gap.

## Scope

Update only root design section 17 so its current implementation summary matches
accepted local import/export behavior through Phase 168.

The updated section should preserve these boundaries:

- current imports remain card/preset/lore/persona import surfaces and mobile
  attachment import behavior;
- project/novel archive import remains deferred;
- project archive ZIP, bulk export, cloud/archive sync, graph exports, automatic
  extraction, provider/generation side effects, content-mode changes,
  minors/underage handling, and safety-bypass behavior remain deferred;
- existing SillyTavern asset compatibility wording remains intact.

The current export summary should mention the implemented local surfaces at the
right level of detail:

- `/rp export [markdown|st-json]`
- `/rp session export <id>`
- `/rp card export <card>`
- `/rp lore export <lorebook>`
- `/rp preset export <preset>`
- `/rp persona export <persona>`
- `/rp project export [id]`
- `/rp chapter export <chapter-id>`
- `/rp scene export <scene-id>`
- `/rp canon export <canon-id>`
- `/rp timeline export <timeline-id>`
- `/rp relationship export <relationship-id>`
- `/rp character state export <character-state-id>`
- `/rp location export <location-id>`
- `/rp organization export <organization-id>`
- `/rp plot thread export <plot-thread-id>`
- `/rp style sample export <style-sample-id>`
- `/rp binding export <binding-id>`
- `/rp scene beat export <beat-id>`
- `/rp project revision export <note-id>`
- `/rp project export json [project-id]`
- `/rp image settings export`

Add one focused regression to `tests/test_hermes_tavern_design_docs.py` that reads
section 17 and asserts:

- stale `current Phase 121-151` / `current Phase 121–151` wording is absent;
- representative current export literals from Phase 152-168 are present in
  section 17;
- stale section-local generic commands `/rp export chat`, `/rp backup`, and
  `/rp import <attachment|url|path>` are not presented as current implemented
  commands.

## Non-Goals

Do not change runtime command handlers, source help, README text, architecture
text, CodeStable attention status, export payloads, file layout, database schemas,
providers, model routing, prompt compiler behavior, generation behavior,
retrieval/vectorization, archive/ZIP/import behavior, graph or automatic
extraction tools, credentials, content mode, minors/underage handling,
safety-bypass behavior, plugin assets, build artifacts, or Hermes core files.

Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `src/**`,
`plugins/**`, `README.md`, `design/codestable/architecture/**`,
`design/codestable/attention.md`, or `build/lib/**`.

## Structure Health

`design/HERMES_TAVERN_DESIGN.md` already owns product-level import/export
positioning. Section 17 is the correct place for this summary correction.

`tests/test_hermes_tavern_design_docs.py` already owns root-design regression
coverage from Phase 171, so adding a section-17 test there is consistent.

No micro-refactor is needed.

## Acceptance

- Root design section 17 no longer describes current implementation as Phase
  121-151.
- Root design section 17 describes current local import/export support through
  Phase 168 without promising archive ZIP/import, cloud sync, provider changes,
  graph tooling, automatic extraction, safety-bypass behavior, or minors/underage
  behavior.
- A focused design-doc regression covers the section-17 parity contract.
- Focused design-doc tests pass.
- Protected runtime/source/plugin/README/architecture/attention/build paths remain
  unchanged.
