
# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "model_result_cli"
# namespace: "omninode.tools.model_result_cli"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "model_result_cli.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Metadata ===





"""
ModelResultCLI: Canonical Pydantic model for structured CLI output/results.
"""
from pydantic import BaseModel
from typing import Optional, List, Any, Dict

class ModelResultCLI(BaseModel):
    exit_code: int
    output: Optional[str] = None
    errors: Optional[List[str]] = None
    result: Optional[Any] = None  # Can be further typed for specific tools/validators
    metadata: Optional[Dict[str, Any]] = None 