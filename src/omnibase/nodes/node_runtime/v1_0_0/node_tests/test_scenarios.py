# [ONEX_PROMPT] This is the canonical scenario regression test for {NODE_NAME}. Replace all tokens and follow [ONEX_PROMPT] instructions when generating a new node.
from omnibase.nodes.{NODE_NAME}.v1_0_0.node import {NODE_CLASS}
from omnibase.nodes.{NODE_NAME}.v1_0_0.registry.registry_{NODE_NAME} import Registry{NODE_CLASS}
from omnibase.testing.testing_scenario_harness import run_scenario_regression_tests

# [ONEX_PROMPT] Update the expected_version as needed for your node's version.
test_scenario_yaml = run_scenario_regression_tests({NODE_CLASS}, Registry{NODE_CLASS}, expected_version="1.0.0") 