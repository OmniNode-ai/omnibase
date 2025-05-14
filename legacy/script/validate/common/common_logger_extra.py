#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "common_logger_extra"
# namespace: "omninode.tools.common_logger_extra"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "common_logger_extra.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['Exception']
# base_class: ['Exception']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""logger_extra.py
containers.foundation.src.foundation.script.validate.common.logger_extra.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

from typing import Any, Dict, Optional

REQUIRED_FIELDS = ["user_id", "request_id"]
OPTIONAL_FIELDS = ["session_id"]
ALLOW_EXTRA = True


class ProtocolLoggerExtraError(Exception):
    pass


def make_logger_extra(
    *, user_id: Any, request_id: Any, session_id: Optional[Any] = None, **extra
) -> Dict[str, Any]:
    """Helper to build logger extra dicts with required/optional fields and a
    marker for validation.

    Raises ProtocolLoggerExtraError if required fields are missing.
    """
    d = {"user_id": user_id, "request_id": request_id}
    if session_id is not None:
        d["session_id"] = session_id
    d.update(extra)
    d["__built_by_logger_extra__"] = True
    # Optionally enforce no extra fields if ALLOW_EXTRA is False
    if not ALLOW_EXTRA:
        allowed = set(REQUIRED_FIELDS + OPTIONAL_FIELDS)
        extras = set(d.keys()) - allowed - {"__built_by_logger_extra__"}
        if extras:
            raise ProtocolLoggerExtraError(f"Unexpected extra fields: {extras}")
    return d