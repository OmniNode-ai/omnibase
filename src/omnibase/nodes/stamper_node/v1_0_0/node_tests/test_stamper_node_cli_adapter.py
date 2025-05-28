# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_stamper_node_cli_adapter.py
# version: 1.0.0
# uuid: 51d50759-5735-483b-b78d-99c30c237fe6
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.857045
# last_modified_at: 2025-05-28T17:20:06.364983
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: a3729d9f0f8ec6ddeaf66167fec478ac832f37d883af2a0c917771901acc1a53
# entrypoint: python@test_stamper_node_cli_adapter.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.test_stamper_node_cli_adapter
# meta_type: tool
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
