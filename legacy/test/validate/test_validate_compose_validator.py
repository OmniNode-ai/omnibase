# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_compose_validator"
# namespace: "omninode.tools.test_validate_compose_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:16+00:00"
# last_modified_at: "2025-05-05T13:00:16+00:00"
# entrypoint: "test_validate_compose_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

from pathlib import Path

import pytest
from foundation.protocol.test_helper import ITestHelper
from foundation.script.validation.validate_compose import ComposeValidator
from foundation.script.validation.validator_registry import get_fixture_by_interface

VALID_PATH = (
    Path(__file__).parent / "test_cases" / "compose" / "valid" / "docker-compose.yml"
)
INVALID_PATH = (
    Path(__file__).parent / "test_cases" / "compose" / "invalid" / "docker-compose.yml"
)


@pytest.fixture
def validator():
    return ComposeValidator()


def test_valid_compose(validator):
    result = validator.validate(VALID_PATH)
    assert result.is_valid
    assert not result.errors
    # Warnings may exist, but should not block validity


def test_invalid_compose(validator):
    result = validator.validate(INVALID_PATH)
    assert not result.is_valid
    helper = get_fixture_by_interface(ITestHelper)()
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(result.errors, "missing", str(INVALID_PATH))


def test_warning_compose(tmp_path, validator):
    # Compose file with best-practice warnings
    compose_content = """
---
services:
  app:
    image: test:latest
    privileged: true
    restart: "no"
    environment:
      - PYTHONPATH=/app/src
      - ENV=production
    volumes:
      - /host/path:/app
    networks:
      - platform-net
      - net2
    build:
      context: /abs/path
      dockerfile: Dockerfile
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
networks:
  platform-net:
  net2:
"""
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text(compose_content)
    result = validator.validate(compose_file)
    assert result.is_valid  # Only warnings, not errors
    assert not result.errors
    helper = get_fixture_by_interface(ITestHelper)()
    for warn in result.warnings:
        helper.assert_issue_fields(warn)
    helper.assert_has_warning(result.warnings, "privileged: true", str(compose_file))
    helper.assert_has_warning(result.warnings, "restart", str(compose_file))
    helper.assert_has_warning(
        result.warnings, "build.context is not relative", str(compose_file)
    )