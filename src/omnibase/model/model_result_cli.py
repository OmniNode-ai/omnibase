# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T13:24:08.058170'
# description: Stamped by PythonHandler
# entrypoint: python://model_result_cli.py
# hash: c83779d983e368904dfdbe9630df62d656f8ff078cf304c4d6c2b4ab7d84f584
# last_modified_at: '2025-05-29T11:50:11.060164+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_result_cli.py
# namespace: omnibase.model_result_cli
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: {}
# uuid: af652fa5-b892-43e4-b5d2-4962b52539d3
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
ModelResultCLI: Canonical Pydantic model for structured CLI output/results.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from omnibase.model.model_base_error import BaseErrorModel
from omnibase.model.model_base_result import BaseResultModel


class CLIOutputModel(BaseModel):
    # Define fields as appropriate for your CLI output
    value: Optional[str] = None
    # Add more fields as needed


class ModelResultCLI(BaseResultModel):
    output: Optional[CLIOutputModel] = None
    errors: List[BaseErrorModel] = []
    result: Optional[BaseModel] = (
        None  # Or Union[BaseModel, ...] if you have a set of known result types
    )
    metadata: Optional[Dict[str, Any]] = None
