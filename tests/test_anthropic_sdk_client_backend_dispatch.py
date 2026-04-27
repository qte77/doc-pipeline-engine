# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Backend-dispatch tests for _anthropic_sdk_client.

Verifies the precedence: explicit client > ANTHROPIC_API_KEY (Anthropic SDK)
> raise. Anthropic SDK calls are mocked so the suite stays unit-level.

The Claude Code CLI fallback was removed in §0.2.3 PR B (see ADR-0004).
Subscription-only users now run external/cc_cli/run_headless.sh instead.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from doc_pipeline_engine.stages import _anthropic_sdk_client


def _stub_sdk_client(text: str) -> object:
    def _create(**_kwargs: object) -> object:
        return SimpleNamespace(content=[SimpleNamespace(text=text)])
    return SimpleNamespace(messages=SimpleNamespace(create=_create))


def test_anthropic_sdk_client_explicit_client_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "should-not-be-used")
    sentinel_called = {"sdk": False}

    def _boom_sdk(*_a: object, **_kw: object) -> str:
        sentinel_called["sdk"] = True
        raise AssertionError("explicit client must short-circuit make_client")

    monkeypatch.setattr(_anthropic_sdk_client, "make_client", _boom_sdk)

    out = _anthropic_sdk_client.call_text(
        _stub_sdk_client("hello"), model="m", system="s", user="u"
    )

    assert out == "hello"
    assert sentinel_called == {"sdk": False}


def test_anthropic_sdk_client_uses_sdk_when_api_key_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setattr(
        _anthropic_sdk_client, "make_client", lambda: _stub_sdk_client("from-sdk")
    )

    assert (
        _anthropic_sdk_client.call_text(None, model="m", system="s", user="u")
        == "from-sdk"
    )


def test_anthropic_sdk_client_raises_when_no_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        _anthropic_sdk_client.call_text(None, model="m", system="s", user="u")
