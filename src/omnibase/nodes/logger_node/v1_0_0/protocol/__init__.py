# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: __init__.py
# version: 1.0.0
# uuid: 8e62d8f4-8d27-45d1-8514-921c5e669d2a
# author: OmniNode Team
# created_at: 2025-05-28T12:36:26.137769
# last_modified_at: 2025-05-28T17:20:04.799599
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: e055ac8e1604d6684dfd726c1d0d8295ecd496d6a7919b5ec212345c0caea525
# entrypoint: python@__init__.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.init
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
