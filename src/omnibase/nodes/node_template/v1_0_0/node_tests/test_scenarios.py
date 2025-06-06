import pytest
from pathlib import Path
from omnibase.constants import SCENARIOS_DIRNAME, SCENARIO_FILE_GLOB
from omnibase.testing.testing_node_fixtures import (
    make_node_class_fixture,
)

# Register the node_class fixture for this module
node_class = make_node_class_fixture("NodeTemplate")

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
    event_bus_config,
):
    output, expected = await scenario_test_harness.run_scenario_test(
        node_class=node_class,
        scenario_path=scenario_path,
        tool_bootstrap=tool_bootstrap_fixture,
        tool_backend_selection=tool_backend_selection,
        tool_health_check=tool_health_check_fixture,
        input_validation_tool=input_validation_tool,
        output_field_tool=output_field_tool,
        config=event_bus_config,
    )
    # Optionally, add node-specific assertions or hooks here 