---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase163-style-sample-json-export"
date: "2026-06-07"
summary: >
  Phase 163 adds one bounded /rp style sample export <style-sample-id> JSON export command
  for any stored novel style sample, following the Phase 149–162 export pattern.
  Resolves style sample by integer ID, exports style sample metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, style-sample, novel, offline, export, json]
owner: codestable-cron
---

# Phase 163: Style Sample JSON Export by ID

## Background

Phases 149–162 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, timeline, relationships, character states,
locations, organizations, and plot threads. Each exports one stored asset to a profile-safe
local JSON file and returns `file:` plus quoted `MEDIA:"<path>"`. Phase 135 added
`/rp style sample ...` CRUD commands but there is no way to export a single style
sample as a standalone JSON file.

## Scope

Add one export branch to the existing style sample command family:

- `/rp style sample export <style-sample-id>`
- Resolve `<style-sample-id>` as an integer ID through existing `get_style_sample(style_sample_id)`.
- Read full style sample metadata (id, project_id, label, sample_text, created_at, updated_at).
- Build a JSON export payload with style sample metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "style-samples"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `style_command()` dispatcher (after the `delete` case).
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change style sample schema/index/migration code, style sample ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk style sample export, style sample import, style sample merge,
or style sample auto-extraction.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "style_sample_id": <int>,
  "project_id": <int>,
  "label": "<string>",
  "sample_text": "<string>",
  "created_at": "<ISO8601>",
  "updated_at": "<ISO8601>"
}
```

### Export path

```
{get_hermes_home()}/plugins/hermes-tavern/exports/style-samples/style_sample_{id}.json
```

### Command dispatch

Add `export` case to `style_command()` in `runtime_novel.py`, after the `delete` case:
```python
if subcommand == "export":
    return style_sample_export(runtime, command)
```

### Error handling

- Missing args: return `_STYLE_SAMPLE_USAGE`
- Non-integer ID: return `_STYLE_SAMPLE_USAGE`
- Non-positive ID: return `_STYLE_SAMPLE_USAGE`
- Style sample not found: return `No style sample found: <id>`

### Files

- `src/hermes_tavern/runtime_novel.py` — add `style_sample_export()` + `export` branch in `style_command()`
- `src/hermes_tavern/commands.py` — update help_lines
- `README.md` — update Core commands table
- `tests/test_hermes_tavern_novel_runtime.py` — add focused tests
- `tests/test_hermes_tavern_readme_docs.py` — update (if needed)

### Verification

- py_compile on changed source and test files
- Targeted pytest on `test_hermes_tavern_novel_runtime.py` + `test_hermes_tavern_readme_docs.py`
- Full Tavern test suite
- Protected files diff guard (empty)
- `git diff --check` (clean)
