import json
from dataclasses import asdict

import pytest

from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers import MAX_LOCAL_IMPORT_BYTES
from plugins.hermes_tavern.importers.lorebooks import (
    import_embedded_lorebook_from_card,
    import_st_lorebook_json,
    import_lorebook_file,
)
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.lorebook import match_lorebook_entries, modules_from_lore_matches


def _v3_card_with_character_book(entries: dict | None = None) -> dict:
    """Minimal v3 card raw dict with an embedded character_book."""
    return {
        "spec": "chara_card_v3",
        "spec_version": "3.0",
        "data": {
            "name": "苏韵柔",
            "description": "",
            "first_mes": "",
            "character_book": {
                "name": "隐欲 V3",
                "entries": entries or {
                    "0": {"comment": "E1", "content": "First lore.", "keys": ["key1"]},
                    "1": {"comment": "E2", "content": "Second lore.", "keys": ["key2"]},
                },
            },
        },
        "name": "",
        "description": "",
        "first_mes": "",
    }


def test_embedded_lorebook_extracts_v3_character_book():
    card = parse_character_card(_v3_card_with_character_book())

    result = import_embedded_lorebook_from_card(card)

    assert result is not None
    assert result.name == "隐欲 V3"
    assert len(result.entries) == 2
    assert result.entries[0].content == "First lore."


def test_embedded_lorebook_extracts_legacy_top_level_character_book():
    raw = {
        "name": "Gareth",
        "character_book": {
            "name": "Legacy Book",
            "entries": [{"comment": "Old", "content": "Old lore.", "keys": ["old"]}],
        },
    }
    card = parse_character_card(raw)

    result = import_embedded_lorebook_from_card(card)

    assert result is not None
    assert result.name == "Legacy Book"
    assert len(result.entries) == 1


def test_embedded_lorebook_extracts_world_info_shape():
    raw = {
        "spec": "chara_card_v3",
        "data": {
            "name": "Elena",
            "world_info": {
                "name": "World Book",
                "entries": [{"comment": "W", "content": "World lore.", "keys": ["world"]}],
            },
        },
        "name": "",
    }
    card = parse_character_card(raw)

    result = import_embedded_lorebook_from_card(card)

    assert result is not None
    assert result.name == "World Book"


def test_embedded_lorebook_returns_none_when_no_book():
    card = parse_character_card({"name": "Plain Card"})

    assert import_embedded_lorebook_from_card(card) is None


@pytest.mark.parametrize(
    "primary_entry",
    (
        {"content": "   "},
        {"content": 12},
        {},
    ),
)
def test_embedded_lorebook_unusable_character_book_falls_back_to_world_info(primary_entry):
    """Unusable data.character_book entries yield the data.world_info book."""
    fallback = "Fallback world lore."
    raw = {
        "spec": "chara_card_v3",
        "data": {
            "name": "Elena",
            "character_book": {
                "name": "Broken Book",
                "entries": [primary_entry],
            },
            "world_info": {
                "name": "World Book",
                "entries": [{"comment": "W", "content": fallback, "keys": ["world"]}],
            },
        },
        "name": "",
    }
    card = parse_character_card(raw)

    result = import_embedded_lorebook_from_card(card)
    repeated = import_embedded_lorebook_from_card(card)

    assert result is not None
    assert repeated is not None
    assert result.source == f"embedded:{card.id}:data.world_info"
    assert [entry.content for entry in result.entries] == [fallback]
    assert result.id == repeated.id
    assert result.id


@pytest.mark.parametrize(
    "content",
    (
        pytest.param(None, id="absent"),
        pytest.param("   ", id="whitespace"),
        pytest.param(12, id="numeric"),
    ),
)
def test_embedded_lorebook_character_book_text_alias_wins_over_world_info(content):
    """Valid data.character_book text wins over data.world_info even if content is blank or numeric."""
    primary = "Primary text lore."
    primary_entry = {"comment": "P", "text": primary, "keys": ["primary"]}
    if content is not None:
        primary_entry["content"] = content
    raw = {
        "spec": "chara_card_v3",
        "data": {
            "name": "Elena",
            "character_book": {
                "name": "Primary Book",
                "entries": [primary_entry],
            },
            "world_info": {
                "name": "World Book",
                "entries": [{"comment": "W", "content": "Fallback world lore.", "keys": ["world"]}],
            },
        },
        "name": "",
    }
    card = parse_character_card(raw)

    result = import_embedded_lorebook_from_card(card)

    assert result is not None
    assert result.source == f"embedded:{card.id}:data.character_book"
    assert [entry.content for entry in result.entries] == [primary]


def test_embedded_lorebook_returns_none_when_all_candidate_entries_unusable():
    """Populated nested and top-level books with no usable entry import as None."""
    raw = {
        "spec": "chara_card_v3",
        "data": {
            "name": "Elena",
            "character_book": {"entries": [{"content": "   "}]},
            "world_info": {"entries": [{"content": 12}]},
        },
        "name": "",
        "character_book": {"entries": [{}]},
        "world_info": {"entries": [{"content": "\n\t"}]},
    }
    card = parse_character_card(raw)

    assert import_embedded_lorebook_from_card(card) is None


def test_embedded_lorebook_stable_id_on_repeated_calls():
    card = parse_character_card(_v3_card_with_character_book())

    result1 = import_embedded_lorebook_from_card(card)
    result2 = import_embedded_lorebook_from_card(card)

    assert result1 is not None
    assert result1.id == result2.id
    assert result1.id  # non-empty


def test_embedded_lorebook_id_differs_between_cards():
    card_a = parse_character_card(_v3_card_with_character_book())
    raw_b = _v3_card_with_character_book()
    raw_b["data"]["name"] = "顾时薇"
    card_b = parse_character_card(raw_b)

    id_a = import_embedded_lorebook_from_card(card_a).id
    id_b = import_embedded_lorebook_from_card(card_b).id

    assert id_a != id_b


def test_embedded_lorebook_store_round_trip_is_idempotent(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    card = parse_character_card(_v3_card_with_character_book())
    embedded = import_embedded_lorebook_from_card(card)

    lore_id1 = store.save_lorebook(embedded)
    lore_id2 = store.save_lorebook(embedded)

    assert lore_id1 == lore_id2
    lorebooks = store.list_lorebooks()
    assert len(lorebooks) == 1


_CONTENT_ALIASES = ("content", "entry", "text", "value")
_UNUSABLE_CONTENT_VALUES = (
    pytest.param("   ", id="whitespace"),
    pytest.param(12, id="nonzero-number"),
    pytest.param(True, id="true"),
    pytest.param(False, id="false"),
    pytest.param(["blocked"], id="nonempty-list"),
    pytest.param({"blocked": "lore"}, id="nonempty-dict"),
    pytest.param("", id="empty"),
    pytest.param(None, id="null"),
    pytest.param(0, id="zero"),
)


@pytest.mark.parametrize("selected_alias", ("entry", "text", "value"))
@pytest.mark.parametrize("unusable", _UNUSABLE_CONTENT_VALUES)
def test_lorebook_import_content_alias_skips_unusable_earlier_values(selected_alias, unusable):
    """Earlier unusable aliases fall through to the first later string with nonempty strip."""
    selected_index = _CONTENT_ALIASES.index(selected_alias)
    raw = {alias: unusable for alias in _CONTENT_ALIASES[:selected_index]}
    for alias in _CONTENT_ALIASES[selected_index:]:
        raw[alias] = f"{alias} lore"
    selected = raw[selected_alias]
    companion = "Companion lore."
    book = import_st_lorebook_json({
        "entries": [
            raw,
            {"comment": "Healthy", "content": companion},
        ],
    })

    assert [entry.content for entry in book.entries] == [selected, companion]


@pytest.mark.parametrize("winner", ("content", "entry", "text"))
def test_lorebook_import_content_alias_precedence_preserves_whitespace(winner):
    """When several aliases are usable, the earliest wins with its whitespace intact."""
    start = _CONTENT_ALIASES.index(winner)
    raw = {alias: f"  {alias} lore  " for alias in _CONTENT_ALIASES[start:]}
    book = import_st_lorebook_json({"entries": [raw]})

    assert [entry.content for entry in book.entries] == [raw[winner]]


@pytest.mark.parametrize("unusable", _UNUSABLE_CONTENT_VALUES)
def test_lorebook_import_excludes_entry_when_content_aliases_unusable(unusable):
    """An entry with only unusable content aliases is dropped; a companion remains."""
    companion = "Companion lore."
    book = import_st_lorebook_json({
        "entries": [
            {alias: unusable for alias in _CONTENT_ALIASES},
            {"comment": "Healthy", "content": companion},
        ],
    })

    assert [entry.content for entry in book.entries] == [companion]


def test_lorebook_imports_st_entries_dict_shape():
    lorebook = import_st_lorebook_json({
        "name": "Atlas",
        "entries": {
            "1": {"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"], "order": 2},
            "2": {"comment": "Sun", "content": "The sun is blue.", "key": "sun", "disable": True},
        },
    })

    assert lorebook.name == "Atlas"
    assert len(lorebook.entries) == 2
    assert lorebook.entries[0].title == "Moon"
    assert lorebook.entries[0].keys == ("moon",)
    assert lorebook.entries[1].enabled is False


@pytest.mark.parametrize(
    ("flags", "expected"),
    (
        pytest.param({}, True, id="native-absence-defaults-enabled"),
        pytest.param({"enabled": 0}, False, id="explicit-numeric-zero"),
        pytest.param({"enabled": 1}, True, id="explicit-numeric-one"),
        pytest.param({"enabled": "false"}, False, id="explicit-text-false"),
        pytest.param({"enabled": "true"}, True, id="explicit-text-true"),
        pytest.param({"enabled": "false", "disabled": "true"}, False, id="explicit-disabled-wins"),
        pytest.param({"enabled": "true", "disable": True}, True, id="explicit-enabled-wins"),
        pytest.param({"disable": "false"}, True, id="disable-text-false"),
        pytest.param({"disabled": "0"}, True, id="disabled-text-zero"),
        pytest.param({"disable": "true"}, False, id="disable-text-true"),
        pytest.param({"disabled": 1}, False, id="disabled-numeric-one"),
        pytest.param({"enabled": "unknown", "disable": "false"}, True, id="unknown-enabled-uses-default"),
        pytest.param({"disabled": "unknown"}, False, id="unknown-negative-is-conservative"),
    ),
)
def test_lorebook_import_normalizes_legacy_enabled_flags(flags, expected):
    """Public lorebook import normalizes enabled and negative legacy aliases."""
    lorebook = import_st_lorebook_json({"entries": [{"content": "Lore.", **flags}]})

    assert lorebook.entries[0].enabled is expected


def test_lorebook_entry_id_keeps_integer_zero():
    """Integer 0 wins by uid/id/key precedence; False and other falsy values fall back."""
    uid_zero = import_st_lorebook_json({
        "name": "Ids",
        "entries": [
            {"uid": 0, "id": "later", "content": "Uid zero.", "keys": ["uid"]},
        ],
    })
    id_zero = import_st_lorebook_json({
        "name": "Ids",
        "entries": [
            {"id": 0, "key": "later", "content": "Id zero."},
        ],
    })
    key_zero = import_st_lorebook_json({
        "name": "Ids",
        "entries": [
            {"uid": False, "id": "", "key": 0, "content": "Key zero."},
        ],
    })
    fallback = import_st_lorebook_json({
        "name": "Ids",
        "entries": [
            {"content": "Missing id."},
            {"uid": False, "id": False, "key": False, "content": "False id."},
            {"uid": "", "id": None, "key": 0.0, "content": "Other falsy."},
        ],
    })

    assert uid_zero.entries[0].id == "0"
    assert id_zero.entries[0].id == "0"
    assert id_zero.entries[0].keys == ("later",)
    assert key_zero.entries[0].id == "0"
    assert [entry.id for entry in fallback.entries] == ["entry_0", "entry_1", "entry_2"]


def test_lorebook_integer_zero_and_one_stay_distinct_in_store(tmp_path):
    """A 0/1 id pair both survive TavernStore instead of collapsing the zero id."""
    lorebook = import_st_lorebook_json({
        "name": "Pair",
        "entries": [
            {"uid": 0, "id": 9, "comment": "Zero", "content": "Zero lore", "keys": ["zero"]},
            {"uid": 1, "comment": "One", "content": "One lore", "keys": ["one"]},
        ],
    })

    assert [entry.id for entry in lorebook.entries] == ["0", "1"]

    store = TavernStore(tmp_path / "tavern.sqlite3")
    lorebook_id = store.save_lorebook(lorebook)
    stored = store.list_lorebook_entries(lorebook_id)

    assert [entry["id"] for entry in stored] == [f"{lorebook_id}:0", f"{lorebook_id}:1"]
    assert [entry["title"] for entry in stored] == ["Zero", "One"]


@pytest.mark.parametrize("field", ("insertion_order", "order", "displayIndex"))
def test_lorebook_import_zero_order_controls_budget(field):
    """Integer zero order is kept and spends the token budget before a later entry."""
    book = import_st_lorebook_json({
        "name": "Orders",
        "entries": [
            {"uid": "one", "comment": "A one", "content": "BBBB", "constant": True, "insertion_order": 1},
            {"uid": "zero", "comment": "Z zero", "content": "AAAA", "constant": True, field: 0},
        ],
    })

    assert [entry.insertion_order for entry in book.entries] == [1, 0]

    result = match_lorebook_entries([asdict(entry) for entry in book.entries], "", token_budget=1)
    modules = modules_from_lore_matches(result)

    assert [item.entry_id for item in result.matches] == ["zero"]
    assert [(item.entry_id, item.reason) for item in result.excluded] == [("one", "token budget exceeded")]
    assert [module.content for module in modules] == ["AAAA"]
    assert result.token_budget == 1


@pytest.mark.parametrize(
    ("order_fields", "expected_order"),
    (
        ({"insertion_order": 0, "order": 9}, 0),
        ({"order": 0, "displayIndex": 9}, 0),
        ({"insertion_order": -1, "order": 9}, -1),
        ({"insertion_order": 1, "order": 9}, 1),
        ({"insertion_order": "0", "order": 9}, 0),
        ({}, 1),
        ({"insertion_order": None, "order": 9}, 9),
        ({"insertion_order": "", "order": 9}, 9),
        ({"insertion_order": False, "order": 9}, 9),
        ({"insertion_order": 0.0, "order": 9}, 9),
        ({"insertion_order": "invalid", "order": 9}, 1),
        ({"displayIndex": False}, 0),
        ({"displayIndex": 0.0}, 0),
    ),
)
def test_lorebook_import_order_precedence_and_fallbacks(order_fields, expected_order):
    """Present numeric orders win; empty sentinels fall through and invalid values use the index."""
    book = import_st_lorebook_json({
        "name": "Orders",
        "entries": [
            {"uid": "filler", "content": "Filler."},
            {"uid": "target", "content": "Target.", **order_fields},
        ],
    })

    assert book.entries[1].insertion_order == expected_order


@pytest.mark.parametrize("field", ("insertion_order", "order", "displayIndex"))
def test_lorebook_file_import_infinite_order_falls_back(field, tmp_path):
    """JSON Infinity on any order alias falls back instead of aborting the import."""
    path = tmp_path / "infinite-order.json"
    path.write_text(
        f'{{"entries": [{{"content": "Filler."}}, {{"content": "Target.", "{field}": Infinity}}]}}',
        encoding="utf-8",
    )

    book = import_lorebook_file(path)

    assert book.entries[1].insertion_order == 1


@pytest.mark.parametrize("field", ("probability", "chance"))
@pytest.mark.parametrize("huge", (10**400, -(10**400)))
def test_lorebook_import_huge_probability_falls_back(field, huge):
    """Huge integer probability or chance falls back to 1.0; a percent still scales."""
    book = import_st_lorebook_json({
        "name": "Odds",
        "entries": [
            {"uid": "huge", "content": "Huge.", field: huge},
            {"uid": "healthy", "content": "Healthy.", "probability": 25},
        ],
    })

    assert [entry.probability for entry in book.entries] == [1.0, 0.25]


@pytest.mark.parametrize("encoding", ("utf-8", "utf-8-sig"))
def test_lorebook_file_import_unicode_json(tmp_path, encoding):
    """UTF-8 and UTF-8-SIG lorebook files keep Unicode fields and no leading BOM."""
    payload = {
        "name": "隐欲 · Élodie",
        "entries": [
            {
                "comment": "月相",
                "content": "月亮裂开了，café 仍亮着。",
                "keys": ["月亮", "Élodie"],
            },
        ],
    }
    path = tmp_path / "unicode-lorebook.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding=encoding)

    book = import_lorebook_file(path)
    entry = book.entries[0]
    imported = (
        book.name,
        book.source,
        json.dumps(book.raw, ensure_ascii=False),
        entry.id,
        entry.title,
        entry.content,
        *entry.keys,
    )

    assert book.name == "隐欲 · Élodie"
    assert book.source == str(path)
    assert book.raw == payload
    assert entry.id == "entry_0"
    assert entry.title == "月相"
    assert entry.content == "月亮裂开了，café 仍亮着。"
    assert entry.keys == ("月亮", "Élodie")
    assert all("\ufeff" not in item for item in imported)


def test_lorebook_store_round_trips_entries(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    lorebook = import_st_lorebook_json({"name": "Atlas", "entries": [{"comment": "Moon", "content": "Moon lore", "keys": ["moon"]}]})

    lorebook_id = store.save_lorebook(lorebook)
    stored = store.get_lorebook(lorebook_id)
    entries = store.list_lorebook_entries(lorebook_id)

    assert stored["name"] == "Atlas"
    assert entries[0]["title"] == "Moon"
    assert json.loads(entries[0]["keys_json"]) == ["moon"]


def test_lorebook_importer_rejects_oversize_json(tmp_path):
    path = tmp_path / "oversize-lorebook.json"
    path.write_text(
        json.dumps({"name": "Atlas", "entries": [{"comment": "Moon", "content": "A" * (MAX_LOCAL_IMPORT_BYTES + 1)}]}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="too large"):
        import_lorebook_file(path)


def test_lorebook_matcher_reports_matches_and_exclusions():
    entries = [
        {"id": "1", "title": "Moon", "content": "Moon lore", "keys_json": '["moon"]', "enabled": 1, "probability": 1, "priority": 1},
        {"id": "2", "title": "Sun", "content": "Sun lore", "keys_json": '["sun"]', "enabled": 1, "probability": 0},
        {"id": "3", "title": "Always", "content": "Always lore", "keys_json": "[]", "enabled": 1, "constant": 1, "probability": 1},
    ]

    result = match_lorebook_entries(entries, "The moon rises.")
    modules = modules_from_lore_matches(result)

    assert [m.name for m in modules] == ["lore:Moon", "lore:Always"]
    assert any(ex.title == "Sun" and ex.reason == "probability=0" for ex in result.excluded)


def test_lorebook_bad_regex_is_excluded_not_raised():
    result = match_lorebook_entries([
        {"id": "1", "title": "Broken", "content": "Broken lore", "keys_json": '["["]', "enabled": 1, "regex": 1, "probability": 1}
    ], "text")

    assert not result.matches
    assert "regex error" in result.excluded[0].reason


def test_lorebook_regex_matches_normal_pattern():
    pattern = json.dumps(["moon\\s+.*"])

    result = match_lorebook_entries([
        {
            "id": "1",
            "title": "Moon",
            "content": "Moon lore",
            "keys_json": pattern,
            "enabled": 1,
            "regex": 1,
            "probability": 1,
        }
    ], "The moon rises over the sea.")

    assert len(result.matches) == 1
    assert result.matches[0].title == "Moon"
    assert result.matches[0].reason == "key match: moon\\s+.*"


def test_lorebook_nested_quantifier_is_rejected_before_search(monkeypatch):
    monkeypatched = {"called": False}

    def fail_search(*args, **kwargs):
        monkeypatched["called"] = True
        raise AssertionError("re.search should not be called for nested quantifiers")

    monkeypatch.setattr("plugins.hermes_tavern.lorebook.re.search", fail_search)

    result = match_lorebook_entries([
        {
            "id": "1",
            "title": "Nested",
            "content": "Nested lore",
            "keys_json": '["(a+)+"]',
            "enabled": 1,
            "regex": 1,
            "probability": 1,
        }
    ], "aaaa")

    assert len(result.matches) == 0
    assert result.excluded[0].reason == "regex rejected: nested quantifier"
    assert not monkeypatched["called"]


def test_lorebook_regex_longer_than_256_is_rejected():
    long_pattern = "a" * 257

    result = match_lorebook_entries([
        {
            "id": "1",
            "title": "Long",
            "content": "Long lore",
            "keys_json": f'[{json.dumps(long_pattern)}]',
            "enabled": 1,
            "regex": 1,
            "probability": 1,
        }
    ], "aaaa")

    assert len(result.matches) == 0
    assert result.excluded[0].reason == "regex rejected: pattern too long"


def test_lorebook_secondary_regex_rejection_excludes_entry():
    result = match_lorebook_entries([
        {
            "id": "1",
            "title": "SecondaryNested",
            "content": "Nested lore",
            "keys_json": '["moon"]',
            "secondary_keys_json": '["(a+)+"]',
            "enabled": 1,
            "regex": 1,
            "probability": 1,
        }
    ], "moon aaa")

    assert len(result.matches) == 0
    assert result.excluded[0].reason == "regex rejected: nested quantifier"


@pytest.mark.parametrize("keyword", ("regex error", "regex rejected"))
@pytest.mark.parametrize("regex", (False, True))
@pytest.mark.parametrize("key_position", ("primary", "secondary"))
def test_lorebook_error_prefix_keyword_public_boundary(keyword, regex, key_position):
    """Keys that share a regex error-reason prefix follow ordinary key matching."""
    if key_position == "secondary":
        primary_key = "moon"
        keys_json = json.dumps(["moon"])
        secondary_keys_json = json.dumps([keyword])
        miss_reason = "secondary key filter miss"
    else:
        primary_key = keyword
        keys_json = json.dumps([keyword])
        secondary_keys_json = json.dumps([])
        miss_reason = "no primary key match"
    entry = {
        "id": "boundary",
        "title": "Boundary",
        "content": "Lore text.",
        "enabled": 1,
        "probability": 1,
        "regex": regex,
        "keys_json": keys_json,
        "secondary_keys_json": secondary_keys_json,
    }

    matched = match_lorebook_entries([entry], "moon REGEX ERROR; REGEX REJECTED")
    modules = modules_from_lore_matches(matched)

    assert [item.entry_id for item in matched.matches] == ["boundary"]
    assert not matched.excluded
    assert matched.matches[0].reason == f"key match: {primary_key}"
    assert [module.content for module in modules] == ["Lore text."]

    missed = match_lorebook_entries([entry], "moon")

    assert not missed.matches
    assert modules_from_lore_matches(missed) == []
    assert [item.reason for item in missed.excluded] == [miss_reason]


@pytest.mark.parametrize("key_position", ("primary", "secondary"))
def test_lorebook_regex_repeat_overflow_is_excluded(key_position):
    """Oversized regex repeats are excluded without dropping a healthy companion."""
    pattern = "a{99999999999999999999}"
    if key_position == "secondary":
        primary_key = "moon"
        keys_json = json.dumps(["moon"])
        secondary_keys_json = json.dumps([pattern])
    else:
        primary_key = pattern
        keys_json = json.dumps([pattern])
        secondary_keys_json = json.dumps([])
    overflow = {
        "id": "overflow",
        "title": "Overflow",
        "content": "Overflow lore",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": keys_json,
        "secondary_keys_json": secondary_keys_json,
    }
    healthy = {
        "id": "healthy",
        "title": "Healthy",
        "content": "Healthy repeat",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": json.dumps(["a{2}"]),
        "secondary_keys_json": json.dumps([]),
    }

    result = match_lorebook_entries([overflow, healthy], "moon aaa")
    modules = modules_from_lore_matches(result)

    assert [(item.entry_id, item.matched) for item in result.matches] == [("healthy", True)]
    assert [module.content for module in modules] == ["Healthy repeat"]
    assert len(result.excluded) == 1
    assert result.excluded[0].entry_id == "overflow"
    assert result.excluded[0].matched is False
    assert result.excluded[0].module is None
    assert result.excluded[0].reason and result.excluded[0].reason.startswith("regex error: ")

    literal = match_lorebook_entries(
        [{
            "id": "literal",
            "title": "Literal",
            "content": "Literal lore",
            "enabled": 1,
            "probability": 1,
            "regex": False,
            "keys_json": keys_json,
            "secondary_keys_json": secondary_keys_json,
        }],
        f"moon aaa {pattern}",
    )
    literal_modules = modules_from_lore_matches(literal)

    assert [(item.entry_id, item.matched, item.reason) for item in literal.matches] == [
        ("literal", True, f"key match: {primary_key}"),
    ]
    assert [module.content for module in literal_modules] == ["Literal lore"]
    assert not literal.excluded


@pytest.mark.parametrize("key_position", ("primary", "secondary"))
def test_lorebook_regex_recursion_error_is_excluded(key_position, monkeypatch):
    """RecursionError from regex search is excluded without dropping a healthy companion."""
    sentinel = "trigger"
    if key_position == "secondary":
        primary_key = "moon"
        keys_json = json.dumps(["moon"])
        secondary_keys_json = json.dumps([sentinel])
    else:
        primary_key = sentinel
        keys_json = json.dumps([sentinel])
        secondary_keys_json = json.dumps([])
    import plugins.hermes_tavern.lorebook as lorebook_module

    real_search = lorebook_module.re.search
    search_calls = {"count": 0}

    def controlled_search(*args, **kwargs):
        search_calls["count"] += 1
        pattern = args[0] if args else kwargs["pattern"]
        if pattern == sentinel:
            raise RecursionError("controlled regex recursion failure")
        return real_search(*args, **kwargs)

    monkeypatch.setattr("plugins.hermes_tavern.lorebook.re.search", controlled_search)
    failing = {
        "id": "failing",
        "title": "Failing",
        "content": "Failing lore",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": keys_json,
        "secondary_keys_json": secondary_keys_json,
    }
    healthy = {
        "id": "healthy",
        "title": "Healthy",
        "content": "Healthy repeat",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": json.dumps(["a{2}"]),
        "secondary_keys_json": json.dumps([]),
    }

    result = match_lorebook_entries([failing, healthy], "moon aaa trigger")
    modules = modules_from_lore_matches(result)

    assert [(item.entry_id, item.matched) for item in result.matches] == [("healthy", True)]
    assert [module.content for module in modules] == ["Healthy repeat"]
    assert len(result.excluded) == 1
    assert result.excluded[0].entry_id == "failing"
    assert result.excluded[0].matched is False
    assert result.excluded[0].module is None
    assert result.excluded[0].reason == "regex error: controlled regex recursion failure"
    assert "excluded Failing: regex error: controlled regex recursion failure" in result.debug

    calls_before_literal = search_calls["count"]
    literal = match_lorebook_entries(
        [{
            "id": "literal",
            "title": "Literal",
            "content": "Literal lore",
            "enabled": 1,
            "probability": 1,
            "regex": False,
            "keys_json": keys_json,
            "secondary_keys_json": secondary_keys_json,
        }],
        "moon aaa trigger",
    )
    literal_modules = modules_from_lore_matches(literal)

    assert search_calls["count"] == calls_before_literal
    assert [(item.entry_id, item.matched, item.reason) for item in literal.matches] == [
        ("literal", True, f"key match: {primary_key}"),
    ]
    assert [module.content for module in literal_modules] == ["Literal lore"]
    assert not literal.excluded


@pytest.mark.parametrize("pattern", ("(?a)(?u)moon", "(?u)(?a)moon"))
@pytest.mark.parametrize("key_position", ("primary", "secondary"))
def test_lorebook_regex_incompatible_inline_flags_are_excluded(pattern, key_position):
    """Incompatible global inline flags are excluded without dropping a healthy companion."""
    if key_position == "secondary":
        primary_key = "moon"
        keys_json = json.dumps(["moon"])
        secondary_keys_json = json.dumps([pattern])
    else:
        primary_key = pattern
        keys_json = json.dumps([pattern])
        secondary_keys_json = json.dumps([])
    incompatible = {
        "id": "incompatible",
        "title": "Incompatible",
        "content": "Incompatible lore",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": keys_json,
        "secondary_keys_json": secondary_keys_json,
    }
    healthy = {
        "id": "healthy",
        "title": "Healthy",
        "content": "Healthy repeat",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": json.dumps(["a{2}"]),
        "secondary_keys_json": json.dumps([]),
    }

    result = match_lorebook_entries([incompatible, healthy], "moon aaa")
    modules = modules_from_lore_matches(result)
    reason = result.excluded[0].reason
    prefix = "regex error: "

    assert [(item.entry_id, item.matched) for item in result.matches] == [("healthy", True)]
    assert [module.content for module in modules] == ["Healthy repeat"]
    assert len(result.excluded) == 1
    assert result.excluded[0].entry_id == "incompatible"
    assert result.excluded[0].matched is False
    assert result.excluded[0].module is None
    assert reason.startswith(prefix)
    assert reason[len(prefix):]
    assert f"excluded Incompatible: {reason}" in result.debug

    literal = match_lorebook_entries(
        [{
            "id": "literal",
            "title": "Literal",
            "content": "Literal lore",
            "enabled": 1,
            "probability": 1,
            "regex": False,
            "keys_json": keys_json,
            "secondary_keys_json": secondary_keys_json,
        }],
        f"moon aaa {pattern}",
    )
    literal_modules = modules_from_lore_matches(literal)

    assert [(item.entry_id, item.matched, item.reason) for item in literal.matches] == [
        ("literal", True, f"key match: {primary_key}"),
    ]
    assert [module.content for module in literal_modules] == ["Literal lore"]
    assert not literal.excluded


@pytest.mark.parametrize("pattern", ("(?a)moon", "(?u)moon", "(?a:moon)(?u:rise)"))
def test_lorebook_regex_valid_inline_flags_match(pattern):
    """Compatible inline flags still match case-insensitively and stay included."""
    entry = {
        "id": "flags",
        "title": "Flags",
        "content": "Flag lore",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": json.dumps([pattern]),
        "secondary_keys_json": json.dumps([]),
    }

    result = match_lorebook_entries([entry], "MOONRISE")
    modules = modules_from_lore_matches(result)

    assert [(item.entry_id, item.matched, item.reason) for item in result.matches] == [
        ("flags", True, f"key match: {pattern}"),
    ]
    assert [module.content for module in modules] == ["Flag lore"]
    assert not result.excluded
    assert not any(item.startswith("regex error: ") for item in result.debug)


def test_lorebook_regex_unexpected_runtime_error_propagates(monkeypatch):
    """Runtime errors outside regex containment propagate unchanged."""
    failure = RuntimeError("unexpected search failure")

    def fail_search(*args, **kwargs):
        raise failure

    monkeypatch.setattr("plugins.hermes_tavern.lorebook.re.search", fail_search)

    with pytest.raises(RuntimeError) as caught:
        match_lorebook_entries(
            [{
                "id": "runtime",
                "title": "Runtime",
                "content": "Runtime lore",
                "enabled": 1,
                "probability": 1,
                "regex": 1,
                "keys_json": json.dumps(["a{2}"]),
                "secondary_keys_json": json.dumps([]),
            }],
            "aaa",
        )

    assert caught.value is failure


@pytest.mark.parametrize("key_position", ("primary", "secondary"))
@pytest.mark.parametrize("malformed_order", ("before", "after"))
def test_lorebook_regex_malformed_key_order_is_excluded(key_position, malformed_order):
    """A malformed regex in the same key list excludes the entry in either order."""
    malformed = "["
    valid = "moon"
    ordered = [malformed, valid] if malformed_order == "before" else [valid, malformed]
    if key_position == "secondary":
        keys_json = json.dumps(["moon"])
        secondary_keys_json = json.dumps(ordered)
    else:
        keys_json = json.dumps(ordered)
        secondary_keys_json = json.dumps([])
    broken = {
        "id": "malformed",
        "title": "Malformed",
        "content": "Malformed lore",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": keys_json,
        "secondary_keys_json": secondary_keys_json,
    }
    healthy = {
        "id": "healthy",
        "title": "Healthy",
        "content": "Healthy repeat",
        "enabled": 1,
        "probability": 1,
        "regex": 1,
        "keys_json": json.dumps(["a{2}"]),
        "secondary_keys_json": json.dumps([]),
    }

    result = match_lorebook_entries([broken, healthy], "moon aaa")
    modules = modules_from_lore_matches(result)
    malformed_excluded = [item for item in result.excluded if item.entry_id == "malformed"]

    assert [(item.entry_id, item.matched) for item in result.matches] == [("healthy", True)]
    assert [module.content for module in modules] == ["Healthy repeat"]
    assert len(result.excluded) == 1
    assert len(malformed_excluded) == 1
    excluded = malformed_excluded[0]
    reason = excluded.reason
    prefix = "regex error: "
    assert excluded.matched is False
    assert excluded.module is None
    assert reason.startswith(prefix)
    assert reason[len(prefix):]
    assert f"excluded Malformed: {reason}" in result.debug


@pytest.mark.parametrize(
    ("keys", "first_key"),
    (
        (("moon", "rises"), "moon"),
        (("rises", "moon"), "rises"),
    ),
)
def test_lorebook_regex_first_matching_key_names_reason(keys, first_key):
    """When several valid regex keys match, the reason names the first matching key."""
    result = match_lorebook_entries(
        [{
            "id": "ordered",
            "title": "Ordered",
            "content": "Ordered lore",
            "enabled": 1,
            "probability": 1,
            "regex": 1,
            "keys_json": json.dumps(list(keys)),
            "secondary_keys_json": json.dumps([]),
        }],
        "The moon rises.",
    )
    modules = modules_from_lore_matches(result)

    assert [(item.entry_id, item.matched, item.reason) for item in result.matches] == [
        ("ordered", True, f"key match: {first_key}"),
    ]
    assert [module.content for module in modules] == ["Ordered lore"]
    assert not result.excluded
