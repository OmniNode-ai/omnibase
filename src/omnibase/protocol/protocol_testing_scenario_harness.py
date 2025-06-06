from typing import Protocol, Any, Callable, Tuple

class ProtocolTestingScenarioHarness(Protocol):
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
        ... 