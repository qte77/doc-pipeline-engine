# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Pipeline quality gates.

Gates are callable checks inserted between stages. Each gate raises
:class:`GateError` when its condition is violated; callers treat a
``GateError`` as a halting failure (equivalent to a ``PipelineError``).

Built-in gates:

- :class:`FormatGate` — rejects files whose type is not in the domain pack's
  accepted input formats (failure mode F11).
- :class:`PolicyGate` — rejects adapter/pack combinations that violate the
  pack's data-locality policy (failure mode F5).
- :class:`ConfidenceGate` — rejects ExtractionBundles below the pack's
  extraction confidence threshold (failure mode F2 partial).
"""
from __future__ import annotations

from typing import Any


class GateError(Exception):
    """Raised when a pipeline gate condition is violated.

    Attributes:
        gate: Name of the gate that fired.
        detail: Human-readable explanation.
    """

    def __init__(self, gate: str, detail: str) -> None:
        self.gate = gate
        self.detail = detail
        super().__init__(f"gate={gate!r}: {detail}")


class FormatGate:
    """Reject files whose type is not accepted by the domain pack (F11).

    Args:
        pack_name: Domain pack name used to look up accepted input formats.
    """

    def __init__(self, pack_name: str) -> None:
        self._pack_name = pack_name

    def check(self, manifest_file: dict[str, Any]) -> None:
        """Raise GateError if file_type is not in the pack's input formats.

        Args:
            manifest_file: One entry from ``DiscoveryManifest.files``.

        Raises:
            GateError: if the file type is not accepted by the pack.
        """
        from doc_pipeline_engine.domain import get as get_pack
        from doc_pipeline_engine.domain.formats import get_input

        pack = get_pack(self._pack_name)
        file_type = manifest_file.get("file_type", "")

        for fmt_id in pack.input_format_ids:
            try:
                fmt = get_input(fmt_id)
            except KeyError:
                continue
            if file_type in fmt.file_types:
                return

        accepted = sorted(
            ext
            for fmt_id in pack.input_format_ids
            for fmt in [_safe_get_input(fmt_id)]
            if fmt
            for ext in fmt.file_types
        )
        raise GateError(
            "F11-format-miss",
            f"file_type={file_type!r} not accepted by pack {self._pack_name!r}. "
            f"Accepted: {accepted}",
        )


def _safe_get_input(fmt_id: str) -> Any:
    from doc_pipeline_engine.domain.formats import get_input

    try:
        return get_input(fmt_id)
    except KeyError:
        return None


_POLICY_ALLOWED_ADAPTERS: dict[str, set[str]] = {
    "local-only": {"kreuzberg", "docling", "glm_ocr", "paddle_ocr"},
    "claude-api-extracted-only": {
        "kreuzberg",
        "claude_cli",
        "docling",
        "glm_ocr",
        "paddle_ocr",
    },
    "cloud-redacted": {
        "kreuzberg",
        "claude_cli",
        "docling",
        "glm_ocr",
        "paddle_ocr",
    },
}


class PolicyGate:
    """Reject adapter/pack combinations that violate data-locality policy (F5).

    Args:
        pack_name: Domain pack name used to look up the policy.
    """

    def __init__(self, pack_name: str) -> None:
        self._pack_name = pack_name

    def check(self, adapter_name: str) -> None:
        """Raise GateError if the adapter violates the pack's policy.

        Args:
            adapter_name: Name of the adapter about to be used (e.g. ``"claude_cli"``).

        Raises:
            GateError: if the adapter is not permitted under the pack's policy.
        """
        from doc_pipeline_engine.domain import get as get_pack

        pack = get_pack(self._pack_name)
        allowed = _POLICY_ALLOWED_ADAPTERS.get(pack.policy, set())
        if adapter_name not in allowed:
            raise GateError(
                "F5-policy-violation",
                f"adapter={adapter_name!r} is not permitted under policy "
                f"{pack.policy!r} of pack {self._pack_name!r}. "
                f"Permitted adapters: {sorted(allowed)}",
            )


class ConfidenceGate:
    """Reject ExtractionBundles below the pack's confidence threshold (F2 partial).

    Args:
        pack_name: Domain pack name used to look up the threshold.
    """

    def __init__(self, pack_name: str) -> None:
        self._pack_name = pack_name

    def check(self, extraction_bundle: dict[str, Any]) -> None:
        """Raise GateError if bundle confidence is below pack threshold.

        Args:
            extraction_bundle: ExtractionBundle dict output from an adapter.

        Raises:
            GateError: if confidence is present and below the threshold.
        """
        from doc_pipeline_engine.domain import get as get_pack

        pack = get_pack(self._pack_name)
        confidence = extraction_bundle.get("confidence")
        if confidence is None:
            return
        if confidence < pack.extraction_confidence_threshold:
            raise GateError(
                "G-extract-confidence",
                f"confidence={confidence} is below pack threshold "
                f"{pack.extraction_confidence_threshold} for pack {self._pack_name!r}",
            )
