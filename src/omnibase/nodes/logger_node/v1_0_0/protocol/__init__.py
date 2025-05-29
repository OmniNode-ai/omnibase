# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:26.137769'
# description: Stamped by PythonHandler
# entrypoint: python://__init__.py
# hash: c117ee43a151ea7f44e985a7f64dad5c00476b5c43b53be349f2b9c56ff44ba2
# last_modified_at: '2025-05-29T11:50:11.347231+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: __init__.py
# namespace: omnibase.init
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
