# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: git_yaml_fixer.py
# version: 1.0.0
# uuid: 1707c3a1-1073-4909-885c-ab9035ac324a
# author: OmniNode Team
# created_at: 2025-05-27T17:23:39.856216
# last_modified_at: 2025-05-27T21:27:01.044114
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 00b8f2e2d0d950c520f2d50145cda7fbd3316125b0cad0109bd24f4a65590c51
# entrypoint: python@git_yaml_fixer.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.git_yaml_fixer
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Git-based YAML fixer that uses Git history to restore proper formatting.

This script:
1. Identifies YAML files with formatting issues
2. Searches Git history for versions that parse correctly
3. Restores the properly formatted versions
4. Validates that the content is semantically equivalent
"""

import argparse
import difflib
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from pydantic import ValidationError

from omnibase.model.model_github_actions import GitHubActionsWorkflow

# Import ONEX models for validation
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_state_contract import StateContractModel

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_git_file_history(file_path: Path, max_commits: int = 50) -> List[str]:
    """
    Get the commit hashes where the file was last modified.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--format=%H", "-n", str(max_commits), "--", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        logger.warning(f"Could not get Git history for {file_path}")
        return []


def get_file_content_at_commit(file_path: Path, commit_hash: str) -> Optional[str]:
    """
    Get the content of a file at a specific commit.
    """
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:{file_path}"],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout
    except subprocess.CalledProcessError:
        return None


def detect_yaml_model_type(file_path: Path, content: str) -> Optional[type]:
    """
    Detect which Pydantic model should be used for this YAML file.
    """
    if file_path.name == "node.onex.yaml":
        return NodeMetadataBlock
    elif file_path.name == "contract.yaml" or "state_contract" in str(file_path):
        return StateContractModel
    elif file_path.name in ["ci.yml", "ci.yaml"] or ".github/workflows" in str(
        file_path
    ):
        return GitHubActionsWorkflow

    # Try to detect from content
    try:
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            if "entrypoint" in data and "namespace" in data and "meta_type" in data:
                return NodeMetadataBlock
            elif "input_state" in data or "output_state" in data:
                return StateContractModel
            elif "on" in data or True in data and "jobs" in data:
                return GitHubActionsWorkflow
    except yaml.YAMLError:
        pass

    return None


def validate_yaml_with_model(
    content: str, model_type: type
) -> Tuple[bool, Optional[str]]:
    """
    Validate YAML content with a Pydantic model.
    Returns (is_valid, error_message).
    """
    try:
        # Handle GitHub Actions special case
        if model_type == GitHubActionsWorkflow:
            # Fix the 'true:' -> 'on:' issue if present
            import re

            content = re.sub(r"^true:$", '"on":', content, flags=re.MULTILINE)

        data = yaml.safe_load(content)
        if data is None:
            return False, "Empty YAML content"

        model_type(**data)
        return True, None

    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except ValidationError as e:
        return False, f"Validation error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def are_yaml_contents_equivalent(
    content1: str, content2: str, model_type: Optional[type] = None
) -> bool:
    """
    Check if two YAML contents are semantically equivalent.
    """
    try:
        # Handle GitHub Actions special case for both contents
        if model_type == GitHubActionsWorkflow:
            import re

            content1 = re.sub(r"^true:$", '"on":', content1, flags=re.MULTILINE)
            content2 = re.sub(r"^true:$", '"on":', content2, flags=re.MULTILINE)

        data1 = yaml.safe_load(content1)
        data2 = yaml.safe_load(content2)

        return bool(data1 == data2)
    except yaml.YAMLError:
        return False


def find_good_version_in_history(
    file_path: Path, current_content: str
) -> Optional[Tuple[str, str]]:
    """
    Find a version in Git history that parses correctly and is semantically equivalent.
    Returns (commit_hash, content) or None.
    """
    model_type = detect_yaml_model_type(file_path, current_content)

    # First, check if current content is already valid
    if model_type:
        is_valid, error = validate_yaml_with_model(current_content, model_type)
        if is_valid:
            logger.debug(f"{file_path} is already valid")
            return None
    else:
        # For files without specific models, just check if they parse as YAML
        try:
            yaml.safe_load(current_content)
            logger.debug(f"{file_path} parses as valid YAML")
            return None
        except yaml.YAMLError:
            pass

    logger.info(f"Searching Git history for valid version of {file_path}")

    commit_hashes = get_git_file_history(file_path)
    if not commit_hashes:
        logger.warning(f"No Git history found for {file_path}")
        return None

    for i, commit_hash in enumerate(commit_hashes):
        historical_content = get_file_content_at_commit(file_path, commit_hash)
        if historical_content is None:
            continue

        # Check if this version is valid
        if model_type:
            is_valid, error = validate_yaml_with_model(historical_content, model_type)
            if not is_valid:
                logger.debug(f"Commit {commit_hash[:8]} invalid: {error}")
                continue
        else:
            try:
                yaml.safe_load(historical_content)
            except yaml.YAMLError as e:
                logger.debug(f"Commit {commit_hash[:8]} invalid YAML: {e}")
                continue

        # Check if semantically equivalent
        if are_yaml_contents_equivalent(
            current_content, historical_content, model_type
        ):
            logger.info(
                f"Found valid equivalent version at commit {commit_hash[:8]} (commit {i+1}/{len(commit_hashes)})"
            )
            return commit_hash, historical_content
        else:
            logger.debug(f"Commit {commit_hash[:8]} valid but not equivalent")

    logger.warning(
        f"No valid equivalent version found in {len(commit_hashes)} commits for {file_path}"
    )
    return None


def fix_yaml_from_git_history(
    file_path: Path, dry_run: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Fix a YAML file using Git history.
    Returns (was_fixed, fixed_content_if_dry_run).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        result = find_good_version_in_history(file_path, current_content)
        if result is None:
            return False, None

        commit_hash, historical_content = result

        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(historical_content)
            logger.info(f"Restored {file_path} from commit {commit_hash[:8]}")

        return True, historical_content if dry_run else None

    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return False, None


def get_yaml_files() -> List[Path]:
    """Get all YAML files in the repository, excluding intentionally invalid test files."""
    all_yaml_files = list(Path(".").rglob("*.yaml")) + list(Path(".").rglob("*.yml"))

    # Filter out intentionally invalid test files
    filtered_files = []
    for file_path in all_yaml_files:
        # Skip files that are intentionally invalid for testing
        if "invalid_" in file_path.name and "testdata" in str(file_path):
            continue
        filtered_files.append(file_path)

    return filtered_files


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Git-based YAML fixer")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--file", type=Path, help="Fix a specific file instead of all YAML files"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.file:
        yaml_files = [args.file]
    else:
        yaml_files = get_yaml_files()

    if not yaml_files:
        logger.info("No YAML files found")
        return 0

    logger.info(f"Found {len(yaml_files)} YAML files to process")

    fixed_count = 0
    for file_path in yaml_files:
        if args.verbose:
            logger.info(f"Processing: {file_path}")

        was_fixed, fixed_content = fix_yaml_from_git_history(
            file_path, dry_run=args.dry_run
        )

        if was_fixed:
            fixed_count += 1
            status = "would be restored" if args.dry_run else "restored"
            logger.info(f"  {status}: {file_path}")

            if args.dry_run and fixed_content:
                # Show diff for dry run
                with open(file_path, "r", encoding="utf-8") as f:
                    original_lines = f.readlines()
                fixed_lines = fixed_content.splitlines(keepends=True)
                diff = difflib.unified_diff(
                    original_lines,
                    fixed_lines,
                    fromfile=f"a/{file_path}",
                    tofile=f"b/{file_path}",
                    lineterm="",
                )
                diff_output = "".join(diff)
                if diff_output:
                    print(diff_output)
        elif args.verbose:
            logger.info(f"  no fix needed: {file_path}")

    if args.dry_run:
        logger.info(
            f"\nDry run complete. {fixed_count} files would be restored from Git history."
        )
    else:
        logger.info(
            f"\nGit-based YAML fixing complete. {fixed_count} files restored from Git history."
        )

    return 0


if __name__ == "__main__":
    exit(main())
