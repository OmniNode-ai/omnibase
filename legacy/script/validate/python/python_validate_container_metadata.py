#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: container_metadata
# namespace: omninode.tools.container_metadata
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:05+00:00
# last_modified_at: 2025-04-27T18:13:05+00:00
# entrypoint: container_metadata.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""container_metadata.py
containers.foundation.src.foundation.script.validate.container_metadata.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import yaml
from foundation.model.model_validate import ValidationIssue
from pydantic import BaseModel, field_validator

# Define allowed values
ALLOWED_PRIORITIES = ["low", "medium", "high", "critical"]
ALLOWED_MEMORY_PROFILES = ["small", "medium", "large", "xlarge"]
ALLOWED_AGENT_CLASSES = ["processor", "api", "worker", "utility", "test"]


@dataclass
class ValidationResult:
    """Class to hold validation results."""

    is_valid: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    metadata: Optional["ContainerMetadata"] = None


class ContainerMetadata(BaseModel):
    """Metadata for a container defined in container.yaml.

    Attributes:
        version: Container version.
        agent_class: Type of agent.
        priority: Container priority (low, medium, high).
        memory_profile: Memory usage profile (low, medium, high).
        retry_policy: Optional retry policy.
        tags: List of tags for the container.
    """

    version: str
    agent_class: str
    priority: str
    memory_profile: str
    retry_policy: Optional[Dict[str, Union[int, str]]] = None
    tags: Optional[List[str]] = None

    @field_validator("priority")
    def validate_priority(cls, v):
        """Validate that priority is one of the allowed values."""
        if v not in ALLOWED_PRIORITIES:
            raise ValueError(f"Priority must be one of {ALLOWED_PRIORITIES}")
        return v

    @field_validator("memory_profile")
    def validate_memory_profile(cls, v):
        """Validate that memory_profile is one of the allowed values."""
        if v not in ALLOWED_MEMORY_PROFILES:
            raise ValueError(f"Memory profile must be one of {ALLOWED_MEMORY_PROFILES}")
        return v

    @field_validator("agent_class")
    def validate_agent_class(cls, v):
        """Validate that agent_class is one of the allowed values."""
        if v not in ALLOWED_AGENT_CLASSES:
            raise ValueError(f"Agent class must be one of {ALLOWED_AGENT_CLASSES}")
        return v


def validate_container_yaml(file_path: str) -> ValidationResult:
    """Validate a container.yaml file against the ContainerMetadata model.

    Args:
        file_path: Path to the YAML file to validate

    Returns:
        ValidationResult object with validation status, errors and warnings
    """
    # Initialize result
    result = ValidationResult(is_valid=True, errors=[], warnings=[])

    # Check if file exists
    if not os.path.exists(file_path):
        result.is_valid = False
        result.errors.append(
            ValidationIssue(
                type="error", message=f"File not found: {file_path}", file=file_path
            )
        )
        return result

    try:
        # Load YAML file
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)

        # Validate against model
        try:
            metadata = ContainerMetadata(**data)
        except Exception as e:
            result.is_valid = False
            result.errors.append(
                ValidationIssue(type="error", message=str(e), file=file_path)
            )
            return result

        # Check for optional fields
        if "retry_policy" not in data:
            result.warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Optional field 'retry_policy' is missing",
                    file=file_path,
                )
            )

        if "tags" not in data:
            result.warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Optional field 'tags' is missing",
                    file=file_path,
                )
            )

        return ValidationResult(
            is_valid=True,
            errors=result.errors,
            warnings=result.warnings,
            metadata=metadata,
        )

    except yaml.YAMLError as e:
        result.is_valid = False
        result.errors.append(
            ValidationIssue(
                type="error", message=f"Invalid YAML format: {e}", file=file_path
            )
        )
        return result
    except Exception as e:
        result.is_valid = False
        result.errors.append(
            ValidationIssue(
                type="error", message=f"Unexpected error: {e}", file=file_path
            )
        )
        return result


def validate_container_yaml_content(content: str) -> ValidationResult:
    """Validate a container.yaml YAML string against the ContainerMetadata model.

    Args:
        content: YAML content as a string

    Returns:
        ValidationResult object with validation status, errors and warnings
    """
    result = ValidationResult(is_valid=True, errors=[], warnings=[])
    try:
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            result.is_valid = False
            result.errors.append(
                ValidationIssue(type="error", message="YAML content is not a dictionary.", file=None)
            )
            return result
        try:
            metadata = ContainerMetadata(**data)
        except Exception as e:
            result.is_valid = False
            result.errors.append(
                ValidationIssue(type="error", message=str(e), file=None)
            )
            return result
        if "retry_policy" not in data:
            result.warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Optional field 'retry_policy' is missing",
                    file=None,
                )
            )
        if "tags" not in data:
            result.warnings.append(
                ValidationIssue(
                    type="warning",
                    message="Optional field 'tags' is missing",
                    file=None,
                )
            )
        result.metadata = metadata
        return result
    except yaml.YAMLError as e:
        result.is_valid = False
        result.errors.append(
            ValidationIssue(
                type="error", message=f"Invalid YAML format: {e}", file=None
            )
        )
        return result
    except Exception as e:
        result.is_valid = False
        result.errors.append(
            ValidationIssue(
                type="error", message=f"Unexpected error: {e}", file=None
            )
        )
        return result
