#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: util_format_headers
# namespace: omninode.tools.util_format_headers
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:53+00:00
# last_modified_at: 2025-04-27T18:12:53+00:00
# entrypoint: util_format_headers.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
util_format_headers.py
containers.foundation.src.foundation.script.utils.util_format_headers

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import difflib
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Set, Tuple

# Configure paths for importing utils module
# This works both when running from the repository and as a git hook
repo_root = os.path.abspath(
    os.getcwd()
)  # Get repo root (hooks run with cwd at repo root)
# sys.path.append(os.path.join(repo_root, 'scripts'))

try:
    from foundation.script.utils.util_header_templates import (
        SHEBANG,
        get_formatted_docstring,
        get_formatted_header,
        get_header_template,
        get_module_docstring_template,
    )
except ModuleNotFoundError:
    print(
        "Error: Unable to import template_utils. Make sure you are running this script from the repository root."
    )
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def detect_and_remove_header(content: str) -> Tuple[str, bool]:
    """
    Detect and remove existing header from file content.

    Args:
        content: The file content

    Returns:
        Tuple of (content with header removed, whether header was found)
    """
    lines = content.splitlines()
    header_end = 0

    # Skip shebang if present
    if lines and lines[0].startswith("#!"):
        header_end = 1

    # Look for copyright and other header lines
    for i in range(header_end, min(10, len(lines))):
        if not lines[i].startswith("#") and lines[i].strip():
            # Found non-header content
            header_end = i
            break
        if "Copyright" in lines[i] or "Author" in lines[i]:
            # Continue looking for end of header
            header_end = i + 1

    # Check if we found a header
    header_found = header_end > 0

    # Skip any blank lines after header
    while header_end < len(lines) and not lines[header_end].strip():
        header_end += 1

    # Return content without header
    return "\n".join(lines[header_end:]), header_found


def detect_and_remove_docstring(content: str) -> Tuple[str, bool]:
    """
    Detect and remove existing module docstring from content.

    Args:
        content: The file content

    Returns:
        Tuple of (content with docstring removed, whether docstring was found)
    """
    lines = content.splitlines()

    # Find docstring start
    docstring_start = None
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('"""') or line.startswith("'''"):
            docstring_start = i
            break
        elif line and not line.startswith("#"):
            # Found non-comment, non-docstring content
            break

    if docstring_start is None:
        return content, False

    # Find docstring end
    docstring_quotes = lines[docstring_start].strip()[0:3]
    docstring_end = None

    # Also check for single-quotes docstring
    for i in range(docstring_start, len(lines)):
        if i > docstring_start and docstring_quotes in lines[i]:
            docstring_end = i
            break

    if docstring_end is None:
        # Could not find matching end quotes
        return content, False

    # Skip any blank lines after docstring
    code_start = docstring_end + 1
    while code_start < len(lines) and not lines[code_start].strip():
        code_start += 1

    # Return content without docstring
    return "\n".join(lines[code_start:]), True


def strip_top_block(content: str) -> str:
    """
    Remove any top-level shebang, contiguous comment block, docstring, and blank lines.
    Returns the rest of the file starting at the first real code/import.
    """
    lines = content.splitlines()
    i = 0
    n = len(lines)
    # Remove shebang
    if i < n and lines[i].startswith("#!"):
        i += 1
    # Remove contiguous comment block
    while i < n and (lines[i].strip().startswith("#") or not lines[i].strip()):
        i += 1
    # Remove top-level docstring (triple quotes)
    if i < n and (
        lines[i].strip().startswith('"""') or lines[i].strip().startswith("'''")
    ):
        quote = lines[i].strip()[:3]
        i += 1
        while i < n and quote not in lines[i]:
            i += 1
        if i < n:
            i += 1  # skip closing quotes
        # Remove any blank lines after docstring
        while i < n and not lines[i].strip():
            i += 1
    # Return the rest
    return "\n".join(lines[i:]).lstrip()


def format_file(
    filepath: str,
    dry_run: bool = False,
    verbose: bool = False,
    check_only: bool = False,
) -> bool:
    """
    Format a Python file with proper header and module docstring.
    Args:
        filepath: Path to the file
        dry_run: If True, only show changes without modifying the file
        verbose: If True, show detailed information
        check_only: If True, only report files that would be changed
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            original_content = f.read()
        if not original_content.strip():
            logger.info(f"Skipping empty file: {filepath}")
            return True
        filename = os.path.basename(filepath)
        # Remove all legacy top blocks
        rest = strip_top_block(original_content)
        # Remove any existing docstring from the rest
        rest, _ = detect_and_remove_docstring(rest)
        header_lines = get_formatted_header(filename)
        header_text = "\n".join(header_lines)
        # Compute namespace
        rel_path = os.path.relpath(filepath, repo_root)
        namespace = rel_path.replace(os.sep, ".").rsplit(".py", 1)[0]
        docstring_template = get_module_docstring_template()
        docstring_text = docstring_template.replace("{File Name}", filename).replace(
            "{Namespace}", namespace
        )
        new_content = (
            f"{header_text}\n\n" + '"""' + docstring_text + '\n"""' + f"\n\n{rest}"
        )
        if original_content == new_content:
            if verbose:
                logger.info(f"No changes needed for {filepath}")
            return True
        if check_only:
            print(f"Would update: {filepath}")
            return False
        if verbose:
            diff = difflib.unified_diff(
                original_content.splitlines(True),
                new_content.splitlines(True),
                fromfile=f"a/{filepath}",
                tofile=f"b/{filepath}",
                n=3,
            )
            logger.info(f"Changes for {filepath}:")
            sys.stdout.writelines(diff)
        if not dry_run:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            logger.info(f"Formatted {filepath}")
        else:
            logger.info(f"Would format {filepath} (dry run)")
        return True
    except Exception as e:
        logger.error(f"Error formatting {filepath}: {str(e)}")
        return False


def get_files_staged_for_deletion() -> Set[str]:
    """
    Get a set of files that are staged for deletion in git.

    Returns:
        Set of file paths that are staged for deletion
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse output lines like "D       path/to/file.py"
        # Only include lines that start with D (deleted)
        deleted_files = set()
        for line in result.stdout.splitlines():
            if line.strip().startswith("D"):
                parts = line.strip().split(maxsplit=1)
                if len(parts) > 1:
                    deleted_files.add(parts[1].strip())

        logger.debug(f"Files staged for deletion: {deleted_files}")
        return deleted_files
    except subprocess.CalledProcessError:
        logger.warning("Failed to get files staged for deletion")
        return set()


def process_paths(
    paths, dry_run=False, verbose=False, staged=False, check_only=False
) -> bool:
    changed = 0
    compliant = 0
    files_checked = 0
    deleted_files = get_files_staged_for_deletion()
    logger.debug(f"Found {len(deleted_files)} files staged for deletion")
    success = True

    def process_file(p):
        nonlocal changed, compliant, files_checked, success
        files_checked += 1
        result = format_file(p, dry_run, verbose, check_only)
        if result:
            compliant += 1
        else:
            changed += 1
            success = False

    if staged:
        # Get staged files
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Filter for Python files
            python_files = [
                Path(file.strip())
                for file in result.stdout.splitlines()
                if file.strip().endswith(".py")
                and file.strip() not in deleted_files
                and os.path.isfile(file.strip())
            ]

            if verbose:
                logger.info(f"Found {len(python_files)} staged Python files")
                for file in python_files:
                    logger.info(f"  {file}")

            # Process each file
            for python_file in python_files:
                process_file(python_file)

        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting staged files: {e}")
            success = False
    else:
        # Process each path provided
        for path in paths:
            path_obj = Path(path)

            # Skip files staged for deletion
            if str(path_obj) in deleted_files:
                logger.info(f"Skipping {path_obj} (staged for deletion)")
                continue

            if not path_obj.exists():
                logger.error(f"Path does not exist: {path}")
                success = False
                continue

            if path_obj.is_file():
                # Process a single file
                if path_obj.suffix == ".py":
                    process_file(path_obj)
                else:
                    logger.warning(f"Skipping non-Python file: {path}")
            elif path_obj.is_dir():
                # Exclude cache and virtual environment directories
                exclude_dirs = {
                    ".venv",
                    "venv",
                    "__pycache__",
                    ".mypy_cache",
                    ".pytest_cache",
                    ".tox",
                    ".eggs",
                    ".cache",
                }
                for python_file in path_obj.glob("**/*.py"):
                    # Skip files in excluded directories
                    if any(part in exclude_dirs for part in python_file.parts):
                        logger.info(f"Skipping {python_file} (excluded directory)")
                        continue
                    # Skip files staged for deletion within directory
                    if str(python_file) in deleted_files:
                        logger.info(f"Skipping {python_file} (staged for deletion)")
                        continue
                    process_file(python_file)
            else:
                logger.error(f"Unknown path type: {path}")
                success = False
    print(
        f"\nSummary: {compliant} files already compliant, {changed} files updated, {files_checked} files checked."
    )
    return success


def lint_file(filepath: str) -> bool:
    """
    Lint a Python file to check that the filename and namespace in the header and docstring match the actual file.
    Returns True if compliant, False if not.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    filename = os.path.basename(filepath)
    rel_path = os.path.relpath(filepath, repo_root)
    namespace = rel_path.replace(os.sep, ".").rsplit(".py", 1)[0]
    # Check header
    header_ok = any(f"# Filename: {filename}" in line for line in lines[:10])
    # Check docstring (look for filename and namespace in first 20 lines)
    docstring_ok = any(filename in line for line in lines[:20]) and any(
        namespace in line for line in lines[:20]
    )
    if not header_ok or not docstring_ok:
        print(f"Lint error in {filepath}:")
        if not header_ok:
            print(f"  - Header filename mismatch (expected: {filename})")
        if not docstring_ok:
            print(
                f"  - Docstring filename or namespace mismatch (expected: {filename}, {namespace})"
            )
        return False
    return True


def lint_paths(paths) -> int:
    """Lint all Python files in the given paths. Returns number of errors found."""
    errors = 0
    for path in paths:
        path_obj = Path(path)
        if path_obj.is_file() and path_obj.suffix == ".py":
            if not lint_file(str(path_obj)):
                errors += 1
        elif path_obj.is_dir():
            for python_file in path_obj.glob("**/*.py"):
                if not lint_file(str(python_file)):
                    errors += 1
    print(f"\nLint summary: {errors} files with errors.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Format Python files with consistent headers and docstrings"
    )
    parser.add_argument(
        "paths", nargs="*", help="Paths to format (files or directories)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without modifying files"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed information"
    )
    parser.add_argument("--stage", action="store_true", help="Process git staged files")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only report files that would be changed (for CI)",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Lint files for filename/namespace compliance",
    )
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    if args.stage:
        success = process_paths(
            args.paths, args.dry_run, args.verbose, True, args.check
        )
        return 0 if success else 1
    if not args.paths:
        logger.error("No paths specified")
        parser.print_help()
        return 1
    if args.lint:
        errors = lint_paths(args.paths)
        return 1 if errors else 0
    success = process_paths(args.paths, args.dry_run, args.verbose, False, args.check)
    return 0 if success else 1


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    sys.exit(main())
