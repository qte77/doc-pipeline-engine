# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Shared Claude client helpers for V1 stages.

Backend dispatch order (first available wins):
  1. Explicit ``client`` kwarg (tests, custom)
  2. Anthropic SDK when ``ANTHROPIC_API_KEY`` is set (the ``v1`` extra)
  3. Claude Code CLI (``claude --print``) when on PATH — uses the user's
     subscription auth, so works in environments without an API key
  4. Raise with install hints

The ``anthropic`` import is deferred so V1 stage modules load without the
optional ``v1`` extra. Tests inject stub clients via the ``client`` kwarg;
real Anthropic and CLI calls happen only in integration tests.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
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


def _has_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _has_claude_cli() -> bool:
    return shutil.which("claude") is not None


def _call_via_sdk(
    client: _ClaudeClient,
    *,
    model: str,
    system: str,
    user: str,
) -> str:
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            return text
    raise RuntimeError("Claude returned no text content")


def _call_via_cli(*, model: str, system: str, user: str) -> str:
    cmd = [
        "claude", "--print",
        "--output-format", "json",
        "--model", model,
        "--system-prompt", system,
        user,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    payload = json.loads(proc.stdout)
    if payload.get("is_error"):
        raise RuntimeError(f"claude CLI returned error: {payload}")
    result = payload.get("result")
    if not result:
        raise RuntimeError(f"claude CLI returned no result field: {payload}")
    return result


def call_text(
    client: _ClaudeClient | None,
    *,
    model: str,
    system: str,
    user: str,
) -> str:
    """Send a single user message; return the assistant's text reply."""
    if client is not None:
        return _call_via_sdk(client, model=model, system=system, user=user)
    if _has_api_key():
        return _call_via_sdk(make_client(), model=model, system=system, user=user)
    if _has_claude_cli():
        return _call_via_cli(model=model, system=system, user=user)
    raise RuntimeError(
        "No V1 backend available. Either set ANTHROPIC_API_KEY "
        "(uv sync --extra v1) or install Claude Code CLI "
        "(https://claude.ai/install.sh) on PATH."
    )


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
