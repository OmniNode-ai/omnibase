from omnibase.nodes.node_template.v1_0_0.node import NodeTemplate
from omnibase.nodes.node_template.v1_0_0.registry.registry_template_node import RegistryTemplateNode
from omnibase.testing.testing_scenario_harness import run_scenario_regression_tests

test_scenario_yaml = run_scenario_regression_tests(NodeTemplate, RegistryTemplateNode, expected_version="1.0.0") 