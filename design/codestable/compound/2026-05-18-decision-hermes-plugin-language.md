---
name: Hermes plugin language policy — Python-first, Rust-as-shim-only
description: Records the decision that native Hermes plugins must be Python entrypoint plugins; Rust is not supported as a first-class plugin language yet
type: decision
date: 2026-05-18
status: accepted
---

# Decision: Hermes plugin language policy

**Decision:** Native Hermes plugins are Python entrypoint plugins. Rust is not a supported first-class plugin language for gateway/runtime core at this time.

## Rule

A Hermes plugin **must** be a Python package that:
1. Contains `plugin.yaml` (plugin metadata, `kind: backend`).
2. Contains `__init__.py` with a `register(ctx) -> None` function that calls `ctx.register_hook(...)`.

Rust code is permitted **only** as a performance-sensitive isolated component, behind one of:
- **Subprocess shim**: Python spawns a compiled Rust binary via `subprocess`/`asyncio.create_subprocess_exec`, communicates over stdin/stdout/JSON.
- **PyO3 binding**: A compiled `.so`/`.pyd` extension loaded via `import` from Python.

Rust must **not** be the entrypoint for gateway dispatch, runtime logic, session management, or any code that calls back into Hermes core APIs.

## Why

**Why:** The Hermes plugin loader (`hermes_cli/plugins.py`) discovers and loads plugins as Python modules. There is no Rust FFI, no WASM runtime, and no Cargo build step in the Hermes CI/CD pipeline. Introducing Rust as a first-class plugin language would require:
- A Cargo toolchain dependency for all contributors.
- A build step before any test run.
- A new plugin loading protocol.
None of these are justified for the current development phase of Hermes Tavern.

Rust-as-subprocess or Rust-as-PyO3 is acceptable for hot paths (e.g. token counting, GGUF inference, vector indexing) where Python overhead is measurable, but only when the Python side fully owns the entrypoint and lifecycle.

## How to apply

- When evaluating a feature that proposes Rust: ask whether Python's overhead is the actual bottleneck. If not, stay Python.
- If Rust performance is justified: design a subprocess or PyO3 boundary first, document it as a separate component, ensure Python tests cover the integration boundary.
- Gateway hook, runtime command handling, DB access, and prompt compilation: Python only.
- Acceptable Rust use cases (future): token counter for context budget, embedding model inference, GGUF loader for local model router.
