# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.857045'
# description: Stamped by PythonHandler
# entrypoint: python://test_stamper_node_cli_adapter.py
# hash: 95f9132efb29e8239a3ac6a8ed5b0be7dbcb3b97b77c787c4e95a668953cc913
# last_modified_at: '2025-05-29T11:50:11.854812+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_stamper_node_cli_adapter.py
# namespace: omnibase.test_stamper_node_cli_adapter
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
    cli_args = ["/tmp/foo.py", "--author", "Alice"]
    input_state = adapter.parse_cli_args(cli_args)
    assert isinstance(input_state, StamperInputState)
    assert input_state.file_path == "/tmp/foo.py"
    assert input_state.author == "Alice"
    assert input_state.version  # Should be non-empty


def test_stamper_node_cli_adapter_default_author() -> None:
    adapter = StamperNodeCliAdapter()
    cli_args = ["/tmp/bar.py"]
    input_state = adapter.parse_cli_args(cli_args)
    assert input_state.file_path == "/tmp/bar.py"
    assert input_state.author == "OmniNode Team"
    assert input_state.version  # Should be non-empty
