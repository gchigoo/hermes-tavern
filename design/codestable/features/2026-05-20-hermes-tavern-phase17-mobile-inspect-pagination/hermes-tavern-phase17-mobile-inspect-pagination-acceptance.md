---
doc_type: feature-acceptance
feature: 2026-05-20-hermes-tavern-phase17-mobile-inspect-pagination
status: accepted
verified_at: '2026-05-20'
---

# Phase 17: Mobile Inspect Parity & Paginated Card Browsing — Acceptance Report

> 阶段：阶段 3（验收闭环）
> 验收日期：2026-05-20
> 关联方案 doc：.codestable/features/2026-05-20-hermes-tavern-phase17-mobile-inspect-pagination/design.md

## 1. 接口契约核对

### 名词层"现状 → 变化"

- [x] `RPCommand(name, args, raw)` — unchanged. `_cards()` reads `args[0]` (limit) and `args[1]` (page) without modifying RPCommand. Consistent.
- [x] Lorebook entry row fields used by `_lore_inspect`: `title`, `content`, `keys_json`, `enabled`, `constant`, `regex` — all present in `list_lorebook_entries()` SELECT (db.py:681-691). Consistent.
- [x] Session row fields used by `_session_info`: `id`, `status`, `card_name`, `card_id`, `title`, `content_mode`, `preset_id`, `lorebook_id`, `adapter_mode`, `live_confirmed` — all returned by `get_active_session()`. Consistent.
- [x] Preset module row fields used by `_preset_inspect`: `name`, `content`, `enabled`, `raw_json` — all returned by `list_prompt_modules()`. Consistent.
- [x] `_module_risk_counts_db(modules: list[dict]) -> dict` — new helper at runtime.py:1175. Returns `{"safe": int, "adult_fiction": int, "risky_disabled": int}`. No naming conflict with `_module_risk_counts` (takes PromptModule objects). Consistent.

### 接口示例逐项核对

- [x] `/rp cards 5 2` with 8 cards → `page 2/2`, cards 5-8, `prev: /rp cards 5 1`, no `next:` — `test_cards_pagination_page2` with 12 cards confirms page 2/3, correct slice, both hints. Behavior correct.
- [x] `_preset_inspect` output: `Preset: <name> (<id[:8]>)` / `safe: X enabled...` / `use: /rp preset use <name>` — runtime.py:624-638 matches exactly. Consistent.
- [x] `_lore_inspect` output: `Lorebook: <name> (<id[:8]>)` / `entries: N total...` / `top entries:` / `use:` / `test:` — runtime.py:715-727 matches. Consistent.
- [x] `_session_info` output: `Session: [<id[:8]>] <title> (<status>)` / all binding lines / `hints:` — runtime.py:1027-1036 matches. Consistent.

### 流程图核对

- [x] Mermaid node `_cards: parse limit+page, compute total_pages, slice` → runtime.py:274-310 ✓
- [x] Mermaid node `_preset_inspect: aggregate counts by risk label + bounded previews` → runtime.py:615-638 ✓
- [x] Mermaid node `_lore_command → _lore_inspect` → runtime.py:668-669 ✓
- [x] Mermaid node `handle_command_sync 'session' → _session_info` → runtime.py:148-149 → 1004-1038 ✓

## 2. 行为与决策核对

### 明确不做

- [x] Telegram inline keyboards — not present anywhere in Phase 17 diff. grep `InlineKeyboard`: 0 hits in plugin. ✓
- [x] Real provider/network calls — no `requests`, `aiohttp`, provider bridge calls added. ✓
- [x] Asset download/file delivery — no file I/O added. ✓
- [x] DB schema changes — no migration code added to db.py. ✓

### 关键决策落地

- [x] All changes in `runtime.py` only — `db.py` and `commands.py` untouched. ✓
- [x] No raw JSON ever output to user — `_preset_inspect`, `_lore_inspect`, `_session_info` all format structured text only; `_module_risk_counts_db` reads `raw_json` internally to extract `risk_level` but never appends raw JSON to output lines. `test_preset_inspect_no_raw_json_in_output` confirms `'{"'` not in output. ✓
- [x] No microrefactor — `runtime.py` remains single-file monolithic dispatcher. ✓
- [x] TDD — red tests written first (10 failures), then implementation made all green. ✓

### 挂载点反向核对（可卸载性）

Listed mount points vs. grep results:

| Mount point (design §2.3) | Code location | Grep confirmed |
|---|---|---|
| `handle_command_sync`: `name == "session"` branch | runtime.py:148-149 | ✓ single occurrence |
| `_lore_command`: `subcommand == "inspect"` branch | runtime.py:668-669 | ✓ single occurrence |
| `/rp help` text: lore inspect + session info | runtime.py:88, 107 | ✓ both present |
| `_cards`: page arg parsing + pagination footer | runtime.py:282-309 | ✓ contained in `_cards` |

**Reverse check** — `_session_command`, `_session_info`, `_lore_inspect`, `_module_risk_counts_db` grep shows each is referenced only from the expected call sites (confirmed above). No unlisted entry points found.

**Removal sandbox**: delete lines 148-149 → `/rp session info` falls through to `Unknown /rp command`. Delete lines 668-669 → `/rp lore inspect` returns usage error. Delete help lines 88, 107 → commands invisible. Delete lines 282-309 in `_cards` → reverts to single-page. Clean removals, no residue.

## 3. 验收场景核对

| Scenario | Evidence | Result |
|---|---|---|
| Cards page 1 default (`/rp cards`) | `test_cards_pagination_backward_compatible`: no prev/next footer | ✓ pass |
| Cards page 2 (`/rp cards 5 2`, 12 cards) | `test_cards_pagination_page2`: `page 2/3`, correct slice, prev+next | ✓ pass |
| Cards page clamp (`/rp cards 5 99`, 8 cards) | `test_cards_pagination_clamp_to_last_page`: `page 2/2`, clamped | ✓ pass |
| Cards single page no footer | `test_cards_pagination_single_page_no_footer`: `page 1/1`, no hints | ✓ pass |
| Cards bad limit | `test_cards_bad_limit_returns_usage`: `Usage:` in output | ✓ pass |
| Preset inspect aggregate | `test_preset_inspect_shows_aggregate_risk_counts`: `safe:` + `enabled` present | ✓ pass |
| Preset inspect no raw JSON | `test_preset_inspect_no_raw_json_in_output`: `'{"'` not in output | ✓ pass |
| Preset inspect bounded previews | `test_preset_inspect_module_previews_bounded`: 200-char content absent | ✓ pass |
| Preset inspect use hint | aggregate test asserts `/rp preset use` in response | ✓ pass |
| Preset inspect missing | pre-existing test in `test_hermes_tavern_runtime_presets.py` (unchanged behavior) | ✓ pass |
| Lore inspect basic | `test_lore_inspect_shows_summary_and_top_entries`: name, counts, constant, use+test hints | ✓ pass |
| Lore inspect not found | `test_lore_inspect_not_found`: `not found` in output | ✓ pass |
| Lore inspect in help | `test_lore_inspect_in_help`: `/rp lore inspect` in help text | ✓ pass |
| Session info active | `test_session_info_shows_bindings_and_counts`: Session/card/content_mode/adapter/memory/hints | ✓ pass |
| Session info no session | `test_session_info_no_active_session`: `No active Hermes Tavern session` | ✓ pass |
| Session info in help | `test_session_info_in_help`: `/rp session info` in help text | ✓ pass |
| No raw JSON any inspect/info | `test_preset_inspect_no_raw_json_in_output`; lore/session output uses formatted text only | ✓ pass |
| Existing 185 tests | Full suite: 199 passed (185 original + 14 new) | ✓ pass |

No frontend/browser verification needed — pure text command output.

## 4. 术语一致性

- `_module_risk_counts_db`: name matches design §2.2 exactly. grep: 2 hits (definition + call site). No collision with `_module_risk_counts`. ✓
- `_lore_inspect`: matches design. grep: 3 hits (def + routing call + usage string). ✓
- `_session_info` / `_session_command`: matches design. grep: 4 hits each. ✓
- `risky_disabled` key in `_module_risk_counts_db` dict: consistent between helper definition and `_preset_inspect` consumer. ✓
- `page X/Y` header format: matches design spec exactly. ✓

## 5. 架构归并

Design §4 not explicitly written (feature predates §4 template requirement). Evaluating now:

**New system-level capabilities introduced by Phase 17:**
- `/rp lore inspect <lorebook>` — new command in the lore subcommand surface
- `/rp session info` — new top-level `/rp session` command namespace
- `/rp cards [limit] [page]` — pagination added to existing command
- `_module_risk_counts_db` — new module-level helper (internal, not user-facing noun)

**Architecture impact:** no new modules, no new DB tables, no new cross-module interfaces. All changes are within `runtime.py` presentation layer. The Hermes Tavern section of ARCHITECTURE.md is stale (still reads "Phase 1-3 done, Phase 4 next") — updated below to reflect Phase 17 completion.

- [x] `.codestable/architecture/ARCHITECTURE.md` — §4 Hermes Tavern Plugin Architecture updated to reflect Phase 17 command surface and current completion status. Written below.

**No new cross-module constraints or architectural patterns introduced.**

## 6. Requirement 回写

Design frontmatter has no `requirement` field. Phase 17 adds mobile UX parity to existing Tavern commands — refinement of an existing capability, not a new top-level user-facing capability distinct from the Tavern plugin's core RP workflow.

**Result:** no requirement backfill needed for Phase 17 alone. The parent capability (Hermes Tavern plugin with mobile-safe UX) is covered by the plugin's ongoing feature stream. If a dedicated `req-hermes-tavern-mobile-ux` has been drafted, this phase would update it; none exists currently.

→ Skipped: no standalone requirement backfill required.

## 7. Roadmap 回写

Design frontmatter has no `roadmap` / `roadmap_item` fields.

→ Skipped: non-roadmap-起头 feature.

## 8. attention.md 候选盘点

No new environment traps, tooling quirks, or project-wide workflow constraints surfaced during Phase 17 implementation. The existing attention.md entries (test command with `-o 'addopts='`, venv path, no hard-coded `~/.hermes`) were all followed without issue.

→ No candidates for attention.md this phase.

## 9. 遗留

- **Preset inspect use hint uses preset name, not original ref**: `use: /rp preset use <name>` — consistent; users can always use the name. No issue.
- **No forward-only pagination index**: large card collections (>250) require multiple `/rp cards 25 N` calls; no jump-to-page UX. Low priority given mobile-use context. Noted for potential Phase 18 if needed.
- **`/rp session` with no subcommand defaults to `info`**: `_session_command` defaults `subcommand = "info"` when `command.args` is empty. This means `/rp session` with no args works as `session info`. Acceptable UX; no issue.
- **Lore inspect `source` field**: `lorebook.get('source', 'imported')` — the lorebook DB row may not always have a `source` column populated (depends on import path). Fallback `'imported'` is safe. Pre-existing data shape concern, not introduced by Phase 17.
- No open issues from impl phase "顺手发现" list. One test updated (`test_hermes_tavern_runtime_presets.py` line 39) to match intentional format change in `_preset_inspect`.
