#!/usr/bin/env bash
# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# External Claude Code CLI one-shot summarizer (headless).
#
# Sends a single `claude --print` call per sample. Vanilla mode passes
# `--bare` to suppress project-context auto-discovery; project mode runs
# from repo root so .claude/{skills,rules,settings.json} auto-load.
#
# The invocation is wrapped through `npx codeburn` for cost capture; the
# captured cost is written to meta.json.cost_usd. See ADR-0004.
#
# Output: outputs/<sha>/external/cc-cli-headless-{vanilla,project}/{summary.md,meta.json}
#
# Usage:
#   bash external/cc_cli/run_headless.sh <sample> --config <vanilla|project> [--output-dir <dir>]

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../.." &> /dev/null && pwd)"
PROMPT_PATH="${REPO_ROOT}/external/PROMPT.md"
CONTRACTS_PATH="${REPO_ROOT}/docs/contracts.md"

CONFIG="vanilla"
OUTPUT_DIR="outputs"
MODEL="claude-opus-4-7"
SAMPLE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)     CONFIG="$2"; shift 2;;
    --output-dir) OUTPUT_DIR="$2"; shift 2;;
    --model)      MODEL="$2"; shift 2;;
    --*)          echo "unknown flag: $1" >&2; exit 2;;
    *)            SAMPLE="$1"; shift;;
  esac
done

if [[ -z "${SAMPLE}" ]]; then
  echo "Usage: $0 <sample> --config <vanilla|project> [--output-dir <dir>]" >&2
  exit 2
fi
if [[ "${CONFIG}" != "vanilla" && "${CONFIG}" != "project" ]]; then
  echo "--config must be 'vanilla' or 'project'" >&2
  exit 2
fi

# sha256 of the sample bytes — matches Discover stage's hashing.
SHA="$(sha256sum "${SAMPLE}" | awk '{print $1}')"
VARIANT="cc-cli-headless-${CONFIG}"
VARIANT_DIR="${OUTPUT_DIR}/${SHA}/external/${VARIANT}"
mkdir -p "${VARIANT_DIR}"

# Assemble the system prompt:
#   PROMPT.md + contracts.md (referenced for CC; not inlined).
SYSTEM="$(cat "${PROMPT_PATH}")
Pipeline contracts reference: ${CONTRACTS_PATH}"

# Build the claude argv. --bare suppresses project context for vanilla.
CLAUDE_ARGS=(--print --output-format json --model "${MODEL}" --system-prompt "${SYSTEM}")
if [[ "${CONFIG}" == "vanilla" ]]; then
  CLAUDE_ARGS=(--bare "${CLAUDE_ARGS[@]}")
fi

# Pipe the sample bytes into claude via stdin (avoids E2BIG on large inputs).
# Wrap through codeburn for cost capture; codeburn passes claude's JSON envelope
# through stdout and emits CODEBURN_COST_USD=<float> on stderr.
TMP_OUT="$(mktemp)"
TMP_ERR="$(mktemp)"
trap 'rm -f "${TMP_OUT}" "${TMP_ERR}"' EXIT

START_NS=$(date +%s%N)
< "${SAMPLE}" claude "${CLAUDE_ARGS[@]}" | npx codeburn > "${TMP_OUT}" 2> "${TMP_ERR}"
END_NS=$(date +%s%N)
WALL_SECONDS="$(awk -v s="${START_NS}" -v e="${END_NS}" 'BEGIN { printf "%.3f", (e - s) / 1e9 }')"

# Parse claude's JSON envelope for the result + usage.
SUMMARY="$(jq -r '.result' < "${TMP_OUT}")"
INPUT_TOKENS="$(jq -r '.usage.input_tokens // 0' < "${TMP_OUT}")"
OUTPUT_TOKENS="$(jq -r '.usage.output_tokens // 0' < "${TMP_OUT}")"
RESPONSE_MODEL="$(jq -r '.model // ""' < "${TMP_OUT}")"

# Cost from codeburn's stderr line.
COST_USD="$(grep -oE 'CODEBURN_COST_USD=[0-9.]+' "${TMP_ERR}" | tail -n1 | cut -d= -f2 || echo 0)"
COST_USD="${COST_USD:-0}"

printf '%s' "${SUMMARY}" > "${VARIANT_DIR}/summary.md"

cat > "${VARIANT_DIR}/meta.json" <<EOF
{
  "variant": "${VARIANT}",
  "transport": "cc-cli",
  "config": "${CONFIG}",
  "model": "${RESPONSE_MODEL:-${MODEL}}",
  "wall_seconds": ${WALL_SECONDS},
  "cost_usd": ${COST_USD},
  "input_tokens": ${INPUT_TOKENS},
  "output_tokens": ${OUTPUT_TOKENS}
}
EOF

echo "wrote ${VARIANT_DIR}/{summary.md,meta.json}"
