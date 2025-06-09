from omnibase.nodes.node_parity_validator.v1_0_0.node import NodeParityValidator
from omnibase.nodes.node_parity_validator.v1_0_0.registry.registry_template_node import RegistryTemplateNode
from omnibase.testing.testing_scenario_harness import run_scenario_regression_tests

# Ensure all test node instantiations inject metadata_loader fixture
# Example:
# node = NodeParityValidator(..., metadata_loader=metadata_loader)

test_scenario_yaml = run_scenario_regression_tests(NodeParityValidator, RegistryTemplateNode, expected_version="1.0.0") 