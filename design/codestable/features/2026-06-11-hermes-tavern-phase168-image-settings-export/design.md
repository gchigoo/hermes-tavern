---
doc_type: feature-design
status: in_progress
feature: "2026-06-11-hermes-tavern-phase168-image-settings-export"
date: "2026-06-11"
summary: >
  DRAFT — Adds one bounded /rp image settings export command that exports the
  active session's image generation settings as a JSON file and returns a quoted
  MEDIA marker. Pure local operation, no provider/generation/schema changes.
tags: [hermes-tavern, image, export, settings, json, offline]
created: "2026-06-11"
updated: "2026-06-11"
owner: codestable-cron
implementation_ready: true
---

# Phase 168: Image Settings JSON Export

## Background

All CodeStable phases 1–167 are accepted. The root design's Phase 11 ("Media and
extension hooks") includes an already-implemented `/rp image settings` inspect
surface backed by `get_image_settings(session_id)`. The image settings can be
inspected, set, and cleared, but there is no standalone JSON export command —
unlike every other metadata entity (card, lorebook, preset, persona, session,
chapter, scene, canon, timeline, relationship, character_state, location,
organization, plot_thread, style_sample, binding, scene_beat, revision_note,
project), which already have JSON export.

This gap means mobile users cannot persist image settings for reference,
debugging, or sharing without copying from inline inspect output.

## Scope

Add one local, offline command:

- `/rp image settings export` — exports the active session's image settings as JSON.
- Resolves the active session via existing session resolution (already used by
  `image_settings()`).
- Writes one JSON file under `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "settings"`.
- Uses `normalize_image_settings(runtime.store.get_image_settings(session["id"]))`
  to produce the canonical settings dict.
- Returns a compact response with quoted `MEDIA:"<path>"`.
- Add generated help and README Core command visibility.
- Add focused offline tests.

## Non-goals / Boundaries

This phase does not add image safety export, image style export, model profile
export, image history export, or any bulk/batch export.

No schema, card/session/message mutation, prompt/debug/context-budget behavior,
provider/model routing, generation, credentials, retrieval/vectorization,
content-mode, media/TTS/image provider behavior, archive/import workflow,
automatic extraction, minors/underage, safety-bypass, plugin registration, or
protected Hermes core behavior changes are in scope.

Do not edit `run_agent.py`, `cli.py`, `gateway/run.py`,
`src/hermes_tavern/runtime.py`, DB files, importer files,
provider/model/generation/prompt files, `plugins/**`, or `build/lib/**`.

## Proposed Design

Current noun layer:

- Image settings are stored per-session in `image_settings(session_id, settings_json, updated_at)`.
- `TavernStore.get_image_settings(session_id)` returns the parsed settings dict.
- `normalize_image_settings()` produces the canonical merged settings.
- `/rp image settings` already resolves the active session and inspects settings.
- Session and project exports already use local files plus quoted `MEDIA:"..."`.

Change:

- Add `export` subcommand to the existing `image_settings()` handler branch in
  `runtime_images.py`.
- The export helper resolves the active session, calls `get_image_settings()`,
  normalizes, writes UTF-8 JSON to the exports tree, and returns bounded output.
- Export does not call image generation, model router, provider bridge, or
  mutation paths.

Flow:

1. `/rp image settings export` → `image_command()` → active session resolution
2. `image_settings(runtime, command, session)` → detects `export` subcommand
3. Resolve export path: `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "settings" / "image_settings_<sessionid>.json"`
4. Write JSON, return `"Image settings exported.\nMEDIA:\"<path>\""`

## Acceptance Criteria

- [ ] `/rp image settings export` writes a JSON file.
- [ ] JSON contains all normalized image settings fields (width, height, steps,
  cfg, sampler, style_prefix, style_suffix, negative_prompt, seed, etc.).
- [ ] File path is under the Hermes Tavern exports tree.
- [ ] Response includes quoted `MEDIA:"<path>"`.
- [ ] Not-found session returns an appropriate error (consistent with existing
  image settings inspect).
- [ ] Existing `/rp image settings` inspect is unchanged.
- [ ] `/rp image settings set/clear` are unchanged.
- [ ] No protected files changed (runtime.py, db.py, prompt.py, model_router.py, etc.).
- [ ] Python py_compile passes for changed files.
- [ ] Focused tests pass.
- [ ] Full Tavern test suite passes.
- [ ] README guard test passes.
- [ ] Git diff --check passes.
