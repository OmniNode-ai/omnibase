import pytest
import yaml
from typing import Any, Callable, Tuple
import asyncio
import pydantic

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
    async def run_scenario_test(
        self,
        node_class: type,
        scenario_path: str,
        tool_bootstrap: Any,
        tool_backend_selection: Any,
        tool_health_check: Any,
        input_validation_tool: Any,
        output_field_tool: Any,
        config: Any = None,
        async_event_handler_attr: str = "start_async_event_handlers",
        output_comparator: Callable = None,
    ) -> Tuple[Any, Any]:
        """
        Shared scenario test harness for ONEX nodes.
        Implements ProtocolTestingScenarioHarness.
        Instantiates the node, runs the scenario, and returns (output, expected).
        Optionally accepts a custom output_comparator for node-specific quirks.
        Now supports error snapshotting: if an exception is raised, it is serialized and compared to the expected snapshot.
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
            config=config,
        )
        # Optionally start async event handlers
        if async_event_handler_attr and hasattr(node, async_event_handler_attr):
            handler = getattr(node, async_event_handler_attr)
            if asyncio.iscoroutinefunction(handler):
                await handler()
            else:
                handler()
        # Canonical: always instantiate the input model for the node
        input_model = getattr(node_class, '__annotations__', {}).get('run', None)
        try:
            if hasattr(node_class, 'run') and hasattr(node_class.run, '__annotations__'):
                input_model_type = node_class.run.__annotations__.get('input_state', None)
                if input_model_type is not None:
                    input_instance = input_model_type(**input_data)
                else:
                    input_instance = input_data
            else:
                input_instance = input_data
            output = node.run(input_instance)
            if output_comparator:
                output_comparator(output, expected)
            return output, expected
        except Exception as exc:
            # Canonical error serialization for snapshot comparison
            error_output = {
                "error_type": type(exc).__name__,
                "error_module": type(exc).__module__,
                "message": str(exc),
            }
            # If it's a Pydantic validation error, include details
            if isinstance(exc, (pydantic.ValidationError, getattr(pydantic, 'PydanticUserError', type(None)))):
                error_output["validation_errors"] = exc.errors() if hasattr(exc, 'errors') else None
            return error_output, expected

# Export a default instance for injection/use

testing_scenario_harness = TestingScenarioHarness() 