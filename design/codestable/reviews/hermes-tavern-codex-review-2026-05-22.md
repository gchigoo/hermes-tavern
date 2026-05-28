# Hermes Tavern Code Review - 2026-05-22

## Executive Summary

Hermes Tavern is feature-rich and has unusually strong unit coverage for a plugin at this stage: the scoped suite passes with `397 passed` using `pytest tests/plugins/test_hermes_tavern_*.py`. The architecture is also directionally sound: gateway interception is isolated in `gateway_hook.py`, identity derivation is separate, model credentials are resolved lazily, and prompt/lore/macro/model/image code has been split into focused modules.

I would not mark it complete for production gateway use yet. Two issues are completion blockers: import commands can read arbitrary local paths supplied by a gateway user, and session switching resolves target sessions globally rather than within the caller's scope. After those are fixed, the remaining work is mostly refactoring and hardening: shrink `runtime.py`/`db.py`, centralize command parsing/pagination, sanitize image-provider errors like model-provider errors, add indexes/busy timeout/WAL for SQLite, and add tests around the newly closed security boundaries.

## What Looks Solid

- Gateway routing is small and understandable. `plugins/hermes_tavern/gateway_hook.py:52` handles `/rp` commands and active sessions, returns `skip` only when Tavern actually handled the event, and catches unexpected hook errors before they can break normal gateway dispatch (`gateway_hook.py:76`). Tests cover no-event, non-RP fallthrough, command interception, async send, active-message routing, and store exceptions in `tests/plugins/test_hermes_tavern_gateway.py` and `tests/plugins/test_hermes_tavern_gateway_hook.py`.

- Session identity is deterministic and defensive. `session_key_from_event()` in `identity.py` tolerates malformed/missing fields via `_safe_attr()`, and `tests/plugins/test_hermes_tavern_identity.py` plus `test_hermes_tavern_plugin_hardening.py::test_malformed_event_does_not_crash` cover this.

- Provider credentials are mostly handled correctly. `HermesRuntimeProviderResolver` resolves at runtime, `TavernStore.save_model_profile()` rejects secret-like keys through `_assert_no_secret_keys()`, `model_status()`/`model_test()` only expose secret-free route metadata, and `validate_provider_base_url()` rejects non-HTTPS/private/loopback URLs without echoing rejected URLs. Coverage exists in `tests/plugins/test_hermes_tavern_provider_bridge.py`, `test_hermes_tavern_adapters.py`, and `test_hermes_tavern_runtime.py`.

- Model-provider failure behavior is production-shaped. `_generate_with_session_adapter()` catches connection/timeouts separately and catches generic provider exceptions without forwarding `str(exc)` (`runtime.py:730`). `test_runtime_live_provider_exception_does_not_leak_secret_detail` verifies secret-bearing exception details are not returned.

- Pagination and mobile outputs are broadly covered. History, sessions, personas, cards, lore inspect, image history, debug prompt, and memory list clamp limits and emit navigation hints. Tests include `test_hermes_tavern_mobile_browsers.py`, `test_hermes_tavern_session_browser.py`, `test_hermes_tavern_turn_controls_mobile.py`, `test_hermes_tavern_plugin_hardening.py`, and related runtime tests.

- Prompt assembly is testable and bounded by module boundaries. `PromptCompiler.compile()` (`prompt.py:37`) expands allowlisted macros and assembles modules/history/user text. Lore matching excludes invalid regexes rather than raising (`lorebook.py:144`). Tests cover prompt compiler, macros, lorebook runtime, content mode filtering, persona, author note, memory, and e2e fake-adapter flow.

- No unsafe `eval`, `exec`, or subprocess usage was found under `plugins/hermes_tavern`. SQL calls are parameterized except for internal fixed table/column strings in `_get_row_by_id()` and SQL fragments assembled from non-user-controlled booleans.

## P0 Blockers

1. Arbitrary local file import from gateway commands.

   - Files/functions: `runtime_assets.card_import()` (`runtime_assets.py:122`), `TavernRuntime._preset_import()` (`runtime.py:949`), `_lore_import()` (`runtime.py:1061`), `_persona_import()` (`runtime.py:1358`), importers in `plugins/hermes_tavern/importers/*.py`.
   - Problem: Explicit import arguments are converted with `Path(...).expanduser()` and read directly. Preset and persona imports are especially risky because they accept arbitrary text, not just structured JSON; `_preset_import()` calls `import_preset_file(path)` after only `path.exists()` (`runtime.py:961`), and `_persona_import()` does the same (`runtime.py:1370`). A gateway user who can send `/rp persona import /some/local/file` or `/rp preset import /some/local/file` can cause the process to read local files and then reveal previews through `/rp persona inspect`, `/rp preset inspect`, or prompt use. Card import also allows explicit URL/path loading (`runtime_assets.py:139`), though format parsing narrows what successfully imports.
   - Risk: Local file disclosure and unintended persistence of host-local content into Tavern SQLite, prompts, exports, or model calls.
   - Proposed fix: Split import sources by trust boundary. For gateway events, allow only gateway-supplied attachment temp paths that are explicitly marked as safe by the platform adapter, or paths under a dedicated Tavern import staging directory. For CLI/local-only usage, keep explicit filesystem paths behind a platform/trust check. Add size limits to all local imports, not just remote cards.
   - Expected tests: Gateway `/rp preset import /etc/hosts` and `/rp persona import /tmp/secret.txt` should be rejected unless the path is an approved attachment. Approved attachment path still imports. Oversized local files fail with a bounded message. Rejected path should not be echoed beyond basename.

2. Session switching is not scoped to the caller.

   - Files/functions: `runtime_sessions.switch()` (`runtime_sessions.py:99`), `TavernStore.get_session_by_id_prefix()` (`db.py:1435`), `TavernStore.switch_to_session()` (`db.py:1445`).
   - Problem: `/rp switch <session-id>` looks up a session by global ID prefix (`SELECT * FROM sessions WHERE id LIKE ? LIMIT 1`) and `switch_to_session()` activates that target under the caller's `current_session_key` without verifying `target.scope_key` belongs to the caller. In contrast, session listing is correctly scoped through `count_sessions_for_scope()`/`list_sessions_for_scope()` (`db.py:1258`, `db.py:1271`).
   - Risk: If a user learns or guesses a session prefix, they can attach another user's session to their own key. The IDs are UUIDs, but the command advertises short prefixes, and this is still a broken authorization boundary.
   - Proposed fix: Replace `get_session_by_id_prefix(prefix)` for gateway switching with `get_session_by_id_prefix_for_scope(scope_key, prefix, include_archived=True)`. Enforce scope again inside `switch_to_session()` or expose a scoped `switch_to_session(scope_key, current_session_key, target_session_id)`.
   - Expected tests: User A cannot switch to User B's session by full ID or prefix. User A can switch to own cloned/archived sessions. Ambiguous prefixes in the same scope return a clear error rather than first match.

## P1 Refactor/Hardening

1. `runtime.py` is still the main maintenance bottleneck.

   - Evidence: `runtime.py` is 2,261 lines and still owns command dispatch, memory, note, persona, lore, preset, image, export, speech placeholder, and generation orchestration. The dispatch ladder starts at `runtime.py:176`, while image handling alone spans roughly `runtime.py:1660-2084`.
   - Risk: New command variants require touching a very large class; error handling and parsing patterns already diverge across assets/presets/lore/persona/memory/image.
   - Proposed fix: Continue the existing extraction pattern used by `runtime_assets.py`, `runtime_sessions.py`, and `runtime_model.py`. Move `runtime_image.py`, `runtime_memory.py`, `runtime_persona.py`, `runtime_lore.py`, `runtime_preset.py`, and `runtime_export.py` behind a command registry table rather than the current if-chain.
   - Tests: Existing command tests should pass unchanged; add one registry dispatch test that asserts every help-listed command has a handler.

2. `db.py` mixes migrations, schemas, and all CRUD in one 1,770-line class.

   - Evidence: `TavernStore` handles migration (`db.py:69`), core sessions/messages, assets, model profiles, memory, sessions browser, image jobs, and image styles.
   - Risk: Persistence changes are hard to review and hard to test in isolation; cross-cutting changes can accidentally affect unrelated tables.
   - Proposed fix: Keep one SQLite connection boundary but split methods into small store modules or mixins: `sessions_store`, `asset_store`, `prompt_store`, `image_store`, `model_store`, `memory_store`. Move schema DDL into versioned migration helpers.
   - Tests: Migration idempotence tests remain; add a smoke test that a fresh DB can construct all repository classes over the same path.

3. Image-provider exception text is returned to users and stored.

   - Evidence: `_image_generate()` catches `Exception as exc`, stores `str(exc)`, and returns `f"Hermes Tavern image generation failed: {exc}"` (`runtime.py:2013`). The tests currently assert the selected placeholder error is shown in `test_image_provider_list_use_and_safe_failure`.
   - Risk: A real image provider exception can contain API keys, signed URLs, local paths, request bodies, or internal hostnames. The model-provider path already avoids this leak.
   - Proposed fix: Mirror `_generate_with_session_adapter()`: return a fixed bounded user message, store a sanitized error code/category, and log full details only to the server log. Keep provider-specific friendly messages by mapping known local `NotImplementedError`/configuration errors to safe strings.
   - Tests: Inject an image provider raising `RuntimeError("api_key=... https://internal ...")`; assert response and stored `metadata_json` do not contain the secret/URL.

4. Provider debug sanitization is case-sensitive in `adapters.py`.

   - Evidence: `HermesProviderAdapter._safe_descriptor()` filters `if k not in _SECRET_FIELDS` (`adapters.py:65`), while `sanitize_provider_payload()` correctly uses `k.lower()`.
   - Risk: Resolver payloads with `API_KEY`, `Access_Token`, or mixed-case secret fields would survive in `last_debug_descriptor`.
   - Proposed fix: Change adapter sanitization to `k.lower() not in _SECRET_FIELDS` and reuse the provider bridge sanitizer to avoid duplicate logic.
   - Tests: Extend `test_hermes_provider_adapter_debug_descriptor_omits_secrets` with mixed-case keys.

5. SQLite should get basic production tuning and indexes.

   - Evidence: Tables frequently query `messages(session_id, created_at)`, `sessions(session_key, status)`, `sessions(scope_key, status, updated_at)`, `session_memory_facts(session_id)`, `lorebook_entries(lorebook_id)`, and `image_jobs(session_id, created_at)` but schema creation does not define indexes. Connections only enable foreign keys (`db.py:62`).
   - Risk: Large histories, lorebooks, and mobile pagination will degrade. Concurrent gateway activity can also hit SQLite busy errors.
   - Proposed fix: Add indexes for the query paths above, set `PRAGMA busy_timeout`, consider WAL mode for the Tavern DB, and add simple explain/query-count regression tests around history/session/image pagination.
   - Tests: Insert thousands of messages/jobs/sessions and assert paginated reads complete within a reasonable bound. Verify indexes exist after migration.

6. Lore matching can become expensive with user-supplied regex entries.

   - Evidence: `_any_key_matches()` runs `re.search(key, haystack, flags=re.IGNORECASE)` for every regex key (`lorebook.py:144`) against recent history and current text; invalid regexes are handled, but catastrophic regex backtracking is not bounded.
   - Risk: A malicious or accidental regex lorebook entry can stall a gateway worker.
   - Proposed fix: For phase one, disable regex entries by default for imported untrusted lorebooks or add a per-entry regex length/complexity gate. Longer term, use the third-party `regex` module with timeout if already acceptable as a dependency, or precompile with conservative validation.
   - Tests: Import lore entries with pathological regexes and assert `lore test`/active-message prompt assembly fails closed quickly.

7. Prompt compilation uses fixed recent-history windows and no true context budget.

   - Evidence: active messages always load 20 recent messages (`runtime.py:336`), lore sees `history[-12:]` (`runtime.py:611`), and `PromptCompiler.compile()` only estimates token budget after assembly (`prompt.py:85`) without pruning to the resolved model context window.
   - Risk: Large cards/presets/lore/personas/notes/history can exceed provider context, especially live mode.
   - Proposed fix: Add a prompt budgeter after module collection and before rendering. Use model profile `context_window`, reserve completion tokens, and prune lower-priority modules/history deterministically.
   - Tests: Oversized card + preset + lore + history should fit a small artificial context window and report what was pruned in debug prompt.

## P2 Polish/Future Work

- Replace ad hoc pagination parsing with shared helpers. `_parse_ref_limit_page()` handles one shape (`runtime.py:72`), while cards, sessions, history, memory, persona, image history, debug prompt, and lore inspect each parse their own arguments. A shared `parse_pagination(args, default, max)` would reduce edge-case drift.

- Persist or clearly scope ephemeral quick-action and voice state. `_last_card_id`/`_last_preset_id`/`_last_lorebook_id`/`_last_persona_id` live only on `TavernStore` (`db.py:34`) and voice state lives only on `TavernRuntime` (`runtime.py:154`). This is acceptable if documented as process-local, but users may perceive `last` and `/rp voice on` as session behavior.

- Convert the help text into generated command metadata. Help is a long string in `runtime.py:184`; dispatch is a separate if-chain. This will drift as commands evolve.

- Export path behavior is safe enough for profile-local output, but exports include full message content and card data (`runtime.py:2086`). Consider adding an explicit "export includes private session content" confirmation for gateway platforms or a config gate.

- Card inspect has a write side effect: inspecting a stored card with embedded lorebook saves that embedded lorebook (`runtime_assets.py:187`). It is convenient, but surprising for an inspect command. Prefer reporting embedded lore and saving only on explicit import/use/start.

## Test Gaps

- Missing P0 security tests:
  - Gateway explicit filesystem path imports are rejected outside approved attachment roots.
  - User cannot switch to another user's session by full ID or prefix.
  - Ambiguous session prefixes are handled deterministically with an error.

- Missing image security tests:
  - Image provider exceptions containing secrets/URLs/paths are not returned to users or persisted raw.
  - `MEDIA:` paths from image providers are constrained to the Tavern image output directory, or at least validated before gateway delivery.

- Missing performance tests:
  - Large message history pagination with thousands of rows.
  - Large lorebooks with many keys/regex entries.
  - Image history and session browser pagination under large tables.

- Missing import hardening tests:
  - Local import size limits for JSON, PNG, and text importers.
  - Malformed-but-valid-extension files for preset/lore/persona commands return bounded user-safe errors through the top-level command boundary.
  - Remote card download errors should not echo sensitive URLs; current tests cover scheme/private-host rejection and size limits, but not exception-message sanitization from `urlopen()`.

- Missing concurrency tests:
  - Two active gateway events for the same session appending messages concurrently.
  - Simultaneous session switch/archive/clone operations.
  - SQLite busy behavior under parallel writes.

Covered areas worth keeping: card PNG/JSON/URL import, provider URL validation, secret-free model status/test, gateway hook fallthrough, malformed event handling, pagination clamps, turn controls, mobile attachment imports, export delivery, content mode, presets, lorebooks, memory, personas, notes, images, and fake-adapter e2e.

## Suggested Next CodeStable Phases

### Phase A - P0 Gateway Security Closure

1. Add a Tavern import-source policy helper.
2. Permit explicit filesystem paths only for trusted local/CLI contexts.
3. Permit gateway imports only from adapter-provided approved attachment paths.
4. Add local file size limits across card/preset/lore/persona importers.
5. Scope session switch lookup and activation to `scope_key`.
6. Add the P0 tests listed above.

Expected result: No gateway user can read arbitrary host files or switch into another user's session.

### Phase B - Runtime Boundary Refactor

1. Move image, memory, persona, lore, preset, and export command handlers out of `runtime.py`.
2. Introduce a table-driven `/rp` command registry with generated help.
3. Centralize pagination, reference parsing, and attachment import handling.
4. Keep `TavernRuntime` focused on orchestration: command dispatch, active-message pipeline, adapter selection.

Expected result: Smaller modules, fewer duplicated parsing paths, easier targeted reviews.

### Phase C - Persistence and Performance Hardening

1. Split `TavernStore` into focused repositories or mixins.
2. Add indexes, `busy_timeout`, and optional WAL.
3. Add large-table pagination benchmarks/regression tests.
4. Add prompt-budget pruning based on model context window.

Expected result: Better behavior under large sessions/lorebooks and concurrent gateway use.

### Phase D - Provider and Media Safety

1. Sanitize image-provider failures like model-provider failures.
2. Reuse one secret-field sanitizer everywhere.
3. Validate `MEDIA:` file paths before returning them from generated assets.
4. Add explicit UX for placeholder `/rp speak` and future real TTS provider gates.

Expected result: Consistent secret/privacy posture across text, image, export, and TTS surfaces.

## Appendix: Files/Functions Inspected

- `plugins/hermes_tavern/runtime.py`: `TavernRuntime.handle_command_sync`, `_handle_command_sync`, `handle_active_message_sync`, `_run_generation_pipeline`, `_debug_prompt`, `_session_prompt_modules`, `_session_memory_modules`, `_session_lore_modules`, `_generate_with_session_adapter`, `_preset_import`, `_preset_use`, `_lore_import`, `_lore_inspect`, `_memory_*`, `_persona_import`, `_persona_inspect`, `_note_*`, `_live_memory_summarize`, `_image_*`, `_export`, `_start`.
- `plugins/hermes_tavern/runtime_assets.py`: `assets`, `cards`, `card_command`, `card_import`, `card_inspect`, `card_use`.
- `plugins/hermes_tavern/runtime_sessions.py`: `session_command`, `session_info`, `sessions`, `switch`, `rename`, `archive`, `clone`.
- `plugins/hermes_tavern/runtime_model.py`: `model_command`, `model_status`, `model_profiles`, `model_seed_apiyi`, `model_use`, `model_mode`, `model_live`, `model_test`.
- `plugins/hermes_tavern/db.py`: `TavernStore.__init__`, `migrate`, connection setup, card/session/message CRUD, preset/lore/persona/model/memory/session-browser/image methods, `get_session_by_id_prefix`, `switch_to_session`.
- `plugins/hermes_tavern/db_utils.py`: `assert_no_secret_keys`, `row_to_dict`, `utc_now`.
- `plugins/hermes_tavern/provider_bridge.py`: `validate_provider_base_url`, `HermesRuntimeProviderResolver`, `_resolve_apiyi`, `sanitize_provider_payload`.
- `plugins/hermes_tavern/adapters.py`: `FakeModelAdapter`, `HermesProviderAdapter`, `HermesChatCompletionAdapter`, `_message_content`.
- `plugins/hermes_tavern/importers/cards.py`: `parse_character_card`, `load_card_file`, `_load_remote_card`, `_read_png_chara`.
- `plugins/hermes_tavern/importers/presets.py`: `import_preset_file`, `import_raw_preset_text`, `import_st_preset_json`, `_safe_raw`.
- `plugins/hermes_tavern/importers/lorebooks.py`: `import_lorebook_file`, `import_st_lorebook_json`, `import_embedded_lorebook_from_card`, `_safe_raw`.
- `plugins/hermes_tavern/importers/personas.py`: `import_persona_file`, `import_persona_json`, `import_raw_persona_text`, `_safe_raw`.
- `plugins/hermes_tavern/images.py`: prompt/settings/safety/provider surfaces by reference from runtime and tests.
- `plugins/hermes_tavern/lorebook.py`: `match_lorebook_entries`, `_entry_matches`, `_any_key_matches`.
- `plugins/hermes_tavern/prompt.py`: `PromptCompiler.compile`.
- `plugins/hermes_tavern/gateway_hook.py`: `_get_adapter`, `_send_if_possible`, `pre_gateway_dispatch`.
- `plugins/hermes_tavern/identity.py`: `session_key_from_event`, `_safe_attr`.
- Tests inspected: all files matching `tests/plugins/test_hermes_tavern_*.py`; scoped suite run passed with `397 passed, 8 warnings`.
