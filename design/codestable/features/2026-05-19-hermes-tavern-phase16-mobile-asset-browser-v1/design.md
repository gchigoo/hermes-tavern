# Hermes Tavern Phase 16 — Mobile Asset Browser v1

## Goal

Make Hermes Tavern easier to operate from Telegram/Feishu on a phone by adding short, readable asset browser commands before moving into inline buttons or richer gateway UI.

Phase 16 keeps the existing mock-first generation boundary unchanged. It only improves command ergonomics around local Tavern assets and active-session bindings.

## User commands

### `/rp assets`

A compact dashboard with:

- imported card count
- imported preset count
- imported lorebook count
- active session card/preset/lorebook bindings when a session exists
- next-command hints for browsing cards, presets, and lorebooks

### `/rp cards [limit]`

Lists character cards in a mobile-safe format:

- short card id prefix
- card name
- up to four tags
- one-line description/personality preview
- next action hints:
  - `/rp start <card>`
  - `/rp card inspect <card>`

The optional limit is clamped to 1..25 and defaults to 10.

### `/rp card inspect <card>`

Shows a mobile-safe character card summary without dumping raw JSON:

- name and short id
- tags
- description/personality/scenario previews
- first-message presence
- alternate greeting count
- system prompt override presence
- post-history instruction presence
- start/bind command hints

### `/rp card use <card>`

Rebinds the active session to another character card while preserving existing messages. If the target card has a first message, it appends that greeting as an assistant message so the switch is visible in session history.

This is intentionally explicit and does not create a new branch by itself. Users who want a branch should use Phase 15 `/rp clone [name]` first, then `/rp card use <card>`.

## Persistence changes

`TavernStore.set_session_card(session_key, card_id)` updates the active session card binding and `updated_at` timestamp. It returns `False` when no active session exists.

No schema migration is required.

## Safety and provider boundaries

- No real model/provider call is introduced.
- Mock-first/fake adapter behavior remains unchanged.
- Real provider usage remains behind the existing session-level adapter mode and live-confirm gate.
- Card inspection intentionally avoids raw JSON dumps to reduce phone noise and avoid accidentally displaying imported opaque metadata.

## Test coverage

`tests/plugins/test_hermes_tavern_mobile_browsers.py` covers:

- `/rp cards` list format, short ids, tags, and next actions
- `/rp card inspect` mobile summary and no raw JSON dump
- `/rp card use` rebind behavior and message preservation
- `/rp assets` count summary and active bindings

## Follow-up candidates

- Telegram inline keyboard support for card/session/preset actions.
- Paginated asset browsing with page cursors.
- `/rp preset inspect` and `/rp lore inspect` mobile-safe formatting parity.
- `/rp session info` and export/import flows.
