# Hermes Tavern Phase 18 — Mobile-Safe Paginated History, Sessions, and Memory Browsing — 验收报告

> 阶段：阶段 3（验收闭环）
> 验收日期：2026-05-20
> 关联方案 doc：`.codestable/features/2026-05-20-hermes-tavern-phase18-mobile-browse-pagination/hermes-tavern-phase18-mobile-browse-pagination-design.md`

---

## 1. 接口契约核对

### 名词层"现状 → 变化"逐项核对

- [x] **`count_messages(session_id)`** → `plugins/hermes_tavern/db.py` — 新增，返回 int 行数；实现完整，直接 `SELECT COUNT(*)` 过滤 session_id。一致 ✓
- [x] **`get_messages_page(session_id, limit, offset)`** → `db.py` — 新增，ASC 升序 slice；`ORDER BY created_at ASC, id ASC LIMIT ? OFFSET ?`，page 1 = 最旧。一致 ✓
- [x] **`count_sessions_for_scope(scope_key, *, include_all)`** → `db.py` — 新增，两路 SQL (include_all / active-only)，返回 int。一致 ✓
- [x] **`list_sessions_for_scope(..., limit=50, offset=0)`** → `db.py` — 已有方法增加 `limit`/`offset` kwargs，默认值保持 `LIMIT 50 OFFSET 0`，后向兼容。一致 ✓
- [x] **`count_session_memory_facts(session_key)`** → `db.py` — 新增，JOIN sessions 过滤 active。一致 ✓
- [x] **`list_session_memory_facts(..., *, limit=None, offset=0)`** → `db.py` — 已有方法增加 `limit`/`offset` kwargs，`limit=None` 时不加 `LIMIT` 子句（全量返回，后向兼容）。一致 ✓

### 编排层主流程图核对（第 2.2 节 mermaid 图）

- [x] `/rp history [limit] [page]` → `_history` (runtime.py:475): args 解析 → `count_messages` → `total_pages` → `get_messages_page` → header + previews + nav hints。节点全部落地 ✓
- [x] `/rp sessions [all] [limit] [page]` → `_sessions` (runtime.py:1075): `all` 标志解析 → `count_sessions_for_scope` → `list_sessions_for_scope(limit, offset)` → header + rows + nav hints。节点全部落地 ✓
- [x] `/rp memory list [limit] [page]` → `_memory_command` → `_memory_list(command, event)` (runtime.py:817): extra_args 解析 → `count_session_memory_facts` → `list_session_memory_facts(limit, offset)` → header + facts + nav hints。节点全部落地 ✓

**偏差**：无。

---

## 2. 行为与决策核对

### 需求摘要逐项验证

- [x] **A: `/rp history [limit] [page]`** — 页头 `page X/Y, N shown, M total`；page 1 = 最旧；prev/next hints 按需出现。测试全绿 ✓
- [x] **B: `/rp sessions [all] [limit] [page]`** — all 标志保留；active marker `*` 保留；prev/next hints 含 `all` 时带 `all`。测试全绿 ✓
- [x] **C: `/rp memory list [limit] [page]`** — summary 状态保留；`facts (page X/Y...)` 行；预览 ≤80 chars；prev/next hints。测试全绿 ✓

### 明确不做 — 反向核对

- [x] **Telegram inline keyboards**：代码中无任何 `InlineKeyboard` / `reply_markup` 引用 — `grep -r "InlineKeyboard\|reply_markup" plugins/hermes_tavern/` → 无命中 ✓
- [x] **真实 provider/network 调用**：所有测试使用 `FakeAdapter`，无 HTTP 客户端引入 ✓
- [x] **DB schema 变更**：仅新增查询方法和扩展 kwargs，无 `ALTER TABLE` / `CREATE TABLE` ✓
- [x] **Asset download / file delivery**：无 ✓
- [x] **raw JSON 输出**：预览走 `_mobile_preview()`，无 `json.dumps` / `data_json` 直接暴露给用户 ✓

### 关键决策落地

- [x] **Chronological pages (page 1 = oldest)** — `get_messages_page` 使用 `ORDER BY created_at ASC, id ASC LIMIT ? OFFSET ?`；`test_history_chronological_order` 测试证实 ✓
- [x] **Sessions page 1 = most-recently-updated** — `list_sessions_for_scope` 保留 `ORDER BY updated_at DESC`；与旧行为一致 ✓
- [x] **All runtime changes in runtime.py, DB helpers in db.py only** — grep 确认无其他文件改动 ✓
- [x] **`_mobile_preview` reused** — `_memory_list` 和 `_history` 均调用 `_mobile_preview(content, 80)` ✓

### 流程级约束核对

- [x] **Bad limit → Usage 字符串，不 crash** — ValueError 捕获后直接返回 Usage 提示；三处均一致 ✓
- [x] **page clamp ≥ 1 且 ≤ total_pages** — `page = min(page, total_pages)` + `max(1, ...)` 三处一致 ✓
- [x] **No active session 行为不变** — 三处均在 store 查询前 guard，返回 `"No active Hermes Tavern session."` ✓
- [x] **Ceil division** — 使用 `-(-total // limit)` 三处一致 ✓

### 挂载点反向核对（可卸载性）

设计中挂载点 5 条，对照代码 grep：

| 挂载点 | 清单条目 | 代码落点 | 结论 |
|---|---|---|---|
| `_history` in runtime.py | ✓ | runtime.py:475，dispatch at :141 | 一致 ✓ |
| `_sessions` in runtime.py | ✓ | runtime.py:1075，dispatch at :151 | 一致 ✓ |
| `_memory_list` in runtime.py | ✓ | runtime.py:817，dispatch at :798 | 一致 ✓ |
| count/page helpers in db.py | ✓ | db.py — 6 new methods/kwargs | 一致 ✓ |
| help text strings | ✓ | runtime.py:84,89,112 | 一致 ✓ |

**反向 grep**：`grep -n "count_messages\|get_messages_page\|count_sessions_for_scope\|count_session_memory_facts" plugins/hermes_tavern/runtime.py` — 仅命中 `_history` 和 `_sessions` 和 `_memory_list` 三处，均在清单内。无清单外引用 ✓

**拔除沙盘推演**：
1. 恢复旧 `_history` (一个 limit arg) → 旧查询回来
2. 移除 `count_sessions_for_scope`，恢复旧 `_sessions` → 旧行为回来
3. 移除 `_memory_list(command, event)` signature，恢复旧方法 → 旧行为回来
4. 移除 db.py 的 count/page helpers → 无残留（仅被上述 3 个方法调用）
5. 还原 help text → 无残留

推演无残留 ✓

---

## 3. 验收场景核对

对照设计文件第 3 节关键场景，测试名称对应验证：

**A — `/rp history [limit] [page]`**

- [x] S-A1: No args → page 1/1, all shown, no nav hints — `test_history_default_compat_shows_page_header` PASSED ✓
- [x] S-A2: `/rp history <limit>` → page 1 — `test_history_limit_only_compat` PASSED ✓
- [x] S-A3: `/rp history 5 2` (15 msgs) → page 2/3, 5 shown, 15 total, prev+next — `test_history_page2_shows_correct_slice_and_hints` PASSED ✓
- [x] S-A4: page=99 clamps → last page, prev hint, no next — `test_history_page_clamp_to_last` PASSED ✓
- [x] S-A5: `/rp history bad` → Usage string — `test_history_bad_limit_returns_usage` PASSED ✓
- [x] S-A6: No active session → unchanged message — `test_history_no_active_session_unchanged` PASSED ✓
- [x] S-A7: Preview ≤80 chars, single-line — `test_history_preview_bounded` PASSED ✓
- [x] S-A8: page 1 = oldest — `test_history_chronological_order` PASSED ✓
- [x] S-A9: Help text updated — `test_history_in_help` PASSED ✓

**B — `/rp sessions [all] [limit] [page]`**

- [x] S-B1: No args → page 1/1 header — `test_sessions_default_compat_shows_page_header` PASSED ✓
- [x] S-B2: `/rp sessions all` → page 1 with default limit — `test_sessions_all_compat` PASSED ✓
- [x] S-B3: `/rp sessions 3 2` (8 sessions) → page 2/3, prev+next without `all` — `test_sessions_page2_shows_hints_without_all` PASSED ✓
- [x] S-B4: `/rp sessions all 3 2` → hints include `all` — `test_sessions_all_page_hints_include_all` PASSED ✓
- [x] S-B5: `/rp sessions bad` and `/rp sessions all bad` → Usage — `test_sessions_bad_args_returns_usage` PASSED ✓
- [x] S-B6: Active session `*` marker preserved — `test_sessions_active_marker_preserved` PASSED ✓
- [x] S-B7: Help text updated — `test_sessions_in_help` PASSED ✓

**C — `/rp memory list [limit] [page]`**

- [x] S-C1: No args → page 1/1, all shown — `test_memory_list_default_compat_shows_page_header` PASSED ✓
- [x] S-C2: `/rp memory list 2 2` (5 facts) → page 2/3, prev+next — `test_memory_list_page2_shows_hints` PASSED ✓
- [x] S-C3: page=99 clamps → page 3/3 — `test_memory_list_page_clamp` PASSED ✓
- [x] S-C4: `/rp memory list bad` → Usage — `test_memory_list_bad_args_returns_usage` PASSED ✓
- [x] S-C5: No active session → unchanged — `test_memory_list_no_active_session_unchanged` PASSED ✓
- [x] S-C6: Preview ≤80 chars — `test_memory_list_preview_bounded` PASSED ✓
- [x] S-C7: `summary: set|none` in header — `test_memory_list_summary_shown` PASSED ✓
- [x] S-C8: `facts (page X/Y, N shown, M total):` line — `test_memory_list_facts_header_line` PASSED ✓
- [x] S-C9: Help text updated — `test_memory_list_in_help` PASSED ✓

**Explicit not-does reverse checks** (all via grep + test suite):
- [x] No Telegram inline keyboards in output ✓
- [x] No raw JSON in output ✓
- [x] No DB schema changes ✓
- [x] `/rp history 5` (no page arg) still works — `test_history_limit_only_compat` ✓
- [x] `/rp sessions all` (no numeric args) still works — `test_sessions_all_compat` ✓
- [x] `/rp memory list` (no args) still works — `test_memory_list_default_compat_shows_page_header` ✓

**Full suite:** 224 passed, 0 failed.

---

## 4. 术语一致性

Design uses: `count_messages`, `get_messages_page`, `count_sessions_for_scope`, `count_session_memory_facts`, `_mobile_preview`, `total_pages`.

- `count_messages` — grep: 2 hits (db.py definition + runtime.py call). No conflict ✓
- `get_messages_page` — grep: 2 hits (db.py def + runtime.py call) ✓
- `count_sessions_for_scope` — grep: 2 hits (db.py def + runtime.py call) ✓
- `count_session_memory_facts` — grep: 2 hits (db.py def + runtime.py call) ✓
- `_mobile_preview` — grep: 6 hits, all in runtime.py as intended. New calls (history, memory_list) consistent with existing usage ✓
- `total_pages` — local variable, used consistently in all 3 command methods ✓

No terminology conflicts found.

---

## 5. 架构归并

Updating ARCHITECTURE.md command surface section from Phase 17 to Phase 18:
- `/rp history [limit] [page]` (was `[limit]`)
- `/rp sessions [all] [limit] [page]` (was `[all]`)
- `/rp memory list [limit] [page]` (was `list`)
- Phase label updated from Phase 17 to Phase 18
- TavernStore db.py description updated to note pagination helpers

Actual changes written to ARCHITECTURE.md — see section below.

---

## 6. requirement 回写

Design frontmatter has no `requirement` field. This feature extends existing browsing capabilities introduced in Phase 15–17; no new user-facing ability class is added (it's a UX bounded-output improvement to existing commands). No new req needed. **无 requirement 回写** ✓

---

## 7. roadmap 回写

Design frontmatter has no `roadmap` / `roadmap_item` fields. **非 roadmap 起头，跳过** ✓

---

## 8. attention.md 候选盘点

本 feature 未暴露需要补入 attention.md 的新内容：
- DB 测试模式（`:memory:` or `tmp_path`）、`append_message` API、`start_session` + `clone_session` 组合创建多会话 — 这些是具体业务细节，不是"每个 feature 都会撞一次的环境 / 工具 / 工作流信息"。
- 唯一的工作流发现（`_start` appends greeting message, adding to count）已经在测试 helper 中用 `no first_mes` 卡设计处理，不是跨 feature 的环境约束。

**本 feature 未暴露需要补入 attention.md 的内容** ✓

---

## 9. 遗留

**后续优化点（低优先级）：**
- `_history` empty-session message: 当 `total == 0` 时当前输出 `page 1/1, 0 shown, 0 total` 而无 "No messages" 提示 — 功能正确，可视情况优化措辞。
- `/rp sessions` without active session still returns count header; could also show a zero-sessions empty message more elegantly.

**已知限制：**
- `list_session_memory_facts` uses an f-string interpolation for `LIMIT/OFFSET` clause (sanitized by `int()` cast). Safe but non-standard — could be refactored to parameterized form in a future cleanup.

**顺手发现（不在 feature PR 范围内）：**
- None.
