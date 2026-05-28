"""Shared utilities for Hermes Tavern."""

from __future__ import annotations


def estimate_tokens(text: str) -> int:
    """Approximate token count using a 4-chars-per-token heuristic.

    Returns at least 1 so callers never divide-by-zero on empty input.
    Phase 4 can swap this for a tiktoken-based implementation without
    changing any call sites.
    """
    return max(1, len(text) // 4)
