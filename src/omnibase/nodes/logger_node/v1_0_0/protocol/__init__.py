# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode.ai
# created_at: '2025-05-28T12:36:26.137769'
# description: Stamped by PythonHandler
# entrypoint: python://__init__
# hash: 95a3c692d03c1520965796a31c871dfe3b5967bc19d00e11e660d2b1028b6598
# last_modified_at: '2025-05-29T14:13:59.287126+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: python://omnibase.nodes.logger_node.v1_0_0.protocol.__init__
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 8e62d8f4-8d27-45d1-8514-921c5e669d2a
# version: 1.0.0
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
