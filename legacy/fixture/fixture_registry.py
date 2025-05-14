# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "fixture_registry"
# namespace: "omninode.tools.fixture_registry"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "fixture_registry.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===



import os
import tempfile
import logging
from pathlib import Path
from foundation.script.validate.python.python_validate_chunk import PythonValidateChunk
import structlog
from foundation.fixture.fixture_tree_file_utils import FixtureTreeFileUtils
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture

class ChunkValidatorFixture:
    def get_fixture(self, python: bool = True):
        if python:
            return PythonValidateChunk(config={}, logger=structlog.get_logger("test_chunk_validator"))
        raise NotImplementedError("Only python=True is supported for this fixture.")

class FixtureRegistry:
    def __init__(self):
        self._fixtures = {}

    def register_fixture(self, name, fixture, description=None, interface=None):
        self._fixtures[name] = fixture

    def get_fixture(self, name):
        return self._fixtures.get(name)

FIXTURE_REGISTRY = FixtureRegistry()

def setup_test_fixtures():
    from foundation.script.validate.validate_registry import register_fixture
    def _register_fixture_patch(name, fixture, description=None, interface=None):
        FIXTURE_REGISTRY.register_fixture(name, fixture, description, interface)
        return register_fixture(name=name, fixture=fixture, description=description, interface=interface)
    import foundation.script.validate.validate_registry as _validate_registry_mod
    _validate_registry_mod.register_fixture = _register_fixture_patch

    _register_fixture_patch(
        name="chunk_validator_fixture",
        fixture=ChunkValidatorFixture,
        description="DI/registry-compliant fixture for chunk validator (Python, class with get_fixture)",
    )

    class ChunkToolFixture:
        def get_fixture(self):
            return DummyChunkTool()

    _register_fixture_patch(
        name="chunk_tool_fixture",
        fixture=ChunkToolFixture(),
        description="DI/registry-compliant fixture for chunk tool (Python, instance with get_fixture)",
    )

    _register_fixture_patch(
        name="tree_file_utils_fixture",
        fixture=FixtureTreeFileUtils(),
        description="Mock/in-memory fixture for tree file utility protocol (for directory tree tests)",
    )

    class TempPyFileFixture(ProtocolValidateFixture):
        def get_fixture(self, config=None):
            import tempfile, os
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write("""
class A:
    pass
class B(A):
    pass
class C(B):
    pass
""")
                fname = f.name
            try:
                yield Path(fname)
            finally:
                os.remove(fname)

    class TempInvalidPyFileFixture(ProtocolValidateFixture):
        def get_fixture(self, config=None):
            import tempfile, os
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write("class A: bad syntax here")
                fname = f.name
            try:
                yield Path(fname)
            finally:
                os.remove(fname)

    class LoggerFixture(ProtocolValidateFixture):
        def get_fixture(self, config=None):
            import logging
            logger = logging.getLogger("test_logger")
            logger.setLevel(logging.DEBUG)
            return logger

    _register_fixture_patch(
        name="temp_py_file",
        fixture=TempPyFileFixture(),
        description="Fixture for a temporary Python file",
    )

    _register_fixture_patch(
        name="temp_invalid_py_file",
        fixture=TempInvalidPyFileFixture(),
        description="Fixture for an invalid Python file",
    )

    _register_fixture_patch(
        name="logger",
        fixture=LoggerFixture(),
        description="Fixture for a logger",
    )

class DummyChunkTool:
    def process(self, fname):
        # Dummy implementation for test; replace with real tool logic if available
        class Result:
            def __init__(self, valid):
                self.is_valid = valid
        fname_str = str(fname)
        if "invalid" in fname_str:
            return Result(False)
        if "valid" in fname_str:
            return Result(True)
        return Result(False) 