# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: fix_yaml_formatting.py
# version: 1.0.0
# uuid: 48922581-6834-4b93-acce-bf27b3de5cb5
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.254689
# last_modified_at: 2025-05-28T17:20:04.420418
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: c898063ab48909e27220262f24bbef67e17a12e4c6112db10b5ee9277848f69b
# entrypoint: python@fix_yaml_formatting.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.fix_yaml_formatting
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Script to fix YAML formatting issues detected by yamllint.

This script fixes common YAML formatting issues:
- Indentation problems
- Line length issues
- Missing newlines at end of file
- Trailing spaces
- Document start markers

Usage:
    python scripts/fix_yaml_formatting.py [--dry-run] [--verbose]
"""

import argparse
from pathlib import Path
from typing import List

import yaml


def find_yaml_files(root_dir: Path) -> List[Path]:
    """Find all YAML files in the repository."""
    yaml_files: List[Path] = []
    for pattern in ["**/*.yaml", "**/*.yml"]:
        yaml_files.extend(root_dir.rglob(pattern))
    return yaml_files


def fix_yaml_formatting(file_path: Path, dry_run: bool = False) -> bool:
    """
    Fix YAML formatting issues in a file.

    Returns True if file was modified, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Skip binary files or files that don't look like YAML
        if not content.strip() or content.startswith("\x00"):
            return False

        # Fix line endings
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # Remove trailing spaces from all lines
        lines = content.split("\n")
        lines = [line.rstrip() for line in lines]

        # Ensure file ends with exactly one newline
        while lines and lines[-1] == "":
            lines.pop()
        lines.append("")  # Add single newline at end

        content = "\n".join(lines)

        # Try to parse and reformat with proper indentation
        try:
            # Parse YAML
            data = yaml.safe_load(content)
            if data is not None:
                # Reformat with consistent indentation
                formatted = yaml.dump(
                    data,
                    default_flow_style=False,
                    indent=4,
                    width=120,
                    allow_unicode=True,
                    sort_keys=False,
                )

                # Ensure document starts with ---
                if not formatted.startswith("---"):
                    formatted = "---\n" + formatted

                content = formatted

        except yaml.YAMLError:
            # If YAML parsing fails, do basic formatting fixes
            lines = content.split("\n")
            fixed_lines = []

            for line in lines:
                # Basic indentation fixes for common patterns
                stripped = line.lstrip()
                if stripped:
                    # Count leading spaces
                    indent_level = len(line) - len(stripped)

                    # Ensure indentation is multiple of 2 or 4
                    if indent_level % 4 != 0 and indent_level % 2 == 0:
                        # Convert 2-space to 4-space indentation
                        new_indent = (indent_level // 2) * 4
                        line = " " * new_indent + stripped
                    elif indent_level % 4 != 0:
                        # Round to nearest 4-space boundary
                        new_indent = ((indent_level + 2) // 4) * 4
                        line = " " * new_indent + stripped

                fixed_lines.append(line)

            content = "\n".join(fixed_lines)

        # Write back if changed and not dry run
        if content != original_content:
            if not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Fix YAML formatting issues")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--files",
        nargs="*",
        help="Specific files to process (default: all YAML files)",
    )

    args = parser.parse_args()

    if args.files:
        yaml_files = [Path(f) for f in args.files]
    else:
        root_dir = Path(".")
        yaml_files = find_yaml_files(root_dir)

    if not yaml_files:
        print("No YAML files found")
        return 0

    print(f"Found {len(yaml_files)} YAML files")

    modified_count = 0
    for file_path in yaml_files:
        if args.verbose:
            print(f"Processing: {file_path}")

        was_modified = fix_yaml_formatting(file_path, dry_run=args.dry_run)

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
