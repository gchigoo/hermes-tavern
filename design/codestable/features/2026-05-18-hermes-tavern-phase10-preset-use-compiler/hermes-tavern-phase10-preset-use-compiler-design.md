---
feature: hermes-tavern-phase10-preset-use-compiler
status: implemented
created: 2026-05-18
---

# Hermes Tavern Phase 10 Preset Use + Prompt Compiler Integration

## Goal

Make imported SillyTavern preset modules usable in active RP sessions while keeping jailbreak/disallowed modules disabled and outside the Prompt Compiler.

## Scope

- Add `sessions.preset_id` migration.
- Add `TavernStore.set_session_preset(session_key, preset_id)`.
- Add `/rp preset use <preset>` command.
- Resolve active session preset modules during active-message generation and `/rp debug prompt`.
- Inject only enabled `safe` modules into Prompt Compiler by default.
- Inject enabled `adult_fiction` modules only when the session content mode is `adult-fiction`.
- Never inject `jailbreak` or `disallowed` modules, even if the original ST preset set them enabled.

## Compatibility boundary

Hermes Tavern now supports the ST flow of importing preset text, inspecting modules, and binding a preset to a session.  This is asset compatibility, not jailbreak activation.  Risky modules remain preserved as local imported assets for migration/inspection but do not become active system prompts.

## Verification

- YAML validation.
- `py_compile` for plugin and tests.
- Direct smoke imports a mixed ST preset, binds it to an active card session, verifies safe module appears in debug prompt, and verifies jailbreak text does not appear.
- Pytest remains unavailable in current venv.
