from types import SimpleNamespace

from hermes_tavern.identity import session_key_from_event


def _event(**source_overrides):
    source = SimpleNamespace(
        platform="telegram",
        chat_id="chat-1",
        user_id="user-1",
        thread_id=None,
        topic_id=None,
    )
    for key, value in source_overrides.items():
        setattr(source, key, value)
    return SimpleNamespace(source=source)


def test_missing_or_empty_thread_id_normalizes_to_main():
    assert session_key_from_event(_event(thread_id=None)).endswith(
        ":thread:main:user:user-1"
    )
    assert session_key_from_event(_event(thread_id="")).endswith(
        ":thread:main:user:user-1"
    )


def test_topic_id_is_fallback_when_thread_id_is_missing_or_empty():
    assert ":thread:topic-1:" in session_key_from_event(
        _event(thread_id=None, topic_id="topic-1")
    )
    assert ":thread:topic-1:" in session_key_from_event(
        _event(thread_id="", topic_id="topic-1")
    )


def test_explicit_thread_id_takes_precedence_over_topic_id():
    key = session_key_from_event(_event(thread_id="thread-1", topic_id="topic-1"))

    assert ":thread:thread-1:" in key
    assert "topic-1" not in key


def test_key_changes_when_any_identity_field_changes():
    base = _event(thread_id="thread-1")
    changed_events = [
        _event(platform="discord", thread_id="thread-1"),
        _event(chat_id="chat-2", thread_id="thread-1"),
        _event(thread_id="thread-2"),
        _event(user_id="user-2", thread_id="thread-1"),
    ]
    base_key = session_key_from_event(base)

    assert (
        len({base_key, *(session_key_from_event(event) for event in changed_events)})
        == 5
    )

    topic_key = session_key_from_event(_event(thread_id=None, topic_id="topic-1"))
    changed_topic_key = session_key_from_event(_event(thread_id=None, topic_id="topic-2"))

    assert topic_key != changed_topic_key


def test_missing_optional_fields_do_not_raise():
    event = SimpleNamespace(source=SimpleNamespace(platform="discord"))

    key = session_key_from_event(event)

    assert "discord" in key
    assert isinstance(key, str)


def test_missing_empty_identity_fields_normalize_to_unknown():
    key = session_key_from_event(
        SimpleNamespace(source=SimpleNamespace(platform="", chat_id=None, user_id=""))
    )

    assert key == "unknown:chat:unknown:thread:main:user:unknown"


def test_direct_event_identity_fields_work_without_source():
    event = SimpleNamespace(
        platform="slack",
        chat_id="chat-1",
        thread_id="thread-1",
        topic_id="topic-1",
        user_id="user-1",
    )

    assert (
        session_key_from_event(event)
        == "slack:chat:chat-1:thread:thread-1:user:user-1"
    )


def test_source_identity_fields_work():
    assert (
        session_key_from_event(_event(thread_id="thread-1"))
        == "telegram:chat:chat-1:thread:thread-1:user:user-1"
    )


class _RaisesOnAttributeAccess:
    def __getattr__(self, name):
        raise RuntimeError(f"failed to read {name}")


def test_attribute_access_errors_fall_back_to_deterministic_key():
    assert (
        session_key_from_event(_RaisesOnAttributeAccess())
        == "unknown:chat:unknown:thread:main:user:unknown"
    )


def test_enum_like_values_use_value_attribute():
    event = _event(
        platform=SimpleNamespace(value="matrix"),
        chat_id=SimpleNamespace(value="room-1"),
        thread_id=SimpleNamespace(value="thread-1"),
        user_id=SimpleNamespace(value="user-1"),
    )

    assert (
        session_key_from_event(event)
        == "matrix:chat:room-1:thread:thread-1:user:user-1"
    )
