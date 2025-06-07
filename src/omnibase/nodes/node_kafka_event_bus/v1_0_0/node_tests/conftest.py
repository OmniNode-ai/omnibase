import pytest
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    tool_bootstrap_fixture,
    tool_health_check_fixture,
    output_field_tool,
)
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_backend_selection import ToolBackendSelection
from omnibase.constants import CONTRACT_FILENAME
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.testing.testing_scenario_harness import make_testing_scenario_harness
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.state import NodeKafkaEventBusNodeInputState, NodeKafkaEventBusNodeOutputState
from omnibase.model.model_event_bus_output_field import ModelEventBusOutputField
from omnibase.nodes.node_kafka_event_bus.constants import NODE_KAFKA_EVENT_BUS_ID
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync

def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[node_kafka_event_bus.conftest] {msg}", context=context or {})

@pytest.fixture(scope="module")
def input_validation_tool():
    debug_log("Creating input_validation_tool fixture for node_kafka_event_bus")
    return ToolInputValidation(
        input_model=NodeKafkaEventBusNodeInputState,
        output_model=NodeKafkaEventBusNodeOutputState,
        output_field_model=ModelEventBusOutputField,
        node_id=NODE_KAFKA_EVENT_BUS_ID,
    )

@pytest.fixture(scope="module")
def scenario_test_harness():
    debug_log("Creating scenario_test_harness fixture for node_kafka_event_bus")
    return make_testing_scenario_harness(NodeKafkaEventBusNodeOutputState)

@pytest.fixture(scope="module")
def tool_backend_selection(node_dir):
    return ToolBackendSelection()

def pytest_addoption(parser):
    parser.addoption(
        "--regenerate-snapshots",
        action="store_true",
        default=False,
        help="Regenerate scenario output snapshots."
    ) 