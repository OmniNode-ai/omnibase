#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "validate_naming_convention"
# namespace: "omninode.tools.validate_naming_convention"
# meta_type: "validator"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-07T11:30:00+00:00"
# last_modified_at: "2025-05-07T11:30:00+00:00"
# entrypoint: "validate_naming_convention.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ["ProtocolValidate", "ProtocolTool"]
# base_class: ["ProtocolValidate", "ProtocolTool"]
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validate_naming_convention.py containers.foundation.src.foundation.script.validate.validate_naming_convention.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import logging
from pathlib import Path
from typing import List, Optional, Any
from dataclasses import dataclass
import argparse
import re
import structlog
from foundation.util.util_file_output_writer import OutputWriter

from foundation.bootstrap.bootstrap import bootstrap
from foundation.script.validate.validate_registry import ValidatorRegistry
from foundation.di.di_container import DIContainer
from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.protocol.protocol_tool import ProtocolTool
from pydantic import BaseModel
from foundation.protocol.protocol_naming_convention import (
    NamingConventionCheck,
    NamingConventionValidator,
    NamingViolation,
)
from foundation.fixture.fixture_naming_convention import NamingConventionRules, NamingRule
from foundation.model.model_unified_result import (
    UnifiedResultModel, 
    UnifiedMessageModel, 
    UnifiedStatus,
    UnifiedVersionModel
)

# Initialize bootstrap
bootstrap()

class NamingConventionValidatorConfig(BaseModel):
    """Configuration for naming convention validation."""
    exclude_dirs: List[str] = [
        "__pycache__", 
        ".venv", 
        ".git", 
        "build", 
        "dist",
        "test_case",  # Test case directories contain example files that don't need to follow conventions
        "template",   # Template files don't need to follow conventions
    ]
    exclude_files: List[str] = [
        ".DS_Store", 
        "Thumbs.db",
        ".tree",      # Tree files are generated and don't need to follow conventions
        "__init__.py",  # Init files don't need to follow conventions
        "README.md",    # README files are standard and don't need to follow conventions
        "py.typed",   # py.typed is a standard file name
    ]
    exclude_patterns: List[str] = [
        r".*\.treeignore$",  # Tree ignore files
        r".*\.txt$",         # Text files (often templates)
        r".*\.json$",        # JSON files
        r".*\.sh$",          # Shell scripts
        r"hooks_[a-z-]+$",   # Git hook files
        r"git_.*\.md$",      # Git documentation files
    ]


@dataclass
class RuleBasedNamingCheck(NamingConventionCheck):
    """Check for naming conventions based on injected rules."""
    
    def __init__(self, rule: NamingRule):
        self.rule = rule
    
    @property
    def check_name(self) -> str:
        return self.rule.name
    
    @property
    def description(self) -> str:
        return self.rule.description or ""
    
    def validate(self, path: Path, content: Optional[str] = None) -> Optional[NamingViolation]:
        """Validate the path against this rule's pattern."""
        name = path.name  # Use full name including extension
        
        if not self.rule.matches(name):
            return NamingViolation(
                file_path=str(path),
                current_name=name,
                suggested_name=None,  # Let the error message guide the user
                violation_type="pattern_violation",
                context={"rule": self.rule.error_message}
            )
                
        return None


class NamingConventionValidator(ProtocolValidate, ProtocolTool):
    """Validator for naming conventions across all file types."""

    def __init__(self, logger: Optional[Any] = None, config: Optional[dict] = None, utility_registry: Any = None, di_container: Optional[DIContainer] = None, **dependencies):
        super().__init__(**dependencies)
        self.logger = logger or logging.getLogger(__name__)
        self.config = NamingConventionValidatorConfig(**(config or {}))
        self.utility_registry = utility_registry
        self.di_container = di_container or DIContainer()
        self.naming_rules = self.di_container.resolve(NamingConventionRules)
        self._checks: List[NamingConventionCheck] = [
            RuleBasedNamingCheck(rule) for rule in self.naming_rules.get_rules()
        ]

    def register_check(self, check: NamingConventionCheck) -> None:
        """Register a new naming convention check."""
        self._checks.append(check)

    def validate_path(self, path: Path) -> List[NamingViolation]:
        """Validate a single path against all registered checks."""
        violations = []
        
        try:
            content = path.read_text() if path.is_file() else None
        except Exception:
            content = None
            
        # First check for prefix-based rules
        prefix_rule = self.naming_rules.get_rule_for_file(path.name)
        if prefix_rule:
            check = RuleBasedNamingCheck(prefix_rule)
            violation = check.validate(path, content)
            if violation:
                violations.append(violation)
                return violations  # If a prefix rule exists and fails, no need to check general rules
                
        # If no prefix rule matched or if it passed, check general rules
        general_rule = self.naming_rules.get_rule("general_file_naming")
        if general_rule and not prefix_rule:  # Only check general rule if no prefix rule matched
            check = RuleBasedNamingCheck(general_rule)
            violation = check.validate(path, content)
            if violation:
                violations.append(violation)
                
        return violations

    def validate_directory(self, directory: Path) -> List[NamingViolation]:
        """Validate an entire directory recursively against all registered checks."""
        violations = []
        
        for path in directory.rglob("*"):
            # Skip directories in exclude list
            if any(ex in path.parts for ex in self.config.exclude_dirs):
                continue
                
            # Skip files in exclude list
            if path.name in self.config.exclude_files:
                continue
                
            # Skip files matching exclude patterns
            if any(re.match(pattern, path.name) for pattern in self.config.exclude_patterns):
                continue
                
            if path.is_file():
                violations.extend(self.validate_path(path))
                
        return violations

    def validate(self, target, config: dict = None):
        # TODO: Refactor to use unified result model
        raise NotImplementedError("NamingConventionValidator.validate() needs unified model refactor.")

    def generate_report(self, violations: List[NamingViolation]) -> str:
        """Generate a human-readable report of violations."""
        if not violations:
            return "No naming convention violations found."
            
        report = ["Naming Convention Violations:"]
        
        for violation in violations:
            report.append(f"\nFile: {violation.file_path}")
            report.append(f"Current name: {violation.current_name}")
            if violation.suggested_name:
                report.append(f"Suggested name: {violation.suggested_name}")
            report.append(f"Violation type: {violation.violation_type}")
            if violation.context:
                for key, value in violation.context.items():
                    report.append(f"{key}: {value}")
                    
        return "\n".join(report)

    def _validate(self, *args, **kwargs):
        raise NotImplementedError(
            "Use validate() instead of _validate() for NamingConventionValidator."
        )

    @classmethod
    def metadata(cls):
        return {
            "name": "naming_convention",
            "group": "standards",
            "description": "Enforces naming conventions across all file types.",
            "version": "v1",
        }

    def get_name(self) -> str:
        return "naming_convention"

    def add_arguments(self) -> None:
        """Add CLI arguments to the parser (if used as a CLI tool)."""
        pass

    def run(self, dry_run: bool = False) -> UnifiedResultModel:
        """Run the validator, supporting dry-run mode."""
        logger = logging.getLogger(__name__)
        if dry_run:
            logger.info(
                "[DRY RUN] NamingConventionValidator would validate naming conventions."
            )
            return UnifiedResultModel(
                status=UnifiedStatus.success, 
                target=".", 
                messages=[], 
                version=UnifiedVersionModel(protocol_version="1.0"),
                tool_name="naming_convention"
            )
        logger.info("Running NamingConventionValidator.")
        return self.validate(target=".")

    def execute(self) -> UnifiedResultModel:
        """Standard entry point for execution."""
        return self.run(dry_run=False)

def main(logger=None, output_writer: OutputWriter = None):
    """CLI entry point for the naming convention validator."""
    if logger is None:
        logger = structlog.get_logger("validate_naming_convention")
    parser = argparse.ArgumentParser(description="Validate naming conventions in files")
    parser.add_argument("target", help="Target directory or file to validate")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    di_container = DIContainer()
    validator = di_container.resolve(NamingConventionValidator)
    result = validator.validate(args.target)
    
    if args.verbose:
        logger.info("\nValidation Results:")
        logger.info(f"Status: {result.status}")
        logger.info(f"Target: {result.target}")
        logger.info(f"Tool: {result.tool_name}")
        logger.info(f"Version: {result.version}")
        logger.info("\nMessages:")
        for msg in result.messages:
            logger.info(f"- {msg.summary}")
            logger.info(f"  File: {msg.file}")
            if msg.context:
                logger.info(f"  Context: {msg.context}")
            logger.info("")
    
    if output_writer:
        output_writer.write_json(result)
    
    return 0 if result.status == UnifiedStatus.success else 1

if __name__ == "__main__":
    exit(main())

# Register with validator registry
ValidatorRegistry().register(
    name="naming_convention",
    validator_cls=NamingConventionValidator,
    meta={
        "name": "naming_convention",
        "version": "v1",
        "group": "standards",
        "description": "Enforces naming conventions across all file types.",
    },
)

# Register with DI container
DIContainer().register(NamingConventionValidator)
DIContainer().register(NamingConventionRules) 