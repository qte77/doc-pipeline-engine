# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""ClassificationManifest model — optional Classify/Sort stage output."""
from __future__ import annotations

from ._common import (
    CONTRACT_VERSION_LITERAL,
    Confidence,
    ContractVersion,
    StrictModel,
)


class ClassificationItem(StrictModel):
    """One classified file with assigned domain + confidence."""

    path: str
    domain: str
    confidence: Confidence


class ClassificationManifest(StrictModel):
    """Optional Classify/Sort stage output. Reserved stub — wired in v0.2."""

    version: ContractVersion = CONTRACT_VERSION_LITERAL
    items: list[ClassificationItem]
