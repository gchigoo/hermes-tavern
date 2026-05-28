"""Smoke test for Phase 14 turn controls (no pytest required)."""
import asyncio
import tempfile
from pathlib import Path

from plugins.hermes_tavern.adapters import FAKE_ADAPTER_REPLY
from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.runtime import TavernRuntime

SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


passed = []
failed = []


def check(name, cond, detail=""):
    if cond:
        passed.append(name)
        print(f"  PASS  {name}")
    else:
        failed.append(name)
        print(f"  FAIL  {name}" + (f": {detail}" for _ in [1]).__next__() if detail else f"  FAIL  {name}")


# --- Store helpers ---
def test_store_helpers():
    with tempfile.TemporaryDirectory() as d:
        store = TavernStore(Path(d) / "t.sqlite3")
        session = store.start_session("k1")
        sid = session["id"]

        store.append_message(sid, "user", "hi")
        store.append_message(sid, "assistant", "reply")

        msgs = store.get_recent_messages(sid)
        check("get_recent_messages_has_id", "id" in msgs[0])

        deleted = store.delete_last_assistant_message(sid)
        check("delete_last_assistant_returns_id", deleted is not None)
        check("delete_last_assistant_removes_row", len(store.get_recent_messages(sid)) == 1)

        noop = store.delete_last_assistant_message(sid)
        check("delete_last_assistant_noop", noop is None)

        store.append_message(sid, "assistant", "r1")
        store.append_message(sid, "user", "u2")
        store.append_message(sid, "assistant", "r2")
        n = store.delete_last_user_assistant_turn(sid)
        check("delete_last_turn_removes_pair", n == 2)
        check("delete_last_turn_leaves_prior", len(store.get_recent_messages(sid)) == 2)

        n0 = store.delete_last_user_assistant_turn(sid)
        # Only assistant messages remain after the pair delete; no user → 0
        check("delete_last_turn_noop_no_user", n0 == 0)

        store.append_message(sid, "user", "original")
        uid = store.update_last_user_message(sid, "edited")
        check("update_last_user_returns_id", uid is not None)
        msgs2 = store.get_recent_messages(sid)
        user_msgs = [m for m in msgs2 if m["role"] == "user"]
        check("update_last_user_content", user_msgs[-1]["content"] == "edited")

        no_uid = store.update_last_user_message("nonexistent_session", "x")
        check("update_last_user_noop_empty_session", no_uid is None)


# --- Runtime commands ---
async def test_runtime():
    with tempfile.TemporaryDirectory() as d:
        store = TavernStore(Path(d) / "t.sqlite3")
        store.migrate()
        store.save_card(parse_character_card({"name": "Alice", "description": "Mage", "first_mes": "Greetings."}))
        rt = TavernRuntime(store)

        await rt.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

        # history — no messages except greeting
        resp = await rt.handle_command(RPCommand("history", [], "/rp history"), Event())
        check("history_shows_session", "session history" in resp)
        check("history_has_bracket_id", "[" in resp)

        # retry — session has greeting (assistant); retry deletes it, then no user
        resp = await rt.handle_command(RPCommand("retry", [], "/rp retry"), Event())
        check("retry_no_user_msg_after_greeting_delete",
              "No user message" in resp or "No assistant reply" in resp)

        # add a user+assistant turn
        class MsgEvent(Event):
            text = "What do you know?"
        await rt.handle_active_message(MsgEvent())

        # retry after real turn
        session = store.get_active_session(SESSION_KEY)
        before = store.get_recent_messages(session["id"])
        a_before = [m for m in before if m["role"] == "assistant"]
        resp = await rt.handle_command(RPCommand("retry", [], "/rp retry"), Event())
        check("retry_returns_fake_reply", resp == FAKE_ADAPTER_REPLY)
        after = store.get_recent_messages(session["id"])
        a_after = [m for m in after if m["role"] == "assistant"]
        check("retry_net_assistant_count_stable", len(a_after) == len(a_before))

        # undo
        count_before = len(store.get_recent_messages(session["id"]))
        resp = await rt.handle_command(RPCommand("undo", [], "/rp undo"), Event())
        check("undo_response_ok", "undo" in resp.lower())
        count_after = len(store.get_recent_messages(session["id"]))
        check("undo_shrinks_messages", count_after < count_before)

        # add another turn for edit test
        class MsgEvent2(Event):
            text = "Original"
        await rt.handle_active_message(MsgEvent2())

        resp = await rt.handle_command(
            RPCommand("edit", ["last", "Edited", "text"], "/rp edit last Edited text"), Event()
        )
        check("edit_returns_fake_reply", resp == FAKE_ADAPTER_REPLY)
        session2 = store.get_active_session(SESSION_KEY)
        msgs = store.get_recent_messages(session2["id"])
        user_msgs = [m for m in msgs if m["role"] == "user"]
        check("edit_updates_user_content", user_msgs[-1]["content"] == "Edited text")

        # edit — no user message
        # clear all user messages by undoing until none
        for _ in range(10):
            store.delete_last_user_assistant_turn(session2["id"])
        resp = await rt.handle_command(
            RPCommand("edit", ["last", "something"], "/rp edit last something"), Event()
        )
        check("edit_no_user_msg", "No user message" in resp)

        # help text
        resp = await rt.handle_command(RPCommand("help", [], "/rp"), Event())
        check("help_has_history", "/rp history [limit]" in resp)
        check("help_has_retry", "/rp retry" in resp)
        check("help_has_undo", "/rp undo" in resp)
        check("help_has_edit", "/rp edit last <text>" in resp)


test_store_helpers()
asyncio.run(test_runtime())

print(f"\n{len(passed)} passed, {len(failed)} failed")
if failed:
    print("FAILED:", failed)
    raise SystemExit(1)
