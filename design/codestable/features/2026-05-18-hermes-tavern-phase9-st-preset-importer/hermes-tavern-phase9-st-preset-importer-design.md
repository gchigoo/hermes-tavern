---
feature: hermes-tavern-phase9-st-preset-importer
status: implemented
created: 2026-05-18
---

# Hermes Tavern Phase 9 ST Preset Importer v1

## Goal

Support SillyTavern-style preset/raw prompt import as an asset-compatibility feature while ensuring jailbreak/no-boundaries modules are preserved only as disabled imported assets and are not active system prompts.

## Scope

- Import raw text presets and JSON presets.
- Extract prompt modules from common ST-style JSON keys such as `prompts`, `prompt_order`, or `modules`.
- Run every module through `preset_safety.classify_preset_text`.
- Preserve original module content in the Tavern preset/module tables for local compatibility and inspection.
- Set `enabled=0` for `jailbreak` and `disallowed` modules even when the source file says enabled.
- Add runtime commands:
  - `/rp preset import <file>`
  - `/rp preset list`
  - `/rp preset inspect <preset>`

## Boundary

This phase supports ST asset import/inspection, including original jailbreak-like prompt text as disabled local assets.  It does not enable those modules in Prompt Compiler, does not optimize them, and does not implement provider safety bypass.  Role-card settings and safe writing-style modules remain importable.

## Verification

- CodeStable YAML validation.
- `py_compile` for plugin and tests.
- Direct smoke: import a raw jailbreak-like preset; verify it is stored disabled and inspectable.
- Pytest remains unavailable in the current venv.
