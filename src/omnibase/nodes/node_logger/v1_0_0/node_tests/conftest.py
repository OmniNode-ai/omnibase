import pytest
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    make_node_class_fixture,
    tool_bootstrap_fixture,
    tool_health_check_fixture,
    output_field_tool,
)
from omnibase.nodes.node_logger.v1_0_0.models.state import LoggerInputState, LoggerOutputState
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.testing.testing_scenario_harness import make_testing_scenario_harness
from omnibase.enums.log_level import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import emit_log_event_sync
from omnibase.nodes.node_logger.v1_0_0.tools.tool_backend_selection import StubBackendSelection
from omnibase.nodes.node_logger.v1_0_0.registry.registry_node_logger import RegistryNodeLogger
from omnibase.runtimes.onex_runtime.v1_0_0.tools.tool_registry_resolver import registry_resolver_tool
from omnibase.nodes.node_logger.v1_0_0.constants import *

# Canonical node_class fixture: resolve from registry
node_class = RegistryNodeLogger().get_tool('logger_engine')

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
    Provides a stub backend selection tool for the logger node, with registry injection.
    """
    return StubBackendSelection(RegistryNodeLogger())

def debug_log(msg, context=None):
    emit_log_event_sync(LogLevelEnum.DEBUG, f"[node_logger.conftest] {msg}", context=context or {})

@pytest.fixture(scope="module")
def input_validation_tool():
    debug_log("Creating input_validation_tool fixture for node_logger")
    return ToolInputValidation(
        input_model=LoggerInputState,
        output_model=LoggerOutputState,
        output_field_model=None,  # Update if logger node uses output field models
        node_id=NODE_LOGGER,
    )

@pytest.fixture(scope="module")
def scenario_test_harness():
    debug_log("Creating scenario_test_harness fixture for node_logger")
    return make_testing_scenario_harness(LoggerOutputState, registry_resolver_tool) 