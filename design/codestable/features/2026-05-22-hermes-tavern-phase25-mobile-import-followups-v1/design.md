---
feature: 2026-05-22-hermes-tavern-phase25-mobile-import-followups-v1
summary: Add compact next-action hints after successful mobile and explicit Hermes Tavern imports.
tags: [hermes-tavern, mobile, imports, gateway, runtime]
---

# Hermes Tavern Phase 25: Mobile Import Follow-up Actions v1

## Goal

After a successful `/rp ... import`, mobile users should be able to inspect,
bind, or start with the imported asset immediately without remembering or
copying a full ID from the response.

## Scope

- Card import success replies include:
  - `inspect: /rp card inspect <short-id>`
  - `use: /rp card use <short-id>`
  - `start: /rp start <short-id>`
- Preset import success replies include:
  - `use: /rp preset use <short-id>`
  - `inspect: /rp preset inspect <short-id>`
- Lorebook import success replies include:
  - `use: /rp lore use <short-id>`
  - `inspect: /rp lore inspect <short-id>`
- Persona import success replies keep the existing use hint and add:
  - `inspect: /rp persona inspect <short-id>`

The same success formatter is used for explicit paths and no-path attachment
imports, so both mobile attachment imports and CLI-style explicit imports get
the same compact follow-up actions.

## Non-Goals

- No DB schema changes.
- No importer behavior changes.
- No network calls or remote attachment downloads.
- No raw JSON dumps or expanded imported content in success replies.
- No platform-specific buttons or rich gateway UI.

## Design

The runtime already stores each imported asset before constructing the success
reply. Phase 25 appends deterministic command hints using the existing saved ID
prefixes. Store lookup paths already accept names and ID prefixes, so short IDs
are compact and unambiguous for the immediate post-import command flow.

Card import output lives in `plugins/hermes_tavern/runtime_assets.py`; preset,
lorebook, and persona import output lives in `plugins/hermes_tavern/runtime.py`.
Only reply text is changed.

## Acceptance

- Focused RED tests fail against the Phase 24 behavior for missing hints.
- Focused GREEN tests cover card, preset, lorebook, and persona import success
  replies.
- Explicit preset and lorebook path imports include the same hints as no-path
  attachment imports.
- Imported content and raw JSON do not appear in success replies.
- Existing Hermes Tavern tests remain green.
