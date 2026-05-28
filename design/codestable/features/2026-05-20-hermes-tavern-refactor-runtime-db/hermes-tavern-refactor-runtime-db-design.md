---
doc_type: feature-design
feature: 2026-05-20-hermes-tavern-refactor-runtime-db
status: approved
summary: Refactor Hermes Tavern runtime and store hotspots by extracting cohesive helper modules without changing command behavior.
tags: [hermes-tavern, refactor, runtime, sqlite]
---

# Hermes Tavern Runtime/DB Refactor

## Scope

This is a refactor-only change to reduce bloated files while preserving the existing `/rp` command surface, gateway safety, fake-provider default, and prompt-generation pipeline.

## Extracted Modules

| Module | Responsibility |
|---|---|
| `runtime_assets.py` | `/rp assets`, `/rp cards`, `/rp card inspect`, `/rp card use` |
| `runtime_model.py` | `/rp model status/profiles/seed/use/mode/live/test` |
| `runtime_sessions.py` | `/rp session info`, `/rp sessions`, `/rp switch`, `/rp rename`, `/rp archive`, `/rp clone` |
| `runtime_utils.py` | Mobile previews, module counts, card row conversion, macro context helpers |
| `db_utils.py` | UTC timestamp, row conversion, recursive secret-key validation |

## Constraints

- No command string or user-facing response changes intended.
- No schema, migration, provider-call, credential-storage, or adapter-mode changes.
- `TavernRuntime` keeps thin private wrappers for compatibility with internal callers and tests.
- DB extraction is limited to pure helpers; `TavernStore` remains a single concrete store class.
