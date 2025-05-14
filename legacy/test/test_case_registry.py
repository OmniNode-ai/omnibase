# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_case_registry"
# namespace: "omninode.tools.test_case_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "test_case_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolRegistryTestCase']
# base_class: ['ProtocolRegistryTestCase']
# mock_safe: true
# === /OmniNode:Metadata ===



import os
from typing import Dict, List, Optional
from pathlib import Path

from foundation.protocol.protocol_registry_test_case import ProtocolRegistryTestCase


class DefaultTestCaseRegistry(ProtocolRegistryTestCase):
    """
    Default implementation of the test case registry.
    Provides access to test cases for various validators and tools.
    """

    def __init__(self):
        """Initialize the test case registry with all known test cases."""
        # Dictionary structure:
        # {
        #     validator_name: {
        #         case_type: {  # "valid" or "invalid"
        #             test_case_name: absolute_path_to_test_case
        #         }
        #     }
        # }
        self._cases: Dict[str, Dict[str, Dict[str, str]]] = {}
        base_dir = os.path.dirname(__file__)

        # Register protocol compatibility test cases
        protocol_compatibility_cases = {
            "valid": {
                "valid_compatible_validator": os.path.abspath(os.path.join(base_dir, "validate/protocol_compatibility/test_case/valid/valid_compatible_validator.py")),
                "valid_empty_registry": os.path.abspath(os.path.join(base_dir, "validate/protocol_compatibility/test_case/valid/valid_empty_registry.py")),
            },
            "invalid": {
                "invalid_incompatible_validator": os.path.abspath(os.path.join(base_dir, "validate/protocol_compatibility/test_case/invalid/invalid_incompatible_validator.py")),
                "invalid_multiple_versions": os.path.abspath(os.path.join(base_dir, "validate/protocol_compatibility/test_case/invalid/invalid_multiple_versions.py")),
                "invalid_broken_registry": os.path.abspath(os.path.join(base_dir, "validate/protocol_compatibility/test_case/invalid/invalid_broken_registry.py")),
            },
        }
        self._cases["protocol_compatibility"] = protocol_compatibility_cases

        # Register chunk validator test cases
        chunk_cases = {
            "valid": {
                "valid_chunk_short": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/chunk/test_case/valid/valid_chunk_short.py"
                    )
                ),
                "valid_chunk_soft_warning": os.path.abspath(
                    os.path.join(
                        base_dir,
                        "validate/chunk/test_case/valid/valid_chunk_soft_warning.py",
                    )
                ),
                # Register chunk tool valid test case
                "valid_chunk_tool_basic": os.path.abspath(
                    os.path.join(
                        base_dir,
                        "tool/chunk/test_case/valid/valid_chunk_tool_basic.py",
                    )
                ),
            },
            "invalid": {
                "invalid_chunk_hard_fail": os.path.abspath(
                    os.path.join(
                        base_dir,
                        "validate/chunk/test_case/invalid/invalid_chunk_hard_fail.py",
                    )
                ),
                # Register chunk tool invalid test case
                "invalid_chunk_tool_edge": os.path.abspath(
                    os.path.join(
                        base_dir,
                        "tool/chunk/test_case/invalid/invalid_chunk_tool_edge.py",
                    )
                ),
            },
        }
        self._cases["chunk"] = chunk_cases
        # Register metadata_block validator test cases
        metadata_block_cases = {
            "valid": {
                "valid_metadata": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/valid/valid_metadata.yaml")),
                "valid_metadata_positive": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/valid/valid_metadata_positive.yaml")),
                "valid_metadata_py": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/valid/valid_metadata_py.py")),
                "valid_metadata_yaml": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/valid/valid_metadata_yaml.yaml")),
                "valid_metadata_md": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/valid/valid_metadata_md.md")),
                "valid_metadata_with_future_imports": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/valid/valid_metadata_with_future_imports.py")),
            },
            "invalid": {
                "invalid_metadata_missing_fields": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_missing_fields.yaml")),
                "invalid_metadata_missing_owner": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_missing_owner.yaml")),
                "invalid_metadata_not_dict": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_not_dict.yaml")),
                "invalid_metadata_yaml_error": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_yaml_error.yaml")),
                "invalid_metadata_py_missing_type": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_py_missing_type.py")),
                "invalid_metadata_yaml_missing_type": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_yaml_missing_type.yaml")),
                "invalid_metadata_md_missing_type": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_md_missing_type.md")),
            },
        }
        self._cases["metadata_block"] = metadata_block_cases
        # Register registry_consistency validator test cases
        registry_consistency_cases = {
            "valid": {
                "valid_registry_consistent": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/valid/valid_registry_consistent.yaml"
                    )
                ),
                "valid_registry_consistency_empty": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/valid/valid_registry_consistency_empty.yaml"
                    )
                ),
                "valid_registry_consistency_not_a_registry": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/valid/valid_registry_consistency_not_a_registry.py"
                    )
                ),
                "valid_registry_entry_without_metadata_block": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/valid/valid_registry_entry_without_metadata_block.yaml"
                    )
                ),
            },
            "invalid": {
                "invalid_registry_missing_metadata": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/invalid/invalid_registry_missing_metadata.yaml"
                    )
                ),
                "invalid_registry_drift": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/invalid/invalid_registry_drift.yaml"
                    )
                ),
                "invalid_registry_consistency_bad": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/invalid/invalid_registry_consistency_bad.yaml"
                    )
                ),
                "invalid_registry_consistency_missing_name": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/invalid/invalid_registry_consistency_missing_name.yaml"
                    )
                ),
                "invalid_registry_consistency_extra": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/invalid/invalid_registry_consistency_extra.yaml"
                    )
                ),
                "invalid_registry_consistency_error_warning": os.path.abspath(
                    os.path.join(
                        base_dir, "validate/python/registry_consistency/test_case/invalid/invalid_registry_consistency_error_warning.yaml"
                    )
                ),
            },
        }
        self._cases["registry_consistency"] = registry_consistency_cases
        # Register model_validate_error test cases
        model_validate_error_cases = {
            "valid": {
                "valid_message_model": os.path.abspath(os.path.join(base_dir, "model/test_case/valid/valid_message_model.yaml")),
                "valid_result_model": os.path.abspath(os.path.join(base_dir, "model/test_case/valid/valid_result_model.yaml")),
            },
            "invalid": {
                "invalid_message_model": os.path.abspath(os.path.join(base_dir, "model/test_case/invalid/invalid_message_model.yaml")),
                "invalid_result_model": os.path.abspath(os.path.join(base_dir, "model/test_case/invalid/invalid_result_model.yaml")),
            },
        }
        self._cases["model_validate_error"] = model_validate_error_cases
        # Register model_validate test cases
        model_validate_cases = {
            "valid": {
                "valid_validate_status": os.path.abspath(os.path.join(base_dir, "model/test_case/valid/valid_validate_status.yaml")),
            },
            "invalid": {
                "invalid_validate_status": os.path.abspath(os.path.join(base_dir, "model/test_case/invalid/invalid_validate_status.yaml")),
            },
        }
        self._cases["model_validate"] = model_validate_cases

        # Register bootstrap import test cases
        bootstrap_import_cases = {
            "valid": {
                "valid_entrypoint_with_bootstrap": os.path.abspath(os.path.join(base_dir, "validate/python/bootstrap_import/test_case/valid/valid_entrypoint_with_bootstrap.py")),
                "non_entrypoint": os.path.abspath(os.path.join(base_dir, "validate/python/bootstrap_import/test_case/valid/non_entrypoint.py")),
            },
            "invalid": {
                "valid_entrypoint_without_bootstrap": os.path.abspath(os.path.join(base_dir, "validate/python/bootstrap_import/test_case/invalid/valid_entrypoint_without_bootstrap.py")),
                "entrypoint_with_import_only": os.path.abspath(os.path.join(base_dir, "validate/python/bootstrap_import/test_case/invalid/entrypoint_with_import_only.py")),
                "entrypoint_with_call_only": os.path.abspath(os.path.join(base_dir, "validate/python/bootstrap_import/test_case/invalid/entrypoint_with_call_only.py")),
                "invalid_python": os.path.abspath(os.path.join(base_dir, "validate/python/bootstrap_import/test_case/invalid/invalid_python.py")),
            },
        }
        self._cases["bootstrap_import"] = bootstrap_import_cases

        # Register metadata stamper test cases
        metadata_stamper_cases = {
            "valid": {
                "valid_metadata_stamper": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/valid/valid_metadata_stamper.py")),
            },
            "invalid": {
                "invalid_metadata_stamper_invalid_logger": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_invalid_logger.py")),
                "invalid_metadata_stamper_missing_registry": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_missing_registry.py")),
                "invalid_metadata_stamper_invalid_registry": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_invalid_registry.py")),
                "invalid_metadata_stamper_invalid_template": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_invalid_template.py")),
                "invalid_metadata_stamper_missing_fields": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_missing_fields.py")),
                "invalid_metadata_stamper_readonly": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_readonly.py")),
                "invalid_metadata_stamper_large_file": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_large_file.py")),
                "invalid_metadata_stamper_invalid_format": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_invalid_format.py")),
                "invalid_metadata_stamper_missing_entries": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_missing_entries.py")),
                "invalid_metadata_stamper_invalid_block": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_invalid_block.py")),
                "invalid_metadata_stamper_ignore": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_ignore.py")),
                "invalid_metadata_stamper_cli": os.path.abspath(os.path.join(base_dir, "validate/metadata/test_case/invalid/invalid_metadata_stamper_cli.py")),
            },
        }
        self._cases["metadata_stamper"] = metadata_stamper_cases

        # Register directory_tree validator test cases (canonical: string values only)
        valid_dir = os.path.abspath(os.path.join(base_dir, "validate/directory_tree/test_case/valid"))
        invalid_dir = os.path.abspath(os.path.join(base_dir, "validate/directory_tree/test_case/invalid"))
        template_dir = os.path.abspath(os.path.join(base_dir, "../../foundation/template/validate"))
        directory_tree_cases = {
            "valid": {
                "tree": os.path.join(valid_dir, "valid_basic.tree"),
                "template": os.path.join(template_dir, "validate_template_directory_tree.yaml"),
                "policy": os.path.join(valid_dir, "tree_policy.yaml"),
            },
            # Add additional valid variations here as needed
            "invalid": {
                "tree": os.path.join(invalid_dir, ".tree"),
                "template": os.path.join(template_dir, "validate_template_directory_tree.yaml"),
                "policy": os.path.join(invalid_dir, "tree_policy.yaml"),
            },
        }
        self._cases["directory_tree"] = directory_tree_cases

        # Register tree_ignore utility test cases
        tree_ignore_cases = {
            "valid": {
                "valid_tree_ignore_yaml": os.path.abspath(os.path.join(base_dir, "util/test_case/tree_ignore/valid/valid_tree_ignore.yaml")),
                "valid_tree_ignore_json": os.path.abspath(os.path.join(base_dir, "util/test_case/tree_ignore/valid/valid_tree_ignore.json")),
            },
            "invalid": {
                "invalid_tree_ignore_missing_patterns": os.path.abspath(os.path.join(base_dir, "util/test_case/tree_ignore/invalid/invalid_tree_ignore_missing_patterns.yaml")),
                "invalid_tree_ignore_bad_format": os.path.abspath(os.path.join(base_dir, "util/test_case/tree_ignore/invalid/invalid_tree_ignore_bad_format.json")),
            },
        }
        self._cases["tree_ignore"] = tree_ignore_cases

        # Register tree_file utility test cases
        tree_file_cases = {
            "valid": {
                "valid_tree": os.path.abspath(os.path.join(base_dir, "../test/util/test_case/tree_file/valid/valid_tree.tree")),
            },
            "invalid": {
                "invalid_tree": os.path.abspath(os.path.join(base_dir, "../test/util/test_case/tree_file/invalid/invalid_tree.tree")),
                "invalid_missing_metadata": os.path.abspath(os.path.join(base_dir, "../test/util/test_case/tree_file/invalid/invalid_missing_metadata.tree")),
                "invalid_invalid_metadata": os.path.abspath(os.path.join(base_dir, "../test/util/test_case/tree_file/invalid/invalid_invalid_metadata.tree")),
            },
        }
        self._cases["tree_file"] = tree_file_cases

        # Register container_yaml validator test cases
        container_yaml_cases = {
            "valid": {
                "valid_container_yaml": os.path.abspath(os.path.join(base_dir, "validate/container_yaml/test_case/valid/valid_container_yaml.yaml")),
            },
            "invalid": {
                "invalid_container_yaml": os.path.abspath(os.path.join(base_dir, "validate/container_yaml/test_case/invalid/invalid_container_yaml.yaml")),
            },
        }
        self._cases["container_yaml"] = container_yaml_cases

        # Register container_validator test cases
        container_validator_cases = {
            "valid": {
                "valid_required_files_present": os.path.abspath(os.path.join(base_dir, "validate/container_validator/test_case/valid/valid_required_files_present.yaml")),
            },
            "invalid": {
                "invalid_missing_required_file": os.path.abspath(os.path.join(base_dir, "validate/container_validator/test_case/invalid/invalid_missing_required_file.yaml")),
            },
        }
        self._cases["container_validator"] = container_validator_cases

        # Register header_util test cases
        header_util_cases = {
            "valid": {
                "valid_header_shebang": os.path.abspath(os.path.join(base_dir, "util/test_case/header/valid/valid_header_shebang.py")),
            },
            "invalid": {
                "invalid_header_no_shebang": os.path.abspath(os.path.join(base_dir, "util/test_case/header/invalid/invalid_header_no_shebang.py")),
            },
        }
        self._cases["header_util"] = header_util_cases

    def get_test_case(self, validator: str, name: str, case_type: str) -> Optional[str]:
        """
        Get the path to a specific test case.

        Args:
            validator: The name of the validator (e.g., "chunk", "metadata_block")
            name: The name of the test case
            case_type: The type of test case ("valid" or "invalid")

        Returns:
            The absolute path to the test case file, or None if not found
        """
        try:
            return self._cases[validator][case_type][name]
        except KeyError:
            return None

    def list_test_cases(self, validator: str, case_type: str) -> List[str]:
        """
        List all test cases for a specific validator and case type.

        Args:
            validator: The name of the validator (e.g., "chunk", "metadata_block")
            case_type: The type of test case ("valid" or "invalid")

        Returns:
            A list of test case names
        """
        try:
            return list(self._cases[validator][case_type].keys())
        except KeyError:
            return []

    def register(self, validator: str, case_type: str, case_name: str, case_data: dict):
        """
        Register a new test case.

        Args:
            validator: The name of the validator (e.g., "chunk", "metadata_block")
            case_type: The type of test case ("valid" or "invalid")
            case_name: The name of the test case
            case_data: A dictionary containing the test case data
        """
        if validator not in self._cases:
            self._cases[validator] = {}
        if case_type not in self._cases[validator]:
            self._cases[validator][case_type] = {}
        self._cases[validator][case_type][case_name] = case_data


# Singleton instance for import
TEST_CASE_REGISTRY = DefaultTestCaseRegistry()

# === Standards Enforcement: Source/Script Files Requiring Metadata Block ===
# These files must have a valid metadata block and are checked by test_metadata_block_deserialization.py
METADATA_BLOCK_SOURCE_FILES = {
    "model_metadata": str(Path(__file__).parent.parent / "model/model_metadata.py"),
    "model_validate_error": str(Path(__file__).parent.parent / "model/model_validate_error.py"),
    "python_validate_metadata_block": str(Path(__file__).parent.parent / "script/validate/python/python_validate_metadata_block.py"),
    "validate_orchestrator": str(Path(__file__).parent.parent / "script/validate/validate_orchestrator.py"),
}

# Add to TEST_CASE_REGISTRY for programmatic access
setattr(TEST_CASE_REGISTRY, "metadata_block_source_files", METADATA_BLOCK_SOURCE_FILES)