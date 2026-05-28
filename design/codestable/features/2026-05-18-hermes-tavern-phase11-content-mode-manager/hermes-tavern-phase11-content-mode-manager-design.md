---
feature: hermes-tavern-phase11-content-mode-manager
status: implemented
created: 2026-05-18
---

# Hermes Tavern Phase 11 Content Mode Manager

## Goal

Add explicit per-session content mode management so adult-fiction preset modules are never injected into safe sessions by accident.

## Scope

- Add `TavernStore.set_session_content_mode(session_key, content_mode)` with allowed values `safe` and `adult-fiction`.
- Add `/rp content mode`, `/rp content mode safe`, and `/rp content mode adult-fiction`.
- Update `/rp status` and `/rp debug prompt` to show the active content mode.
- Keep `_session_preset_modules(session)` as the single Prompt Compiler guard: `adult_fiction` modules require `content_mode == 'adult-fiction'`; jailbreak/disallowed modules remain excluded.

## Boundary

This phase introduces a product-level adult-fiction workflow flag. It does not create a jailbreak mode, no-boundaries mode, or provider-policy bypass. The mode is for consenting-adult fictional writing controls and for safe prompt-module routing.

## Verification

Direct smoke imports an adult-fiction style preset, binds it to a session, verifies the adult module is absent in safe mode, appears after `/rp content mode adult-fiction`, and disappears again after switching back to safe.
