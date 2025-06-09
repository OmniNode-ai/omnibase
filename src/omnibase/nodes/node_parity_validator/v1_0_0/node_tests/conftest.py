import pytest
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    make_node_class_fixture,
    tool_bootstrap_fixture,
    tool_health_check_fixture,
    output_field_tool,
)
from omnibase.nodes.node_parity_validator.v1_0_0.models.state import ParityValidatorInputState, ParityValidatorOutputState, ModelParityValidatorOutputField
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.testing.testing_scenario_harness import make_testing_scenario_harness
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync
from omnibase.nodes.node_parity_validator.v1_0_0.registry.registry_template_node import RegistryTemplateNode
from omnibase.nodes.node_parity_validator.v1_0_0.tools.tool_backend_selection import StubBackendSelection
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.constants import BACKEND_SELECTION_KEY, INPUT_VALIDATION_KEY, OUTPUT_FIELD_KEY, BOOTSTRAP_KEY, HEALTH_CHECK_KEY, INMEMORY_KEY
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_registry_resolver import registry_resolver_tool
from omnibase.schemas.loader import SchemaLoader  # Canonical implementation for tests
from omnibase.protocol.protocol_schema_loader import ProtocolSchemaLoader

# Register the node_class fixture for this module
node_class = make_node_class_fixture("NodeParityValidator")

def pytest_addoption(parser):
    parser.addoption(
        "--regenerate-snapshots",
        action="store_true",
        default=False,
        help="Regenerate scenario output snapshots."
    )

@pytest.fixture(scope="module")
def tool_backend_selection():
    registry_template_node = RegistryTemplateNode()
    registry_template_node.register_tool(INMEMORY_KEY, InMemoryEventBus)
    return StubBackendSelection(registry_template_node)

def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[node_parity_validator.conftest] {msg}", context=context or {})

@pytest.fixture(scope="module")
def input_validation_tool():
    debug_log("Creating input_validation_tool fixture for node_parity_validator")
    return ToolInputValidation(
        input_model=ParityValidatorInputState,
        output_model=ParityValidatorOutputState,
        output_field_model=ModelParityValidatorOutputField,
        node_id="node_parity_validator",
    )

@pytest.fixture(scope="module")
def scenario_test_harness():
    debug_log("Creating scenario_test_harness fixture for node_parity_validator")
    return make_testing_scenario_harness(ParityValidatorOutputState, registry_resolver_tool)

@pytest.fixture
def metadata_loader() -> ProtocolSchemaLoader:
    """Fixture for protocol-typed metadata loader (SchemaLoader)."""
    return SchemaLoader()

# When instantiating NodeParityValidator in tests, inject metadata_loader=metadata_loader 