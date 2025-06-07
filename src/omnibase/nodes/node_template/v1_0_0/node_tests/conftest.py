import pytest
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    node_metadata,
    scenario_test_entrypoint,
    scenario_dir,
    scenario_files,
    make_node_class_fixture,
    input_validation_tool,
    scenario_test_harness,
    tool_bootstrap_fixture,
    tool_health_check_fixture,
    output_field_tool,
    event_bus_config,
)
from omnibase.protocol.protocol_tool_backend_selection import ToolBackendSelectionProtocol
from omnibase.nodes.node_template.v1_0_0.models.state import NodeTemplateInputState, NodeTemplateOutputState, ModelTemplateOutputField
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.testing.testing_scenario_harness import make_testing_scenario_harness
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync

# Register the node_class fixture for this module
node_class = make_node_class_fixture("NodeTemplate")

def pytest_addoption(parser):
    parser.addoption(
        "--regenerate-snapshots",
        action="store_true",
        default=False,
        help="Regenerate scenario output snapshots."
    )

class StubBackendSelection(ToolBackendSelectionProtocol):
    """
    Canonical example stub for ToolBackendSelectionProtocol.
    This is only required to satisfy the shared test harness for the node_template.
    Most nodes do NOT need a backend selection tool—only nodes with real backend logic (e.g., Kafka) should implement/inject a real backend selection tool.
    See ONEX node migration checklist and standards for details.
    """
    def select_event_bus(self, config=None, logger=None):
        # Always returns an in-memory event bus for testing/example purposes.
        from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
        return InMemoryEventBus()

@pytest.fixture(scope="module")
def tool_backend_selection():
    """
    Provides a stub backend selection tool for the node_template.
    Real nodes with backend logic should inject a real ToolBackendSelection.
    """
    return StubBackendSelection()

def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[node_template.conftest] {msg}", context=context or {})

@pytest.fixture(scope="module")
def input_validation_tool():
    debug_log("Creating input_validation_tool fixture for node_template")
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