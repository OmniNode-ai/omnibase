# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 0.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 0.1.0
# name: stamping_engine.py
# version: 1.0.0
# uuid: b17353b3-d017-4f14-959e-d2a458bd81ea
# author: OmniNode Team
# created_at: 2025-05-21T12:41:40.163704
# last_modified_at: 2025-05-21T16:42:46.052159
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 19749bad06689fafdef65bcfb690339ebe0370d5a82ad1225e876c7893d00d51
# entrypoint: {'type': 'python', 'target': 'stamping_engine.py'}
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.stamping_engine
# meta_type: tool
# === /OmniNode:Metadata ===

from pathlib import Path
from typing import Optional

from omnibase.model.enum_onex_status import OnexStatus
from omnibase.model.model_onex_message import LogLevelEnum, OnexMessageModel
from omnibase.model.model_onex_message_result import OnexResultModel
from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


def stamp_file(
    path: Path,
    content: str,
    handler: "ProtocolFileTypeHandler",
    now: Optional[str] = None,
) -> OnexResultModel:
    """
    Canonical stamping pipeline for all file types.
    - Delegates all stamping/idempotency logic to the handler (which uses the mixin).
    - Aggregates and returns results.
    """
    try:
        # Delegate to handler's protocol-compliant stamping method
        result = handler.stamp(path, content)
        return result
    except Exception as e:
        messages = [
            OnexMessageModel(summary=f"Stamping failed: {e}", level=LogLevelEnum.ERROR)
        ]
        return OnexResultModel(
            status=OnexStatus.ERROR,
            target=str(path),
            messages=messages,
            metadata={"note": "Stamping failed", "error": str(e)},
            auto_fix_applied=False,
            failed_files=[str(path)],
        )
