"""Tests for mock-first Hermes provider bridge."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.model_router import ModelProfileDescriptor
from plugins.hermes_tavern.provider_bridge import (
    APIYI_BASE_URL,
    APIYI_DEFAULT_MODEL,
    APIYI_KEY_ENV,
    APIYI_PROVIDER,
    HermesRuntimeProviderResolver,
    sanitize_provider_payload,
    validate_provider_base_url,
)


def test_sanitize_provider_payload_omits_secret_fields():
    payload = {
        "provider": "anthropic",
        "model": "claude-opus-4-6",
        "api_key": "do-not-leak",
        "access_token": "do-not-leak",
        "password": "do-not-leak",
    }

    safe = sanitize_provider_payload(payload)

    assert safe == {"provider": "anthropic", "model": "claude-opus-4-6"}


def test_sanitize_provider_payload_normalizes_secret_key_variants_recursively():
    payload = {
        "provider": "anthropic",
        "model": "claude-opus-4-6",
        "base_url": "https://api.example.test/v1",
        "api-key": "leaked-api-key",
        "ApiKey": "leaked-camel-api-key",
        "ＡＰＩ＿ＫＥＹ": "leaked-fullwidth-api-key",
        "headers": {
            "Access Token": "leaked-access-token",
            "x-request-id": "req-123",
        },
        "nested": [
            {
                "Secret": "fake-secret-do-not-persist",
                "metadata": {
                    "Pass-Word": "leaked-password",
                    "𝚊𝚙𝚒_𝚔𝚎𝚢": "leaked-monospace-api-key",
                    "region": "test",
                    7: "non-string-key-metadata",
                },
                "tuple": ({"TOKEN": "leaked-token", "timeout": 30},),
            }
        ],
    }

    safe = sanitize_provider_payload(payload)

    assert safe["provider"] == "anthropic"
    assert safe["model"] == "claude-opus-4-6"
    assert safe["base_url"] == "https://api.example.test/v1"
    assert safe["headers"] == {"x-request-id": "req-123"}
    assert safe["nested"] == [
        {
            "metadata": {"region": "test", 7: "non-string-key-metadata"},
            "tuple": ({"timeout": 30},),
        }
    ]
    assert "leaked-" not in repr(safe)
    assert "fake-secret-do-not-persist" not in repr(safe)


def test_runtime_provider_resolver_is_dependency_injectable():
    calls = []

    def fake_resolver(**kwargs):
        calls.append(kwargs)
        return {"provider": kwargs["requested"], "model": kwargs["target_model"]}

    descriptor = ModelProfileDescriptor(
        provider="anthropic",
        model_id="claude-opus-4-6",
        mode="chat",
        context_window=200_000,
        source="default_priority_2",
    )
    resolver = HermesRuntimeProviderResolver(descriptor, resolve_fn=fake_resolver)

    payload = resolver.resolve()

    assert calls == [{"requested": "anthropic", "target_model": "claude-opus-4-6"}]
    assert payload == {"provider": "anthropic", "model": "claude-opus-4-6"}


def test_apiyi_resolver_uses_env_file_without_leaking_secret(monkeypatch):
    secret = "test-secret"

    def fake_get_env_value(key):
        assert key == APIYI_KEY_ENV
        return secret

    import hermes_cli.config as config_module

    monkeypatch.setattr(config_module, "get_env_value", fake_get_env_value)
    descriptor = ModelProfileDescriptor(
        provider=APIYI_PROVIDER,
        model_id=APIYI_DEFAULT_MODEL,
        mode="chat",
        context_window=200_000,
        source="db_profile",
    )

    payload = HermesRuntimeProviderResolver(descriptor).resolve()
    safe = sanitize_provider_payload(payload)

    assert payload["api_key"] == secret
    assert payload["base_url"] == APIYI_BASE_URL
    assert payload["model"] == APIYI_DEFAULT_MODEL
    assert safe["provider"] == APIYI_PROVIDER
    assert safe["key_env"] == APIYI_KEY_ENV
    assert "api_key" not in safe


# --- Phase 19: base_url validation ---


@pytest.mark.parametrize("url", [
    "http://api.example.com/v1",
    "ftp://api.example.com/v1",
    "file:///etc/passwd",
    "javascript:alert(1)",
])
def test_validate_provider_base_url_rejects_non_https_scheme(url):
    with pytest.raises(ValueError) as exc_info:
        validate_provider_base_url(url)
    msg = str(exc_info.value)
    assert url not in msg  # error message must never echo the rejected URL


def test_validate_provider_base_url_rejects_empty_string():
    with pytest.raises(ValueError):
        validate_provider_base_url("")


@pytest.mark.parametrize("url", [
    "https://user@api.example.com/v1",
    "https://user:secret@api.example.com/v1",
])
def test_validate_provider_base_url_rejects_embedded_credentials(url):
    with pytest.raises(ValueError) as exc_info:
        validate_provider_base_url(url)
    assert url not in str(exc_info.value)


@pytest.mark.parametrize("url", [
    "https://localhost/v1",
    "https://127.0.0.1/v1",
    "https://127.1.2.3/v1",
    "https://１２７.０.０.１/v1",
    "https://2130706433/v1",
    "https://２１３０７０６４３３/v1",
    "https://0x7f000001/v1",
    "https://0x7f.1/v1",
    "https://0177.1/v1",
    "https://4294967296/v1",
    "https://4294967297/v1",
    "https://0.0.0.0/v1",
    "https://::1/v1",
    "https://10.0.0.1/v1",
    "https://10.255.255.255/v1",
    "https://192.168.0.1/v1",
    "https://192.168.1.100/v1",
    "https://172.16.0.1/v1",
    "https://172.31.255.255/v1",
    "https://169.254.1.1/v1",
    "https://[::1]/v1",
])
def test_validate_provider_base_url_rejects_private_hosts(url):
    with pytest.raises(ValueError) as exc_info:
        validate_provider_base_url(url)
    msg = str(exc_info.value)
    assert url not in msg  # error message must never echo the rejected URL


@pytest.mark.parametrize("url", [
    "https://%31%32%37.0.0.1/v1",
    "https://127%2e0%2e0%2e1/v1",
    "https://%32%31%33%30%37%30%36%34%33%33/v1",
])
def test_validate_provider_base_url_rejects_percent_encoded_hosts(url):
    with pytest.raises(ValueError) as exc_info:
        validate_provider_base_url(url)
    assert url not in str(exc_info.value)


@pytest.mark.parametrize(
    "root_dot",
    [".", "\u3002", "\uff61", "\uff0e"],
    ids=[
        "ascii",
        "ideographic-full-stop",
        "halfwidth-ideographic-full-stop",
        "fullwidth-full-stop",
    ],
)
def test_validate_provider_base_url_rejects_localhost_with_trailing_root_dot(root_dot):
    url = f"https://localhost{root_dot}/v1"
    with pytest.raises(ValueError) as exc_info:
        validate_provider_base_url(url)
    assert url not in str(exc_info.value)


@pytest.mark.parametrize(
    "separator",
    ["\u3002", "\uff61", "\uff0e"],
    ids=["ideographic-full-stop", "halfwidth-ideographic-full-stop", "fullwidth-full-stop"],
)
def test_validate_provider_base_url_rejects_loopback_with_idna_dot_separator(separator):
    url = f"https://127{separator}0{separator}0{separator}1/v1"
    with pytest.raises(ValueError):
        validate_provider_base_url(url)


@pytest.mark.parametrize("url", [
    "https://api.apiyi.com/v1",
    "https://api.openai.com/v1",
    "https://openrouter.ai/api/v1",
    "https://api.anthropic.com/v1",
    "https://1.1.1.1/v1",
    "https://134744072/v1",     # legacy integer form of public 8.8.8.8
    "https://0x08080808/v1",    # legacy hexadecimal form of public 8.8.8.8
    "https://172.32.0.1/v1",   # 172.32 is NOT in the private range
])
def test_validate_provider_base_url_allows_safe_urls(url):
    validate_provider_base_url(url)  # must not raise
