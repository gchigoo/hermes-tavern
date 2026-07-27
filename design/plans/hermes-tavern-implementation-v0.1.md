# Hermes Tavern Phase 1-3 Implementation Plan

> **For Hermes:** Use subagent-driven-development or Codex CLI to implement this plan task-by-task.

**Goal:** Build the first usable Hermes Tavern plugin slice: `/rp` command interception, SQLite-backed session/card persistence, ST JSON card import, and start/end RP sessions.

**Architecture:** Implement as a bundled/user Hermes plugin under `plugins/hermes_tavern/` or `plugins/hermes-tavern/` following the existing plugin loader conventions. Use the existing `pre_gateway_dispatch` hook to intercept `/rp` commands and active RP sessions while allowing non-RP traffic to continue to normal Hermes. Keep runtime/model calls mocked or injectable in this phase.

**Tech Stack:** Python 3.11+, Hermes plugin system, gateway `MessageEvent`, SQLite stdlib, pytest.

---

## Read First

- `design/HERMES_TAVERN_DESIGN.md`
- `AGENTS.md`, especially plugin and testing sections
- `hermes_cli/plugins.py`
- `gateway/run.py` around `pre_gateway_dispatch`
- `tests/gateway/test_pre_gateway_dispatch.py`
- `tests/hermes_cli/test_plugins.py`
- `plugins/spotify/plugin.yaml` and `plugins/spotify/__init__.py` for simple bundled plugin shape

Do not modify `run_agent.py`, `cli.py`, or `gateway/run.py` unless a generic plugin hook is genuinely missing. Phase 1-3 should not need core edits.

---

## Acceptance Criteria for This Plan

By the end of Phase 3:

1. A Hermes Tavern plugin can be discovered/loaded by Hermes plugin loader.
2. `/rp help` returns a Tavern help message and skips normal Hermes dispatch.
3. `/rp status` reports no active session or active session details.
4. `/rp end` ends an active session and returns the chat to normal Hermes.
5. Plugin creates a SQLite DB under a profile-safe Hermes home path.
6. ST JSON character cards can be imported through a pure parser function.
7. A session can be started from an imported card through a testable command handler.
8. Tests cover command parsing, session keying, DB persistence, card parsing, and gateway hook behavior.

---

## Task 1: Create Plugin Skeleton

**Objective:** Add a loadable Hermes Tavern plugin with no behavior except registration.

**Files:**
- Create: `plugins/hermes_tavern/plugin.yaml`
- Create: `plugins/hermes_tavern/__init__.py`
- Test: `tests/plugins/test_hermes_tavern_plugin.py`

**Step 1: Write failing test**

Create a test that imports `plugins.hermes_tavern` and calls `register(ctx)` with a fake context exposing `register_hook`.

Expected assertion:

```python
assert fake_ctx.hooks == [("pre_gateway_dispatch", ANY_CALLABLE)]
```

**Step 2: Run test to verify failure**

```bash
python -m pytest tests/plugins/test_hermes_tavern_plugin.py -q -o 'addopts='
```

Expected: FAIL because plugin module does not exist.

**Step 3: Implement skeleton**

`plugin.yaml` should include:

```yaml
name: hermes-tavern
version: 0.1.0
description: "SillyTavern-compatible RP/novel runtime for Hermes Gateway."
author: Hermes Agent
kind: backend
```

`__init__.py` should define:

```python
def register(ctx) -> None:
    from plugins.hermes_tavern.gateway_hook import pre_gateway_dispatch
    ctx.register_hook("pre_gateway_dispatch", pre_gateway_dispatch)
```

Also create a stub `gateway_hook.py` with an allow-by-default handler.

**Step 4: Run test**

Expected: PASS.

---

## Task 2: Add Session Identity Utilities

**Objective:** Create deterministic session keys from gateway events.

**Files:**
- Create: `plugins/hermes_tavern/identity.py`
- Test: `tests/plugins/test_hermes_tavern_identity.py`

**Required behavior:**

Implement:

```python
def session_key_from_event(event) -> str:
    ...
```

The key must include:

- platform
- chat_id
- thread/topic id if present
- user_id

Use safe string conversion and fallbacks for missing attributes.

**Tests:**

- DM event key contains platform/chat/user.
- Group/topic event key differs when thread id differs.
- Missing optional fields do not raise.

**Verification:**

```bash
python -m pytest tests/plugins/test_hermes_tavern_identity.py -q -o 'addopts='
```

---

## Task 3: Add Command Parser

**Objective:** Parse `/rp` commands into a small structured object.

**Files:**
- Create: `plugins/hermes_tavern/commands.py`
- Test: `tests/plugins/test_hermes_tavern_commands.py`

**Implementation:**

Create:

```python
@dataclass(frozen=True)
class RPCommand:
    name: str
    args: list[str]
    raw: str


def parse_rp_command(text: str) -> RPCommand | None:
    ...
```

Required behavior:

- `hello` → `None`
- `/rp` → command `help`
- `/rp help` → command `help`
- `/rp status` → command `status`
- `/rp end` → command `end`
- `/rp start Alice` → command `start`, args `["Alice"]`
- tolerate extra whitespace
- do not treat `/rpx help` as `/rp`

**Verification:**

```bash
python -m pytest tests/plugins/test_hermes_tavern_commands.py -q -o 'addopts='
```

---

## Task 4: Add SQLite Store and Migrations

**Objective:** Add profile-safe SQLite persistence for cards, sessions, and messages.

**Files:**
- Create: `plugins/hermes_tavern/db.py`
- Test: `tests/plugins/test_hermes_tavern_db.py`

**Implementation:**

Use stdlib `sqlite3` only.

Functions/classes:

```python
class TavernStore:
    def __init__(self, db_path: str | Path | None = None): ...
    def connect(self) -> sqlite3.Connection: ...
    def migrate(self) -> None: ...
```

If `db_path` is None, compute:

```text
get_hermes_home() / "plugins" / "hermes-tavern" / "data" / "tavern.sqlite3"
```

Tables for this phase:

```sql
cards(id TEXT PRIMARY KEY, name TEXT NOT NULL, data_json TEXT NOT NULL, created_at TEXT NOT NULL)
sessions(id TEXT PRIMARY KEY, session_key TEXT UNIQUE NOT NULL, card_id TEXT, status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)
messages(id TEXT PRIMARY KEY, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL, metadata_json TEXT)
```

**Tests:**

- `migrate()` creates tables.
- migration is idempotent.
- custom temp db path works.

**Verification:**

```bash
python -m pytest tests/plugins/test_hermes_tavern_db.py -q -o 'addopts='
```

---

## Task 5: Add Session Repository Methods

**Objective:** Add CRUD helpers for active sessions.

**Files:**
- Modify: `plugins/hermes_tavern/db.py`
- Test: `tests/plugins/test_hermes_tavern_sessions.py`

**Methods:**

```python
def get_active_session(self, session_key: str) -> dict | None: ...
def start_session(self, session_key: str, card_id: str | None = None) -> dict: ...
def end_session(self, session_key: str) -> bool: ...
def append_message(self, session_id: str, role: str, content: str, metadata: dict | None = None) -> str: ...
```

**Tests:**

- starting creates active session;
- starting same key returns or updates the same active session predictably;
- ending marks session ended;
- ended session is no longer active;
- appended messages persist.

**Verification:**

```bash
python -m pytest tests/plugins/test_hermes_tavern_sessions.py -q -o 'addopts='
```

---

## Task 6: Add ST JSON Card Parser

**Objective:** Parse SillyTavern JSON character cards into canonical fields.

**Files:**
- Create: `plugins/hermes_tavern/importers/__init__.py`
- Create: `plugins/hermes_tavern/importers/cards.py`
- Test: `tests/plugins/test_hermes_tavern_cards.py`

**Canonical result:**

```python
@dataclass(frozen=True)
class CharacterCard:
    id: str
    name: str
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""
    alternate_greetings: list[str] = field(default_factory=list)
    creator_notes: str = ""
    raw: dict = field(default_factory=dict)
```

**Support:**

- ST V2 style: `{ "spec": "chara_card_v2", "data": {...} }`
- loose/direct style: `{ "name": "...", "description": "..." }`

**Tests:**

- V2 sample parses name/description/personality/scenario/first_mes.
- direct sample parses.
- missing name raises `ValueError`.
- raw JSON preserved.

**Verification:**

```bash
python -m pytest tests/plugins/test_hermes_tavern_cards.py -q -o 'addopts='
```

---

## Task 7: Persist Imported Cards

**Objective:** Add DB helpers for storing and listing parsed cards.

**Files:**
- Modify: `plugins/hermes_tavern/db.py`
- Test: `tests/plugins/test_hermes_tavern_card_store.py`

**Methods:**

```python
def save_card(self, card: CharacterCard) -> str: ...
def list_cards(self) -> list[dict]: ...
def get_card(self, card_id_or_name: str) -> dict | None: ...
```

**Tests:**

- save card persists JSON;
- list cards returns names;
- get by id works;
- get by exact name works.

**Verification:**

```bash
python -m pytest tests/plugins/test_hermes_tavern_card_store.py -q -o 'addopts='
```

---

## Task 8: Implement Basic Command Handler

**Objective:** Implement `/rp help`, `/rp status`, `/rp end`, and `/rp start <card>` as pure async/sync handler logic.

**Files:**
- Create: `plugins/hermes_tavern/runtime.py`
- Modify: `plugins/hermes_tavern/commands.py`
- Test: `tests/plugins/test_hermes_tavern_runtime.py`

**Implementation:**

Create a runtime class:

```python
class TavernRuntime:
    def __init__(self, store: TavernStore | None = None): ...
    async def handle_command(self, command: RPCommand, event, gateway=None) -> str: ...
```

Required command behavior:

- `help` returns command list.
- `status` reports no active session or current card/status.
- `end` ends session and reports result.
- `start <card>` looks up card, starts active session, and returns first greeting if available.

Do not call external LLMs in this phase.

**Verification:**

```bash
python -m pytest tests/plugins/test_hermes_tavern_runtime.py -q -o 'addopts='
```

---

## Task 9: Wire Gateway Hook

**Objective:** Make `pre_gateway_dispatch` intercept `/rp` commands and active session messages.

**Files:**
- Modify: `plugins/hermes_tavern/gateway_hook.py`
- Test: `tests/plugins/test_hermes_tavern_gateway_hook.py`

**Behavior:**

- Non-`/rp` message with no active session returns `{"action": "allow"}` or `None`.
- `/rp help` returns skip and sends help text through gateway adapter if possible.
- `/rp status` returns skip and sends status text.
- Active session non-command message returns skip and stores user message; actual model reply can be a placeholder in Phase 1-3, e.g. `"[Hermes Tavern runtime placeholder]"`.
- `/rp end` returns skip and deactivates session.

**Testing approach:**

Use fake event, fake gateway/adapters, and temp SQLite DB. Do not require a live Telegram/Feishu gateway.

**Verification:**

```bash
python -m pytest tests/plugins/test_hermes_tavern_gateway_hook.py -q -o 'addopts='
```

---

## Task 10: Run Focused Regression Suite

**Objective:** Ensure plugin tests and existing gateway hook tests pass.

**Commands:**

```bash
python -m pytest \
  tests/plugins/test_hermes_tavern_*.py \
  tests/gateway/test_pre_gateway_dispatch.py \
  tests/hermes_cli/test_plugins.py::TestPluginHooks \
  -q -o 'addopts='
```

If `TestPluginHooks` class name differs, run:

```bash
python -m pytest tests/hermes_cli/test_plugins.py -q -o 'addopts='
```

Expected: all selected tests pass.

---

## Codex Execution Prompt

Use this as the first Codex prompt for a narrow implementation slice:

```text
Implement Hermes Tavern Phase 1-3 foundation from design/plans/hermes-tavern-implementation-v0.1.md.

Scope for this Codex run:
- Tasks 1-4 only: plugin skeleton, session identity utilities, /rp command parser, SQLite store/migrations.
- Follow TDD: add tests first, verify they fail, implement, then run focused tests.
- Do not modify run_agent.py, cli.py, or gateway/run.py.
- Use profile-safe get_hermes_home() for default DB path.
- Keep all runtime/model calls out of scope.
- At the end, report files changed and exact test commands/results.
```

After Tasks 1-4 pass, run a second Codex session for Tasks 5-9.
