import pytest
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    make_node_class_fixture,
    tool_bootstrap_fixture,
    tool_health_check_fixture,
    output_field_tool,
)
from omnibase.nodes.node_template.v1_0_0.models.state import NodeTemplateInputState, NodeTemplateOutputState, ModelTemplateOutputField
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.testing.testing_scenario_harness import make_testing_scenario_harness
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync
from omnibase.nodes.node_template.v1_0_0.tools.tool_backend_selection import stub_backend_selection

# Register the node_class fixture for this module
node_class = make_node_class_fixture("NodeTemplate")

def pytest_addoption(parser):
    parser.addoption(
        "--regenerate-snapshots",
        action="store_true",
        default=False,
        help="Regenerate scenario output snapshots."
    )

@pytest.fixture(scope="module")
def tool_backend_selection():
    """
    Provides a stub backend selection tool for the node_template.
    Real nodes with backend logic should inject a real ToolBackendSelection.
    """
    return stub_backend_selection

def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[node_template.conftest] {msg}", context=context or {})

@pytest.fixture(scope="module")
def input_validation_tool():
    debug_log("Creating input_validation_tool fixture for node_template")
    # For full parity with the Kafka node, replace 'node_template' with a NODE_TEMPLATE_ID constant if/when constants.py is reintroduced.
    return ToolInputValidation(
        input_model=NodeTemplateInputState,
        output_model=NodeTemplateOutputState,
        output_field_model=ModelTemplateOutputField,
        node_id="node_template",
    )

@pytest.fixture(scope="module")
def scenario_test_harness():
    debug_log("Creating scenario_test_harness fixture for node_template")
    return make_testing_scenario_harness(NodeTemplateOutputState) 