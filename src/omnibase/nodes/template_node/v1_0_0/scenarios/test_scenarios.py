import pytest
from pathlib import Path

@pytest.mark.parametrize(
    "scenario_path",
    [
        pytest.param(str(p), id=p.name)
        for p in (Path(__file__).parent.glob("*.yaml"))
        if p.name.startswith("scenario_")
    ],
)
@pytest.mark.asyncio
async def test_scenario_yaml(
    node_class,
    scenario_path,
    input_validation_tool,
    tool_backend_selection,
    output_field_tool,
    scenario_test_harness,
):
    output, expected = scenario_test_harness.run_scenario_test(
        node_class=node_class,
        scenario_path=scenario_path,
        input_validation_tool=input_validation_tool,
        tool_backend_selection=tool_backend_selection,
        output_field_tool=output_field_tool,
    )
    # Optionally, add node-specific assertions or hooks here 