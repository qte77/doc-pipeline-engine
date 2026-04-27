# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Common Pydantic types and base config shared across all 10 contract models."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

CONTRACT_VERSION_LITERAL = "0.1.0"
ContractVersion = Literal["0.1.0"]
"""Pinned contract schema version, mirrored across every model."""

Sha256Hex = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
"""Lowercase hex sha256 digest (64 chars)."""

SemVerString = Annotated[str, StringConstraints(pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")]
"""Semantic version string like ``1.2.3``."""

FormatId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9-]+/[a-z0-9-]+$")]
"""Domain-pack format identifier like ``mech-elec-cert/datasheet``."""

Confidence = Annotated[float, Field(ge=0, le=1)]
"""Probability-like score in [0, 1]."""


class StrictModel(BaseModel):
    """Base model that forbids unknown fields, matching ``additionalProperties: false``."""

    model_config = ConfigDict(extra="forbid")
