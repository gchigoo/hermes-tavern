import asyncio
from enum import Enum
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from plugins.hermes_tavern.db import TavernStore
from gateway.platforms.base import BasePlatformAdapter
from plugins.hermes_tavern.gateway_hook import _get_adapter, _send_if_possible, pre_gateway_dispatch
from plugins.hermes_tavern.importers.cards import parse_character_card


def _event(text: str) -> SimpleNamespace:
    return SimpleNamespace(
        text=text,
        message_id="m1",
        source=SimpleNamespace(
            platform="telegram",
            chat_id="chat-1",
            thread_id=None,
            user_id="user-1",
        ),
    )


def _gateway() -> SimpleNamespace:
    adapter = SimpleNamespace(send=AsyncMock())
    return SimpleNamespace(adapters={"telegram": adapter}), adapter


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
