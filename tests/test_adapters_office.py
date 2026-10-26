# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Tests for the lightweight python-docx / openpyxl office adapter (#163)."""
from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

import pytest

from doc_pipeline_engine.base.adapter import get
from doc_pipeline_engine.models.extraction_bundle import ExtractionBundle

if TYPE_CHECKING:
    from pathlib import Path

SHA_ZERO = "0" * 64


def _entry(name: str) -> dict[str, Any]:
    return {"path": name, "sha256": SHA_ZERO}


def test_office_adapter_is_a_local_builtin() -> None:
    adapter = get("office")
    assert adapter.name == "office"
    assert adapter.locality == "local"


def test_docx_extracts_paragraphs_and_table_cells(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    doc = docx.Document()
    doc.add_heading("Quarterly report", level=1)
    doc.add_paragraph("Revenue grew.")
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Region"
    table.rows[0].cells[1].text = "EMEA"
    doc.save(tmp_path / "report.docx")

    bundle = get("office").extract(_entry("report.docx"), tmp_path)

    assert isinstance(bundle, ExtractionBundle)
    assert bundle.adapter.name == "office"
    assert bundle.content.text.splitlines() == ["Quarterly report", "Revenue grew.", "Region\tEMEA"]


def test_xlsx_extracts_sheet_rows_as_tab_separated_text(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Q1"
    ws.append(["Region", "Revenue"])
    ws.append(["EMEA", 42])
    ws.append([None, None])
    wb.save(tmp_path / "numbers.xlsx")

    bundle = get("office").extract(_entry("numbers.xlsx"), tmp_path)

    assert bundle.content.text.splitlines() == ["# Q1", "Region\tRevenue", "EMEA\t42"]


def test_unsupported_suffix_raises_value_error(tmp_path: Path) -> None:
    (tmp_path / "slides.pptx").write_bytes(b"")
    with pytest.raises(ValueError, match=r"\.docx/\.xlsx"):
        get("office").extract(_entry("slides.pptx"), tmp_path)


def test_missing_library_raises_install_hint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_import = builtins.__import__

    def _no_openpyxl(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "openpyxl":
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _no_openpyxl)
    (tmp_path / "numbers.xlsx").write_bytes(b"")
    with pytest.raises(RuntimeError, match="uv sync --extra office"):
        get("office").extract(_entry("numbers.xlsx"), tmp_path)
