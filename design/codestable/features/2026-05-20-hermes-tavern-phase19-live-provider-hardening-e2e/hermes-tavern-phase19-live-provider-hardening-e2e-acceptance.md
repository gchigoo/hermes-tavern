---
doc_type: feature-acceptance
feature: 2026-05-20-hermes-tavern-phase19-live-provider-hardening-e2e
status: accepted
verified_date: 2026-05-20
related_design: hermes-tavern-phase19-live-provider-hardening-e2e-design.md
---

# Phase 19 Live Provider Hardening + E2E Generation — Acceptance Report

> Stage: Phase 3 (acceptance closure)
> Date: 2026-05-20
> Design: `.codestable/features/2026-05-20-hermes-tavern-phase19-live-provider-hardening-e2e/hermes-tavern-phase19-live-provider-hardening-e2e-design.md`

---

## 1. Interface Contract Verification

**Noun layer (design §2.1) — current → change verified:**

- [x] `validate_provider_base_url(base_url: str) -> None` — defined at `provider_bridge.py:34`; raises `ValueError` with user-safe message (no URL echo); tested in `test_hermes_tavern_provider_bridge.py` parametric tests. ✓
- [x] `SAFE_URL_SCHEMES: frozenset[str]` — defined at `provider_bridge.py:19`. ✓
- [x] `_BLOCKED_HOST_PREFIXES: tuple[str, ...]` — defined at `provider_bridge.py:22`. ✓
- [x] `_BLOCKED_HOSTS: frozenset[str]` — defined at `provider_bridge.py:29`. ✓
- [x] `_build_client()` in `HermesChatCompletionAdapter` — calls `validate_provider_base_url(base_url)` at `adapters.py:108` before constructing OpenAI client. ✓
- [x] `_model_test()` — defined at `runtime.py:1044`; dry-run, no generation. ✓

**Flow diagram (design §2.2) — nodes verified by grep:**

- [x] `_generate_with_session_adapter` → `HermesChatCompletionAdapter.generate` → `resolver()` → `_build_client(payload)` → `validate_provider_base_url(base_url)` → `ValueError` path → `except Exception` → bounded envelope. All nodes in code. ✓
- [x] `_model_test` → `HermesRuntimeProviderResolver.resolve` → `sanitize_provider_payload` → `validate_provider_base_url` — all calls confirmed at `runtime.py:1072–1088`. ✓

No deviations found.

---

## 2. Behavior and Decisions Verification

**Requirements (design §1):**

- [x] Default `adapter_mode=fake` preserved — no change to `TavernStore` defaults or migration. ✓
- [x] Real calls require both `/rp model mode hermes` + `/rp model live confirm` — gate logic unchanged at `runtime.py:443–457`. ✓
- [x] Error envelope never forwards `str(exc)` — both injected adapter path (`runtime.py:456`) and `HermesChatCompletionAdapter` path (`runtime.py:475`) return fixed string. ✓
- [x] No DB schema changes — no new columns, no migration needed. ✓

**Explicitly not done (design §1):**

- [x] No real network calls in tests — confirmed by code review and test structure. ✓
- [x] No credentials in code/DB/docs/test fixtures — targeted search for real-looking key patterns (`sk-*`, prior placeholder key strings, long `api_key=` values) returned no Tavern matches. ✓
- [x] Provider client receives a bounded timeout (`DEFAULT_PROVIDER_TIMEOUT_SECONDS = 45.0`); no thread-level timeout wrapper yet. ✓
- [x] No breaking command signature changes — existing `/rp model` sub-commands all preserved. ✓

**Key decisions landed:**

- [x] Decision: error message never echoes rejected URL — all `ValueError` messages in `validate_provider_base_url` use fixed strings without interpolating `base_url`. ✓
- [x] Decision: `except Exception` catches for both injected-adapter and HermesChatCompletionAdapter paths — verified at `runtime.py:454-457` and `runtime.py:473-476`. ✓
- [x] Decision: `/rp model test` always "no real generation" note regardless of mode — verified for fake branch (`runtime.py:1070`) and hermes branch (`runtime.py:1104`). ✓

**Orchestration layer (design §2.2) changes:**

- [x] `validate_provider_base_url` inserted in `_build_client` before client construction. ✓
- [x] Both `except Exception` handlers return `"[Hermes Tavern: provider error — check /rp model status]"`. ✓
- [x] `_model_test()` wired in `_model_command()` dispatcher at `runtime.py:923`. ✓
- [x] `/rp model test` added to help text at `runtime.py:101`. ✓

**Mount points (design §2.3) — grep + unplug sandbox:**

| Mount point | Code location | Grep confirmed |
|---|---|---|
| `validate_provider_base_url` called in `_build_client` | `adapters.py:108` | ✓ |
| error envelope `except Exception` (injected adapter) | `runtime.py:456` | ✓ |
| error envelope `except Exception` (HermesChatCompletionAdapter) | `runtime.py:475` | ✓ |
| `/rp model test` branch in `_model_command` | `runtime.py:923` | ✓ |
| `/rp model test` in help text | `runtime.py:101` | ✓ |

**Reverse grep (no undeclared mount points):** `validate_provider_base_url` appears only in 3 files: `provider_bridge.py` (definition), `adapters.py` (call), `runtime.py` (import + call in `_model_test`). No hidden callers. ✓

**Unplug sandbox:** removing `validate_provider_base_url(base_url)` from `_build_client` → URL injection re-opened. Removing `except Exception` blocks → exc-leaking message returns. Removing `/rp model test` branch → command goes to unknown-command fallback. Each mount point is independently load-bearing. ✓

---

## 3. Acceptance Scenario Verification

| Check | Scene | Evidence | Result |
|---|---|---|---|
| A1 | `validate_provider_base_url("http://...")` raises ValueError; message has no URL | `test_validate_provider_base_url_rejects_non_https_scheme` — 4 parametric cases | ✓ |
| A2 | `validate_provider_base_url("file:///...")` raises ValueError | same parametric test | ✓ |
| A3 | `validate_provider_base_url("https://127.0.0.1/v1")` raises ValueError | `test_validate_provider_base_url_rejects_private_hosts` — 12 parametric cases incl. 127.x | ✓ |
| A4 | `validate_provider_base_url("https://192.168.x.x/v1")` raises ValueError | same parametric test | ✓ |
| A5 | `validate_provider_base_url("https://api.apiyi.com/v1")` no raise | `test_validate_provider_base_url_allows_safe_urls` — 6 cases | ✓ |
| A6 | `validate_provider_base_url("https://api.openai.com/v1")` no raise | same test | ✓ |
| A7 | adapter invalid base_url → bounded error; no URL in response | `test_hermes_chat_completion_adapter_rejects_private_base_url` + `rejects_http_base_url` | ✓ |
| A8 | arbitrary RuntimeError from adapter → error envelope no secret leak | `test_runtime_live_provider_exception_does_not_leak_secret_detail` | ✓ |
| A9 | `/rp model test` fake mode — readiness status, no generation, no api_key value | `test_runtime_model_test_fake_mode` + `test_runtime_model_test_hermes_mode_with_fake_resolver` | ✓ |
| A10 | `/rp model test` no session → "No active Hermes Tavern session." | `test_runtime_model_test_no_session` | ✓ |
| A11 | E2E session+card+preset+lore+memory → fake adapter → reply persisted | `test_e2e_full_pipeline_with_fake_adapter` | ✓ |
| A12 | gateway hook survives provider exception; returns allow/skip | `test_gateway_hook_does_not_crash_on_active_message_provider_exception` | ✓ |
| A13 | api_key/access_token absent from test-asserted output | checked in A9, A11, all model test assertions — placeholder key value not in response asserted | ✓ |

**Full test suite:** 259 passed, 0 failed. No frontend changes; mobile output format unchanged.

---

## 4. Terminology Consistency

- `validate_provider_base_url` — consistent across 3 files (definition + 2 call sites). ✓
- `SAFE_URL_SCHEMES`, `_BLOCKED_HOSTS`, `_BLOCKED_HOST_PREFIXES` — internal constants, no external surface. ✓
- `"[Hermes Tavern: provider error — check /rp model status]"` — exact string used in both error envelope locations (`runtime.py:457`, `runtime.py:476`). ✓
- `_model_test` — single definition, single call in dispatcher. ✓
- No naming conflicts with existing modules confirmed (grep found no pre-existing `validate_provider_base_url`). ✓

---

## 5. Architecture归并

Design §4 was not written (Phase 19 scope was implementation only), so evaluating here:

**What changed architecturally:**

1. `provider_bridge.py` — now exports `validate_provider_base_url()` as a stable public function. This is a new safety boundary in the provider path.
2. `adapters.py` — `HermesChatCompletionAdapter._build_client()` now enforces URL safety before client construction and passes a bounded OpenAI-client timeout.
3. `runtime.py` — error envelope hardened (no exc leakage); `/rp model test` command added.
4. New test module `test_hermes_tavern_e2e.py` — first E2E coverage for full generation pipeline.

**Architecture doc updates needed:**

- [x] `ARCHITECTURE.md §4` — update phase progress marker from "Phases 1–17" to "Phases 1–19". Update `/rp model` command surface. Update `provider_bridge.py` description to mention `validate_provider_base_url`. Update §6 Known Constraints to document URL safety rule.

Updating now.

---

## 6. Requirement Backfill

Design `requirement` field is empty. This phase adds user-observable capabilities:
- `/rp model test` command (new user-facing surface)
- URL safety (transparent safety hardening — not user-observable as a command)
- Error envelope improvement (user sees better bounded message, not secrets)

The `/rp model test` command is a small user-visible addition, but it's part of the broader Hermes Tavern model routing capability already implicit in prior phases. No standalone req doc warranted — the capability is subsumed under the Tavern model routing surface. Writing: **no requirement backfill** — capability extends existing model routing surface, not a new top-level ability.

---

## 7. Roadmap Backfill

Design frontmatter has no `roadmap` / `roadmap_item` fields. **Non-roadmap feature — skipped.** ✓

---

## 8. attention.md Candidates

- **Candidate 1:** `test_hermes_tavern_e2e.py` pattern for importing from runtime+commands+db in the same test module — no new env/tooling knowledge surfaced. Not an attention.md candidate.
- **Candidate 2:** `validate_provider_base_url` is intentionally not imported in `gateway_hook.py` — the validator is enforced at adapter build time, not hook time. This is by design and doesn't need documentation in attention.md.

**No attention.md candidates surfaced.** ✓

---

## 9. Residuals

**Post-Phase-19 improvement candidates (not blocking):**

- `runtime.py` is now 1330+ lines. A `cs-refactor` pass to split command handlers into a `_commands/` subpackage would reduce per-command cognitive load. Flagged for after Phase 20.
- Thread-level timeout wrapping (e.g., `concurrent.futures.ThreadPoolExecutor` hard stop) is not implemented. The client-level timeout and fixed error envelope are sufficient for Phase 19; a stricter runtime watchdog can be a Phase 20+ candidate.
- IPv6 provider base URLs are rejected conservatively in Phase 19, including private IPv6 ranges (`fc00::/7`, `fe80::/10`) and public IPv6 hosts. This is safe but may need loosening if a future provider requires IPv6 literal URLs.

**No issues opened yet** — all are documentation/future-hardening items.
