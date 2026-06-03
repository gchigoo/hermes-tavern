# 2026-06-03-shared-pagination-helper scan

Scope: shared pagination argument parsing for Hermes Tavern runtime command modules. Inspected `src/hermes_tavern/runtime_utils.py`, `runtime_assets.py`, `runtime_turns.py`, `runtime_sessions.py`, `runtime_memory.py`, `runtime_persona.py`, `runtime_debug.py`, `runtime_images.py`, `runtime_lore.py`, and related tests. Found one low-risk L2 duplication item suitable for a bounded refactor.

## Findings

1. Repeated plain `[limit] [page]` parsing appears in six handlers with the same semantics: default limit, max limit clamp, page lower-bound clamp, usage string on non-integer input, and caller-local total-page clamping.
   - `cards`: default 10, max 50.
   - `history`: default 10, max 50.
   - `sessions`: default 10, max 25 after optional `all`.
   - `memory list`: default 10, max 25 after `list`.
   - `persona list`: default 10, max 25 after `list`.
   - `debug prompt`: default 8, max 30 after optional `prompt`.

2. `runtime_utils.py` is the best helper home. It already contains shared runtime command helpers and has direct unit coverage.

3. Existing tests cover default, limit-only, page 2, overflow clamp, usage errors, and navigation strings for the selected slice.

## Chosen Refactor Item

- R1: Extract a small `parse_pagination(args, *, default_limit, max_limit)` helper returning `(limit, page)` or `None` on parse failure, then migrate the six plain callers listed above.

Method mapping: M-L2-01 Extract Function, with M-L1-04 Characterization Test via existing command-output tests plus focused helper unit tests.

## Rejected / Out Of Scope

- `runtime_lore._parse_ref_limit_page()`: out of scope because it handles `<ref> [limit] [page]` and allows spaces in refs.
- `runtime_images.image_history()`: out of scope because current overflow-page behavior differs from the other callers; migrate only after characterization for page overflow.
- Attachment parsing, reference parsing, command syntax, output text, DB pagination queries, and performance/index work are out of scope.
