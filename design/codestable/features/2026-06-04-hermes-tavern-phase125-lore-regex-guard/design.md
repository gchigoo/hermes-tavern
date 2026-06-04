---
doc_type: feature-design
feature: 2026-06-04-hermes-tavern-phase125-lore-regex-guard
status: approved
summary: >
  Add a local complexity guard for imported lorebook regex keys so malformed or
  high-risk regex entries are excluded before matching instead of stalling prompt
  assembly or /rp lore test.
tags: [lorebook, regex, safety, hardening, prompt]
---

# Phase 125: Lore Regex Complexity Guard

> Approval note: approved for unattended S1 implementation only. This approval
> is limited to the matcher-level guard and focused tests; acceptance/writeback
> remains deferred.

## 0. Terms

| Term | Meaning | Conflict guard |
|---|---|---|
| Lore Regex Key | A lorebook entry key with `regex` enabled, imported from ST world info/lorebook data. | Not a regex postprocessor or output rewrite hook. |
| Regex Complexity Guard | A local pre-search check that rejects high-risk regex keys before `re.search`. | Not a provider safety bypass and not content moderation. |
| Rejected Regex Entry | A lore entry excluded with a debug reason such as `regex rejected: nested quantifier`. | The entry remains stored/imported; only matching excludes it. |
| Lore Matcher | `match_lorebook_entries()` in `src/hermes_tavern/lorebook.py`. | Current prompt and `/rp lore test` caller remain unchanged. |

## 1. Decisions And Constraints

Need:
- Imported ST lorebooks can contain regex keys. Current invalid regexes are excluded, but valid catastrophic patterns can still be sent directly to Python `re.search`.
- The review gap calls out gateway-worker stalls from user-supplied regex lore entries.

Success:
- Ordinary literal keys and normal regex keys still match.
- Invalid regex keys still return a `regex error` exclusion.
- High-risk regex keys are excluded before search with a bounded reason.
- Prompt assembly and `/rp lore test` continue without provider/network calls.

Explicit non-goals:
- No lorebook import format changes.
- No disabling regex entries globally.
- No regex postprocessor, write/rewrite/expand/compress command, outline editing, character state, relationship state, novel import, ZIP/archive import, cloud sync, collaboration, backend accounts, provider credential persistence, provider safety bypass, or minors/underage content path.
- No protected core-file edits.

Key decisions:
1. Add the guard in `src/hermes_tavern/lorebook.py`, directly before regex matching.
2. Reject regex keys longer than 256 characters.
3. Reject nested quantified groups such as `(a+)+`, `(.+)*`, or `([a-z]+){2,}` with reason `regex rejected: nested quantifier`.
4. Preserve existing `re.error` handling for malformed patterns.
5. Do not mutate stored lorebook rows; this is a runtime matching decision only.

## 2. Current -> Change

### 2.1 Noun Layer

Current:
- Lorebook importers preserve `regex` flags and raw keys.
- `match_lorebook_entries()` returns `LoreMatchResult(matches, excluded, debug)`.
- Exclusion reasons are already surfaced by `/rp lore test` and debug output.

Change:
- Add `MAX_REGEX_KEY_CHARS = 256`.
- Add a small helper, e.g. `_regex_rejection_reason(pattern: str) -> str | None`.
- New exclusion reasons:
  - `regex rejected: pattern too long`
  - `regex rejected: nested quantifier`

No DB schema, command, importer, or prompt module type changes.

### 2.2 Orchestration Layer

Current flow:

```text
entries -> match_lorebook_entries
  -> _entry_matches
  -> _any_key_matches
  -> re.search(regex_key, haystack)
```

Changed flow:

```text
entries -> match_lorebook_entries
  -> _entry_matches
  -> _any_key_matches
  -> _regex_rejection_reason(regex_key)
      -> rejected reason? exclude entry
      -> no rejection? compile/search as today
```

Flow constraints:
- Guard runs only for `regex=True`.
- Non-regex substring matching is unchanged.
- Constant entries are unchanged.
- Secondary regex keys use the same guard as primary regex keys.
- Rejected entries do not raise and do not block matching other entries.

### 2.3 Mount Points

| Mount | Purpose |
|---|---|
| `src/hermes_tavern/lorebook.py` | Add regex guard constants/helper and wire it before `re.search`. |
| `tests/test_hermes_tavern_lorebooks.py` | Add matcher tests for valid regex, invalid regex preservation, long regex rejection, and nested quantifier rejection before search. |
| `tests/test_hermes_tavern_lore_runtime.py` | Add `/rp lore test` coverage proving rejected regex reasons are user-visible and bounded. |

### 2.4 Slicing

1. S1: Matcher guard and focused tests only.
2. S2: Acceptance/writeback only, deferred to controller or a later acceptance lane.

### 2.5 Structure Health

No pre-feature micro-refactor.

- `lorebook.py` is small and cohesive for matcher behavior.
- Existing lorebook tests are the right place for pure matcher cases.
- Runtime lore tests already cover `/rp lore test`, so a focused output test belongs there.
- Creating a new regex policy module would be unnecessary for this narrow guard.

## 3. Acceptance Criteria

1. A normal regex key such as `\bmoon(s)?\b` still matches expected text.
2. A malformed regex key such as `[` is excluded with a `regex error` reason.
3. A nested-quantifier regex key such as `(a+)+$` is excluded with `regex rejected: nested quantifier`.
4. A regex key longer than 256 characters is excluded with `regex rejected: pattern too long`.
5. Rejected regex keys are not passed to `re.search`.
6. `/rp lore test <message>` shows the rejected regex reason in the excluded sample and does not crash.
7. Non-regex lore keys, constant entries, probability handling, priorities, and token-budget behavior are unchanged.
8. Reverse-scope scan confirms no protected core edits and no prohibited feature families.

## 4. Risks

- False positives may exclude an advanced but legitimate ST regex. The guard is intentionally conservative: it targets long patterns and nested quantified groups only.
- This is a heuristic, not a full regex timeout engine. It reduces common catastrophic cases without adding dependencies or changing provider/runtime architecture.
- If later regex features need richer compatibility, that should be a separate design with explicit product review.

## 5. Architecture Writeback

On acceptance, update:
- `design/codestable/architecture/ARCHITECTURE.md`: add the lore regex complexity guard to known constraints or plugin capability summary.
- `design/HERMES_TAVERN_DESIGN.md`: note that lorebook regex keys are supported with a local complexity guard; keep regex postprocessors/output rewrite hooks deferred.
