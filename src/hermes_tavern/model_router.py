"""Model routing skeleton for Hermes Tavern.

Returns a secret-free ModelProfileDescriptor. No resolve_runtime_provider import;
real credential resolution happens outside this module at call time.

Priority order (Phase 4 stubs tiers 1 and 3; tier 2 is the effective default):
  1. claude-subscription adapter   — skipped (no registry hook yet)
  2. anthropic / claude-opus-4-6   — default
  3. openrouter / custom profile   — skipped (no profile in DB for Phase 4)
  4. hermes_global fallback        — used if session has no card/profile at all
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import Any

_DEBUG_OMIT: frozenset[str] = frozenset(
    {"api_key", "access_token", "secret", "token", "password"}
)

_DEFAULT_MODEL_ID = "claude-opus-4-6"
_DEFAULT_PROVIDER = "anthropic"
_DEFAULT_CONTEXT_WINDOW = 200_000


@dataclass(frozen=True)
class ModelProfileDescriptor:
    """Routing metadata only — never carries api_key or access_token."""

    provider: str
    model_id: str
    mode: str           # "chat" | "completion"
    context_window: int
    source: str         # "db_profile" | "default_priority_2" | "hermes_global"
    profile_name: str = "opus-4.6-default"

    def to_debug_dict(self) -> dict[str, Any]:
        """Return a plain dict of routing metadata, omitting any secret fields."""
        d = dataclasses.asdict(self)
        for k in list(d):
            if k in _DEBUG_OMIT:
                d.pop(k)
        return d


class ModelRouter:
    def resolve(
        self,
        session_row: dict[str, Any] | None = None,
        store: Any = None,
    ) -> ModelProfileDescriptor:
        # Tier 1: claude-subscription adapter — not yet wired, always skipped.

        # Tier DB: session has an explicit model_profile_id → look it up.
        if session_row and store:
            profile_id = session_row.get("model_profile_id")
            if profile_id:
                row = _fetch_profile(store, profile_id)
                if row:
                    return _descriptor_from_row(row)

        # Tier 3: openrouter / custom profile — not yet wired, always skipped.

        # Tier 2: anthropic / claude-opus-4-6 (effective Phase 4 default).
        return ModelProfileDescriptor(
            provider=_DEFAULT_PROVIDER,
            model_id=_DEFAULT_MODEL_ID,
            mode="chat",
            context_window=_DEFAULT_CONTEXT_WINDOW,
            source="default_priority_2",
            profile_name="opus-4.6-default",
        )


def _fetch_profile(store: Any, profile_id: str) -> dict[str, Any] | None:
    if hasattr(store, "get_model_profile"):
        return store.get_model_profile(profile_id)
    try:
        with store.connect() as conn:
            row = conn.execute(
                "SELECT * FROM model_profiles WHERE id = ?", (profile_id,)
            ).fetchone()
        return dict(row) if row else None
    except Exception:
        return None


def _descriptor_from_row(row: dict[str, Any]) -> ModelProfileDescriptor:
    raw = row.get("raw_json") or "{}"
    extra: dict[str, Any] = {}
    try:
        extra = json.loads(raw)
    except Exception:
        pass
    return ModelProfileDescriptor(
        provider=row.get("provider", _DEFAULT_PROVIDER),
        model_id=row.get("model_id", _DEFAULT_MODEL_ID),
        mode=row.get("mode", extra.get("mode", "chat")),
        context_window=int(row.get("context_window", _DEFAULT_CONTEXT_WINDOW)),
        source="db_profile",
        profile_name=row.get("name", "custom"),
    )
