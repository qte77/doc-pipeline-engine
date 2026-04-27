# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""OutputFormat model — meta-schema for domain-pack output format definitions."""
from __future__ import annotations

from typing import Literal

from ._common import FormatId, SemVerString, StrictModel


class OutputFormat(StrictModel):
    """Meta-schema for domain pack output format definitions. Reserved stub — wired in v0.3."""

    id: FormatId
    version: SemVerString
    tier: Literal["quick", "comprehensive", "both"]
