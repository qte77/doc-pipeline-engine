#!/usr/bin/env python3
# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate DiscoveryManifest fixtures for each samples/<domain>/ dir."""
from __future__ import annotations

import hashlib
import json
import mimetypes
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from doc_pipeline_engine.base.contracts import validate  # noqa: E402

SAMPLES_ROOT = REPO_ROOT / "samples"

TOP_LEVEL_DOMAINS = (
    "generic",
    "mech-elec-cert",
    "contracts",
    "invoices",
    "communication",
    "patents",
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"}
EXT_TO_TYPE = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".txt": "txt",
    ".md": "md",
}


def file_type_for(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in EXT_TO_TYPE:
        return EXT_TO_TYPE[ext]
    if ext in IMAGE_EXTS:
        return "image"
    return "unknown"


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect_files(domain_dir: Path) -> list[dict]:
    now = iso_utc_now()
    entries: list[dict] = []
    for p in sorted(domain_dir.iterdir()):
        if not p.is_file():
            continue
        if p.name == "_manifest.json" or p.name.startswith(".") or p.suffix == ".md":
            continue
        entry: dict = {
            "path": p.name,
            "size_bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "file_type": file_type_for(p),
            "detected_at": now,
        }
        mime = mimetypes.guess_type(p.name)[0]
        if mime:
            entry["mime"] = mime
        entries.append(entry)
    return entries


def build_manifest(domain_dir: Path) -> dict:
    return {
        "version": "0.1.0",
        "source": {"root": str(domain_dir.resolve()), "kind": "folder"},
        "discovered_at": iso_utc_now(),
        "files": collect_files(domain_dir),
    }


def domain_dirs() -> list[Path]:
    dirs: list[Path] = []
    for name in TOP_LEVEL_DOMAINS:
        d = SAMPLES_ROOT / name
        if d.is_dir():
            dirs.append(d)
    legal = SAMPLES_ROOT / "legal"
    if legal.is_dir():
        dirs.extend(sorted(p for p in legal.iterdir() if p.is_dir()))
    return dirs


def main() -> int:
    dirs = domain_dirs()
    total = 0
    for domain_dir in dirs:
        manifest = build_manifest(domain_dir)
        try:
            validate("DiscoveryManifest", manifest)
        except Exception as exc:
            print(f"FAIL {domain_dir.relative_to(REPO_ROOT)}: {exc}", file=sys.stderr)
            return 1
        out = domain_dir / "_manifest.json"
        out.write_text(json.dumps(manifest, indent=2) + "\n")
        n = len(manifest["files"])
        total += n
        print(f"{domain_dir.relative_to(SAMPLES_ROOT)}: {n} files")
    print(f"total: {total} files across {len(dirs)} domains")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
