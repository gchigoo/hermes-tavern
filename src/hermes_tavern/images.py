"""ST-style image generation helpers for Hermes Tavern.

This module mirrors SillyTavern's image-generation layering without copying its
frontend-specific implementation:

1. generation mode / initiator selection (scene, character, face, last, free)
2. prompt compilation from character card + scenario + memory + recent turns
3. provider adapter dispatch
4. persisted job/asset metadata for retry/inspect/export

The default provider is deterministic and local so tests and mobile command UX
work without network calls. Real providers (OpenAI/ChatGPT Image2, ComfyUI,
FAL, etc.) can implement the same adapter contract later.
"""

from __future__ import annotations

import base64
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from hermes_constants import get_hermes_home
from plugins.hermes_tavern.utils import estimate_tokens


# SillyTavern-inspired generation modes, mapped to mobile-safe commands.
IMAGE_MODE_ALIASES = {
    "prompt": "free",
    "free": "free",
    "scene": "scenario",
    "scenario": "scenario",
    "character": "character",
    "char": "character",
    "you": "character",
    "face": "face",
    "portrait": "face",
    "last": "last",
    "now": "last",
    "raw_last": "raw_last",
    "background": "background",
    "bg": "background",
}

MODE_LABELS = {
    "free": "Free Prompt",
    "scenario": "Scenario / Whole Story",
    "character": "Character",
    "face": "Portrait / Face",
    "last": "Last Message",
    "raw_last": "Raw Last Message",
    "background": "Background",
}


@dataclass(frozen=True)
class ImagePrompt:
    mode: str
    prompt: str
    negative_prompt: str = ""
    source: str = "command"
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class GeneratedImage:
    provider: str
    model: str
    file_path: str
    mime_type: str = "image/png"
    width: int = 1
    height: int = 1
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ImageSafetyResult:
    allowed: bool
    mode: str
    risk_level: str
    reasons: list[str]
    flags: dict[str, bool]


DEFAULT_IMAGE_SETTINGS: dict[str, Any] = {
    "width": 1024,
    "height": 1024,
    "steps": 28,
    "cfg_scale": 7.0,
    "sampler": "euler_a",
    "seed": -1,
    "style_prefix": "",
    "style_suffix": "",
    "negative_prompt": "",
}

IMAGE_SETTING_TYPES = {
    "width": int,
    "height": int,
    "steps": int,
    "cfg_scale": float,
    "sampler": str,
    "seed": int,
    "style_prefix": str,
    "style_suffix": str,
    "negative_prompt": str,
}

SAFETY_MODES = {"safe", "mature", "explicit"}
DEFAULT_IMAGE_SAFETY: dict[str, Any] = {"mode": "safe"}
IMAGE_PROVIDER_FAILURE_ERROR = "image provider error (details hidden)"
IMAGE_PROVIDER_FAILURE_REPLY = (
    "Hermes Tavern image generation failed.\n"
    "error: image provider error (details hidden)\n"
    "retry: /rp image retry\n"
    "status: /rp image inspect"
)

_MINOR_TERMS = {
    "minor", "underage", "child", "kid", "teen", "teenager", "schoolgirl", "schoolboy",
    "loli", "shota", "幼女", "未成年", "儿童", "小孩", "萝莉", "正太", "学生妹",
}
_EXPLICIT_TERMS = {
    "sex", "sexual", "nude", "naked", "porn", "explicit", "erotic", "xxx", "nsfw",
    "genitals", "breasts", "nipples", "vagina", "penis", "cum", "orgasm",
    "裸体", "色情", "性爱", "裸露", "露点", "乳头", "性器", "黄片", "成人内容",
}
_SUGGESTIVE_TERMS = {
    "sensual", "seductive", "lingerie", "bikini", "cleavage", "suggestive", "pinup",
    "性感", "诱惑", "内衣", "比基尼", "暧昧",
}
_REAL_PERSON_TERMS = {
    "real person", "celebrity", "deepfake", "politician", "actor", "actress", "singer",
    "真人", "名人", "明星", "深伪", "换脸", "公众人物",
}
_NONCONSENT_TERMS = {
    "rape", "raped", "non-consensual", "nonconsensual", "forced", "coerced", "unwilling",
    "drugged", "asleep", "unconscious", "抵抗", "强迫", "强奸", "迷奸", "昏迷", "非自愿",
}


# ST-inspired default style presets seeded into image_styles on first migration.
SEED_IMAGE_STYLES: list[dict[str, Any]] = [
    {
        "name": "anime",
        "positive_template": "{{prompt}}, anime style, high detail",
        "negative_template": "low quality, blurry, extra fingers, watermark",
        "settings": {"sampler": "euler_a", "steps": 28, "cfg_scale": 7},
    },
    {
        "name": "realistic",
        "positive_template": "{{prompt}}, photorealistic, 8k, cinematic lighting",
        "negative_template": "cartoon, anime, 3d render, low quality",
        "settings": {"sampler": "dpmpp_2m", "steps": 32, "cfg_scale": 7.5},
    },
    {
        "name": "illustration",
        "positive_template": "{{prompt}}, digital illustration, sharp focus, vibrant colors",
        "negative_template": "photo, realistic, low quality, jpeg artifacts",
        "settings": {"sampler": "dpmpp_2m", "steps": 20, "cfg_scale": 7},
    },
    {
        "name": "painting",
        "positive_template": "{{prompt}}, oil painting, masterpiece, fine art style",
        "negative_template": "digital art, anime, photo, low quality",
        "settings": {"sampler": "euler_a", "steps": 35, "cfg_scale": 6.5},
    },
    {
        "name": "manga",
        "positive_template": "{{prompt}}, manga style, monochrome, crosshatching",
        "negative_template": "color, 3d render, photo, low quality",
        "settings": {"sampler": "euler_a", "steps": 24, "cfg_scale": 7},
    },
    {
        "name": "pixel-art",
        "positive_template": "{{prompt}}, pixel art, 16-bit, retro game style",
        "negative_template": "smooth, realistic, high resolution, blurry",
        "settings": {"sampler": "euler_a", "steps": 20, "cfg_scale": 7, "width": 512, "height": 512},
    },
]


def seed_image_styles(store: Any) -> None:
    """Seed ST-inspired default styles into an empty TavernStore."""
    existing = store.list_image_styles()
    if existing:
        return
    for style in SEED_IMAGE_STYLES:
        store.save_image_style(
            name=style["name"],
            positive_template=style["positive_template"],
            negative_template=style["negative_template"],
            settings=style.get("settings", {}),
        )


def apply_style_to_settings(
    style: dict[str, Any], current_settings: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Merge a style preset into current session image settings.

    The style's generation params (sampler, steps, cfg_scale, width, height, seed)
    overwrite current session settings. The positive/negative templates replace
    style_prefix/style_suffix rather than being appended.
    """
    merged = dict(current_settings or DEFAULT_IMAGE_SETTINGS)
    style_settings = style.get("settings") or {}
    for key in ("sampler", "steps", "cfg_scale", "width", "height", "seed"):
        if key in style_settings:
            merged[key] = style_settings[key]
    pos = (style.get("positive_template") or "").strip()
    neg = (style.get("negative_template") or "").strip()
    if pos:
        merged["style_prefix"] = pos
    if neg:
        merged["negative_prompt"] = neg
    return normalize_image_settings(merged)


def expand_image_template_macros(
    template: str,
    *,
    prompt: str = "",
    char_name: str = "",
    user: str = "user",
    scenario: str = "",
    memory: str = "",
    mode: str = "",
    seed: int | str | None = None,
) -> str:
    """Expand a small ST-inspired macro subset for image prompt templates.

    Supported:
    - {{prompt}} / {{char}} / {{user}} / {{scenario}} / {{memory}} / {{mode}}
    - {{random:a|b|c}} with deterministic choice when seed is provided
    Unknown macros are removed so mobile output never leaks raw template syntax.
    """
    text = template or ""

    def pick_random(match: re.Match[str]) -> str:
        options = [x.strip() for x in match.group(1).split("|") if x.strip()]
        if not options:
            return ""
        if seed not in (None, "", -1, "-1"):
            digest = hashlib.sha256(str(seed).encode("utf-8")).hexdigest()
            return options[int(digest[:8], 16) % len(options)]
        return options[0]

    text = re.sub(r"\{\{\s*random\s*:\s*(.*?)\s*\}\}", pick_random, text, flags=re.I)
    replacements = {
        "prompt": prompt,
        "char": char_name,
        "character": char_name,
        "user": user,
        "scenario": scenario,
        "memory": memory,
        "summary": memory,
        "mode": mode,
    }

    def replace_macro(match: re.Match[str]) -> str:
        key = match.group(1).strip().lower()
        return str(replacements.get(key, ""))

    text = re.sub(r"\{\{\s*([a-zA-Z_][\w-]*)\s*\}\}", replace_macro, text)
    return _dedupe_commas(text)


def _dedupe_commas(text: str) -> str:
    parts = [p.strip() for p in (text or "").split(",") if p.strip()]
    seen: set[str] = set()
    deduped: list[str] = []
    for p in parts:
        if p.lower() not in seen:
            seen.add(p.lower())
            deduped.append(p)
    return ", ".join(deduped)


def interpolate_style_prompt(template: str, user_prompt: str = "", char_name: str = "") -> str:
    """Backward-compatible helper for style template previews."""
    return expand_image_template_macros(template, prompt=user_prompt, char_name=char_name)


def normalize_image_settings(settings: dict[str, Any] | None = None) -> dict[str, Any]:
    merged = dict(DEFAULT_IMAGE_SETTINGS)
    if settings:
        for key, value in settings.items():
            if key in IMAGE_SETTING_TYPES and value not in (None, ""):
                try:
                    merged[key] = IMAGE_SETTING_TYPES[key](value)
                except Exception:
                    merged[key] = value
    merged["width"] = max(64, min(4096, int(merged["width"])))
    merged["height"] = max(64, min(4096, int(merged["height"])))
    merged["steps"] = max(1, min(150, int(merged["steps"])))
    merged["cfg_scale"] = max(0.0, min(30.0, float(merged["cfg_scale"])))
    return merged


def normalize_image_safety(safety: dict[str, Any] | None = None) -> dict[str, Any]:
    merged = dict(DEFAULT_IMAGE_SAFETY)
    if safety:
        mode = str(safety.get("mode") or merged["mode"]).strip().lower()
        if mode in SAFETY_MODES:
            merged["mode"] = mode
    return merged


def _contains_any(text: str, terms: set[str]) -> bool:
    low = text.lower()
    return any(term in low for term in terms)


def _card_safety_text(card: Any) -> str:
    chunks = [
        getattr(card, "name", ""),
        getattr(card, "description", ""),
        getattr(card, "personality", ""),
        getattr(card, "scenario", ""),
    ]
    extensions = getattr(card, "extensions", {}) or {}
    if isinstance(extensions, dict):
        chunks.append(str(extensions))
    return "\n".join(str(x) for x in chunks if x)


def evaluate_image_safety(
    *,
    prompt: str,
    negative_prompt: str = "",
    card: Any = None,
    safety: dict[str, Any] | None = None,
) -> ImageSafetyResult:
    """Heuristic image safety gate for Tavern image generation.

    Text RP may allow broader fictional content, but image generation gets a
    stricter gate.  The guard is intentionally deterministic and provider-agnostic
    so card/preset jailbreak text cannot bypass it.
    """
    cfg = normalize_image_safety(safety)
    mode = cfg["mode"]
    card_text = _card_safety_text(card) if card is not None else ""
    text = "\n".join([prompt or "", negative_prompt or "", card_text])
    prompt_text = "\n".join([prompt or "", card_text])
    has_minor = _contains_any(text, _MINOR_TERMS) or bool(re.search(r"\b(1[0-7])\s*(yo|y/o|years? old)\b", text, re.I))
    has_explicit = _contains_any(prompt_text, _EXPLICIT_TERMS)
    has_suggestive = _contains_any(prompt_text, _SUGGESTIVE_TERMS)
    has_real_person = _contains_any(prompt_text, _REAL_PERSON_TERMS)
    has_nonconsent = _contains_any(prompt_text, _NONCONSENT_TERMS)
    flags = {
        "minor": has_minor,
        "explicit": has_explicit,
        "suggestive": has_suggestive,
        "real_person": has_real_person,
        "nonconsent": has_nonconsent,
    }
    reasons: list[str] = []
    if has_minor and (has_explicit or has_suggestive):
        reasons.append("minor-or-underage sexualized image content is blocked")
    if has_real_person and (has_explicit or has_suggestive):
        reasons.append("real-person sexualized or deepfake image content is blocked")
    if has_nonconsent and (has_explicit or has_suggestive):
        reasons.append("non-consensual sexualized image content is blocked")
    if mode == "safe" and (has_explicit or has_suggestive):
        reasons.append("safe image mode blocks sexualized or suggestive image prompts")
    if mode == "mature" and has_explicit:
        reasons.append("mature image mode blocks explicit sexual image prompts")
    risk = "high" if reasons else ("medium" if (has_explicit or has_suggestive or has_minor or has_real_person or has_nonconsent) else "low")
    return ImageSafetyResult(allowed=not reasons, mode=mode, risk_level=risk, reasons=reasons, flags=flags)


class TavernImageProvider(Protocol):
    name: str
    model: str

    def generate(self, prompt: ImagePrompt, *, output_dir: Path) -> GeneratedImage:
        """Generate an image and return a local file path."""


# 1x1 PNG, deterministic placeholder for tests/mock provider.
_PLACEHOLDER_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


class MockImageProvider:
    """Deterministic local provider used until a real image backend is configured."""

    name = "mock"
    model = "placeholder-png"

    def generate(self, prompt: ImagePrompt, *, output_dir: Path) -> GeneratedImage:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"tavern-image-{uuid4().hex[:12]}.png"
        path.write_bytes(_PLACEHOLDER_PNG)
        settings = normalize_image_settings((prompt.metadata or {}).get("settings") if prompt.metadata else None)
        return GeneratedImage(
            provider=self.name,
            model=self.model,
            file_path=str(path),
            width=int(settings.get("width") or 1),
            height=int(settings.get("height") or 1),
            metadata={
                "mock": True,
                "mode": prompt.mode,
                "requested_width": int(settings.get("width") or 1),
                "requested_height": int(settings.get("height") or 1),
                "prompt_chars": len(prompt.prompt),
                "prompt_tokens_estimate": estimate_tokens(prompt.prompt),
            },
        )


class ChatGPTImage2Provider:
    """Placeholder adapter surface for a future ChatGPT/OpenAI Image2 backend.

    Keep this as an adapter, not as core runtime logic.  A production
    implementation should prefer official OpenAI image APIs or a stable
    OpenAI-compatible endpoint; reverse-engineered web sessions should remain
    experimental and be configured explicitly by the user.
    """

    name = "chatgpt-image2"

    def __init__(self, *, model: str = "gpt-image-1", endpoint: str = "") -> None:
        self.model = model
        self.endpoint = endpoint

    def generate(self, prompt: ImagePrompt, *, output_dir: Path) -> GeneratedImage:
        raise RuntimeError(
            "chatgpt-image2 provider is selected but not configured for live image calls yet; "
            "switch to /rp image provider use mock or wire an OpenAI/Image2 adapter"
        )


class ComfyUIProvider:
    """Live ComfyUI adapter for Tavern image generation.

    Talks to a local or remote ComfyUI server via its REST API:
    1. POST /prompt with a standard text-to-image workflow
    2. Poll GET /history/{prompt_id} until the job completes
    3. Download the output image via /view

    The workflow uses CheckpointLoaderSimple → CLIPTextEncode ×2 →
    EmptyLatentImage → KSampler → VAEDecode → SaveImage.
    """

    name = "comfyui"

    # Map A1111 / ST-style sampler names to ComfyUI native sampler names.
    _SAMPLER_MAP: dict[str, str] = {
        "euler_a": "euler_ancestral",
        "euler": "euler",
        "dpm_2": "dpm_2",
        "dpm_2_a": "dpm_2_ancestral",
        "dpmpp_2m": "dpmpp_2m",
        "dpmpp_2m_sde": "dpmpp_2m_sde",
        "dpmpp_sde": "dpmpp_sde",
        "ddim": "ddim",
        "lcm": "lcm",
        "uni_pc": "uni_pc",
        "uni_pc_bh2": "uni_pc_bh2",
        "heun": "heun",
        "lms": "lms",
        "dpm_fast": "dpm_fast",
        "dpm_adaptive": "dpm_adaptive",
        "ddpm": "ddpm",
        "ipndm": "ipndm",
        "ipndm_v": "ipndm_v",
        "deis": "deis",
    }

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8188",
        model: str = "",
        timeout: int = 300,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._checkpoint = model
        self.timeout = max(30, timeout)

    def generate(self, prompt: ImagePrompt, *, output_dir: Path) -> GeneratedImage:
        import json as _json
        import time as _time
        import urllib.error
        import urllib.parse
        import urllib.request

        settings = normalize_image_settings((prompt.metadata or {}).get("settings") if prompt.metadata else None)
        width = int(settings.get("width") or 1024)
        height = int(settings.get("height") or 1024)
        steps = int(settings.get("steps") or 20)
        cfg = float(settings.get("cfg_scale") or 7.0)
        sampler = str(settings.get("sampler") or "euler")
        sampler = self._SAMPLER_MAP.get(sampler, sampler)  # map A1111 → ComfyUI names
        seed = int(settings.get("seed") or -1)

        # ── 1. Resolve checkpoint ──────────────────────────────────
        checkpoint = self._checkpoint
        if not checkpoint:
            try:
                checkpoint = self._first_checkpoint_name()
            except Exception:
                checkpoint = ""
        if not checkpoint:
            raise RuntimeError(
                "comfyui provider: no checkpoint configured and none found on the server. "
                "Set one with /rp image provider use comfyui <checkpoint-name>"
            )

        # ── 2. Build workflow ──────────────────────────────────────
        workflow = {
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": checkpoint},
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": width, "height": height, "batch_size": 1},
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt.prompt, "clip": ["4", 1]},
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt.negative_prompt or "", "clip": ["4", 1]},
            },
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": seed if seed >= 0 else _time.time_ns() & 0xFFFFFFFF,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": sampler,
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {"filename_prefix": "hermes-tavern", "images": ["8", 0]},
            },
        }

        # ── 3. Queue prompt ────────────────────────────────────────
        payload = _json.dumps({"prompt": workflow}).encode("utf-8")
        try:
            req = urllib.request.Request(
                f"{self.base_url}/prompt",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = _json.loads(resp.read().decode())
        except urllib.error.URLError as exc:
            msg = f"comfyui provider unavailable at {self.base_url}: {exc.reason}"
            raise ConnectionError(msg) from exc
        except Exception as exc:
            raise RuntimeError(f"comfyui provider queue failed: {exc}") from exc

        prompt_id = body.get("prompt_id")
        if not prompt_id:
            raise RuntimeError(f"comfyui provider: no prompt_id in response: {body}")

        # ── 4. Poll for completion ─────────────────────────────────
        deadline = _time.monotonic() + self.timeout
        while True:
            if _time.monotonic() > deadline:
                raise TimeoutError(
                    f"comfyui provider timed out after {self.timeout}s waiting for {prompt_id}"
                )
            try:
                req = urllib.request.Request(f"{self.base_url}/history/{prompt_id}")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    history = _json.loads(resp.read().decode())
            except Exception as exc:
                raise RuntimeError(f"comfyui provider poll failed: {exc}") from exc

            entry = history.get(prompt_id)
            if entry is not None:
                break
            _time.sleep(2)

        # ── 5. Extract output filename ─────────────────────────────
        outputs = entry.get("outputs") or {}
        node_output = outputs.get("9") or {}
        images = node_output.get("images") or []
        if not images:
            raise RuntimeError(f"comfyui provider: no output images in job {prompt_id}")

        image_info = images[0]
        filename = image_info["filename"]
        subfolder = image_info.get("subfolder") or ""
        img_type = image_info.get("type") or "output"

        # ── 6. Download image ──────────────────────────────────────
        view_url = (
            f"{self.base_url}/view"
            f"?filename={urllib.parse.quote(filename)}"
            f"&subfolder={urllib.parse.quote(subfolder)}"
            f"&type={urllib.parse.quote(img_type)}"
        )
        try:
            with urllib.request.urlopen(view_url, timeout=30) as resp:
                data = resp.read()
        except Exception as exc:
            raise RuntimeError(f"comfyui provider download failed: {exc}") from exc

        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / f"tavern-comfyui-{prompt_id[:8]}.png"
        out_path.write_bytes(data)

        return GeneratedImage(
            provider=self.name,
            model=checkpoint,
            file_path=str(out_path),
            mime_type="image/png",
            width=width,
            height=height,
            metadata={
                "comfyui_prompt_id": prompt_id,
                "checkpoint": checkpoint,
                "sampler": sampler,
                "steps": steps,
                "cfg_scale": cfg,
                "seed": seed,
                "prompt_chars": len(prompt.prompt),
            },
        )

    def _first_checkpoint_name(self) -> str:
        import json as _json
        import urllib.error
        import urllib.request

        try:
            req = urllib.request.Request(f"{self.base_url}/object_info")
            with urllib.request.urlopen(req, timeout=10) as resp:
                info = _json.loads(resp.read().decode())
        except Exception:
            return ""
        node = info.get("CheckpointLoaderSimple")
        if not node:
            return ""
        required = node.get("input", {}).get("required", {})
        raw = required.get("ckpt_name")
        # ComfyUI returns [[name1, name2, ...], {tooltip: ...}]
        if isinstance(raw, list) and raw:
            inner = raw[0]
            if isinstance(inner, list) and inner:
                return str(inner[0])
        return ""


def available_image_providers() -> dict[str, str]:
    """Return mobile-safe provider descriptions."""
    return {
        "mock": "deterministic local placeholder PNG; safe for tests and command UX",
        "chatgpt-image2": "experimental adapter slot for ChatGPT/OpenAI Image2-style backends",
        "openai": "alias reserved for official OpenAI Images API adapter",
        "comfyui": "local/remote ComfyUI adapter — /rp image provider use comfyui [checkpoint-name]",
    }


def build_image_provider(name: str, *, model: str | None = None, endpoint: str = "") -> TavernImageProvider:
    """Build a provider adapter from a user-facing name.

    Reserved real providers deliberately return placeholder adapters until their
    live HTTP implementations are added. Keeping them behind this factory lets
    runtime/provider commands stay stable while avoiding hard-coded API calls.
    """
    key = (name or "mock").strip().lower().replace("_", "-")
    if key in {"mock", "placeholder", "local"}:
        provider = MockImageProvider()
        if model:
            provider.model = model
        return provider
    if key in {"chatgpt", "chatgpt-image", "chatgpt-image2", "image2", "openai"}:
        return ChatGPTImage2Provider(model=model or "gpt-image-1", endpoint=endpoint)
    if key == "comfyui":
        return ComfyUIProvider(base_url=endpoint or "http://127.0.0.1:8188", model=model or "")
    raise ValueError(f"unknown image provider: {name}")


def image_output_dir() -> Path:
    return get_hermes_home() / "hermes-agent" / "exports" / "tavern-images"


def normalize_image_mode(value: str | None) -> str:
    key = (value or "scene").strip().lower().replace("-", "_")
    return IMAGE_MODE_ALIASES.get(key, key)


def _compact(text: str, *, limit: int = 500) -> str:
    compact = " ".join((text or "").split())
    if len(compact) > limit:
        return compact[: limit - 1].rstrip() + "…"
    return compact


def _card_image_prefix(card: Any) -> tuple[str, str]:
    """Return ST-compatible per-character positive/negative prompt fields."""
    extensions = getattr(card, "extensions", {}) or {}
    shared = extensions.get("sd_character_prompt") if isinstance(extensions, dict) else None
    if isinstance(shared, dict):
        return str(shared.get("positive") or ""), str(shared.get("negative") or "")
    return "", ""


def _last_message(history: list[dict[str, Any]], *, raw: bool = False) -> str:
    for row in reversed(history):
        text = (row.get("content") or "").strip()
        if text:
            return text if raw else _compact(text, limit=350)
    return ""


def compile_image_prompt(
    *,
    mode: str,
    card: Any,
    session: dict[str, Any],
    history: list[dict[str, Any]],
    memory_summary: str = "",
    user_prompt: str = "",
    negative_prompt: str = "",
    source: str = "command",
    settings: dict[str, Any] | None = None,
) -> ImagePrompt:
    """Compile an ST-style image prompt from Tavern context.

    Mode mapping follows ST's mental model:
    - free: user prompt, optionally with {{charPrefix}}/leading "char" expansion
    - character: visual character description
    - face: portrait-oriented character prompt
    - scenario: character + scenario + recent chat + memory
    - last/raw_last: last chat message
    - background: scenario/environment only
    """
    mode = normalize_image_mode(mode)
    settings = normalize_image_settings(settings)
    char_name = getattr(card, "name", "") or session.get("card_name") or "character"
    char_prefix, char_negative = _card_image_prefix(card)
    negative = ", ".join(
        x for x in [settings.get("negative_prompt", "").strip(), negative_prompt.strip(), char_negative.strip()] if x
    )

    description = _compact(getattr(card, "description", ""), limit=650)
    personality = _compact(getattr(card, "personality", ""), limit=300)
    scenario = _compact(getattr(card, "scenario", ""), limit=650)
    recent = " | ".join(
        f"{m.get('role')}: {_compact(m.get('content', ''), limit=180)}"
        for m in history[-6:]
        if (m.get("content") or "").strip()
    )
    summary = _compact(memory_summary, limit=500)

    if mode == "free":
        prompt = user_prompt.strip()
        if prompt.lower().startswith("char ") or "{{charPrefix}}" in prompt:
            prompt = prompt.replace("{{charPrefix}}", char_prefix).strip()
            if prompt.lower().startswith("char "):
                prompt = (char_prefix + ", " + prompt[5:].strip()).strip(" ,")
        elif char_prefix:
            prompt = f"{char_prefix}, {prompt}" if prompt else char_prefix
    elif mode == "character":
        parts = [char_prefix, f"{char_name}, full body character illustration", description, personality]
        prompt = ", ".join(p for p in parts if p)
    elif mode == "face":
        parts = [char_prefix, f"portrait of {char_name}, face focus", description]
        prompt = ", ".join(p for p in parts if p)
    elif mode == "background":
        parts = ["background/environment concept art", scenario, summary]
        prompt = ", ".join(p for p in parts if p)
    elif mode == "last":
        prompt = _last_message(history) or user_prompt.strip()
    elif mode == "raw_last":
        prompt = _last_message(history, raw=True) or user_prompt.strip()
    else:  # scenario / scene
        parts = [
            char_prefix,
            f"cinematic scene featuring {char_name}",
            description,
            f"Scenario: {scenario}" if scenario else "",
            f"Memory: {summary}" if summary else "",
            f"Recent chat: {recent}" if recent else "",
            user_prompt.strip(),
        ]
        prompt = ", ".join(p for p in parts if p)

    if not prompt:
        prompt = f"cinematic roleplay scene featuring {char_name}"

    prefix = str(settings.get("style_prefix") or "").strip()
    suffix = str(settings.get("style_suffix") or "").strip()
    template_context = {
        "char_name": char_name,
        "user": str(session.get("user_name") or "user"),
        "scenario": scenario,
        "memory": summary,
        "mode": mode,
        "seed": settings.get("seed"),
    }
    if prefix:
        expanded = expand_image_template_macros(prefix, prompt=prompt, **template_context)
        prompt = expanded if "{{prompt" in prefix.lower() else ", ".join(x for x in [expanded, prompt] if x)
    if suffix:
        expanded = expand_image_template_macros(suffix, prompt=prompt, **template_context)
        prompt = expanded if "{{prompt" in suffix.lower() else ", ".join(x for x in [prompt, expanded] if x)
    if negative:
        negative = expand_image_template_macros(negative, prompt=prompt, **template_context)
    # Imported ST cards/presets often contain macros in descriptions/scenarios.
    # Do a final cleanup pass so no raw {{...}} leaks into provider prompts.
    prompt = expand_image_template_macros(prompt, prompt="", **template_context)
    if negative:
        negative = expand_image_template_macros(negative, prompt="", **template_context)

    metadata = {
        "mode_label": MODE_LABELS.get(mode, mode),
        "char_name": char_name,
        "history_count": len(history),
        "has_card_prefix": bool(char_prefix),
        "has_memory_summary": bool(summary),
        "settings": settings,
    }
    return ImagePrompt(mode=mode, prompt=prompt, negative_prompt=negative, source=source, metadata=metadata)


def mobile_image_preview(prompt: str, *, limit: int = 220) -> str:
    return _compact(prompt, limit=limit)
