# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: schema_version_validator.py
# version: 1.0.0
# uuid: 8a201f37-b68f-4448-a611-535e33933db7
# author: OmniNode Team
# created_at: 2025-05-25T14:59:41.337983
# last_modified_at: 2025-05-25T19:21:33.379851
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c3fb53e70a6f0cf07b2eeddc2d878f10d4a310258f38ead37a13324f1aaa3ae8
# entrypoint: python@schema_version_validator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.schema_version_validator
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Schema Version Validation Utilities for ONEX State Models.

This module provides utilities for validating and managing schema versions
across all ONEX state models, ensuring consistency and compatibility.
"""

import re
from typing import Dict, List, Optional, Tuple


class SchemaVersionError(Exception):
    """Exception raised for schema version validation errors."""

    pass


class SchemaVersionValidator:
    """
    Utility class for validating schema versions and managing compatibility.

    This class provides methods to validate semantic versions, check compatibility,
    and manage schema evolution across different state models.
    """

    # Semantic versioning regex pattern
    SEMVER_PATTERN = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"

    def __init__(self) -> None:
        """Initialize the schema version validator."""
        self._registered_schemas: Dict[str, str] = {}

    def register_schema(self, schema_name: str, current_version: str) -> None:
        """
        Register a schema with its current version.

        Args:
            schema_name: Name of the schema (e.g., "stamper_state")
            current_version: Current version of the schema

        Raises:
            SchemaVersionError: If the version format is invalid
        """
        self.validate_semantic_version(current_version)
        self._registered_schemas[schema_name] = current_version

    def validate_semantic_version(self, version: str) -> str:
        """
        Validate that a version string follows semantic versioning format.

        Args:
            version: Version string to validate

        Returns:
            The validated version string

        Raises:
            SchemaVersionError: If version doesn't match semantic versioning format
        """
        if not re.match(self.SEMVER_PATTERN, version):
            raise SchemaVersionError(
                f"Version '{version}' does not follow semantic versioning format (e.g., '1.0.0')"
            )
        return version

    def parse_version(
        self, version: str
    ) -> Tuple[int, int, int, Optional[str], Optional[str]]:
        """
        Parse a semantic version string into its components.

        Args:
            version: Version string to parse

        Returns:
            Tuple of (major, minor, patch, prerelease, build)

        Raises:
            SchemaVersionError: If version format is invalid
        """
        self.validate_semantic_version(version)
        match = re.match(self.SEMVER_PATTERN, version)
        if not match:
            raise SchemaVersionError(f"Failed to parse version '{version}'")

        major, minor, patch, prerelease, build = match.groups()
        return (int(major), int(minor), int(patch), prerelease, build)

    def is_compatible(self, requested_version: str, current_version: str) -> bool:
        """
        Check if a requested version is compatible with the current version.

        Compatibility rules:
        - Major versions must match exactly
        - Minor version can be lower or equal (backward compatibility)
        - Patch version is ignored for compatibility

        Args:
            requested_version: The version being requested
            current_version: The current schema version

        Returns:
            True if versions are compatible, False otherwise
        """
        try:
            req_major, req_minor, _, _, _ = self.parse_version(requested_version)
            cur_major, cur_minor, _, _, _ = self.parse_version(current_version)

            # Major version must match
            if req_major != cur_major:
                return False

            # Minor version can be lower or equal
            return req_minor <= cur_minor

        except SchemaVersionError:
            return False

    def validate_compatibility(
        self, requested_version: str, current_version: str
    ) -> str:
        """
        Validate that a requested version is compatible with the current version.

        Args:
            requested_version: The version being requested
            current_version: The current schema version

        Returns:
            The validated requested version

        Raises:
            SchemaVersionError: If versions are not compatible
        """
        self.validate_semantic_version(requested_version)
        self.validate_semantic_version(current_version)

        if not self.is_compatible(requested_version, current_version):
            req_major, req_minor, _, _, _ = self.parse_version(requested_version)
            cur_major, cur_minor, _, _, _ = self.parse_version(current_version)

            if req_major != cur_major:
                raise SchemaVersionError(
                    f"Schema version '{requested_version}' is not compatible with current version '{current_version}'. "
                    f"Major version mismatch (requested: {req_major}, current: {cur_major}) requires migration."
                )

            if req_minor > cur_minor:
                raise SchemaVersionError(
                    f"Schema version '{requested_version}' is newer than current version '{current_version}'. "
                    f"Please upgrade the implementation to support minor version {req_minor}."
                )

        return requested_version

    def validate_schema_version(self, schema_name: str, version: str) -> str:
        """
        Validate a version for a registered schema.

        Args:
            schema_name: Name of the schema to validate against
            version: Version string to validate

        Returns:
            The validated version string

        Raises:
            SchemaVersionError: If schema is not registered or version is incompatible
        """
        if schema_name not in self._registered_schemas:
            raise SchemaVersionError(f"Schema '{schema_name}' is not registered")

        current_version = self._registered_schemas[schema_name]
        return self.validate_compatibility(version, current_version)

    def get_registered_schemas(self) -> Dict[str, str]:
        """
        Get all registered schemas and their current versions.

        Returns:
            Dictionary mapping schema names to their current versions
        """
        return self._registered_schemas.copy()

    def suggest_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """
        Suggest a migration path between two versions.

        Args:
            from_version: Starting version
            to_version: Target version

        Returns:
            List of suggested migration steps
        """
        try:
            from_major, from_minor, from_patch, _, _ = self.parse_version(from_version)
            to_major, to_minor, to_patch, _, _ = self.parse_version(to_version)
        except SchemaVersionError as e:
            return [f"Error parsing versions: {e}"]

        steps = []

        # Major version changes require explicit migration
        if from_major != to_major:
            if from_major < to_major:
                for major in range(from_major + 1, to_major + 1):
                    steps.append(f"Migrate to major version {major}.0.0")
            else:
                steps.append("Downgrading major versions is not supported")
                return steps

        # Minor version changes
        if from_minor != to_minor:
            if from_minor < to_minor:
                steps.append(f"Upgrade to minor version {to_major}.{to_minor}.0")
            else:
                steps.append("Downgrading minor versions may lose functionality")

        # Patch version changes
        if from_patch != to_patch:
            steps.append(f"Update to patch version {to_major}.{to_minor}.{to_patch}")

        if not steps:
            steps.append("No migration required - versions are identical")

        return steps


# Global schema version validator instance
_global_validator = SchemaVersionValidator()

# Register known schemas
_global_validator.register_schema("stamper_state", "1.1.1")
_global_validator.register_schema("tree_generator_state", "1.0.0")
_global_validator.register_schema("registry_loader_state", "1.0.0")
_global_validator.register_schema("template_state", "1.0.0")


def validate_semantic_version(version: str) -> str:
    """
    Validate that a version string follows semantic versioning format.

    Args:
        version: Version string to validate

    Returns:
        The validated version string

    Raises:
        SchemaVersionError: If version doesn't match semantic versioning format
    """
    return _global_validator.validate_semantic_version(version)


def validate_schema_compatibility(requested_version: str, current_version: str) -> str:
    """
    Validate that a requested version is compatible with the current version.

    Args:
        requested_version: The version being requested
        current_version: The current schema version

    Returns:
        The validated requested version

    Raises:
        SchemaVersionError: If versions are not compatible
    """
    return _global_validator.validate_compatibility(requested_version, current_version)


def validate_schema_version(schema_name: str, version: str) -> str:
    """
    Validate a version for a registered schema.

    Args:
        schema_name: Name of the schema to validate against
        version: Version string to validate

    Returns:
        The validated version string

    Raises:
        SchemaVersionError: If schema is not registered or version is incompatible
    """
    return _global_validator.validate_schema_version(schema_name, version)


def get_current_schema_version(schema_name: str) -> Optional[str]:
    """
    Get the current version for a registered schema.

    Args:
        schema_name: Name of the schema

    Returns:
        Current version string or None if schema is not registered
    """
    schemas = _global_validator.get_registered_schemas()
    return schemas.get(schema_name)


def suggest_migration_path(from_version: str, to_version: str) -> List[str]:
    """
    Suggest a migration path between two versions.

    Args:
        from_version: Starting version
        to_version: Target version

    Returns:
        List of suggested migration steps
    """
    return _global_validator.suggest_migration_path(from_version, to_version)
