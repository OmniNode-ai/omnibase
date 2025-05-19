"""
Pydantic models and validators for OmniNode metadata block schema and validation.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.model.model_enum_metadata import (
    MetaTypeEnum,
    ProtocolVersionEnum,
    RuntimeLanguageEnum,
)
from omnibase.model.model_metadata_config import MetadataConfigModel


class MetadataBlockModel(BaseModel):
    metadata_version: str = Field(
        ..., description="Must be a semver string, e.g., '0.1.0'"
    )
    name: str = Field(..., description="Validator/tool name")
    namespace: str = Field(..., description="Namespace, e.g., omninode.tools.<name>")
    version: str = Field(..., description="Semantic version, e.g., 0.1.0")
    entrypoint: Dict[str, Any] = Field(
        ..., description="Entrypoint object with 'type' and 'target'"
    )  # Arbitrary structure, extensible
    protocols_supported: List[str] = Field(
        ..., description="List of supported protocols"
    )
    protocol_version: ProtocolVersionEnum = Field(
        ..., description="Protocol version, e.g., 0.1.0"
    )
    author: str = Field(...)
    owner: str = Field(...)
    copyright: str = Field(...)
    created_at: str = Field(...)
    last_modified_at: str = Field(...)
    description: Optional[str] = Field(
        None, description="Optional description of the validator/tool"
    )
    tags: Optional[List[str]] = Field(None, description="Optional list of tags")
    dependencies: Optional[List[str]] = Field(
        None, description="Optional list of dependencies"
    )
    config: Optional[MetadataConfigModel] = Field(
        None, description="Optional config model"
    )
    meta_type: MetaTypeEnum = Field(
        MetaTypeEnum.UNKNOWN, description="Meta type of the node/tool"
    )
    runtime_language_hint: RuntimeLanguageEnum = Field(
        RuntimeLanguageEnum.UNKNOWN, description="Runtime language hint"
    )

    @field_validator("metadata_version")
    @classmethod
    def check_metadata_version(cls, v: str) -> str:
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("metadata_version must be a semver string, e.g., '0.1.0'")
        return v

    @field_validator("name")
    @classmethod
    def check_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v):
            raise ValueError(f"Invalid name: {v}")
        return v

    @field_validator("namespace")
    @classmethod
    def check_namespace(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.]+$", v):
            raise ValueError(f"Invalid namespace: {v}")
        return v

    @field_validator("version")
    @classmethod
    def check_version(cls, v: str) -> str:
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError(f"Invalid version: {v}")
        return v

    @field_validator("protocols_supported", mode="before")
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


class MetadataModel(BaseModel):
    meta_type: str = Field(..., description="Type of metadata block")
    metadata_version: str = Field(..., description="Version of the metadata schema")
    schema_version: str = Field(..., description="Version of the content schema")
    uuid: str = Field(..., description="Unique identifier for this file")
    name: str = Field(..., description="File name")
    version: str = Field(..., description="File version")
    author: str = Field(..., description="Author of the file")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_modified_at: datetime = Field(..., description="Last modification timestamp")
    description: Optional[str] = Field(None, description="Description of the file")
    state_contract: Optional[str] = Field(None, description="State contract reference")
    lifecycle: Optional[str] = Field(None, description="Lifecycle state")
    hash: str = Field(..., description="Canonical content hash")
    entrypoint: Optional[str] = Field(None, description="Entrypoint information")
    namespace: Optional[str] = Field(None, description="Namespace for the file")
