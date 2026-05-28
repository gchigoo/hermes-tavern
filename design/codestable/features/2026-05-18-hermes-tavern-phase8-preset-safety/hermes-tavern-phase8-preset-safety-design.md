---
feature: hermes-tavern-phase8-preset-safety
status: implemented
created: 2026-05-18
---

# Hermes Tavern Phase 8 Preset Safety Classification

## Goal

Safely handle imported ST-style preset/prompt modules, including jailbreak/no-boundaries prompts, without integrating or optimizing those prompts as active Hermes Tavern system instructions.

## Design

Add a lightweight classifier for imported preset text:

- `safe`: ordinary style/format controls; may be enabled by default.
- `adult_fiction`: consenting-adult fictional writing signals; may be enabled only under explicit content-mode workflows.
- `jailbreak`: instruction override, no-disclaimer, unconditional compliance, anti-ethics, flagged-content override, or jailbreak markers; disabled by default.
- `disallowed`: no-boundaries modules, sexual violence/non-consent, sexualized real-person/celebrity framing, bestiality, etc.; never enabled as Tavern system prompts.

The classifier stores only labels/reasons; it does not store the unsafe prompt sample.

## Product stance

Hermes Tavern can learn from ST preset structure:

- modular prompt order;
- writing style controls;
- character/lore/persona slots;
- anti-repetition guidance;
- length/pacing controls.

It must not import no-boundaries jailbreak text into the active system prompt.  Unsafe modules can be retained as disabled metadata for user review later, but not activated by default or used to bypass provider rules.

## Verification

- `py_compile` for plugin and tests.
- direct smoke for safe/adult/jailbreak/disallowed classification.
- pytest remains unavailable in current environment.
