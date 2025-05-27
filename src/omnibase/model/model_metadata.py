# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: model_metadata.py
# version: 1.0.0
# uuid: a3e3ab50-6cb0-43e2-95f0-97653f550abc
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.165709
# last_modified_at: 2025-05-21T16:42:46.136039
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4705bd19c97d3c1000d00b7684a0ba16749bdb79b78626309d527a33c18b242f
# entrypoint: python@model_metadata.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.model_metadata
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Pydantic models and validators for OmniNode metadata block schema and validation.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import MetaTypeEnum, ProtocolVersionEnum, RuntimeLanguageEnum
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
            raise OnexError(
                "metadata_version must be a semver string, e.g., '0.1.0'",
                CoreErrorCode.VALIDATION_ERROR,
            )
        return v

    @field_validator("name")
    @classmethod
    def check_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", v):
            raise OnexError(f"Invalid name: {v}", CoreErrorCode.VALIDATION_ERROR)
        return v

    @field_validator("namespace")
    @classmethod
    def check_namespace(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_.]+$", v):
            raise OnexError(f"Invalid namespace: {v}", CoreErrorCode.VALIDATION_ERROR)
        return v

    @field_validator("version")
    @classmethod
    def check_version(cls, v: str) -> str:
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise OnexError(f"Invalid version: {v}", CoreErrorCode.VALIDATION_ERROR)
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
                raise OnexError(
                    f"protocols_supported must be a list, got: {v}",
                    CoreErrorCode.VALIDATION_ERROR,
                )
        if not isinstance(v, list):
            raise OnexError(
                f"protocols_supported must be a list, got: {v}",
                CoreErrorCode.VALIDATION_ERROR,
            )
        return v


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
