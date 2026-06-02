"""Model route commands for Hermes Tavern runtime."""

from __future__ import annotations

from typing import Any

from hermes_tavern.adapters import HermesChatCompletionAdapter
from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.model_router import ModelRouter
from hermes_tavern.provider_bridge import (
    APIYI_BASE_URL,
    APIYI_CONTEXT_WINDOW,
    APIYI_DEFAULT_MODEL,
    APIYI_PROVIDER,
    HermesRuntimeProviderResolver,
    sanitize_provider_payload,
    validate_provider_base_url,
)

_router = ModelRouter()


def model_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0] if command.args else "status"
    if subcommand == "status":
        return runtime._model_status(event)
    if subcommand == "profiles":
        return runtime._model_profiles()
    if subcommand == "seed" and len(command.args) > 1 and command.args[1].lower() == "apiyi":
        return runtime._model_seed_apiyi()
    if subcommand == "use":
        return runtime._model_use(command, event)
    if subcommand == "mode":
        return runtime._model_mode(command, event)
    if subcommand == "live":
        return runtime._model_live(command, event)
    if subcommand == "test":
        return runtime._model_test(event)
    return (
        "Usage: /rp model status | /rp model profiles | /rp model seed apiyi | "
        "/rp model use <profile> | /rp model mode [fake|hermes] | "
        "/rp model live [status|confirm|off] | /rp model test"
    )


def model_status(runtime: Any, event: Any) -> str:
    session = runtime.store.get_active_session(session_key_from_event(event))
    descriptor = _router.resolve(session_row=session, store=runtime.store)
    data = sanitize_provider_payload(descriptor.to_debug_dict())
    lines = ["Hermes Tavern model route:"]
    for key in (
        "profile_name",
        "provider",
        "model_id",
        "mode",
        "context_window",
        "source",
    ):
        if key in data:
            lines.append(f"  {key}: {data[key]}")
    lines.append(f"  adapter_mode: {(session or {}).get('adapter_mode', 'fake')}")
    lines.append(f"  live_confirmed: {bool((session or {}).get('live_confirmed', 0))}")
    return "\n".join(lines)


def model_profiles(runtime: Any) -> str:
    profiles = runtime.store.list_model_profiles()
    if not profiles:
        return (
            "No Tavern model profiles configured.\n"
            "Default route: anthropic / claude-opus-4-6 (Opus 4.6 preference)."
        )
    lines = ["Hermes Tavern model profiles:"]
    for profile in profiles:
        lines.append(
            "  {name} ({id}): {provider} / {model_id} [{mode}]".format(
                name=profile["name"],
                id=profile["id"],
                provider=profile["provider"],
                model_id=profile["model_id"],
                mode=profile["mode"],
            )
        )
    return "\n".join(lines)


def model_seed_apiyi(runtime: Any) -> str:
    profile_id = runtime.store.save_model_profile(
        profile_id="apiyi-opus-default",
        name="apiyi-opus-default",
        provider=APIYI_PROVIDER,
        model_id=APIYI_DEFAULT_MODEL,
        mode="chat",
        context_window=APIYI_CONTEXT_WINDOW,
        raw={
            "base_url": APIYI_BASE_URL,
            "key_env": "APIYI_API_KEY",
            "api_mode": "chat_completions",
            "source": "apiyi_docs_openai_compatible",
        },
    )
    return (
        "Seeded APIYI Tavern model profile: "
        f"{profile_id} ({APIYI_PROVIDER} / {APIYI_DEFAULT_MODEL}). "
        "Credential is read from APIYI_API_KEY, not stored in Tavern DB."
    )


def model_use(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp model use <profile>"
    profile_ref = " ".join(command.args[1:]).strip()
    profile = runtime.store.get_model_profile(profile_ref)
    if profile is None:
        return f"Tavern model profile not found: {profile_ref}"
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session. Start one before binding a model profile."
    runtime.store.set_session_model_profile(session_key, profile["id"])
    return (
        "Hermes Tavern model profile selected: "
        f"{profile['name']} ({profile['provider']} / {profile['model_id']})."
    )


def model_mode(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if len(command.args) == 1:
        mode = (session or {}).get("adapter_mode", "fake")
        return f"Hermes Tavern model adapter mode: {mode}"
    requested = command.args[1].lower()
    if requested not in {"fake", "hermes"}:
        return "Usage: /rp model mode [fake|hermes]"
    if session is None:
        return "No active Hermes Tavern session. Start one before changing model mode."
    runtime.store.set_session_adapter_mode(session_key, requested)
    if requested == "hermes":
        return (
            "Hermes Tavern model adapter mode set to hermes. "
            "Provider resolution is enabled, but real generation is still mock-first/not wired."
        )
    return "Hermes Tavern model adapter mode set to fake."


def model_live(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session. Start one before changing live model access."
    action = command.args[1].lower() if len(command.args) > 1 else "status"
    if action == "status":
        return f"Hermes Tavern live provider calls enabled: {bool(session.get('live_confirmed', 0))}"
    if action == "confirm":
        runtime.store.set_session_live_confirmed(session_key, True)
        descriptor = _router.resolve(session_row=session, store=runtime.store)
        try:
            runtime.hermes_adapter = HermesChatCompletionAdapter(
                HermesRuntimeProviderResolver(descriptor).resolve
            )
        except Exception:
            pass
        return (
            "Hermes Tavern live provider calls ENABLED for this session. "
            "Messages may now call the selected external model provider."
        )
    if action in {"off", "disable", "disabled"}:
        runtime.store.set_session_live_confirmed(session_key, False)
        return "Hermes Tavern live provider calls disabled for this session."
    return "Usage: /rp model live [status|confirm|off]"


def model_test(runtime: Any, event: Any) -> str:
    """Dry-run: resolve provider config + validate base_url, no real generation."""
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."

    adapter_mode = session.get("adapter_mode") or "fake"
    live_confirmed = bool(session.get("live_confirmed", 0))
    descriptor = _router.resolve(session_row=session, store=runtime.store)

    lines = ["Hermes Tavern model test (dry-run, no generation):"]
    lines.append(f"  adapter_mode: {adapter_mode}")
    lines.append(f"  live_confirmed: {live_confirmed}")
    lines.append(f"  provider: {descriptor.provider}")
    lines.append(f"  model_id: {descriptor.model_id}")

    if adapter_mode != "hermes":
        lines.append("  result: fake mode — no live provider configured")
        lines.append("  hint: /rp model mode hermes + /rp model live confirm to enable real calls")
        lines.append("  note: no real generation performed")
        return "\n".join(lines)

    try:
        resolver = HermesRuntimeProviderResolver(descriptor)
        payload = resolver.resolve()
        safe = sanitize_provider_payload(payload)
    except Exception:
        lines.append("  resolver: error (check provider configuration)")
        lines.append("  result: not ready")
        return "\n".join(lines)

    base_url = safe.get("base_url") or ""
    url_status = "none"
    if base_url:
        try:
            validate_provider_base_url(base_url)
            url_status = "valid"
        except ValueError:
            url_status = "invalid (rejected)"

    has_key = bool(payload.get("api_key"))
    lines.append(f"  base_url: {url_status}")
    lines.append(f"  api_key: {'present' if has_key else 'missing'}")
    lines.append(f"  source: {safe.get('source', 'unknown')}")

    if url_status == "invalid (rejected)":
        lines.append("  result: not ready (base_url rejected — check profile configuration)")
    elif not has_key:
        lines.append("  result: not ready (api_key missing)")
    elif not live_confirmed:
        lines.append("  result: not ready (run /rp model live confirm to enable)")
    else:
        lines.append("  result: ready (live generation enabled)")

    lines.append("  note: no real generation performed")
    return "\n".join(lines)
