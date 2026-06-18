# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Extract stage: Kreuzberg-backed adapter → ExtractionBundle.

Kreuzberg is an opt-in extra (``uv sync --extra extract``). The import is
deferred so this module is importable without it; calling ``extract`` without
the extra installed raises a clear error.

The unit tests substitute ``_extract_file_sync`` and ``_kreuzberg_version``
via monkeypatch so they run without the extra. Real-Kreuzberg behavior is
covered by tests marked ``integration``.

Supported input formats: see docs/architecture.md → "Supported input formats".
SVG is not supported.
"""
from __future__ import annotations

import contextlib
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ADAPTER_NAME = "kreuzberg"
CONTRACT_VERSION = "0.1.0"


def _load_kreuzberg() -> tuple[Callable[..., Any], str]:
    try:
        from kreuzberg import __version__ as version  # type: ignore[import-not-found]
        from kreuzberg import extract_file_sync as fn  # type: ignore[import-not-found]
    except ImportError as e:
        raise RuntimeError(
            "Kreuzberg not installed. Install the extras: "
            "uv sync --extra extract"
        ) from e
    return fn, version


_extract_file_sync, _kreuzberg_version = (None, "")
with contextlib.suppress(RuntimeError):
    _extract_file_sync, _kreuzberg_version = _load_kreuzberg()


def extract(file_entry: dict[str, Any], source_root: Path) -> dict[str, Any]:
    """Run Kreuzberg on ``source_root / file_entry['path']`` → ExtractionBundle dict."""
    if _extract_file_sync is None:
        raise RuntimeError(
            "Kreuzberg not installed. Install the extras: uv sync --extra extract"
        )

    abs_path = source_root / file_entry["path"]
    result = _extract_file_sync(str(abs_path))

    return {
        "version": CONTRACT_VERSION,
        "source_path": file_entry["path"],
        "source_sha256": file_entry["sha256"],
        "adapter": {"name": ADAPTER_NAME, "version": _kreuzberg_version},
        "extracted_at": datetime.now(UTC).isoformat(),
        "content": {
            "text": getattr(result, "content", "") or "",
            "layout": [],
        },
    }
