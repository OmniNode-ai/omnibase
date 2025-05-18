"""
Canonical Test Example for ONEX/OmniBase

This file is the canonical reference for all test contributors. It demonstrates:
- Naming conventions: test_ prefix, lowercase, descriptive
- Context-agnostic, registry-driven, fixture-injected testing
- Use of both mock (unit) and integration (real) contexts via pytest fixture parametrization
- No global state; all dependencies are injected
- Registry-driven test case execution pattern
- Compliance with all standards in docs/standards.md and docs/testing.md

All new tests should follow this pattern unless a justified exception is documented and reviewed.
"""

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.utils.utils_node_metadata_extractor import (
    load_node_metadata_from_dict,
    load_node_metadata_from_json,
    load_node_metadata_from_yaml,
)
from tests.utils.utils_test_node_metadata_extractor_cases import (
    UTILS_NODE_METADATA_EXTRACTOR_CASES,
)


@pytest.fixture
def minimal_node_metadata_dict() -> dict[str, Any]:
    """Fixture providing a minimal valid node metadata dict."""
    return {
        "schema_version": "1.0.0",
        "name": "test_node",
        "version": "1.0.0",
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "metadata_version": "1.0.0",
        "protocol_version": "1.0.0",
        "owner": "test_owner",
        "copyright": "test_copyright",
        "author": "test_author",
        "created_at": "2024-01-01T00:00:00Z",
        "last_modified_at": "2024-01-02T00:00:00Z",
        "description": "A test node for extractor tests.",
        "state_contract": "onex.contracts.state.v1",
        "lifecycle": "active",
        "hash": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "entrypoint": {"type": "python", "target": "main.py"},
        "namespace": "onex.test_node",
        "meta_type": "plugin",
        "tags": ["test", "extractor"],
        "trust_score_stub": {"runs": 1, "failures": 0},
        "x_extensions": {},
        "protocols_supported": ["v1"],
        "base_class": [],
        "dependencies": [],
        "environment": [],
        "license": "MIT",
    }


def test_load_node_metadata_from_dict_success(
    minimal_node_metadata_dict: dict[str, Any]
) -> None:
    """Test loading node metadata from a valid dict."""
    result = load_node_metadata_from_dict(minimal_node_metadata_dict)
    assert isinstance(result, NodeMetadataBlock)
    assert result.name == "test_node"


def test_load_node_metadata_from_dict_invalid() -> None:
    """Test loading node metadata from an invalid dict raises an exception."""
    with pytest.raises(Exception):
        load_node_metadata_from_dict({"not_a_field": 123})


def test_load_node_metadata_from_yaml_success(
    minimal_node_metadata_dict: dict[str, Any]
) -> None:
    """Test loading node metadata from a valid YAML file."""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        yaml.dump(minimal_node_metadata_dict, f)
        fpath = Path(f.name)
    try:
        result = load_node_metadata_from_yaml(fpath)
        assert isinstance(result, NodeMetadataBlock)
        assert result.name == "test_node"
    finally:
        fpath.unlink()


def test_load_node_metadata_from_json_success(
    minimal_node_metadata_dict: dict[str, Any]
) -> None:
    """Test loading node metadata from a valid JSON file."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(minimal_node_metadata_dict, f)
        fpath = Path(f.name)
    try:
        result = load_node_metadata_from_json(fpath)
        assert isinstance(result, NodeMetadataBlock)
        assert result.name == "test_node"
    finally:
        fpath.unlink()


def test_load_node_metadata_from_yaml_invalid() -> None:
    """Test loading node metadata from an invalid YAML file raises an exception."""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(": not valid yaml :::\n")
        fpath = Path(f.name)
    try:
        with pytest.raises(Exception):
            load_node_metadata_from_yaml(fpath)
    finally:
        fpath.unlink()


def test_load_node_metadata_from_json_invalid() -> None:
    """Test loading node metadata from an invalid JSON file raises an exception."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write("not valid json")
        fpath = Path(f.name)
    try:
        with pytest.raises(Exception):
            load_node_metadata_from_json(fpath)
    finally:
        fpath.unlink()


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock", marks=pytest.mark.mock),
        pytest.param("integration", id="integration", marks=pytest.mark.integration),
    ]
)
def context(request: pytest.FixtureRequest) -> Any:  # type: ignore[no-any-return]
    # Return type is Any due to pytest param mechanics; see ONEX test standards
    return request.param


@pytest.mark.parametrize(
    "context", ["mock", "integration"], ids=["mock", "integration"]
)
@pytest.mark.parametrize(
    "test_case",
    list(UTILS_NODE_METADATA_EXTRACTOR_CASES.values()),
    ids=list(UTILS_NODE_METADATA_EXTRACTOR_CASES.keys()),
)
def test_utils_node_metadata_extractor_cases(test_case: type, context: str) -> None:
    test_case().run(context)
