# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:33:19.587297'
# description: Stamped by PythonHandler
# entrypoint: python://revert_header_files.py
# hash: 97883fa70d39e41a6191050a6b55570e48b1908a6a46f0a3b92b0e850d5d9d2a
# last_modified_at: '2025-05-29T13:43:06.683567+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: revert_header_files.py
# namespace:
#   value: py://omnibase.revert_header_files_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 9babb5ce-6eec-46df-93ff-4314dddc7f93
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Script to revert the 78 files that only have incorrect header changes.
"""

import subprocess

# The 78 files identified as having only incorrect header changes
files_to_revert = [
    "docs/templates/template_validator.py",
    "src/omnibase/__init__.py",
    "src/omnibase/cli_tools/onex/v1_0_0/cli_main.py",
    "src/omnibase/cli_tools/onex/v1_0_0/cli_tests/__init__.py",
    "src/omnibase/cli_tools/onex/v1_0_0/cli_tests/test_cli_main.py",
    "src/omnibase/cli_tools/onex/v1_0_0/cli_tests/test_docstring_generator.py",
    "src/omnibase/cli_tools/onex/v1_0_0/cli_tests/test_onex_validator.py",
    "src/omnibase/cli_tools/onex/v1_0_0/cli_tests/test_tree_discovery.py",
    "src/omnibase/cli_tools/onex/v1_0_0/cli_tests/test_tree_generator.py",
    "src/omnibase/cli_tools/onex/v1_0_0/cli_tests/tools_test_cli_main_cases.py",
    "src/omnibase/core/__init__.py",
    "src/omnibase/enums/file_status.py",
    "src/omnibase/enums/file_type.py",
    "src/omnibase/enums/ignore_pattern_source.py",
    "src/omnibase/enums/log_level.py",
    "src/omnibase/enums/metadata.py",
    "src/omnibase/enums/onex_status.py",
    "src/omnibase/enums/output_format.py",
    "src/omnibase/enums/template_type.py",
    "src/omnibase/exceptions.py",
    "src/omnibase/handlers/block_placement_mixin.py",
    "src/omnibase/model/__init__.py",
    "src/omnibase/model/model_base_error.py",
    "src/omnibase/model/model_base_result.py",
    "src/omnibase/model/model_block_placement_policy.py",
    "src/omnibase/model/model_context.py",
    "src/omnibase/model/model_doc_link.py",
    "src/omnibase/model/model_file_filter.py",
    "src/omnibase/model/model_file_reference.py",
    "src/omnibase/model/model_log_entry.py",
    "src/omnibase/model/model_metadata.py",
    "src/omnibase/model/model_metadata_config.py",
    "src/omnibase/model/model_naming_convention.py",
    "src/omnibase/model/model_onex_ignore.py",
    "src/omnibase/model/model_onex_message.py",
    "src/omnibase/model/model_onex_message_result.py",
    "src/omnibase/model/model_orchestrator.py",
    "src/omnibase/model/model_output_data.py",
    "src/omnibase/model/model_reducer.py",
    "src/omnibase/model/model_result_cli.py",
    "src/omnibase/model/model_schema.py",
    "src/omnibase/model/model_tree_sync_result.py",
    "src/omnibase/model/model_uri.py",
    "src/omnibase/model/model_validate_error.py",
    "src/omnibase/protocol/protocol_canonical_serializer.py",
    "src/omnibase/protocol/protocol_cli.py",
    "src/omnibase/protocol/protocol_naming_convention.py",
    "src/omnibase/protocol/protocol_schema_loader.py",
    "src/omnibase/protocol/protocol_stamper.py",
    "src/omnibase/protocol/protocol_testable.py",
    "src/omnibase/protocol/protocol_testable_cli.py",
    "src/omnibase/protocol/protocol_testable_registry.py",
    "src/omnibase/protocol/protocol_tool.py",
    "src/omnibase/protocol/protocol_uri_parser.py",
    "src/omnibase/runtimes/onex_runtime/v1_0_0/mixins/mixin_block_placement.py",
    "src/omnibase/templates/__init__.py",
    "src/omnibase/utils/__init__.py",
    "src/omnibase/utils/minimal_repro.py",
    "src/omnibase/utils/utils_uri_parser.py",
    "src/omnibase/utils/utils_velocity_log.py",
    "src/omnibase/utils/yaml_extractor.py",
    "tests/core/__init__.py",
    "tests/core/core_test_registry_cases.py",
    "tests/core/test_registry.py",
    "tests/schemas/__init__.py",
    "tests/schemas/test_backward_compatibility.py",
    "tests/schemas/test_execution_result.py",
    "tests/schemas/test_onex_node.py",
    "tests/schemas/test_state_contract.py",
    "tests/shared/__init__.py",
    "tests/shared/test_metadata_blocks.py",
    "tests/utils/__init__.py",
    "tests/utils/test_directory_traverser.py",
    "tests/utils/test_file_discovery_sources.py",
    "tests/utils/test_utils_uri_parser.py",
    "tests/utils/utils_test_file_discovery_sources_cases.py",
    "tests/utils/utils_test_stamper_cases.py",
    "tests/utils/utils_test_uri_parser_cases.py"
]

def main():
    print(f"Reverting {len(files_to_revert)} files with only incorrect header changes...")
    
    for i, filepath in enumerate(files_to_revert):
        print(f"Reverting {i+1}/{len(files_to_revert)}: {filepath}")
        try:
            subprocess.run(["git", "checkout", "HEAD", "--", filepath], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error reverting {filepath}: {e}")
    
    print(f"\nCompleted reverting {len(files_to_revert)} files.")
    print("These files had only incorrect stamper metadata changes:")
    print("- protocol_version: 0.1.0 -> 1.1.0 (incorrect)")
    print("- schema_version: 0.1.0 -> 1.1.0 (incorrect)")
    print("- uuid changed (idempotency bug)")
    print("- created_at changed (idempotency bug)")

if __name__ == "__main__":
    main()
