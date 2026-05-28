---
feature: hermes-tavern-phase23-mobile-export-delivery
status: approved
summary: Make /rp export mobile/gateway-friendly by returning MEDIA attachments and writing exports under profile-safe HERMES_HOME.
---

# Phase 23 — Mobile Export Delivery

## Problem

`/rp export` produced a local `file:` path only and wrote under `Path.home() / ".hermes"`, which is not profile-safe and does not let Telegram/Feishu deliver the exported Markdown/JSON as a native attachment.

## Scope

- Keep existing `/rp export [markdown|st-json]` formats and file contents.
- Write export files under `get_hermes_home() / "hermes-agent" / "exports"`.
- Return a quoted `MEDIA:"<path>"` attachment marker plus `file: <path>` so gateway platforms can upload the artifact even when `HERMES_HOME` contains spaces.
- Preserve existing message/card/swipe export behavior.

## Non-goals

- No zip bundle/export UI yet.
- No import-from-export restore command yet.
- No changes to SillyTavern card/lore/preset import semantics.

## Verification

- Focused RED/GREEN tests assert `MEDIA:` is present and equals the `file:` path.
- Focused tests assert export paths honor `HERMES_HOME`.
- Full Hermes Tavern plugin tests must remain green.
