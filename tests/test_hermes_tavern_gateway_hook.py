import asyncio
from enum import Enum
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from plugins.hermes_tavern import gateway_hook
from plugins.hermes_tavern.db import TavernStore
from gateway.platforms.base import BasePlatformAdapter
from plugins.hermes_tavern.gateway_hook import _get_adapter, _send_if_possible, pre_gateway_dispatch
from plugins.hermes_tavern.importers.cards import parse_character_card


def _event(text: str) -> SimpleNamespace:
    return _event_for(text, user_id="user-1")


def _event_for(
    text: str,
    *,
    user_id: str,
    platform: str = "telegram",
    chat_id: str = "chat-1",
    thread_id=None,
    message_id: str = "m1",
) -> SimpleNamespace:
    return SimpleNamespace(
        text=text,
        message_id=message_id,
        source=SimpleNamespace(
            platform=platform,
            chat_id=chat_id,
            thread_id=thread_id,
            user_id=user_id,
        ),
    )


def _gateway() -> SimpleNamespace:
    adapter = SimpleNamespace(send=AsyncMock())
    return SimpleNamespace(adapters={"telegram": adapter}), adapter


def _multi_platform_gateway() -> tuple[SimpleNamespace, SimpleNamespace, SimpleNamespace]:
    telegram_adapter = SimpleNamespace(send=AsyncMock())
    discord_adapter = SimpleNamespace(send=AsyncMock())
    gateway = SimpleNamespace(
        adapters={
            "telegram": telegram_adapter,
            "discord": discord_adapter,
        }
    )
    return gateway, telegram_adapter, discord_adapter


def _media_gateway() -> tuple[SimpleNamespace, SimpleNamespace]:
    adapter = SimpleNamespace(
        send=AsyncMock(),
        extract_media=BasePlatformAdapter.extract_media,
    )
    gateway = SimpleNamespace(
        adapters={"telegram": adapter},
        _deliver_media_from_response=AsyncMock(),
    )
    return gateway, adapter


class _Platform(Enum):
    TELEGRAM = "telegram"


def test_get_adapter_resolves_enum_valued_platform():
    """_get_adapter must find the adapter when platform is an Enum whose .value is the dict key."""
    adapter = object()
    gateway = SimpleNamespace(adapters={"telegram": adapter})
    event = SimpleNamespace(
        source=SimpleNamespace(platform=_Platform.TELEGRAM)
    )

    assert _get_adapter(gateway, event) is adapter


def test_gateway_hook_returns_allow_on_store_exception(tmp_path):
    """Any Exception from store/runtime must not propagate; hook returns allow."""

    class _BrokenStore:
        def migrate(self) -> None:
            raise RuntimeError("db down")

        def get_active_session(self, key: str):
            raise RuntimeError("db down")

    result = pre_gateway_dispatch(event=_event("hello"), store=_BrokenStore())

    assert result == {"action": "allow"}


def test_gateway_hook_allows_non_rp_without_active_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    result = pre_gateway_dispatch(event=_event("hello"), store=store)

    assert result == {"action": "allow"}


def test_gateway_hook_rp_command_skips_when_adapter_missing(tmp_path):
    gateway = SimpleNamespace(adapters={})

    result = pre_gateway_dispatch(
        event=_event("/rp help"),
        gateway=gateway,
        store=TavernStore(tmp_path / "tavern.sqlite3"),
    )

    assert result == {"action": "skip", "reason": "hermes-tavern"}


@pytest.mark.parametrize(
    "source",
    [
        SimpleNamespace(platform="telegram", thread_id=None, user_id="user-1"),
        SimpleNamespace(platform="telegram", chat_id=None, thread_id=None, user_id="user-1"),
        SimpleNamespace(platform="telegram", chat_id="", thread_id=None, user_id="user-1"),
    ],
)
def test_gateway_hook_rp_command_skips_without_chat_id(source, tmp_path):
    gateway, adapter = _gateway()
    event = SimpleNamespace(text="/rp help", message_id="m1", source=source)

    result = pre_gateway_dispatch(
        event=event,
        gateway=gateway,
        store=TavernStore(tmp_path / "tavern.sqlite3"),
    )

    assert result == {"action": "skip", "reason": "hermes-tavern"}
    adapter.send.assert_not_called()


@pytest.mark.asyncio
async def test_gateway_hook_sends_help_and_skips(tmp_path):
    gateway, adapter = _gateway()

    result = pre_gateway_dispatch(
        event=_event("/rp help"),
        gateway=gateway,
        store=TavernStore(tmp_path / "tavern.sqlite3"),
    )
    await asyncio.sleep(0)

    assert result == {"action": "skip", "reason": "hermes-tavern"}
    adapter.send.assert_awaited_once()
    assert "/rp start <card>" in adapter.send.await_args.args[1]


@pytest.mark.asyncio
async def test_send_if_possible_strips_media_tags_and_delivers_native_media(tmp_path):
    gateway, adapter = _media_gateway()
    media = tmp_path / "scene.png"
    media.write_bytes(b"png")

    _send_if_possible(gateway, _event("ignored"), f"Generated scene.\nMEDIA:\"{media}\"")
    await asyncio.sleep(0)

    adapter.send.assert_awaited_once_with("chat-1", "Generated scene.")
    gateway._deliver_media_from_response.assert_awaited_once()
    assert gateway._deliver_media_from_response.await_args.args[0].endswith(f'MEDIA:"{media}"')


@pytest.mark.asyncio
async def test_send_if_possible_media_only_delivers_without_empty_text(tmp_path):
    gateway, adapter = _media_gateway()
    media = tmp_path / "export.json"
    media.write_text("{}", encoding="utf-8")

    _send_if_possible(gateway, _event("ignored"), f'MEDIA:"{media}"')
    await asyncio.sleep(0)

    adapter.send.assert_not_awaited()
    gateway._deliver_media_from_response.assert_awaited_once()


@pytest.mark.asyncio
async def test_gateway_hook_export_media_marker_is_not_sent_as_chat_text(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    gateway, adapter = _media_gateway()

    result = pre_gateway_dispatch(event=_event("/rp export"), gateway=gateway, store=store)
    await asyncio.sleep(0)

    assert result == {"action": "skip", "reason": "hermes-tavern"}
    adapter.send.assert_awaited_once()
    sent_chat_id, sent_text = adapter.send.await_args.args
    assert sent_chat_id == "chat-1"
    assert "Session exported as Markdown." in sent_text
    assert "file:" in sent_text
    assert "MEDIA:" not in sent_text
    gateway._deliver_media_from_response.assert_awaited_once()
    delivered_content = gateway._deliver_media_from_response.await_args.args[0]
    assert 'MEDIA:"' in delivered_content
    assert "hermes home" in delivered_content


@pytest.mark.asyncio
async def test_gateway_hook_active_message_media_marker_is_not_sent_as_chat_text(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    media = tmp_path / "active scene.png"
    media.write_bytes(b"png")
    gateway, adapter = _media_gateway()

    def fake_active_reply(self, event):
        assert event.text == "show the scene"
        return f'Generated active scene.\nMEDIA:"{media}"'

    monkeypatch.setattr(
        gateway_hook.TavernRuntime,
        "handle_active_message_sync",
        fake_active_reply,
    )

    result = pre_gateway_dispatch(event=_event("show the scene"), gateway=gateway, store=store)
    await asyncio.sleep(0)

    assert result == {"action": "skip", "reason": "hermes-tavern"}
    adapter.send.assert_awaited_once_with("chat-1", "Generated active scene.")
    gateway._deliver_media_from_response.assert_awaited_once()
    delivered_content, delivered_event, delivered_adapter = (
        gateway._deliver_media_from_response.await_args.args
    )
    assert delivered_content == f'Generated active scene.\nMEDIA:"{media}"'
    assert delivered_event.text == "show the scene"
    assert delivered_adapter is adapter


@pytest.mark.asyncio
async def test_gateway_hook_active_message_is_stored_and_placeholder_sent(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card({"name": "Alice", "first_mes": "Hello."})
    store.save_card(card)
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1", card_id=card.id)
    gateway, adapter = _gateway()

    result = pre_gateway_dispatch(event=_event("A user reply"), gateway=gateway, store=store)
    await asyncio.sleep(0)

    assert result == {"action": "skip", "reason": "hermes-tavern"}
    adapter.send.assert_awaited_once()
    assert adapter.send.await_args.args[1] == "[Hermes Tavern fake adapter response]"

    with store.connect() as conn:
        rows = conn.execute("SELECT role, content FROM messages ORDER BY created_at").fetchall()
    assert [(row["role"], row["content"]) for row in rows] == [
        ("user", "A user reply"),
        ("assistant", "[Hermes Tavern fake adapter response]"),
    ]


@pytest.mark.asyncio
async def test_gateway_hook_multi_user_loop_keeps_active_messages_and_pause_scoped(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card({"name": "Alice", "first_mes": "Hello."})
    store.save_card(card)
    gateway, adapter = _gateway()
    user1_key = "telegram:chat:chat-1:thread:main:user:user-1"
    user2_key = "telegram:chat:chat-1:thread:main:user:user-2"

    start1 = pre_gateway_dispatch(
        event=_event_for("/rp start Alice", user_id="user-1", message_id="m-start-1"),
        gateway=gateway,
        store=store,
    )
    start2 = pre_gateway_dispatch(
        event=_event_for("/rp start Alice", user_id="user-2", message_id="m-start-2"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert start1 == {"action": "skip", "reason": "hermes-tavern"}
    assert start2 == {"action": "skip", "reason": "hermes-tavern"}
    user1_session = store.get_active_session(user1_key)
    user2_session = store.get_active_session(user2_key)
    assert user1_session is not None
    assert user2_session is not None
    assert user1_session["id"] != user2_session["id"]

    message1 = pre_gateway_dispatch(
        event=_event_for("user one reply", user_id="user-1", message_id="m-msg-1"),
        gateway=gateway,
        store=store,
    )
    message2 = pre_gateway_dispatch(
        event=_event_for("user two reply", user_id="user-2", message_id="m-msg-2"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert message1 == {"action": "skip", "reason": "hermes-tavern"}
    assert message2 == {"action": "skip", "reason": "hermes-tavern"}
    assert [row["content"] for row in store.get_recent_messages(user1_session["id"], limit=4)] == [
        "Hello.",
        "user one reply",
        "[Hermes Tavern fake adapter response]",
    ]
    assert [row["content"] for row in store.get_recent_messages(user2_session["id"], limit=4)] == [
        "Hello.",
        "user two reply",
        "[Hermes Tavern fake adapter response]",
    ]

    pause1 = pre_gateway_dispatch(
        event=_event_for("/rp pause", user_id="user-1", message_id="m-pause-1"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert pause1 == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session(user1_key) is None
    assert store.get_paused_session(user1_key)["id"] == user1_session["id"]
    assert store.get_active_session(user2_key)["id"] == user2_session["id"]

    paused_user_message = pre_gateway_dispatch(
        event=_event_for("paused user should fall through", user_id="user-1", message_id="m-paused"),
        gateway=gateway,
        store=store,
    )
    active_user_message = pre_gateway_dispatch(
        event=_event_for("user two still active", user_id="user-2", message_id="m-active"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert paused_user_message == {"action": "allow"}
    assert active_user_message == {"action": "skip", "reason": "hermes-tavern"}
    assert "paused user should fall through" not in [
        row["content"] for row in store.get_recent_messages(user1_session["id"], limit=10)
    ]
    assert "user two still active" in [
        row["content"] for row in store.get_recent_messages(user2_session["id"], limit=10)
    ]

    sessions1 = pre_gateway_dispatch(
        event=_event_for("/rp sessions all", user_id="user-1", message_id="m-sessions-1"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert sessions1 == {"action": "skip", "reason": "hermes-tavern"}
    sent_text = adapter.send.await_args.args[1]
    assert user1_session["id"][:8] in sent_text
    assert user2_session["id"][:8] not in sent_text
    assert user2_key not in sent_text


@pytest.mark.asyncio
async def test_gateway_hook_resume_only_reactivates_caller_scope(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card({"name": "Alice", "first_mes": "Hello."})
    store.save_card(card)
    gateway, adapter = _gateway()
    user_a_key = "telegram:chat:chat-1:thread:main:user:user-a"
    user_b_key = "telegram:chat:chat-1:thread:main:user:user-b"

    start_a = pre_gateway_dispatch(
        event=_event_for("/rp start Alice", user_id="user-a", message_id="m-start-a"),
        gateway=gateway,
        store=store,
    )
    start_b = pre_gateway_dispatch(
        event=_event_for("/rp start Alice", user_id="user-b", message_id="m-start-b"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert start_a == {"action": "skip", "reason": "hermes-tavern"}
    assert start_b == {"action": "skip", "reason": "hermes-tavern"}
    user_a_session = store.get_active_session(user_a_key)
    user_b_session = store.get_active_session(user_b_key)
    assert user_a_session is not None
    assert user_b_session is not None
    assert user_a_session["id"] != user_b_session["id"]

    pause_a = pre_gateway_dispatch(
        event=_event_for("/rp pause", user_id="user-a", message_id="m-pause-a"),
        gateway=gateway,
        store=store,
    )
    pause_b = pre_gateway_dispatch(
        event=_event_for("/rp pause", user_id="user-b", message_id="m-pause-b"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert pause_a == {"action": "skip", "reason": "hermes-tavern"}
    assert pause_b == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session(user_a_key) is None
    assert store.get_active_session(user_b_key) is None
    assert store.get_paused_session(user_a_key)["id"] == user_a_session["id"]
    assert store.get_paused_session(user_b_key)["id"] == user_b_session["id"]

    resume_a = pre_gateway_dispatch(
        event=_event_for("/rp resume", user_id="user-a", message_id="m-resume-a"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert resume_a == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session(user_a_key)["id"] == user_a_session["id"]
    assert store.get_paused_session(user_a_key) is None
    assert store.get_active_session(user_b_key) is None
    assert store.get_paused_session(user_b_key)["id"] == user_b_session["id"]

    resumed_user_message = pre_gateway_dispatch(
        event=_event_for("resumed user should be stored", user_id="user-a", message_id="m-active-a"),
        gateway=gateway,
        store=store,
    )
    paused_user_message = pre_gateway_dispatch(
        event=_event_for("still paused user should fall through", user_id="user-b", message_id="m-paused-b"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert resumed_user_message == {"action": "skip", "reason": "hermes-tavern"}
    assert paused_user_message == {"action": "allow"}
    assert "resumed user should be stored" in [
        row["content"] for row in store.get_recent_messages(user_a_session["id"], limit=10)
    ]
    assert "still paused user should fall through" not in [
        row["content"] for row in store.get_recent_messages(user_b_session["id"], limit=10)
    ]

    sessions_a = pre_gateway_dispatch(
        event=_event_for("/rp sessions all", user_id="user-a", message_id="m-sessions-a"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert sessions_a == {"action": "skip", "reason": "hermes-tavern"}
    sent_text = adapter.send.await_args.args[1]
    assert user_a_session["id"][:8] in sent_text
    assert user_b_session["id"][:8] not in sent_text
    assert user_b_session["id"] not in sent_text
    assert user_b_key not in sent_text


@pytest.mark.asyncio
async def test_gateway_hook_switch_same_scope_does_not_leak_other_scope(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    alice = parse_character_card({"name": "Alice", "first_mes": "Hello from Alice."})
    bob = parse_character_card({"name": "BobPhase86Secret", "first_mes": "Hello from Bob."})
    store.save_card(alice)
    store.save_card(bob)
    gateway, adapter = _gateway()
    caller_key = "telegram:chat:chat-1:thread:main:user:user-a"
    other_key = "telegram:chat:chat-1:thread:main:user:user-b"
    caller_target_id = "phase86a-target-same-scope"
    other_tempting_id = "other86a-scope-secret"
    caller_active_id = "active86-current-same-scope"

    caller_start = pre_gateway_dispatch(
        event=_event_for("/rp start Alice", user_id="user-a", message_id="m-start-a"),
        gateway=gateway,
        store=store,
    )
    other_start = pre_gateway_dispatch(
        event=_event_for("/rp start BobPhase86Secret", user_id="user-b", message_id="m-start-b"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert caller_start == {"action": "skip", "reason": "hermes-tavern"}
    assert other_start == {"action": "skip", "reason": "hermes-tavern"}
    caller_active = store.get_active_session(caller_key)
    other_session = store.get_active_session(other_key)
    assert caller_active is not None
    assert other_session is not None
    caller_target = store.clone_session(caller_active["id"], caller_key, title="CallerPhase86Target")
    assert store.archive_active_session(caller_target["session_key"]) is True

    with store.connect() as conn:
        for old_id, new_id in (
            (caller_active["id"], caller_active_id),
            (caller_target["id"], caller_target_id),
            (other_session["id"], other_tempting_id),
        ):
            conn.execute("UPDATE sessions SET id = ? WHERE id = ?", (new_id, old_id))
            conn.execute("UPDATE messages SET session_id = ? WHERE session_id = ?", (new_id, old_id))
        conn.execute(
            "UPDATE sessions SET session_key = ? WHERE id = ?",
            (caller_target_id, caller_target_id),
        )
        conn.execute(
            "UPDATE sessions SET title = ? WHERE id = ?",
            ("OtherScopePhase86SecretTitle", other_tempting_id),
        )

    switch = pre_gateway_dispatch(
        event=_event_for(
            f"/rp switch {caller_target_id[:8]}",
            user_id="user-a",
            message_id="m-switch-a",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert switch == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session(caller_key)["id"] == caller_target_id
    assert store.get_active_session(other_key)["id"] == other_tempting_id
    caller_sessions = store.list_sessions_for_scope(caller_key, include_all=True)
    assert {session["id"]: session["status"] for session in caller_sessions} == {
        caller_active_id: "archived",
        caller_target_id: "active",
    }

    switch_text = adapter.send.await_args.args[1]
    assert caller_target_id[:8] in switch_text
    assert "CallerPhase86Target" in switch_text
    assert other_tempting_id[:8] not in switch_text
    assert other_tempting_id not in switch_text
    assert other_key not in switch_text
    assert "BobPhase86Secret" not in switch_text
    assert "OtherScopePhase86SecretTitle" not in switch_text

    post_switch = pre_gateway_dispatch(
        event=_event_for(
            "post switch caller message",
            user_id="user-a",
            message_id="m-post-switch-a",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert post_switch == {"action": "skip", "reason": "hermes-tavern"}
    assert "post switch caller message" in [
        row["content"] for row in store.get_recent_messages(caller_target_id, limit=10)
    ]
    assert "post switch caller message" not in [
        row["content"] for row in store.get_recent_messages(caller_active_id, limit=10)
    ]
    assert "post switch caller message" not in [
        row["content"] for row in store.get_recent_messages(other_tempting_id, limit=10)
    ]


@pytest.mark.parametrize(
    ("command", "status"),
    [
        ("/rp end", "ended"),
        ("/rp archive", "archived"),
    ],
)
@pytest.mark.asyncio
async def test_gateway_hook_end_and_archive_only_mutate_caller_scope(
    command,
    status,
    tmp_path,
):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card({"name": "Alice", "first_mes": "Hello."})
    store.save_card(card)
    gateway, adapter = _gateway()
    user_a_key = "telegram:chat:chat-1:thread:main:user:user-a"
    user_b_key = "telegram:chat:chat-1:thread:main:user:user-b"

    start_a = pre_gateway_dispatch(
        event=_event_for("/rp start Alice", user_id="user-a", message_id=f"m-start-a-{status}"),
        gateway=gateway,
        store=store,
    )
    start_b = pre_gateway_dispatch(
        event=_event_for("/rp start Alice", user_id="user-b", message_id=f"m-start-b-{status}"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert start_a == {"action": "skip", "reason": "hermes-tavern"}
    assert start_b == {"action": "skip", "reason": "hermes-tavern"}
    user_a_session = store.get_active_session(user_a_key)
    user_b_session = store.get_active_session(user_b_key)
    assert user_a_session is not None
    assert user_b_session is not None
    assert user_a_session["id"] != user_b_session["id"]

    result = pre_gateway_dispatch(
        event=_event_for(command, user_id="user-a", message_id=f"m-command-a-{status}"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert result == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session(user_a_key) is None
    assert store.get_active_session(user_b_key)["id"] == user_b_session["id"]
    user_a_sessions = store.list_sessions_for_scope(user_a_key, include_all=True)
    assert [(session["id"], session["status"]) for session in user_a_sessions] == [
        (user_a_session["id"], status)
    ]

    inactive_user_message = pre_gateway_dispatch(
        event=_event_for(
            f"{status} user should fall through",
            user_id="user-a",
            message_id=f"m-inactive-a-{status}",
        ),
        gateway=gateway,
        store=store,
    )
    active_user_message = pre_gateway_dispatch(
        event=_event_for(
            f"user b still active after {status}",
            user_id="user-b",
            message_id=f"m-active-b-{status}",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert inactive_user_message == {"action": "allow"}
    assert active_user_message == {"action": "skip", "reason": "hermes-tavern"}
    assert f"{status} user should fall through" not in [
        row["content"] for row in store.get_recent_messages(user_a_session["id"], limit=10)
    ]
    assert f"user b still active after {status}" in [
        row["content"] for row in store.get_recent_messages(user_b_session["id"], limit=10)
    ]

    sessions_a = pre_gateway_dispatch(
        event=_event_for("/rp sessions all", user_id="user-a", message_id=f"m-sessions-a-{status}"),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert sessions_a == {"action": "skip", "reason": "hermes-tavern"}
    sent_text = adapter.send.await_args.args[1]
    assert user_a_session["id"][:8] in sent_text
    assert status in sent_text
    assert user_b_session["id"][:8] not in sent_text
    assert user_b_session["id"] not in sent_text
    assert user_b_key not in sent_text


@pytest.mark.asyncio
async def test_gateway_hook_topic_loop_keeps_active_messages_and_pause_scoped(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card({"name": "Alice", "first_mes": "Hello."})
    store.save_card(card)
    gateway, adapter = _gateway()
    thread_a = "topic-a"
    thread_b = "topic-b"
    thread_a_key = f"telegram:chat:chat-1:thread:{thread_a}:user:user-1"
    thread_b_key = f"telegram:chat:chat-1:thread:{thread_b}:user:user-1"

    start_a = pre_gateway_dispatch(
        event=_event_for(
            "/rp start Alice",
            user_id="user-1",
            thread_id=thread_a,
            message_id="m-start-a",
        ),
        gateway=gateway,
        store=store,
    )
    start_b = pre_gateway_dispatch(
        event=_event_for(
            "/rp start Alice",
            user_id="user-1",
            thread_id=thread_b,
            message_id="m-start-b",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert start_a == {"action": "skip", "reason": "hermes-tavern"}
    assert start_b == {"action": "skip", "reason": "hermes-tavern"}
    thread_a_session = store.get_active_session(thread_a_key)
    thread_b_session = store.get_active_session(thread_b_key)
    assert thread_a_session is not None
    assert thread_b_session is not None
    assert thread_a_session["id"] != thread_b_session["id"]

    message_a = pre_gateway_dispatch(
        event=_event_for(
            "thread A reply",
            user_id="user-1",
            thread_id=thread_a,
            message_id="m-msg-a",
        ),
        gateway=gateway,
        store=store,
    )
    message_b = pre_gateway_dispatch(
        event=_event_for(
            "thread B reply",
            user_id="user-1",
            thread_id=thread_b,
            message_id="m-msg-b",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert message_a == {"action": "skip", "reason": "hermes-tavern"}
    assert message_b == {"action": "skip", "reason": "hermes-tavern"}
    thread_a_contents = [
        row["content"] for row in store.get_recent_messages(thread_a_session["id"], limit=4)
    ]
    thread_b_contents = [
        row["content"] for row in store.get_recent_messages(thread_b_session["id"], limit=4)
    ]
    assert thread_a_contents == [
        "Hello.",
        "thread A reply",
        "[Hermes Tavern fake adapter response]",
    ]
    assert thread_b_contents == [
        "Hello.",
        "thread B reply",
        "[Hermes Tavern fake adapter response]",
    ]
    assert "thread B reply" not in thread_a_contents
    assert "thread A reply" not in thread_b_contents

    pause_a = pre_gateway_dispatch(
        event=_event_for(
            "/rp pause",
            user_id="user-1",
            thread_id=thread_a,
            message_id="m-pause-a",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert pause_a == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session(thread_a_key) is None
    assert store.get_paused_session(thread_a_key)["id"] == thread_a_session["id"]
    assert store.get_active_session(thread_b_key)["id"] == thread_b_session["id"]
    assert store.get_paused_session(thread_b_key) is None

    paused_thread_message = pre_gateway_dispatch(
        event=_event_for(
            "paused thread should fall through",
            user_id="user-1",
            thread_id=thread_a,
            message_id="m-paused-a",
        ),
        gateway=gateway,
        store=store,
    )
    active_thread_message = pre_gateway_dispatch(
        event=_event_for(
            "thread B still active",
            user_id="user-1",
            thread_id=thread_b,
            message_id="m-active-b",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert paused_thread_message == {"action": "allow"}
    assert active_thread_message == {"action": "skip", "reason": "hermes-tavern"}
    assert "paused thread should fall through" not in [
        row["content"] for row in store.get_recent_messages(thread_a_session["id"], limit=10)
    ]
    assert "thread B still active" in [
        row["content"] for row in store.get_recent_messages(thread_b_session["id"], limit=10)
    ]

    sessions_a = pre_gateway_dispatch(
        event=_event_for(
            "/rp sessions all",
            user_id="user-1",
            thread_id=thread_a,
            message_id="m-sessions-a",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert sessions_a == {"action": "skip", "reason": "hermes-tavern"}
    sent_text = adapter.send.await_args.args[1]
    assert thread_a_session["id"][:8] in sent_text
    assert thread_b_session["id"][:8] not in sent_text
    assert thread_b_session["id"] not in sent_text
    assert thread_b_key not in sent_text
    assert thread_b not in sent_text


@pytest.mark.asyncio
async def test_gateway_hook_platform_loop_keeps_active_messages_and_pause_scoped(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card({"name": "Alice", "first_mes": "Hello."})
    store.save_card(card)
    gateway, telegram_adapter, discord_adapter = _multi_platform_gateway()
    telegram_key = "telegram:chat:chat-1:thread:main:user:user-1"
    discord_key = "discord:chat:chat-1:thread:main:user:user-1"

    telegram_start = pre_gateway_dispatch(
        event=_event_for(
            "/rp start Alice",
            user_id="user-1",
            platform="telegram",
            message_id="m-start-telegram",
        ),
        gateway=gateway,
        store=store,
    )
    discord_start = pre_gateway_dispatch(
        event=_event_for(
            "/rp start Alice",
            user_id="user-1",
            platform="discord",
            message_id="m-start-discord",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert telegram_start == {"action": "skip", "reason": "hermes-tavern"}
    assert discord_start == {"action": "skip", "reason": "hermes-tavern"}
    telegram_session = store.get_active_session(telegram_key)
    discord_session = store.get_active_session(discord_key)
    assert telegram_session is not None
    assert discord_session is not None
    assert telegram_session["id"] != discord_session["id"]
    assert telegram_adapter.send.await_args_list[0].args[0] == "chat-1"
    assert discord_adapter.send.await_args_list[0].args[0] == "chat-1"
    assert "Alice" in telegram_adapter.send.await_args_list[0].args[1]
    assert "Alice" in discord_adapter.send.await_args_list[0].args[1]

    telegram_message = pre_gateway_dispatch(
        event=_event_for(
            "telegram reply",
            user_id="user-1",
            platform="telegram",
            message_id="m-msg-telegram",
        ),
        gateway=gateway,
        store=store,
    )
    discord_message = pre_gateway_dispatch(
        event=_event_for(
            "discord reply",
            user_id="user-1",
            platform="discord",
            message_id="m-msg-discord",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert telegram_message == {"action": "skip", "reason": "hermes-tavern"}
    assert discord_message == {"action": "skip", "reason": "hermes-tavern"}
    telegram_contents = [
        row["content"] for row in store.get_recent_messages(telegram_session["id"], limit=4)
    ]
    discord_contents = [
        row["content"] for row in store.get_recent_messages(discord_session["id"], limit=4)
    ]
    assert telegram_contents == [
        "Hello.",
        "telegram reply",
        "[Hermes Tavern fake adapter response]",
    ]
    assert discord_contents == [
        "Hello.",
        "discord reply",
        "[Hermes Tavern fake adapter response]",
    ]
    assert "discord reply" not in telegram_contents
    assert "telegram reply" not in discord_contents
    telegram_adapter.send.assert_any_await("chat-1", "[Hermes Tavern fake adapter response]")
    discord_adapter.send.assert_any_await("chat-1", "[Hermes Tavern fake adapter response]")

    telegram_pause = pre_gateway_dispatch(
        event=_event_for(
            "/rp pause",
            user_id="user-1",
            platform="telegram",
            message_id="m-pause-telegram",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert telegram_pause == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session(telegram_key) is None
    assert store.get_paused_session(telegram_key)["id"] == telegram_session["id"]
    assert store.get_active_session(discord_key)["id"] == discord_session["id"]
    assert store.get_paused_session(discord_key) is None

    paused_telegram_message = pre_gateway_dispatch(
        event=_event_for(
            "paused telegram should fall through",
            user_id="user-1",
            platform="telegram",
            message_id="m-paused-telegram",
        ),
        gateway=gateway,
        store=store,
    )
    active_discord_message = pre_gateway_dispatch(
        event=_event_for(
            "discord still active",
            user_id="user-1",
            platform="discord",
            message_id="m-active-discord",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert paused_telegram_message == {"action": "allow"}
    assert active_discord_message == {"action": "skip", "reason": "hermes-tavern"}
    assert "paused telegram should fall through" not in [
        row["content"] for row in store.get_recent_messages(telegram_session["id"], limit=10)
    ]
    assert "discord still active" in [
        row["content"] for row in store.get_recent_messages(discord_session["id"], limit=10)
    ]

    telegram_sessions = pre_gateway_dispatch(
        event=_event_for(
            "/rp sessions all",
            user_id="user-1",
            platform="telegram",
            message_id="m-sessions-telegram",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert telegram_sessions == {"action": "skip", "reason": "hermes-tavern"}
    sent_text = telegram_adapter.send.await_args.args[1]
    assert telegram_adapter.send.await_args.args[0] == "chat-1"
    assert discord_adapter.send.await_args.args[0] == "chat-1"
    assert telegram_session["id"][:8] in sent_text
    assert discord_session["id"][:8] not in sent_text
    assert discord_session["id"] not in sent_text
    assert discord_key not in sent_text
    assert "discord" not in sent_text.lower()


@pytest.mark.asyncio
async def test_gateway_hook_chat_loop_keeps_active_messages_and_pause_scoped(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card({"name": "Alice", "first_mes": "Hello."})
    store.save_card(card)
    gateway, adapter = _gateway()
    chat1_key = "telegram:chat:chat-1:thread:main:user:user-1"
    chat2_key = "telegram:chat:chat-2:thread:main:user:user-1"

    chat1_start = pre_gateway_dispatch(
        event=_event_for(
            "/rp start Alice",
            user_id="user-1",
            chat_id="chat-1",
            message_id="m-start-chat-1",
        ),
        gateway=gateway,
        store=store,
    )
    chat2_start = pre_gateway_dispatch(
        event=_event_for(
            "/rp start Alice",
            user_id="user-1",
            chat_id="chat-2",
            message_id="m-start-chat-2",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert chat1_start == {"action": "skip", "reason": "hermes-tavern"}
    assert chat2_start == {"action": "skip", "reason": "hermes-tavern"}
    chat1_session = store.get_active_session(chat1_key)
    chat2_session = store.get_active_session(chat2_key)
    assert chat1_session is not None
    assert chat2_session is not None
    assert chat1_session["id"] != chat2_session["id"]
    assert adapter.send.await_args_list[0].args[0] == "chat-1"
    assert adapter.send.await_args_list[1].args[0] == "chat-2"
    assert "Alice" in adapter.send.await_args_list[0].args[1]
    assert "Alice" in adapter.send.await_args_list[1].args[1]

    chat1_message = pre_gateway_dispatch(
        event=_event_for(
            "chat one reply",
            user_id="user-1",
            chat_id="chat-1",
            message_id="m-msg-chat-1",
        ),
        gateway=gateway,
        store=store,
    )
    chat2_message = pre_gateway_dispatch(
        event=_event_for(
            "chat two reply",
            user_id="user-1",
            chat_id="chat-2",
            message_id="m-msg-chat-2",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert chat1_message == {"action": "skip", "reason": "hermes-tavern"}
    assert chat2_message == {"action": "skip", "reason": "hermes-tavern"}
    chat1_contents = [
        row["content"] for row in store.get_recent_messages(chat1_session["id"], limit=4)
    ]
    chat2_contents = [
        row["content"] for row in store.get_recent_messages(chat2_session["id"], limit=4)
    ]
    assert chat1_contents == [
        "Hello.",
        "chat one reply",
        "[Hermes Tavern fake adapter response]",
    ]
    assert chat2_contents == [
        "Hello.",
        "chat two reply",
        "[Hermes Tavern fake adapter response]",
    ]
    assert "chat two reply" not in chat1_contents
    assert "chat one reply" not in chat2_contents
    adapter.send.assert_any_await("chat-1", "[Hermes Tavern fake adapter response]")
    adapter.send.assert_any_await("chat-2", "[Hermes Tavern fake adapter response]")

    chat1_pause = pre_gateway_dispatch(
        event=_event_for(
            "/rp pause",
            user_id="user-1",
            chat_id="chat-1",
            message_id="m-pause-chat-1",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert chat1_pause == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session(chat1_key) is None
    assert store.get_paused_session(chat1_key)["id"] == chat1_session["id"]
    assert store.get_active_session(chat2_key)["id"] == chat2_session["id"]
    assert store.get_paused_session(chat2_key) is None
    assert adapter.send.await_args.args[0] == "chat-1"

    paused_chat_message = pre_gateway_dispatch(
        event=_event_for(
            "paused chat should fall through",
            user_id="user-1",
            chat_id="chat-1",
            message_id="m-paused-chat-1",
        ),
        gateway=gateway,
        store=store,
    )
    active_chat_message = pre_gateway_dispatch(
        event=_event_for(
            "chat two still active",
            user_id="user-1",
            chat_id="chat-2",
            message_id="m-active-chat-2",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert paused_chat_message == {"action": "allow"}
    assert active_chat_message == {"action": "skip", "reason": "hermes-tavern"}
    assert "paused chat should fall through" not in [
        row["content"] for row in store.get_recent_messages(chat1_session["id"], limit=10)
    ]
    assert "chat two still active" in [
        row["content"] for row in store.get_recent_messages(chat2_session["id"], limit=10)
    ]
    adapter.send.assert_any_await("chat-2", "[Hermes Tavern fake adapter response]")

    chat1_sessions = pre_gateway_dispatch(
        event=_event_for(
            "/rp sessions all",
            user_id="user-1",
            chat_id="chat-1",
            message_id="m-sessions-chat-1",
        ),
        gateway=gateway,
        store=store,
    )
    await asyncio.sleep(0)

    assert chat1_sessions == {"action": "skip", "reason": "hermes-tavern"}
    sent_chat_id, sent_text = adapter.send.await_args.args
    assert sent_chat_id == "chat-1"
    assert chat1_session["id"][:8] in sent_text
    assert chat2_session["id"][:8] not in sent_text
    assert chat2_session["id"] not in sent_text
    assert chat2_key not in sent_text
    assert "chat-2" not in sent_text


@pytest.mark.asyncio
async def test_gateway_hook_end_deactivates_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    gateway, adapter = _gateway()

    result = pre_gateway_dispatch(event=_event("/rp end"), gateway=gateway, store=store)
    await asyncio.sleep(0)

    assert result == {"action": "skip", "reason": "hermes-tavern"}
    assert store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1") is None
    assert "ended" in adapter.send.await_args.args[1].lower()
