# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:25.245663'
# description: Stamped by PythonHandler
# entrypoint: python://comprehensive_yaml_fixer.py
# hash: 0335bda02f42cf35389776ff4aff4ef9d54a10bdbf1e146ca13dece4bf053b04
# last_modified_at: '2025-05-29T13:51:13.779848+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: comprehensive_yaml_fixer.py
# namespace: py://omnibase.comprehensive_yaml_fixer_py
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 3ff942e3-e297-45f1-b2ca-7a68a14d5492
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Comprehensive YAML fixer using Pydantic models for proper serialization.

This script fixes YAML formatting issues by:
1. Loading YAML files using appropriate Pydantic models
2. Re-serializing them with proper formatting
3. Ensuring consistent indentation and structure

Uses existing ONEX Pydantic models for type-safe YAML handling.
"""

import argparse
import difflib
import logging
import re
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel, ValidationError

from omnibase.model.model_github_actions import GitHubActionsWorkflow

# Import ONEX models
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.model.model_state_contract import StateContractModel

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def detect_yaml_type(file_path: Path, content: str) -> Optional[str]:
    """
    Detect the type of YAML file based on path and content.
    Returns the model type to use for parsing.
    """
    # Check file path patterns
    if file_path.name == "node.onex.yaml":
        return "node_metadata"
    elif file_path.name == "contract.yaml":
        return "state_contract"
    elif "state_contract" in str(file_path):
        return "state_contract"
    elif file_path.name == "ci.yml" or ".github/workflows" in str(file_path):
        return "github_actions"
    elif file_path.suffix in [".yml", ".yaml"] and "schemas" in str(file_path):
        return "json_schema"
    elif file_path.name == "runtime.yaml":
        return "runtime_config"
    elif file_path.name == "cli_tool.yaml":
        return "cli_tool_config"

    # Check content patterns
    try:
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            # Check for JSON Schema markers
            if "$schema" in data or "$id" in data or "SCHEMA_VERSION" in data:
                return "json_schema"
            # Check for GitHub Actions markers
            elif "on" in data or "jobs" in data or "runs-on" in data:
                return "github_actions"
            # Check for node metadata fields
            elif "entrypoint" in data and "namespace" in data and "meta_type" in data:
                return "node_metadata"
            # Check for state contract fields
            elif (
                "input_state" in data
                or "output_state" in data
                or "contract_version" in data
            ):
                return "state_contract"
            # Check for runtime config
            elif "components" in data and "capabilities" in data:
                return "runtime_config"
    except yaml.YAMLError:
        pass

    return "generic"


def fix_basic_yaml_indentation(content: str) -> str:
    """
    Pre-process YAML content to fix basic indentation issues that prevent parsing.
    This standardizes all indentation to 2-space increments.
    """
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Remove trailing spaces
        line = line.rstrip()

        if line.strip():
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)

            # Convert any indentation to 2-space increments
            # Count the logical indentation level (how many levels deep)
            if current_indent > 0:
                # Estimate indentation level based on original spacing
                # This handles both 2-space and 4-space indentation
                if current_indent <= 2:
                    level = 1
                elif current_indent <= 4:
                    level = 2
                elif current_indent <= 6:
                    level = 3
                elif current_indent <= 8:
                    level = 4
                else:
                    # For deeper indentation, assume 2-space increments
                    level = (current_indent + 1) // 2

                # Convert to 2-space indentation
                proper_indent = level * 2
            else:
                proper_indent = 0

            line = " " * proper_indent + stripped

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def fix_github_actions_indentation(content: str) -> str:
    """
    Fix GitHub Actions specific indentation issues.
    """
    lines = content.split("\n")
    fixed_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if line.strip():
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)

            # Check if this is a step in a GitHub Actions workflow
            if stripped.startswith("- ") and (
                "name:" in stripped or "uses:" in stripped or "run:" in stripped
            ):
                # This is a step - add it with proper indentation
                step_indent = ((current_indent + 1) // 2) * 2
                fixed_lines.append(" " * step_indent + stripped)

                # Look ahead for step properties that should be at the same level
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].rstrip()
                    if not next_line.strip():
                        fixed_lines.append(next_line)
                        j += 1
                        continue

                    next_stripped = next_line.lstrip()
                    next_indent = len(next_line) - len(next_stripped)

                    # Check if this is a step property (uses, with, run, env, if, etc.)
                    step_properties = [
                        "uses:",
                        "run:",
                        "with:",
                        "env:",
                        "if:",
                        "continue-on-error:",
                        "timeout-minutes:",
                        "working-directory:",
                        "shell:",
                    ]

                    if any(next_stripped.startswith(prop) for prop in step_properties):
                        # This should be at the same level as the step content (step_indent + 2)
                        fixed_lines.append(" " * (step_indent + 2) + next_stripped)
                        j += 1

                        # If this is 'with:', look for its nested properties
                        if next_stripped.startswith("with:"):
                            k = j
                            while k < len(lines):
                                with_line = lines[k].rstrip()
                                if not with_line.strip():
                                    fixed_lines.append(with_line)
                                    k += 1
                                    continue

                                with_stripped = with_line.lstrip()
                                with_indent = len(with_line) - len(with_stripped)

                                # If this looks like a property of 'with', indent it properly
                                if (
                                    ":" in with_stripped
                                    and not with_stripped.startswith("- ")
                                ):
                                    # Check if this is still part of the 'with' block
                                    if with_indent > next_indent or (
                                        with_indent == next_indent
                                        and not any(
                                            with_stripped.startswith(prop)
                                            for prop in step_properties
                                        )
                                    ):
                                        fixed_lines.append(
                                            " " * (step_indent + 4) + with_stripped
                                        )
                                        k += 1
                                    else:
                                        # This is a new step property or next step
                                        break
                                else:
                                    # This is a new step or other structure
                                    break
                            j = k
                            continue
                    elif next_stripped.startswith("- "):
                        # This is the next step
                        break
                    elif ":" in next_stripped and next_indent <= current_indent:
                        # This is a new job or top-level property
                        break
                    else:
                        # This might be a continuation of a multiline value
                        # Keep the relative indentation but ensure it's properly nested
                        if next_indent > current_indent:
                            fixed_lines.append(" " * (step_indent + 4) + next_stripped)
                        else:
                            fixed_lines.append(
                                " " * ((next_indent + 1) // 2 * 2) + next_stripped
                            )
                        j += 1

                i = j
                continue

        # For non-step lines, apply standard indentation fixing
        if line.strip():
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            proper_indent = ((current_indent + 1) // 2) * 2
            fixed_lines.append(" " * proper_indent + stripped)
        else:
            fixed_lines.append(line)

        i += 1

    return "\n".join(fixed_lines)


def fix_yaml_with_model(content: str, model_class: type[BaseModel]) -> Optional[str]:
    """
    Fix YAML content using a specific Pydantic model.
    Returns the fixed content or None if it can't be parsed.
    """
    try:
        # First, try to fix basic YAML syntax issues
        if model_class.__name__ == "GitHubActionsWorkflow":
            # Apply GitHub Actions specific preprocessing
            preprocessed_content = re.sub(
                r"^true:$", '"on":', content, flags=re.MULTILINE
            )
            preprocessed_content = fix_github_actions_indentation(preprocessed_content)
        else:
            preprocessed_content = fix_basic_yaml_indentation(content)

        # Parse YAML
        data = yaml.safe_load(preprocessed_content)
        if data is None:
            return None

        # Validate with Pydantic model
        model_instance = model_class(**data)

        # Serialize back to YAML with proper formatting
        # Use the model's serialization method if available, otherwise model_dump
        if hasattr(model_instance, "to_serializable_dict"):
            clean_data = model_instance.to_serializable_dict()
        else:
            clean_data = model_instance.model_dump(
                exclude_unset=False, exclude_none=True
            )

        # Format as YAML with consistent style
        formatted = yaml.dump(
            clean_data,
            default_flow_style=False,
            indent=2,
            width=120,
            allow_unicode=True,
            sort_keys=False,
        )

        # Ensure document starts with ---
        if not formatted.startswith("---"):
            formatted = "---\n" + formatted

        # Ensure single newline at end
        formatted = formatted.rstrip() + "\n"

        return formatted

    except (yaml.YAMLError, ValidationError, TypeError) as e:
        logger.debug(f"Could not parse with {model_class.__name__}: {e}")
        return None


def fix_generic_yaml(content: str) -> Optional[str]:
    """
    Fix generic YAML files that don't match specific models.
    """
    try:
        # First, try to fix basic YAML syntax issues
        preprocessed_content = fix_basic_yaml_indentation(content)

        # Parse and reformat
        data = yaml.safe_load(preprocessed_content)
        if data is None:
            return None

        formatted = yaml.dump(
            data,
            default_flow_style=False,
            indent=2,
            width=120,
            allow_unicode=True,
            sort_keys=False,
        )

        # Ensure document starts with ---
        if not formatted.startswith("---"):
            formatted = "---\n" + formatted

        # Ensure single newline at end
        formatted = formatted.rstrip() + "\n"

        return formatted

    except yaml.YAMLError as e:
        logger.debug(f"Could not parse as generic YAML: {e}")
        return None


def fix_github_actions_yaml(content: str) -> Optional[str]:
    """
    Fix GitHub Actions YAML files with their specific structure.
    """
    try:
        # Fix common GitHub Actions syntax errors
        fixed_content = content

        # Fix "true:" -> "on:" (common mistake)
        fixed_content = re.sub(r"^true:\s*$", "on:", fixed_content, flags=re.MULTILINE)

        # Apply basic indentation fixes
        fixed_content = fix_basic_yaml_indentation(fixed_content)

        # Parse and reformat
        data = yaml.safe_load(fixed_content)
        if data is None:
            return None

        formatted = yaml.dump(
            data,
            default_flow_style=False,
            indent=2,
            width=120,
            allow_unicode=True,
            sort_keys=False,
        )

        # Ensure document starts with ---
        if not formatted.startswith("---"):
            formatted = "---\n" + formatted

        # Ensure single newline at end
        formatted = formatted.rstrip() + "\n"

        return formatted

    except yaml.YAMLError as e:
        logger.debug(f"Could not parse as GitHub Actions YAML: {e}")
        return None


def fix_json_schema_yaml(content: str) -> Optional[str]:
    """
    Fix JSON Schema YAML files.
    """
    try:
        # Apply basic indentation fixes
        fixed_content = fix_basic_yaml_indentation(content)

        # Parse and reformat
        data = yaml.safe_load(fixed_content)
        if data is None:
            return None

        formatted = yaml.dump(
            data,
            default_flow_style=False,
            indent=2,
            width=120,
            allow_unicode=True,
            sort_keys=False,
        )

        # Ensure document starts with ---
        if not formatted.startswith("---"):
            formatted = "---\n" + formatted

        # Ensure single newline at end
        formatted = formatted.rstrip() + "\n"

        return formatted

    except yaml.YAMLError as e:
        logger.debug(f"Could not parse as JSON Schema YAML: {e}")
        return None


def fix_comprehensive_yaml_issues(
    file_path: Path, dry_run: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Fix YAML issues using appropriate Pydantic models.

    Returns (was_modified, fixed_content_if_dry_run).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # Skip empty files
        if not original_content.strip():
            return False, None

        # Detect YAML type and choose appropriate model
        yaml_type = detect_yaml_type(file_path, original_content)

        fixed_content = None

        if yaml_type == "node_metadata":
            fixed_content = fix_yaml_with_model(original_content, NodeMetadataBlock)
        elif yaml_type == "state_contract":
            fixed_content = fix_yaml_with_model(original_content, StateContractModel)
        elif yaml_type == "github_actions":
            fixed_content = fix_yaml_with_model(original_content, GitHubActionsWorkflow)
        elif yaml_type == "json_schema":
            fixed_content = fix_json_schema_yaml(original_content)
        elif yaml_type in ["runtime_config", "cli_tool_config"]:
            # These are configuration files that don't have specific models yet
            # Use generic YAML handling with pre-processing
            fixed_content = fix_generic_yaml(original_content)

        # If we still couldn't fix it, return unchanged
        if fixed_content is None:
            logger.warning(f"Could not parse or fix {file_path}")
            return False, None

        # Validate the fixed content can be parsed
        try:
            yaml.safe_load(fixed_content)
        except yaml.YAMLError as validate_err:
            logger.error(f"Post-fix validation failed for {file_path}: {validate_err}")
            return False, None

        # Check if content was actually modified
        if fixed_content != original_content:
            if not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
            return True, fixed_content if dry_run else None

        return False, None

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
    parser = argparse.ArgumentParser(description="YAML fixer using Pydantic models")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    yaml_files = get_yaml_files()

    if not yaml_files:
        logger.info("No YAML files found")
        return 0

    logger.info(f"Found {len(yaml_files)} YAML files to process")

    modified_count = 0
    for file_path in yaml_files:
        if args.verbose:
            logger.info(f"Processing: {file_path}")

        was_modified, fixed_content = fix_comprehensive_yaml_issues(
            file_path, dry_run=args.dry_run
        )

        if was_modified:
            modified_count += 1
            status = "would be modified" if args.dry_run else "modified"
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
            logger.info(f"  unchanged: {file_path}")

    if args.dry_run:
        logger.info(f"\nDry run complete. {modified_count} files would be modified.")
    else:
        logger.info(f"\nYAML fixing complete. {modified_count} files modified.")

    return 0


if __name__ == "__main__":
    exit(main())
