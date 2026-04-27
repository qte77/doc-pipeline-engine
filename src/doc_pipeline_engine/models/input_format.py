# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""InputFormat model — meta-schema for domain-pack input format definitions."""
from __future__ import annotations

from pydantic import Field

from ._common import FormatId, SemVerString, StrictModel


class InputFormat(StrictModel):
    """Meta-schema for domain pack input format definitions. Reserved stub — wired in v0.3."""

    id: FormatId
    version: SemVerString
    file_types: list[str] = Field(min_length=1)
