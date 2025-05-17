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
