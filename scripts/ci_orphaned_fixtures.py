# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: ci_orphaned_fixtures.py
# version: 1.0.0
# uuid: cad27ec1-e0af-420c-b41b-fa9568452af7
# author: OmniNode Team
# created_at: 2025-05-28T12:36:25.202407
# last_modified_at: 2025-05-28T17:20:05.250723
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 17ee55fdb212d0d99bf21e51e7d2bf33c4314f6a6a323c0ecdd2d02eb3d1f40f
# entrypoint: python@ci_orphaned_fixtures.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.ci_orphaned_fixtures
# meta_type: tool
# === /OmniNode:Metadata ===


#!/usr/bin/env python3
"""
CI script to detect orphaned fixtures and unused data files.

This script scans for unreferenced YAML/JSON files in fixture directories
and reports them for cleanup. It helps prevent drift and bloat from
accumulating unused test assets.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set


class OrphanedFixtureDetector:
    """Detector for orphaned fixtures and unused data files."""

    def __init__(self, root_dir: Optional[Path] = None):
        """Initialize the detector."""
        self.root_dir = root_dir or Path.cwd()
        self.fixture_dirs = [
            "tests/fixtures",
            "tests/data",
            "src/omnibase/schemas/schemas_tests/testdata",
            "tests/validation/directory_tree/test_case",
        ]
        self.node_fixture_pattern = "src/omnibase/nodes/*/v1_0_0/node_tests/fixtures"

    def find_all_fixture_files(self) -> Dict[str, List[Path]]:
        """Find all fixture files in known directories."""
        fixture_files = {}

        # Find files in standard fixture directories
        for fixture_dir in self.fixture_dirs:
            dir_path = self.root_dir / fixture_dir
            if dir_path.exists():
                files = (
                    list(dir_path.rglob("*.yaml"))
                    + list(dir_path.rglob("*.yml"))
                    + list(dir_path.rglob("*.json"))
                )
                if files:
                    fixture_files[fixture_dir] = files

        # Find files in node-local fixture directories
        nodes_dir = self.root_dir / "src/omnibase/nodes"
        if nodes_dir.exists():
            for node_dir in nodes_dir.iterdir():
                if not node_dir.is_dir():
                    continue

                for version_dir in node_dir.iterdir():
                    if not version_dir.is_dir() or not version_dir.name.startswith("v"):
                        continue

                    fixtures_dir = version_dir / "node_tests" / "fixtures"
                    if fixtures_dir.exists():
                        files = (
                            list(fixtures_dir.rglob("*.yaml"))
                            + list(fixtures_dir.rglob("*.yml"))
                            + list(fixtures_dir.rglob("*.json"))
                        )
                        if files:
                            relative_path = str(fixtures_dir.relative_to(self.root_dir))
                            fixture_files[relative_path] = files

        return fixture_files

    def find_fixture_references(self) -> Set[str]:
        """Find all references to fixture files in Python code."""
        references = set()

        # Search in all Python files
        for py_file in self.root_dir.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")

                # Find string literals that might be fixture references
                string_literals = self._extract_string_literals(content)
                for literal in string_literals:
                    if self._looks_like_fixture_reference(literal):
                        references.add(literal)

                # Find file path patterns in the content
                file_patterns = re.findall(
                    r'["\']([^"\']*\.(?:yaml|yml|json))["\']', content
                )
                for pattern in file_patterns:
                    references.add(pattern)

            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")

        return references

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped during analysis."""
        skip_patterns = [
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            "node_modules",
            ".git",
            ".venv",
            "venv",
        ]

        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _extract_string_literals(self, content: str) -> List[str]:
        """Extract string literals from Python code."""
        literals = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    literals.append(node.value)
        except SyntaxError:
            # Fallback to regex if AST parsing fails
            string_patterns = [r'"([^"]*)"', r"'([^']*)'"]
            for pattern in string_patterns:
                matches = re.findall(pattern, content)
                literals.extend(matches)

        return literals

    def _looks_like_fixture_reference(self, literal: str) -> bool:
        """Check if a string literal looks like a fixture reference."""
        # Check for file extensions
        if not any(literal.endswith(ext) for ext in [".yaml", ".yml", ".json"]):
            return False

        # Check for fixture-like patterns
        fixture_indicators = [
            "test",
            "fixture",
            "data",
            "valid",
            "invalid",
            "sample",
            "mock",
        ]

        return any(indicator in literal.lower() for indicator in fixture_indicators)

    def detect_orphaned_fixtures(self) -> Dict[str, List[Path]]:
        """Detect orphaned fixtures that are not referenced in code."""
        fixture_files = self.find_all_fixture_files()
        references = self.find_fixture_references()

        orphaned = {}

        for directory, files in fixture_files.items():
            orphaned_in_dir = []

            for file_path in files:
                # Check if file is referenced
                file_name = file_path.name
                relative_path = str(file_path.relative_to(self.root_dir))

                is_referenced = any(
                    ref in file_name
                    or ref in relative_path
                    or file_name in ref
                    or relative_path in ref
                    for ref in references
                )

                if not is_referenced:
                    orphaned_in_dir.append(file_path)

            if orphaned_in_dir:
                orphaned[directory] = orphaned_in_dir

        return orphaned

    def generate_report(self) -> str:
        """Generate a report of orphaned fixtures."""
        orphaned = self.detect_orphaned_fixtures()

        if not orphaned:
            return "✅ No orphaned fixtures detected."

        report = ["🔍 Orphaned Fixture Detection Report", "=" * 50, ""]

        total_orphaned = 0
        for directory, files in orphaned.items():
            report.append(f"📁 {directory}:")
            for file_path in files:
                relative_path = file_path.relative_to(self.root_dir)
                report.append(f"  - {relative_path}")
                total_orphaned += 1
            report.append("")

        report.extend(
            [
                f"Total orphaned files: {total_orphaned}",
                "",
                "💡 Recommendations:",
                "- Review each file to determine if it's still needed",
                "- Remove unused fixtures to prevent bloat",
                "- Update references if files are actually used but not detected",
                "- Consider adding .onexignore entries for intentionally unused files",
            ]
        )

        return "\n".join(report)


def main() -> int:
    """Main entry point for the script."""
    detector = OrphanedFixtureDetector()
    report = detector.generate_report()

    print(report)

    # Return non-zero exit code if orphaned fixtures are found
    orphaned = detector.detect_orphaned_fixtures()
    return 1 if orphaned else 0


if __name__ == "__main__":
    sys.exit(main())
