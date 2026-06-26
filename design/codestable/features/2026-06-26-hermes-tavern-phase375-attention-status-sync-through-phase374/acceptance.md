---
doc_type: feature-acceptance
feature: 2026-06-26-hermes-tavern-phase375-attention-status-sync-through-phase374
status: accepted
accepted_at: "2026-06-26"
summary: "Phase 375 attention/status sync through accepted Phase 374 — S1 executor completed, S2 parent-controller verification and finalization done."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase375]
---

# Phase 375 Acceptance Report

## 1 接口契约核对

- [x] `design/codestable/attention.md` 当前状态行从 `All phases 1-374 accepted` 推进到 `All phases 1-375 accepted`。
- [x] 追加 `Phase 375 attention status sync through Phase 374` 标签恰好一次。
- [x] 终端后缀从 Phase 372/373/374 移动到 Phase 373/374/375。
- [x] 所有 Phase 168-375 标签完整保留，包括 `Phase 121-167` 和 Phase 374。

## 2 行为与决策核对

- [x] `tests/test_hermes_tavern_codestable_status.py` 更新为 Phase 375 合同。
- [x] `CURRENT_STATUS_PREFIX` 指向 `All phases 1-375 accepted`。
- [x] `STALE_STATUS_PREFIX` 指向 `All phases 1-374 accepted`。
- [x] `STALE_PHASE_MARKER` / `STALE_PHASE_MARKER_EN_DASH` 设为 `1-374` / `1–374`。
- [x] `REQUIRED_PHASE_LABELS` 包含 Phase 375。
- [x] `FINAL_STATUS_SUFFIX` 以 Phase 375 结尾，且只有一个 terminal `and`。
- [x] `phase_range = range(168, 376)`, `aggregate_range = "range(168, 376)"`。
- [x] 新增 split stale aggregate guard `stale_aggregate_range_375`。
- [x] Test source 中无 contiguous `range(168, 375)` literal（guard passed）。
- [x] Anchored `CURRENT_STATUS_PREFIX` / `FINAL_STATUS_SUFFIX` 赋值 guard 保持。
- [x] No-discovery-token guards（glob/rglob/iterdir/os.walk）保持。

## 3 验收场景核对

- [x] Architect read-only pass selected exactly one bounded Phase 375 status-sync slice and produced Phase 375 design/checklist artifacts。
- [x] S1: Codex executor 完成 attention.md + focused status test 修改，未创建 acceptance.md、未 stage/commit/push。
- [x] Architect read-only review returned `PASS` after checking the bounded dirty tree and status contract。
- [x] S2: Parent controller 验证 YAML/frontmatter/py_compile/focused pytest/static guards/git diff --check/full pytest，并创建本 acceptance report。

## 4 反向核对

- [x] 未修改 runtime/source/plugin/provider/gateway/CLI/config/dependency/compound/build/root docs/architecture/roadmap/requirements。
- [x] 未在 S1 期间创建 acceptance.md（S2 controller 创建）。
- [x] Hermes-native plugin architecture 和 SillyTavern asset compatibility 保持不变。
- [x] Adult-content safety boundary 保持不变，未添加 provider safety/adult/minors 行为改动。

## 5 架构归并

无架构维度变更。Phase 375 为纯 docs/status 同步。

## 6 requirement 回写

N/A — status-sync phase。

## 7 roadmap 回写

N/A — status-sync phase。

## 8 attention.md 候选盘点

无新规约。当前 attention 状态线已推至 Phase 375。

## 9 遗留

无。

## 10 Controller-Run Verification Evidence

| Command | Result |
|---------|--------|
| `validate-yaml --file phase375/design.md --require doc_type --require status --require feature --require implementation_ready` | passed |
| `validate-yaml --yaml-only phase375/checklist.yaml` | passed after S2 finalization |
| `validate-yaml --file phase375/acceptance.md --require doc_type --require status --require accepted_at` | passed after S2 finalization |
| `py_compile test_hermes_tavern_codestable_status.py` | OK |
| `focused pytest (PYTEST_DISABLE_PLUGIN_AUTOLOAD=1)` | 1 passed |
| `static Phase 375 status/scope guard` | no contiguous stale `range(168, 375)` literal; single anchored current/final constants; Phase 168-375 labels present; changed paths allowlisted |
| `full Tavern pytest via project Python` | passed after S2 finalization |
| `git diff --check` | clean |
| Changed/untracked whitespace/final-newline guard | clean |

Codex architect design JSONL produced the Phase 375 artifact. Codex executor JSONL advanced the status line/test/artifacts within the allowed file set. Codex architect review JSONL returned PASS. Parent controller reran validators, focused/static guards, full pytest, and diff checks before finalizing S2.
