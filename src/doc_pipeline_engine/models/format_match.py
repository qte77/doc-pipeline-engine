# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""FormatMatch model — RecognizeInputFormat stage output."""
from __future__ import annotations

from ._common import (
    CONTRACT_VERSION_LITERAL,
    Confidence,
    ContractVersion,
    StrictModel,
)


class MatchEntry(StrictModel):
    """One candidate input format with confidence."""

    format_id: str
    confidence: Confidence


class FormatMatch(StrictModel):
    """RecognizeInputFormat stage output. Reserved stub — wired in v0.2."""

    version: ContractVersion = CONTRACT_VERSION_LITERAL
    matches: list[MatchEntry]
