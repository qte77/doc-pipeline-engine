# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Shared Anthropic client helpers for V1 stages.

The ``anthropic`` import is deferred so V1 stage modules load without the
optional ``v1`` extra. Tests inject stub clients via the ``client`` kwarg;
real Anthropic calls happen only in integration tests.
"""
from __future__ import annotations

import json
from typing import Any, Protocol

MODEL_DEFAULT = "claude-opus-4-7"
MAX_TOKENS = 4096


class _MessagesAPI(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


class _ClaudeClient(Protocol):
    messages: _MessagesAPI


def make_client() -> _ClaudeClient:
    """Instantiate a real Anthropic client. Requires the ``v1`` extra and
    ``ANTHROPIC_API_KEY`` in env."""
    try:
        import anthropic  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "Anthropic SDK not installed. Install with: uv sync --extra v1"
        ) from e
    return anthropic.Anthropic()


def call_text(
    client: _ClaudeClient | None,
    *,
    model: str,
    system: str,
    user: str,
) -> str:
    """Send a single user message; return the first text block."""
    c = client if client is not None else make_client()
    response = c.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    blocks = response.content
    for block in blocks:
        text = getattr(block, "text", None)
        if text:
            return text
    raise RuntimeError("Claude returned no text content")


def call_json(
    client: _ClaudeClient | None,
    *,
    model: str,
    system: str,
    user: str,
) -> dict[str, Any]:
    """Same as call_text, but parse the response as JSON."""
    raw = call_text(client, model=model, system=system, user=user)
    return json.loads(raw)
