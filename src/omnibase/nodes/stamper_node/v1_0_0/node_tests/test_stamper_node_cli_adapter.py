# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.857045'
# description: Stamped by PythonHandler
# entrypoint: python://test_stamper_node_cli_adapter
# hash: 3fdd7992a1851e6213177d16b523d0be4d37fb541fbd2b45b54f1e3f3f596685
# last_modified_at: '2025-05-29T14:13:59.974533+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_stamper_node_cli_adapter.py
# namespace: python://omnibase.nodes.stamper_node.v1_0_0.node_tests.test_stamper_node_cli_adapter
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 51d50759-5735-483b-b78d-99c30c237fe6
# version: 1.0.0
# === /OmniNode:Metadata ===


from ..helpers.stamper_node_cli_adapter import StamperNodeCliAdapter
from ..models.state import StamperInputState


def test_stamper_node_cli_adapter_basic() -> None:
    adapter = StamperNodeCliAdapter()
    cli_args = ["/tmp/foo", "--author", "Alice"]
    input_state = adapter.parse_cli_args(cli_args)
    assert isinstance(input_state, StamperInputState)
    assert input_state.file_path == "/tmp/foo"
    assert input_state.author == "Alice"
    assert input_state.version  # Should be non-empty


def test_stamper_node_cli_adapter_default_author() -> None:
    adapter = StamperNodeCliAdapter()
    cli_args = ["/tmp/bar"]
    input_state = adapter.parse_cli_args(cli_args)
    assert input_state.file_path == "/tmp/bar"
    assert input_state.author == "OmniNode Team"
    assert input_state.version  # Should be non-empty
