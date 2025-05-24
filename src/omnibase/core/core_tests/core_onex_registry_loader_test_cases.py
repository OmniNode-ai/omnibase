# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: core_onex_registry_loader_test_cases.py
# version: 1.0.0
# uuid: 6d310b0e-a852-49ea-8764-dd9fe34ab4e4
# author: OmniNode Team
# created_at: 2025-05-24T14:40:41.648632
# last_modified_at: 2025-05-24T18:52:54.042248
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 6fbe397caf63510e8b91159026f00f2ca3892343480d5deaff54e1d923c8004f
# entrypoint: python@core_onex_registry_loader_test_cases.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.core_onex_registry_loader_test_cases
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Registry-driven test cases for OnexRegistryLoader following canonical testing patterns.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from omnibase.model.enum_onex_status import OnexStatus
from omnibase.protocol.protocol_registry_loader_test_case import (
    ProtocolRegistryLoaderTestCase,
)


@dataclass
class RegistryTestData:
    """Test data for registry scenarios."""

    registry_yaml: Dict[str, Any]
    artifacts: Dict[
        str, Dict[str, Any]
    ]  # artifact_type -> {name -> {version -> files}}
    expected_total: int
    expected_valid: int
    expected_invalid: int
    expected_wip: int


class RealRegistryLoaderTestCase(ProtocolRegistryLoaderTestCase):
    """Concrete test case for registry loader scenarios."""

    def __init__(
        self,
        id: str,
        test_data: RegistryTestData,
        expected_status: OnexStatus,
        description: Optional[str] = None,
    ):
        self.id = id
        self.test_data = test_data
        self.expected_status = expected_status
        self.description = description or f"Test case: {id}"


# Registry of test cases
REGISTRY_LOADER_TEST_CASES = []

# Valid registry with metadata files
valid_registry_data = RegistryTestData(
    registry_yaml={
        "registry_schema_version": "1.0.0",
        "nodes": [
            {
                "name": "test_node",
                "versions": [
                    {
                        "version": "v1_0_0",
                        "path": "nodes/test_node/v1_0_0",
                        "metadata_file": "node.onex.yaml",
                        "status": "active",
                    }
                ],
            }
        ],
        "cli_tools": [],
        "runtimes": [],
        "adapters": [],
        "contracts": [],
        "packages": [],
    },
    artifacts={
        "nodes": {
            "test_node": {
                "v1_0_0": {
                    "node.onex.yaml": {
                        "name": "test_node",
                        "version": "v1_0_0",
                        "schema_version": "0.1.0",
                        "description": "Test node",
                    }
                }
            }
        }
    },
    expected_total=1,
    expected_valid=1,
    expected_invalid=0,
    expected_wip=0,
)

REGISTRY_LOADER_TEST_CASES.append(
    RealRegistryLoaderTestCase(
        id="valid_registry_with_metadata",
        test_data=valid_registry_data,
        expected_status=OnexStatus.SUCCESS,
        description="Valid registry with proper metadata files",
    )
)

# WIP marker test case
wip_registry_data = RegistryTestData(
    registry_yaml={
        "registry_schema_version": "1.0.0",
        "nodes": [
            {
                "name": "wip_node",
                "versions": [
                    {
                        "version": "v1_0_0",
                        "path": "nodes/wip_node/v1_0_0",
                        "metadata_file": "node.onex.yaml",
                        "status": "active",
                    }
                ],
            }
        ],
        "cli_tools": [],
        "runtimes": [],
        "adapters": [],
        "contracts": [],
        "packages": [],
    },
    artifacts={"nodes": {"wip_node": {"v1_0_0": {".wip": ""}}}},  # WIP marker file
    expected_total=1,
    expected_valid=1,
    expected_invalid=0,
    expected_wip=1,
)

REGISTRY_LOADER_TEST_CASES.append(
    RealRegistryLoaderTestCase(
        id="wip_marker_precedence",
        test_data=wip_registry_data,
        expected_status=OnexStatus.SUCCESS,
        description="WIP marker takes precedence over metadata files",
    )
)

# WIP marker with metadata file (precedence test)
wip_precedence_data = RegistryTestData(
    registry_yaml={
        "registry_schema_version": "1.0.0",
        "nodes": [
            {
                "name": "precedence_node",
                "versions": [
                    {
                        "version": "v1_0_0",
                        "path": "nodes/precedence_node/v1_0_0",
                        "metadata_file": "node.onex.yaml",
                        "status": "active",
                    }
                ],
            }
        ],
        "cli_tools": [],
        "runtimes": [],
        "adapters": [],
        "contracts": [],
        "packages": [],
    },
    artifacts={
        "nodes": {
            "precedence_node": {
                "v1_0_0": {
                    ".wip": "",  # WIP marker
                    "node.onex.yaml": {  # Also has metadata
                        "name": "precedence_node",
                        "version": "v1_0_0",
                        "schema_version": "0.1.0",
                    },
                }
            }
        }
    },
    expected_total=1,
    expected_valid=1,
    expected_invalid=0,
    expected_wip=1,
)

REGISTRY_LOADER_TEST_CASES.append(
    RealRegistryLoaderTestCase(
        id="wip_precedence_over_metadata",
        test_data=wip_precedence_data,
        expected_status=OnexStatus.SUCCESS,
        description="WIP marker takes precedence even when metadata file exists",
    )
)

# Invalid metadata test case
invalid_metadata_data = RegistryTestData(
    registry_yaml={
        "registry_schema_version": "1.0.0",
        "nodes": [
            {
                "name": "invalid_node",
                "versions": [
                    {
                        "version": "v1_0_0",
                        "path": "nodes/invalid_node/v1_0_0",
                        "metadata_file": "node.onex.yaml",
                        "status": "active",
                    }
                ],
            }
        ],
        "cli_tools": [],
        "runtimes": [],
        "adapters": [],
        "contracts": [],
        "packages": [],
    },
    artifacts={
        "nodes": {
            "invalid_node": {
                "v1_0_0": {
                    "node.onex.yaml": {
                        "description": "Missing required fields"
                        # Missing name, version, schema_version
                    }
                }
            }
        }
    },
    expected_total=1,
    expected_valid=0,
    expected_invalid=1,
    expected_wip=0,
)

REGISTRY_LOADER_TEST_CASES.append(
    RealRegistryLoaderTestCase(
        id="invalid_metadata_validation",
        test_data=invalid_metadata_data,
        expected_status=OnexStatus.SUCCESS,  # Loader succeeds but marks artifact as invalid
        description="Invalid metadata files are handled gracefully",
    )
)

# Missing metadata file test case
missing_metadata_data = RegistryTestData(
    registry_yaml={
        "registry_schema_version": "1.0.0",
        "nodes": [
            {
                "name": "missing_metadata_node",
                "versions": [
                    {
                        "version": "v1_0_0",
                        "path": "nodes/missing_metadata_node/v1_0_0",
                        "metadata_file": "node.onex.yaml",
                        "status": "active",
                    }
                ],
            }
        ],
        "cli_tools": [],
        "runtimes": [],
        "adapters": [],
        "contracts": [],
        "packages": [],
    },
    artifacts={
        "nodes": {
            "missing_metadata_node": {
                "v1_0_0": {
                    # No metadata file or .wip marker
                }
            }
        }
    },
    expected_total=1,
    expected_valid=0,
    expected_invalid=1,
    expected_wip=0,
)

REGISTRY_LOADER_TEST_CASES.append(
    RealRegistryLoaderTestCase(
        id="missing_metadata_file",
        test_data=missing_metadata_data,
        expected_status=OnexStatus.SUCCESS,  # Loader succeeds but marks artifact as invalid
        description="Missing metadata file without .wip marker is invalid",
    )
)

# Multiple artifact types test case
multiple_artifacts_data = RegistryTestData(
    registry_yaml={
        "registry_schema_version": "1.0.0",
        "nodes": [
            {
                "name": "node1",
                "versions": [
                    {
                        "version": "v1_0_0",
                        "path": "nodes/node1/v1_0_0",
                        "metadata_file": "node.onex.yaml",
                        "status": "active",
                    }
                ],
            }
        ],
        "cli_tools": [
            {
                "name": "tool1",
                "versions": [
                    {
                        "version": "v1_0_0",
                        "path": "cli_tools/tool1/v1_0_0",
                        "metadata_file": "cli_tool.yaml",
                        "status": "active",
                    }
                ],
            }
        ],
        "runtimes": [],
        "adapters": [],
        "contracts": [],
        "packages": [],
    },
    artifacts={
        "nodes": {"node1": {"v1_0_0": {".wip": ""}}},  # WIP marker
        "cli_tools": {"tool1": {"v1_0_0": {".wip": ""}}},  # WIP marker
    },
    expected_total=2,
    expected_valid=2,
    expected_invalid=0,
    expected_wip=2,
)

REGISTRY_LOADER_TEST_CASES.append(
    RealRegistryLoaderTestCase(
        id="multiple_artifact_types",
        test_data=multiple_artifacts_data,
        expected_status=OnexStatus.SUCCESS,
        description="Multiple artifact types are loaded correctly",
    )
)
