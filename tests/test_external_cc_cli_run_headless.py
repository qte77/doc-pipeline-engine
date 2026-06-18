# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Tests for external/cc_cli/run_headless.sh.

The bash runner shells out to `claude --print` (with `--bare` for
vanilla, without for project) and pipes through `npx codeburn` for
cost capture. Tested by writing fake `claude` and `codeburn`
shims to a tmpdir, prepending tmpdir to `PATH`, then asserting the
output dir + meta.json contents.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "external" / "cc_cli" / "run_headless.sh"


def _write_fake_claude(shim_dir: Path, summary_text: str = "# Stub summary") -> Path:
    """Fake `claude` binary that records its invocation + emits a fixed JSON envelope.

    summary_text must not contain control chars (jq is strict). Use a one-line
    placeholder.
    """
    claude = shim_dir / "claude"
    log = shim_dir / "claude.log"
    json_line = (
        f'{{"result": "{summary_text}", "is_error": false,'
        f' "model": "claude-opus-4-7",'
        f' "usage": {{"input_tokens": 100, "output_tokens": 50}}}}'
    )
    claude.write_text(dedent(f"""\
        #!/usr/bin/env bash
        # Record invocation
        echo "ARGV: $*" >> "{log}"
        printf '%s\\n' '{json_line}'
    """))
    claude.chmod(0o755)
    return claude


def _write_fake_codeburn(shim_dir: Path, cost_usd: float = 0.0125) -> Path:
    """Fake `npx codeburn` shim.

    Reads stdin (claude's JSON), echoes it back, prints cost to stderr.
    """
    codeburn = shim_dir / "npx"
    codeburn.write_text(dedent(f"""\
        #!/usr/bin/env bash
        # Only intercept `npx codeburn ...`; pass through stdin → stdout, emit cost on stderr
        if [ "$1" = "codeburn" ]; then
            cat                                          # passthrough JSON
            echo "CODEBURN_COST_USD={cost_usd}" 1>&2     # cost on stderr
        else
            exit 1
        fi
    """))
    codeburn.chmod(0o755)
    return codeburn


def _write_sample(tmp_path: Path) -> Path:
    sample = tmp_path / "sample.txt"
    sample.write_text("Sample document body.\n")
    return sample


@pytest.fixture
def shim_env(tmp_path: Path) -> dict[str, str]:
    """Build a tmpdir with fake claude+npx shims, return env with PATH override."""
    shim_dir = tmp_path / "shims"
    shim_dir.mkdir()
    _write_fake_claude(shim_dir)
    _write_fake_codeburn(shim_dir)
    env = os.environ.copy()
    env["PATH"] = f"{shim_dir}:{env['PATH']}"
    return env


def _run_script(
    *, sample: Path, config: str, output_dir: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        ["bash", str(SCRIPT), str(sample), "--config", config, "--output-dir", str(output_dir)],  # noqa: S607
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )


def test_cc_cli_run_headless_vanilla_invokes_claude_with_bare_flag(
    tmp_path: Path, shim_env: dict[str, str]
) -> None:
    sample = _write_sample(tmp_path)
    out = tmp_path / "outputs"

    _run_script(sample=sample, config="vanilla", output_dir=out, env=shim_env)

    log_path = Path(shim_env["PATH"].split(":")[0]) / "claude.log"
    invocation = log_path.read_text()
    assert "--bare" in invocation, "vanilla mode must invoke claude with --bare"
    assert "--print" in invocation
    # Output exists
    sha_dirs = list(out.iterdir())
    assert sha_dirs, "no sha dir created"
    summary = sha_dirs[0] / "external" / "cc-cli-headless-vanilla" / "summary.md"
    assert summary.exists()


def test_cc_cli_run_headless_project_omits_bare_flag(
    tmp_path: Path, shim_env: dict[str, str]
) -> None:
    sample = _write_sample(tmp_path)
    out = tmp_path / "outputs"

    _run_script(sample=sample, config="project", output_dir=out, env=shim_env)

    log_path = Path(shim_env["PATH"].split(":")[0]) / "claude.log"
    invocation = log_path.read_text()
    assert "--bare" not in invocation, "project mode must NOT pass --bare"
    sha_dirs = list(out.iterdir())
    summary = sha_dirs[0] / "external" / "cc-cli-headless-project" / "summary.md"
    assert summary.exists()


def test_cc_cli_run_headless_records_cost_from_codeburn_envelope(
    tmp_path: Path, shim_env: dict[str, str]
) -> None:
    sample = _write_sample(tmp_path)
    out = tmp_path / "outputs"

    _run_script(sample=sample, config="vanilla", output_dir=out, env=shim_env)

    sha_dirs = list(out.iterdir())
    meta_path = sha_dirs[0] / "external" / "cc-cli-headless-vanilla" / "meta.json"
    meta = json.loads(meta_path.read_text())
    assert meta["variant"] == "cc-cli-headless-vanilla"
    assert meta["transport"] == "cc-cli"
    assert meta["config"] == "vanilla"
    # Codeburn cost (0.0125) propagated into meta.json
    assert meta["cost_usd"] == pytest.approx(0.0125)
