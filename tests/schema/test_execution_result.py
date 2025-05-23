# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: test_execution_result.py
# version: 1.0.0
# uuid: a0438368-7e03-4b8b-adee-e01c81adab02
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.170814
# last_modified_at: 2025-05-21T16:42:46.088982
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d0ab9d7561f2e3bcc6ea8b7ae5946b21666d0191eb4e91c55be25a460331a4b3
# entrypoint: python@test_execution_result.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_execution_result
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Standards-Compliant Test File for ONEX/OmniBase Execution Result Schema

This file should follow the canonical test pattern as demonstrated in tests/utils/test_node_metadata_extractor.py. It should demonstrate:
- Naming conventions: test_ prefix, lowercase, descriptive
- Context-agnostic, registry-driven, fixture-injected testing
- Use of both mock (unit) and integration (real) contexts via pytest fixture parametrization
- No global state; all dependencies are injected
- Compliance with all standards in docs/standards.md and docs/testing.md

All new execution result schema tests should follow this pattern unless a justified exception is documented and reviewed.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema
import pytest
import yaml

SCHEMA_YAML_PATH = Path("src/omnibase/schemas/execution_result.yaml")
SCHEMA_JSON_PATH = Path("src/omnibase/schemas/execution_result.json")

VALID_YAML_PATH = Path("tests/schema/testdata/valid_execution_result.yaml")
VALID_JSON_PATH = Path("tests/schema/testdata/valid_execution_result.json")
INVALID_YAML_PATH = Path("tests/schema/testdata/invalid_execution_result.yaml")
INVALID_JSON_PATH = Path("tests/schema/testdata/invalid_execution_result.json")


def normalize_datetime_fields(data: Any) -> Any:
    # Recursively convert datetime objects to ISO8601 strings for known fields
    if isinstance(data, dict):
        for key, value in data.items():
            if key in {"started_at", "completed_at"} and isinstance(value, datetime):
                data[key] = value.isoformat().replace("+00:00", "Z")
            else:
                data[key] = normalize_datetime_fields(value)
    elif isinstance(data, list):
        return [normalize_datetime_fields(item) for item in data]
    return data


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
def test_valid_execution_result(
    request: pytest.FixtureRequest, data_path: Path, schema_fixture: str
) -> None:
    schema = request.getfixturevalue(schema_fixture)
    if data_path.suffix == ".yaml":
        with data_path.open("r") as f:
            data = yaml.safe_load(f)
        data = normalize_datetime_fields(data)
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
def test_invalid_execution_result(
    request: pytest.FixtureRequest, data_path: Path, schema_fixture: str
) -> None:
    schema = request.getfixturevalue(schema_fixture)
    if data_path.suffix == ".yaml":
        with data_path.open("r") as f:
            data = yaml.safe_load(f)
        data = normalize_datetime_fields(data)
    else:
        with data_path.open("r") as f:
            data = json.load(f)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=data, schema=schema)


def test_valid_execution_result_yaml(context: str) -> None:
    """Test that a valid execution result YAML file passes schema validation in both mock and integration contexts."""
    # Implementation here should use the context fixture for dependency injection or context switching.
    # ...
