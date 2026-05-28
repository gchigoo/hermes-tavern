---
feature: 2026-05-22-hermes-tavern-phase33-provider-media-safety
summary: Provider and media safety hardening for Hermes Tavern.
tags: [hermes-tavern, provider-safety, media, gateway]
---

# Hermes Tavern Phase 33: Provider and Media Safety Hardening

## Goal

Close remaining P1/P2 safety issues without changing user-facing command
surfaces or adding new real provider integrations:

- Image provider exceptions must not be echoed to mobile/gateway users or
  persisted in image job metadata.
- Provider/debug payload sanitization must be case-insensitive and recursive.
- Gateway export MEDIA delivery must preserve quoted paths with spaces while
  avoiding raw event JSON or secret metadata in exported files.

## Design

Image generation uses a fixed bounded failure envelope for provider exceptions:
the reply contains a generic hidden-details error plus `/rp image retry` and
`/rp image inspect` hints. Failed image jobs persist only the same sanitized
generic error string alongside existing prompt/safety metadata.

Provider debug sanitization is centralized in
`plugins/hermes_tavern/provider_bridge.py::sanitize_provider_payload`. It omits
secret-like keys case-insensitively at every nested dict level, including
`api_key`, `access_token`, `password`, `secret`, and `token`. Non-secret
metadata such as provider, model, base_url, source, and request IDs remains
visible for dry-run diagnostics.

Export delivery keeps the Phase 23 `MEDIA:"<path>"` marker contract intact so
gateway adapters can attach files whose paths include spaces. Exported Markdown
and ST JSON continue to include message content and selected swipe metadata,
but not raw message metadata JSON or event-derived secrets.

## Non-Goals

- No new live image, TTS, or model provider calls.
- No schema changes.
- No removal of existing quoted MEDIA marker support.
- No persistence of credentials or realistic test keys.
