import base64
import json
import struct
import zlib
from pathlib import Path

import pytest

from plugins.hermes_tavern.importers.cards import (
    UnsupportedCardFormat,
    _read_png_chara,
    load_card_file,
    parse_character_card,
)
from plugins.hermes_tavern.importers import MAX_LOCAL_IMPORT_BYTES


def _make_png_with_chara(card_json: dict) -> bytes:
    """Minimal PNG bytes with a tEXt 'chara' chunk containing base64-encoded card JSON."""
    chara_b64 = base64.b64encode(json.dumps(card_json).encode()).decode("latin-1")
    chunk_data = b"chara\x00" + chara_b64.encode("latin-1")

    def chunk(type_: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(type_ + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + type_ + data + struct.pack(">I", crc)

    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr_data)
        + chunk(b"tEXt", chunk_data)
        + chunk(b"IEND", b"")
    )


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    """Return a length-prefixed PNG chunk with its CRC."""
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def _png_with_chunks(*chunks: tuple[bytes, bytes]) -> bytes:
    """Return a complete 1x1 truecolor PNG with chunks between IHDR and IDAT."""
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    # Filter 0 (None) plus one black RGB pixel. IDAT must precede IEND.
    idat = zlib.compress(b"\x00\x00\x00\x00")
    parts = [b"\x89PNG\r\n\x1a\n", _png_chunk(b"IHDR", ihdr)]
    parts.extend(_png_chunk(chunk_type, data) for chunk_type, data in chunks)
    parts.append(_png_chunk(b"IDAT", idat))
    parts.append(_png_chunk(b"IEND", b""))
    return b"".join(parts)


def _itxt_chara_payload(
    card_json: dict | None = None,
    *,
    language: str = "",
    translated_keyword: str = "",
    compression_flag: int = 0,
    compression_method: int = 0,
    text: bytes | None = None,
) -> bytes:
    """Return iTXt data for keyword 'chara'.

    Language is Latin-1. Translated keyword and text are UTF-8.
    When text is omitted, the text field is base64 JSON of card_json, and a
    non-zero compression flag zlib-compresses that generated field. Pass text
    to set the field bytes directly, including precompressed or malformed data.
    compression_method is the iTXt method byte; 0 means zlib.
    """
    if text is None:
        if card_json is None:
            raise ValueError("card_json is required when text is omitted")
        text = base64.b64encode(json.dumps(card_json).encode("utf-8"))
        if compression_flag:
            text = zlib.compress(text)
    return (
        b"chara\x00"
        + bytes((compression_flag, compression_method))
        + language.encode("latin-1")
        + b"\x00"
        + translated_keyword.encode("utf-8")
        + b"\x00"
        + text
    )


def _png_with_compressed_itxt_text(raw_text: bytes) -> bytes:
    """Return a 1x1 PNG whose iTXt chara text inflates to raw_text."""
    payload = _itxt_chara_payload(
        language="en",
        translated_keyword="角色",
        compression_flag=1,
        compression_method=0,
        text=zlib.compress(raw_text),
    )
    return _png_with_chunks((b"iTXt", payload))


_PNG_CHUNK_BOUNDS_CARD = {"name": "Bounds"}
_PNG_CHUNK_BOUNDS_B64 = base64.b64encode(
    json.dumps(_PNG_CHUNK_BOUNDS_CARD).encode("utf-8")
).decode("ascii")


def _png_chunk_bounds_chara_chunk(form: str) -> bytes:
    """Return one CRC-complete chara chunk: tEXt, iTXt, or compressed iTXt.

    The text field is the same base64 JSON in every form. Callers truncate
    the returned bytes to drop physical CRC bytes without altering the CRC value.
    """
    if form == "tEXt":
        text = _PNG_CHUNK_BOUNDS_B64.encode("ascii")
        return _png_chunk(b"tEXt", b"chara\x00" + text)
    if form == "iTXt":
        return _png_chunk(b"iTXt", _itxt_chara_payload(_PNG_CHUNK_BOUNDS_CARD))
    if form == "iTXt-compressed":
        payload = _itxt_chara_payload(
            _PNG_CHUNK_BOUNDS_CARD,
            language="en",
            translated_keyword="角色",
            compression_flag=1,
            compression_method=0,
        )
        return _png_chunk(b"iTXt", payload)
    raise ValueError(f"unknown chara chunk form: {form}")


def _png_chunk_flip_final_crc_bit(chunk: bytes) -> bytes:
    """Return chunk with one bit flipped in its final CRC byte."""
    return chunk[:-1] + bytes((chunk[-1] ^ 0x01,))


FIXTURES = Path(__file__).parent / "fixtures" / "cards"


def test_parse_v2_character_card_preserves_core_fields():
    raw = {
        "spec": "chara_card_v2",
        "data": {
            "name": "Alice",
            "description": "A curious scholar.",
            "personality": "Warm and direct",
            "scenario": "A quiet library",
            "first_mes": "Welcome back.",
            "mes_example": "<START>",
            "alternate_greetings": ["Good evening."],
            "creator_notes": "Test card",
        },
    }

    card = parse_character_card(raw)

    assert card.name == "Alice"
    assert card.description == "A curious scholar."
    assert card.personality == "Warm and direct"
    assert card.scenario == "A quiet library"
    assert card.first_mes == "Welcome back."
    assert card.mes_example == "<START>"
    assert card.alternate_greetings == ["Good evening."]
    assert card.creator_notes == "Test card"
    assert card.raw == raw
    assert card.id


def test_parse_direct_character_card():
    card = parse_character_card({"name": "Bob", "description": "Direct card"})

    assert card.name == "Bob"
    assert card.description == "Direct card"


def test_parse_character_card_requires_name():
    with pytest.raises(ValueError, match="name"):
        parse_character_card({"description": "No name"})


def test_parse_character_card_copies_raw_json():
    raw = {"name": "Alice"}

    card = parse_character_card(raw)
    raw["name"] = "Changed"

    assert card.raw == {"name": "Alice"}


def test_parse_v3_character_card_uses_nested_data():
    raw = {
        "spec": "chara_card_v3",
        "spec_version": "3.0",
        "data": {
            "name": "Seraphine",
            "description": "A wandering minstrel.",
            "personality": "Carefree",
            "scenario": "A bustling inn",
            "first_mes": "Good evening, traveler.",
            "mes_example": "<START>",
            "system_prompt": "You are Seraphine, a bard.",
            "post_history_instructions": "Stay in character.",
            "alternate_greetings": ["Hello there!", "Well met!"],
            "tags": ["bard", "fantasy"],
            "creator_notes": "v3 test card",
        },
        # top-level legacy fields that are empty (as real v3 cards often have)
        "name": "",
        "description": "",
        "first_mes": "",
    }

    card = parse_character_card(raw)

    assert card.name == "Seraphine"
    assert card.description == "A wandering minstrel."
    assert card.first_mes == "Good evening, traveler."
    assert card.system_prompt_override == "You are Seraphine, a bard."
    assert card.post_history_instructions == "Stay in character."
    assert card.alternate_greetings == ["Hello there!", "Well met!"]
    assert card.tags == ["bard", "fantasy"]
    assert card.creator_notes == "v3 test card"
    assert card.raw == raw


def test_parse_v3_png_card_uses_nested_data(tmp_path):
    raw = {
        "spec": "chara_card_v3",
        "data": {
            "name": "Mira",
            "system_prompt": "Be Mira.",
            "post_history_instructions": "Remain in character.",
            "alternate_greetings": ["Greetings!", "Salutations!"],
        },
        "name": "",
    }
    png_path = tmp_path / "mira.png"
    png_path.write_bytes(_make_png_with_chara(raw))

    card = load_card_file(png_path)

    assert card.name == "Mira"
    assert card.system_prompt_override == "Be Mira."
    assert card.post_history_instructions == "Remain in character."
    assert card.alternate_greetings == ["Greetings!", "Salutations!"]


def test_parse_v3_json_file_uses_nested_data(tmp_path):
    raw = {
        "spec": "chara_card_v3",
        "data": {
            "name": "Thorn",
            "description": "A rogue.",
            "system_prompt": "Play Thorn.",
            "alternate_greetings": ["Shadow greets you."],
        },
    }
    card_file = tmp_path / "thorn.json"
    card_file.write_text(json.dumps(raw))

    card = load_card_file(card_file)

    assert card.name == "Thorn"
    assert card.description == "A rogue."
    assert card.system_prompt_override == "Play Thorn."
    assert card.alternate_greetings == ["Shadow greets you."]
    assert card.source_path == str(card_file)


def test_parse_v2_extended_fields():
    raw = {
        "spec": "chara_card_v2",
        "data": {
            "name": "X",
            "system_prompt": "Be X.",
            "post_history_instructions": "Stay.",
            "tags": ["a", "b"],
            "talkativeness": 0.5,
            "extensions": {"k": 1},
        },
    }

    card = parse_character_card(raw)

    assert card.system_prompt_override == "Be X."
    assert card.post_history_instructions == "Stay."
    assert card.tags == ["a", "b"]
    assert card.talkativeness == 0.5
    assert card.extensions == {"k": 1}
    assert card.source_path == ""


def test_parse_extended_fields_missing_defaults_to_empty():
    card = parse_character_card({"name": "Minimal"})

    assert card.system_prompt_override == ""
    assert card.post_history_instructions == ""
    assert card.tags == []
    assert card.talkativeness is None
    assert card.extensions == {}
    assert card.source_path == ""


def test_parse_talkativeness_invalid_value_becomes_none():
    card = parse_character_card({"name": "T", "talkativeness": "not-a-number"})

    assert card.talkativeness is None


@pytest.mark.parametrize("talkativeness", [10**400, -(10**400)])
@pytest.mark.parametrize("nested", [False, True], ids=["direct", "nested"])
def test_parse_talkativeness_overflow_becomes_none(talkativeness: int, nested: bool):
    """Huge optional talkativeness integers become None and leave raw metadata intact."""
    fields = {"name": "Overflow", "talkativeness": talkativeness}
    raw = {"spec": "chara_card_v2", "data": fields} if nested else fields
    snapshot = json.loads(json.dumps(raw))

    parsed = parse_character_card(raw)
    loaded = load_card_file(json.dumps(raw))

    assert raw == snapshot
    for card in (parsed, loaded):
        assert card.name == "Overflow"
        assert card.talkativeness is None
        assert card.raw == snapshot


def test_parse_fixture_st_v2():
    raw = json.loads((FIXTURES / "st_v2.json").read_text())

    card = parse_character_card(raw)

    assert card.name == "Lyra"
    assert card.system_prompt_override != ""
    assert "bard" in card.tags
    assert card.talkativeness == 0.8
    assert card.extensions.get("world") == "Aldenmere"


def test_parse_fixture_direct():
    raw = json.loads((FIXTURES / "direct.json").read_text())

    card = parse_character_card(raw)

    assert card.name == "Gareth"
    assert "blacksmith" in card.tags
    assert card.talkativeness == 0.2


# --- load_card_file ---


def test_load_card_file_from_json_file(tmp_path):
    card_file = tmp_path / "alice.json"
    card_file.write_text(json.dumps({"name": "Alice", "description": "Scholar"}))

    card = load_card_file(card_file)

    assert card.name == "Alice"
    assert card.source_path == str(card_file)


def test_load_card_file_sets_source_path_to_resolved_path(tmp_path):
    card_file = tmp_path / "bob.json"
    card_file.write_text(json.dumps({"name": "Bob"}))

    card = load_card_file(card_file)

    assert card.source_path == str(card_file)


def test_load_card_file_from_raw_json_text():
    card = load_card_file('{"name": "Inline"}')

    assert card.name == "Inline"
    assert card.source_path == ""


def test_load_card_file_invalid_json_raises_value_error(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json at all")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_card_file(bad_file)


def test_load_card_file_rejects_oversize_json_local(tmp_path):
    card_file = tmp_path / "oversize.json"
    payload = {"name": "Alice", "description": "A" * (MAX_LOCAL_IMPORT_BYTES + 1)}
    payload_text = json.dumps(payload)
    assert len(payload_text.encode("utf-8")) > MAX_LOCAL_IMPORT_BYTES
    card_file.write_text(payload_text, encoding="utf-8")

    with pytest.raises(UnsupportedCardFormat, match="too large"):
        load_card_file(card_file)


def test_load_card_file_raw_invalid_json_raises_value_error():
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_card_file("{not valid json}")


def test_load_card_file_png_with_chara_returns_card(tmp_path):
    png_path = tmp_path / "alice.png"
    png_path.write_bytes(_make_png_with_chara({"name": "Alice", "description": "Scholar"}))

    card = load_card_file(png_path)

    assert card.name == "Alice"
    assert card.description == "Scholar"
    assert card.source_path == str(png_path)


def test_load_card_file_rejects_oversize_png_local(tmp_path):
    png_path = tmp_path / "oversize.png"
    signature = b"\x89PNG\r\n\x1a\n"
    png_path.write_bytes(signature + b"0" * (MAX_LOCAL_IMPORT_BYTES + 1 - len(signature)))

    with pytest.raises(UnsupportedCardFormat, match="too large"):
        load_card_file(png_path)


def test_load_card_file_png_with_chara_v2_returns_card(tmp_path):
    raw = {"spec": "chara_card_v2", "data": {"name": "Lyra", "first_mes": "Hi!"}}
    png_path = tmp_path / "lyra.png"
    png_path.write_bytes(_make_png_with_chara(raw))

    card = load_card_file(png_path)

    assert card.name == "Lyra"
    assert card.first_mes == "Hi!"
    assert card.source_path == str(png_path)


@pytest.mark.parametrize("compression_method", [0, 1, 255])
def test_load_card_file_png_itxt_empty_language_returns_card(
    tmp_path,
    compression_method: int,
):
    """Uncompressed iTXt with empty language ignores the method byte."""
    png_path = tmp_path / "empty-lang.png"
    payload = _itxt_chara_payload(
        {"name": "Ita", "description": "Empty tags"},
        language="",
        translated_keyword="",
        compression_flag=0,
        compression_method=compression_method,
    )
    png_path.write_bytes(_png_with_chunks((b"iTXt", payload)))

    card = load_card_file(png_path)

    assert card.name == "Ita"
    assert card.description == "Empty tags"
    assert card.source_path == str(png_path)


def test_load_card_file_png_itxt_populated_language_returns_card(tmp_path):
    """Uncompressed iTXt with a language tag and translated keyword."""
    png_path = tmp_path / "populated-lang.png"
    payload = _itxt_chara_payload(
        {"name": "Nia", "description": "Tagged"},
        language="en",
        translated_keyword="角色",
    )
    png_path.write_bytes(_png_with_chunks((b"iTXt", payload)))

    card = load_card_file(png_path)

    assert card.name == "Nia"
    assert card.description == "Tagged"
    assert card.source_path == str(png_path)


def test_load_card_file_png_itxt_truncated_raises_unsupported(tmp_path):
    """iTXt cut off before the translated-keyword separator is not a card."""
    text = base64.b64encode(json.dumps({"name": "Cut"}).encode("utf-8"))
    # keyword, flag, method, empty-language null, then text with no keyword null
    payload = b"chara\x00\x00\x00\x00" + text
    png_path = tmp_path / "truncated.png"
    png_path.write_bytes(_png_with_chunks((b"iTXt", payload)))

    with pytest.raises(UnsupportedCardFormat, match="No 'chara' metadata"):
        load_card_file(png_path)


def test_load_card_file_png_itxt_compressed_returns_card(tmp_path):
    """Compressed iTXt chara (flag 1, method 0) loads a card."""
    png_path = tmp_path / "compressed.png"
    payload = _itxt_chara_payload(
        {"name": "Zip", "description": "Compressed"},
        language="en",
        translated_keyword="角色",
        compression_flag=1,
        compression_method=0,
    )
    png_path.write_bytes(_png_with_chunks((b"iTXt", payload)))

    card = load_card_file(png_path)

    assert card.name == "Zip"
    assert card.description == "Compressed"
    assert card.source_path == str(png_path)


_UNCOMPRESSED_CHARA_TEXT = base64.b64encode(
    json.dumps({"name": "Nope", "description": "Rejected"}).encode("utf-8")
)
_COMPRESSED_CHARA_TEXT = zlib.compress(_UNCOMPRESSED_CHARA_TEXT)


@pytest.mark.parametrize(
    ("compression_flag", "compression_method", "text"),
    [
        pytest.param(2, 0, _COMPRESSED_CHARA_TEXT, id="invalid-compression-flag"),
        pytest.param(1, 1, _COMPRESSED_CHARA_TEXT, id="compression-method-not-zero"),
        pytest.param(1, 0, b"not-a-zlib-stream", id="invalid-zlib"),
        pytest.param(1, 0, _COMPRESSED_CHARA_TEXT[:-1], id="truncated-zlib"),
        pytest.param(1, 0, _COMPRESSED_CHARA_TEXT + b"trailing", id="trailing-bytes"),
    ],
)
def test_load_card_file_png_itxt_malformed_compressed_rejected(
    tmp_path,
    compression_flag: int,
    compression_method: int,
    text: bytes,
):
    """Malformed iTXt chara chunks expose no usable metadata."""
    png_path = tmp_path / "bad-compressed.png"
    payload = _itxt_chara_payload(
        language="en",
        translated_keyword="角色",
        compression_flag=compression_flag,
        compression_method=compression_method,
        text=text,
    )
    png_path.write_bytes(_png_with_chunks((b"iTXt", payload)))

    with pytest.raises(UnsupportedCardFormat, match="No 'chara' metadata"):
        load_card_file(png_path)


def test_read_png_chara_accepts_decompressed_text_at_byte_limit():
    """Decompressed iTXt text of exactly MAX_LOCAL_IMPORT_BYTES is returned."""
    decoded = _read_png_chara(
        _png_with_compressed_itxt_text(b"A" * MAX_LOCAL_IMPORT_BYTES)
    )
    assert decoded is not None
    length = len(decoded)
    head = decoded[:4]
    tail = decoded[-4:]
    mark_count = decoded.count("A")
    assert length == MAX_LOCAL_IMPORT_BYTES
    assert head == "AAAA"
    assert tail == "AAAA"
    assert mark_count == length


def test_read_png_chara_rejects_decompressed_text_over_byte_limit():
    """Decompressed iTXt text one byte over MAX_LOCAL_IMPORT_BYTES is ignored."""
    decoded = _read_png_chara(
        _png_with_compressed_itxt_text(b"A" * (MAX_LOCAL_IMPORT_BYTES + 1))
    )
    assert decoded is None


_PNG_CHUNK_BOUNDS_FORMS = [
    pytest.param("tEXt", id="tEXt"),
    pytest.param("iTXt", id="iTXt-uncompressed"),
    pytest.param("iTXt-compressed", id="iTXt-compressed"),
]


@pytest.mark.parametrize("form", _PNG_CHUNK_BOUNDS_FORMS)
@pytest.mark.parametrize("dropped_crc_bytes", [1, 2, 3, 4])
def test_read_png_chara_png_chunk_bounds_missing_crc_returns_none(
    form: str,
    dropped_crc_bytes: int,
):
    """A chara chunk missing 1 to 4 physical CRC bytes is not metadata."""
    chunk = _png_chunk_bounds_chara_chunk(form)
    data = b"\x89PNG\r\n\x1a\n" + chunk[:-dropped_crc_bytes]
    assert _read_png_chara(data) is None


@pytest.mark.parametrize("length_mode", ["one-over-available", "ffffffff"])
def test_read_png_chara_png_chunk_bounds_oversize_length_returns_none(length_mode: str):
    """A declared payload past the buffer, including 0xffffffff, yields None."""
    payload = b"chara\x00" + _PNG_CHUNK_BOUNDS_B64.encode("ascii")
    available = len(payload)
    declared = available + 1 if length_mode == "one-over-available" else 0xFFFFFFFF
    data = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", declared) + b"tEXt" + payload
    assert _read_png_chara(data) is None


@pytest.mark.parametrize("form", _PNG_CHUNK_BOUNDS_FORMS)
def test_read_png_chara_png_chunk_bounds_exact_eof(form: str):
    """A standalone chara chunk ending at EOF decodes; one byte short does not."""
    data = b"\x89PNG\r\n\x1a\n" + _png_chunk_bounds_chara_chunk(form)
    assert _read_png_chara(data) == _PNG_CHUNK_BOUNDS_B64
    assert _read_png_chara(data[:-1]) is None


@pytest.mark.parametrize("form", _PNG_CHUNK_BOUNDS_FORMS)
def test_read_png_chara_png_chunk_bounds_bad_crc_returns_none(form: str):
    """A complete chara chunk with one flipped CRC bit is not metadata."""
    chunk = _png_chunk_flip_final_crc_bit(_png_chunk_bounds_chara_chunk(form))
    data = b"\x89PNG\r\n\x1a\n" + chunk
    assert _read_png_chara(data) is None


@pytest.mark.parametrize("form", _PNG_CHUNK_BOUNDS_FORMS)
def test_read_png_chara_png_chunk_bounds_bad_crc_returns_later_chara(form: str):
    """A bad-CRC chara chunk before a valid one yields the later base64 payload."""
    later_card = {"name": "Later"}
    later_b64 = base64.b64encode(json.dumps(later_card).encode("utf-8")).decode("ascii")
    if form == "tEXt":
        later_chunk = _png_chunk(b"tEXt", b"chara\x00" + later_b64.encode("ascii"))
    elif form == "iTXt":
        later_chunk = _png_chunk(b"iTXt", _itxt_chara_payload(later_card))
    elif form == "iTXt-compressed":
        later_chunk = _png_chunk(
            b"iTXt",
            _itxt_chara_payload(
                later_card,
                language="en",
                translated_keyword="角色",
                compression_flag=1,
                compression_method=0,
            ),
        )
    else:
        raise ValueError(f"unknown chara chunk form: {form}")
    bad_chunk = _png_chunk_flip_final_crc_bit(_png_chunk_bounds_chara_chunk(form))
    data = b"\x89PNG\r\n\x1a\n" + bad_chunk + later_chunk
    assert _read_png_chara(data) == later_b64


def test_load_card_file_png_chunk_bounds_truncated_raises_unsupported(tmp_path):
    """A PNG whose chara chunk stops one byte early has no readable metadata."""
    png_path = tmp_path / "truncated-chara.png"
    data = b"\x89PNG\r\n\x1a\n" + _png_chunk_bounds_chara_chunk("tEXt")
    png_path.write_bytes(data[:-1])

    with pytest.raises(UnsupportedCardFormat, match="No 'chara' metadata"):
        load_card_file(png_path)


@pytest.mark.parametrize("form", _PNG_CHUNK_BOUNDS_FORMS)
def test_load_card_file_png_chunk_bounds_bad_crc_raises_unsupported(tmp_path, form: str):
    """A PNG whose only chara chunk has a bad CRC has no readable metadata."""
    png_path = tmp_path / "bad-crc-chara.png"
    chunk = _png_chunk_flip_final_crc_bit(_png_chunk_bounds_chara_chunk(form))
    png_path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk)

    with pytest.raises(UnsupportedCardFormat, match="No 'chara' metadata"):
        load_card_file(png_path)


def test_load_card_file_png_missing_chara_raises_unsupported(tmp_path):
    # Valid PNG signature but no chara chunk
    png_path = tmp_path / "card.png"
    png_path.write_bytes(b"\x89PNG\r\n\x1a\n")

    with pytest.raises(UnsupportedCardFormat, match="No 'chara' metadata"):
        load_card_file(png_path)


def test_load_card_file_png_malformed_base64_raises_unsupported(tmp_path):
    # tEXt chunk with 'chara' keyword but garbage base64
    def chunk(type_: bytes, data: bytes) -> bytes:
        import zlib
        crc = zlib.crc32(type_ + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + type_ + data + struct.pack(">I", crc)

    chunk_data = b"chara\x00!!!not-valid-base64!!!"
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr_data)
        + chunk(b"tEXt", chunk_data)
        + chunk(b"IEND", b"")
    )
    png_path = tmp_path / "bad.png"
    png_path.write_bytes(png_bytes)

    with pytest.raises(UnsupportedCardFormat, match="Could not decode"):
        load_card_file(png_path)


def test_load_card_file_png_valid_base64_invalid_json_raises_unsupported(tmp_path):
    # base64-encodes "not json"
    bad_b64 = base64.b64encode(b"not json at all").decode()
    chunk_data = b"chara\x00" + bad_b64.encode("latin-1")

    def chunk(type_: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(type_ + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + type_ + data + struct.pack(">I", crc)

    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr_data)
        + chunk(b"tEXt", chunk_data)
        + chunk(b"IEND", b"")
    )
    png_path = tmp_path / "badjson.png"
    png_path.write_bytes(png_bytes)

    with pytest.raises(UnsupportedCardFormat, match="Could not decode"):
        load_card_file(png_path)


def test_load_card_file_webp_raises_unsupported(tmp_path):
    webp_path = tmp_path / "card.webp"
    webp_path.write_bytes(b"RIFF")

    with pytest.raises(UnsupportedCardFormat, match="WebP/JPEG"):
        load_card_file(webp_path)


def test_load_card_file_jpg_raises_unsupported(tmp_path):
    jpg_path = tmp_path / "card.jpg"
    jpg_path.write_bytes(b"\xff\xd8\xff")

    with pytest.raises(UnsupportedCardFormat, match="WebP/JPEG"):
        load_card_file(jpg_path)


class _FakeUrlResponse:
    def __init__(self, data: bytes):
        self._data = data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, limit: int) -> bytes:
        return self._data[:limit]


def test_load_card_file_https_json_url(monkeypatch):
    payload = json.dumps({"name": "Remote Alice", "description": "URL card"}).encode()

    def fake_urlopen(request, timeout):
        assert request.full_url == "https://example.com/cards/alice.json"
        assert timeout == 20
        return _FakeUrlResponse(payload)

    monkeypatch.setattr("plugins.hermes_tavern.importers.cards.urlopen", fake_urlopen)

    card = load_card_file("https://example.com/cards/alice.json")

    assert card.name == "Remote Alice"
    assert card.description == "URL card"
    assert card.source_path == "https://example.com/cards/alice.json"


def test_load_card_file_https_url_download_error_does_not_leak_secret(monkeypatch):
    def fake_urlopen(request, timeout):
        raise RuntimeError("TLS handshake failed for https://example.com/cards/alice.json?token=SECRET")

    monkeypatch.setattr("plugins.hermes_tavern.importers.cards.urlopen", fake_urlopen)

    with pytest.raises(UnsupportedCardFormat) as exc_info:
        load_card_file("https://example.com/cards/alice.json?token=SECRET")

    msg = str(exc_info.value)
    assert msg == "Could not download card URL: download failed"
    assert "SECRET" not in msg
    assert "token=SECRET" not in msg
    assert "https://example.com/cards/alice.json" not in msg


def test_load_card_file_https_png_url(monkeypatch):
    payload = _make_png_with_chara({"name": "Remote Bob", "first_mes": "Hi"})

    def fake_urlopen(request, timeout):
        return _FakeUrlResponse(payload)

    monkeypatch.setattr("plugins.hermes_tavern.importers.cards.urlopen", fake_urlopen)

    card = load_card_file("https://example.com/cards/bob.png")

    assert card.name == "Remote Bob"
    assert card.first_mes == "Hi"
    assert card.source_path == "https://example.com/cards/bob.png"


def test_load_card_file_rejects_insecure_url_without_download(monkeypatch):
    def fake_urlopen(request, timeout):
        raise AssertionError("urlopen should not be called")

    monkeypatch.setattr("plugins.hermes_tavern.importers.cards.urlopen", fake_urlopen)

    with pytest.raises(UnsupportedCardFormat, match="Card URL not allowed"):
        load_card_file("http://example.com/cards/alice.json")


def test_load_card_file_remote_png_without_chara_is_friendly(monkeypatch):
    def fake_urlopen(request, timeout):
        return _FakeUrlResponse(b"\x89PNG\r\n\x1a\n")

    monkeypatch.setattr("plugins.hermes_tavern.importers.cards.urlopen", fake_urlopen)

    with pytest.raises(UnsupportedCardFormat, match="No 'chara' metadata found"):
        load_card_file("https://example.com/cards/not-a-card.PNG")


def test_load_card_file_unknown_extension_raises_unsupported(tmp_path):
    weird = tmp_path / "card.yaml"
    weird.write_text("name: Alice")

    with pytest.raises(UnsupportedCardFormat, match="Unsupported file format"):
        load_card_file(weird)


def test_load_card_file_missing_file_raises_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_card_file(tmp_path / "nonexistent.json")
