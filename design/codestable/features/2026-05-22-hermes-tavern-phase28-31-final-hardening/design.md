---
feature: 2026-05-22-hermes-tavern-phase28-31-final-hardening
summary: Final Hermes Tavern hardening for provider failures, placeholder speech commands, and mobile-safe edge cases.
tags: [hermes-tavern, hardening, provider-recovery, tts, mobile]
---

# Hermes Tavern Phases 28, 30, and 31: Final Hardening

## Goal

Keep Hermes Tavern safe on messaging clients when providers, malformed gateway
events, or extreme command arguments fail. Add the placeholder `/rp speak` and
`/rp voice` command surface without making network calls or changing the DB
schema.

## Scope

- Provider recovery around live adapter generation.
- `/rp speak` placeholder response with a `MEDIA:` marker.
- `/rp voice [on|off]` in-memory per-session auto-speak flag.
- Top-level command exception boundary.
- Limit clamping for `/rp history` and `/rp cards` at 50.
- Malformed event/session-key handling.
- Help text and focused regression tests.

## Design

Provider recovery remains inside `_generate_with_session_adapter`. Explicit
`ConnectionError` and `TimeoutError` failures return a concise retryable
provider-unavailable message. The existing generic provider catch-all remains as
the final boundary for unexpected provider exceptions.

Speech is intentionally a command/UX placeholder. `/rp speak` looks up the last
assistant reply in the active session, but does not call a TTS provider. It
returns a compact status line plus `MEDIA:tts-placeholder` so gateway delivery
shape can be exercised later. `/rp voice on|off` stores an in-memory session key
flag only; no persistence is added.

The top-level `/rp` command handler wraps runtime dispatch and returns
`[Hermes Tavern: internal error]` for unexpected plugin exceptions. Normal usage
errors still return command-specific help strings. Session identity extraction
guards malformed event/source attributes so bad gateway payloads do not crash
the plugin.

## Non-Goals

- No database schema changes.
- No network calls or real TTS integration.
- No image-generation logic changes.
- No rewrite of the generation pipeline.
