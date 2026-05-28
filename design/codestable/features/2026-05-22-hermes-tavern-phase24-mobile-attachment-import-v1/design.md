---
feature: hermes-tavern-phase24-mobile-attachment-import-v1
status: approved
summary: Complete mobile attachment import fallback for preset, lorebook, and persona assets.
---

# Phase 24 — Mobile Attachment Import v1

## Problem

Telegram, Feishu, and similar gateway users can attach files and send short
commands more easily than they can paste local paths. Phase 23 made export
mobile-safe; import parity still required explicit paths for presets, lorebooks,
and personas even when the gateway event already contained local attachment
paths in `event.media_urls`.

## Scope

- Preserve explicit path behavior for `/rp preset import <file>`,
  `/rp lore import <file>`, and `/rp persona import <file>`.
- When no path is provided, resolve exactly one local attachment from
  `event.media_urls`.
- Preset imports accept local `.json` and `.txt` attachments.
- Lorebook imports accept local `.json` attachments only.
- Persona imports accept local `.json` and `.txt` attachments.
- Empty and ambiguous attachment cases return compact mobile-safe guidance.

## Non-goals

- No network download support for import URLs.
- No broad gateway attachment architecture changes.
- No raw JSON dumps or secret persistence changes.
- No change to card import semantics.

## Verification

- RED tests first for no-path preset, lorebook, and persona attachment imports.
- Focused GREEN tests for exact-one, none, multiple, and remote-URL ignored cases.
- Full Hermes Tavern plugin test glob must remain green.
- `py_compile` must pass for touched runtime/test files.
- Checklist YAML must validate.
