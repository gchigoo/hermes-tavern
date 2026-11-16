"""SillyTavern character-card parsing."""

from __future__ import annotations

import base64
import copy
import json
import struct
import zlib
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import NAMESPACE_URL, uuid5

from hermes_tavern.importers import MAX_LOCAL_IMPORT_BYTES, assert_local_import_size
from hermes_tavern.provider_bridge import validate_provider_base_url


class UnsupportedCardFormat(ValueError):
    """Raised when a card file format is not supported for import."""


@dataclass(frozen=True)
class CharacterCard:
    id: str
    name: str
    description: str = ""
    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    mes_example: str = ""
    alternate_greetings: list[str] = field(default_factory=list)
    creator_notes: str = ""
    system_prompt_override: str = ""
    post_history_instructions: str = ""
    tags: list[str] = field(default_factory=list)
    talkativeness: float | None = None
    extensions: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _card_id(raw: dict[str, Any], data: dict[str, Any], name: str) -> str:
    explicit = data.get("id") or raw.get("id")
    if explicit:
        return str(explicit)
    stable = json.dumps(raw, sort_keys=True, separators=(",", ":"), default=str)
    return str(uuid5(NAMESPACE_URL, f"hermes-tavern:{name}:{stable}"))


def parse_character_card(raw_card: dict[str, Any]) -> CharacterCard:
    if not isinstance(raw_card, dict):
        raise ValueError("character card must be a JSON object")

    raw = copy.deepcopy(raw_card)
    nested = raw.get("data")
    data = nested if isinstance(nested, dict) else raw
    if not isinstance(data, dict):
        raise ValueError("character card data must be a JSON object")

    name = _text(data.get("name")).strip()
    if not name:
        raise ValueError("character card requires a name")

    alternate = data.get("alternate_greetings") or []
    if not isinstance(alternate, list):
        alternate = []

    tags = data.get("tags") or []
    if not isinstance(tags, list):
        tags = []

    extensions = data.get("extensions") or {}
    if not isinstance(extensions, dict):
        extensions = {}

    raw_talkativeness = data.get("talkativeness")
    talkativeness: float | None = None
    if raw_talkativeness is not None:
        try:
            talkativeness = float(raw_talkativeness)
        except (TypeError, ValueError, OverflowError):
            talkativeness = None

    return CharacterCard(
        id=_card_id(raw, data, name),
        name=name,
        description=_text(data.get("description")),
        personality=_text(data.get("personality")),
        scenario=_text(data.get("scenario")),
        first_mes=_text(data.get("first_mes")),
        mes_example=_text(data.get("mes_example")),
        alternate_greetings=[str(item) for item in alternate],
        creator_notes=_text(data.get("creator_notes")),
        system_prompt_override=_text(
            data.get("system_prompt") or data.get("system_prompt_override")
        ),
        post_history_instructions=_text(data.get("post_history_instructions")),
        tags=[str(t) for t in tags],
        talkativeness=talkativeness,
        extensions=dict(extensions),
        source_path="",
        raw=raw,
    )


_PNG_SIG = b"\x89PNG\r\n\x1a\n"
_UNSUPPORTED_IMAGE_EXTS = {".webp", ".jpg", ".jpeg"}
_MAX_REMOTE_CARD_BYTES = 10 * 1024 * 1024


def _is_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def _display_source_name(source: str | Path) -> str:
    if isinstance(source, Path):
        return source.name
    parsed = urlparse(str(source))
    if parsed.scheme and parsed.netloc:
        return Path(parsed.path).name or parsed.netloc
    return Path(str(source)).name


def _load_card_bytes(data: bytes, suffix: str, source_label: str) -> CharacterCard:
    suffix = suffix.lower()
    if suffix == ".png":
        chara_b64 = _read_png_chara(data)
        if chara_b64 is None:
            raise UnsupportedCardFormat(
                f"No 'chara' metadata found in {source_label}. "
                f"This PNG may not be a SillyTavern character card."
            )
        try:
            raw = json.loads(base64.b64decode(chara_b64, validate=True))
        except Exception as exc:
            raise UnsupportedCardFormat(
                f"Could not decode character data from {source_label}: {exc}"
            ) from exc
        return parse_character_card(raw)
    if suffix == ".json":
        try:
            raw = json.loads(data.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ValueError(f"Invalid UTF-8 in {source_label}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in {source_label}: {exc}") from exc
        return parse_character_card(raw)
    if suffix in _UNSUPPORTED_IMAGE_EXTS:
        raise UnsupportedCardFormat(
            "WebP/JPEG card import is not supported. "
            "Export the card as JSON or PNG from SillyTavern."
        )
    raise UnsupportedCardFormat(
        f"Unsupported file format: {suffix!r}. Only .json and .png files are supported."
    )


def _load_remote_card(source: str) -> CharacterCard:
    try:
        validate_provider_base_url(source)
    except ValueError as exc:
        raise UnsupportedCardFormat(str(exc).replace("Provider URL", "Card URL")) from exc

    parsed = urlparse(source)
    suffix = Path(parsed.path).suffix.lower()
    if not suffix:
        raise UnsupportedCardFormat(
            "Unsupported remote card URL: missing file extension. Only .json and .png URLs are supported."
        )
    if suffix not in {".json", ".png", *_UNSUPPORTED_IMAGE_EXTS}:
        raise UnsupportedCardFormat(
            f"Unsupported file format: {suffix!r}. Only .json and .png files are supported."
        )

    request = Request(source, headers={"User-Agent": "HermesTavern/1.0"})
    try:
        with urlopen(request, timeout=20) as response:
            data = response.read(_MAX_REMOTE_CARD_BYTES + 1)
    except Exception:
        raise UnsupportedCardFormat("Could not download card URL: download failed") from None
    if len(data) > _MAX_REMOTE_CARD_BYTES:
        raise UnsupportedCardFormat("Remote card is too large; maximum supported size is 10 MB.")

    card = _load_card_bytes(data, suffix, _display_source_name(source))
    return replace(card, source_path=source)


def _decompress_itxt_text(payload: bytes) -> bytes | None:
    """Inflate one zlib iTXt text field, or return None when it must be rejected.

    Reads at most ``MAX_LOCAL_IMPORT_BYTES + 1`` decompressed bytes. Oversized,
    truncated, invalid, trailing, or concatenated zlib streams are rejected.
    """
    inflater = zlib.decompressobj()
    try:
        # read one extra byte to detect overflow; avoid unbounded compression-bomb allocation
        text = inflater.decompress(payload, MAX_LOCAL_IMPORT_BYTES + 1)
    except zlib.error:
        return None
    if (
        len(text) > MAX_LOCAL_IMPORT_BYTES
        or inflater.unconsumed_tail
        or not inflater.eof
        or inflater.unused_data
    ):
        return None
    return text


def _read_png_chara(data: bytes) -> str | None:
    """Return the base64 text from a PNG tEXt/iTXt 'chara' chunk, or None."""
    if not data.startswith(_PNG_SIG):
        return None
    pos = 8
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        # length field + type + payload + CRC; equal to len(data) is a complete chunk
        chunk_end = pos + 12 + length
        if chunk_end > len(data):
            return None
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos = chunk_end

        # CRC-check tEXt/iTXt only; a mismatch skips the chunk and keeps scanning for chara
        if chunk_type in (b"tEXt", b"iTXt"):
            (stored_crc,) = struct.unpack(">I", data[chunk_end - 4 : chunk_end])
            if stored_crc != (zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF):
                continue

        if chunk_type == b"tEXt":
            sep = chunk_data.find(b"\x00")
            if sep == -1:
                continue
            if chunk_data[:sep].decode("latin-1") == "chara":
                return chunk_data[sep + 1 :].decode("latin-1")

        elif chunk_type == b"iTXt":
            sep = chunk_data.find(b"\x00")
            if sep == -1:
                continue
            if chunk_data[:sep].decode("latin-1") != "chara":
                continue
            # flag at sep+1, method at sep+2; method is ignored when flag is 0
            if sep + 2 >= len(chunk_data):
                continue
            compression_flag = chunk_data[sep + 1]
            compression_method = chunk_data[sep + 2]
            if compression_flag == 0:
                compressed = False
            elif compression_flag == 1 and compression_method == 0:
                compressed = True
            else:
                continue
            rest = chunk_data[sep + 3 :]  # language tag follows the method byte
            lang_end = rest.find(b"\x00")
            if lang_end == -1:
                continue
            rest = rest[lang_end + 1 :]
            trans_end = rest.find(b"\x00")
            if trans_end == -1:
                continue
            text = rest[trans_end + 1 :]
            if compressed:
                inflated = _decompress_itxt_text(text)
                if inflated is None:
                    continue
                text = inflated
            return text.decode("utf-8", errors="replace")

        elif chunk_type == b"IEND":
            break
    return None


def load_card_file(source: str | Path) -> CharacterCard:
    """Load a CharacterCard from a .json/.png file path, HTTPS URL, or raw JSON text.

    Pass a file path or HTTPS URL ending in .json or .png, or raw JSON text starting with '{'.
    PNG files must contain a SillyTavern tEXt/iTXt 'chara' chunk (base64 JSON).
    WebP/JPEG paths raise UnsupportedCardFormat. Other unknown extensions also raise it.
    """
    if isinstance(source, str) and source.strip().startswith("{"):
        try:
            raw = json.loads(source)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON: {exc}") from exc
        return parse_character_card(raw)

    if isinstance(source, str) and _is_url(source.strip()):
        return _load_remote_card(source.strip())

    path = Path(source)
    suffix = path.suffix.lower()

    if suffix == ".png":
        if not path.exists():
            raise FileNotFoundError(f"Card file not found: {path}")
        assert_local_import_size(
            path,
            label="Character card file",
            error_type=UnsupportedCardFormat,
        )
        card = _load_card_bytes(path.read_bytes(), suffix, path.name)
        return replace(card, source_path=str(path))

    if suffix in _UNSUPPORTED_IMAGE_EXTS:
        raise UnsupportedCardFormat(
            f"WebP/JPEG card import is not supported. "
            f"Export the card as JSON or PNG from SillyTavern."
        )
    if suffix and suffix != ".json":
        raise UnsupportedCardFormat(
            f"Unsupported file format: {suffix!r}. Only .json and .png files are supported."
        )

    if not path.exists():
        raise FileNotFoundError(f"Card file not found: {path}")
    assert_local_import_size(
        path,
        label="Character card file",
        error_type=UnsupportedCardFormat,
    )

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path.name}: {exc}") from exc

    card = parse_character_card(raw)
    return replace(card, source_path=str(path))
