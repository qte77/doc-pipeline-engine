# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Shared Anthropic Python SDK client helpers for the `anthropic_sdk` leg.

Backend dispatch (first available wins):

1. Explicit ``client`` kwarg (tests, custom — e.g. point at a self-hosted
   Anthropic-compatible endpoint via the SDK's ``base_url``). An
   OpenAI-shaped client (``client.chat.completions``) is called via Chat
   Completions; anything else via the Anthropic Messages API.
2. A non-Anthropic model spec from the environment
   (``DPE_MODEL_PROVIDER=azure_openai``, see :mod:`._model_spec`) — Azure
   OpenAI via Entra ID, model = the deployment name.
3. Anthropic SDK when ``ANTHROPIC_API_KEY`` is set (the
   ``anthropic_sdk`` extra).
4. Raise with install hints.

The Claude Code CLI fallback (#41 / #30) was removed in §0.2.3 PR B
(see ADR-0004); subscription-only users now run the
``external/cc_cli/`` track instead. This module is purely the SDK
transport for the in-process pipeline.

The ``anthropic`` import is deferred so the leg's stage modules
load without the optional ``anthropic_sdk`` extra. Tests inject
stub clients via the ``client`` kwarg; real Anthropic calls happen
only in integration tests.
"""
from __future__ import annotations

import json
import os
from typing import Any, Protocol

from doc_pipeline_engine.stages import _model_spec

MODEL_DEFAULT = "claude-opus-4-7"
MAX_TOKENS = 4096


class _MessagesAPI(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


class _ClaudeClient(Protocol):
    messages: _MessagesAPI


def make_client() -> _ClaudeClient:
    """Instantiate a real Anthropic client. Requires the ``anthropic_sdk`` extra and
    ``ANTHROPIC_API_KEY`` in env."""
    try:
        import anthropic  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "Anthropic SDK not installed. Install with: uv sync --extra anthropic_sdk"
        ) from e
    return anthropic.Anthropic()


def _has_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


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


def _call_via_chat_completions(client: Any, *, model: str, system: str, user: str) -> str:
    response = client.chat.completions.create(
        model=model,
        max_completion_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    text = response.choices[0].message.content if response.choices else None
    if not text:
        raise RuntimeError("Chat Completions returned no text content")
    return text


def _call(client: Any, *, model: str, system: str, user: str) -> str:
    if hasattr(client, "chat"):
        return _call_via_chat_completions(client, model=model, system=system, user=user)
    return _call_via_sdk(client, model=model, system=system, user=user)


def call_text(
    client: _ClaudeClient | None,
    *,
    model: str,
    system: str,
    user: str,
) -> str:
    """Send a single user message; return the assistant's text reply."""
    if client is not None:
        return _call(client, model=model, system=system, user=user)
    spec = _model_spec.spec_from_env()
    if spec.provider != "anthropic":
        return _call(
            _model_spec.make_client_for_spec(spec),
            model=spec.model or model,
            system=system,
            user=user,
        )
    if _has_api_key():
        return _call_via_sdk(make_client(), model=model, system=system, user=user)
    raise RuntimeError(
        "anthropic_sdk leg requires ANTHROPIC_API_KEY (uv sync --extra anthropic_sdk). "
        "Without an API key, run the off-the-shelf Claude Code track at "
        "external/cc_cli/run_headless.sh instead."
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
