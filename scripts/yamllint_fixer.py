# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.329547'
# description: Stamped by PythonHandler
# entrypoint: python://yamllint_fixer.py
# hash: 4d50e8dd09cfd1423eac2c22306ffdf5d4835bb1f05279e61dec31c9b07e8e4f
# last_modified_at: '2025-05-29T13:51:14.146326+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: yamllint_fixer.py
# namespace: py://omnibase.yamllint_fixer_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: cd693357-4bd3-48c3-9e66-3be9ab11619c
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
YAMLLint-focused fixer

This script fixes yamllint issues (indentation, line length) without changing
the semantic content of YAML files. It uses our existing models when possible
but falls back to simple formatting fixes for files that can't be parsed.
"""

import re
import subprocess
from pathlib import Path
from typing import List

import yaml


def fix_yamllint_issues(file_path: Path) -> bool:
    """Fix yamllint issues in a YAML file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # First try to parse and reformat with proper YAML formatting
        try:
            data = yaml.safe_load(content)
            if data is not None:
                # Use our standard YAML formatting
                fixed_content = yaml.dump(
                    data,
                    default_flow_style=False,
                    indent=2,
                    width=120,
                    allow_unicode=True,
                    sort_keys=False,
                )

                # Ensure proper document start
                if not fixed_content.startswith("---"):
                    fixed_content = "---\n" + fixed_content

                # Ensure single trailing newline
                fixed_content = fixed_content.rstrip() + "\n"

                # Only write if content changed
                if fixed_content != content:
                    with open(file_path, "w") as f:
                        f.write(fixed_content)
                    return True

                return False
            else:
                # Empty YAML file, try manual fixes
                return fix_manual_formatting(file_path, content)

        except yaml.YAMLError:
            # If YAML parsing fails, try manual fixes
            return fix_manual_formatting(file_path, content)

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def fix_manual_formatting(file_path: Path, content: str) -> bool:
    """Manually fix formatting issues when YAML parsing fails."""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Fix line length by breaking long lines
        if len(line) > 120 and "description:" in line:
            # Handle long description lines
            match = re.match(r"(\s*description:\s*)(.*)", line)
            if match:
                indent = match.group(1)
                desc = match.group(2).strip("'\"")

                # Use folded string format
                fixed_lines.append(f"{indent}>")

                # Break description into multiple lines
                words = desc.split()
                current_line = ""
                base_indent = len(indent.replace("description:", "").rstrip()) + 2

                for word in words:
                    if len(current_line + " " + word) <= 118 - base_indent:
                        current_line += (" " if current_line else "") + word
                    else:
                        if current_line:
                            fixed_lines.append(" " * base_indent + current_line)
                        current_line = word

                if current_line:
                    fixed_lines.append(" " * base_indent + current_line)
                continue

        # Fix basic indentation issues
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            # Calculate proper indentation
            if ":" in stripped and not stripped.startswith("- "):
                # Key-value pairs should have even indentation
                current_indent = len(line) - len(stripped)
                if current_indent % 2 != 0:
                    line = " " * (current_indent + 1) + stripped
            elif stripped.startswith("- "):
                # List items should have even indentation
                current_indent = len(line) - len(stripped)
                if current_indent % 2 != 0:
                    line = " " * (current_indent + 1) + stripped

        fixed_lines.append(line)

    fixed_content = "\n".join(fixed_lines)

    if fixed_content != content:
        with open(file_path, "w") as f:
            f.write(fixed_content)
        return True

    return False


def get_yamllint_issues(file_path: Path) -> List[str]:
    """Get yamllint issues for a specific file."""
    try:
        result = subprocess.run(
            ["yamllint", str(file_path), "--format", "parsable"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return []

        return result.stdout.strip().split("\n") if result.stdout.strip() else []

    except subprocess.CalledProcessError:
        return []
    except FileNotFoundError:
        print("Error: yamllint not found. Please install yamllint.")
        return []


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix yamllint issues in YAML files")
    parser.add_argument("--file", help="Fix a specific file")
    parser.add_argument(
        "--all", action="store_true", help="Fix all YAML files with issues"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed"
    )

    args = parser.parse_args()

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return 1

        issues_before = get_yamllint_issues(file_path)
        if not issues_before:
            print(f"No yamllint issues found in {file_path}")
            return 0

        print(f"Found {len(issues_before)} yamllint issues in {file_path}")

        if not args.dry_run:
            success = fix_yamllint_issues(file_path)
            if success:
                issues_after = get_yamllint_issues(file_path)
                print(
                    f"✅ Fixed {file_path} ({len(issues_before) - len(issues_after)} issues resolved)"
                )
            else:
                print(f"⚠️  No changes made to {file_path}")
        else:
            print(f"Would fix {file_path}")

    elif args.all:
        # Find all YAML files with yamllint issues
        yaml_files: List[Path] = []
        for pattern in ["**/*.yaml", "**/*.yml"]:
            yaml_files.extend(Path(".").glob(pattern))

        files_with_issues = []
        for file_path in yaml_files:
            if file_path.is_file():
                issues = get_yamllint_issues(file_path)
                if issues:
                    files_with_issues.append((file_path, len(issues)))

        if not files_with_issues:
            print("No YAML files with yamllint issues found")
            return 0

        print(f"Found {len(files_with_issues)} YAML files with yamllint issues")

        fixed_count = 0
        for file_path, issue_count in files_with_issues:
            print(f"Processing {file_path} ({issue_count} issues)...")

            if not args.dry_run:
                success = fix_yamllint_issues(file_path)
                if success:
                    issues_after = get_yamllint_issues(file_path)
                    remaining = len(issues_after)
                    resolved = issue_count - remaining
                    if resolved > 0:
                        print(f"  ✅ Fixed {resolved} issues ({remaining} remaining)")
                        fixed_count += 1
                    else:
                        print("  ⚠️  No issues resolved")
                else:
                    print("  ⚠️  No changes made")
            else:
                print(f"  Would fix {file_path}")

        if not args.dry_run:
            print(f"\nFixed {fixed_count} files")

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
