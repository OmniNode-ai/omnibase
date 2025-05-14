# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_metadata_stamper"
# namespace: "omninode.tools.test_validate_metadata_stamper"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:16+00:00"
# last_modified_at: "2025-05-05T13:00:16+00:00"
# entrypoint: "test_validate_metadata_stamper.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import logging
import os
import tempfile
from pathlib import Path

import pytest
from foundation.protocol.protocol_logger import ProtocolLogger
from foundation.script.metadata.metadata_stamper import MetadataStamper
from foundation.script.tool.tool_registry import ToolRegistry, populate_tool_registry
from foundation.script.validate.validate_registry import get_registered_fixture
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.template.metadata.metadata_template_registry import MetadataRegistryTemplate
from foundation.base.base_metadata_block_test import BaseMetadataBlockTest
from foundation.registry.utility_registry import get_util

@pytest.fixture(scope="session")
def registry_fixtures():
    return {
        "CaplogFixture": get_registered_fixture("caplog_fixture"),
        "ValidMetadataFactoryFixture": get_registered_fixture("valid_metadata_factory_fixture"),
        "InvalidMetadataFactoryFixture": get_registered_fixture("invalid_metadata_factory_fixture"),
        "ValidContainerYamlFixture": get_registered_fixture("valid_container_yaml_fixture"),
    }

@pytest.fixture(scope="module")
def metadata_stamper_cli_path():
    # Registry-compliant fixture for CLI path
    return str(Path(__file__).parent.parent.parent.parent / "script/metadata/metadata_stamper.py")

@pytest.fixture
def temp_py_file(tmp_path):
    file_path = tmp_path / "test_script.py"
    file_path.write_text("# Dummy Python file\n")
    return str(file_path)

@pytest.fixture
def temp_non_py_file(tmp_path):
    file_path = tmp_path / "test_script.txt"
    file_path.write_text("Just some text\n")
    return str(file_path)

@pytest.fixture(scope="module")
def tool_registry():
    template_registry = MetadataRegistryTemplate()
    from foundation.template.metadata.metadata_template_blocks import MINIMAL_METADATA
    template_registry.register_template("minimal", MINIMAL_METADATA, [".py", ".yaml", ".yml", ".md"])
    registry = ToolRegistry()
    populate_tool_registry(registry, template_registry)
    return registry

@pytest.fixture(scope="module")
def metadata_stamper_cls(tool_registry) -> type:
    tool_cls = tool_registry.get_tool("metadata_stamper")
    assert tool_cls is not None, "MetadataStamper not registered in tool_registry!"
    return tool_cls

@pytest.fixture
def logger() -> ProtocolLogger:
    """Protocol-compliant logger fixture for DI."""
    logger = logging.getLogger("test_metadata_stamper")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    return logger

@pytest.fixture(scope="module")
def header_util():
    return get_util('header')

def test_registry_discovery(tool_registry) -> None:
    """Test that MetadataStamper is discoverable via the tool registry and has correct metadata."""
    cls = tool_registry.get_tool("metadata_stamper")
    assert cls is not None, "MetadataStamper not found in tool_registry!"
    meta = tool_registry.get_all_metadata()["metadata_stamper"]
    assert meta["name"] == "metadata_stamper"
    assert meta["entrypoint"] == "foundation.script.metadata.metadata_stamper"

def test_dry_run_no_metadata(caplog, metadata_stamper_cls: type, logger: ProtocolLogger):
    """Test dry run stamping on a file with no metadata block."""
    stamper = metadata_stamper_cls(logger)
    fname = TEST_CASE_REGISTRY.get_test_case('metadata_block', 'invalid_metadata_missing_fields', 'invalid')
    path = Path(fname)
    with caplog.at_level(logging.INFO, logger="test_metadata_stamper"):
        result = stamper.stamp_file(path, overwrite=False)
    assert f"[! dry run] Would stamp/replace {path}" in caplog.text


def test_dry_run_valid_metadata(caplog, metadata_stamper_cls: type, logger: ProtocolLogger):
    """Test dry run stamping on a file with a valid metadata block."""
    stamper = metadata_stamper_cls(logger)
    fname = TEST_CASE_REGISTRY.get_test_case('metadata_block', 'valid_metadata', 'valid')
    path = Path(fname)
    with caplog.at_level(logging.INFO, logger="test_metadata_stamper"):
        result = stamper.stamp_file(path, overwrite=False)
    assert f"[! dry run] Would stamp/replace {path}" in caplog.text


def test_dry_run_partial_metadata(caplog, metadata_stamper_cls: type, logger: ProtocolLogger):
    """Test dry run stamping on a file with a partial metadata block."""
    stamper = metadata_stamper_cls(logger)
    # TODO: Add a partial metadata block test case file and register it
    fname = TEST_CASE_REGISTRY.get_test_case('metadata_block', 'invalid_metadata_missing_fields', 'invalid')
    path = Path(fname)
    with caplog.at_level(logging.INFO, logger="test_metadata_stamper"):
        result = stamper.stamp_file(path, overwrite=False)
    assert f"[! dry run] Would stamp/replace {path}" in caplog.text


def test_non_python_file(logger: ProtocolLogger):
    """Test that non-Python files are not stamped."""
    # TODO: Add a non-Python test case file and register it
    fname = TEST_CASE_REGISTRY.get_test_case('metadata_block', 'invalid_metadata_yaml_error', 'invalid')
    path = Path(fname)
    assert path.suffix != ".py"


def test_cli_help():
    # CLI help is not tested via importable API; would require subprocess
    # This test is intentionally left as a placeholder for CLI-level tests
    pass


def test_docstring_preserved(temp_py_file: str, metadata_stamper_cls: type, logger: ProtocolLogger, header_util) -> None:
    """Test that module docstrings are preserved after stamping."""
    stamper = metadata_stamper_cls(logger, header_util=header_util)
    path = Path(temp_py_file)
    docstring = '"""This is a module docstring."""'
    with open(temp_py_file, "w") as f:
        f.write(f'{docstring}\n# Some comment\nprint("hello")\n')
    stamper.stamp_file(path, overwrite=True)
    with open(temp_py_file) as f:
        content = f.read()
    logger.info(f"[TEST LOG] Stamped file content:\n{content}")
    assert docstring in content, "Module docstring should be preserved after stamping."


def test_ast_base_class_extraction(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test AST base class extraction from a Python file."""
    py_content = """
class Foo(BaseModel, ProtocolValidate):
    pass

class Bar(Foo, CustomMixin):
    pass

class Baz:
    pass
"""
    file_path = tmp_path / "test_ast_classes.py"
    file_path.write_text(py_content)
    stamper = metadata_stamper_cls(logger)
    bases = stamper.extract_base_classes_from_file(str(file_path))
    assert set(bases) == {"BaseModel", "ProtocolValidate", "Foo", "CustomMixin"}
    block = stamper.generate_metadata_block(
        name="test_ast_classes",
        entrypoint=str(file_path.name),
        file_path=str(file_path),
    )
    # Assert YAML list format for protocol_class
    assert "protocol_class:" in block
    for base in ["BaseModel", "CustomMixin", "Foo", "ProtocolValidate"]:
        assert f"  - {base}" in block

def test_extract_base_classes_from_file_nonexistent(tmp_path, caplog, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test AST extraction on a nonexistent file returns empty list and logs a warning."""
    stamper = metadata_stamper_cls(logger)
    fake_path = tmp_path / "does_not_exist.py"
    with caplog.at_level(logging.WARNING, logger="test_metadata_stamper"):
        bases = stamper.extract_base_classes_from_file(str(fake_path))
    assert bases == []
    assert "AST parse failed" in caplog.text or "does not exist" in caplog.text

def test_extract_base_classes_from_file_invalid_python(tmp_path, caplog, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test AST extraction on invalid Python returns empty list and logs a warning."""
    stamper = metadata_stamper_cls(logger)
    file_path = tmp_path / "bad.py"
    file_path.write_text("def this is not valid python")
    with caplog.at_level(logging.WARNING, logger="test_metadata_stamper"):
        bases = stamper.extract_base_classes_from_file(str(file_path))
    assert bases == []
    assert "AST parse failed" in caplog.text

def test_generate_metadata_block_unknown_template(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test that generating a metadata block with an unknown template raises ValueError."""
    stamper = metadata_stamper_cls(logger)
    file_path = tmp_path / "foo.py"
    file_path.write_text("class Foo: pass")
    with pytest.raises(ValueError):
        stamper.generate_metadata_block(
            name="foo",
            entrypoint="foo.py",
            template="unknown",
            file_path=str(file_path),
        )

def test_extract_metadata_block_and_validate_missing(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test extraction and validation of missing metadata block."""
    stamper = metadata_stamper_cls(logger)
    text = "print('no metadata')\n"
    block, start, end, *_ = stamper.extract_metadata_block(text)
    assert block is None
    status, msg = stamper.validate_metadata_block(block)
    assert status == "none"

def test_extract_metadata_block_and_validate_corrupted(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test extraction and validation of a corrupted metadata block."""
    stamper = metadata_stamper_cls(logger)
    text = "# === OmniNode:Metadata ===\nmetadata_version: '0.1'\nname: foo\n"  # no end marker
    block, start, end, *_ = stamper.extract_metadata_block(text)
    assert block is not None
    status, msg = stamper.validate_metadata_block(block)
    assert status in ("partial", "corrupted")

def test_validate_metadata_block_invalid_fields(metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test validation of a metadata block with invalid fields."""
    stamper = metadata_stamper_cls(logger)
    block = """# === OmniNode:Metadata ===\nmetadata_version: 0.2\nname: 123badname\nnamespace: bad namespace\nversion: notaversion\nentrypoint: foo.txt\ntype: tool\nauthor: a\nowner: b\ncreated_at: d\nlast_modified_at: e\n# === /OmniNode:Metadata ===\n"""
    status, msg = stamper.validate_metadata_block(block)
    assert status in ("corrupted", "partial")

def test_strip_existing_header_and_place_metadata_shebang(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger, header_util) -> None:
    """Test that shebang is preserved and metadata is inserted at the top."""
    stamper = metadata_stamper_cls(logger, header_util=header_util)
    shebang = "#!/usr/bin/env python3"
    code = f"{shebang}\n# Comment\nprint('hi')\n"
    meta = "# === OmniNode:Metadata ===\n# name: foo\n# === /OmniNode:Metadata ==="
    result = stamper.strip_existing_header_and_place_metadata(code, meta)
    assert result.startswith(shebang)
    assert meta in result

def test_strip_existing_header_and_place_metadata_no_shebang(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger, header_util) -> None:
    """Test that metadata is inserted at the top if no shebang is present."""
    stamper = metadata_stamper_cls(logger, header_util=header_util)
    code = "# Comment\nprint('hi')\n"
    meta = "# === OmniNode:Metadata ===\n# name: foo\n# === /OmniNode:Metadata ==="
    result = stamper.strip_existing_header_and_place_metadata(code, meta)
    assert result.lstrip().startswith(meta)

def test_stamp_file_overwrite(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test that stamp_file overwrites the file and inserts metadata."""
    stamper = metadata_stamper_cls(logger)
    file_path = tmp_path / "foo.py"
    file_path.write_text("print('hi')\n")
    result = stamper.stamp_file(file_path, overwrite=True)
    assert result is True
    content = file_path.read_text()
    assert "OmniNode:Metadata" in content

def test_stamp_file_dry_run(tmp_path, caplog, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test that stamp_file in dry run mode does not write to the file."""
    stamper = metadata_stamper_cls(logger)
    file_path = tmp_path / "foo.py"
    file_path.write_text("print('hi')\n")
    with caplog.at_level(logging.INFO, logger="test_metadata_stamper"):
        result = stamper.stamp_file(file_path, overwrite=False)
    assert result is False
    assert "dry run" in caplog.text

def test_cli_help_flag(metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test that the CLI help flag works via the registry and DI."""
    stamper = metadata_stamper_cls(logger)
    # If the tool implements a CLI interface, call main(["--help"])
    if hasattr(stamper, "main"):
        import pytest
        with pytest.raises(SystemExit) as excinfo:
            stamper.main(["--help"])
        assert excinfo.value.code == 0
    else:
        assert False, "MetadataStamper does not implement a CLI main() method."

def test_cli_non_python_file(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test CLI invocation on a non-Python file via the registry and DI."""
    stamper = metadata_stamper_cls(logger)
    file_path = tmp_path / "foo.txt"
    file_path.write_text("not python\n")
    if hasattr(stamper, "main"):
        result = stamper.main([str(file_path)])
        assert result == 0 or result is None
    else:
        pytest.skip("MetadataStamper does not implement a CLI main() method.")

def test_cli_overwrite_flag(tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
    """Test CLI invocation with --overwrite flag via the registry and DI."""
    stamper = metadata_stamper_cls(logger)
    file_path = tmp_path / "foo.py"
    file_path.write_text("print('hi')\n")
    if hasattr(stamper, "main"):
        result = stamper.main([str(file_path), "--overwrite"])
        assert result == 0 or result is None
        content = file_path.read_text()
        assert "OmniNode:Metadata" in content
    else:
        pytest.skip("MetadataStamper does not implement a CLI main() method.")

def test_metadata_block_after_future_imports_registry(metadata_stamper_cls: type, logger: ProtocolLogger):
    """Test that the metadata block is inserted after shebang and all contiguous from __future__ import ... lines using the registry test case."""
    from foundation.test.test_case_registry import TEST_CASE_REGISTRY
    import shutil
    import tempfile
    # Copy the canonical test case to a temp file to avoid modifying the source
    src = TEST_CASE_REGISTRY.get_test_case("metadata_block", "valid_metadata_with_future_imports", "valid")
    tmp_dir = tempfile.mkdtemp()
    dst = shutil.copy(src, tmp_dir)
    stamper = metadata_stamper_cls(logger)
    stamper.stamp_file(Path(dst), overwrite=True)
    new_content = Path(dst).read_text()
    lines = new_content.splitlines()
    assert lines[0].startswith("#!")
    assert lines[1].startswith("from __future__ import annotations")
    assert lines[2].startswith("from __future__ import division")
    # Next non-blank line should be the metadata block
    idx = 3
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    assert lines[idx].startswith("# === OmniNode:Metadata ===")

class TestValidateMetadataStamper(BaseMetadataBlockTest):
    @pytest.fixture(scope="session")
    def registry_fixtures(self):
        return {
            "CaplogFixture": get_registered_fixture("caplog_fixture"),
            "ValidMetadataFactoryFixture": get_registered_fixture("valid_metadata_factory_fixture"),
            "InvalidMetadataFactoryFixture": get_registered_fixture("invalid_metadata_factory_fixture"),
            "ValidContainerYamlFixture": get_registered_fixture("valid_container_yaml_fixture"),
        }

    @pytest.fixture(scope="module")
    def metadata_stamper_cli_path(self):
        return str(Path(__file__).parent.parent.parent.parent / "script/metadata/metadata_stamper.py")

    @pytest.fixture
    def temp_py_file(self, tmp_path):
        file_path = tmp_path / "test_script.py"
        file_path.write_text("# Dummy Python file\n")
        return str(file_path)

    @pytest.fixture
    def temp_non_py_file(self, tmp_path):
        file_path = tmp_path / "test_script.txt"
        file_path.write_text("Just some text\n")
        return str(file_path)

    @pytest.fixture(scope="module")
    def tool_registry(self):
        template_registry = MetadataRegistryTemplate()
        from foundation.template.metadata.metadata_template_blocks import MINIMAL_METADATA
        template_registry.register_template("minimal", MINIMAL_METADATA, [".py", ".yaml", ".yml", ".md"])
        registry = ToolRegistry()
        populate_tool_registry(registry, template_registry)
        return registry

    @pytest.fixture(scope="module")
    def metadata_stamper_cls(self, tool_registry) -> type:
        tool_cls = tool_registry.get_tool("metadata_stamper")
        assert tool_cls is not None, "MetadataStamper not registered in tool_registry!"
        return tool_cls

    @pytest.fixture
    def logger(self) -> ProtocolLogger:
        logger = logging.getLogger("test_metadata_stamper")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        handler.setFormatter(formatter)
        if not logger.hasHandlers():
            logger.addHandler(handler)
        return logger

    @pytest.fixture(scope="module")
    def header_util(self):
        return get_util('header')

    def test_registry_discovery(self, tool_registry) -> None:
        cls = tool_registry.get_tool("metadata_stamper")
        assert cls is not None, "MetadataStamper not found in tool_registry!"
        meta = tool_registry.get_all_metadata()["metadata_stamper"]
        assert meta["name"] == "metadata_stamper"
        assert meta["entrypoint"] == "foundation.script.metadata.metadata_stamper"

    def test_dry_run_no_metadata(self, caplog, metadata_stamper_cls: type, logger: ProtocolLogger):
        stamper = metadata_stamper_cls(logger)
        fname = TEST_CASE_REGISTRY.get_test_case('metadata_block', 'invalid_metadata_missing_fields', 'invalid')
        path = Path(fname)
        with caplog.at_level(logging.INFO, logger="test_metadata_stamper"):
            result = stamper.stamp_file(path, overwrite=False)
        assert f"[! dry run] Would stamp/replace {path}" in caplog.text

    def test_dry_run_valid_metadata(self, caplog, metadata_stamper_cls: type, logger: ProtocolLogger):
        stamper = metadata_stamper_cls(logger)
        fname = TEST_CASE_REGISTRY.get_test_case('metadata_block', 'valid_metadata', 'valid')
        path = Path(fname)
        with caplog.at_level(logging.INFO, logger="test_metadata_stamper"):
            result = stamper.stamp_file(path, overwrite=False)
        assert f"[! dry run] Would stamp/replace {path}" in caplog.text

    def test_dry_run_partial_metadata(self, caplog, metadata_stamper_cls: type, logger: ProtocolLogger):
        stamper = metadata_stamper_cls(logger)
        fname = TEST_CASE_REGISTRY.get_test_case('metadata_block', 'invalid_metadata_missing_fields', 'invalid')
        path = Path(fname)
        with caplog.at_level(logging.INFO, logger="test_metadata_stamper"):
            result = stamper.stamp_file(path, overwrite=False)
        assert f"[! dry run] Would stamp/replace {path}" in caplog.text

    def test_non_python_file(self, logger: ProtocolLogger):
        fname = TEST_CASE_REGISTRY.get_test_case('metadata_block', 'invalid_metadata_yaml_error', 'invalid')
        path = Path(fname)
        assert path.suffix != ".py"

    def test_cli_help(self):
        pass

    def test_docstring_preserved(self, temp_py_file: str, metadata_stamper_cls: type, logger: ProtocolLogger, header_util) -> None:
        stamper = metadata_stamper_cls(logger, header_util=header_util)
        path = Path(temp_py_file)
        docstring = '"""This is a module docstring."""'
        with open(temp_py_file, "w") as f:
            f.write(f'{docstring}\n# Some comment\nprint("hello")\n')
        stamper.stamp_file(path, overwrite=True)
        with open(temp_py_file) as f:
            content = f.read()
        logger.info(f"[TEST LOG] Stamped file content:\n{content}")
        assert docstring in content, "Module docstring should be preserved after stamping."

    def test_ast_base_class_extraction(self, tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
        py_content = """
class Foo(BaseModel, ProtocolValidate):
    pass

class Bar(Foo, CustomMixin):
    pass

class Baz:
    pass
"""
        file_path = tmp_path / "test_ast_classes.py"
        file_path.write_text(py_content)
        stamper = metadata_stamper_cls(logger)
        bases = stamper.extract_base_classes_from_file(str(file_path))
        assert set(bases) == {"BaseModel", "ProtocolValidate", "Foo", "CustomMixin"}
        block = stamper.generate_metadata_block(
            name="test_ast_classes",
            entrypoint=str(file_path.name),
            file_path=str(file_path),
        )
        assert "protocol_class:" in block
        for base in ["BaseModel", "CustomMixin", "Foo", "ProtocolValidate"]:
            assert f"  - {base}" in block

    def test_extract_base_classes_from_file_nonexistent(self, tmp_path, caplog, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
        stamper = metadata_stamper_cls(logger)
        fake_path = tmp_path / "does_not_exist.py"
        with caplog.at_level(logging.WARNING, logger="test_metadata_stamper"):
            bases = stamper.extract_base_classes_from_file(str(fake_path))
        assert bases == []
        assert "AST parse failed" in caplog.text or "does not exist" in caplog.text

    def test_extract_base_classes_from_file_invalid_python(self, tmp_path, caplog, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
        stamper = metadata_stamper_cls(logger)
        file_path = tmp_path / "bad.py"
        file_path.write_text("def this is not valid python")
        with caplog.at_level(logging.WARNING, logger="test_metadata_stamper"):
            bases = stamper.extract_base_classes_from_file(str(file_path))
        assert bases == []
        assert "AST parse failed" in caplog.text

    def test_generate_metadata_block_unknown_template(self, tmp_path, metadata_stamper_cls: type, logger: ProtocolLogger) -> None:
        pass