import pytest
from pydantic import ValidationError

from omnibase.nodes.stamper_node.src.main import (
    StamperInputState,
    StamperOutputState,
    run_stamper_node,
)


# Canonical ONEX fixture-injected, protocol-first test (see docs/testing.md)
@pytest.fixture
def input_state():
    # In-memory, context-agnostic input (no real file path)
    return StamperInputState(file_path="mock/path.yaml", author="TestUser")


@pytest.mark.node
def test_run_stamper_node_stub(input_state):
    output = run_stamper_node(input_state)
    assert isinstance(output, StamperOutputState)
    assert output.status == "success"
    assert "mock/path.yaml" in output.message
    assert "TestUser" in output.message


# TODO: Integrate protocol registry and context-parametrized fixture per docs/testing.md

# TODO: Add more comprehensive tests after real logic is migrated
