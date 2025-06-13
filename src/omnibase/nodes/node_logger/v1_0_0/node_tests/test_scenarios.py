from omnibase.nodes.node_logger.v1_0_0.node import NodeLogger
from omnibase.nodes.node_logger.v1_0_0.registry.registry_node_logger import RegistryNodeLogger
from omnibase.testing.testing_scenario_harness import run_scenario_regression_tests

test_scenario_yaml = run_scenario_regression_tests(NodeLogger, RegistryNodeLogger, expected_version="1.0.0") 