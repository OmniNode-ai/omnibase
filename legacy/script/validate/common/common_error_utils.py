# === OmniNode:Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "common_error_utils"
# namespace: "omninode.tools.common_error_utils"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T18:25:48+00:00"
# last_modified_at: "2025-05-05T18:25:48+00:00"
# entrypoint: "common_error_utils.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: []
# base_class: []
# mock_safe: true
# === /OmniNode:Metadata ===



from typing import Any, Optional, List
from foundation.model.model_validate_error import ValidateMessageModel

class CommonErrorUtils:
    def add_error(self, errors: list, message: str, file: str, line: int = None, details: str = None, type: str = "error"):
        # TODO: Refactor to use unified message model
        raise NotImplementedError("add_error needs unified model refactor.")

    def add_warning(self, warnings: list, message: str, file: str, line: int = None, details: str = None, type: str = "warning"):
        # TODO: Refactor to use unified message model
        raise NotImplementedError("add_warning needs unified model refactor.")

    def add_failed_file(self, failed_files: list, file: str):
        failed_files.append(file)

# Singleton instance for use 