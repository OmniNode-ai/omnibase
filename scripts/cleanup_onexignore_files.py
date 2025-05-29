# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.235821'
# description: Stamped by PythonHandler
# entrypoint: python://cleanup_onexignore_files.py
# hash: afbee6f055d5e30518a2b09dafa34b59e55c5654ca770996672c6ca191d3d961
# last_modified_at: '2025-05-29T11:50:10.520672+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: cleanup_onexignore_files.py
# namespace: omnibase.cleanup_onexignore_files
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: a6e99acc-b16d-445f-85dd-6161aa6a75c4
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Script to clean up .onexignore files by removing node.onex.yaml references
and deleting empty .onexignore files.

This script:
1. Finds all .onexignore files
2. Removes node.onex.yaml from stamper patterns
3. Deletes .onexignore files that become empty after cleanup
4. Provides a summary of changes made

Usage:
    python scripts/cleanup_onexignore_files.py [--dry-run] [--verbose]
"""

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


def find_onexignore_files(root_dir: Path) -> List[Path]:
    """
    Find all .onexignore files in the repository.

    Args:
        root_dir: Root directory to search

    Returns:
        List of .onexignore file paths
    """
    return list(root_dir.rglob(".onexignore"))


def is_onexignore_empty_after_cleanup(file_path: Path) -> Tuple[bool, bool]:
    """
    Check if an .onexignore file would be empty after removing node.onex.yaml.

    Args:
        file_path: Path to .onexignore file

    Returns:
        Tuple of (needs_cleanup, would_be_empty_after_cleanup)
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()

        # Parse YAML
        data = yaml.safe_load(content)
        if not data:
            return False, True

        needs_cleanup = False

        # Check stamper patterns
        if "stamper" in data and "patterns" in data["stamper"]:
            patterns = data["stamper"]["patterns"]
            if "node.onex.yaml" in patterns:
                needs_cleanup = True
                # Remove node.onex.yaml to see what's left
                remaining_patterns = [p for p in patterns if p != "node.onex.yaml"]
                data["stamper"]["patterns"] = remaining_patterns

        # Check if file would be effectively empty after cleanup
        would_be_empty = True

        if "stamper" in data and data["stamper"].get("patterns"):
            would_be_empty = False

        if "all" in data and data["all"].get("patterns"):
            would_be_empty = False

        # Check for any other sections
        for key in data:
            if key not in ["stamper", "all"] and data[key]:
                would_be_empty = False
                break

        return needs_cleanup, would_be_empty

    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return False, False


def cleanup_onexignore_file(
    file_path: Path, dry_run: bool = False, verbose: bool = False
) -> Tuple[bool, bool]:
    """
    Clean up an .onexignore file by removing node.onex.yaml references.

    Args:
        file_path: Path to .onexignore file
        dry_run: If True, don't make actual changes
        verbose: If True, print detailed information

    Returns:
        Tuple of (was_modified, should_be_deleted)
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read()

        # Parse YAML
        data = yaml.safe_load(content)
        if not data:
            return False, True

        modified = False

        # Update stamper patterns
        if "stamper" in data and "patterns" in data["stamper"]:
            patterns = data["stamper"]["patterns"]
            if "node.onex.yaml" in patterns:
                patterns.remove("node.onex.yaml")
                modified = True
                if verbose:
                    print(f"  Removed node.onex.yaml from {file_path}")

        # Check if file should be deleted (effectively empty)
        should_delete = True

        if "stamper" in data and data["stamper"].get("patterns"):
            should_delete = False

        if "all" in data and data["all"].get("patterns"):
            should_delete = False

        # Check for any other meaningful sections
        for key in data:
            if key not in ["stamper", "all"] and data[key]:
                should_delete = False
                break

        if modified and not should_delete and not dry_run:
            # Write back the updated content
            with file_path.open("w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            if verbose:
                print(f"  Updated: {file_path}")

        return modified, should_delete

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, False


def cleanup_onexignore_files(
    root_dir: Path, dry_run: bool = False, verbose: bool = False
) -> Dict[str, int]:
    """
    Clean up all .onexignore files in the repository.

    Args:
        root_dir: Root directory to clean up
        dry_run: If True, don't make actual changes
        verbose: If True, print detailed information

    Returns:
        Dictionary with cleanup statistics
    """
    stats = {"files_found": 0, "files_modified": 0, "files_deleted": 0, "errors": 0}

    print(f"Starting .onexignore cleanup in: {root_dir}")
    print(f"Dry run: {dry_run}")
    print()

    # Find all .onexignore files
    onexignore_files = find_onexignore_files(root_dir)
    stats["files_found"] = len(onexignore_files)

    if not onexignore_files:
        print("No .onexignore files found.")
        return stats

    print(f"Found {len(onexignore_files)} .onexignore files:")

    for file_path in onexignore_files:
        if verbose:
            print(f"\nProcessing: {file_path}")

        try:
            was_modified, should_delete = cleanup_onexignore_file(
                file_path, dry_run, verbose
            )

            if should_delete:
                print(f"  DELETE: {file_path} (empty after cleanup)")
                if not dry_run:
                    file_path.unlink()
                stats["files_deleted"] += 1
            elif was_modified:
                print(f"  MODIFY: {file_path} (removed node.onex.yaml)")
                stats["files_modified"] += 1
            else:
                if verbose:
                    print(f"  SKIP: {file_path} (no changes needed)")

        except Exception as e:
            print(f"  ERROR: {file_path}: {e}")
            stats["errors"] += 1

    print()

    # Summary
    print("Cleanup Summary:")
    print(f"  Files found: {stats['files_found']}")
    print(f"  Files modified: {stats['files_modified']}")
    print(f"  Files deleted: {stats['files_deleted']}")
    print(f"  Errors: {stats['errors']}")

    if dry_run:
        print()
        print("This was a dry run. No actual changes were made.")
        print("Run without --dry-run to perform the cleanup.")

    return stats


def main() -> int:
    """Main entry point for the cleanup script."""
    parser = argparse.ArgumentParser(
        description="Clean up .onexignore files by removing node.onex.yaml references"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed information about changes"
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=Path("."),
        help="Root directory to clean up (default: current directory)",
    )

    args = parser.parse_args()

    if not args.root_dir.exists():
        print(f"Error: Root directory does not exist: {args.root_dir}")
        return 1

    try:
        stats = cleanup_onexignore_files(
            args.root_dir, dry_run=args.dry_run, verbose=args.verbose
        )

        # Return non-zero exit code if there were errors
        return 1 if stats["errors"] > 0 else 0

    except KeyboardInterrupt:
        print("\nCleanup interrupted by user.")
        return 1
    except Exception as e:
        print(f"Cleanup failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
