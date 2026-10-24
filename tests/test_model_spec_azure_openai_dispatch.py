# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Model-spec dispatch (#162): route cloud-leg calls to Azure OpenAI via Entra.

No real SDKs: ``openai`` / ``azure.identity`` are replaced in ``sys.modules`` and
clients are SimpleNamespace stubs with the Chat Completions call surface.
"""
from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace
from typing import TYPE_CHECKING, Any

from doc_pipeline_engine.stages import _anthropic_sdk_client, _model_spec
from doc_pipeline_engine.stages._model_spec import ModelSpec

if TYPE_CHECKING:
    import pytest

_AZURE_ENV = {
    "DPE_MODEL_PROVIDER": "azure_openai",
    "AZURE_OPENAI_ENDPOINT": "https://example-eu.openai.azure.com",
    "AZURE_OPENAI_DEPLOYMENT": "gpt-eu-deploy",
    "AZURE_OPENAI_API_VERSION": "2024-10-21",
}


def _stub_chat_client(text: str, captured: dict[str, Any]) -> object:
    def _create(**kwargs: Any) -> object:
        captured.update(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=_create)))


def test_call_text_dispatches_openai_shaped_client_to_chat_completions() -> None:
    captured: dict[str, Any] = {}

    out = _anthropic_sdk_client.call_text(
        _stub_chat_client("from-azure", captured), model="gpt-eu-deploy", system="S", user="U"
    )

    assert out == "from-azure"
    assert captured["model"] == "gpt-eu-deploy"
    assert captured["messages"] == [
        {"role": "system", "content": "S"},
        {"role": "user", "content": "U"},
    ]


def test_spec_from_env_builds_azure_entra_spec(monkeypatch: pytest.MonkeyPatch) -> None:
    for k, v in _AZURE_ENV.items():
        monkeypatch.setenv(k, v)

    spec = _model_spec.spec_from_env()

    assert spec == ModelSpec(
        provider="azure_openai",
        model="gpt-eu-deploy",
        endpoint="https://example-eu.openai.azure.com",
        api_version="2024-10-21",
        auth="entra",
    )


def test_spec_from_env_defaults_to_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DPE_MODEL_PROVIDER", raising=False)

    assert _model_spec.spec_from_env().provider == "anthropic"


def test_call_text_without_client_routes_to_azure_deployment_without_anthropic_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for k, v in _AZURE_ENV.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    captured: dict[str, Any] = {}
    built: list[ModelSpec] = []

    def _fake_make(spec: ModelSpec) -> object:
        built.append(spec)
        return _stub_chat_client("routed", captured)

    monkeypatch.setattr(_model_spec, "make_client_for_spec", _fake_make)

    out = _anthropic_sdk_client.call_text(None, model="claude-opus-4-7", system="S", user="U")

    assert out == "routed"
    assert built[0].provider == "azure_openai"
    assert captured["model"] == "gpt-eu-deploy", "Azure routes by deployment, not the Claude id"


def test_make_client_for_azure_entra_uses_token_provider_not_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, Any] = {}

    fake_openai = ModuleType("openai")
    fake_openai.AzureOpenAI = lambda **kw: calls.setdefault("client", kw)  # type: ignore[attr-defined]
    fake_identity = ModuleType("azure.identity")
    fake_identity.DefaultAzureCredential = lambda: "cred"  # type: ignore[attr-defined]

    def _provider(cred: str, scope: str) -> str:
        calls["provider"] = (cred, scope)
        return "token-provider"

    fake_identity.get_bearer_token_provider = _provider  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", fake_openai)
    monkeypatch.setitem(sys.modules, "azure", ModuleType("azure"))
    monkeypatch.setitem(sys.modules, "azure.identity", fake_identity)

    _model_spec.make_client_for_spec(
        ModelSpec(
            provider="azure_openai",
            model="gpt-eu-deploy",
            endpoint="https://example-eu.openai.azure.com",
            api_version="2024-10-21",
            auth="entra",
        )
    )

    assert calls["provider"] == ("cred", "https://cognitiveservices.azure.com/.default")
    assert calls["client"] == {
        "azure_endpoint": "https://example-eu.openai.azure.com",
        "api_version": "2024-10-21",
        "azure_ad_token_provider": "token-provider",
    }
