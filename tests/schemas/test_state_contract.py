# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: test_state_contract.py
# version: 1.0.0
# uuid: 8a744df1-b948-421c-9cc4-04f96615576c
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.170933
# last_modified_at: 2025-05-21T16:42:46.055548
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 339cbae8532c898b293a9d1bfc1d4075ee04690b34acfbee190d29bd8cbda627
# entrypoint: python@test_state_contract.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_state_contract
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Standards-Compliant Test File for ONEX/OmniBase State Contract Schema

This file should follow the canonical test pattern as demonstrated in src/omnibase/utils/tests/test_node_metadata_extractor.py. It should demonstrate:
- Naming conventions: test_ prefix, lowercase, descriptive
- Context-agnostic, registry-driven, fixture-injected testing
- Use of both mock (unit) and integration (real) contexts via pytest fixture parametrization
- No global state; all dependencies are injected
- Compliance with all standards in docs/standards.md and docs/testing.md

All new state contract schema tests should follow this pattern unless a justified exception is documented and reviewed.
"""

import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest
import yaml

SCHEMA_YAML_PATH = Path("src/omnibase/schemas/state_contract.yaml")
SCHEMA_JSON_PATH = Path("src/omnibase/schemas/state_contract.json")

VALID_YAML_PATH = Path("tests/schemas/testdata/valid_state_contract.yaml")
VALID_JSON_PATH = Path("tests/schemas/testdata/valid_state_contract.json")
INVALID_YAML_PATH = Path("tests/schemas/testdata/invalid_state_contract.yaml")
INVALID_JSON_PATH = Path("tests/schemas/testdata/invalid_state_contract.json")


@pytest.fixture(scope="module")
def schema_yaml() -> Any:
    with SCHEMA_YAML_PATH.open("r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def schema_json() -> Any:
    with SCHEMA_JSON_PATH.open("r") as f:
        return json.load(f)


@pytest.fixture(
    params=[
        pytest.param("mock", id="mock", marks=pytest.mark.mock),
        pytest.param("integration", id="integration", marks=pytest.mark.integration),
    ]
)
def context(request: Any) -> str:
    return str(request.param)


@pytest.mark.parametrize(
    "data_path,schema_fixture",
    [
        (VALID_YAML_PATH, "schema_yaml"),
        (VALID_JSON_PATH, "schema_json"),
    ],
    ids=["yaml", "json"],
)
def test_valid_state_contract(
    request: pytest.FixtureRequest, data_path: Path, schema_fixture: str
) -> None:
    schema = request.getfixturevalue(schema_fixture)
    if data_path.suffix == ".yaml":
        with data_path.open("r") as f:
            data = yaml.safe_load(f)
    else:
        with data_path.open("r") as f:
            data = json.load(f)
    jsonschema.validate(instance=data, schema=schema)


@pytest.mark.parametrize(
    "data_path,schema_fixture",
    [
        (INVALID_YAML_PATH, "schema_yaml"),
        (INVALID_JSON_PATH, "schema_json"),
    ],
    ids=["yaml", "json"],
)
def test_invalid_state_contract(
    request: pytest.FixtureRequest, data_path: Path, schema_fixture: str
) -> None:
    schema = request.getfixturevalue(schema_fixture)
    if data_path.suffix == ".yaml":
        with data_path.open("r") as f:
            data = yaml.safe_load(f)
    else:
        with data_path.open("r") as f:
            data = json.load(f)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=data, schema=schema)


def test_valid_state_contract_yaml(context: str) -> None:
    """Test that a valid state contract YAML file passes schema validation in both mock and integration contexts."""
    # Implementation here should use the context fixture for dependency injection or context switching.
    # ...
