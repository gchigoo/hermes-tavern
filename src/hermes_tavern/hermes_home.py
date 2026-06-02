"""Hermes home path compatibility helpers.

Hermes Tavern normally runs inside Hermes Agent, where ``hermes_constants`` is
available. Standalone packaging/import smoke tests may run before Hermes Agent is
installed, so keep a tiny local fallback that follows the same environment
contract for paths only.
"""

from __future__ import annotations

import os
from pathlib import Path

try:  # pragma: no cover - exercised when installed inside Hermes Agent
    from hermes_constants import get_hermes_home as _get_hermes_home  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - exercised by external smoke tests

    def _get_hermes_home() -> Path:
        return Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))


def get_hermes_home() -> Path:
    """Return the active Hermes home directory as a ``Path``."""

    return Path(_get_hermes_home())
