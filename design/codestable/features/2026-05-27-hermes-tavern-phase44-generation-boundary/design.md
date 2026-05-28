---
feature: 2026-05-27-hermes-tavern-phase44-generation-boundary
summary: Extract `_generate_with_session_adapter` from `runtime.py` into `runtime_generation.py`, keeping a compatibility wrapper on `TavernRuntime`.
tags: [hermes-tavern, refactor, generation, provider]
---

# Hermes Tavern Phase 44: Generation Boundary Refactor

## Goal

Extract the `_generate_with_session_adapter` method (33 lines, lines 259-291 in `runtime.py`) into a new module `runtime_generation.py`. This is the last meaningful runtime boundary refactor — the method is the generation/provider adapter dispatch hub.

## Scope

1. Create `plugins/hermes_tavern/runtime_generation.py`
2. Move `_generate_with_session_adapter` logic to a pure function `generate_with_session_adapter(runtime, session, messages, descriptor) -> str`
3. Keep `_run_generation_pipeline` in `runtime.py` — it is the orchestration hub that calls _generate_with_session_adapter
4. Keep a compatibility wrapper on `TavernRuntime`:
   ```python
   def _generate_with_session_adapter(self, session, messages, descriptor) -> str:
       return runtime_generation.generate_with_session_adapter(self, session, messages, descriptor)
   ```

## Design

The method handles four paths:
1. **Fake adapter** — `adapter_mode != "hermes"` → delegate to `_fake_adapter.generate()`
2. **Live gate** — `live_confirmed` not set → returns safety message
3. **Hermes adapter** — lazy-init `self.hermes_adapter` from `HermesChatCompletionAdapter(HermesRuntimeProviderResolver(descriptor).resolve)`, then call `adapter.generate()`
4. **Error boundaries** — ConnectionError/TimeoutError → retryable message; NotImplementedError → "not wired yet" message; generic Exception → "provider error" message

The new module needs these imports:
- `HermesChatCompletionAdapter` from `plugins.hermes_tavern.adapters`
- `HermesRuntimeProviderResolver` from `plugins.hermes_tavern.provider_bridge`
- The `FakeModelAdapter` singleton `_fake_adapter` must be passed in or imported

`runtime.py` should import the new module and add the wrapper. The `_fake_adapter` singleton stays in `runtime.py` and is passed as a parameter or the new module imports it from runtime (which creates a circular import — better to pass it as a parameter, or move the singleton to the new module).

**Approach: pass `_fake_adapter` as a parameter**
```python
def generate_with_session_adapter(runtime, session, messages, descriptor, fake_adapter) -> str:
```

The wrapper in `runtime.py` passes `self._fake_adapter` (or the module-level `_fake_adapter`).

## Non-Goals

- No changes to the generation pipeline logic itself
- No changes to provider selection, model routing, or adapter internals
- No DB schema changes
- No prompt compiler changes

## Files

| Action | File |
|--------|------|
| Create | `plugins/hermes_tavern/runtime_generation.py` |
| Modify | `plugins/hermes_tavern/runtime.py` |
