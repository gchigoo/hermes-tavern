"""Tests for Hermes Tavern model adapters."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.adapters import (
    FAKE_ADAPTER_REPLY,
    FakeModelAdapter,
    HermesChatCompletionAdapter,
    HermesProviderAdapter,
)


def test_fake_model_adapter_is_deterministic():
    assert FakeModelAdapter().generate([], None) == FAKE_ADAPTER_REPLY


def test_hermes_provider_adapter_debug_descriptor_omits_secrets():
    adapter = HermesProviderAdapter(
        lambda: {
            "provider": "anthropic",
            "model": "claude-opus-4-6",
            "api_key": "should-not-leak",
            "access_token": "should-not-leak",
        }
    )

    descriptor = adapter.resolve_debug_descriptor()

    assert descriptor == {"provider": "anthropic", "model": "claude-opus-4-6"}
    assert "api_key" not in descriptor
    assert "access_token" not in descriptor


def test_hermes_provider_adapter_debug_descriptor_redacts_nested_mixed_case_secrets():
    adapter = HermesProviderAdapter(
        lambda: {
            "provider": "anthropic",
            "model": "claude-opus-4-6",
            "API_KEY": "fake-api-key-do-not-persist",
            "headers": {"Access_Token": "fake-access-token-do-not-persist", "x-safe": "yes"},
            "extra": {"Secret": "fake-secret-do-not-persist", "base_url": "https://api.example.test/v1"},
        }
    )

    descriptor = adapter.resolve_debug_descriptor()

    assert descriptor == {
        "provider": "anthropic",
        "model": "claude-opus-4-6",
        "headers": {"x-safe": "yes"},
        "extra": {"base_url": "https://api.example.test/v1"},
    }
    assert "fake-" not in repr(descriptor)


def test_hermes_provider_adapter_does_not_make_real_generation():
    adapter = HermesProviderAdapter(lambda: {"provider": "anthropic", "api_key": "secret"})

    with pytest.raises(NotImplementedError):
        adapter.generate([{"role": "user", "content": "hi"}], None)

    assert adapter.last_debug_descriptor == {"provider": "anthropic"}


class _FakeCompletions:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return {"choices": [{"message": {"content": "live adapter reply"}}]}


class _FakeChat:
    def __init__(self) -> None:
        self.completions = _FakeCompletions()


class _FakeOpenAIClient:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.chat = _FakeChat()


def test_hermes_chat_completion_adapter_uses_injected_client_and_redacts_debug():
    created = []

    def factory(**kwargs):
        client = _FakeOpenAIClient(**kwargs)
        created.append(client)
        return client

    adapter = HermesChatCompletionAdapter(
        lambda: {
            "provider": "apiyi",
            "base_url": "https://api.apiyi.com/v1",
            "api_key": "secret",
            "model": "claude-opus-4-6",
        },
        client_factory=factory,
    )

    reply = adapter.generate([{"role": "user", "content": "hi"}], None)

    assert reply == "live adapter reply"
    assert created[0].kwargs == {
        "api_key": "secret",
        "base_url": "https://api.apiyi.com/v1",
        "timeout": 45.0,
    }
    assert created[0].chat.completions.calls[0]["model"] == "claude-opus-4-6"
    assert "api_key" not in adapter.last_debug_descriptor
    assert adapter.last_debug_descriptor["provider"] == "apiyi"


def test_hermes_chat_completion_adapter_applies_bounded_timeout():
    created = []

    def factory(**kwargs):
        client = _FakeOpenAIClient(**kwargs)
        created.append(client)
        return client

    adapter = HermesChatCompletionAdapter(
        lambda: {
            "provider": "apiyi",
            "base_url": "https://api.apiyi.com/v1",
            "api_key": "test-placeholder-key",
            "model": "claude-opus-4-6",
            "timeout": 999,
        },
        client_factory=factory,
    )

    assert adapter.generate([{"role": "user", "content": "hi"}], None) == "live adapter reply"
    assert created[0].kwargs["timeout"] == 45.0


# --- Phase 19: base_url validation + error envelope ---


def test_hermes_chat_completion_adapter_rejects_private_base_url():
    adapter = HermesChatCompletionAdapter(
        lambda: {
            "provider": "evil",
            "base_url": "https://127.0.0.1/v1",
            "api_key": "test-placeholder-key",
            "model": "some-model",
        },
        client_factory=lambda **kw: None,
    )

    with pytest.raises((ValueError, RuntimeError)):
        adapter.generate([{"role": "user", "content": "hi"}], None)


def test_hermes_chat_completion_adapter_rejects_http_base_url():
    adapter = HermesChatCompletionAdapter(
        lambda: {
            "provider": "evil",
            "base_url": "http://api.example.com/v1",
            "api_key": "test-placeholder-key",
            "model": "some-model",
        },
        client_factory=lambda **kw: None,
    )

    with pytest.raises((ValueError, RuntimeError)):
        adapter.generate([{"role": "user", "content": "hi"}], None)
