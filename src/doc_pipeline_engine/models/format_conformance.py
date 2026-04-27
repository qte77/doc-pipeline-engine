# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""FormatConformance model — output format conformance gate result."""
from __future__ import annotations

from ._common import CONTRACT_VERSION_LITERAL, ContractVersion, StrictModel


class FormatConformance(StrictModel):
    """Output format conformance gate result. Reserved stub — wired in v0.2."""

    version: ContractVersion = CONTRACT_VERSION_LITERAL
    output_format_id: str
    conformant: bool
