#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validation_message
# namespace: omninode.tools.validation_message
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:00+00:00
# last_modified_at: 2025-04-27T18:13:00+00:00
# entrypoint: validation_message.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validation_message.py
containers.foundation.src.foundation.script.validate.validation_message.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ValidationMessage:
    """Class for validation messages (errors or warnings)."""

    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    code: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Format the message for display."""
        parts = [self.message]
        if self.file:
            parts.append(f"File: {self.file}")
        if self.line:
            parts.append(f"Line: {self.line}")
        if self.code:
            parts.append(f"Code: {self.code}")
        if self.details:
            parts.append(f"Details: {json.dumps(self.details, indent=2)}")
        return " | ".join(parts)
