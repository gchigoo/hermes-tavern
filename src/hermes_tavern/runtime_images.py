"""Image command handlers for Hermes Tavern runtime."""

from __future__ import annotations

import json
from typing import Any

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.identity import session_key_from_event
from plugins.hermes_tavern.images import (
    DEFAULT_IMAGE_SETTINGS,
    IMAGE_PROVIDER_FAILURE_ERROR,
    IMAGE_PROVIDER_FAILURE_REPLY,
    IMAGE_SETTING_TYPES,
    apply_style_to_settings,
    available_image_providers,
    build_image_provider,
    compile_image_prompt,
    evaluate_image_safety,
    image_output_dir,
    mobile_image_preview,
    normalize_image_mode,
    normalize_image_safety,
    normalize_image_settings,
)
from plugins.hermes_tavern.runtime_utils import card_row_to_obj as _card_row_to_obj

def image_command(runtime, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session. Start one before generating images."

    action = command.args[0].lower() if command.args else "scene"
    if action in {"settings", "status"}:
        return runtime._image_settings(command, session)
    if action == "provider":
        return runtime._image_provider(command)
    if action == "safety":
        return runtime._image_safety(command, session)
    if action == "style":
        return runtime._image_style(command, session)
    if action == "history":
        return runtime._image_history(command, session)
    if action == "inspect":
        return runtime._image_inspect(session)
    if action == "retry":
        return runtime._image_retry(session)
    if action == "prompt":
        user_prompt = " ".join(command.args[1:]).strip()
        if not user_prompt:
            return "Usage: /rp image prompt <text>"
        return runtime._image_generate(session, event, mode="free", user_prompt=user_prompt, source="command")

    mode = normalize_image_mode(action)
    if mode not in {"scenario", "character", "face", "background", "last", "raw_last", "free"}:
        return "Usage: /rp image [scene|character|face|background|last|raw_last|prompt <text>|retry|inspect|settings]"
    extra = " ".join(command.args[1:]).strip()
    return runtime._image_generate(session, event, mode=mode, user_prompt=extra, source="command")

def image_settings(runtime, command: RPCommand, session: dict[str, Any]) -> str:
    settings = normalize_image_settings(runtime.store.get_image_settings(session["id"]))
    action = command.args[1].lower() if len(command.args) > 1 else "show"
    if action in {"show", "status"}:
        lines = [
            "Hermes Tavern image settings",
            f"provider: {runtime.image_provider.name}",
            f"model: {runtime.image_provider.model}",
            "modes: scene, character, face, background, last, raw_last, prompt\n"
            "commands: /rp image scene | /rp image prompt <text> | /rp image retry | /rp image inspect | /rp image history | /rp image provider | /rp image settings | /rp image style | /rp image safety\n"
        ]
        for key in ["width", "height", "steps", "cfg_scale", "sampler", "seed"]:
            lines.append(f"- {key}: {settings.get(key)}")
        lines.append(f"- style_prefix: {mobile_image_preview(str(settings.get('style_prefix') or ''), limit=100) or '(empty)'}")
        lines.append(f"- style_suffix: {mobile_image_preview(str(settings.get('style_suffix') or ''), limit=100) or '(empty)'}")
        lines.append(f"- negative_prompt: {mobile_image_preview(str(settings.get('negative_prompt') or ''), limit=120) or '(empty)'}")
        lines.append("set: /rp image settings set <key> <value>")
        lines.append("clear: /rp image settings clear <key|all>")
        lines.append("styles: /rp image style list")
        return "\n".join(lines)
    if action == "set":
        if len(command.args) < 4:
            return "Usage: /rp image settings set <width|height|steps|cfg_scale|sampler|seed|style_prefix|style_suffix|negative_prompt> <value>"
        key = command.args[2].lower().replace("-", "_")
        if key not in IMAGE_SETTING_TYPES:
            return "Unknown image setting. Use /rp image settings to inspect valid keys."
        raw_value = " ".join(command.args[3:]).strip()
        try:
            value = IMAGE_SETTING_TYPES[key](raw_value)
        except Exception:
            return f"Invalid value for {key}: {raw_value}"
        updated = dict(settings)
        updated[key] = value
        updated = normalize_image_settings(updated)
        runtime.store.set_image_settings(session["id"], updated)
        return f"Hermes Tavern image setting updated: {key} = {updated.get(key)}"
    if action == "clear":
        if len(command.args) < 3:
            return "Usage: /rp image settings clear <key|all>"
        key = command.args[2].lower().replace("-", "_")
        updated = dict(settings)
        if key == "all":
            updated = dict(DEFAULT_IMAGE_SETTINGS)
        elif key in DEFAULT_IMAGE_SETTINGS:
            updated[key] = DEFAULT_IMAGE_SETTINGS[key]
        else:
            return "Unknown image setting. Use /rp image settings to inspect valid keys."
        runtime.store.set_image_settings(session["id"], normalize_image_settings(updated))
        return f"Hermes Tavern image setting cleared: {key}"
    return "Usage: /rp image settings [set <key> <value>|clear <key|all>]"

def image_safety(runtime, command: RPCommand, session: dict[str, Any]) -> str:
    safety = normalize_image_safety(runtime.store.get_image_safety(session["id"]))
    action = command.args[1].lower() if len(command.args) > 1 else "inspect"
    if action in {"inspect", "show", "status"}:
        return "\n".join(
            [
                "Hermes Tavern image safety",
                f"mode: {safety['mode']}",
                "modes: safe | mature | explicit",
                "hard blocks: minor/underage sexualized image content, real-person sexualized/deepfake content, non-consensual sexualized content",
                "set: /rp image safety mode <safe|mature|explicit>",
            ]
        )
    if action == "mode":
        if len(command.args) < 3:
            return "Usage: /rp image safety mode <safe|mature|explicit>"
        mode = command.args[2].lower()
        if mode not in {"safe", "mature", "explicit"}:
            return "Unknown image safety mode. Use safe, mature, or explicit."
        safety["mode"] = mode
        runtime.store.set_image_safety(session["id"], safety)
        return f"Hermes Tavern image safety mode set: {mode}"
    if action == "clear":
        safety = normalize_image_safety({})
        runtime.store.set_image_safety(session["id"], safety)
        return "Hermes Tavern image safety reset to safe."
    return "Usage: /rp image safety [inspect|mode <safe|mature|explicit>|clear]"

def image_style(runtime, command: RPCommand, session: dict[str, Any]) -> str:
    action = command.args[1].lower() if len(command.args) > 1 else "list"
    if action == "list":
        styles = runtime.store.list_image_styles()
        if not styles:
            return "No image styles saved. Use /rp image style save <name> to create one."
        lines = [f"Hermes Tavern image styles ({len(styles)}):"]
        for s in styles:
            pos_preview = mobile_image_preview(s.get("positive_template") or "", limit=60) or "(empty)"
            lines.append(f"- {s['name']}: {pos_preview}")
        lines.append("use: /rp image style use <name> | inspect: /rp image style inspect <name>")
        return "\n".join(lines)
    if action == "save":
        if len(command.args) < 3:
            return "Usage: /rp image style save <name> [from-current] — add 'from-current' to snapshot current session settings"
        name = command.args[2].lower().replace(" ", "-")
        settings = normalize_image_settings(runtime.store.get_image_settings(session["id"]))
        positive = settings.get("style_prefix") or ""
        negative = settings.get("negative_prompt") or ""
        snap_settings = {k: settings[k] for k in ("width", "height", "steps", "cfg_scale", "sampler", "seed")}
        runtime.store.save_image_style(name, positive_template=positive, negative_template=negative, settings=snap_settings)
        return f"Hermes Tavern image style saved: {name}"
    if action == "use":
        if len(command.args) < 3:
            return "Usage: /rp image style use <name>"
        name = command.args[2].lower()
        style = runtime.store.get_image_style(name)
        if style is None:
            return f"Unknown image style: {name}. Use /rp image style list."
        current = normalize_image_settings(runtime.store.get_image_settings(session["id"]))
        merged = apply_style_to_settings(style, current)
        runtime.store.set_image_settings(session["id"], merged)
        lines = [
            f"Hermes Tavern image style applied: {name}",
            f"- positive: {mobile_image_preview(style.get('positive_template') or '', limit=80) or '(empty)'}",
            f"- negative: {mobile_image_preview(style.get('negative_template') or '', limit=80) or '(empty)'}",
        ]
        ss = style.get("settings") or {}
        params = [f"{k}={ss[k]}" for k in ("sampler", "steps", "cfg_scale", "width", "height") if k in ss]
        if params:
            lines.append(f"- params: {', '.join(params)}")
        return "\n".join(lines)
    if action == "inspect":
        if len(command.args) < 3:
            return "Usage: /rp image style inspect <name>"
        name = command.args[2].lower()
        style = runtime.store.get_image_style(name)
        if style is None:
            return f"Unknown image style: {name}. Use /rp image style list."
        lines = [
            f"Hermes Tavern image style: {style['name']}",
            f"positive_template: {style.get('positive_template') or '(empty)'}",
            f"negative_template: {style.get('negative_template') or '(empty)'}",
        ]
        ss = style.get("settings") or {}
        for k in ("width", "height", "steps", "cfg_scale", "sampler", "seed"):
            if k in ss:
                lines.append(f"- {k}: {ss[k]}")
        lines.append(f"created: {style.get('created_at', '-')}")
        return "\n".join(lines)
    if action == "delete":
        if len(command.args) < 3:
            return "Usage: /rp image style delete <name>"
        name = command.args[2].lower()
        ok = runtime.store.delete_image_style(name)
        if not ok:
            return f"Unknown image style: {name}. Use /rp image style list."
        return f"Hermes Tavern image style deleted: {name}"
    return "Usage: /rp image style [list|save <name> [from-current]|use <name>|inspect <name>|delete <name>]"

def image_provider(runtime, command: RPCommand) -> str:
    action = command.args[1].lower() if len(command.args) > 1 else "status"
    if action in {"status", "current"}:
        return (
            "Hermes Tavern image provider\n"
            f"current: {runtime.image_provider.name}\n"
            f"model: {runtime.image_provider.model}\n"
            "use: /rp image provider use <mock|chatgpt-image2|openai|comfyui> [model]\n"
            "list: /rp image provider list"
        )
    if action == "list":
        lines = ["Hermes Tavern image providers"]
        for name, description in available_image_providers().items():
            marker = "*" if name == runtime.image_provider.name else "-"
            lines.append(f"{marker} {name}: {description}")
        lines.append("Use: /rp image provider use <name> [model]")
        return "\n".join(lines)
    if action == "use":
        if len(command.args) < 3:
            return "Usage: /rp image provider use <mock|chatgpt-image2|openai|comfyui> [model]"
        name = command.args[2]
        model = command.args[3] if len(command.args) > 3 else None
        try:
            runtime.image_provider = build_image_provider(name, model=model)
        except Exception as exc:
            return f"Could not select image provider: {exc}"
        note = ""
        if runtime.image_provider.name == "chatgpt-image2":
            note = "\nnote: adapter selected, but live Image2 HTTP calls are not wired yet. Generation will fail safely until configured."
        return (
            "Hermes Tavern image provider selected.\n"
            f"provider: {runtime.image_provider.name}\n"
            f"model: {runtime.image_provider.model}{note}"
        )
    return "Usage: /rp image provider [list|status|use <name> [model]]"

def image_history(runtime, command: RPCommand, session: dict[str, Any]) -> str:
    limit = 5
    page = 1
    if len(command.args) > 1:
        try:
            limit = max(1, min(20, int(command.args[1])))
        except ValueError:
            return "Usage: /rp image history [limit] [page]"
    if len(command.args) > 2:
        try:
            page = max(1, int(command.args[2]))
        except ValueError:
            return "Usage: /rp image history [limit] [page]"
    offset = (page - 1) * limit
    total = runtime.store.count_image_jobs(session["id"])
    rows = runtime.store.list_image_jobs(session["id"], limit=limit, offset=offset)
    if not rows:
        return "No Hermes Tavern image jobs for this session."
    total_pages = max(1, (total + limit - 1) // limit)
    lines = [f"Hermes Tavern image history page {page}/{total_pages} ({total} total)"]
    for idx, row in enumerate(rows, start=offset + 1):
        prompt = row.get("prompt_snapshot") or row.get("prompt") or ""
        asset = str(row.get("asset_id") or "")[:8] or "none"
        lines.append(
            f"{idx}. {row.get('mode')} {row.get('status')} {row.get('provider')}/{row.get('model')} "
            f"asset={asset} prompt={mobile_image_preview(prompt, limit=90)}"
        )
    if page < total_pages:
        lines.append(f"next: /rp image history {limit} {page + 1}")
    if page > 1:
        lines.append(f"prev: /rp image history {limit} {page - 1}")
    return "\n".join(lines)

def image_generate(
    runtime,
    session: dict[str, Any],
    event: Any,
    *,
    mode: str,
    user_prompt: str = "",
    negative_prompt: str = "",
    source: str = "command",
) -> str:
    card_row = runtime.store.get_card(session.get("card_id") or "") if session.get("card_id") else None
    if card_row is None:
        return "No card is bound to this session; start or bind a card before image generation."
    card = _card_row_to_obj(card_row)
    history = runtime.store.get_recent_messages(session["id"], limit=20)
    summary = runtime.store.get_session_summary(session.get("session_key") or "")
    summary_text = summary["summary"] if summary and summary.get("summary") else ""
    settings = normalize_image_settings(runtime.store.get_image_settings(session["id"]))
    prompt = compile_image_prompt(
        mode=mode,
        card=card,
        session=session,
        history=history,
        memory_summary=summary_text,
        user_prompt=user_prompt,
        negative_prompt=negative_prompt,
        source=source,
        settings=settings,
    )
    safety = normalize_image_safety(runtime.store.get_image_safety(session["id"]))
    safety_result = evaluate_image_safety(
        prompt=prompt.prompt,
        negative_prompt=prompt.negative_prompt,
        card=card,
        safety=safety,
    )
    prompt_metadata = dict(prompt.metadata or {})
    prompt_metadata["safety"] = {
        "allowed": safety_result.allowed,
        "mode": safety_result.mode,
        "risk_level": safety_result.risk_level,
        "reasons": safety_result.reasons,
        "flags": safety_result.flags,
    }
    job_id = runtime.store.create_image_job(
        session_id=session["id"],
        provider=runtime.image_provider.name,
        model=runtime.image_provider.model,
        mode=prompt.mode,
        prompt=prompt.prompt,
        negative_prompt=prompt.negative_prompt,
        metadata=prompt_metadata,
    )
    if not safety_result.allowed:
        reason = "; ".join(safety_result.reasons) or "image safety guard blocked the request"
        runtime.store.fail_image_job(job_id, reason, metadata=prompt_metadata)
        flags = ", ".join(k for k, v in safety_result.flags.items() if v) or "none"
        return (
            "Hermes Tavern image blocked by safety guard.\n"
            f"mode: {safety_result.mode}\n"
            f"risk: {safety_result.risk_level}\n"
            f"flags: {flags}\n"
            f"reason: {reason}\n"
            "adjust: /rp image safety mode <safe|mature|explicit>"
        )
    try:
        generated = runtime.image_provider.generate(prompt, output_dir=image_output_dir())
    except Exception:
        runtime.store.fail_image_job(job_id, IMAGE_PROVIDER_FAILURE_ERROR, metadata=prompt_metadata)
        return IMAGE_PROVIDER_FAILURE_REPLY

    asset_id = runtime.store.complete_image_job(
        job_id=job_id,
        session_id=session["id"],
        file_path=generated.file_path,
        mime_type=generated.mime_type,
        width=generated.width,
        height=generated.height,
        prompt_snapshot=prompt.prompt,
        metadata=generated.metadata or {},
    )
    preview = mobile_image_preview(prompt.prompt)
    neg = f"\nnegative: {mobile_image_preview(prompt.negative_prompt, limit=120)}" if prompt.negative_prompt else ""
    return (
        "Hermes Tavern image generated.\n"
        f"mode: {prompt.mode}\n"
        f"provider: {generated.provider}/{generated.model}\n"
        f"asset: {asset_id[:8]}\n"
        f"prompt: {preview}{neg}\n"
        f"MEDIA:{generated.file_path}"
    )

def image_retry(runtime, session: dict[str, Any]) -> str:
    last = runtime.store.get_last_image_job(session["id"])
    if last is None:
        return "No previous Hermes Tavern image job to retry."
    return runtime._image_generate(
        session,
        event=None,
        mode=last.get("mode") or "free",
        user_prompt=last.get("prompt") or "",
        negative_prompt=last.get("negative_prompt") or "",
        source="retry",
    )

def image_inspect(runtime, session: dict[str, Any]) -> str:
    last = runtime.store.get_last_image_job(session["id"])
    if last is None:
        return "No Hermes Tavern image jobs for this session."
    prompt = last.get("prompt_snapshot") or last.get("prompt") or ""
    file_path = last.get("file_path") or "none"
    lines = [
        "Hermes Tavern image inspect",
        f"job: {str(last.get('id') or '')[:8]}",
        f"asset: {str(last.get('asset_id') or '')[:8] or 'none'}",
        f"status: {last.get('status')}",
        f"mode: {last.get('mode')}",
        f"provider: {last.get('provider')}/{last.get('model')}",
        f"size: {last.get('width') or '?'}x{last.get('height') or '?'}",
        f"file: {file_path}",
        f"prompt: {mobile_image_preview(prompt, limit=300)}",
    ]
    if last.get("negative_prompt"):
        lines.append(f"negative: {mobile_image_preview(last['negative_prompt'], limit=160)}")
    try:
        metadata = json.loads(last.get("metadata_json") or "{}")
    except Exception:
        metadata = {}
    safety = metadata.get("safety") if isinstance(metadata, dict) else None
    if isinstance(safety, dict):
        lines.append(
            f"safety: {safety.get('mode', '?')} {safety.get('risk_level', '?')} "
            f"allowed={safety.get('allowed', '?')}"
        )
        if safety.get("reasons"):
            lines.append(f"safety_reason: {mobile_image_preview('; '.join(safety['reasons']), limit=180)}")
    return "\n".join(lines)
