# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# schema_version: 1.0.0
# name: python_tool_fix_base_abc
# namespace: omninode.tools.python_tool_fix_base_abc
# meta_type: model
# version: 0.1.0
# author: OmniNode Team
# owner: jonah@omninode.ai
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-05-02T18:46:08+00:00
# last_modified_at: 2025-05-02T18:46:08+00:00
# entrypoint: python_tool_fix_base_abc.py
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ABC']
# base_class: ['ABC']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class FixResult:
    def __init__(
        self,
        changed: bool,
        errors: Optional[List[str]] = None,
        warnings: Optional[List[str]] = None,
        details: Optional[dict] = None,
    ):
        self.changed = changed
        self.errors = errors or []
        self.warnings = warnings or []
        self.details = details or {}

    def __bool__(self):
        return self.changed and not self.errors


class BaseFixer(ABC):
    @abstractmethod
    def fix(
        self, path: Path, dry_run: bool = False, logger: Optional[logging.Logger] = None
    ) -> FixResult:
        """Apply the fixer to the given file. Return a FixResult object."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def languages_supported(self) -> List[str]:
        return ["python"]  # Default, override as needed