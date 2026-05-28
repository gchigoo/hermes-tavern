---
feature: hermes-tavern-apiyi-provider-profile
status: implemented
created: 2026-05-18
---

# Hermes Tavern APIYI Provider Profile Integration

## Goal

Integrate APIYI as a third-party OpenAI-compatible relay profile for later real Hermes Tavern testing, while keeping credentials out of Tavern SQLite rows, debug output, tests, and exported artifacts.

## Documentation facts verified

- APIYI documents an OpenAI-compatible endpoint at `https://api.apiyi.com/v1`.
- APIYI supports OpenAI Chat Completions style SDK usage.
- APIYI documentation advertises a broad model hub including Claude-family models. The Tavern default profile keeps the user's preferred `claude-opus-4-6` logical model id in one profile location so it can be changed if APIYI's live model naming differs.

## Implementation

- Store the APIYI credential only in `~/.hermes/.env` as `APIYI_API_KEY`.
- Add Hermes config provider `providers.apiyi` with `base_url`, `key_env`, `api_mode`, default model, and model metadata only.
- Add Tavern-level APIYI constants and resolver support in `provider_bridge.py`.
- Add `/rp model seed apiyi` to create/update the secret-free `apiyi-opus-default` Tavern model profile.
- Add `/rp model use <profile>` to bind a model profile to the active RP session.
- Seed the local Tavern SQLite store with `apiyi-opus-default` for convenience.

## Safety

- No API key is stored in Tavern DB.
- Runtime debug/status paths sanitize provider payloads.
- The current runtime remains mock-first: even APIYI-backed sessions require explicit `hermes` mode, and real generation is still not enabled until the later live-adapter phase.
- The `/v1/models` live probe was attempted but timed out at TLS handshake from this environment; no LLM generation was attempted.
