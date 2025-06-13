import pytest
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    make_node_class_fixture,
    tool_bootstrap_fixture,
    tool_health_check_fixture,
    output_field_tool,
)
from omnibase.nodes.node_manager.v1_0_0.models.state import NodeManagerInputState, NodeManagerOutputState, ModelNodeManagerOutputField
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.testing.testing_scenario_harness import make_testing_scenario_harness
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync
from omnibase.nodes.node_manager.v1_0_0.registry.registry_node_manager import RegistryNodeManager
from omnibase.nodes.node_manager.v1_0_0.tools.tool_backend_selection import StubBackendSelection
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.constants import BACKEND_SELECTION_KEY, INPUT_VALIDATION_KEY, OUTPUT_FIELD_KEY, BOOTSTRAP_KEY, HEALTH_CHECK_KEY, INMEMORY_KEY
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_registry_resolver import registry_resolver_tool
from omnibase.nodes.node_logger.protocols.protocol_logger_emit_log_event import ProtocolLoggerEmitLogEvent
from pathlib import Path

# Register the node_class fixture for this module
node_class = make_node_class_fixture("NodeManager")

def pytest_addoption(parser):
    parser.addoption(
        "--regenerate-snapshots",
        action="store_true",
        default=False,
        help="Regenerate scenario output snapshots."
    )

@pytest.fixture(scope="module")
def logger_tool():
    """Fixture for logger tool implementing ProtocolLoggerEmitLogEvent."""
    class MockLoggerTool:
        def emit_log_event_sync(self, level, message, context=None):
            """Mock implementation of emit_log_event_sync."""
            emit_log_event_sync(level, message, context or {})
        
        def emit_log_event_async(self, level, message, context=None):
            """Mock implementation of emit_log_event_async."""
            self.emit_log_event_sync(level, message, context)
    
    return MockLoggerTool()

@pytest.fixture(scope="module")
def registry_node_manager(node_dir):
    """Fixture for RegistryNodeManager with all canonical tools already registered."""
    # The registry automatically registers all CANONICAL_TOOLS, so we don't need to register them manually
    registry = RegistryNodeManager(node_dir)
    
    # Only register additional tools that aren't in CANONICAL_TOOLS
    # The INMEMORY_KEY might need to be registered if not already present
    try:
        registry.register_tool(INMEMORY_KEY, InMemoryEventBus)
    except Exception:
        # Tool already registered, which is fine
        pass
    
    return registry

@pytest.fixture(scope="module")
def tool_backend_selection(registry_node_manager):
    return StubBackendSelection(registry_node_manager)

def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[node_manager.conftest] {msg}", context=context or {})

@pytest.fixture(scope="module")
def input_validation_tool():
    debug_log("Creating input_validation_tool fixture for node_manager")
    return ToolInputValidation(
        input_model=NodeManagerInputState,
        output_model=NodeManagerOutputState,
        output_field_model=ModelNodeManagerOutputField,
        node_id="node_manager",
    )

@pytest.fixture(scope="module")
def scenario_test_harness():
    debug_log("Creating scenario_test_harness fixture for node_manager")
    return make_testing_scenario_harness(NodeManagerOutputState, registry_resolver_tool) 