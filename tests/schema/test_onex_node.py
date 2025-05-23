# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: test_onex_node.py
# version: 1.0.0
# uuid: dcf29549-fcb8-4abd-9bba-43cc6733a88c
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.170874
# last_modified_at: 2025-05-21T16:42:46.063653
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 75721d9ab26ed172939cfd683893d3dceba9e788d8f96b4e9b3dc98da5d490f1
# entrypoint: python@test_onex_node.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_onex_node
# meta_type: tool
# === /OmniNode:Metadata ===


# mypy: ignore-errors
# NOTE: File-level mypy suppression is required due to a persistent list comprehension typing issue with pytest parameterization (see omnibase_mypy_debug_log.md for details).
import json
from pathlib import Path
from typing import Any, List

import pytest
import yaml
from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate as jsonschema_validate

# Paths
SCHEMA_JSON_PATH = (
    Path(__file__).parent.parent.parent / "src/omnibase/schemas/onex_node.json"
)
SCHEMA_YAML_PATH = (
    Path(__file__).parent.parent.parent / "src/omnibase/schemas/onex_node.yaml"
)
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "src/omnibase/templates"
TESTDATA_DIR = Path(__file__).parent / "testdata"

# Registry for all test cases
ONEX_NODE_TEST_CASES = []


def register_onex_node_test_case(
    case_id: str, case_type: str, data_path: Path, expect_valid: bool
) -> None:
    ONEX_NODE_TEST_CASES.append(
        {
            "id": case_id,
            "type": case_type,
            "data_path": data_path,
            "expect_valid": expect_valid,
        }
    )


# Register testdata files
register_onex_node_test_case(
    "valid_onex_node_json", "testdata", TESTDATA_DIR / "valid_onex_node.json", True
)
register_onex_node_test_case(
    "valid_onex_node_yaml", "testdata", TESTDATA_DIR / "valid_onex_node.yaml", True
)
register_onex_node_test_case(
    "invalid_onex_node_json", "testdata", TESTDATA_DIR / "invalid_onex_node.json", False
)
register_onex_node_test_case(
    "invalid_onex_node_yaml", "testdata", TESTDATA_DIR / "invalid_onex_node.yaml", False
)


# Register schema examples
# (Do not register schema examples with data_path=None)
def extract_schema_examples(schema_path: Path) -> list[Any]:
    with open(schema_path, "r") as f:
        schema = json.load(f)
    examples = schema.get("examples", [])
    return list(examples)


SCHEMA_EXAMPLES = extract_schema_examples(SCHEMA_JSON_PATH)


@pytest.fixture(scope="module")
def onex_node_schema_json() -> Any:
    with open(SCHEMA_JSON_PATH, "r") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def onex_node_schema_yaml() -> Any:
    with open(SCHEMA_YAML_PATH, "r") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "case",
    [c for c in ONEX_NODE_TEST_CASES if c["data_path"] is not None],
    ids=[c["id"] for c in ONEX_NODE_TEST_CASES if c["data_path"] is not None],
)
def test_onex_node_testdata_validation(
    case: dict[str, Any], onex_node_schema_json: dict[str, Any]
) -> None:
    """
    Validate ONEX node testdata files (JSON/YAML) against the canonical schema.
    """
    data_path = case["data_path"]
    expect_valid = case["expect_valid"]
    if data_path.suffix == ".json":
        with open(data_path, "r") as f:
            data = json.load(f)
    elif data_path.suffix in (".yaml", ".yml"):
        with open(data_path, "r") as f:
            data = yaml.safe_load(f)
    else:
        pytest.skip(f"Unsupported file type: {data_path}")
    if expect_valid:
        jsonschema_validate(instance=data, schema=onex_node_schema_json)
    else:
        with pytest.raises(JsonSchemaValidationError):
            jsonschema_validate(instance=data, schema=onex_node_schema_json)


def schema_example_ids(n: int) -> List[str]:
    """
    Generate pytest parametrize ids for schema example tests as a list of str.
    This avoids mypy list comprehension inference issues.
    """
    return [f"schema_example_{i}" for i in range(n)]


ids_for_schema_examples: List[str] = [
    f"schema_example_{i}" for i in range(len(SCHEMA_EXAMPLES))
]


@pytest.mark.parametrize(
    "idx,example",
    list(enumerate(SCHEMA_EXAMPLES)),
    ids=ids_for_schema_examples,
)
def test_onex_node_schema_examples(
    idx: int, example: Any, onex_node_schema_json: Any
) -> None:
    """
    Validate each canonical example embedded in the ONEX node JSON schema.
    """
    jsonschema_validate(instance=example, schema=onex_node_schema_json)


# TODO: Implement tests for schema examples, template rendering, CLI validator, and drift-proofing
