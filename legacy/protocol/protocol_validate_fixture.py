# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: protocol_fixture_validate
# namespace: foundation.protocol
# version: 0.1.0
# author: AI-Dev Migration
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-06-28
# last_modified_at: 2025-06-28
# entrypoint: protocol_fixture_validate.py
# protocols_supported: ["O.N.E. v0.1"]
# interface_type: Protocol
# interface_name: IProtocolValidateFixture
# mock_safe: true
# rationale: Provides a swappable, testable fixture interface for validator testing. Enables DI and flexible test setup.
# === /OmniNode:Tool_Metadata ===

from typing import Any, Dict, Optional, Protocol


class ProtocolValidateFixture(Protocol):
    """Protocol for a fixture that provides a validator instance for testing."""

    def get_fixture(self, config: Optional[Dict[str, Any]] = None) -> Any:
        """Return a validator instance, optionally configured."""
        ...
