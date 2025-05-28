# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_onextree_validator.py
# version: 1.0.0
# uuid: 0f72de69-a00d-4132-b3e2-9e8f79de64c0
# author: OmniNode Team
# created_at: 2025-05-28T12:36:27.075705
# last_modified_at: 2025-05-28T17:20:04.872475
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: 4d7de195d7a1ef413a865f13d7673c42d1d1740261fffaa0f551d3cecce373f5
# entrypoint: python@protocol_onextree_validator.py
# runtime_language_hint: python>=3.11
# namespace: omnibase.stamped.protocol_onextree_validator
# meta_type: tool
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
