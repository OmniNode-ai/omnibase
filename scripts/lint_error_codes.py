# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: lint_error_codes.py
# version: 1.0.0
# uuid: caa31246-9598-4dca-8cd1-87dbb8cad2a7
# author: OmniNode Team
# created_at: 2025-05-26T10:11:38.403536
# last_modified_at: 2025-05-26T16:53:38.722840
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 9d558667e6b349daba19d33ff0581d28a86603f69061320147c035edbcc0bc2e
# entrypoint: python@lint_error_codes.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.lint_error_codes
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
Error Code Usage Linter for ONEX

This script validates that all error handling in the ONEX codebase follows
the centralized error code patterns defined in src/omnibase/core/error_codes.py.

Checks performed:
1. All exceptions should use OnexError or subclasses instead of generic exceptions
2. All error codes should be registered in the central registry
3. All nodes should define their error codes in error_codes.py modules
4. Generic exceptions (ValueError, RuntimeError, etc.) should be avoided in favor of OnexError

Exit codes:
- 0: All checks passed
- 1: Error code violations found
- 2: Script execution error
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Generic exceptions that should be replaced with OnexError
FORBIDDEN_EXCEPTIONS = {
    "Exception",
    "ValueError",
    "RuntimeError",
    "FileNotFoundError",
    "IOError",
    "OSError",
    "TypeError",
    "AttributeError",
    "KeyError",
    "IndexError",
}

# Only truly system-level exceptions are allowed
ALLOWED_EXCEPTIONS = {
    "SystemExit",  # For CLI exit handling
    "KeyboardInterrupt",  # For signal handling
    "StopIteration",  # For iterators
    "GeneratorExit",  # For generators
}

# Patterns for test files and other exceptions
TEST_FILE_PATTERNS = [
    r"test_.*\.py$",
    r".*_test\.py$",
    r"tests/.*\.py$",
    r"conftest\.py$",
]


EXCEPTION_ALLOWLIST: List[str] = [
    # No exceptions needed - all files should use OnexError
]


class ErrorCodeLinter:
    """Linter for ONEX error code usage patterns."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.violations: List[Tuple[str, int, str]] = []
        self.registered_components: Set[str] = set()

    def is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        file_str = str(file_path)
        return any(re.search(pattern, file_str) for pattern in TEST_FILE_PATTERNS)

    def is_allowlisted(self, file_path: Path) -> bool:
        """Check if a file is in the exception allowlist."""
        file_str = str(file_path.relative_to(self.root_dir))
        return file_str in EXCEPTION_ALLOWLIST

    def find_registered_components(self) -> None:
        """Find all registered error code components."""
        error_codes_files = list(self.root_dir.rglob("**/error_codes.py"))

        for file_path in error_codes_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for register_error_codes calls
                matches = re.findall(
                    r'register_error_codes\(["\']([^"\']+)["\']', content
                )
                self.registered_components.update(matches)

            except Exception as e:
                print(f"Warning: Could not parse {file_path}: {e}")

    def check_file(self, file_path: Path) -> None:
        """Check a single Python file for error code violations."""
        # Zero legacy debt policy - no exemptions
        if self.is_allowlisted(file_path):
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))
            self._check_ast_node(tree, file_path)

        except SyntaxError as e:
            print(f"Warning: Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")

    def _check_ast_node(self, node: ast.AST, file_path: Path) -> None:
        """Recursively check AST nodes for violations."""
        if isinstance(node, ast.Raise):
            self._check_raise_statement(node, file_path)

        for child in ast.iter_child_nodes(node):
            self._check_ast_node(child, file_path)

    def _check_raise_statement(self, node: ast.Raise, file_path: Path) -> None:
        """Check a raise statement for proper error code usage."""
        if node.exc is None:
            return  # Re-raise statement

        # Check for direct exception instantiation
        if isinstance(node.exc, ast.Call):
            if isinstance(node.exc.func, ast.Name):
                exception_name = node.exc.func.id
                if exception_name in FORBIDDEN_EXCEPTIONS:
                    self.violations.append(
                        (
                            str(file_path.relative_to(self.root_dir)),
                            node.lineno,
                            f"Use OnexError instead of {exception_name}",
                        )
                    )

        # Check for exception references
        elif isinstance(node.exc, ast.Name):
            exception_name = node.exc.id
            if exception_name in FORBIDDEN_EXCEPTIONS:
                self.violations.append(
                    (
                        str(file_path.relative_to(self.root_dir)),
                        node.lineno,
                        f"Use OnexError instead of {exception_name}",
                    )
                )

    def check_node_error_codes(self) -> None:
        """Check that all nodes have proper error code definitions."""
        nodes_dir = self.root_dir / "src" / "omnibase" / "nodes"
        if not nodes_dir.exists():
            return

        for node_dir in nodes_dir.iterdir():
            if not node_dir.is_dir():
                continue

            # Look for versioned subdirectories
            for version_dir in node_dir.iterdir():
                if not version_dir.is_dir() or not re.match(
                    r"v\d+_\d+_\d+", version_dir.name
                ):
                    continue

                error_codes_file = version_dir / "error_codes.py"
                if not error_codes_file.exists():
                    self.violations.append(
                        (
                            str(version_dir.relative_to(self.root_dir)),
                            0,
                            "Missing error_codes.py module",
                        )
                    )
                    continue

                # Check if error codes are registered
                component_name = node_dir.name.replace("_node", "")
                if component_name not in self.registered_components:
                    self.violations.append(
                        (
                            str(error_codes_file.relative_to(self.root_dir)),
                            0,
                            f"Error codes not registered for component '{component_name}'",
                        )
                    )

    def run(self) -> int:
        """Run all error code checks."""
        print("🔍 Checking error code usage patterns...")

        # Find registered components first
        self.find_registered_components()
        print(
            f"Found {len(self.registered_components)} registered components: {sorted(self.registered_components)}"
        )

        # Check all Python files
        python_files = list(self.root_dir.rglob("**/*.py"))
        for file_path in python_files:
            self.check_file(file_path)

        # Check node error code definitions
        self.check_node_error_codes()

        # Report results
        if self.violations:
            print(f"\n❌ Found {len(self.violations)} error code violations:")
            for file_path_str, line_no, message in sorted(self.violations):
                if line_no > 0:
                    print(f"  {file_path_str}:{line_no}: {message}")
                else:
                    print(f"  {file_path_str}: {message}")
            return 1
        else:
            print("✅ All error code checks passed!")
            return 0


def main() -> int:
    """Main entry point."""
    if len(sys.argv) > 1:
        root_dir = Path(sys.argv[1])
    else:
        root_dir = Path.cwd()

    if not root_dir.exists():
        print(f"Error: Directory {root_dir} does not exist")
        return 2

    linter = ErrorCodeLinter(root_dir)
    return linter.run()


if __name__ == "__main__":
    sys.exit(main())
