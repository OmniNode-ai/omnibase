# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: protocol_onextree_validator.py
# version: 1.0.0
# uuid: e32e6ec4-c1bf-4ecf-a70e-7b3b5257acda
# author: OmniNode Team
# created_at: 2025-05-24T12:09:47.506857
# last_modified_at: 2025-05-24T16:13:11.913757
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: f33326bcc5efdca793cae5f399d51d31fe55c9db45f56782722b24978cff661d
# entrypoint: python@protocol_onextree_validator.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.protocol_onextree_validator
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
