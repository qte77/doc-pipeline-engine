# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Backend-dispatch tests for _v1_client.

Verifies the precedence: explicit client > ANTHROPIC_API_KEY (Anthropic SDK)
> claude CLI on PATH > raise. Subprocess and Anthropic SDK calls are
mocked so the suite stays unit-level.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from doc_pipeline_engine.stages import _v1_client


def _stub_sdk_client(text: str) -> object:
    def _create(**_kwargs: object) -> object:
        return SimpleNamespace(content=[SimpleNamespace(text=text)])
    return SimpleNamespace(messages=SimpleNamespace(create=_create))


def test_v1_client_explicit_client_wins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "should-not-be-used")
    monkeypatch.setattr(_v1_client, "_has_claude_cli", lambda: True)
    sentinel_called = {"sdk": False, "cli": False}

    def _boom_sdk(*_a: object, **_kw: object) -> str:
        sentinel_called["sdk"] = True
        raise AssertionError("explicit client must short-circuit make_client")

    def _boom_cli(*_a: object, **_kw: object) -> str:
        sentinel_called["cli"] = True
        raise AssertionError("explicit client must short-circuit CLI fallback")

    monkeypatch.setattr(_v1_client, "make_client", _boom_sdk)
    monkeypatch.setattr(_v1_client, "_call_via_cli", _boom_cli)

    out = _v1_client.call_text(
        _stub_sdk_client("hello"), model="m", system="s", user="u"
    )

    assert out == "hello"
    assert sentinel_called == {"sdk": False, "cli": False}


def test_v1_client_uses_sdk_when_api_key_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setattr(_v1_client, "_has_claude_cli", lambda: True)
    monkeypatch.setattr(_v1_client, "make_client", lambda: _stub_sdk_client("from-sdk"))

    def _boom_cli(*_a: object, **_kw: object) -> str:
        raise AssertionError("CLI must not run when API key is set")

    monkeypatch.setattr(_v1_client, "_call_via_cli", _boom_cli)

    assert _v1_client.call_text(None, model="m", system="s", user="u") == "from-sdk"


def test_v1_client_falls_back_to_cli_when_no_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(_v1_client, "_has_claude_cli", lambda: True)

    captured: dict[str, list[str]] = {}

    def _fake_run(cmd: list[str], **_kw: object) -> object:
        captured["cmd"] = cmd
        return SimpleNamespace(
            stdout=json.dumps({"result": "from-cli", "is_error": False}),
            stderr="",
            returncode=0,
        )

    monkeypatch.setattr(_v1_client.subprocess, "run", _fake_run)

    out = _v1_client.call_text(
        None, model="claude-opus-4-7", system="be terse", user="hi"
    )

    assert out == "from-cli"
    assert captured["cmd"][:2] == ["claude", "--print"]
    assert "--system-prompt" in captured["cmd"]
    assert "be terse" in captured["cmd"]
    assert captured["cmd"][-1] == "hi"


def test_v1_client_raises_when_no_backend_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(_v1_client, "_has_claude_cli", lambda: False)

    with pytest.raises(RuntimeError, match="No V1 backend available"):
        _v1_client.call_text(None, model="m", system="s", user="u")


def test_v1_client_cli_propagates_is_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(_v1_client, "_has_claude_cli", lambda: True)

    def _fake_run(_cmd: list[str], **_kw: object) -> object:
        return SimpleNamespace(
            stdout=json.dumps({"is_error": True, "result": ""}),
            stderr="",
            returncode=0,
        )

    monkeypatch.setattr(_v1_client.subprocess, "run", _fake_run)

    with pytest.raises(RuntimeError, match="claude CLI returned error"):
        _v1_client.call_text(None, model="m", system="s", user="u")


def test_v1_client_call_json_parses_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(_v1_client, "_has_claude_cli", lambda: True)

    def _fake_run(_cmd: list[str], **_kw: object) -> object:
        return SimpleNamespace(
            stdout=json.dumps(
                {"result": json.dumps({"key": "value"}), "is_error": False}
            ),
            stderr="",
            returncode=0,
        )

    monkeypatch.setattr(_v1_client.subprocess, "run", _fake_run)

    out = _v1_client.call_json(None, model="m", system="s", user="u")

    assert out == {"key": "value"}
