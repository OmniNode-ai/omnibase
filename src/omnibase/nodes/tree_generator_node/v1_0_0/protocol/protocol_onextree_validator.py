# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:27.075705'
# description: Stamped by PythonHandler
# entrypoint: python://protocol_onextree_validator.py
# hash: 1cd602d4388d8847a52994d31176eb54eb02dbfd884b28503a2cd6c25afb230d
# last_modified_at: '2025-05-29T11:50:12.047200+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: protocol_onextree_validator.py
# namespace: omnibase.protocol_onextree_validator
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 0f72de69-a00d-4132-b3e2-9e8f79de64c0
# version: 1.0.0
# === /OmniNode:Metadata ===


from pathlib import Path
from typing import Protocol

from omnibase.model.model_onextree_validation import OnextreeValidationResultModel


class ProtocolOnextreeValidator(Protocol):
    """
    Protocol for .onextree validator tools.
    All implementations must return a canonical OnextreeValidationResultModel.
    """

    def validate_onextree_file(
        self, onextree_path: Path, root_directory: Path
    ) -> OnextreeValidationResultModel: ...
