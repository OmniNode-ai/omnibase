import asyncio
import importlib
import logging
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

from omnibase.model.model_node_metadata import NodeMetadataBlock
# from omnibase.nodes.node_kafka_event_bus.v1_0_0.models import ModelEventBusConfig, NodeKafkaEventBusNodeInputState, ModelEventBusOutputField, NodeKafkaEventBusNodeOutputState
# If needed, import from .models.state instead
# from omnibase.nodes.node_kafka_event_bus.v1_0_0.models.state import NodeKafkaEventBusNodeInputState, NodeKafkaEventBusNodeOutputState
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_kafka_event_bus import (
    KafkaEventBus,
)
from omnibase.tools.tool_bootstrap import tool_bootstrap
from omnibase.tools.tool_health_check import tool_health_check
from omnibase.nodes.node_kafka_event_bus.v1_0_0.tools.tool_backend_selection import ToolBackendSelection
from omnibase.tools.tool_input_validation import ToolInputValidation
from omnibase.tools.tool_compute_output_field import tool_compute_output_field
from omnibase.model.model_output_field import OnexFieldModel
from omnibase.nodes.node_kafka_event_bus.constants import NODE_KAFKA_EVENT_BUS_ID, NODE_CLASS_NAME
from omnibase.constants import (
    CONTRACT_FILENAME,
    SCENARIOS_DIRNAME,
    SCENARIO_FILE_GLOB,
    NODE_KEY,
    INPUT_KEY,
    EXPECT_KEY,
    VERSION_KEY,
    OUTPUT_FIELD_KEY,
    MESSAGE_KEY,
    FIELD_REQUIRED_ERROR_MSG,
    BACKEND_KEY,
    ERROR_VALUE,
)
from omnibase.testing.testing_node_fixtures import (
    node_dir,
    node_metadata,
    scenario_test_entrypoint,
    scenario_dir,
    scenario_files,
    make_node_class_fixture,
    input_validation_tool,
    scenario_test_harness,
)


@pytest.fixture(scope="module")
def tool_backend_selection(node_dir):
    contract_path = node_dir / CONTRACT_FILENAME
    return ToolBackendSelection(contract_path=contract_path)


@pytest.mark.parametrize(
    "scenario_path",
    [
        pytest.param(str(p), id=p.name)
        for p in (Path(__file__).parent.parent / SCENARIOS_DIRNAME).glob(SCENARIO_FILE_GLOB)
    ],
)
@pytest.mark.asyncio
async def test_scenario_yaml(
    node_class,
    scenario_path,
    tool_bootstrap_fixture,
    tool_backend_selection,
    tool_health_check_fixture,
    input_validation_tool,
    output_field_tool,
    scenario_test_harness,
):
    output, expected = await scenario_test_harness.run_scenario_test(
        node_class=node_class,
        scenario_path=scenario_path,
        tool_bootstrap=tool_bootstrap_fixture,
        tool_backend_selection=tool_backend_selection,
        tool_health_check=tool_health_check_fixture,
        input_validation_tool=input_validation_tool,
        output_field_tool=output_field_tool,
    )
    # Optionally, add node-specific assertions or hooks here

# Register the node_class fixture for this module
node_class = make_node_class_fixture(NODE_CLASS_NAME)
