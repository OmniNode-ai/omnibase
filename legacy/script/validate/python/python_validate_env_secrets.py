#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_env_secrets
# namespace: omninode.tools.validate_env_secrets
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:12:56+00:00
# last_modified_at: 2025-04-27T18:12:56+00:00
# entrypoint: validate_env_secrets.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_env_secrets.py containers.foundation.src.foundation.script.validat
ion.validate_env_secrets.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import argparse
import logging
from pathlib import Path

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)


class EnvSecretsValidatorConfig(ValidatorConfig):
    version: str = "v1"
    # Add config fields as needed (patterns, safe_values, ignore_paths, etc.)


    name="env_secrets",
    version="v1",
    group="security",
    description="Validates that secrets/configuration are not hardcoded in code or config files.",
)
class EnvSecretsValidator(ProtocolValidate):
    """Validates that secrets/configuration are not hardcoded in code or config
    files."""

    def __init__(self, config=None, **dependencies):
        super().__init__(config, **dependencies)
        self.config = EnvSecretsValidatorConfig(**(config or {}))
        self.logger = (
            dependencies.get("logger")
            if "logger" in dependencies
            else logging.getLogger(__name__)
        )
        # Patterns to identify potential secrets/configuration
        self.patterns = {
            "port": r"(?:^|\s|=)(\d{2,5})(?:\s|$|:)",
            "password": r'(?i)(?:password|passwd|pwd)[\s]*[=:]\s*["\']?([^"\'\s]+)["\']?',
            "username": r'(?i)(?:username|user|uname)[\s]*[=:]\s*["\']?([^"\'\s]+)["\']?',
            "api_key": r'(?i)(?:api[_-]?key|token|secret)[\s]*[=:]\s*["\']?([^"\'\s]+)["\']?',
            "url": r'(?i)(?:url|host|endpoint)[\s]*[=:]\s*["\']?(http[s]?://[^"\'\s]+)["\']?',
            "email": r"([\w\.-]+@[\w\.-]+\.\w+)",
            "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
        }
        self.safe_values = {
            "port": {"80", "443", "3000", "8080"},
            "username": {"postgres", "root", "admin"},
            "password": {"postgres"},
            "host": {"localhost", "127.0.0.1", "0.0.0.0"},
        }
        self.ignore_paths = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            "dist",
            "build",
        }
        self.check_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".yml",
            ".yaml",
            ".json",
            ".toml",
            ".ini",
            ".conf",
            ".sh",
            ".bash",
            ".zsh",
            ".env",
            "Dockerfile",
            "docker-compose.yml",
        }

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="env_secrets",
            group="security",
            description="Validates that secrets/configuration are not hardcoded in code or config files.",
            version="v1",
        )

    def get_name(self) -> str:
        return "env_secrets"

    def should_check_file(self, file_path):
        for parent in file_path.parents:
            if parent.name in self.ignore_paths:
                return False
        if file_path.name in self.ignore_paths:
            return False
        return any(str(file_path).endswith(ext) for ext in self.check_extensions)

    def is_safe_value(self, pattern_type, value):
        return value in self.safe_values.get(pattern_type, set())

    def validate(
        self, target: Path, config: EnvSecretsValidatorConfig = None
    ) -> ValidationResult:
        """Validate that secrets/configuration are not hardcoded in code or config files.

        Args:
            target: Path to directory or file to check
            config: Optional configuration
        Returns:
            ValidationResult: Result of the validation
        """
        self.errors.clear()
        self.warnings.clear()
        self.failed_files.clear()
        is_valid = True
        findings = []
        failed_files = set()
        if target.is_file():
            if self.should_check_file(target):
                findings = self.check_file(target)
        else:
            for file_path in target.rglob("*"):
                if file_path.is_file() and self.should_check_file(file_path):
                    findings.extend(self.check_file(file_path))
        for file_path, pattern_type, line_num, line in findings:
            self.add_error(
                message=f"Potential {pattern_type} found in {file_path} at line {line_num}",
                file=str(file_path),
                line=line_num,
                details={"line": line},
                type="error",
            )
            self.add_failed_file(file_path)
            is_valid = False
        return ValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            version=self.config.version,
        )

    def check_file(self, file_path):
        findings = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line_num, line in enumerate(lines, 1):
                if line.strip().startswith(("#", "//", "/*", "*", "--")):
                    continue
                for pattern_type, pattern in self.patterns.items():
                    import re

                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1)
                        # For URLs, skip common non-secret env keys
                        if pattern_type == "url":
                            key = (
                                line.split("=", 1)[0].strip().upper()
                                if "=" in line
                                else ""
                            )
                            safe_url_keys = {
                                "API_URL",
                                "BASE_URL",
                                "ENDPOINT",
                                "CALLBACK_URL",
                                "WEBHOOK_URL",
                                "REDIRECT_URL",
                                "FRONTEND_URL",
                                "BACKEND_URL",
                                "SITE_URL",
                                "HOME_URL",
                                "URL",
                                "HOST",
                            }
                            if key in safe_url_keys:
                                continue
                        if not self.is_safe_value(pattern_type, value):
                            findings.append(
                                (str(file_path), pattern_type, line_num, line.strip())
                            )
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
        return findings

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return result.is_valid


def main():
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(
        description="Check for hardcoded secrets and configuration that should be in .env files"
    )
    parser.add_argument("path", type=str, help="Path to directory or file to check")
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    args = parser.parse_args()

    checker = EnvSecretsValidator()
    path = Path(args.path)

    if not path.exists():
        logger.error(f"Error: Path {path} does not exist")
        return 1

    findings = []
    if path.is_file():
        if checker.should_check_file(path):
            findings = checker.check_file(path)
    else:
        findings = checker.check_directory(path)

    if args.json:
        import json

        json_findings = [
            {"file": f[0], "type": f[1], "line": f[2], "content": f[3]}
            for f in findings
        ]
        print(json.dumps(json_findings, indent=2))
        if findings:
            logger.error("Hardcoded secrets/configuration found.")
        else:
            logger.info("No hardcoded secrets/configuration found.")
    else:
        logger.info("Validation results:")
        logger.info(checker.format_findings(findings))

    # Return non-zero exit code if findings were found
    return 1 if findings else 0


if __name__ == "__main__":
    exit(main())
