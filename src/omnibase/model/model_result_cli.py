# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_result_cli.py
# version: 1.0.0
# uuid: 3478a453-62ac-41a8-a6fd-0ec9492b7007
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.166394
# last_modified_at: 2025-05-21T16:42:46.102290
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c1f07bb409290f82ae330e2db253d83b9157c1cd6a1df63a84ae0d92cf106337
# entrypoint: {'type': 'python', 'target': 'model_result_cli.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_result_cli
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
