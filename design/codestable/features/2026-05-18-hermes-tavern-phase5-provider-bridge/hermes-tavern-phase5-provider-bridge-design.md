---
feature: hermes-tavern-phase5-provider-bridge
status: implemented
created: 2026-05-18
---

# Hermes Tavern Phase 5 Provider Bridge Skeleton

## Goal

Add the first provider-bridge layer without making real LLM/network calls. Hermes Tavern should remain safe-by-default while preparing for future reuse of Hermes provider credentials and the user's preferred Opus 4.6 routing.

## Decisions

- Runtime still uses `FakeModelAdapter` for active RP replies.
- `HermesProviderAdapter` is introduced as a skeleton only. It accepts an injected resolver callable so tests can simulate Hermes `resolve_runtime_provider` without importing or calling real providers.
- Resolver payloads may include credentials internally in the future, but debug/status descriptors must omit `api_key`, `access_token`, `secret`, `token`, and `password`.
- Tavern SQLite persists only secret-free model profile metadata.
- Model status and profile listing commands must never display secrets.

## User-facing commands

- `/rp model status` — shows the active/default model route descriptor.
- `/rp model profiles` — lists configured Tavern model profiles, if any.

## Storage

Add secret-free model profile helpers:

- `save_model_profile(...)`
- `list_model_profiles()`
- `get_model_profile(id_or_name)`
- `set_session_model_profile(session_key, profile_id)`

`save_model_profile` rejects secret-like keys recursively in `raw`.

## Routing

Default descriptor remains:

- provider: `anthropic`
- model_id: `claude-opus-4-6`
- profile_name: `opus-4.6-default`
- source: `default_priority_2`

Explicit session-bound `model_profile_id` resolves to DB profile metadata with source `db_profile`.

## Non-goals

- No real external LLM call.
- No network.
- No credential persistence.
- No import of `resolve_runtime_provider` in skeleton tests.
- No changes to Hermes core gateway/CLI files.
