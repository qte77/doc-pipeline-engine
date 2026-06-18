# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Tests for the domain pack registry and concrete packs (§0.5.0)."""
from __future__ import annotations

import pytest

from doc_pipeline_engine.domain import DomainPack, available, get, register
from doc_pipeline_engine.domain.formats import (
    available_inputs,
    available_outputs,
    get_input,
    get_output,
)


class TestDomainPackRegistry:
    """Domain pack registry: get, register, available."""

    def test_get_unknown_raises_key_error(self) -> None:
        with pytest.raises(KeyError, match="Unknown domain pack"):
            get("__nonexistent__")

    def test_register_and_get_roundtrip(self) -> None:
        pack = DomainPack(
            name="__test__",
            policy="local-only",
            input_format_ids=[],
            output_format_ids=[],
        )
        register(pack)
        assert get("__test__") is pack

    def test_available_returns_sorted_list(self) -> None:
        names = available()
        assert names == sorted(names)

    def test_builtin_packs_lazy_load(self) -> None:
        for name in ("generic", "mech-elec-cert", "med-research-patents"):
            pack = get(name)
            assert pack.name == name


class TestGenericPack:
    """generic pack is fully wired: formats, policy, prompts, threshold."""

    def setup_method(self) -> None:
        self.pack = get("generic")

    def test_policy_is_claude_api_extracted_only(self) -> None:
        assert self.pack.policy == "claude-api-extracted-only"

    def test_has_four_input_formats(self) -> None:
        assert len(self.pack.input_format_ids) == 4

    def test_has_two_output_formats(self) -> None:
        assert len(self.pack.output_format_ids) == 2

    def test_input_format_ids_are_registered(self) -> None:
        for fmt_id in self.pack.input_format_ids:
            fmt = get_input(fmt_id)
            assert fmt.id == fmt_id

    def test_output_format_ids_are_registered(self) -> None:
        for fmt_id in self.pack.output_format_ids:
            fmt = get_output(fmt_id)
            assert fmt.id == fmt_id

    def test_threshold_is_0_7(self) -> None:
        assert self.pack.extraction_confidence_threshold == 0.7

    def test_prompts_cover_three_stages(self) -> None:
        for stage in ("normalize", "analyze", "draft"):
            assert stage in self.pack.prompts
            assert self.pack.prompts[stage]


class TestStubPacks:
    """Stub packs declare their policy and have empty format lists."""

    def test_mech_elec_cert_policy_local_only(self) -> None:
        pack = get("mech-elec-cert")
        assert pack.policy == "local-only"
        assert pack.input_format_ids == []

    def test_med_research_patents_policy_cloud_redacted(self) -> None:
        pack = get("med-research-patents")
        assert pack.policy == "cloud-redacted"
        assert pack.input_format_ids == []

    def test_mech_elec_cert_threshold_higher(self) -> None:
        assert get("mech-elec-cert").extraction_confidence_threshold == 0.85

    def test_med_research_patents_threshold_highest(self) -> None:
        assert get("med-research-patents").extraction_confidence_threshold == 0.9


class TestFormatRegistry:
    """Format registry get/available functions."""

    def test_get_input_unknown_raises_key_error(self) -> None:
        with pytest.raises(KeyError, match="Unknown input format"):
            get_input("__nonexistent__/__format__")

    def test_get_output_unknown_raises_key_error(self) -> None:
        with pytest.raises(KeyError, match="Unknown output format"):
            get_output("__nonexistent__/__format__")

    def test_available_inputs_sorted(self) -> None:
        names = available_inputs()
        assert names == sorted(names)

    def test_available_outputs_sorted(self) -> None:
        names = available_outputs()
        assert names == sorted(names)

    def test_generic_inputs_present_after_pack_load(self) -> None:
        get("generic")  # ensure pack loaded
        for fmt_id in ("generic/text", "generic/pdf", "generic/office", "generic/image"):
            assert get_input(fmt_id).id == fmt_id

    def test_generic_outputs_present_after_pack_load(self) -> None:
        get("generic")
        for fmt_id in ("generic/quick-summary", "generic/comprehensive-report"):
            assert get_output(fmt_id).id == fmt_id
