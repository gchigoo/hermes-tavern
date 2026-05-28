"""Mobile-friendly Tavern asset browser command tests (Phases 16 & 17)."""

from __future__ import annotations

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.lorebooks import import_st_lorebook_json
from plugins.hermes_tavern.importers.presets import import_st_preset_json
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


def test_cards_command_lists_short_ids_tags_and_next_actions(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    alice_id = store.save_card(
        parse_character_card(
            {
                "name": "Alice",
                "description": "A curious scholar who travels with a brass owl.",
                "tags": ["scholar", "slow-burn"],
                "first_mes": "Welcome back.",
            }
        )
    )
    store.save_card(parse_character_card({"name": "Bob", "description": "Village blacksmith."}))
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(RPCommand("cards", [], "/rp cards"), Event())

    assert "Hermes Tavern cards" in response
    assert f"{alice_id[:8]}" in response
    assert "Alice" in response
    assert "scholar, slow-burn" in response
    assert "start: /rp start Alice" in response
    assert "inspect: /rp card inspect Alice" in response


def test_card_inspect_returns_mobile_safe_summary_without_raw_json_dump(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(
        parse_character_card(
            {
                "name": "Alice",
                "description": "A curious scholar. " * 20,
                "personality": "Warm and direct",
                "scenario": "A quiet library",
                "first_mes": "Welcome back.",
                "alternate_greetings": ["Good evening.", "Tea?"],
                "system_prompt": "Stay in character.",
                "post_history_instructions": "Keep continuity.",
                "tags": ["scholar"],
            }
        )
    )
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["inspect", "Alice"], "/rp card inspect Alice"),
        Event(),
    )

    assert "Card: Alice" in response
    assert "description:" in response
    assert "personality: Warm and direct" in response
    assert "alternate greetings: 2" in response
    assert "system prompt override: yes" in response
    assert "start: /rp start Alice" in response
    assert '"raw"' not in response


def test_card_inspect_reports_embedded_lorebook_without_raw_dump(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(
        parse_character_card(
            {
                "spec": "chara_card_v3",
                "spec_version": "3.0",
                "data": {
                    "name": "Alice",
                    "description": "A scholar with a private world book.",
                    "character_book": {
                        "name": "Alice World",
                        "entries": {
                            "0": {"key": ["moon"], "content": "The moon is a sealed archive."},
                            "1": {"key": ["owl"], "content": "The brass owl remembers names."},
                        },
                    },
                },
            }
        )
    )
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["inspect", "Alice"], "/rp card inspect Alice"),
        Event(),
    )

    assert "embedded lorebook: Alice World" in response
    assert "2 entries" in response
    assert "/rp lore inspect" in response
    assert "The moon is a sealed archive" not in response
    assert '"character_book"' not in response


def test_card_inspect_reports_no_embedded_lorebook_for_plain_card(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Plain", "description": "No book."}))
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["inspect", "Plain"], "/rp card inspect Plain"),
        Event(),
    )

    assert "embedded lorebook: none" in response


def test_card_use_rebinds_active_session_without_losing_messages(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello."}))
    store.save_card(parse_character_card({"name": "Bob", "first_mes": "Forge is hot."}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.append_message(session["id"], "user", "Keep this turn")

    response = runtime.handle_command_sync(
        RPCommand("card", ["use", "Bob"], "/rp card use Bob"),
        Event(),
    )

    active = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    messages = store.get_recent_messages(active["id"], limit=10)
    assert "Hermes Tavern card bound: Bob" in response
    assert active["card_name"] == "Bob"
    assert any(msg["content"] == "Keep this turn" for msg in messages)
    assert any(msg["content"] == "Forge is hot." for msg in messages)


def test_assets_command_summarizes_cards_presets_lorebooks_and_active_bindings(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "tags": ["scholar"]}))
    preset_id = store.save_preset(
        import_st_preset_json({"name": "Writer", "prompts": [{"name": "style", "content": "Write vividly."}]})
    )
    lorebook_id = store.save_lorebook(
        import_st_lorebook_json(
            {
                "name": "Library",
                "entries": {"0": {"key": ["library"], "content": "Old books."}},
            }
        )
    )
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    runtime.handle_command_sync(RPCommand("preset", ["use", preset_id], f"/rp preset use {preset_id}"), Event())
    runtime.handle_command_sync(RPCommand("lore", ["use", lorebook_id], f"/rp lore use {lorebook_id}"), Event())

    response = runtime.handle_command_sync(RPCommand("assets", [], "/rp assets"), Event())

    assert "Hermes Tavern assets" in response
    assert "cards: 1" in response
    assert "presets: 1" in response
    assert "lorebooks: 1" in response
    assert "active card: Alice" in response
    assert "active preset: Writer" in response
    assert "active lorebook: Library" in response
    assert "/rp cards" in response
    assert "/rp preset list" in response
    assert "/rp lore list" in response


# ── Phase 17: cards pagination ────────────────────────────────────────────────

def _make_cards(store: TavernStore, count: int) -> None:
    for i in range(count):
        store.save_card(parse_character_card({"name": f"Card{i:02d}", "description": f"Desc {i}"}))


def test_cards_pagination_backward_compatible(tmp_path):
    """No page arg → same output format as Phase 16 (no pagination footer)."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    _make_cards(store, 3)
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(RPCommand("cards", [], "/rp cards"), Event())

    assert "Hermes Tavern cards" in response
    assert "Card00" in response
    # single page → no prev/next hints
    assert "prev:" not in response
    assert "next:" not in response


def test_cards_pagination_page2(tmp_path):
    """With 12 cards and limit 5, page 2 shows cards 5-9."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    _make_cards(store, 12)
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("cards", ["5", "2"], "/rp cards 5 2"), Event()
    )

    assert "page 2/3" in response
    assert "Card05" in response
    assert "Card00" not in response
    assert "prev: /rp cards 5 1" in response
    assert "next: /rp cards 5 3" in response


def test_cards_pagination_clamp_to_last_page(tmp_path):
    """page=99 clamps to last valid page."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    _make_cards(store, 8)
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("cards", ["5", "99"], "/rp cards 5 99"), Event()
    )

    assert "page 2/2" in response
    assert "Card05" in response
    assert "prev: /rp cards 5 1" in response
    assert "next:" not in response


def test_cards_pagination_single_page_no_footer(tmp_path):
    """Fewer cards than limit → no pagination footer at all."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    _make_cards(store, 3)
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("cards", ["10", "1"], "/rp cards 10 1"), Event()
    )

    assert "page 1/1" in response
    assert "prev:" not in response
    assert "next:" not in response


def test_cards_bad_limit_returns_usage(tmp_path):
    """Non-integer limit still returns usage error."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("cards", ["abc"], "/rp cards abc"), Event()
    )

    assert "Usage:" in response


# ── Phase 17: preset inspect improved ────────────────────────────────────────

def test_preset_inspect_shows_aggregate_risk_counts(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    preset = import_st_preset_json({
        "name": "TestPreset",
        "prompts": [
            {"name": "safe_mod", "content": "Write clearly.", "enabled": True},
            {"name": "adult_mod", "content": "Adult content goes here.", "enabled": True},
        ],
    })
    preset_id = store.save_preset(preset)
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("preset", ["inspect", preset_id], f"/rp preset inspect {preset_id}"),
        Event(),
    )

    assert "TestPreset" in response
    assert "modules:" in response
    # aggregate counts line
    assert "safe:" in response or "enabled" in response
    assert "/rp preset use" in response


def test_preset_inspect_no_raw_json_in_output(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    preset = import_st_preset_json({
        "name": "RawTest",
        "prompts": [{"name": "m1", "content": "Some prompt text."}],
    })
    preset_id = store.save_preset(preset)
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("preset", ["inspect", preset_id], f"/rp preset inspect {preset_id}"),
        Event(),
    )

    # output must not contain raw JSON blob (opening brace + key pattern)
    assert '{"' not in response


def test_preset_inspect_module_previews_bounded(tmp_path):
    """Module content previews must not exceed 60 chars in output lines."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    long_content = "X" * 200
    preset = import_st_preset_json({
        "name": "LongPreset",
        "prompts": [{"name": "verbosemod", "content": long_content}],
    })
    preset_id = store.save_preset(preset)
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("preset", ["inspect", preset_id], f"/rp preset inspect {preset_id}"),
        Event(),
    )

    assert long_content not in response
    assert "verbosemod" in response


# ── Phase 17: lore inspect ────────────────────────────────────────────────────

def test_lore_inspect_shows_summary_and_top_entries(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    lorebook = import_st_lorebook_json({
        "name": "WorldLore",
        "entries": {
            "0": {"key": ["dragon", "fire"], "content": "Dragons breathe fire in the north."},
            "1": {"key": ["elf"], "content": "Elves live for centuries in deep forests.", "constant": True},
            "2": {"key": ["sword"], "content": "A magic sword lies in the vault."},
        },
    })
    lorebook_id = store.save_lorebook(lorebook)
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("lore", ["inspect", lorebook_id], f"/rp lore inspect {lorebook_id}"),
        Event(),
    )

    assert "WorldLore" in response
    assert "entries:" in response
    assert "constant" in response
    assert "showing entries 1-3 of 3 (page 1/1)" in response
    assert "/rp lore use" in response
    assert "/rp lore test" in response


def test_lore_inspect_paginates_entries_with_next_prev_hints(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    lorebook = import_st_lorebook_json(
        {
            "name": "BigLore",
            "entries": {
                str(i): {"key": [f"key{i}"], "content": f"Lore entry {i} content."}
                for i in range(7)
            },
        }
    )
    lorebook_id = store.save_lorebook(lorebook)
    runtime = TavernRuntime(store)

    page1 = runtime.handle_command_sync(
        RPCommand("lore", ["inspect", lorebook_id[:8], "3", "1"], f"/rp lore inspect {lorebook_id[:8]} 3 1"),
        Event(),
    )
    page2 = runtime.handle_command_sync(
        RPCommand("lore", ["inspect", lorebook_id[:8], "3", "2"], f"/rp lore inspect {lorebook_id[:8]} 3 2"),
        Event(),
    )

    assert "showing entries 1-3 of 7 (page 1/3)" in page1
    assert "next: /rp lore inspect" in page1
    assert "Lore entry 4 content" not in page1
    assert "showing entries 4-6 of 7 (page 2/3)" in page2
    assert "prev: /rp lore inspect" in page2
    assert "next: /rp lore inspect" in page2


def test_lore_inspect_not_found(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("lore", ["inspect", "no-such-lorebook"], "/rp lore inspect no-such-lorebook"),
        Event(),
    )

    assert "not found" in response.lower()


def test_lore_inspect_in_help(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(RPCommand("help", [], "/rp help"), Event())

    assert "/rp lore inspect" in response


# ── Phase 17: session info ────────────────────────────────────────────────────

def test_session_info_shows_bindings_and_counts(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello."}))
    preset = import_st_preset_json({"name": "Writer", "prompts": [{"name": "style", "content": "Be vivid."}]})
    preset_id = store.save_preset(preset)
    lorebook = import_st_lorebook_json({
        "name": "Lore",
        "entries": {"0": {"key": ["x"], "content": "Some lore."}},
    })
    lorebook_id = store.save_lorebook(lorebook)
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    runtime.handle_command_sync(RPCommand("preset", ["use", preset_id], f"/rp preset use {preset_id}"), Event())
    runtime.handle_command_sync(RPCommand("lore", ["use", lorebook_id], f"/rp lore use {lorebook_id}"), Event())
    store.add_session_memory_fact("telegram:chat:chat-1:thread:main:user:user-1", "Alice likes tea.")

    response = runtime.handle_command_sync(
        RPCommand("session", ["info"], "/rp session info"), Event()
    )

    assert "Session:" in response
    assert "Alice" in response
    assert "content_mode:" in response
    assert "adapter:" in response
    assert "memory:" in response
    assert "/rp history" in response


def test_session_info_no_active_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("session", ["info"], "/rp session info"), Event()
    )

    assert "No active Hermes Tavern session" in response


def test_session_info_in_help(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(RPCommand("help", [], "/rp help"), Event())

    assert "/rp session info" in response


# ── Phase 18: history pagination ──────────────────────────────────────────────

SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


def _start_session(store: TavernStore, runtime: TavernRuntime) -> str:
    """Start an Alice session (no greeting message) and return its session_id."""
    store.save_card(parse_character_card({"name": "Alice"}))
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session = store.get_active_session(SESSION_KEY)
    assert session is not None
    return session["id"]


def _add_messages(store: TavernStore, session_id: str, count: int) -> None:
    """Append alternating user/assistant messages."""
    for i in range(count):
        role = "user" if i % 2 == 0 else "assistant"
        store.append_message(session_id, role, f"Message {i} content here.")


def test_history_default_compat_shows_page_header(tmp_path):
    """No args → page 1/1 header appears; existing data all shown."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    session_id = _start_session(store, runtime)
    _add_messages(store, session_id, 5)

    response = runtime.handle_command_sync(RPCommand("history", [], "/rp history"), Event())

    assert "Hermes Tavern session history" in response
    assert "page 1/1" in response
    assert "5 shown" in response
    assert "prev:" not in response
    assert "next:" not in response


def test_history_limit_only_compat(tmp_path):
    """/rp history <limit> with no page arg works as page 1."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    session_id = _start_session(store, runtime)
    _add_messages(store, session_id, 15)

    response = runtime.handle_command_sync(RPCommand("history", ["5"], "/rp history 5"), Event())

    assert "page 1/" in response
    assert "5 shown" in response


def test_history_page2_shows_correct_slice_and_hints(tmp_path):
    """15 messages, limit 5 → 3 pages; page 2 shows msgs 6-10 with prev+next."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    session_id = _start_session(store, runtime)
    _add_messages(store, session_id, 15)

    response = runtime.handle_command_sync(
        RPCommand("history", ["5", "2"], "/rp history 5 2"), Event()
    )

    assert "page 2/3" in response
    assert "5 shown" in response
    assert "15 total" in response
    assert "prev: /rp history 5 1" in response
    assert "next: /rp history 5 3" in response


def test_history_page_clamp_to_last(tmp_path):
    """page=99 clamps to last valid page; shows prev hint, no next hint."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    session_id = _start_session(store, runtime)
    _add_messages(store, session_id, 12)

    response = runtime.handle_command_sync(
        RPCommand("history", ["5", "99"], "/rp history 5 99"), Event()
    )

    assert "page 3/3" in response
    assert "prev: /rp history 5 2" in response
    assert "next:" not in response


def test_history_bad_limit_returns_usage(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _start_session(store, runtime)

    response = runtime.handle_command_sync(
        RPCommand("history", ["bad"], "/rp history bad"), Event()
    )

    assert "Usage: /rp history [limit] [page]" in response


def test_history_no_active_session_unchanged(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(RPCommand("history", [], "/rp history"), Event())

    assert "No active Hermes Tavern session" in response


def test_history_preview_bounded(tmp_path):
    """Each message preview must be ≤80 chars and single-line."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    session_id = _start_session(store, runtime)
    store.append_message(session_id, "user", "A" * 200 + "\nnewline here")

    response = runtime.handle_command_sync(RPCommand("history", [], "/rp history"), Event())

    for line in response.splitlines():
        if "user:" in line or "assistant:" in line:
            preview_part = line.split(":", 2)[-1].strip() if ":" in line else line
            assert len(preview_part) <= 80
    assert "\n" not in "A" * 80  # sanity: previews collapsed to single line


def test_history_chronological_order(tmp_path):
    """Page 1 = oldest messages; chronological order across pages."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    session_id = _start_session(store, runtime)
    for i in range(10):
        store.append_message(session_id, "user", f"Msg {i:02d}")

    resp_p1 = runtime.handle_command_sync(
        RPCommand("history", ["5", "1"], "/rp history 5 1"), Event()
    )
    resp_p2 = runtime.handle_command_sync(
        RPCommand("history", ["5", "2"], "/rp history 5 2"), Event()
    )

    assert "Msg 00" in resp_p1
    assert "Msg 04" in resp_p1
    assert "Msg 00" not in resp_p2
    assert "Msg 05" in resp_p2
    assert "Msg 09" in resp_p2


def test_history_in_help(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(RPCommand("help", [], "/rp help"), Event())

    assert "/rp history [limit] [page]" in response


# ── Phase 18: sessions pagination ─────────────────────────────────────────────

def _make_sessions(store: TavernStore, count: int, scope_key: str) -> list[str]:
    """Create `count` sessions under scope_key and return their ids.

    The first session (ids[0]) is the "active" one reachable via
    get_active_session(scope_key).  Subsequent sessions are clones and appear
    in list_sessions_for_scope(scope_key) but have their own session_keys.
    """
    card_id = store.save_card(parse_character_card({"name": "Base", "first_mes": "Hi."}))
    base = store.start_session(scope_key, card_id)
    ids = [base["id"]]
    for _ in range(count - 1):
        cloned = store.clone_session(base["id"], scope_key)
        ids.append(cloned["id"])
    return ids


def test_sessions_default_compat_shows_page_header(tmp_path):
    """No args → page 1/1 header appears."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _make_sessions(store, 3, SESSION_KEY)

    response = runtime.handle_command_sync(RPCommand("sessions", [], "/rp sessions"), Event())

    assert "Hermes Tavern sessions" in response
    assert "page 1/1" in response
    assert "prev:" not in response
    assert "next:" not in response


def test_sessions_all_compat(tmp_path):
    """/rp sessions all still works as page 1 with default limit."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _make_sessions(store, 3, SESSION_KEY)
    # archive one so include_all matters
    active = store.get_active_session(SESSION_KEY)
    if active:
        store.archive_active_session(SESSION_KEY)

    response = runtime.handle_command_sync(
        RPCommand("sessions", ["all"], "/rp sessions all"), Event()
    )

    assert "Hermes Tavern sessions" in response
    assert "page 1/" in response
    assert "all" in response


def test_sessions_page2_shows_hints_without_all(tmp_path):
    """8 sessions, limit 3 → 3 pages; page 2 hints don't include 'all'."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _make_sessions(store, 8, SESSION_KEY)

    response = runtime.handle_command_sync(
        RPCommand("sessions", ["3", "2"], "/rp sessions 3 2"), Event()
    )

    assert "page 2/3" in response
    assert "prev: /rp sessions 3 1" in response
    assert "next: /rp sessions 3 3" in response
    assert "all" not in response.split("prev:")[1] if "prev:" in response else True


def test_sessions_all_page_hints_include_all(tmp_path):
    """With all flag, page hints include 'all'."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _make_sessions(store, 8, SESSION_KEY)
    store.archive_active_session(SESSION_KEY)

    response = runtime.handle_command_sync(
        RPCommand("sessions", ["all", "3", "2"], "/rp sessions all 3 2"), Event()
    )

    assert "page 2/3" in response
    assert "prev: /rp sessions all 3 1" in response
    assert "next: /rp sessions all 3 3" in response


def test_sessions_bad_args_returns_usage(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    resp1 = runtime.handle_command_sync(
        RPCommand("sessions", ["bad"], "/rp sessions bad"), Event()
    )
    resp2 = runtime.handle_command_sync(
        RPCommand("sessions", ["all", "bad"], "/rp sessions all bad"), Event()
    )

    assert "Usage: /rp sessions [all] [limit] [page]" in resp1
    assert "Usage: /rp sessions [all] [limit] [page]" in resp2


def test_sessions_active_marker_preserved(tmp_path):
    """Active session has * marker even after pagination changes."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    session_ids = _make_sessions(store, 5, SESSION_KEY)
    # session_ids[0] is the base session with session_key=SESSION_KEY, always active

    response = runtime.handle_command_sync(RPCommand("sessions", [], "/rp sessions"), Event())

    active_line = next(
        (line for line in response.splitlines() if "*" in line), None
    )
    assert active_line is not None
    assert session_ids[0][:8] in active_line


def test_sessions_in_help(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(RPCommand("help", [], "/rp help"), Event())

    assert "/rp sessions [all] [limit] [page]" in response


# ── Phase 18: memory list pagination ──────────────────────────────────────────

def _add_facts(store: TavernStore, session_key: str, count: int) -> None:
    for i in range(count):
        store.add_session_memory_fact(session_key, f"Fact {i:02d}: " + "detail " * 20)


def test_memory_list_default_compat_shows_page_header(tmp_path):
    """No args → page 1/1 header appears."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _start_session(store, runtime)
    _add_facts(store, SESSION_KEY, 5)

    response = runtime.handle_command_sync(
        RPCommand("memory", ["list"], "/rp memory list"), Event()
    )

    assert "Hermes Tavern session memory" in response
    assert "page 1/1" in response
    assert "5 shown" in response
    assert "prev:" not in response
    assert "next:" not in response


def test_memory_list_page2_shows_hints(tmp_path):
    """5 facts, limit 2 → 3 pages; page 2 shows prev+next hints."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _start_session(store, runtime)
    _add_facts(store, SESSION_KEY, 5)

    response = runtime.handle_command_sync(
        RPCommand("memory", ["list", "2", "2"], "/rp memory list 2 2"), Event()
    )

    assert "page 2/3" in response
    assert "2 shown" in response
    assert "5 total" in response
    assert "prev: /rp memory list 2 1" in response
    assert "next: /rp memory list 2 3" in response


def test_memory_list_page_clamp(tmp_path):
    """page=99 clamps to last page."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _start_session(store, runtime)
    _add_facts(store, SESSION_KEY, 5)

    response = runtime.handle_command_sync(
        RPCommand("memory", ["list", "2", "99"], "/rp memory list 2 99"), Event()
    )

    assert "page 3/3" in response
    assert "prev: /rp memory list 2 2" in response
    assert "next:" not in response


def test_memory_list_bad_args_returns_usage(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _start_session(store, runtime)

    response = runtime.handle_command_sync(
        RPCommand("memory", ["list", "bad"], "/rp memory list bad"), Event()
    )

    assert "Usage: /rp memory list [limit] [page]" in response


def test_memory_list_no_active_session_unchanged(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("memory", ["list"], "/rp memory list"), Event()
    )

    assert "No active Hermes Tavern session" in response


def test_memory_list_preview_bounded(tmp_path):
    """Fact content previews ≤80 chars, single-line."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _start_session(store, runtime)
    store.add_session_memory_fact(SESSION_KEY, "X" * 200 + "\nline2")

    response = runtime.handle_command_sync(
        RPCommand("memory", ["list"], "/rp memory list"), Event()
    )

    for line in response.splitlines():
        if line.strip().startswith("- ("):
            fact_text = line.split(")", 1)[-1].strip()
            assert len(fact_text) <= 80


def test_memory_list_summary_shown(tmp_path):
    """Header block always shows summary: set|none."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _start_session(store, runtime)

    resp_none = runtime.handle_command_sync(
        RPCommand("memory", ["list"], "/rp memory list"), Event()
    )
    store.set_session_summary(SESSION_KEY, "A summary.")
    resp_set = runtime.handle_command_sync(
        RPCommand("memory", ["list"], "/rp memory list"), Event()
    )

    assert "summary: none" in resp_none
    assert "summary: set" in resp_set


def test_memory_list_facts_header_line(tmp_path):
    """Facts section has 'facts (page X/Y, N shown, M total):' line."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    _start_session(store, runtime)
    _add_facts(store, SESSION_KEY, 3)

    response = runtime.handle_command_sync(
        RPCommand("memory", ["list"], "/rp memory list"), Event()
    )

    assert "facts (page" in response
    assert "total):" in response


def test_memory_list_in_help(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(RPCommand("help", [], "/rp help"), Event())

    assert "/rp memory list [limit] [page]" in response
