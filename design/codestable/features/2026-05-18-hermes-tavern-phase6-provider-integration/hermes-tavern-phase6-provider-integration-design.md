---
feature: hermes-tavern-phase6-provider-integration
status: implemented
created: 2026-05-18
---

# Hermes Tavern Phase 6 Provider Integration — Mock First

## Goal

Introduce the real Hermes provider-resolution boundary while keeping runtime default behavior safe, deterministic, and network-free. This phase prepares Tavern to reuse Hermes provider credentials later without making real calls yet.

## Scope

- Add a dependency-injectable `HermesRuntimeProviderResolver` wrapper around `hermes_cli.runtime_provider.resolve_runtime_provider`.
- Keep the import lazy so loading Hermes Tavern does not touch provider credentials.
- Add sanitized provider payload helpers for debug/status paths.
- Add per-session model adapter mode:
  - `fake` — default, deterministic `FakeModelAdapter`.
  - `hermes` — provider resolution path selected, but real generation still raises/returns not-yet-wired message.
- Add `/rp model mode`, `/rp model mode fake`, `/rp model mode hermes`.
- Active messages continue using fake mode unless the session explicitly selects `hermes`.

## Non-goals

- No real LLM call.
- No network.
- No credential persistence.
- No core Hermes gateway/CLI/agent modifications.
- No default switch to paid/API model usage.

## Safety requirements

- Adapter mode defaults to `fake` for every new or migrated session.
- Hermes provider resolver is only invoked when `adapter_mode == 'hermes'`.
- Debug/status output must omit `api_key`, `access_token`, `secret`, `token`, and `password`.
- Tests must inject fake resolver/adapter and must not call real provider code.

## Files

- `plugins/hermes_tavern/provider_bridge.py`
- `plugins/hermes_tavern/db.py`
- `plugins/hermes_tavern/runtime.py`
- `tests/plugins/test_hermes_tavern_provider_bridge.py`
- `tests/plugins/test_hermes_tavern_runtime.py`
