from types import SimpleNamespace

from plugins.hermes_tavern.identity import session_key_from_event


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


def test_dm_event_key_contains_platform_chat_and_user():
    key = session_key_from_event(_event())

    assert "telegram" in key
    assert "chat-1" in key
    assert "user-1" in key


def test_group_topic_event_key_differs_by_thread_id():
    key_a = session_key_from_event(_event(thread_id="thread-a"))
    key_b = session_key_from_event(_event(thread_id="thread-b"))

    assert key_a != key_b
    assert "thread-a" in key_a
    assert "thread-b" in key_b


def test_missing_optional_fields_do_not_raise():
    event = SimpleNamespace(source=SimpleNamespace(platform="discord"))

    key = session_key_from_event(event)

    assert "discord" in key
    assert isinstance(key, str)
