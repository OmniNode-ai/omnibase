# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:25.283236'
# description: Stamped by PythonHandler
# entrypoint: python://hybrid_yaml_fixer.py
# hash: 66a7f2376bb388feabc8c7516a542e47600d3daaf1212b284f92b62ad0a1aa09
# last_modified_at: '2025-05-29T11:50:10.550058+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: hybrid_yaml_fixer.py
# namespace: omnibase.hybrid_yaml_fixer
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 0d9eb09c-aa22-4ec5-a5ea-597274b1577d
# version: 1.0.0
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Hybrid YAML fixer that combines Pydantic models with Git history fallback.

This script:
1. First tries to fix YAML files using Pydantic models (fast, preserves content)
2. Falls back to Git history for files that can't be fixed algorithmically
3. Provides comprehensive reporting on what was fixed and how
"""

import argparse
import difflib
import logging
import sys
from pathlib import Path
from typing import Optional, Tuple

import yaml

# Add the project root to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Project imports
try:
    from scripts.comprehensive_yaml_fixer import fix_comprehensive_yaml_issues
    from scripts.comprehensive_yaml_fixer import (
        get_yaml_files as get_yaml_files_comprehensive,
    )
    from scripts.git_yaml_fixer import (
        detect_yaml_model_type,
        fix_yaml_from_git_history,
        validate_yaml_with_model,
    )
except ImportError as e:
    print(f"Error importing project modules: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def is_yaml_file_problematic(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Check if a YAML file has formatting or parsing issues.
    Returns (has_problems, error_description).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # First check if it parses as YAML
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            return True, f"YAML parsing error: {e}"

        # Check if it validates against its expected model
        model_type = detect_yaml_model_type(file_path, content)
        if model_type:
            is_valid, error = validate_yaml_with_model(content, model_type)
            if not is_valid:
                return True, f"Model validation error: {error}"

        return False, None

    except Exception as e:
        return True, f"File reading error: {e}"


def fix_yaml_hybrid(
    file_path: Path, dry_run: bool = False
) -> Tuple[bool, str, Optional[str]]:
    """
    Fix a YAML file using hybrid approach.
    Returns (was_fixed, method_used, fixed_content_if_dry_run).
    """
    # First, check if the file actually has problems
    has_problems, error_desc = is_yaml_file_problematic(file_path)
    if not has_problems:
        return False, "no_fix_needed", None

    logger.debug(f"{file_path} has problems: {error_desc}")

    # Strategy 1: Try Pydantic-based fixing
    logger.debug(f"Trying Pydantic-based fix for {file_path}")
    was_fixed_pydantic, fixed_content_pydantic = fix_comprehensive_yaml_issues(
        file_path, dry_run=True
    )

    if was_fixed_pydantic and fixed_content_pydantic:
        # Verify the fix actually resolves the problems
        try:
            yaml.safe_load(fixed_content_pydantic)
            model_type = detect_yaml_model_type(file_path, fixed_content_pydantic)
            if model_type:
                is_valid, _ = validate_yaml_with_model(
                    fixed_content_pydantic, model_type
                )
                if is_valid:
                    # Pydantic fix worked!
                    if not dry_run:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(fixed_content_pydantic)
                    return (
                        True,
                        "pydantic_model",
                        fixed_content_pydantic if dry_run else None,
                    )
            else:
                # No specific model, but YAML parses - good enough
                if not dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(fixed_content_pydantic)
                return (
                    True,
                    "pydantic_generic",
                    fixed_content_pydantic if dry_run else None,
                )
        except Exception as e:
            logger.debug(f"Pydantic fix validation failed: {e}")

    # Strategy 2: Try Git history fallback
    logger.debug(f"Trying Git history fix for {file_path}")
    was_fixed_git, fixed_content_git = fix_yaml_from_git_history(
        file_path, dry_run=True
    )

    if was_fixed_git and fixed_content_git:
        # Git fix worked!
        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content_git)
        return True, "git_history", fixed_content_git if dry_run else None

    # Strategy 3: Try basic YAML reformatting (last resort)
    logger.debug(f"Trying basic YAML reformat for {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to parse and reformat
        data = yaml.safe_load(content)
        if data is not None:
            reformatted = yaml.dump(
                data,
                default_flow_style=False,
                indent=2,
                width=120,
                allow_unicode=True,
                sort_keys=False,
            )

            if not reformatted.startswith("---"):
                reformatted = "---\n" + reformatted
            reformatted = reformatted.rstrip() + "\n"

            if reformatted != content:
                if not dry_run:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(reformatted)
                return True, "basic_reformat", reformatted if dry_run else None
    except Exception as e:
        logger.debug(f"Basic reformat failed: {e}")

    return False, "unfixable", None


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Hybrid YAML fixer (Pydantic + Git history)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument(
        "--file", type=Path, help="Fix a specific file instead of all YAML files"
    )
    parser.add_argument(
        "--strategy",
        choices=["pydantic", "git", "hybrid"],
        default="hybrid",
        help="Choose fixing strategy",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.file:
        yaml_files = [args.file]
    else:
        yaml_files = get_yaml_files_comprehensive()

    if not yaml_files:
        logger.info("No YAML files found")
        return 0

    logger.info(f"Found {len(yaml_files)} YAML files to process")

    # Statistics
    stats = {
        "total": len(yaml_files),
        "no_fix_needed": 0,
        "pydantic_model": 0,
        "pydantic_generic": 0,
        "git_history": 0,
        "basic_reformat": 0,
        "unfixable": 0,
    }

    for file_path in yaml_files:
        if args.verbose:
            logger.info(f"Processing: {file_path}")

        if args.strategy == "pydantic":
            was_fixed, fixed_content = fix_comprehensive_yaml_issues(
                file_path, dry_run=args.dry_run
            )
            method = "pydantic_model" if was_fixed else "no_fix_needed"
        elif args.strategy == "git":
            was_fixed, fixed_content = fix_yaml_from_git_history(
                file_path, dry_run=args.dry_run
            )
            method = "git_history" if was_fixed else "no_fix_needed"
        else:  # hybrid
            was_fixed, method, fixed_content = fix_yaml_hybrid(
                file_path, dry_run=args.dry_run
            )

        stats[method] += 1

        if was_fixed:
            status = "would be fixed" if args.dry_run else "fixed"
            logger.info(f"  {status} ({method}): {file_path}")

            if args.dry_run and fixed_content and args.verbose:
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
            logger.info(f"  {method}: {file_path}")

    # Report statistics
    fixed_count = (
        stats["pydantic_model"]
        + stats["pydantic_generic"]
        + stats["git_history"]
        + stats["basic_reformat"]
    )

    logger.info("\n=== SUMMARY ===")
    logger.info(f"Total files: {stats['total']}")
    logger.info(f"No fix needed: {stats['no_fix_needed']}")
    logger.info(f"Fixed by Pydantic models: {stats['pydantic_model']}")
    logger.info(f"Fixed by Pydantic generic: {stats['pydantic_generic']}")
    logger.info(f"Fixed by Git history: {stats['git_history']}")
    logger.info(f"Fixed by basic reformat: {stats['basic_reformat']}")
    logger.info(f"Unfixable: {stats['unfixable']}")

    if args.dry_run:
        logger.info(f"\nDry run complete. {fixed_count} files would be fixed.")
    else:
        logger.info(f"\nHybrid YAML fixing complete. {fixed_count} files fixed.")

    return 0


if __name__ == "__main__":
    exit(main())
