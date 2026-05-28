# Hermes Tavern Phase 15 — Session Browser / Multi-session v1

## Goal

Make Hermes Tavern usable as a Telegram/mobile Tavern entry with multiple RP branches per platform/chat/thread/user scope.

## User commands

| Command | Behavior |
|---|---|
| `/rp sessions [all]` | List sessions in the current event scope. Default shows active sessions; `all` includes archived/ended sessions. Output includes short id, status, current marker, card name/id, and optional title. |
| `/rp switch <session-id-prefix>` | Make an existing session the active session for the current event identity. The previous active session is archived to free the unique `session_key`. |
| `/rp rename <name>` | Set a human-readable title on the current active session. |
| `/rp archive` | Archive the current active session and leave the current scope with no active session. |
| `/rp clone [name]` | Create a new active branch with copied card/config/message history and optional title. The source session is not mutated; use `/rp switch <id>` to continue in the clone. |

## Data model

Phase 15 keeps the existing SQLite-only store and adds nullable columns to `sessions`:

- `title TEXT` — user-facing label for list/switch flows.
- `scope_key TEXT` — stable scope grouping; backfilled from `session_key` for older rows.

Because `sessions.session_key` remains unique and existing runtime code resolves the active session by exact event identity, switching archives the previous active row by changing its `session_key` to its own id and setting `status='archived'`, then moves the selected row onto the current event `session_key` with `status='active'`.

Cloning creates a separate active row with a generated branch key (`<scope>:b:<short-id>`), copies card/config fields, resets live confirmation to false, and copies message history using monotonic clone timestamps so `get_recent_messages` preserves original message order.

## Store helpers

- `list_sessions_for_scope(scope_key, include_all=False)`
- `rename_session(session_id, title)`
- `archive_active_session(session_key)`
- `clone_session(from_session_id, scope_key, title=None)`
- `get_session_by_id_prefix(prefix)`
- `switch_to_session(current_session_key, target_session_id)`

## Safety / constraints

- Mock-first behavior preserved; no live provider calls are added.
- No new runtime dependencies.
- Existing `/rp start`, `/rp end`, `/rp history`, `/rp retry`, `/rp undo`, `/rp edit last` behavior remains compatible.
- Archived/ended sessions are hidden from default listing but visible with `/rp sessions all`.

## Verification

- Python compile gate for plugin/tests.
- Full Hermes Tavern plugin pytest suite.
- CodeStable checklist YAML validation.
