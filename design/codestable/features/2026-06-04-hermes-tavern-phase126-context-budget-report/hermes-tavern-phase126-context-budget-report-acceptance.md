---
doc_type: feature-acceptance
feature: "2026-06-04-hermes-tavern-phase126-context-budget-report"
status: accepted
date: "2026-06-04"
summary: >
  Phase 126 Context Budget Report v1 is accepted: `/rp debug context [limit]
  [page]` is implemented as a read-only context/prompt composition report,
  command/docs visibility is present, architecture and root-design writeback are
  complete, and controller verification passed.
---

# Phase 126: Context Budget Report v1 Acceptance

> Stage: CodeStable feature acceptance / architecture writeback
> Acceptance date: 2026-06-04
> Design: `design/codestable/features/2026-06-04-hermes-tavern-phase126-context-budget-report/design.md`

## 1. Interface Contract Check

- [x] `/rp debug context [limit] [page]` is the accepted command shape.
  - Code evidence: `src/hermes_tavern/runtime.py` dispatches `debug context` through the existing debug command family; `src/hermes_tavern/commands.py` exposes help for the literal.
  - Test evidence: `tests/test_hermes_tavern_commands.py` and `tests/test_hermes_tavern_readme_docs.py` cover command/help/docs visibility.
- [x] No active session returns `No active Hermes Tavern session.`.
  - Test evidence: `tests/test_hermes_tavern_runtime.py` no-active-session coverage.
- [x] Active session without a card returns `No character card bound to this session.`.
  - Test evidence: `tests/test_hermes_tavern_runtime.py` no-card coverage.
- [x] Invalid pagination returns `Usage: /rp debug context [limit] [page]`.
  - Test evidence: command/runtime invalid-pagination assertions.
- [x] The report includes the accepted fields: header, card, renderer, model descriptor, context window, estimated tokens, module/history/rendered-message counts, omitted-layer summary, row token estimates, and prev/next pagination hints.
  - Code evidence: `src/hermes_tavern/runtime_debug.py` `debug_context(...)` report builder.
  - Test evidence: active report, row-estimate, and pagination tests.

## 2. Behavior And Decision Check

- [x] The command is read-only.
  - Evidence: focused tests prove message counts/session bindings do not change.
- [x] The command does not call a live provider.
  - Evidence: tests use an exploding generation adapter and verify it is not invoked.
- [x] The command does not persist credentials or provider debug data.
  - Evidence: source review and reverse-scope diff show no DB/schema/provider-routing changes.
- [x] The command uses existing prompt compilation/rendering output and existing token-estimate heuristics.
  - Evidence: implementation is localized to runtime debug/reporting and does not change `PromptCompiler`, provider routing, storage, or generation behavior.
- [x] Omitted-layer reporting remains shallow v1.
  - Evidence: acceptance keeps trimming, summarization, vector retrieval, provider tokenization, and full excluded-lore explanations deferred.

## 3. Acceptance Scenario Check

| Design criterion | Result | Evidence |
|---|---|---|
| No active session boundary | Passed | Runtime no-active-session tests |
| Card-backed active session report | Passed | Runtime active report tests |
| Pagination `2 1` / `2 2` | Passed | Runtime pagination tests with prev/next hints |
| Invalid pagination usage | Passed | Command/runtime usage tests |
| Active session without card | Passed | Runtime no-card tests |
| Row token estimates and mobile previews | Passed | Runtime row estimate / preview assertions |
| No message/session mutation | Passed | Read-only runtime tests |
| No live provider call or credential persistence | Passed | Exploding adapter test plus source/diff review |
| Help and README/docs visibility | Passed | Command-table and README docs tests |
| Reverse-scope guard | Passed | Docs/status-only S3 diff; no protected core/source/test/README diffs in final slice |

## 4. Terminology Consistency

- **Context Budget Report** remains a read-only mobile report for estimated prompt/context token composition, not an enforcement manager.
- **Context Row** remains an ephemeral displayed item from compiled modules, history, rendered messages, or pending user-message slot.
- **Omitted Layer** remains a shallow summary of known absent configured sources, not a full retrieval/exclusion engine.
- **Token Estimate** remains the existing local heuristic and is not provider-specific token accounting.

## 5. Architecture Writeback

- [x] `design/codestable/architecture/ARCHITECTURE.md` records `/rp debug context [limit] [page]` as current read-only debug context budget reporting.
- [x] `design/HERMES_TAVERN_DESIGN.md` records current Context Budget Report v1 behavior while preserving future/deferred context budget manager responsibilities.
- [x] The writeback is descriptive only; it does not make trimming, summarization, vectorization, provider tokenization, provider/model routing, prompt mutation, or enforcement current.

## 6. Requirement Writeback

No requirement writeback was required. The Phase 126 design has no `requirement` frontmatter and this slice is a narrow observability/debug surface rather than a new product requirement document.

## 7. Roadmap Writeback

No roadmap writeback was required. The Phase 126 design has no `roadmap` / `roadmap_item` frontmatter, and `design/codestable/roadmap` is not an active roadmap directory in this project snapshot.

## 8. Attention Candidates

No new startup-wide `attention.md` candidate was found. Existing attention guidance already covers the relevant constraints: plugin-only architecture, protected core files, no credential persistence, and verification commands.

## 9. Deferred Boundaries And Residuals

Still deferred / explicitly not implemented:

- context budget enforcement
- prompt trimming, summarization, or compression
- vectorization or retrieval-memory redesign
- provider-specific tokenizer integration
- provider/model routing changes
- prompt mutation / prompt manager movement commands
- regex postprocessor or output rewrite hook
- credential persistence
- minors/underage paths or provider safety bypasses
- cloud/collaboration scope
- archive import/export scope

Residuals: none for Phase 126 v1 after controller verification.

## 10. Controller Verification

- `codex --profile architect exec --json --color never --disable image_generation --sandbox read-only --cd /Users/steven/Projects/hermes-tavern <Phase 126 S3 artifact prompt>`
  - Passed; artifact: `/tmp/hermes-tavern-architect-phase126-s3.jsonl`.
- `codex --profile executor exec --json --color never --disable image_generation --sandbox workspace-write --cd /Users/steven/Projects/hermes-tavern <Phase 126 S3 docs/status prompt>`
  - Completed; JSONL: `/tmp/hermes-tavern-executor-phase126-s3.jsonl`.
  - One early executor inspection command failed before the acceptance file existed, then executor created the file and later validations passed; no rate-limit/429/exhaustion signal occurred.
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_debug.py src/hermes_tavern/runtime.py src/hermes_tavern/commands.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
  - Passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts='`
  - Passed; 104 passed in 3.65s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='`
  - Passed; 830 passed in 31.49s.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase126-context-budget-report/design.md --require doc_type --require status`
  - Passed; 1 passed, 0 failed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-04-hermes-tavern-phase126-context-budget-report/checklist.yaml`
  - Passed; 1 passed, 0 failed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase126-context-budget-report/hermes-tavern-phase126-context-budget-report-acceptance.md --require doc_type --require status --require feature`
  - Passed; 1 passed, 0 failed.
- `git diff --check`
  - Passed.
- `git diff --name-only -- run_agent.py cli.py gateway/run.py`
  - Passed; no protected core file diffs.
