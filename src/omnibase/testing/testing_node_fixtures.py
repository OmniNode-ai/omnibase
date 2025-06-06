import pytest
from pathlib import Path
import importlib

from omnibase.constants import CONTRACT_FILENAME, SCENARIOS_DIRNAME, SCENARIO_FILE_GLOB
from omnibase.model.model_node_metadata import NodeMetadataBlock
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import (
    ModelEventBusInputState,
    ModelEventBusOutputState,
    ModelEventBusOutputField,
)
from omnibase.nodes.node_kafka_event_bus.constants import NODE_KAFKA_EVENT_BUS_ID
from omnibase.testing.testing_scenario_harness import testing_scenario_harness
from omnibase.tools.tool_bootstrap import tool_bootstrap
from omnibase.tools.tool_health_check import tool_health_check
from omnibase.tools.tool_compute_output_field import tool_compute_output_field

def resolve_node_class(scenario_test_entrypoint: str, node_class_name: str):
    if not scenario_test_entrypoint or not scenario_test_entrypoint.startswith("python -m "):
        pytest.skip("Only python -m ... entrypoints are supported in this test")
    module_path = scenario_test_entrypoint.split("python -m ", 1)[1].strip()
    if module_path.endswith(".py"):
        module_path = module_path[:-3]
    module_path = module_path.replace("/", ".").replace(".py", "")
    module = importlib.import_module(module_path)
    node_cls = None
    for attr in dir(module):
        obj = getattr(module, attr)
        if isinstance(obj, type) and attr == node_class_name:
            node_cls = obj
            break
    if node_cls is None:
        raise RuntimeError(f"Could not find node class in module {module_path}")
    return node_cls

@pytest.fixture(scope="module")
def node_dir(request):
    return Path(request.fspath).parent.parent

@pytest.fixture(scope="module")
def node_metadata(node_dir):
    node_onex_yaml = node_dir / CONTRACT_FILENAME
    with open(node_onex_yaml, "r") as f:
        content = f.read()
    return NodeMetadataBlock.from_file_or_content(content)

@pytest.fixture(scope="module")
def scenario_test_entrypoint(node_metadata):
    return node_metadata.scenario_test_entrypoint

@pytest.fixture(scope="module")
def scenario_dir(node_dir):
    return node_dir / SCENARIOS_DIRNAME

@pytest.fixture(scope="module")
def scenario_files(scenario_dir):
    return list(scenario_dir.glob(SCENARIO_FILE_GLOB))

def make_node_class_fixture(node_class_name):
    @pytest.fixture(scope="module")
    def node_class(scenario_test_entrypoint):
        return resolve_node_class(scenario_test_entrypoint, node_class_name)
    return node_class

@pytest.fixture(scope="module")
def input_validation_tool():
    return ToolInputValidation(
        input_model=ModelEventBusInputState,
        output_model=ModelEventBusOutputState,
        output_field_model=ModelEventBusOutputField,
        node_id=NODE_KAFKA_EVENT_BUS_ID,
    )

@pytest.fixture(scope="module")
def scenario_test_harness():
    return testing_scenario_harness

@pytest.fixture(scope="module")
def tool_bootstrap_fixture():
    return tool_bootstrap

@pytest.fixture(scope="module")
def tool_health_check_fixture():
    return tool_health_check

@pytest.fixture(scope="module")
def output_field_tool():
    return tool_compute_output_field 