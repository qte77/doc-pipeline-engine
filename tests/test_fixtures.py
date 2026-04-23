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

"""Exercise the fixture generator: every domain yields a valid DiscoveryManifest."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from doc_pipeline_engine.base.contracts import validate

REPO_ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "_genfix", REPO_ROOT / "scripts" / "generate-fixtures.py"
)
assert _spec and _spec.loader
_genfix = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_genfix)

DOMAIN_DIRS = _genfix.domain_dirs()


def test_domains_discovered() -> None:
    assert len(DOMAIN_DIRS) >= 7, f"expected >=7 domains, found {len(DOMAIN_DIRS)}"


@pytest.mark.parametrize(
    "domain_dir", DOMAIN_DIRS, ids=lambda p: str(p.relative_to(REPO_ROOT / "samples"))
)
def test_manifest_validates(domain_dir: Path) -> None:
    manifest = _genfix.build_manifest(domain_dir)
    validate("DiscoveryManifest", manifest)
