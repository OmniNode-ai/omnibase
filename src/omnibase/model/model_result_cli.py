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
from typing import Optional, List, Dict, Any
from src.omnibase.model.model_base_result import BaseResultModel
from src.omnibase.model.model_base_error import BaseErrorModel

class CLIOutputModel(BaseModel):
    # Define fields as appropriate for your CLI output
    value: Optional[str] = None
    # Add more fields as needed

class ModelResultCLI(BaseResultModel):
    output: Optional[CLIOutputModel] = None
    errors: Optional[List[BaseErrorModel]] = None
    result: Optional[BaseModel] = None  # Or Union[...] if you have a set of known result types
    metadata: Optional[Dict[str, Any]] = None 