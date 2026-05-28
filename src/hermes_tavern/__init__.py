"""Hermes Tavern plugin entry point."""

from __future__ import annotations


def register(ctx) -> None:
    """Register Hermes Tavern gateway hooks."""
    from plugins.hermes_tavern.gateway_hook import pre_gateway_dispatch

    ctx.register_hook("pre_gateway_dispatch", pre_gateway_dispatch)
