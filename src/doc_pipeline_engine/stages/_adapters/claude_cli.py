# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Claude Code CLI adapter — headless one-shot extraction via ``claude --print``."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from doc_pipeline_engine.base.adapter import AdapterBase, register

ADAPTER_NAME = "claude_cli"
ADAPTER_VERSION = "0.1.0"
_DEFAULT_MODEL = "claude-opus-4-8"
_PROMPT = (
    "Extract the full text content of this document. "
    "Output only the plain-text content — no commentary, no markdown, no metadata."
)


class ClaudeCliAdapter(AdapterBase):
    """Extraction backend that shells out to ``claude --print --bare``.

    Requires the Claude Code CLI (``claude``) to be on PATH and a valid
    session or ANTHROPIC_API_KEY to be configured.

    Args:
        model: Claude model identifier passed via ``--model``.
        timeout: Seconds before the subprocess is killed.
    """

    name = ADAPTER_NAME
    version = ADAPTER_VERSION
    locality = "api"

    def __init__(self, model: str = _DEFAULT_MODEL, timeout: int = 120) -> None:
        self._model = model
        self._timeout = timeout

    def extract(self, manifest_file: dict[str, Any], source_root: Path) -> dict[str, Any]:
        """Shell out to ``claude --print --bare`` and parse its JSON envelope.

        Args:
            manifest_file: One entry from ``DiscoveryManifest.files``.
            source_root: Absolute path to the discovered folder.

        Returns:
            ExtractionBundle dict.

        Raises:
            RuntimeError: if ``claude`` is not on PATH or returns a non-zero exit.
        """
        abs_path = source_root / manifest_file["path"]
        cmd = [
            "claude",
            "--print",
            "--bare",
            "--output-format", "json",
            "--model", self._model,
            "--system-prompt", _PROMPT,
        ]
        try:
            result = subprocess.run(  # noqa: S603
                cmd,
                stdin=abs_path.open("rb"),
                capture_output=True,
                timeout=self._timeout,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Claude Code CLI not found. Install it and ensure 'claude' is on PATH."
            ) from exc

        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace")
            raise RuntimeError(
                f"claude exited {result.returncode}: {stderr[:500]}"
            )

        try:
            envelope = json.loads(result.stdout)
            text = envelope.get("result", "")
        except json.JSONDecodeError:
            # --bare with --output-format json should always be valid; fall back to raw
            text = result.stdout.decode(errors="replace")

        return {
            "version": "0.1.0",
            "source_path": manifest_file["path"],
            "source_sha256": manifest_file["sha256"],
            "adapter": {"name": ADAPTER_NAME, "version": ADAPTER_VERSION},
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "content": {"text": text, "layout": []},
        }


register(ClaudeCliAdapter())
