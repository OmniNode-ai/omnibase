from pydantic import BaseModel, Field
from typing import Optional, List
from omnibase.core.core_error_codes import ModelOnexError
from .model_metadata import ModelMetadata
from .model_validation_issue import ValidationIssueModel

class ModelValidationResult(BaseModel):
    """
    Canonical output model for validation engine tools.
    Contains the result of validating a node, contract, or artifact.
    Optionally includes canonical metadata.
    """
    success: bool = Field(..., description="True if validation passes, False otherwise.")
    details: Optional[str] = Field(default=None, description="Details or summary of the validation result.")
    errors: Optional[List[ModelOnexError]] = Field(default=None, description="List of ONEX error objects, if any.")
    metadata: Optional[ModelMetadata] = Field(default=None, description="Optional canonical metadata for the validation result.")

class ValidationResultModel(BaseModel):
    """Result of template validation with comprehensive metrics"""
    issues: List[ValidationIssueModel]
    error_count: int
    warning_count: int
    info_count: int
    total_files_checked: int
    node_name: str
    validation_passed: bool 