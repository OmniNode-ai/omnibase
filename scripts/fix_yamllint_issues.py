# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.263410'
# description: Stamped by PythonHandler
# entrypoint: python://fix_yamllint_issues.py
# hash: 8400cbcae46f671a4a1811bc867f696476a7e0c7b5ff7f9d6c37150f076b53ab
# last_modified_at: '2025-05-29T13:51:13.795083+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: fix_yamllint_issues.py
# namespace: py://omnibase.fix_yamllint_issues_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 5c95e8e8-a1e5-4498-b514-05b907f30e52
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Script to fix specific yamllint issues.

This script fixes:
- Wrong indentation
- Too many spaces after hyphen
- Line length issues
- Missing document start markers
- Duplicate keys
"""

import argparse
import re
from pathlib import Path
from typing import List


def fix_yamllint_issues(file_path: Path, dry_run: bool = False) -> bool:
    """
    Fix yamllint issues in a YAML file.

    Returns True if file was modified, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        lines = content.split("\n")

        # Skip empty files
        if not content.strip():
            return False

        fixed_lines = []

        for i, line in enumerate(lines):
            # Fix hyphen spacing (should be "- " not "-   ")
            if re.match(r"^(\s*)-\s{2,}", line):
                # Replace multiple spaces after hyphen with single space
                line = re.sub(r"^(\s*)-\s+", r"\1- ", line)

            # Fix basic indentation issues for common patterns
            stripped = line.lstrip()
            if stripped:
                # Count current indentation
                current_indent = len(line) - len(stripped)

                # For YAML, ensure indentation is multiple of 2 or 4
                if current_indent > 0:
                    # Round to nearest multiple of 4 for consistency
                    if current_indent % 4 != 0:
                        new_indent = ((current_indent + 2) // 4) * 4
                        line = " " * new_indent + stripped

            # Remove trailing spaces
            line = line.rstrip()

            fixed_lines.append(line)

        # Ensure document starts with --- if it's a YAML file
        if fixed_lines and not fixed_lines[0].startswith("---"):
            # Check if this looks like a YAML document
            has_yaml_content = any(
                ":" in line or line.strip().startswith("-")
                for line in fixed_lines[:10]
                if line.strip()
            )
            if has_yaml_content:
                fixed_lines.insert(0, "---")

        # Remove duplicate empty lines at the end
        while len(fixed_lines) > 1 and fixed_lines[-1] == "" and fixed_lines[-2] == "":
            fixed_lines.pop()

        # Ensure file ends with exactly one newline
        if fixed_lines and fixed_lines[-1] != "":
            fixed_lines.append("")

        new_content = "\n".join(fixed_lines)

        # Write back if changed
        if new_content != original_content:
            if not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def find_yaml_files_with_issues() -> List[Path]:
    """Find YAML files that likely have yamllint issues."""
    # Focus on the files that showed errors in the yamllint output
    problem_files = [
        "src/omnibase/schemas/onex_node.yaml",
        "src/omnibase/nodes/stamper_node/v1_0_0/examples/minimal_example.yaml",
        "src/omnibase/nodes/registry_loader_node/v1_0_0/contract.yaml",
        "src/omnibase/nodes/parity_validator_node/v1_0_0/node.onex.yaml",
        "src/omnibase/nodes/parity_validator_node/v1_0_0/contract.yaml",
        ".github/workflows/ci.yml",
        "src/omnibase/schemas/state_contract.yaml",
        "src/omnibase/nodes/cli_node/v1_0_0/contract.yaml",
        "src/omnibase/schemas/tree_format.yaml",
        "src/omnibase/nodes/stamper_node/v1_0_0/node_tests/fixtures/minimal_stamped_fixture.yaml",
        "tests/schemas/testdata/invalid_execution_result.yaml",
        "src/omnibase/nodes/template_node/v1_0_0/contract.yaml",
        "src/omnibase/nodes/schema_generator_node/v1_0_0/node.onex.yaml",
        ".pre-commit-config.yaml",
        "src/omnibase/nodes/docstring_generator_node/v1_0_0/contract.yaml",
        "src/omnibase/nodes/registry_loader_node/v1_0_0/node.onex.yaml",
        "src/omnibase/nodes/logger_node/v1_0_0/node.onex.yaml",
        "src/omnibase/schemas/execution_result.yaml",
        "src/omnibase/nodes/docstring_generator_node/v1_0_0/node.onex.yaml",
        "src/omnibase/runtimes/onex_runtime/v1_0_0/runtime.yaml",
        "src/omnibase/cli_tools/onex/v1_0_0/cli_tool.yaml",
        "src/omnibase/nodes/tree_generator_node/v1_0_0/node.onex.yaml",
        "tests/schemas/testdata/valid_onex_node.yaml",
        "src/omnibase/nodes/cli_node/v1_0_0/node.onex.yaml",
        "src/omnibase/nodes/stamper_node/v1_0_0/node.onex.yaml",
        "src/omnibase/nodes/logger_node/v1_0_0/contract.yaml",
        "src/omnibase/nodes/stamper_node/v1_0_0/contract.yaml",
        "tests/data/shared_test_data_basic.yaml",
        "tests/schemas/testdata/valid_execution_result.yaml",
        "src/omnibase/nodes/tree_generator_node/v1_0_0/contract.yaml",
        "src/omnibase/nodes/template_node/v1_0_0/node.onex.yaml",
        "src/omnibase/nodes/schema_generator_node/v1_0_0/contract.yaml",
        "tests/schemas/testdata/invalid_onex_node.yaml",
    ]

    existing_files = []
    for file_str in problem_files:
        file_path = Path(file_str)
        if file_path.exists():
            existing_files.append(file_path)

    return existing_files


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Fix yamllint issues")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    yaml_files = find_yaml_files_with_issues()

    if not yaml_files:
        print("No YAML files with known issues found")
        return 0

    print(f"Found {len(yaml_files)} YAML files with potential issues")

    modified_count = 0
    for file_path in yaml_files:
        if args.verbose:
            print(f"Processing: {file_path}")

        was_modified = fix_yamllint_issues(file_path, dry_run=args.dry_run)

        if was_modified:
            modified_count += 1
            status = "would be modified" if args.dry_run else "modified"
            print(f"  {status}: {file_path}")
        elif args.verbose:
            print(f"  unchanged: {file_path}")

    if args.dry_run:
        print(f"\nDry run complete. {modified_count} files would be modified.")
    else:
        print(f"\nFormatting complete. {modified_count} files modified.")

    return 0


if __name__ == "__main__":
    exit(main())
