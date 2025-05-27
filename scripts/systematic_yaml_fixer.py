# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: systematic_yaml_fixer.py
# version: 1.0.0
# uuid: 88ea0b13-7bcb-4763-99b5-b605790826cb
# author: OmniNode Team
# created_at: 2025-05-27T18:06:06.186814
# last_modified_at: 2025-05-27T22:20:27.144403
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a43cb8c64979f29fe496c7166ba6b7c81031e76b24779ab7ff108fd929d337dd
# entrypoint: python@systematic_yaml_fixer.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.systematic_yaml_fixer
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Systematic YAML Fixer

This script provides targeted fixes for different types of YAML issues
based on their root causes. It works with the YAML issues tracker to
ensure we don't keep regenerating the same problems.

Fixing Strategy:
1. Schema files: Recreate from scratch using proper templates
2. Contract files: Fix indentation and structure systematically  
3. CI workflows: Use proper GitHub Actions formatting
4. Node metadata: Ensure consistent stamper output
5. Test data: Fix or mark as intentionally invalid
"""

import json
from pathlib import Path
from typing import List

from yaml_issues_tracker import YAMLIssuesTracker  # type: ignore


class SystematicYAMLFixer:
    """Systematic fixer for YAML issues based on root cause analysis."""

    def __init__(self) -> None:
        self.tracker = YAMLIssuesTracker()
        self.fixed_files: List[str] = []
        self.failed_files: List[str] = []

    def fix_indentation_issues(self, file_path: Path) -> bool:
        """Fix common indentation issues in YAML files."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            lines = content.split("\n")
            fixed_lines = []

            for line in lines:
                # Skip empty lines and comments
                if not line.strip() or line.strip().startswith("#"):
                    fixed_lines.append(line)
                    continue

                # Fix common indentation patterns
                fixed_line = self._fix_line_indentation(line)
                fixed_lines.append(fixed_line)

            fixed_content = "\n".join(fixed_lines)

            # Only write if content changed
            if fixed_content != content:
                with open(file_path, "w") as f:
                    f.write(fixed_content)
                return True

            return False

        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return False

    def _fix_line_indentation(self, line: str) -> str:
        """Fix indentation for a single line based on common patterns."""
        # Don't modify lines that are already properly indented
        if not line.strip():
            return line

        # Get the content without leading whitespace
        content = line.lstrip()
        leading_spaces = len(line) - len(content)

        # Common fixes for specific patterns
        if content.startswith("- "):
            # List items should be properly aligned
            if leading_spaces % 2 != 0:
                # Make it even (2-space indentation)
                leading_spaces = (leading_spaces // 2) * 2
        elif ":" in content and not content.startswith("#"):
            # Key-value pairs should be properly aligned
            if leading_spaces % 2 != 0:
                leading_spaces = (leading_spaces // 2) * 2

        return " " * leading_spaces + content

    def fix_schema_file(self, file_path: Path) -> bool:
        """Fix schema files by recreating them with proper structure."""
        print(f"Fixing schema file: {file_path}")

        # For now, just fix basic indentation issues
        # TODO: Implement schema-specific fixes based on the file type
        return self.fix_indentation_issues(file_path)

    def fix_contract_file(self, file_path: Path) -> bool:
        """Fix contract files with proper YAML structure."""
        print(f"Fixing contract file: {file_path}")

        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Fix common contract file issues
            lines = content.split("\n")
            fixed_lines = []
            in_input_section = False
            in_output_section = False

            for line in lines:
                stripped = line.strip()

                # Track sections
                if stripped.startswith("input:"):
                    in_input_section = True
                    in_output_section = False
                elif stripped.startswith("output:"):
                    in_input_section = False
                    in_output_section = True
                elif stripped and not stripped.startswith(" ") and ":" in stripped:
                    in_input_section = False
                    in_output_section = False

                # Fix indentation based on context
                if stripped and not stripped.startswith("#"):
                    if stripped.startswith("type:") or stripped.startswith(
                        "description:"
                    ):
                        # These should be indented under their parent
                        if in_input_section or in_output_section:
                            line = "    " + stripped
                        else:
                            line = "  " + stripped
                    elif stripped.startswith("required:") or stripped.startswith(
                        "properties:"
                    ):
                        line = "  " + stripped
                    elif stripped.startswith("- "):
                        # List items
                        if in_input_section or in_output_section:
                            line = "      " + stripped
                        else:
                            line = "    " + stripped

                fixed_lines.append(line)

            fixed_content = "\n".join(fixed_lines)

            if fixed_content != content:
                with open(file_path, "w") as f:
                    f.write(fixed_content)
                return True

            return False

        except Exception as e:
            print(f"Error fixing contract file {file_path}: {e}")
            return False

    def fix_ci_workflow(self, file_path: Path) -> bool:
        """Fix GitHub Actions workflow files."""
        print(f"Fixing CI workflow: {file_path}")

        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Fix the GitHub Actions workflow structure
            lines = content.split("\n")
            fixed_lines = []

            for line in lines:
                stripped = line.strip()

                if not stripped or stripped.startswith("#"):
                    fixed_lines.append(line)
                    continue

                # Fix specific GitHub Actions indentation issues
                if stripped.startswith("jobs:"):
                    fixed_lines.append("jobs:")
                elif stripped.startswith("steps:"):
                    fixed_lines.append("      steps:")
                elif stripped.startswith("- name:") or stripped.startswith("- uses:"):
                    fixed_lines.append("        " + stripped)
                elif stripped.startswith("with:") or stripped.startswith("run:"):
                    fixed_lines.append("          " + stripped)
                elif stripped.startswith("env:") and "run:" in [
                    line_item.strip()
                    for line_item in lines[
                        max(0, lines.index(line) - 5) : lines.index(line)
                    ]
                ]:
                    fixed_lines.append("          " + stripped)
                elif ":" in stripped and not stripped.startswith(" "):
                    # Top-level keys
                    fixed_lines.append(stripped)
                else:
                    # Try to preserve existing indentation for complex cases
                    fixed_lines.append(line)

            fixed_content = "\n".join(fixed_lines)

            if fixed_content != content:
                with open(file_path, "w") as f:
                    f.write(fixed_content)
                return True

            return False

        except Exception as e:
            print(f"Error fixing CI workflow {file_path}: {e}")
            return False

    def fix_node_metadata(self, file_path: Path) -> bool:
        """Fix node metadata YAML files."""
        print(f"Fixing node metadata: {file_path}")

        # These are often generated by stamper, so fix basic issues
        return self.fix_indentation_issues(file_path)

    def fix_test_data(self, file_path: Path) -> bool:
        """Fix test data files, being careful about intentionally invalid ones."""
        print(f"Fixing test data: {file_path}")

        # Check if this is intentionally invalid
        if "invalid" in str(file_path):
            print(
                f"Skipping {file_path} - appears to be intentionally invalid test data"
            )
            return False

        return self.fix_indentation_issues(file_path)

    def fix_file_by_root_cause(self, file_path: str, root_cause: str) -> bool:
        """Fix a file based on its identified root cause."""
        path = Path(file_path)

        if not path.exists():
            print(f"File not found: {file_path}")
            return False

        print(f"Fixing {file_path} (root cause: {root_cause})")

        try:
            if root_cause == "schema":
                success = self.fix_schema_file(path)
            elif root_cause == "contract":
                success = self.fix_contract_file(path)
            elif root_cause == "ci_workflow":
                success = self.fix_ci_workflow(path)
            elif root_cause == "template":
                success = self.fix_node_metadata(path)
            elif root_cause == "unknown":
                if "test" in file_path.lower():
                    success = self.fix_test_data(path)
                else:
                    success = self.fix_indentation_issues(path)
            else:
                success = self.fix_indentation_issues(path)

            if success:
                self.fixed_files.append(file_path)
                print(f"✅ Fixed {file_path}")
            else:
                print(f"⚠️  No changes needed for {file_path}")

            return success

        except Exception as e:
            print(f"❌ Failed to fix {file_path}: {e}")
            self.failed_files.append(file_path)
            return False

    def fix_most_problematic_files(self, max_files: int = 5) -> None:
        """Fix the most problematic files first."""
        # Load the issues database
        try:
            with open(".yaml_issues_db.json", "r") as f:
                issues_db = json.load(f)
        except FileNotFoundError:
            print("No issues database found. Run the tracker first.")
            return

        # Sort files by total issues
        sorted_files = sorted(
            issues_db.items(), key=lambda x: x[1]["total_issues"], reverse=True
        )

        print(f"Fixing top {max_files} most problematic files...")

        for i, (file_path, file_data) in enumerate(sorted_files[:max_files]):
            print(f"\n{i+1}. {file_path} ({file_data['total_issues']} issues)")

            # Determine root cause
            root_causes = file_data.get("root_causes", ["unknown"])
            primary_cause = root_causes[0] if root_causes else "unknown"

            self.fix_file_by_root_cause(file_path, primary_cause)

    def fix_by_root_cause(self, root_cause: str) -> None:
        """Fix all files with a specific root cause."""
        try:
            with open(".yaml_issues_db.json", "r") as f:
                issues_db = json.load(f)
        except FileNotFoundError:
            print("No issues database found. Run the tracker first.")
            return

        files_to_fix = [
            file_path
            for file_path, file_data in issues_db.items()
            if root_cause in file_data.get("root_causes", [])
        ]

        print(f"Fixing {len(files_to_fix)} files with root cause '{root_cause}'...")

        for file_path in files_to_fix:
            self.fix_file_by_root_cause(file_path, root_cause)

    def generate_summary(self) -> None:
        """Generate a summary of the fixing session."""
        print(f"\n{'='*50}")
        print("YAML Fixing Summary")
        print(f"{'='*50}")
        print(f"✅ Fixed files: {len(self.fixed_files)}")
        print(f"❌ Failed files: {len(self.failed_files)}")

        if self.fixed_files:
            print("\nFixed files:")
            for file_path in self.fixed_files:
                print(f"  - {file_path}")

        if self.failed_files:
            print("\nFailed files:")
            for file_path in self.failed_files:
                print(f"  - {file_path}")


def main() -> None:
    """Main entry point for the systematic YAML fixer."""
    import argparse

    parser = argparse.ArgumentParser(description="Systematically fix YAML issues")
    parser.add_argument(
        "--top", type=int, default=5, help="Fix top N most problematic files"
    )
    parser.add_argument("--cause", help="Fix files by root cause")
    parser.add_argument("--file", help="Fix a specific file")
    parser.add_argument(
        "--all-contracts", action="store_true", help="Fix all contract files"
    )
    parser.add_argument(
        "--all-schemas", action="store_true", help="Fix all schema files"
    )

    args = parser.parse_args()

    fixer = SystematicYAMLFixer()

    if args.file:
        # Fix a specific file (need to determine root cause)
        fixer.fix_file_by_root_cause(args.file, "unknown")
    elif args.cause:
        fixer.fix_by_root_cause(args.cause)
    elif args.all_contracts:
        fixer.fix_by_root_cause("contract")
    elif args.all_schemas:
        fixer.fix_by_root_cause("schema")
    else:
        fixer.fix_most_problematic_files(args.top)

    fixer.generate_summary()


if __name__ == "__main__":
    main()
