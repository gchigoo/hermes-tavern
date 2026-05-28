# Hermes Tavern

A Hermes Agent plugin for character-based roleplay (RP) with SillyTavern compatibility.

Extracted from the hermes-agent monorepo to an independent project.

## Structure

```
hermes-tavern/
├── src/hermes_tavern/    # Plugin source code
├── tests/                # Test suite (pytest)
├── design/               # Design docs, CodeStable plans, architecture decisions
│   ├── codestable/       # Phase-by-phase feature designs & checklists
│   └── plans/            # Implementation plans
├── patches/              # Core hermes-agent diffs this plugin depends on
└── README.md
```

## Origin

This plugin was developed as part of the [hermes-agent](https://github.com/nousresearch/hermes-agent) monorepo (`tavern-dev` branch), spanning 40+ feature phases from May 2026.

## Dependencies

- Hermes Agent (the plugin system and gateway hooks)
- The patches in `patches/` may need to be applied to a compatible hermes-agent version
