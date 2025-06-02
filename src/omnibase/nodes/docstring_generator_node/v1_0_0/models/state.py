# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.896736'
# description: Stamped by PythonHandler
# entrypoint: python://state
# hash: 71e70cb6a461e5d0aabd5dfaf9ca5c8926741657df016a4f3bb2f6d3680a4787
# last_modified_at: '2025-05-29T14:13:59.090159+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: state.py
# namespace: python://omnibase.nodes.docstring_generator_node.v1_0_0.models.state
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 63c899c1-7583-4207-bdb3-eab88c270807
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
State models for the docstring generator node.

This module defines the input and output state contracts for generating
markdown documentation from JSON schemas.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import OnexStatus


class DocstringGeneratorInputState(BaseModel):
    """Input state for the docstring generator node."""

    version: str = Field(default="1.0.0", description="Schema version for input state")

    schema_directory: str = Field(
        default="src/omnibase/schemas",
        description="Directory containing JSON/YAML schema files to process",
    )

    template_path: str = Field(
        default="docs/templates/schema_doc.md.j2",
        description="Path to the Jinja2 template file for documentation generation",
    )

    output_directory: str = Field(
        default="docs/generated",
        description="Directory where generated markdown files will be written",
    )

    changelog_path: Optional[str] = Field(
        default="docs/changelog.md",
        description="Optional path to changelog file to include in generated docs",
    )

    verbose: bool = Field(
        default=False, description="Enable verbose logging during generation"
    )

    include_examples: bool = Field(
        default=True, description="Include schema examples in generated documentation"
    )

    correlation_id: Optional[str] = Field(
        default=None, description="Optional correlation ID for request tracking"
    )

    @field_validator("schema_directory", "output_directory")
    @classmethod
    def validate_directories(cls, v: str) -> str:
        """Validate that directory paths are not empty."""
        if not v or not v.strip():
            raise OnexError(
                "Directory paths cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()

    @field_validator("template_path")
    @classmethod
    def validate_template_path(cls, v: str) -> str:
        """Validate template path is not empty."""
        if not v or not v.strip():
            raise OnexError(
                "Template path cannot be empty",
                CoreErrorCode.MISSING_REQUIRED_PARAMETER,
            )
        return v.strip()


class GeneratedDocument(BaseModel):
    """Information about a generated documentation file."""

    schema_name: str = Field(description="Name of the schema file (without extension)")
    schema_path: str = Field(description="Path to the source schema file")
    output_path: str = Field(description="Path to the generated markdown file")
    title: str = Field(description="Title extracted from schema")
    version: str = Field(description="Version extracted from schema")
    field_count: int = Field(description="Number of fields documented")
    example_count: int = Field(description="Number of examples included")


class DocstringGeneratorOutputState(BaseModel):
    """Output state for the docstring generator node."""

    version: str = Field(default="1.0.0", description="Schema version for output state")

    status: OnexStatus = Field(description="Overall generation status")

    message: str = Field(description="Human-readable status message")

    generated_documents: List[GeneratedDocument] = Field(
        default_factory=list,
        description="List of successfully generated documentation files",
    )

    skipped_files: List[str] = Field(
        default_factory=list, description="List of schema files that were skipped"
    )

    error_files: List[str] = Field(
        default_factory=list, description="List of schema files that caused errors"
    )

    summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Summary statistics (total_schemas, generated, skipped, errors)",
    )

    output_directory: str = Field(description="Directory where files were generated")

    correlation_id: Optional[str] = Field(
        default=None, description="Optional correlation ID for request tracking"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: OnexStatus) -> OnexStatus:
        """Validate status field."""
        if v not in [OnexStatus.SUCCESS, OnexStatus.WARNING, OnexStatus.ERROR]:
            raise OnexError(f"Invalid status: {v}", CoreErrorCode.INVALID_PARAMETER)
        return v


def create_docstring_generator_input_state(
    schema_directory: str = "src/omnibase/schemas",
    template_path: str = "docs/templates/schema_doc.md.j2",
    output_directory: str = "docs/generated",
    changelog_path: Optional[str] = "docs/changelog.md",
    verbose: bool = False,
    include_examples: bool = True,
    correlation_id: Optional[str] = None,
) -> DocstringGeneratorInputState:
    """Factory function to create DocstringGeneratorInputState."""
    return DocstringGeneratorInputState(
        schema_directory=schema_directory,
        template_path=template_path,
        output_directory=output_directory,
        changelog_path=changelog_path,
        verbose=verbose,
        include_examples=include_examples,
        correlation_id=correlation_id,
    )


def create_docstring_generator_output_state(
    status: OnexStatus,
    message: str,
    generated_documents: Optional[List[GeneratedDocument]] = None,
    skipped_files: Optional[List[str]] = None,
    error_files: Optional[List[str]] = None,
    summary: Optional[Dict[str, int]] = None,
    output_directory: str = "docs/generated",
    correlation_id: Optional[str] = None,
) -> DocstringGeneratorOutputState:
    """Factory function to create DocstringGeneratorOutputState."""
    return DocstringGeneratorOutputState(
        status=status,
        message=message,
        generated_documents=generated_documents or [],
        skipped_files=skipped_files or [],
        error_files=error_files or [],
        summary=summary or {},
        output_directory=output_directory,
        correlation_id=correlation_id,
    )
