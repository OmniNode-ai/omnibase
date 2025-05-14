# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_python_fixture_project"
# namespace: "omninode.tools.test_python_fixture_project"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:25+00:00"
# last_modified_at: "2025-05-05T13:00:25+00:00"
# entrypoint: "test_python_fixture_project.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['BaseTestFixture', 'IProjectStructureFixture']
# base_class: ['BaseTestFixture', 'IProjectStructureFixture']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""
ProjectStructureFixture: Provides a temp project root directory with customizable structure for maintainable, extensible tests.
Registry-registered, DI-compliant, and supports adding files, subdirectories, and metadata.

Usage Example:
    fixture = ProjectStructureFixture({
        "files": {"README.md": "# Project\n.."},
        "dirs": ["src", "tests"],
    })
    project_root = fixture.get_fixture()
    # project_root is a Path to the temp project directory
"""

import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from foundation.fixture import BaseTestFixture
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.script.validate.validate_registry import register_fixture


class ProjectStructureFixture(BaseTestFixture, ProtocolValidateFixture):
    """Fixture for a temp project root directory with customizable structure."""

    def __init__(self, structure: Optional[Dict[str, Any]] = None):
        self.project_root = Path(tempfile.mkdtemp())
        self.structure = structure or {}
        self._populate_structure(self.structure)

    def _populate_structure(self, structure: Dict[str, Any]):
        # Add directories
        for d in structure.get("dirs", []):
            (self.project_root / d).mkdir(parents=True, exist_ok=True)
        # Add files
        for fname, content in structure.get("files", {}).items():
            fpath = self.project_root / fname
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content)
        # Add metadata (optional, e.g., .project-meta)
        if "metadata" in structure:
            meta_path = self.project_root / ".project-meta"
            meta_path.write_text(str(structure["metadata"]))

    def add_file(self, rel_path: str, content: str = "") -> None:
        fpath = self.project_root / rel_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        fpath.write_text(content)

    def add_dir(self, rel_path: str) -> None:
        (self.project_root / rel_path).mkdir(parents=True, exist_ok=True)

    def get_fixture(self) -> Path:
        return self.project_root

    def cleanup(self) -> None:
        shutil.rmtree(self.project_root)


register_fixture(
    name="project_structure_fixture",
    fixture=ProjectStructureFixture,
    description="Fixture for a temp project root directory with customizable structure for maintainable, extensible tests.",
    interface=ProtocolValidateFixture,
)