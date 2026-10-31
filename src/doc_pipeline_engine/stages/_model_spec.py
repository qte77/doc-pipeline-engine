# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Model spec for the cloud leg: which provider/model/endpoint/auth to call.

Selected from the environment (see ADR-0004 amendment, #162):

- ``DPE_MODEL_PROVIDER`` unset or ``anthropic`` — Anthropic Messages API
  (``ANTHROPIC_API_KEY``), the existing default.
- ``DPE_MODEL_PROVIDER=azure_openai`` — Azure OpenAI Chat Completions with
  Entra ID / Managed Identity (``DefaultAzureCredential``; no API key):
  ``AZURE_OPENAI_ENDPOINT``, ``AZURE_OPENAI_DEPLOYMENT``,
  ``AZURE_OPENAI_API_VERSION``. Needs the ``azure-openai`` extra.

SDK imports are deferred so stage modules load without either extra.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

AZURE_SCOPE = "https://cognitiveservices.azure.com/.default"
AZURE_API_VERSION_DEFAULT = "2024-10-21"


@dataclass(frozen=True)
class ModelSpec:
    """Provider, model (Azure: deployment name), endpoint and auth mode."""

    provider: str
    model: str | None = None
    endpoint: str | None = None
    api_version: str | None = None
    auth: str = "api_key"


def spec_from_env() -> ModelSpec:
    """Build the active spec from ``DPE_MODEL_PROVIDER`` and provider env vars."""
    provider = os.environ.get("DPE_MODEL_PROVIDER", "anthropic")
    if provider == "anthropic":
        return ModelSpec(provider="anthropic")
    if provider == "azure_openai":
        return ModelSpec(
            provider="azure_openai",
            model=_require("AZURE_OPENAI_DEPLOYMENT"),
            endpoint=_require("AZURE_OPENAI_ENDPOINT"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", AZURE_API_VERSION_DEFAULT),
            auth="entra",
        )
    raise ValueError(
        f"DPE_MODEL_PROVIDER must be 'anthropic' or 'azure_openai', got {provider!r}"
    )


def make_client_for_spec(spec: ModelSpec) -> Any:
    """Instantiate the real SDK client for a non-Anthropic spec."""
    if spec.provider != "azure_openai":
        raise ValueError(f"no client factory for provider {spec.provider!r}")
    try:
        from azure.identity import (  # type: ignore[import-not-found]
            DefaultAzureCredential,
            get_bearer_token_provider,
        )
        from openai import AzureOpenAI  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "Azure OpenAI transport not installed. Install with: uv sync --extra azure-openai"
        ) from e
    return AzureOpenAI(
        azure_endpoint=spec.endpoint,
        api_version=spec.api_version,
        azure_ad_token_provider=get_bearer_token_provider(DefaultAzureCredential(), AZURE_SCOPE),
    )


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"DPE_MODEL_PROVIDER=azure_openai requires {name}")
    return value
