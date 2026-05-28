---
feature: 2026-05-22-hermes-tavern-phase32-gateway-security-session-isolation
summary: Gateway import path trust policy and scoped Tavern session switching.
tags: [hermes-tavern, gateway, security, session-isolation]
---

# Hermes Tavern Phase 32: Gateway Security and Session Isolation

## Goal

Close two P0 issues in Hermes Tavern without changing the database schema:

- Gateway/mobile `/rp ... import <path>` commands must not read arbitrary local files.
- `/rp switch <prefix>` must resolve sessions only inside the caller's Tavern scope.

## Design

Asset import trust is centralized in `plugins/hermes_tavern/import_policy.py`.
The helper treats event objects with gateway source/platform identity as
untrusted for explicit local paths. A gateway event can import exactly one local
attachment with no explicit path, or can explicitly name a path only when it
normalizes to one of the local attachment paths on the same event and has an
allowed suffix. Remote URLs are rejected in gateway context. Event-like objects
without gateway identity remain trusted for CLI/local tests and existing
explicit path workflows.

Card, preset, lorebook, and persona import commands all route through the same
policy helper before calling their importer. Rejections are short and do not
echo full sensitive paths.

Session switching now uses a scoped store query,
`list_sessions_by_id_prefix_for_scope`, before activation. The query filters by
the caller's `scope_key` and returns all same-scope prefix matches. `/rp switch`
returns a clear ambiguity message when the prefix is not unique in that scope,
and `switch_to_session` refuses direct cross-scope activation as a defense in
depth.

## Non-Goals

- No schema migration or table changes.
- No provider or network calls.
- No changes to unrelated Tavern commands, import formats, or browser output.
