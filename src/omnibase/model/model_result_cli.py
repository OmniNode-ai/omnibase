# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# schema_version: 1.1.0
# uuid: 1e0c15a3-90c9-4999-b8c4-7ba02f6f860f
# name: model_result_cli.py
# version: 1.0.0
# author: OmniNode Team
# created_at: 2025-05-19T16:20:02.924346
# last_modified_at: 2025-05-19T16:20:02.924348
# description: Stamped Python file: model_result_cli.py
# state_contract: none
# lifecycle: active
# hash: a740ee745bf90a0645c32bdc3e8edd146df60bc55112a357474b63b8032cc06b
# entrypoint: {'type': 'python', 'target': 'model_result_cli.py'}
# namespace: onex.stamped.model_result_cli.py
# meta_type: tool
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
