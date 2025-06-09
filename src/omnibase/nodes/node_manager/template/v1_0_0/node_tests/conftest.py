# [ONEX_PROMPT] This is the canonical conftest.py for {NODE_NAME} node tests. Replace all tokens and follow [ONEX_PROMPT] instructions when generating a new node.
import pytest
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    make_node_class_fixture,
    tool_bootstrap_fixture,
    tool_health_check_fixture,
    output_field_tool,
)
from omnibase.nodes.{NODE_NAME}.v1_0_0.models.state import {NODE_CLASS}InputState, {NODE_CLASS}OutputState, Model{NODE_CLASS}OutputField
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.testing.testing_scenario_harness import make_testing_scenario_harness
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync
from omnibase.nodes.{NODE_NAME}.v1_0_0.registry.registry_{NODE_NAME} import Registry{NODE_CLASS}
from omnibase.nodes.{NODE_NAME}.v1_0_0.tools.tool_backend_selection import StubBackendSelection
from omnibase.runtimes.onex_runtime.v1_0_0.events.event_bus_in_memory import InMemoryEventBus
from omnibase.constants import BACKEND_SELECTION_KEY, INPUT_VALIDATION_KEY, OUTPUT_FIELD_KEY, BOOTSTRAP_KEY, HEALTH_CHECK_KEY, INMEMORY_KEY
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_registry_resolver import registry_resolver_tool

# [ONEX_PROMPT] Register the node_class fixture for this module. Update the class name as needed for your node.
node_class = make_node_class_fixture("{NODE_CLASS}")

def pytest_addoption(parser):
    parser.addoption(
        "--regenerate-snapshots",
        action="store_true",
        default=False,
        help="Regenerate scenario output snapshots."
    )

# [ONEX_PROMPT] Customize this fixture to register backend selection tools for your node.
@pytest.fixture(scope="module")
def tool_backend_selection():
    registry = Registry{NODE_CLASS}()
    registry.register_tool(INMEMORY_KEY, InMemoryEventBus)
    return StubBackendSelection(registry)

# [ONEX_PROMPT] Use this function for debug logging in test fixtures for {NODE_NAME}.
def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[{NODE_NAME}.conftest] {msg}", context=context or {})

# [ONEX_PROMPT] Customize this fixture to provide the input validation tool for your node.
@pytest.fixture(scope="module")
def input_validation_tool():
    debug_log("Creating input_validation_tool fixture for {NODE_NAME}")
    return ToolInputValidation(
        input_model={NODE_CLASS}InputState,
        output_model={NODE_CLASS}OutputState,
        output_field_model=Model{NODE_CLASS}OutputField,
        node_id="{NODE_NAME}",
    )

# [ONEX_PROMPT] Customize this fixture to provide the scenario test harness for your node.
@pytest.fixture(scope="module")
def scenario_test_harness():
    debug_log("Creating scenario_test_harness fixture for {NODE_NAME}")
    return make_testing_scenario_harness({NODE_CLASS}OutputState, registry_resolver_tool) 