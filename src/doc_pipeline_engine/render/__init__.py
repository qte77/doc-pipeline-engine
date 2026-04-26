# Copyright 2026 qte77
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
"""Shared render utilities. Both V1 (Claude-written Markdown) and V2
(Jinja-rendered Markdown) feed through ``render_artifacts`` so the A/B
between variants is about the Markdown content, not the conversion path.
"""
from doc_pipeline_engine.render.formats import RenderArtifacts, render_artifacts

__all__ = ["RenderArtifacts", "render_artifacts"]
