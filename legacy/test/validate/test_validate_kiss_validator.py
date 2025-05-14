# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_kiss_validator"
# namespace: "omninode.tools.test_validate_kiss_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:15+00:00"
# last_modified_at: "2025-05-05T13:00:15+00:00"
# entrypoint: "test_validate_kiss_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import textwrap
from pathlib import Path

import pytest
from foundation.protocol.protocol_validate_fixture import ProtocolValidateFixture
from foundation.fixture.fixture_helper import TestHelper
from foundation.script.validate.validate_registry import get_fixture_by_interface


@pytest.fixture
def temp_py_dir():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls.get_fixture()


@pytest.fixture
def kiss_validator():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    return fixture_cls().get_fixture()


@pytest.fixture
def kiss_validator_factory():
    fixture_cls = get_fixture_by_interface(ProtocolValidateFixture)
    from containers.foundation.test.fixture.test_fixture_helper import TestHelper
    return TestHelper().get_fixture()


def write_py(path: Path, source: str):
    path.write_text(textwrap.dedent(source))


# Valid: simple function
def test_kiss_validator_valid(temp_py_dir, kiss_validator):
    helper = get_fixture_by_interface(TestHelper)()
    f = temp_py_dir / "simple.py"
    write_py(
        f,
        """
    def add(a, b):
        return a + b
    """,
    )
    result = kiss_validator.validate(temp_py_dir)
    assert result.is_valid
    assert not result.errors


# Invalid: function with high complexity, nesting, and too many params
@pytest.mark.parametrize(
    "source,expected",
    [
        (
            """
    def bad(a, b, c, d, e, f):
        if a:
            for i in range(2):
                if b:
                    while c:
                        pass
        if d:
            pass
    """,
            ["cyclomatic complexity", "nesting depth", "parameters"],
        ),
    ],
)
def test_kiss_validator_invalid(temp_py_dir, kiss_validator_factory, source, expected):
    helper = get_fixture_by_interface(TestHelper)()
    f = temp_py_dir / "bad.py"
    write_py(f, source)
    validator = kiss_validator_factory(
        {"max_cyclomatic_complexity": 2, "max_nesting_depth": 1, "max_params": 2}
    )
    result = validator.validate(temp_py_dir)
    assert not result.is_valid
    for exp in expected:
        helper.assert_has_error(result.errors, exp, str(f))
    for err in result.errors:
        helper.assert_issue_fields(err)


# Edge: syntax error file


def test_kiss_validator_syntax_error(temp_py_dir, kiss_validator):
    helper = get_fixture_by_interface(TestHelper)()
    f = temp_py_dir / "broken.py"
    f.write_text("def foo(:\n    pass")
    result = kiss_validator.validate(temp_py_dir)
    assert result.is_valid  # Should not fail overall
    for warn in result.warnings:
        helper.assert_issue_fields(warn)
    helper.assert_has_error(result.warnings, "Could not parse", str(f))