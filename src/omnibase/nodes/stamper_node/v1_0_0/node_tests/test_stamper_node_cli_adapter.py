# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: test_stamper_node_cli_adapter.py
# version: 1.0.0
# uuid: 045cfb47-d7e9-4760-8e90-3448808a2bac
# author: OmniNode Team
# created_at: 2025-05-23T10:29:19.163773
# last_modified_at: 2025-05-23T17:42:52.030891
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d003c0005a274f91583524a98a8f69b3ef3fb12cfdfea24a7e40a332f2d92b29
# entrypoint: python@test_stamper_node_cli_adapter.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.test_stamper_node_cli_adapter
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
