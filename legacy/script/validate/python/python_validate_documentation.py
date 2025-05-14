#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_documentation
# namespace: omninode.tools.validate_documentation
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:58+00:00
# last_modified_at: 2025-04-27T18:12:58+00:00
# entrypoint: validate_documentation.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_documentation.py containers.foundation.src.foundation.script.valid
ation.validate_documentation.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from pydantic import Field


# Config model for DocumentationValidator
class DocumentationValidatorConfig(ValidatorConfig):
    version: str = "v1"
    required_sections: List[str] = Field(
        default_factory=lambda: [
            "Overview",
            "Installation",
            "Usage",
            "API Reference",
            "Contributing",
        ]
    )
    min_readme_length: int = 100
    check_links: bool = True


    name="documentation",
    version="v1",
    group="quality",
    description="Validates documentation content and structure.",
)
class DocumentationValidator(ProtocolValidate):
    """Validates documentation content and structure."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = DocumentationValidatorConfig(**(config or {}))
        self.logger = dependencies.get("logger")

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="documentation",
            group="quality",
            description="Validates documentation content and structure.",
            version="v1",
        )

    def get_name(self) -> str:
        return "documentation"

    def validate(
        self, target: Path, config: Optional[DocumentationValidatorConfig] = None
    ) -> ValidationResult:
        cfg = config or self.config
        self.errors.clear()
        self.warnings.clear()
        is_valid = True

        readme_path = target / "README.md"
        if not readme_path.exists():
            self.errors.append(
                ValidationIssue(
                    message=f"README.md not found in {target}",
                    file=str(readme_path),
                    type="error",
                )
            )
            is_valid = False
        else:
            try:
                content = readme_path.read_text()
            except Exception as e:
                self.errors.append(
                    ValidationIssue(
                        message=f"Failed to read README.md: {e}",
                        file=str(readme_path),
                        type="error",
                    )
                )
                is_valid = False
                content = ""

            # Validate sections
            if not self._validate_sections(content, cfg.required_sections):
                is_valid = False
            # Validate length
            if not self._validate_length(content, cfg.min_readme_length):
                is_valid = False
            # Validate links if enabled
            if cfg.check_links and not self._validate_links(content):
                is_valid = False

        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version=cfg.version,
        )

    def _validate_sections(self, content: str, required_sections: List[str]) -> bool:
        is_valid = True
        headers = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
        headers = [h.strip() for h in headers]
        for section in required_sections:
            if section not in headers:
                self.errors.append(
                    ValidationIssue(
                        message=f"Required section '{section}' not found",
                        file="README.md",
                        type="error",
                    )
                )
                is_valid = False
        return is_valid

    def _validate_length(self, content: str, min_length: int) -> bool:
        if len(content) < min_length:
            self.errors.append(
                ValidationIssue(
                    message=f"README.md is too short (minimum {min_length} characters, found {len(content)})",
                    file="README.md",
                    type="error",
                )
            )
            return False
        return True

    def _validate_links(self, content: str) -> bool:
        is_valid = True
        links = re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", content)
        for text, url in links:
            if url.startswith(("http://", "https://")):
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code >= 400:
                        self.warnings.append(
                            ValidationIssue(
                                message=f"Broken link: {url} (status {response.status_code})",
                                file="README.md",
                                type="warning",
                            )
                        )
                        is_valid = False
                except Exception as e:
                    self.warnings.append(
                        ValidationIssue(
                            message=f"Failed to check link {url}: {e}",
                            file="README.md",
                            type="warning",
                        )
                    )
                    is_valid = False
        return is_valid

    def _validate(self, target: Path) -> bool:
        # Delegate to the main validate logic and return boolean validity
        result = self.validate(target)
        return result.is_valid
