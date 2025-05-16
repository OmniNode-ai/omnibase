import pytest
import yaml
import json
import jsonschema
from pathlib import Path
from datetime import datetime

SCHEMA_YAML_PATH = Path("src/omnibase/schemas/execution_result.yaml")
SCHEMA_JSON_PATH = Path("src/omnibase/schemas/execution_result.json")

VALID_YAML_PATH = Path("tests/schema/testdata/valid_execution_result.yaml")
VALID_JSON_PATH = Path("tests/schema/testdata/valid_execution_result.json")
INVALID_YAML_PATH = Path("tests/schema/testdata/invalid_execution_result.yaml")
INVALID_JSON_PATH = Path("tests/schema/testdata/invalid_execution_result.json")

def normalize_datetime_fields(data):
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
def schema_yaml():
    with SCHEMA_YAML_PATH.open("r") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="module")
def schema_json():
    with SCHEMA_JSON_PATH.open("r") as f:
        return json.load(f)

@pytest.mark.parametrize("data_path,schema_fixture", [
    (VALID_YAML_PATH, "schema_yaml"),
    (VALID_JSON_PATH, "schema_json"),
], ids=["yaml", "json"])
def test_valid_execution_result(request, data_path, schema_fixture):
    schema = request.getfixturevalue(schema_fixture)
    if data_path.suffix == ".yaml":
        with data_path.open("r") as f:
            data = yaml.safe_load(f)
        data = normalize_datetime_fields(data)
    else:
        with data_path.open("r") as f:
            data = json.load(f)
    jsonschema.validate(instance=data, schema=schema)

@pytest.mark.parametrize("data_path,schema_fixture", [
    (INVALID_YAML_PATH, "schema_yaml"),
    (INVALID_JSON_PATH, "schema_json"),
], ids=["yaml", "json"])
def test_invalid_execution_result(request, data_path, schema_fixture):
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