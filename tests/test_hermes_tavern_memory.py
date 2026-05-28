import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.memory import (
    TavernMemoryContext,
    TavernMemoryFact,
    build_memory_modules,
    summarize_recent_messages,
)
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


def test_memory_store_round_trips_session_facts_and_summary(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session(SESSION_KEY)

    fact_id = store.add_session_memory_fact(SESSION_KEY, "Alice trusts the moon map.", importance=3)
    store.set_session_summary(SESSION_KEY, "Alice and Bob reached the observatory.")

    facts = store.list_session_memory_facts(SESSION_KEY)
    summary = store.get_session_summary(SESSION_KEY)
    assert fact_id is not None
    assert facts[0]["content"] == "Alice trusts the moon map."
    assert facts[0]["importance"] == 3
    assert summary["summary"] == "Alice and Bob reached the observatory."


def test_memory_store_deletes_facts_and_clears_summary(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session(SESSION_KEY)

    fact_id = store.add_session_memory_fact(SESSION_KEY, "Alice trusts the moon map.", importance=3)
    store.set_session_summary(SESSION_KEY, "Alice and Bob reached the observatory.")

    assert store.delete_session_memory_fact(SESSION_KEY, fact_id[:8]) == 1
    assert store.list_session_memory_facts(SESSION_KEY) == []
    assert store.clear_session_summary(SESSION_KEY) is True
    assert store.get_session_summary(SESSION_KEY) is None


def test_memory_modules_include_summary_and_budgeted_facts():
    modules = build_memory_modules(
        TavernMemoryContext(
            summary="They are travelling at night.",
            facts=(
                TavernMemoryFact(id="low", content="Low importance note", importance=1),
                TavernMemoryFact(id="high", content="High importance note", importance=5),
            ),
        )
    )

    assert [module.name for module in modules] == ["memory:summary", "memory:facts"]
    assert "They are travelling at night" in modules[0].content
    assert "High importance note" in modules[1].content
    assert "Low importance note" in modules[1].content


def test_summarize_recent_messages_is_deterministic_and_local():
    summary = summarize_recent_messages([
        {"role": "assistant", "content": "Hello there."},
        {"role": "user", "content": "We should inspect the moon map."},
    ])

    assert summary == (
        "Recent session turns:\n"
        "- assistant: Hello there.\n"
        "- user: We should inspect the moon map."
    )


@pytest.mark.asyncio
async def test_memory_runtime_add_list_summary_debug(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session(SESSION_KEY)
    runtime = TavernRuntime(store)

    added = await runtime.handle_command(
        RPCommand("memory", ["add", "Alice", "trusts", "the", "moon", "map."], "/rp memory add"),
        Event(),
    )
    set_summary = await runtime.handle_command(
        RPCommand("memory", ["summary", "set", "The", "party", "found", "a", "map."], "/rp memory summary set"),
        Event(),
    )
    listed = await runtime.handle_command(RPCommand("memory", ["list"], "/rp memory list"), Event())
    debug = await runtime.handle_command(RPCommand("memory", ["debug"], "/rp memory debug"), Event())

    assert "memory fact saved" in added
    assert "summary saved" in set_summary
    assert "Alice trusts the moon map." in listed
    assert "[" in listed and "]" in listed
    assert "summary: set" in listed
    assert "memory:summary" in debug
    assert "memory:facts" in debug


@pytest.mark.asyncio
async def test_memory_runtime_forget_and_summary_clear(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session(SESSION_KEY)
    runtime = TavernRuntime(store)

    fact_id = store.add_session_memory_fact(SESSION_KEY, "Alice trusts the moon map.", importance=3)
    store.set_session_summary(SESSION_KEY, "The party found a map.")

    forgotten = await runtime.handle_command(
        RPCommand("memory", ["forget", fact_id[:8]], "/rp memory forget"),
        Event(),
    )
    cleared = await runtime.handle_command(
        RPCommand("memory", ["summary", "clear"], "/rp memory summary clear"),
        Event(),
    )

    assert "memory fact forgotten" in forgotten
    assert "summary cleared" in cleared
    assert store.list_session_memory_facts(SESSION_KEY) == []
    assert store.get_session_summary(SESSION_KEY) is None


@pytest.mark.asyncio
async def test_memory_modules_appear_in_debug_prompt(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    store.add_session_memory_fact(SESSION_KEY, "Alice trusts the moon map.", importance=3)
    store.set_session_summary(SESSION_KEY, "The group reached the observatory.")

    prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "memory_facts: 1" in prompt
    assert "memory_summary: yes" in prompt
    assert "memory:summary" in prompt
    assert "memory:facts" in prompt
    assert "The group reached the observatory" in prompt
    assert "Alice trusts the moon map" in prompt


@pytest.mark.asyncio
async def test_memory_summary_summarize_uses_recent_messages_without_provider(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    active = store.get_active_session(SESSION_KEY)
    store.append_message(active["id"], "user", "Remember the cracked moon.")
    store.append_message(active["id"], "assistant", "I will keep it in mind.")

    response = await runtime.handle_command(
        RPCommand("memory", ["summary", "summarize", "4"], "/rp memory summary summarize 4"),
        Event(),
    )

    assert "deterministic summary saved" in response
    assert "Remember the cracked moon" in response
    assert "I will keep it in mind" in store.get_session_summary(SESSION_KEY)["summary"]
