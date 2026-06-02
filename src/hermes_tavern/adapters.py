"""Model adapters for Hermes Tavern."""

from __future__ import annotations

from typing import Any, Callable, Protocol

from hermes_tavern.provider_bridge import sanitize_provider_payload, validate_provider_base_url


def _message_content(response: Any) -> str:
    choices = getattr(response, "choices", None)
    if not choices and isinstance(response, dict):
        choices = response.get("choices")
    if not choices:
        return ""
    first = choices[0]
    message = getattr(first, "message", None)
    if message is None and isinstance(first, dict):
        message = first.get("message")
    content = getattr(message, "content", None)
    if content is None and isinstance(message, dict):
        content = message.get("content")
    return content or ""

FAKE_ADAPTER_REPLY = "[Hermes Tavern fake adapter response]"
DEFAULT_PROVIDER_TIMEOUT_SECONDS = 45.0

class TavernModelClient(Protocol):
    """Structural interface every Tavern model adapter must satisfy."""

    def generate(self, messages: list[dict[str, Any]], profile: Any) -> str:
        ...


class FakeModelAdapter:
    """Deterministic stand-in adapter — no network, no secrets."""

    def generate(self, messages: list[dict[str, Any]], profile: Any) -> str:
        return FAKE_ADAPTER_REPLY


class HermesProviderAdapter:
    """Real-provider bridge skeleton.

    ``resolver`` is injected by the caller so tests can pass a fake and the
    future real adapter can call Hermes' ``resolve_runtime_provider`` at the
    last possible moment.  Resolver payloads may contain credentials because
    Hermes needs them to perform the request, but this class never persists or
    exposes those fields through debug/status helpers.

    Real network generation is intentionally not wired in Phase 5;
    ``generate`` resolves and sanitizes metadata, then raises
    ``NotImplementedError`` before any outbound request can happen.
    """

    def __init__(self, resolver: Callable[[], dict[str, Any]]) -> None:
        self._resolver = resolver
        self.last_debug_descriptor: dict[str, Any] | None = None

    def _safe_descriptor(self, payload: dict[str, Any]) -> dict[str, Any]:
        return sanitize_provider_payload(payload)

    def resolve_debug_descriptor(self) -> dict[str, Any]:
        payload = self._resolver()
        safe = self._safe_descriptor(payload)
        self.last_debug_descriptor = safe
        return safe

    def generate(self, messages: list[dict[str, Any]], profile: Any) -> str:
        del messages, profile
        self.resolve_debug_descriptor()
        raise NotImplementedError(
            "HermesProviderAdapter: real generation not yet wired"
        )


class HermesChatCompletionAdapter(HermesProviderAdapter):
    """OpenAI-compatible chat-completions adapter, live-gated by runtime.

    Tests pass ``client_factory``; production lazily imports ``openai.OpenAI``.
    The resolved provider payload may contain credentials, but only sanitized
    descriptors are exposed via ``last_debug_descriptor``.
    """

    def __init__(
        self,
        resolver: Callable[[], dict[str, Any]],
        client_factory: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(resolver)
        self._client_factory = client_factory

    def _build_client(self, payload: dict[str, Any]) -> Any:
        factory = self._client_factory
        if factory is None:
            from openai import OpenAI

            factory = OpenAI
        kwargs: dict[str, Any] = {}
        if payload.get("api_key"):
            kwargs["api_key"] = payload["api_key"]
        base_url = payload.get("base_url")
        if base_url:
            validate_provider_base_url(base_url)   # raises ValueError if unsafe
            kwargs["base_url"] = base_url
        timeout = payload.get("timeout", DEFAULT_PROVIDER_TIMEOUT_SECONDS)
        try:
            timeout = float(timeout)
        except (TypeError, ValueError):
            timeout = DEFAULT_PROVIDER_TIMEOUT_SECONDS
        kwargs["timeout"] = max(1.0, min(timeout, DEFAULT_PROVIDER_TIMEOUT_SECONDS))
        return factory(**kwargs)

    def generate(self, messages: list[dict[str, Any]], profile: Any) -> str:
        try:
            payload = self._resolver()
        except Exception:
            if self._client_factory is None:
                raise
            payload = {"model": getattr(profile, "model_id", None) or getattr(profile, "model", None) or "test-model"}
        self.last_debug_descriptor = self._safe_descriptor(payload)
        model = payload.get("model") or getattr(profile, "model_id", None)
        if not model:
            raise RuntimeError("HermesChatCompletionAdapter requires a model id")
        if not payload.get("api_key") and self._client_factory is None:
            raise RuntimeError("HermesChatCompletionAdapter requires a resolved API key")
        client = self._build_client(payload)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        content = _message_content(response)
        if not content:
            raise RuntimeError("HermesChatCompletionAdapter returned empty content")
        return content
