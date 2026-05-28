---
feature: 2026-05-22-hermes-tavern-phase26-session-quick-actions-v1
summary: Resolve `last` in Hermes Tavern asset commands to the most recently imported asset of that type.
tags: [hermes-tavern, mobile, imports, quick-actions, runtime]
---

# Hermes Tavern Phase 26: Session Quick Actions v1

## Goal

Mobile users can type `last` instead of copying an asset ID after importing a
card, preset, lorebook, or persona in the current runtime session.

## Scope

- `/rp start last`
- `/rp card inspect last`
- `/rp card use last`
- `/rp preset inspect last`
- `/rp preset use last`
- `/rp lore inspect last`
- `/rp lore use last`
- `/rp persona inspect last`
- `/rp persona use last`

## Design

`TavernStore` keeps four in-memory IDs for the current Python process:
`_last_card_id`, `_last_preset_id`, `_last_lorebook_id`, and
`_last_persona_id`. The IDs are updated by the corresponding `save_*` methods
and can also be set explicitly by runtime import handlers.

The existing `get_card`, `get_preset`, `get_lorebook`, and `get_persona`
methods treat a case-insensitive `last` reference as a lookup by the matching
in-memory ID. This keeps command handlers on the same resolution path as exact
ID, name, and prefix lookups.

No database schema is changed. The quick-action state is intentionally
session-lifetime only; restarting Hermes clears `last`.

## UX

If `last` is used before an asset of that type has been imported in the current
runtime session, the command returns a short actionable message:

`No card has been imported yet. Import a card first: /rp card import <file>`

Equivalent messages are used for presets, lorebooks, and personas.

## Non-Goals

- No persistent last-used state.
- No database migration.
- No remote attachment fetching.
- No raw imported JSON or content dumps in replies.
