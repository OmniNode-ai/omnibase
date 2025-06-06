import pytest
import yaml
from typing import Any, Callable, Tuple

from omnibase.constants import (
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
from omnibase.protocol.protocol_testing_scenario_harness import ProtocolTestingScenarioHarness

class TestingScenarioHarness(ProtocolTestingScenarioHarness):
    def run_scenario_test(
        self,
        node_class: type,
        scenario_path: str,
        tool_bootstrap: Any,
        tool_backend_selection: Any,
        tool_health_check: Any,
        input_validation_tool: Any,
        output_field_tool: Any,
        async_event_handler_attr: str = "start_async_event_handlers",
        output_comparator: Callable = None,
    ) -> Tuple[Any, Any]:
        """
        Shared scenario test harness for ONEX nodes.
        Implements ProtocolTestingScenarioHarness.
        Instantiates the node, runs the scenario, and returns (output, expected).
        Optionally accepts a custom output_comparator for node-specific quirks.
        """
        with open(scenario_path, "r") as f:
            scenario = yaml.safe_load(f)
        chain = scenario.get("chain", [])
        assert chain, f"No chain found in scenario: {scenario_path}"
        step = chain[0]
        node_name = step[NODE_KEY]
        input_data = step[INPUT_KEY]
        expected = step.get(EXPECT_KEY)
        if expected is None:
            pytest.skip(f"No 'expect' field in scenario: {scenario_path}")
        node = node_class(
            tool_bootstrap=tool_bootstrap,
            tool_backend_selection=tool_backend_selection,
            tool_health_check=tool_health_check,
            input_validation_tool=input_validation_tool,
            output_field_tool=output_field_tool,
        )
        # Optionally start async event handlers
        if async_event_handler_attr and hasattr(node, async_event_handler_attr):
            getattr(node, async_event_handler_attr)()
        output = node.run(input_data)
        if output_comparator:
            output_comparator(output, expected)
        return output, expected

# Export a default instance for injection/use

testing_scenario_harness = TestingScenarioHarness() 