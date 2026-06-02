"""Compatibility package for legacy ``plugins.hermes_tavern`` imports.

The standalone project keeps production source in ``src/hermes_tavern`` while
older tests and Hermes plugin-loading paths import ``plugins.hermes_tavern``.
This package is intentionally thin: it exposes the real package path so Python
can load submodules from ``src/hermes_tavern`` without copying source files.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

_real = importlib.import_module("hermes_tavern")

# Let imports such as ``plugins.hermes_tavern.runtime`` resolve against the
# canonical standalone source directory.
__path__ = list(getattr(_real, "__path__", []))
__all__ = list(getattr(_real, "__all__", []))


def __getattr__(name: str):
    return getattr(_real, name)


# Keep the plugin entry point available on the legacy package object.
register = _real.register
