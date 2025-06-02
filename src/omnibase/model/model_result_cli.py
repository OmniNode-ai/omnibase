# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T13:24:08.058170'
# description: Stamped by PythonHandler
# entrypoint: python://model_result_cli
# hash: f9d42025dba161f3fbd7e72812b0af89c2b9f8644615f98da7ba18212d09237e
# last_modified_at: '2025-05-29T14:13:58.926400+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: model_result_cli.py
# namespace: python://omnibase.model.model_result_cli
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
    # Use Optional[Any] instead of Optional[BaseModel] to avoid PydanticUserError.
    # TODO: Replace Any with Union of allowed result models for stricter typing.
    result: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
