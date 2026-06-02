"""Standalone test compatibility shim.

Adds src/ to sys.path so ``import hermes_tavern`` works, then installs a
MetaPathFinder that makes ``from plugins.hermes_tavern.X import Y`` resolve
to the real source at src/hermes_tavern/X.py.

This file is intentionally thin: all production source stays in src/;
nothing here changes runtime behaviour when the plugin runs inside
hermes-agent.
"""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import os
import sys
from pathlib import Path

_SRC = Path(__file__).parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Stub hermes_constants when it is absent from the host environment (standalone
# CI or a developer checkout without hermes-agent installed).  Only
# get_hermes_home is used by hermes_tavern source files.  When the real module
# IS importable (hermes-agent active) this block is skipped entirely.
try:
    import hermes_constants as _  # noqa: F401
except ModuleNotFoundError:
    import types as _types

    _stub = _types.ModuleType("hermes_constants")
    _stub.get_hermes_home = lambda: Path(  # type: ignore[attr-defined]
        os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))
    )
    sys.modules["hermes_constants"] = _stub
    del _types, _stub

# Stub hermes_cli.config for standalone provider-bridge tests. The monkeypatch
# in those tests replaces get_env_value; the default keeps credentials absent.
try:
    import hermes_cli.config as _  # noqa: F401
except ModuleNotFoundError:
    import types as _types

    _hermes_cli = _types.ModuleType("hermes_cli")
    _config = _types.ModuleType("hermes_cli.config")
    _config.get_env_value = lambda key: None  # type: ignore[attr-defined]
    _hermes_cli.config = _config  # type: ignore[attr-defined]
    sys.modules.setdefault("hermes_cli", _hermes_cli)
    sys.modules.setdefault("hermes_cli.config", _config)
    del _types, _hermes_cli, _config

# Provide the tiny gateway.platforms.base surface used by standalone tests when
# hermes-agent itself is not importable.  Production runs inside hermes-agent use
# the real gateway module; this shim only keeps the extracted public repo's test
# suite self-contained on clean GitHub Actions runners.
try:
    from gateway.platforms.base import BasePlatformAdapter as _  # noqa: F401
except ModuleNotFoundError:
    import re
    import types as _types

    class _BasePlatformAdapter:
        @staticmethod
        def extract_media(content: str):
            media = []
            cleaned = content
            has_voice_tag = "[[audio_as_voice]]" in content
            cleaned = cleaned.replace("[[audio_as_voice]]", "")
            cleaned = cleaned.replace("[[as_document]]", "")
            media_pattern = re.compile(
                r'''[`"']?MEDIA:\s*(?P<path>`[^`\n]+`|"[^"\n]+"|'[^'\n]+'|(?:~/|/)\S+(?:[^\S\n]+\S+)*?\.(?:png|jpe?g|gif|webp|mp4|mov|avi|mkv|webm|ogg|opus|mp3|wav|m4a|flac|epub|pdf|zip|rar|7z|docx?|xlsx?|pptx?|txt|csv|apk|ipa)(?=[\s`"',;:)\]}]|$))[`"']?'''
            )
            for match in media_pattern.finditer(content):
                path = match.group("path").strip()
                if len(path) >= 2 and path[0] == path[-1] and path[0] in "`\"'":
                    path = path[1:-1].strip()
                path = path.lstrip("`\"'").rstrip("`\"',.;:)}]")
                if path:
                    media.append((os.path.expanduser(path), has_voice_tag))
            if media:
                cleaned = media_pattern.sub("", cleaned)
                cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
            return media, cleaned

    _gateway = _types.ModuleType("gateway")
    _platforms = _types.ModuleType("gateway.platforms")
    _base = _types.ModuleType("gateway.platforms.base")
    _base.BasePlatformAdapter = _BasePlatformAdapter  # type: ignore[attr-defined]
    _platforms.base = _base  # type: ignore[attr-defined]
    _gateway.platforms = _platforms  # type: ignore[attr-defined]
    sys.modules.setdefault("gateway", _gateway)
    sys.modules.setdefault("gateway.platforms", _platforms)
    sys.modules.setdefault("gateway.platforms.base", _base)
    del _types, _gateway, _platforms, _base, _BasePlatformAdapter


class _HermesTavernShimFinder(importlib.abc.MetaPathFinder):
    """Redirect ``plugins.hermes_tavern[.submodule]*`` to ``hermes_tavern[.submodule]*``."""

    _SHIM = "plugins.hermes_tavern"
    _REAL = "hermes_tavern"

    def find_spec(self, fullname: str, path, target=None):
        if fullname != self._SHIM and not fullname.startswith(self._SHIM + "."):
            return None
        real_name = self._REAL + fullname[len(self._SHIM):]
        try:
            real_spec = importlib.util.find_spec(real_name)
        except (ModuleNotFoundError, ValueError):
            return None
        if real_spec is None:
            return None
        spec = importlib.machinery.ModuleSpec(
            fullname,
            _AliasLoader(real_name),
            origin=real_spec.origin,
        )
        # Preserve package vs. module distinction so submodule imports work.
        spec.submodule_search_locations = real_spec.submodule_search_locations
        return spec


class _AliasLoader(importlib.abc.Loader):
    """Load a shim name by pointing it at the already-loaded real module."""

    def __init__(self, real_name: str) -> None:
        self._real = real_name

    def create_module(self, spec):
        return None  # use Python's default module object

    def exec_module(self, module) -> None:
        real_mod = importlib.import_module(self._real)
        # Replace the freshly-created shim module with the canonical real module
        # so identity checks (isinstance, is, id) work across both import paths.
        sys.modules[module.__spec__.name] = real_mod


if not any(isinstance(f, _HermesTavernShimFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, _HermesTavernShimFinder())
