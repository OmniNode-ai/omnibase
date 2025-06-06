# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:28.078162'
# description: Stamped by PythonHandler
# entrypoint: python://test_schema_evolution.py
# hash: 71f696699c18ae44a533bca6a9ec4945fa4b8b3997e887b7fdacc49948b6992d
# last_modified_at: '2025-05-29T13:43:05.331765+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_schema_evolution.py
# namespace:
#   value: py://omnibase.tests.schema_tests.test_schema_evolution_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 4aa0f23f-bdda-4825-82e5-99dbe1506eaf
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Test cases for schema evolution and backward compatibility.

This module tests that schema changes maintain backward compatibility
and that evolution mechanisms work correctly using registry-driven,
fixture-injected, protocol-first testing patterns.
"""

from typing import Any, Callable, Dict, List, Optional

import pytest
from pydantic import ValidationError

from omnibase.core.core_error_codes import CoreErrorCode, OnexError
from omnibase.enums import NodeMetadataField
from omnibase.model.model_node_metadata import (
    EntrypointBlock,
    EntrypointType,
    Lifecycle,
    MetaTypeEnum,
    NodeMetadataBlock,
)

# Context constants for fixture parameterization
MOCK_CONTEXT = 1
INTEGRATION_CONTEXT = 2


class SchemaEvolutionTestCase:
    """Base class for schema evolution test cases."""

    def __init__(
        self,
        test_id: str,
        description: str,
        metadata: Dict[str, Any],
        expected_valid: bool = True,
        expected_error: Optional[str] = None,
    ) -> None:
        self.test_id = test_id
        self.description = description
        self.metadata = metadata
        self.expected_valid = expected_valid
        self.expected_error = expected_error


class SchemaEvolutionTestRegistry:
    """Registry for schema evolution test cases."""

    def __init__(self) -> None:
        self._test_cases: Dict[str, SchemaEvolutionTestCase] = {}

    def register(self, test_case: SchemaEvolutionTestCase) -> None:
        """Register a test case."""
        self._test_cases[test_case.test_id] = test_case

    def get_test_case(self, test_id: str) -> SchemaEvolutionTestCase:
        """Get a test case by ID."""
        return self._test_cases[test_id]

    def get_all_test_cases(self) -> List[SchemaEvolutionTestCase]:
        """Get all registered test cases."""
        return list(self._test_cases.values())

    def get_valid_test_cases(self) -> List[SchemaEvolutionTestCase]:
        """Get all test cases that should validate successfully."""
        return [tc for tc in self._test_cases.values() if tc.expected_valid]

    def get_invalid_test_cases(self) -> List[SchemaEvolutionTestCase]:
        """Get all test cases that should fail validation."""
        return [tc for tc in self._test_cases.values() if not tc.expected_valid]


# Global registry instance
# TODO: Convert to decorator-based registration in future milestone
_schema_evolution_registry = SchemaEvolutionTestRegistry()


def register_schema_evolution_test_case(test_case: SchemaEvolutionTestCase) -> None:
    """Register a schema evolution test case."""
    _schema_evolution_registry.register(test_case)


def _create_base_metadata() -> Dict[str, Any]:
    """Create base metadata with all required fields using canonical enums."""
    return {
        NodeMetadataField.METADATA_VERSION.value: "0.1.0",
        NodeMetadataField.PROTOCOL_VERSION.value: "1.1.0",
        NodeMetadataField.SCHEMA_VERSION.value: "1.1.0",
        NodeMetadataField.NAME.value: "test_node",
        NodeMetadataField.VERSION.value: "1.0.0",
        NodeMetadataField.UUID.value: "550e8400-e29b-41d4-a716-446655440000",
        NodeMetadataField.AUTHOR.value: "Test Author",
        NodeMetadataField.CREATED_AT.value: "2025-05-25T10:00:00.000000",
        NodeMetadataField.LAST_MODIFIED_AT.value: "2025-05-25T10:00:00.000000",
        NodeMetadataField.DESCRIPTION.value: "Test node for schema evolution",
        NodeMetadataField.STATE_CONTRACT.value: "state_contract://default",
        NodeMetadataField.LIFECYCLE.value: Lifecycle.ACTIVE.value,
        NodeMetadataField.HASH.value: "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        NodeMetadataField.ENTRYPOINT.value: EntrypointBlock(
            type="python", target="test_node.py"
        ),
        NodeMetadataField.NAMESPACE.value: "omnibase.test.node",
        NodeMetadataField.META_TYPE.value: MetaTypeEnum.TOOL.value,
    }


# Register test cases using the registry pattern
# TODO: Convert to decorator-based registration in future milestone

# V1.0 backward compatibility test case
v1_metadata = _create_base_metadata()
v1_metadata.update(
    {
        NodeMetadataField.PROTOCOL_VERSION.value: "1.0.0",
        NodeMetadataField.SCHEMA_VERSION.value: "1.0.0",
        NodeMetadataField.NAME.value: "legacy_node",
    }
)
register_schema_evolution_test_case(
    SchemaEvolutionTestCase(
        "v1_0_backward_compatibility",
        "V1.0 metadata format should still validate",
        v1_metadata,
    )
)

# Minimal metadata test case
minimal_metadata = _create_base_metadata()
minimal_metadata[NodeMetadataField.NAME.value] = "minimal_node"
register_schema_evolution_test_case(
    SchemaEvolutionTestCase(
        "minimal_metadata_compatibility",
        "Minimal metadata without optional fields should validate",
        minimal_metadata,
    )
)

# Deprecated field handling test case
deprecated_metadata = _create_base_metadata()
deprecated_metadata.update(
    {
        NodeMetadataField.NAME.value: "deprecated_field_node",
        "deprecated_field": "this_should_be_ignored",  # Simulated deprecated field
    }
)
register_schema_evolution_test_case(
    SchemaEvolutionTestCase(
        "deprecated_field_handling",
        "Metadata with deprecated fields should validate and ignore deprecated fields",
        deprecated_metadata,
    )
)

# Lifecycle enum evolution test cases
for lifecycle in Lifecycle:
    lifecycle_metadata = _create_base_metadata()
    lifecycle_metadata.update(
        {
            NodeMetadataField.NAME.value: f"lifecycle_{lifecycle.value}_node",
            NodeMetadataField.LIFECYCLE.value: lifecycle.value,
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"lifecycle_enum_{lifecycle.value}",
            f"Lifecycle value {lifecycle.value} should validate",
            lifecycle_metadata,
        )
    )

# Entrypoint type evolution test cases
for entrypoint_type in EntrypointType:
    entrypoint_metadata = _create_base_metadata()
    entrypoint_metadata.update(
        {
            NodeMetadataField.NAME.value: f"entrypoint_{entrypoint_type.value}_node",
            NodeMetadataField.ENTRYPOINT.value: EntrypointBlock(
                type=entrypoint_type.value,
                target=f"{entrypoint_type.value}://test_node.{entrypoint_type.value}",
            ),
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"entrypoint_type_{entrypoint_type.value}",
            f"Entrypoint type {entrypoint_type.value} should validate",
            entrypoint_metadata,
        )
    )

# Meta type evolution test cases
for meta_type in MetaTypeEnum:
    meta_type_metadata = _create_base_metadata()
    meta_type_metadata.update(
        {
            NodeMetadataField.NAME.value: f"meta_{meta_type.value}_node",
            NodeMetadataField.META_TYPE.value: meta_type.value,
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"meta_type_{meta_type.value}",
            f"Meta type {meta_type.value} should validate",
            meta_type_metadata,
        )
    )

# Add explicit test case for meta_type_project using ProjectMetadataBlock fields
project_metadata = {
    NodeMetadataField.METADATA_VERSION.value: "0.1.0",
    NodeMetadataField.PROTOCOL_VERSION.value: "0.1.0",
    NodeMetadataField.SCHEMA_VERSION.value: "0.1.0",
    NodeMetadataField.NAME.value: "meta_project_node",
    NodeMetadataField.NAMESPACE.value: "omnibase.project",
    NodeMetadataField.AUTHOR.value: "Test Author",
    NodeMetadataField.DESCRIPTION.value: "Test project metadata",
    NodeMetadataField.LIFECYCLE.value: Lifecycle.ACTIVE.value,
    NodeMetadataField.ENTRYPOINT.value: EntrypointBlock(
        type="yaml", target="project.onex.yaml"
    ),
    NodeMetadataField.META_TYPE.value: MetaTypeEnum.PROJECT.value,
    NodeMetadataField.CREATED_AT.value: "2025-05-25T10:00:00.000000",
    NodeMetadataField.LAST_MODIFIED_AT.value: "2025-05-25T10:00:00.000000",
    NodeMetadataField.HASH.value: "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    NodeMetadataField.VERSION.value: "1.0.0",
    NodeMetadataField.UUID.value: "550e8400-e29b-41d4-a716-446655440000",
    "copyright": "Test Copyright",
}
register_schema_evolution_test_case(
    SchemaEvolutionTestCase(
        "meta_type_project",
        "Meta type project should validate (ProjectMetadataBlock)",
        project_metadata,
    )
)

# Version format test cases
version_formats = ["1.0.0", "2.1.3", "10.20.30"]
for version in version_formats:
    version_metadata = _create_base_metadata()
    version_metadata.update(
        {
            NodeMetadataField.NAME.value: f"version_{version.replace('.', '_')}_node",
            NodeMetadataField.VERSION.value: version,
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"version_format_{version.replace('.', '_')}",
            f"Version format {version} should validate",
            version_metadata,
        )
    )

# Namespace pattern test cases
namespaces = [
    "omnibase.simple",
    "omnibase.multi.level.namespace",
    "omnibase.legacy.format",
    "omnibase.with_underscores",
    "omnibase.with123numbers",
]
for i, namespace in enumerate(namespaces):
    namespace_metadata = _create_base_metadata()
    namespace_metadata.update(
        {
            NodeMetadataField.NAME.value: f"namespace_test_{i}_node",
            NodeMetadataField.NAMESPACE.value: namespace,
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"namespace_pattern_{i}",
            f"Namespace pattern {namespace} should validate",
            namespace_metadata,
        )
    )

# Valid hash format test cases
valid_hashes = [
    "a" * 64,  # All lowercase
    "A" * 64,  # All uppercase
    "1234567890abcdef" * 4,  # Mixed hex
    "ABCDEF1234567890" * 4,  # Mixed case hex
]
for i, hash_value in enumerate(valid_hashes):
    hash_metadata = _create_base_metadata()
    hash_metadata.update(
        {
            NodeMetadataField.NAME.value: f"hash_test_{i}_node",
            NodeMetadataField.HASH.value: hash_value,
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"valid_hash_format_{i}",
            f"Valid hash format {i} should validate",
            hash_metadata,
        )
    )

# Invalid hash format test cases (should fail validation)
invalid_hashes = [
    "short",  # Too short
    "a" * 63,  # One character short
    "a" * 65,  # One character too long
    "g" * 64,  # Invalid hex character
    "abcd-efgh-" + "a" * 54,  # Contains hyphens
]
for i, hash_value in enumerate(invalid_hashes):
    invalid_hash_metadata = _create_base_metadata()
    invalid_hash_metadata.update(
        {
            NodeMetadataField.NAME.value: "invalid_hash_node",
            NodeMetadataField.HASH.value: hash_value,
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"invalid_hash_format_{i}",
            f"Invalid hash format {i} should fail validation",
            invalid_hash_metadata,
            expected_valid=False,
            expected_error="validation error",
        )
    )

# UUID format test cases
valid_uuids = [
    "550e8400-e29b-41d4-a716-446655440000",  # Standard UUID4
    "6ba7b810-9dad-11d1-80b4-00c04fd430c8",  # UUID1
    "6ba7b811-9dad-11d1-80b4-00c04fd430c8",  # UUID2
    "6ba7b812-9dad-11d1-80b4-00c04fd430c8",  # UUID3
    "550e8400-e29b-41d4-a716-446655440001",  # UUID5
]
for i, uuid_value in enumerate(valid_uuids):
    uuid_metadata = _create_base_metadata()
    uuid_metadata.update(
        {
            NodeMetadataField.NAME.value: "uuid_test_node",
            NodeMetadataField.UUID.value: uuid_value,
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"uuid_format_{i}", f"UUID format {i} should validate", uuid_metadata
        )
    )

# Timestamp format test cases
valid_timestamps = [
    "2025-05-25T10:00:00.000000",  # Microseconds
    "2025-05-25T10:00:00.000",  # Milliseconds
    "2025-05-25T10:00:00",  # Seconds only
    "2025-12-31T23:59:59.999999",  # End of year
    "2025-01-01T00:00:00.000000",  # Start of year
]
for i, timestamp in enumerate(valid_timestamps):
    timestamp_metadata = _create_base_metadata()
    timestamp_metadata.update(
        {
            NodeMetadataField.NAME.value: "timestamp_test_node",
            NodeMetadataField.CREATED_AT.value: timestamp,
            NodeMetadataField.LAST_MODIFIED_AT.value: timestamp,
        }
    )
    register_schema_evolution_test_case(
        SchemaEvolutionTestCase(
            f"timestamp_format_{i}",
            f"Timestamp format {i} should validate",
            timestamp_metadata,
        )
    )

# Extension fields test case
extension_metadata = _create_base_metadata()
extension_metadata.update(
    {
        NodeMetadataField.NAME.value: "extension_test_node",
        "x_extensions": {
            "custom_field": "custom_value",
            "organization": "test_org",
            "internal_id": 12345,
        },
    }
)
register_schema_evolution_test_case(
    SchemaEvolutionTestCase(
        "extension_fields_preservation",
        "Extension fields should be preserved",
        extension_metadata,
    )
)


@pytest.fixture(
    params=[
        pytest.param(MOCK_CONTEXT, id="mock", marks=pytest.mark.mock),
        pytest.param(
            INTEGRATION_CONTEXT, id="integration", marks=pytest.mark.integration
        ),
    ]
)
def schema_evolution_registry(
    request: pytest.FixtureRequest,
) -> SchemaEvolutionTestRegistry:
    """
    Canonical registry fixture for schema evolution tests.

    Context mapping:
      MOCK_CONTEXT = 1 (mock context; in-memory registry)
      INTEGRATION_CONTEXT = 2 (integration context; full registry with all test cases)

    Returns:
        SchemaEvolutionTestRegistry: Registry instance in the appropriate context.

    Raises:
        OnexError: If an unknown context is requested.
    """
    if request.param == MOCK_CONTEXT:
        # In mock context, return a subset of test cases for faster execution
        mock_registry = SchemaEvolutionTestRegistry()
        # Register essential test cases for mock context - include all test cases that tests expect
        essential_cases = [
            "v1_0_backward_compatibility",
            "minimal_metadata_compatibility",
            "lifecycle_enum_active",
            "lifecycle_enum_draft",
            "lifecycle_enum_deprecated",
            "lifecycle_enum_archived",
            "entrypoint_type_python",
            "entrypoint_type_cli",
            "entrypoint_type_docker",
            "entrypoint_type_markdown",
            "entrypoint_type_yaml",
            "entrypoint_type_json",
            "entrypoint_type_typescript",
            "entrypoint_type_javascript",
            "entrypoint_type_html",
            "meta_type_tool",
            "meta_type_validator",
            "meta_type_agent",
            "meta_type_model",
            "meta_type_schema",
            "meta_type_plugin",
            "meta_type_node",
            "meta_type_ignore_config",
            "meta_type_unknown",
            "meta_type_project",
            "extension_fields_preservation",
            "valid_hash_format_0",
        ]
        # Protocol-pure debug log emit for traceability
        import inspect
        from datetime import datetime, timezone

        from omnibase.model.model_log_entry import LogEntryModel, LogLevelEnum

        frame = inspect.currentframe()
        outer = inspect.getouterframes(frame)[1]
        context = {
            "calling_module": outer.frame.f_globals.get("__name__", "unknown"),
            "calling_function": outer.function,
            "calling_line": outer.lineno,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        log_entry = LogEntryModel(
            level=LogLevelEnum.DEBUG,
            message="Schema evolution mock context essential_cases",
            context=context,
            metadata={"essential_cases": essential_cases},
        )
        # Use protocol-pure logging utility if available, else fallback to print for CI logs
        try:
            from omnibase.core.core_structured_logging import emit_log_event_sync

            emit_log_event_sync(log_entry)
        except Exception:
            pass
        for case_id in essential_cases:
            if case_id in _schema_evolution_registry._test_cases:
                mock_registry.register(
                    _schema_evolution_registry.get_test_case(case_id)
                )
        return mock_registry
    elif request.param == INTEGRATION_CONTEXT:
        # In integration context, return the full registry
        return _schema_evolution_registry
    else:
        raise OnexError(
            f"Unknown schema evolution registry context: {request.param}",
            CoreErrorCode.INVALID_PARAMETER,
        )


@pytest.fixture
def metadata_validator() -> Callable[[Dict[str, Any]], NodeMetadataBlock]:
    """Fixture providing metadata validation functionality."""

    def validate_metadata(metadata: Dict[str, Any]) -> NodeMetadataBlock:
        """Validate metadata and return NodeMetadataBlock instance."""
        return NodeMetadataBlock(**metadata)

    return validate_metadata


class TestSchemaEvolution:
    """Test schema evolution and backward compatibility using registry-driven patterns."""

    def test_enum_model_sync(self) -> None:
        """Test that NodeMetadataField enum stays in sync with NodeMetadataBlock model."""
        model_fields = set(NodeMetadataBlock.model_fields.keys())
        enum_fields = set(field.value for field in NodeMetadataField)

        # Check that all enum fields exist in model
        missing_in_model = enum_fields - model_fields
        assert not missing_in_model, f"Enum fields missing in model: {missing_in_model}"

        # Check that all model fields exist in enum
        missing_in_enum = model_fields - enum_fields
        assert not missing_in_enum, f"Model fields missing in enum: {missing_in_enum}"

    def test_valid_metadata_cases(
        self,
        schema_evolution_registry: SchemaEvolutionTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that all valid metadata cases validate successfully."""
        valid_cases = schema_evolution_registry.get_valid_test_cases()
        assert len(valid_cases) > 0, "No valid test cases found in registry"

        for test_case in valid_cases:
            # Use model-based validation instead of string assertions
            metadata_block = metadata_validator(test_case.metadata)

            # Validate using canonical enum fields
            assert hasattr(metadata_block, NodeMetadataField.NAME.value)
            assert hasattr(metadata_block, NodeMetadataField.LIFECYCLE.value)
            assert hasattr(metadata_block, NodeMetadataField.VERSION.value)

            # Validate specific field values using model properties
            assert metadata_block.name is not None
            assert metadata_block.lifecycle in Lifecycle
            assert metadata_block.version is not None

    def test_invalid_metadata_cases(
        self,
        schema_evolution_registry: SchemaEvolutionTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that invalid metadata cases fail validation as expected."""
        invalid_cases = schema_evolution_registry.get_invalid_test_cases()

        for test_case in invalid_cases:
            with pytest.raises(ValidationError) as exc_info:
                metadata_validator(test_case.metadata)

            # Validate that the error is related to the expected issue
            if test_case.expected_error:
                assert test_case.expected_error in str(exc_info.value).lower()

    def test_backward_compatibility_v1_0(
        self,
        schema_evolution_registry: SchemaEvolutionTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test specific v1.0 backward compatibility."""
        test_case = schema_evolution_registry.get_test_case(
            "v1_0_backward_compatibility"
        )
        metadata_block = metadata_validator(test_case.metadata)

        # Use model-based assertions
        assert metadata_block.name == "legacy_node"
        assert metadata_block.lifecycle == Lifecycle.ACTIVE
        assert metadata_block.protocol_version == "1.0.0"
        assert metadata_block.schema_version == "1.0.0"

    def test_lifecycle_enum_evolution(
        self,
        schema_evolution_registry: SchemaEvolutionTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that all lifecycle enum values validate correctly."""
        for lifecycle in Lifecycle:
            test_case_id = f"lifecycle_enum_{lifecycle.value}"
            test_case = schema_evolution_registry.get_test_case(test_case_id)
            metadata_block = metadata_validator(test_case.metadata)

            # Use enum-based assertion instead of string comparison
            assert metadata_block.lifecycle == lifecycle

    def test_entrypoint_type_evolution(
        self,
        schema_evolution_registry: SchemaEvolutionTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that all entrypoint types validate correctly."""
        for entrypoint_type in EntrypointType:
            test_case_id = f"entrypoint_type_{entrypoint_type.value}"
            test_case = schema_evolution_registry.get_test_case(test_case_id)
            metadata_block = metadata_validator(test_case.metadata)

            # Use enum-based assertion
            assert metadata_block.entrypoint.type == entrypoint_type.value

    def test_meta_type_evolution(
        self,
        schema_evolution_registry: SchemaEvolutionTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that all meta types validate correctly."""
        for meta_type in MetaTypeEnum:
            test_case_id = f"meta_type_{meta_type.value}"
            test_case = schema_evolution_registry.get_test_case(test_case_id)
            metadata_block = metadata_validator(test_case.metadata)

            # Use enum-based assertion
            assert metadata_block.meta_type == meta_type

    def test_extension_fields_preservation(
        self,
        schema_evolution_registry: SchemaEvolutionTestRegistry,
        metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock],
    ) -> None:
        """Test that extension fields are preserved."""
        test_case = schema_evolution_registry.get_test_case(
            "extension_fields_preservation"
        )
        metadata_block = metadata_validator(test_case.metadata)

        # Use model-based assertions for extension fields
        assert hasattr(metadata_block, "x_extensions")
        assert metadata_block.x_extensions["custom_field"].value == "custom_value"
        assert metadata_block.x_extensions["organization"].value == "test_org"
        assert metadata_block.x_extensions["internal_id"].value == 12345

    def test_schema_serialization_stability(
        self, metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock]
    ) -> None:
        """Test that schema serialization remains stable."""
        base_metadata = _create_base_metadata()
        base_metadata[NodeMetadataField.NAME.value] = "serialization_test_node"

        metadata_block = metadata_validator(base_metadata)

        # Test model serialization using model_dump
        model_dict = metadata_block.model_dump()
        assert model_dict["name"] == "serialization_test_node"
        assert model_dict["lifecycle"] == Lifecycle.ACTIVE.value

        # Test round-trip serialization using model validation
        reconstructed = NodeMetadataBlock.from_serializable_dict(model_dict)

        # Use model-based comparison
        assert reconstructed.name == metadata_block.name
        assert reconstructed.lifecycle == metadata_block.lifecycle

    def test_template_node_traceability_fields(self):
        from src.omnibase.nodes.template_node.v1_0_0.models.state import TemplateNodeInputState, TemplateNodeOutputState
        trace_fields = [
            "event_id",
            "correlation_id",
            "node_name",
            "node_version",
            "timestamp",
        ]
        for field in trace_fields:
            assert field in TemplateNodeInputState.model_fields, f"InputState missing field: {field}"
            assert field in TemplateNodeOutputState.model_fields, f"OutputState missing field: {field}"


class TestSchemaVersioning:
    """Test schema versioning mechanisms using registry-driven patterns."""

    def test_metadata_version_tracking(
        self, metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock]
    ) -> None:
        """Test that metadata version is properly tracked."""
        base_metadata = _create_base_metadata()
        base_metadata[NodeMetadataField.NAME.value] = "version_tracking_node"

        metadata_block = metadata_validator(base_metadata)

        # Use model properties instead of string assertions
        assert metadata_block.metadata_version == "0.1.0"
        assert metadata_block.protocol_version == "1.1.0"
        assert metadata_block.schema_version == "1.1.0"

    def test_schema_version_compatibility_matrix(
        self, metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock]
    ) -> None:
        """Test compatibility matrix for different schema versions."""
        compatible_versions = [
            ("1.0.0", "1.0.0"),  # Exact match
            ("1.0.0", "1.1.0"),  # Minor version increase
            ("1.1.0", "1.1.1"),  # Patch version increase
        ]

        for old_version, new_version in compatible_versions:
            metadata = _create_base_metadata()
            metadata.update(
                {
                    NodeMetadataField.NAME.value: "compatibility_test_node",
                    NodeMetadataField.SCHEMA_VERSION.value: old_version,
                }
            )

            # Should validate successfully using model validation
            metadata_block = metadata_validator(metadata)
            assert metadata_block.schema_version == old_version

    def test_future_schema_version_handling(
        self, metadata_validator: Callable[[Dict[str, Any]], NodeMetadataBlock]
    ) -> None:
        """Test handling of future schema versions."""
        metadata = _create_base_metadata()
        metadata.update(
            {
                NodeMetadataField.NAME.value: "future_schema_node",
                NodeMetadataField.SCHEMA_VERSION.value: "2.0.0",  # Future version
            }
        )

        # Should still validate (forward compatibility)
        metadata_block = metadata_validator(metadata)
        assert metadata_block.schema_version == "2.0.0"


if __name__ == "__main__":
    pytest.main([__file__])
