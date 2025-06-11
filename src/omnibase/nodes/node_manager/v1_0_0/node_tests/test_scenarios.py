from omnibase.nodes.node_manager.v1_0_0.node import NodeManager
from omnibase.nodes.node_manager.v1_0_0.registry.registry_node_manager import RegistryNodeManager
from omnibase.testing.testing_scenario_harness import run_scenario_regression_tests
from pathlib import Path

test_scenario_yaml = run_scenario_regression_tests(NodeManager, lambda *args, **kwargs: RegistryNodeManager(Path(__file__).parent, **kwargs), expected_version="1.0.0") 