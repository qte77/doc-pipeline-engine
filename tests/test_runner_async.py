# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Async runner (#161): awaits async stage callables, keeps the sync gate."""
from __future__ import annotations

import asyncio

import pytest

from doc_pipeline_engine.runner import PipelineError, run_async
from tests.test_runner_chain_halts_on_gate_failure import (
    _invalid_extraction_bundle,
    _valid_discovery_manifest,
    _valid_extraction_bundle,
)


async def _async_discover(seed: dict) -> dict:
    await asyncio.sleep(0)
    return _valid_discovery_manifest(seed)


async def _async_extract(manifest: dict) -> dict:
    await asyncio.sleep(0)
    return _valid_extraction_bundle(manifest)


async def _async_invalid_extract(manifest: dict) -> dict:
    return _invalid_extraction_bundle(manifest)


def test_run_async_awaits_async_stages_in_order() -> None:
    stages = [
        ("discover", _async_discover, "DiscoveryManifest"),
        ("extract", _async_extract, "ExtractionBundle"),
    ]

    outputs = asyncio.run(run_async(stages, seed={}))

    assert outputs[0]["files"][0]["path"] == "a.pdf"
    assert outputs[1]["adapter"]["name"] == "stub"


def test_run_async_accepts_sync_stages_alongside_async() -> None:
    stages = [
        ("discover", _valid_discovery_manifest, "DiscoveryManifest"),
        ("extract", _async_extract, "ExtractionBundle"),
    ]

    outputs = asyncio.run(run_async(stages, seed={}))

    assert len(outputs) == 2


def test_run_async_halts_on_first_invalid_output_without_running_later_stages() -> None:
    called: list[str] = []

    async def _never(_bundle: dict) -> dict:
        called.append("later")
        return {}

    stages = [
        ("discover", _async_discover, "DiscoveryManifest"),
        ("extract", _async_invalid_extract, "ExtractionBundle"),
        ("later", _never, "CanonicalDoc"),
    ]

    with pytest.raises(PipelineError) as exc:
        asyncio.run(run_async(stages, seed={}))

    assert exc.value.stage_name == "extract"
    assert exc.value.contract_name == "ExtractionBundle"
    assert called == []
