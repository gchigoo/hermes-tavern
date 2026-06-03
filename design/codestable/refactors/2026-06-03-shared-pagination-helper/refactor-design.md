---
doc_type: refactor-design
refactor: 2026-06-03-shared-pagination-helper
status: approved
scope: Extract shared parsing for plain Hermes Tavern `[limit] [page]` command arguments only.
summary: Add a small runtime pagination helper and migrate six behavior-compatible callers without changing command syntax or output text.
---

# shared pagination helper refactor design

## 1. Scope

Selected from scan: R1 only.

Implement:
- Add `parse_pagination(args, *, default_limit, max_limit)` in `src/hermes_tavern/runtime_utils.py`.
- Add direct tests in `tests/test_hermes_tavern_runtime_utils.py`.
- Migrate `cards`, `history`, `sessions`, `memory_list`, `persona_list`, and `debug_prompt`.

Do not implement:
- `lore inspect` reference-aware parser.
- `image history`.
- Attachment parsing, reference parsing, DB query behavior, output formatting, or command metadata changes.

Risk: low. Estimated executor effort: one small helper, six local call-site replacements, focused tests.

## 2. Behavior-Equivalence Requirements

- Defaults remain identical per command.
- Limit clamps remain identical: lower bound 1, caller-specific max.
- Page lower-bound clamp remains `max(1, int(value))`.
- Non-integer limit or page returns the exact existing usage string from each caller.
- Extra args after the first two pagination args remain ignored, matching current behavior.
- Total-page clamping and offset calculation remain caller-owned and unchanged.
- User-visible command syntax and output text must not change.

## 3. Execution Order

Step 1: Add helper tests.
- Method: M-L1-04 Characterization Test.
- Cover empty args, limit clamp, negative page clamp, invalid limit, invalid page, and ignored trailing args.

Step 2: Add helper.
- Method: M-L2-01 Extract Function.
- Implement in `runtime_utils.py`; keep API small and command-agnostic.

Step 3: Migrate six callers.
- Method: M-L2-01 Extract Function.
- Replace only parsing blocks; preserve local usage strings and existing total-page logic.

Step 4: Validate.
- Run focused helper and command tests.
- Run full Tavern pytest glob.
- Validate checklist YAML.

## 4. Rollback Strategy

Revert this refactor as one small change set:
- Remove `parse_pagination()` and its tests.
- Restore the six inline parsing blocks from git.
- Re-run the focused command tests listed in the checklist.

## 5. Acceptance / Apply-Note Expectations

Executor should create `design/codestable/refactors/2026-06-03-shared-pagination-helper/apply-note.md` with:
- `doc_type: refactor-apply-note`
- `refactor: 2026-06-03-shared-pagination-helper`
- changed files
- exact commands run and results
- confirmation that checklist statuses were not marked done/passed
- any deviations or "none"

Acceptance requires all validation commands passing and no changes to forbidden Tavern plugin files, credential persistence, Hermes home handling, command syntax, or output text.
