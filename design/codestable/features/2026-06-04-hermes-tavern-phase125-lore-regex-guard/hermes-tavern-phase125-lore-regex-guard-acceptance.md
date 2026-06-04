---
doc_type: feature-acceptance
feature: 2026-06-04-hermes-tavern-phase125-lore-regex-guard
status: accepted
verified_at: "2026-06-04"
summary: >
  Lore Regex Complexity Guard is accepted after S1 matcher/runtime implementation,
  S2 architecture/root-design writeback, and controller-run verification. Runtime
  lore regex keys now use a local bounded matcher guard for over-length and
  nested-quantifier patterns while preserving SillyTavern lorebook compatibility
  and keeping regex postprocessors deferred.
tags:
  - lorebook
  - regex
  - safety
  - hardening
  - acceptance
---

## 1. Interface Contract

- `src/hermes_tavern/lorebook.py` exports `match_lorebook_entries()` as the primary lore match contract.
- Matching returns `LoreMatchResult(matches, excluded, token_budget, debug)` where:
  - `matches` contain included `LoreMatch` rows and generated prompt modules.
  - `excluded` contains skip reason strings.
  - `debug` reflects matcher outcomes for prompt and `/rp lore test` visibility.
- For regex mode, `_any_key_matches()` applies a local guard to each regex key before `re.search`.
- Guard rejects are bounded to deterministic reasons only:
  - `regex rejected: pattern too long`
  - `regex rejected: nested quantifier`
- Invalid syntax is still surfaced as:
  - `regex error: <re.error>`
- Guard applies to both primary and secondary key evaluation, and is evaluated before provider calls or network steps.

## 2. Behavior and Decisions

- Added local complexity limits directly in lore matcher behavior:
  - `_MAX_REGEX_KEY_LENGTH = 256` in `src/hermes_tavern/lorebook.py`.
  - `_NESTED_QUANTIFIER_RE` detects nested quantified groups such as `(a+)+`.
- Behavior changed:
  - Regex keys > 256 chars are rejected before search.
  - Nested quantified regex keys are rejected before search.
  - Non-regex keys and existing substring behavior are unchanged.
  - Existing `re.error` capture path remains unchanged and still returns `regex error: ...`.
- Guard does not mutate importer data (`raw_json`) and does not alter schema, command parsing, provider routing, or postprocessing flow.

## 3. Acceptance Scenario Evidence

- `src/hermes_tavern/lorebook.py`
  - `_any_key_matches()` returns `regex rejected: pattern too long` when `len(key) > _MAX_REGEX_KEY_LENGTH`.
  - `_NESTED_QUANTIFIER_RE` and `re.search` are guarded identically for primary and secondary keys under regex mode.
  - `regex error:` formatting is still produced on compile/execution exception from `re.search`.
- `tests/test_hermes_tavern_lorebooks.py`
  - `test_lorebook_nested_quantifier_is_rejected_before_search` verifies no `re.search` call is performed and reason is `regex rejected: nested quantifier`.
  - `test_lorebook_regex_longer_than_256_is_rejected` verifies `regex rejected: pattern too long`.
  - `test_lorebook_secondary_regex_rejection_excludes_entry` verifies secondary keys use the same guard.
- `tests/test_hermes_tavern_lore_runtime.py`
  - `test_lore_runtime_rejects_nested_quantifier_without_crash` verifies `/rp lore test` prints bounded rejection and does not include blocked content.
- Existing `/rp lore test`/debug behavior remains as existing contract: bounded exclusion reasons are observable, no crash on excluded regex.

## 4. Architecture and Root Design Merge

- `design/codestable/architecture/ARCHITECTURE.md` updates are included:
  - `lorebook.py` module index now notes local regex complexity guard.
  - Capability summary includes Phase 125 lore regex guard.
  - Known constraints section includes the bounded regex guard + deferred non-goals.
- `design/HERMES_TAVERN_DESIGN.md` updates are included:
  - §6.6 now documents current matcher behavior for regex complexity guard.
  - §14 explicitly separates Phase 125 matcher guard from ST-style output postprocessing/hooks.
  - §21 Phase 7 acceptance note links to this acceptance evidence.

## 5. Requirement and Roadmap Disposition

- No requirement or roadmap frontmatter fields are defined in this feature artifact.
- No requirement/roadmap documents are created in S2, per boundary.

## 6. Attention Candidates

- No new persistent engineering, tooling, or environment changes are required from this acceptance slice.

## 7. Reverse Scope and Deferred Boundaries

- No regex postprocessor/output rewrite implementation is included in this slice.
- No `write/rewrite/expand/compress` command behavior changes.
- No importer/schema/command/provider/runtime architecture change.
- No extension hooks, novel import/archive, cloud sync, collaboration, backend account, credential persistence, provider safety bypass, or minor/underage paths were introduced.

## 8. Executor Verification

- S2 is documentation/writeback only; runtime/source/test behavior was not modified in this lane.
- Executor created the acceptance report draft, checklist handoff text, and architecture/root-design writeback, leaving final accepted/completed status for controller verification.
- Executor-side validators passed for the acceptance report and checklist, and protected core diff check returned no protected file changes.

## 9. Controller Verification

Controller reran the implementation and CodeStable gates after S2 docs/status edits:

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/lorebook.py tests/test_hermes_tavern_lorebooks.py tests/test_hermes_tavern_lore_runtime.py` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_lorebooks.py tests/test_hermes_tavern_lore_runtime.py -q -o 'addopts='` — passed; 20 passed in 0.33s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_runtime.py -k lore -q -o 'addopts='` — passed; 3 passed, 41 deselected in 0.18s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` — passed; 821 passed in 32.87s.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase125-lore-regex-guard/design.md --require doc_type --require status` — passed; 1 passed, 0 failed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-04-hermes-tavern-phase125-lore-regex-guard/checklist.yaml` — passed; 1 passed, 0 failed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase125-lore-regex-guard/hermes-tavern-phase125-lore-regex-guard-acceptance.md --require doc_type --require status` — passed; 1 passed, 0 failed.
- `git diff --check` — passed.
- `git diff --name-only -- run_agent.py cli.py gateway/run.py` — passed; no protected core file diffs.
- Controller diff review confirmed only the four S2 docs/status files changed and no current capability was added for regex postprocessors, output rewrite hooks, provider behavior, novel import/archive, credential persistence, safety bypass, or minor/underage paths.

Final acceptance status: **ACCEPTED**.

## 10. Residuals

- None for Phase 125 S2. Future ST Regex-style output postprocessing remains deferred outside this feature.
