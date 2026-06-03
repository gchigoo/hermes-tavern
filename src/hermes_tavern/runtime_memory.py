"""Memory commands for Hermes Tavern runtime."""

from __future__ import annotations

from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.memory import summarize_recent_messages
from hermes_tavern.model_router import ModelRouter
from hermes_tavern.runtime_utils import mobile_preview, parse_pagination


def memory_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "add":
        return memory_add(runtime, command, event)
    if subcommand in {"forget", "delete", "remove"}:
        return memory_forget(runtime, command, event)
    if subcommand == "list":
        return memory_list(runtime, command, event)
    if subcommand == "summary":
        return memory_summary(runtime, command, event)
    if subcommand == "debug":
        return memory_debug(runtime, event)
    return "Usage: /rp memory add <fact> | /rp memory forget <fact-id|all> | /rp memory list [limit] [page] | /rp memory summary [set <text>|clear|summarize [limit]] | /rp memory debug"


def memory_add(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp memory add <fact>"
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session. Start one before adding memory."
    fact_text = " ".join(command.args[1:]).strip()
    fact_id = runtime.store.add_session_memory_fact(session_key, fact_text)
    if fact_id is None:
        return "Could not add memory fact to active session."
    return f"Hermes Tavern memory fact saved: {fact_id}"


def memory_list(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session."
    extra_args = command.args[1:] if command.args else []
    parsed = parse_pagination(extra_args, default_limit=10, max_limit=25)
    if parsed is None:
        return "Usage: /rp memory list [limit] [page]"
    limit, page = parsed
    total = runtime.store.count_session_memory_facts(session_key)
    total_pages = max(1, -(-total // limit))
    page = min(page, total_pages)
    offset = (page - 1) * limit
    facts = runtime.store.list_session_memory_facts(session_key, limit=limit, offset=offset)
    summary = runtime.store.get_session_summary(session_key)
    shown = len(facts)
    lines = ["Hermes Tavern session memory:"]
    lines.append(f"summary: {'set' if summary else 'none'}")
    if total == 0:
        lines.append("facts: none")
    else:
        lines.append(f"facts (page {page}/{total_pages}, {shown} shown, {total} total):")
        for fact in facts:
            preview = mobile_preview(fact.get("content") or "", 80)
            lines.append(f"  - [{fact.get('id', '')[:8]}] ({fact.get('importance', 1)}) {preview}")
    if page > 1:
        lines.append(f"prev: /rp memory list {limit} {page - 1}")
    if page < total_pages:
        lines.append(f"next: /rp memory list {limit} {page + 1}")
    return "\n".join(lines)


def memory_forget(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session."
    if len(command.args) < 2:
        return "Usage: /rp memory forget <fact-id|all>"
    ref = command.args[1].strip()
    deleted = runtime.store.delete_session_memory_fact(session_key, ref)
    if deleted <= 0:
        return f"No Hermes Tavern memory fact matched: {ref}"
    if ref.lower() == "all":
        return f"Hermes Tavern memory facts cleared: {deleted}"
    return f"Hermes Tavern memory fact forgotten: {ref}"


def memory_summary(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    action = command.args[1].lower() if len(command.args) > 1 else "show"
    if action == "set":
        summary = " ".join(command.args[2:]).strip()
        if not summary:
            return "Usage: /rp memory summary set <text>"
        runtime.store.set_session_summary(session_key, summary)
        return "Hermes Tavern session summary saved."
    if action == "clear":
        if runtime.store.clear_session_summary(session_key):
            return "Hermes Tavern session summary cleared."
        return "No Hermes Tavern session summary set."
    if action == "summarize":
        limit = 12
        live = False
        trailing = list(command.args[2:]) if len(command.args) > 2 else []
        while trailing and trailing[-1].lower() == "live":
            live = True
            trailing.pop()
        if trailing:
            try:
                limit = max(1, min(50, int(trailing[0])))
            except ValueError:
                return "Usage: /rp memory summary summarize [limit] [live]"
        messages = runtime.store.get_recent_messages(session["id"], limit=limit)
        if not messages:
            return "No recent session messages to summarize."
        if live:
            return live_memory_summarize(runtime, session, session_key, messages, event)
        summary_text = summarize_recent_messages(messages, limit=limit)
        if not summary_text:
            return "No recent session messages to summarize."
        runtime.store.set_session_summary(session_key, summary_text)
        return "Hermes Tavern deterministic summary saved.\n" + summary_text
    if action != "show":
        return "Usage: /rp memory summary [set <text>|clear|summarize [limit] [live]]"
    summary_row = runtime.store.get_session_summary(session_key)
    if summary_row is None or not summary_row.get("summary"):
        return "No Hermes Tavern session summary set."
    return "Hermes Tavern session summary:\n" + summary_row["summary"]


def memory_debug(runtime: Any, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    modules = runtime._session_memory_modules(session)
    lines = [
        f"Memory facts: {len(runtime.store.list_session_memory_facts(session_key))}",
        f"Memory summary: {'yes' if runtime.store.get_session_summary(session_key) else 'none'}",
        f"modules: {len(modules)}",
    ]
    for module in modules:
        preview = module.content[:120].replace("\n", " ")
        lines.append(f"  - {module.name}: {preview}")
    return "\n".join(lines)


def live_memory_summarize(
    runtime: Any,
    session: dict[str, Any],
    session_key: str,
    messages: list[dict[str, Any]],
    event: Any,
) -> str:
    """Generate a rolling summary from recent messages using the Hermes adapter."""
    adapter_mode = session.get("adapter_mode") or "fake"
    live_confirmed = bool(session.get("live_confirmed"))

    if adapter_mode != "hermes" or not live_confirmed:
        return (
            "Live summarization requires hermes adapter mode + live confirmed. "
            "Use /rp model mode hermes then /rp model live confirm first, "
            "or run /rp memory summary summarize without 'live' for mock summarization."
        )

    previous = runtime.store.get_session_summary(session_key)
    previous_text = previous["summary"].strip() if previous and previous.get("summary") else ""

    recent_lines = []
    for m in messages[-24:]:
        role = m.get("role", "unknown")
        content = (m.get("content") or "").strip()
        if role not in ("user", "assistant") or not content:
            continue
        snippet = content[:300]
        if len(content) > 300:
            snippet = snippet.rstrip() + "…"
        recent_lines.append(f"{role}: {snippet}")

    previous_block = ""
    if previous_text:
        previous_block = "Previous summary:\n" + previous_text[:800] + "\n\n"

    summarization_messages = [
        {
            "role": "system",
            "content": (
                "You are a session summarizer for an ongoing roleplay/novel conversation. "
                "Write a concise narrative summary of what has happened so far. "
                "Merge the previous summary (if provided) with the recent messages. "
                "Preserve key plot points, character decisions, relationship developments, "
                "and important revelations. Write in third-person past tense. "
                "Keep the summary under 600 words. "
                "Output ONLY the summary text, no preamble or commentary."
            ),
        },
        {
            "role": "user",
            "content": (
                previous_block
                + "Recent session turns:\n"
                + "\n".join(recent_lines)
                + "\n\nWrite a rolling summary merging the above."
            ),
        },
    ]

    descriptor = ModelRouter().resolve(session_row=session, store=runtime.store)
    try:
        summary = runtime._generate_with_session_adapter(
            session, summarization_messages, descriptor
        )
    except Exception:
        summary = summarize_recent_messages(messages, limit=len(messages))

    if not summary.strip():
        return "Live summarization produced empty result."

    runtime.store.set_session_summary(session_key, summary.strip())
    preview = summary.strip()[:360]
    if len(summary.strip()) > 360:
        preview += "…"
    return (
        f"Hermes Tavern live summary saved ({len(summary.split())} words).\n"
        + preview
    )
