---
feature: hermes-tavern-phase7-live-chat-adapter
status: implemented
created: 2026-05-18
---

# Hermes Tavern Phase 7 Live Chat Adapter — gated

## Goal

Add the first real OpenAI-compatible chat-completions adapter for Hermes Tavern while preventing accidental model calls and credential leakage.

## Design

- Keep `adapter_mode=fake` as the default for every session.
- Keep `adapter_mode=hermes` as explicit opt-in.
- Add a second explicit live gate: `sessions.live_confirmed INTEGER NOT NULL DEFAULT 0`.
- Real provider calls require both:
  - `/rp model mode hermes`
  - `/rp model live confirm`
- Add `/rp model live [status|confirm|off]` for per-session live access control.
- Add `HermesChatCompletionAdapter`, an OpenAI-compatible adapter that:
  - resolves provider payload at call time;
  - constructs `OpenAI(api_key=..., base_url=...)` lazily;
  - calls `client.chat.completions.create(model=..., messages=...)`;
  - extracts `choices[0].message.content`;
  - stores only sanitized debug descriptors.

## Safety

- Tests inject fake clients; no tests or smoke checks call a live network endpoint.
- Runtime returns a clear live-gate message when `adapter_mode=hermes` but `live_confirmed=0`.
- Runtime catches live provider exceptions and returns an error envelope rather than crashing the gateway hook.
- APIYI remains a secret-free Tavern profile; the real key is read from Hermes `.env` at provider resolution time.

## Verification

- CodeStable YAML validation.
- Python compile for plugin and tests.
- Direct smoke proving live gate, APIYI profile, and fake client adapter path.
- Pytest remains blocked in the current environment because pytest is not installed.
