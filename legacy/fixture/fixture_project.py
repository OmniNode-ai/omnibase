# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_fixture_project"
# namespace: "omninode.tools.test_fixture_project"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:24+00:00"
# last_modified_at: "2025-05-05T13:00:24+00:00"
# entrypoint: "test_fixture_project.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import logging

from foundation.script.validation.validator_registry import get_registered_fixture
from foundation.fixture.project.python.python_fixture_project import (
    ProjectStructureFixture,
)


def test_project_structure_fixture_basic():
    logger = logging.getLogger(__name__)
    structure = {
        "dirs": ["src", "tests"],
        "files": {"README.md": "# Project\nTest"},
        "metadata": {"owner": "test", "type": "demo"},
    }
    fixture = ProjectStructureFixture(structure)
    project_root = fixture.get_fixture()
    try:
        assert (project_root / "src").is_dir()
        assert (project_root / "tests").is_dir()
        assert (project_root / "README.md").is_file()
        assert (project_root / ".project-meta").is_file()
        logger.info(f"Project root: {project_root}")
        logger.info(f"README.md content: {(project_root / 'README.md').read_text()}")
        logger.info(
            f".project-meta content: {(project_root / '.project-meta').read_text()}"
        )
    finally:
        fixture.cleanup()


def test_project_structure_fixture_registry():
    fixture = get_registered_fixture()
    assert "project_structure_fixture" in fixture
    assert issubclass(fixture["project_structure_fixture"], ProjectStructureFixture)