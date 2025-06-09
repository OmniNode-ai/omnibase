import pytest
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    make_node_class_fixture,
    tool_bootstrap_fixture,
    tool_health_check_fixture,
    output_field_tool,
)
from omnibase.nodes.node_model_generator.v1_0_0.models.model_generator_state import NodeModelGeneratorInputState, NodeModelGeneratorOutputState, ModelGeneratorOutputField
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.testing.testing_scenario_harness import make_testing_scenario_harness
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync
from omnibase.nodes.node_model_generator.v1_0_0.registry.registry_model_generator import RegistryModelGeneratorNode
from omnibase.nodes.node_model_generator.v1_0_0.tools.tool_backend_selection import StubBackendSelection
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.constants import BACKEND_SELECTION_KEY, INPUT_VALIDATION_KEY, OUTPUT_FIELD_KEY, BOOTSTRAP_KEY, HEALTH_CHECK_KEY, INMEMORY_KEY
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_registry_resolver import registry_resolver_tool

@pytest.fixture(scope="module")
def node_class():
    # Resolve the node class via the registry abstraction
    return RegistryModelGeneratorNode.get_node_class()

def pytest_addoption(parser):
    parser.addoption(
        "--regenerate-snapshots",
        action="store_true",
        default=False,
        help="Regenerate scenario output snapshots."
    )

@pytest.fixture(scope="module")
def tool_backend_selection():
    registry_model_generator_node = RegistryModelGeneratorNode()
    registry_model_generator_node.register_tool(INMEMORY_KEY, InMemoryEventBus)
    return StubBackendSelection(registry_model_generator_node)

def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[node_model_generator.conftest] {msg}", context=context or {})

@pytest.fixture(scope="module")
def input_validation_tool():
    debug_log("Creating input_validation_tool fixture for node_model_generator")
    # For full parity with the Kafka node, replace 'node_model_generator' with a NODE_MODEL_GENERATOR_ID constant if/when constants.py is reintroduced.
    return ToolInputValidation(
        input_model=NodeModelGeneratorInputState,
        output_model=NodeModelGeneratorOutputState,
        output_field_model=ModelGeneratorOutputField,
        node_id="node_model_generator",
    )

@pytest.fixture(scope="module")
def scenario_test_harness():
    debug_log("Creating scenario_test_harness fixture for node_model_generator")
    return make_testing_scenario_harness(NodeModelGeneratorOutputState, registry_resolver_tool) 