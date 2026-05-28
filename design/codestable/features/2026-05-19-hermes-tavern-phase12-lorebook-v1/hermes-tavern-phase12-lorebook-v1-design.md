# Hermes Tavern Phase 12 Lorebook v1 Design

## Scope

Add a mock-first SillyTavern World Info / lorebook slice to the existing Hermes Tavern plugin without touching Hermes core gateway/agent files and without real network or model calls.

## Requirements

- Import local ST world-info JSON shapes: `entries` dict, `entries` list, or top-level list.
- Preserve raw imported lorebook/entry data while normalizing title/content/keys/enabled/constant/regex/order/priority/probability fields.
- Persist lorebooks and entries in SQLite with idempotent migrations.
- Bind one active lorebook to an RP session.
- Match lore entries by constant, keyword, or regex with debug exclusion reasons.
- Inject matched lore entries into the existing Prompt Compiler as `PromptModule`s.
- Add gateway commands under `/rp lore` for import/list/use/test/debug.

## Non-goals

- No URL/file-host downloader.
- No vector matching.
- No recursive scanning or timed effects yet.
- No real LLM/provider generation changes.

## Files

- `plugins/hermes_tavern/importers/lorebooks.py`
- `plugins/hermes_tavern/lorebook.py`
- `plugins/hermes_tavern/db.py`
- `plugins/hermes_tavern/runtime.py`
- `tests/plugins/test_hermes_tavern_lorebooks.py`
- `tests/plugins/test_hermes_tavern_lore_runtime.py`

## Verification

- `python -m py_compile plugins/hermes_tavern/*.py plugins/hermes_tavern/importers/*.py tests/plugins/test_hermes_tavern_*.py`
- `python -m pytest tests/plugins/test_hermes_tavern_lore*.py -q -o 'addopts='` when pytest is installed.
- Direct smoke checks are acceptable when pytest is unavailable in the active venv.
