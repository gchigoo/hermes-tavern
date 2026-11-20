"""Mock-first bridge to Hermes runtime provider resolution.

Phase 6 intentionally does not perform real LLM/network calls.  This module
only centralizes the lazy provider-resolution boundary so tests can inject a
fake resolver and future real adapters can reuse Hermes' configured provider
credentials without persisting them in Tavern storage.
"""

from __future__ import annotations

import unicodedata
from ipaddress import ip_address
from urllib.parse import urlparse
from typing import Any, Callable

from hermes_tavern.model_router import ModelProfileDescriptor

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
_IDNA_DOT_EQUIVALENTS = str.maketrans({"\u3002": ".", "\uff61": ".", "\uff0e": "."})


def _normalize_host(host: str) -> str:
    """Normalize compatibility characters, digits, and a DNS root dot."""
    normalized = unicodedata.normalize(
        "NFKC", host.translate(_IDNA_DOT_EQUIVALENTS)
    ).casefold().removesuffix(".")
    return "".join(
        str(unicodedata.decimal(character)) if character.isdecimal() else character
        for character in normalized
    )


def _looks_like_legacy_ipv4(host: str) -> bool:
    """Return whether every hostname label uses legacy numeric IPv4 syntax."""
    parts = host.split(".")
    if not parts or any(not part for part in parts):
        return False
    for part in parts:
        if part.startswith("0x"):
            digits = part[2:]
            if not digits or any(character not in "0123456789abcdef" for character in digits):
                return False
        elif not part.isascii() or not part.isdecimal():
            return False
    return True


def _parse_legacy_ipv4(host: str):
    """Parse inet_aton-style numeric IPv4 without resolving hostnames."""
    parts = host.split(".")
    if not 1 <= len(parts) <= 4:
        return None

    numbers: list[int] = []
    for part in parts:
        if not part:
            return None
        if part.lower().startswith("0x"):
            digits, base = part[2:], 16
        elif len(part) > 1 and part.startswith("0"):
            digits, base = part[1:], 8
        else:
            digits, base = part, 10
        valid_digits = {
            8: "01234567",
            10: "0123456789",
            16: "0123456789abcdef",
        }[base]
        if not digits or any(character.lower() not in valid_digits for character in digits):
            return None
        numbers.append(int(digits, base))

    final_width = {1: 32, 2: 24, 3: 16, 4: 8}[len(numbers)]
    if any(number > 0xFF for number in numbers[:-1]):
        return None
    if numbers[-1] >= 1 << final_width:
        return None

    value = numbers[-1]
    for index, number in enumerate(numbers[:-1]):
        value |= number << (24 - 8 * index)
    return ip_address(value)


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
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Provider URL not allowed: embedded credentials")

    # parsed.hostname strips brackets from IPv6 addresses but leaves percent-
    # encoded host text intact. Reject it before clients can decode it to an
    # otherwise blocked address.
    raw_host = parsed.hostname or ""
    if "%" in raw_host:
        raise ValueError("Provider URL not allowed: encoded host")

    # Normalize Unicode decimal forms before classifying numeric hosts; no DNS
    # lookup is needed.
    host = _normalize_host(raw_host)
    if not host:
        raise ValueError("Provider URL not allowed: missing host")

    if host in _BLOCKED_HOSTS:
        raise ValueError("Provider URL not allowed: private or loopback host")

    try:
        parsed_ip = ip_address(host)
    except ValueError:
        parsed_ip = _parse_legacy_ipv4(host)
        if parsed_ip is None and _looks_like_legacy_ipv4(host):
            raise ValueError("Provider URL not allowed: invalid numeric host")
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
    {"apikey", "accesstoken", "secret", "token", "password"}
)


def _is_secret_key(key: Any) -> bool:
    if not isinstance(key, str):
        return False
    normalized_key = "".join(
        character
        for character in unicodedata.normalize("NFKC", key).casefold()
        if character.isalnum()
    )
    return normalized_key in _SECRET_FIELDS


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

    Secret-like keys are omitted at every nested dict level regardless of case
    or non-alphanumeric separators.
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
