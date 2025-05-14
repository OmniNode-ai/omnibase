"""
Pydantic models and validators for OmniNode metadata block schema and validation.
"""

# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "model_metadata"
# namespace: "omninode.tools.model_metadata"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:04:56+00:00"
# last_modified_at: "2025-05-05T13:04:56+00:00"
# entrypoint: "model_metadata.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseModel']
# base_class: ['BaseModel']
# mock_safe: true
# === /OmniNode:Metadata ===

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Optional
import re

class MetadataBlockModel(BaseModel):
    metadata_version: str = Field(..., description="Must be '0.1'")
    name: str = Field(..., description="Validator/tool name")
    namespace: str = Field(..., description="Namespace, e.g., omninode.tools.<name>")
    version: str = Field(..., description="Semantic version, e.g., 0.1.0")
    entrypoint: str = Field(..., description="Entrypoint file, must end with .py")
    protocols_supported: List[str] = Field(..., description="List of supported protocols")
    protocol_version: str = Field(..., description="Protocol version, e.g., 0.1.0")
    author: str = Field(...)
    owner: str = Field(...)
    copyright: str = Field(...)
    created_at: str = Field(...)
    last_modified_at: str = Field(...)
    description: Optional[str] = Field(None, description="Optional description of the validator/tool")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags")
    dependencies: Optional[List[str]] = Field(None, description="Optional list of dependencies")
    config: Optional[dict] = Field(None, description="Optional config dictionary")

    @field_validator('metadata_version')
    @classmethod
    def check_metadata_version(cls, v: str) -> str:
        if v != '0.1':
            raise ValueError("metadata_version must be '0.1'")
        return v

    @field_validator('name')
    @classmethod
    def check_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError(f"Invalid name: {v}")
        return v

    @field_validator('namespace')
    @classmethod
    def check_namespace(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_.]+$', v):
            raise ValueError(f"Invalid namespace: {v}")
        return v

    @field_validator('version')
    @classmethod
    def check_version(cls, v: str) -> str:
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError(f"Invalid version: {v}")
        return v

    @field_validator('entrypoint')
    @classmethod
    def check_entrypoint(cls, v: str) -> str:
        if not v.endswith('.py'):
            raise ValueError(f"Invalid entrypoint: {v}")
        return v

    @field_validator('protocols_supported', mode='before')
    @classmethod
    def check_protocols_supported(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            # Try to parse as list from string
            import ast
            try:
                v = ast.literal_eval(v)
            except Exception:
                raise ValueError(f"protocols_supported must be a list, got: {v}")
        if not isinstance(v, list):
            raise ValueError(f"protocols_supported must be a list, got: {v}")
        return v

class StamperIgnoreModel(BaseModel):
    ignore_files: list[str]

    def __init__(self, ignore_files: Optional[list[str]] = None) -> None:
        if ignore_files is None:
            ignore_files = [
                "containers/foundation/src/foundation/template/metadata/metadata_template_blocks.py",
            ]
        super().__init__(ignore_files=ignore_files)
        self.ignore_files = ignore_files

    def get_ignore_files(self) -> list[str]:
        return self.ignore_files 