"""Mock-first bridge to Hermes runtime provider resolution.

Phase 6 intentionally does not perform real LLM/network calls.  This module
only centralizes the lazy provider-resolution boundary so tests can inject a
fake resolver and future real adapters can reuse Hermes' configured provider
credentials without persisting them in Tavern storage.
"""

from __future__ import annotations

from ipaddress import ip_address
from urllib.parse import urlparse
from typing import Any, Callable

from plugins.hermes_tavern.model_router import ModelProfileDescriptor

APIYI_PROVIDER = "apiyi"
APIYI_BASE_URL = "https://api.apiyi.com/v1"

SAFE_URL_SCHEMES: frozenset[str] = frozenset({"https"})

# IPv4 private/loopback prefixes that must never appear as provider base_url hosts.
_BLOCKED_HOST_PREFIXES: tuple[str, ...] = (
    "127.",
    "10.",
    "192.168.",
    "169.254.",   # link-local
    "0.",
)
_BLOCKED_HOSTS: frozenset[str] = frozenset(
    {"localhost", "::1", "0.0.0.0"}
)


def validate_provider_base_url(base_url: str) -> None:
    """Raise ValueError (user-safe message) if base_url is not allowed.

    Rejects non-https schemes and private/loopback hostnames.
    The error message never echoes the rejected URL value.
    """
    if not base_url:
        raise ValueError("Provider URL not allowed: empty URL")

    try:
        parsed = urlparse(base_url)
    except Exception:
        raise ValueError("Provider URL not allowed: could not parse URL")

    scheme = (parsed.scheme or "").lower()
    if scheme not in SAFE_URL_SCHEMES:
        raise ValueError("Provider URL not allowed: unsupported scheme")

    # parsed.hostname lowercases and strips brackets from IPv6 addresses
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("Provider URL not allowed: missing host")

    if host in _BLOCKED_HOSTS:
        raise ValueError("Provider URL not allowed: private or loopback host")

    try:
        parsed_ip = ip_address(host)
    except ValueError:
        parsed_ip = None
    if parsed_ip is not None:
        if (
            parsed_ip.is_private
            or parsed_ip.is_loopback
            or parsed_ip.is_link_local
            or parsed_ip.is_reserved
            or parsed_ip.is_unspecified
        ):
            raise ValueError("Provider URL not allowed: private or loopback host")
        return

    # Conservative phase-19 stance: reject non-IP IPv6-looking hostnames too.
    if ":" in host:
        raise ValueError("Provider URL not allowed: private or loopback host")

    for prefix in _BLOCKED_HOST_PREFIXES:
        if host.startswith(prefix):
            raise ValueError("Provider URL not allowed: private or loopback host")

    # Reject 172.16.0.0/12 private range for dotted hosts that ip_address did not parse.
    if host.startswith("172."):
        parts = host.split(".")
        try:
            second = int(parts[1]) if len(parts) >= 2 else -1
        except ValueError:
            second = -1
        if 16 <= second <= 31:
            raise ValueError("Provider URL not allowed: private or loopback host")
APIYI_KEY_ENV = "APIYI_API_KEY"
APIYI_DEFAULT_MODEL = "claude-opus-4-6"
APIYI_CONTEXT_WINDOW = 200_000

_SECRET_FIELDS: frozenset[str] = frozenset(
    {"api_key", "access_token", "secret", "token", "password"}
)


def _is_secret_key(key: Any) -> bool:
    return str(key).lower() in _SECRET_FIELDS


class HermesRuntimeProviderResolver:
    """Resolve a Tavern model descriptor through Hermes' provider chain.

    The resolver import is lazy so importing Hermes Tavern never initializes
    provider credentials.  Tests should pass ``resolve_fn`` to avoid touching
    real Hermes configuration or external services.
    """

    def __init__(
        self,
        descriptor: ModelProfileDescriptor,
        resolve_fn: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        self.descriptor = descriptor
        self._resolve_fn = resolve_fn

    def resolve(self) -> dict[str, Any]:
        if self.descriptor.provider in {APIYI_PROVIDER, f"custom:{APIYI_PROVIDER}"}:
            return _resolve_apiyi(self.descriptor)

        resolve_fn = self._resolve_fn
        if resolve_fn is None:
            from hermes_cli.runtime_provider import resolve_runtime_provider

            resolve_fn = resolve_runtime_provider
        return resolve_fn(
            requested=self.descriptor.provider,
            target_model=self.descriptor.model_id,
        )


def _resolve_apiyi(descriptor: ModelProfileDescriptor) -> dict[str, Any]:
    try:
        from hermes_cli.config import get_env_value

        api_key = get_env_value(APIYI_KEY_ENV) or ""
    except Exception:
        api_key = ""
    return {
        "provider": APIYI_PROVIDER,
        "api_mode": "chat_completions",
        "base_url": APIYI_BASE_URL,
        "api_key": api_key,
        "model": descriptor.model_id or APIYI_DEFAULT_MODEL,
        "source": "tavern_apiyi_profile",
        "requested_provider": descriptor.provider,
        "key_env": APIYI_KEY_ENV,
    }


def sanitize_provider_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return provider metadata safe for debug/status display.

    Secret-like keys are omitted case-insensitively at every nested dict level.
    Non-secret metadata such as provider, model, base_url, source, and timeout is
    preserved so dry-run/status output remains useful without exposing
    credentials.
    """
    safe = _sanitize_provider_value(payload)
    return safe if isinstance(safe, dict) else {}


def _sanitize_provider_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: _sanitize_provider_value(v)
            for k, v in value.items()
            if not _is_secret_key(k)
        }
    if isinstance(value, list):
        return [_sanitize_provider_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_sanitize_provider_value(item) for item in value)
    return value
