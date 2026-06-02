"""Hermes Tavern plugin entry point."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _pkg_version

try:
    __version__: str = _pkg_version("hermes-tavern")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"


def register(ctx) -> None:
    """Register Hermes Tavern gateway hooks."""
    from hermes_tavern.gateway_hook import pre_gateway_dispatch

    ctx.register_hook("pre_gateway_dispatch", pre_gateway_dispatch)
