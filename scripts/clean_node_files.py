# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: clean_node_files.py
# version: 1.0.0
# uuid: e6944c91-f60e-42cb-b818-0f42648f5f05
# author: OmniNode Team
# created_at: 2025-05-27T16:23:46.998671
# last_modified_at: 2025-05-27T20:42:03.263599
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f665c909bc62e47220a8e4defb913a42a066d6e3f95bf540989d2e9ea623d6d2
# entrypoint: python@clean_node_files.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.clean_node_files
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Script to clean node.onex.yaml files by removing ONEX metadata blocks.

These files should be handled by NodeContractHandler, not regular metadata handlers.
This script removes any existing ONEX metadata blocks and ensures proper YAML structure.

Usage:
    python scripts/clean_node_files.py [--dry-run] [--verbose]
"""

import argparse
import re
from pathlib import Path
from typing import List

import yaml


def find_node_files(root_dir: Path) -> List[Path]:
    """Find all node.onex.yaml files in the repository."""
    return list(root_dir.rglob("node.onex.yaml"))


def clean_node_file(file_path: Path, dry_run: bool = False) -> bool:
    """
    Clean a node.onex.yaml file by removing ONEX metadata blocks.

    Returns True if file was modified, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Remove ONEX metadata blocks
        metadata_pattern = (
            r"# === OmniNode:Metadata ===.*?# === /OmniNode:Metadata ===\n?"
        )
        content = re.sub(metadata_pattern, "", content, flags=re.DOTALL)

        # Remove duplicate document start markers
        # Replace multiple --- with single ---
        lines = content.split("\n")
        cleaned_lines = []
        doc_start_found = False

        for line in lines:
            stripped = line.strip()
            if stripped == "---":
                if not doc_start_found:
                    cleaned_lines.append("---")
                    doc_start_found = True
                # Skip duplicate --- markers
            elif stripped == "" and not cleaned_lines:
                # Skip leading empty lines
                continue
            else:
                cleaned_lines.append(line)

        # Ensure we start with --- if we have content
        if cleaned_lines and not doc_start_found:
            cleaned_lines.insert(0, "---")

        content = "\n".join(cleaned_lines)

        # Validate YAML structure
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            print(f"Warning: {file_path} has invalid YAML after cleaning: {e}")
            return False

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
    parser = argparse.ArgumentParser(description="Clean node.onex.yaml files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    root_dir = Path(".")
    node_files = find_node_files(root_dir)

    if not node_files:
        print("No node.onex.yaml files found")
        return 0

    print(f"Found {len(node_files)} node.onex.yaml files")

    modified_count = 0
    for file_path in node_files:
        if args.verbose:
            print(f"Processing: {file_path}")

        was_modified = clean_node_file(file_path, dry_run=args.dry_run)

        if was_modified:
            modified_count += 1
            status = "would be modified" if args.dry_run else "modified"
            print(f"  {status}: {file_path}")
        elif args.verbose:
            print(f"  unchanged: {file_path}")

    if args.dry_run:
        print(f"\nDry run complete. {modified_count} files would be modified.")
    else:
        print(f"\nCleaning complete. {modified_count} files modified.")

    return 0


if __name__ == "__main__":
    exit(main())
