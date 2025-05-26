# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: 36dd8e64-47ff-4b11-9962-5334b7271469
# author: OmniNode Team
# created_at: 2025-05-26T12:15:35.015026
# last_modified_at: 2025-05-26T16:53:38.728671
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 35b1de74ba206b48d3f24011e8e893ecf104c0751678ac6c8d9986a10cd16ce9
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.init
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Protocols for the logger node.

This package contains protocol definitions that define interfaces
for pluggable components in the logger node.
"""

from .protocol_log_format_handler import ProtocolLogFormatHandler

__all__ = [
    "ProtocolLogFormatHandler",
]
