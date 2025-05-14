# === OmniNode:Test_Metadata ===
# metadata_version: "0.1"
# name: "test_model_validate_error"
# namespace: "omninode.tests.model_validate_error"
# meta_type: "test"
# version: "0.1.0"
# owner: "foundation-team"
# === /OmniNode:Test_Metadata ===

import os
import pytest
import yaml
from foundation.test.test_case_registry import TEST_CASE_REGISTRY
from foundation.model.model_validate_error import (
    ValidateMessageModel,
    ValidateResultModel,
    ValidateError,
    insert_template_marker,
)
import json

# --- ValidateMessageModel Tests ---

def test_validate_message_model_valid():
    fname = TEST_CASE_REGISTRY.get_test_case("model_validate_error", "valid_message_model", "valid")
    with open(fname) as f:
        data = yaml.safe_load(f)
    msg = ValidateMessageModel(**data)
    assert msg.message == "Test message"
    assert msg.file == "test.py"
    assert msg.line == 42
    assert msg.severity == "warning"
    assert msg.code == "TEST001"
    assert msg.context == {"key": "value"}
    assert isinstance(msg.uid, str)
    assert isinstance(msg.timestamp, str)
    assert msg.hash is None

def test_validate_message_model_invalid():
    fname = TEST_CASE_REGISTRY.get_test_case("model_validate_error", "invalid_message_model", "invalid")
    with open(fname) as f:
        data = yaml.safe_load(f)
    with pytest.raises(ValueError):
        ValidateMessageModel(**data)

def test_validate_message_model_compute_hash():
    msg = ValidateMessageModel(
        message="test message",
        file="test.py",
        code="TEST001",
        severity="error",
        context={"key": "value"},
    )
    hash1 = msg.compute_hash()
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA-256 hash length
    
    # Same content should produce same hash
    msg2 = ValidateMessageModel(
        message="test message",
        file="test.py",
        code="TEST001",
        severity="error",
        context={"key": "value"},
    )
    assert msg2.compute_hash() == hash1
    
    # Different content should produce different hash
    msg3 = ValidateMessageModel(
        message="different message",
        file="test.py",
        code="TEST001",
        severity="error",
        context={"key": "value"},
    )
    assert msg3.compute_hash() != hash1

def test_validate_message_model_with_hash():
    msg = ValidateMessageModel(message="test message")
    assert msg.hash is None
    msg_with_hash = msg.with_hash()
    assert msg_with_hash.hash is not None
    assert msg_with_hash.hash == msg.compute_hash()
    assert msg_with_hash is msg  # Should return self

def test_validate_message_model_to_json():
    msg = ValidateMessageModel(
        message="test message",
        file="test.py",
        line=42,
        severity="warning",
        code="TEST001",
        context={"key": "value"},
    )
    json_str = msg.model_dump_json()  # Using model_dump_json instead of deprecated json()
    assert isinstance(json_str, str)
    # Verify JSON can be parsed and contains all fields
    data = json.loads(json_str)
    assert data["message"] == "test message"
    assert data["file"] == "test.py"
    assert data["line"] == 42
    assert data["severity"] == "warning"
    assert data["code"] == "TEST001"
    assert data["context"] == {"key": "value"}
    assert "uid" in data
    assert "timestamp" in data

def test_validate_message_model_to_text():
    msg = ValidateMessageModel(
        message="test message",
        file="test.py",
        line=42,
        severity="warning",
        code="TEST001",
        context={"key": "value"},
    )
    text = msg.to_text()
    assert isinstance(text, str)
    assert "[WARNING] test message" in text
    assert "File: test.py" in text
    assert "Line: 42" in text
    assert "Code: TEST001" in text
    assert "Context: {'key': 'value'}" in text
    assert "UID:" in text
    assert "Hash:" in text
    assert "Timestamp:" in text

def test_validate_message_model_to_ci():
    msg = ValidateMessageModel(
        message="test message",
        file="test.py",
        line=42,
        severity="warning",
    )
    ci_text = msg.to_ci()
    assert isinstance(ci_text, str)
    assert "::warning file=test.py,line=42::test message" == ci_text

def test_validate_message_model_to_ci_no_location():
    msg = ValidateMessageModel(
        message="test message",
        severity="warning",
    )
    ci_text = msg.to_ci()
    assert isinstance(ci_text, str)
    assert "::warning ::test message" == ci_text

# --- ValidateResultModel Tests ---

def test_validate_result_model_valid():
    fname = TEST_CASE_REGISTRY.get_test_case("model_validate_error", "valid_result_model", "valid")
    with open(fname) as f:
        data = yaml.safe_load(f)
    result = ValidateResultModel(**data)
    assert len(result.messages) == 2
    assert result.messages[0].message == "Test message 1"
    assert result.messages[0].file == "test1.py"
    assert result.messages[0].line == 42
    assert result.messages[0].severity == "error"
    assert result.messages[1].message == "Test message 2"
    assert result.messages[1].file == "test2.py"
    assert result.messages[1].line == 43
    assert result.messages[1].severity == "warning"
    assert result.status == ValidateStatus.VALID
    assert result.summary == "All good"
    assert isinstance(result.uid, str)
    assert isinstance(result.timestamp, str)
    assert result.hash is None

def test_validate_result_model_invalid():
    fname = TEST_CASE_REGISTRY.get_test_case("model_validate_error", "invalid_result_model", "invalid")
    with open(fname) as f:
        data = yaml.safe_load(f)
    with pytest.raises(ValueError):
        ValidateResultModel(**data)

def test_validate_result_model_compute_hash():
    msg1 = ValidateMessageModel(message="test message 1")
    msg2 = ValidateMessageModel(message="test message 2")
    result = ValidateResultModel(
        messages=[msg1, msg2],
        status=ValidateStatus.VALID,
        summary="All good",
    )
    hash1 = result.compute_hash()
    assert isinstance(hash1, str)
    assert len(hash1) == 64  # SHA-256 hash length
    
    # Same content should produce same hash
    result2 = ValidateResultModel(
        messages=[msg1, msg2],
        status=ValidateStatus.VALID,
        summary="All good",
    )
    assert result2.compute_hash() == hash1
    
    # Different content should produce different hash
    result3 = ValidateResultModel(
        messages=[msg1],
        status=ValidateStatus.VALID,
        summary="All good",
    )
    assert result3.compute_hash() != hash1

def test_validate_result_model_with_hash():
    result = ValidateResultModel(messages=[])
    assert result.hash is None
    result_with_hash = result.with_hash()
    assert result_with_hash.hash is not None
    assert result_with_hash.hash == result.compute_hash()
    assert result_with_hash is result  # Should return self

def test_validate_result_model_to_json():
    msg = ValidateMessageModel(message="test message")
    result = ValidateResultModel(
        messages=[msg],
        status=ValidateStatus.VALID,
        summary="All good",
    )
    json_str = result.model_dump_json()  # Using model_dump_json instead of deprecated json()
    assert isinstance(json_str, str)
    # Verify JSON can be parsed and contains all fields
    data = json.loads(json_str)
    assert len(data["messages"]) == 1
    assert data["status"] == "valid"
    assert data["summary"] == "All good"
    assert "uid" in data
    assert "timestamp" in data

def test_validate_result_model_to_text():
    msg = ValidateMessageModel(message="test message")
    result = ValidateResultModel(
        messages=[msg],
        status=ValidateStatus.VALID,
        summary="All good",
    )
    text = result.to_text()
    assert isinstance(text, str)
    assert "Status: valid" in text
    assert "Summary: All good" in text
    assert "UID:" in text
    assert "Hash:" in text
    assert "Timestamp:" in text
    assert "[ERROR] test message" in text

def test_validate_result_model_to_ci():
    msg1 = ValidateMessageModel(
        message="test message 1",
        file="test1.py",
        line=42,
        severity="error",
    )
    msg2 = ValidateMessageModel(
        message="test message 2",
        file="test2.py",
        line=43,
        severity="warning",
    )
    result = ValidateResultModel(messages=[msg1, msg2])
    ci_text = result.to_ci()
    assert isinstance(ci_text, str)
    assert "::error file=test1.py,line=42::test message 1" in ci_text
    assert "::warning file=test2.py,line=43::test message 2" in ci_text

# --- Template Marker Tests ---

def test_insert_template_marker_empty():
    result = insert_template_marker("")
    assert result == "# TEMPLATE: validator.v0.1\n"

def test_insert_template_marker_no_marker():
    result = insert_template_marker("some content")
    assert result == "# TEMPLATE: validator.v0.1\nsome content"

def test_insert_template_marker_has_marker():
    content = "# TEMPLATE: validator.v0.1\nsome content"
    result = insert_template_marker(content)
    assert result == content

def test_insert_template_marker_custom_marker():
    result = insert_template_marker("content", marker="# CUSTOM: marker")
    assert result == "# CUSTOM: marker\ncontent"

# --- ValidateError Tests ---

def test_validate_error():
    error = ValidateError("test error")
    assert str(error) == "test error" 