#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: util_validate_docstrings
# namespace: omninode.tools.util_validate_docstrings
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:52+00:00
# last_modified_at: 2025-04-27T18:12:52+00:00
# entrypoint: util_validate_docstrings.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""
util_validate_docstrings.py
containers.foundation.src.foundation.script.utils.util_validate_docstrings

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
import glob
import os
import subprocess
import sys
from typing import Dict, List

# Configure paths for importing utils module
# This works both when running from the repository and as a git hook
repo_root = os.path.abspath(
    os.getcwd()
)  # Get repo root (hooks run with cwd at repo root)
# sys.path.append(os.path.join(repo_root, 'scripts'))

# Constants for docstring validation
REQUIRED_SECTIONS = ["Args", "Returns"]
OPTIONAL_SECTIONS = ["Raises", "Examples", "Notes", "Attributes", "Warning"]
VALID_SECTIONS = REQUIRED_SECTIONS + OPTIONAL_SECTIONS


def check_file_docstrings(file_path: str) -> Dict[str, List[str]]:
    """Check docstrings in a file for proper formatting.

    Args:
        file_path (str): Path to Python file to check

    Returns:
        Dict[str, List[str]]: Dictionary with invalid docstrings by function name
    """
    with open(file_path, "r") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return {"SYNTAX_ERROR": [str(e)]}

    invalid_docstrings = {}

    # Check module-level docstring
    module_docstring = ast.get_docstring(tree)
    if module_docstring:
        errors = validate_docstring("Module", module_docstring)
        if errors:
            invalid_docstrings["Module"] = errors

    # Check function and class docstrings
    for node in ast.walk(tree):
        # For functions
        if isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node)
            if docstring:
                errors = validate_docstring(node.name, docstring)
                if errors:
                    invalid_docstrings[node.name] = errors

        # For classes
        elif isinstance(node, ast.ClassDef):
            # Check class docstring
            class_docstring = ast.get_docstring(node)
            if class_docstring:
                errors = validate_docstring(f"Class {node.name}", class_docstring)
                if errors:
                    invalid_docstrings[f"Class {node.name}"] = errors

            # Check method docstrings
            for method in [n for n in node.body if isinstance(n, ast.FunctionDef)]:
                method_docstring = ast.get_docstring(method)
                if method_docstring:
                    errors = validate_docstring(
                        f"{node.name}.{method.name}", method_docstring
                    )
                    if errors:
                        invalid_docstrings[f"{node.name}.{method.name}"] = errors

    return invalid_docstrings


def validate_docstring(name: str, docstring: str) -> List[str]:
    """Validate a docstring for proper formatting.

    Args:
        name (str): Name of the function or class
        docstring (str): Docstring to validate

    Returns:
        List[str]: List of error messages
    """
    errors = []

    # Skip private methods (starting with _)
    if name.split(".")[-1].startswith("_") and name.split(".")[-1] != "__init__":
        return []

    # Check for empty docstring
    if not docstring.strip():
        return ["Empty docstring"]

    # Split docstring into lines and strip whitespace
    lines = [line.strip() for line in docstring.split("\n")]

    # Verify there's a summary line
    if not lines[0]:
        errors.append("Missing summary line")

    # Find all section headers
    section_headers = []
    for i, line in enumerate(lines):
        if i > 0 and line and line[-1] == ":" and not line.startswith("    "):
            header = line[:-1].strip()
            section_headers.append(header)

    # Check for required section headers
    for section in REQUIRED_SECTIONS:
        if section not in section_headers:
            errors.append(f"Missing required section: {section}")

    # Check for invalid section headers
    for header in section_headers:
        if header not in VALID_SECTIONS:
            errors.append(f"Invalid section header: {header}")

    return errors


def get_python_files(include_patterns: List[str]) -> List[str]:
    """Get all Python files matching the given patterns.

    Args:
        include_patterns (List[str]): List of patterns to include

    Returns:
        List[str]: List of Python file paths
    """
    python_files = set()
    for pattern in include_patterns:
        python_files.update(glob.glob(pattern, recursive=True))

    # Filter out files that aren't Python
    return [f for f in python_files if f.endswith(".py")]


def print_errors(invalid_files: Dict[str, Dict[str, List[str]]]) -> None:
    """Print docstring errors in a readable format.

    Args:
        invalid_files (Dict[str, Dict[str, List[str]]]): Dictionary of invalid files
    """
    total_errors = sum(len(funcs) for funcs in invalid_files.values())
    total_files = len(invalid_files)

    print(f"\nFound {total_errors} docstring issues in {total_files} files:")

    for file_path, invalid_functions in invalid_files.items():
        print(f"\n📄 {file_path}")
        for func_name, errors in invalid_functions.items():
            print(f"  🔸 {func_name}:")
            for error in errors:
                print(f"    - {error}")


def prompt_user_for_action(invalid_files: Dict[str, Dict[str, List[str]]]) -> str:
    """Prompt user for action on invalid files.

    Args:
        invalid_files (Dict[str, Dict[str, List[str]]]): Dictionary of invalid files

    Returns:
        str: User action choice ('fix', 'bypass', 'abort')
    """
    print("\nFound docstring issues. What would you like to do?")
    print("1) Fix issues automatically (using format_python_file.py)")
    print("2) Bypass validation for this commit")
    print("3) Abort commit")

    while True:
        choice = input("\nEnter your choice (1-3): ")
        if choice == "1":
            return "fix"
        elif choice == "2":
            return "bypass"
        elif choice == "3":
            return "abort"
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


def reformat_files(
    invalid_files: Dict[str, Dict[str, List[str]]], interactive: bool = False
) -> bool:
    """Reformat invalid files using format_python_file.py.

    Args:
        invalid_files (Dict[str, Dict[str, List[str]]]): Dictionary of invalid files
        interactive (bool): Whether to prompt user for action

    Returns:
        bool: True if all files were reformatted successfully or user chose to bypass
    """
    if not invalid_files:
        return True

    if interactive:
        action = prompt_user_for_action(invalid_files)
        if action == "bypass":
            print("Bypassing docstring validation for this commit.")
            return True
        elif action == "abort":
            print("Aborting commit due to docstring issues.")
            return False

    # Get path to util_format_headers.py
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reformat_script = os.path.join(script_dir, "utils", "util_format_headers.py")

    # Make sure reformat script exists
    if not os.path.exists(reformat_script):
        print(f"Error: Cannot find format_python_file.py at {reformat_script}")
        return False

    success = True
    print(f"\nAttempting to fix docstring issues in {len(invalid_files)} files..")
    for file_path in invalid_files:
        try:
            result = subprocess.run(
                [sys.executable, reformat_script, file_path, "--stage"],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✓ Fixed docstring header in {file_path}")
        except subprocess.CalledProcessError as e:
            print(f"× Failed to fix {file_path}: {e.stderr}")
            success = False

    return success


def main() -> int:
    """Main entry point for the docstring validator.

    Returns:
        int: Exit code
    """
    # Check for the --interactive flag
    interactive = "--interactive" in sys.argv
    if interactive:
        sys.argv.remove("--interactive")

    # Get staged Python files from git
    staged_files = []
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True,
            text=True,
            check=True,
        )
        staged_files = [f for f in result.stdout.splitlines() if f.endswith(".py")]
    except subprocess.CalledProcessError as e:
        print(f"Error getting staged files: {e.stderr}")
        return 1

    # Process command line arguments
    if len(sys.argv) > 1:
        # If specific files are provided, validate only those
        python_files = [f for f in sys.argv[1:] if f.endswith(".py")]
    else:
        # Otherwise validate all staged Python files
        python_files = staged_files

    if not python_files:
        print("No Python files to validate.")
        return 0

    # Check docstrings in all files
    invalid_files = {}
    for file_path in python_files:
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            continue

        invalid_docstrings = check_file_docstrings(file_path)
        if invalid_docstrings:
            invalid_files[file_path] = invalid_docstrings

    # If all docstrings are valid, exit with success
    if not invalid_files:
        print("All docstrings are valid.")
        return 0

    # Print out the errors
    print_errors(invalid_files)

    # Attempt to reformat files or prompt user for action
    if reformat_files(invalid_files, interactive):
        return 0
    else:
        return 1


if __name__ == "__main__":
    from foundation.bootstrap.bootstrap import bootstrap
    bootstrap()
    sys.exit(main())
