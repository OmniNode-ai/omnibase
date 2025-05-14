# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "test_validate_dockerfile_validator"
# namespace: "omninode.tools.test_validate_dockerfile_validator"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T13:00:16+00:00"
# last_modified_at: "2025-05-05T13:00:16+00:00"
# entrypoint: "test_validate_dockerfile_validator.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import pytest
from foundation.protocol.test_helper import ITestHelper
from foundation.script.validation.validate_dockerfile import DockerfileValidator
from foundation.script.validation.validator_registry import get_fixture_by_interface


@pytest.fixture
def valid_dockerfile(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text(
        """
# Stage 1: builder
FROM python:3.11.8 AS builder
LABEL maintainer="example@domain.com"
LABEL version="1.0"
LABEL description="Test Dockerfile"
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/app" \
    VENV_PATH="/app/venv"
WORKDIR /app
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="$POETRY_HOME/bin:$PATH"
# Copy dependency files and install dependencies
COPY pyproject.toml poetry.lock /app/
RUN $POETRY_HOME/bin/poetry install --no-interaction --no-ansi
# Copy source code
COPY src/ /app/src/

# Stage 2: final image
FROM python:3.11.8 AS final
LABEL maintainer="example@domain.com"
LABEL version="1.0"
LABEL description="Test Dockerfile"
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/app" \
    VENV_PATH="/app/venv"
WORKDIR /app
COPY --from=builder /app /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:8080/ || exit 1
USER nobody
COPY --chown=nobody:nogroup src/ /app/src/
CMD ["python3", "-m", "http.server", "8080"]
"""
    )
    # Also create required files and dirs for COPY
    (tmp_path / "pyproject.toml").write_text(
        "[tool.poetry]\nname = 'test'\nversion = '0.1.0'\n"
    )
    (tmp_path / "poetry.lock").write_text("")
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "main.py").write_text("print('hello world')\n")
    return dockerfile


@pytest.fixture
def invalid_dockerfile(tmp_path):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text(
        """
FROM ubuntu:latest
LABEL maintainer="example@domain.com"
"""
    )
    return dockerfile


@pytest.fixture
def missing_dockerfile(tmp_path):
    # Return a path that does not exist
    return tmp_path / "Dockerfile"


def test_valid_dockerfile(valid_dockerfile):
    validator = DockerfileValidator()
    result = validator.validate(valid_dockerfile)
    assert result.is_valid
    assert not result.errors


def test_invalid_dockerfile(invalid_dockerfile):
    helper = get_fixture_by_interface(ITestHelper)()
    validator = DockerfileValidator()
    result = validator.validate(invalid_dockerfile)
    assert not result.is_valid
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(
        result.errors, "Base image must be", str(invalid_dockerfile)
    )


def test_missing_dockerfile(missing_dockerfile):
    helper = get_fixture_by_interface(ITestHelper)()
    validator = DockerfileValidator()
    result = validator.validate(missing_dockerfile)
    assert not result.is_valid
    for err in result.errors:
        helper.assert_issue_fields(err)
    helper.assert_has_error(result.errors, "not found", str(missing_dockerfile))