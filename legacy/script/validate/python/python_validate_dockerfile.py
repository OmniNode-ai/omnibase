#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: 0.1
# name: validate_dockerfile
# namespace: omninode.tools.validate_dockerfile
# version: 0.1.0
# author: OmniNode Team
# copyright: Copyright (c) 2025 OmniNode.ai
# created_at: 2025-04-27T18:13:00+00:00
# last_modified_at: 2025-04-27T18:13:00+00:00
# entrypoint: validate_dockerfile.py
# protocols_supported: ["O.N.E. v0.1"]
# === /OmniNode:Tool_Metadata ===

"""validate_dockerfile.py
containers.foundation.src.foundation.script.validate.validate_dockerfile.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import (
    ValidationIssue,
    ValidationResult,
    ValidatorConfig,
    ValidatorMetadata,
)
from foundation.script.validate.validate_registry import ValidatorRegistry


class DockerfileValidatorConfig(ValidatorConfig):
    version: str = "1.0.0"
    required_env_vars: List[str] = [
        "PYTHONUNBUFFERED",
        "PYTHONDONTWRITEBYTECODE",
        "POETRY_VERSION",
        "POETRY_HOME",
        "POETRY_VIRTUALENVS_IN_PROJECT",
        "POETRY_NO_INTERACTION",
        "PYSETUP_PATH",
        "VENV_PATH",
    ]
    required_labels: List[str] = ["maintainer", "version", "description"]
    base_image_prefix: str = "python:3.11"


class DockerfileValidationResult(ValidationResult):
    pass


class DockerfileValidator(ProtocolValidate):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.config = DockerfileValidatorConfig(**(config or {}))

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="dockerfile",
            group="container",
            description="Validates Dockerfile for OmniNode platform compliance.",
        )

    def validate(
        self, target: Path, config: Optional[ValidatorConfig] = None
    ) -> DockerfileValidationResult:
        self.errors.clear()
        self.warnings.clear()
        is_valid = True
        try:
            if not target.is_file():
                self.errors.append(
                    ValidationIssue(
                        message=f"Dockerfile not found: {target}",
                        file=str(target),
                        type="error",
                    )
                )
                is_valid = False
                return DockerfileValidationResult(
                    is_valid=is_valid, errors=self.errors, warnings=self.warnings
                )
            with open(target) as f:
                content = f.read()
            instructions = self.parse_dockerfile(content)
            # Run all checks (errors)
            for check_func in [
                self.check_base_image,
                self.check_environment_variables,
                self.check_poetry_installation,
                self.check_dependencies_installation,
                self.check_healthcheck,
                self.check_labels,
                self.check_multi_stage_build,
                self.check_system_cleanup,
                self.check_non_root_user,
                self.check_base_image_pinning,
                self.check_standardized_copy,
                self.check_env_secrets_and_ports,
            ]:
                errors = check_func(instructions)
                if errors:
                    for err in errors:
                        self.errors.append(
                            ValidationIssue(message=err, file=str(target), type="error")
                        )
                    is_valid = False
            # Run warnings
            warnings = self.check_warnings(instructions)
            for warn in warnings:
                self.warnings.append(
                    ValidationIssue(message=warn, file=str(target), type="warning")
                )
        except Exception as e:
            self.errors.append(
                ValidationIssue(
                    message=f"Validation failed: {str(e)}",
                    file=str(target),
                    type="error",
                )
            )
            is_valid = False
        return DockerfileValidationResult(
            is_valid=is_valid, errors=self.errors, warnings=self.warnings
        )

    @staticmethod
    def parse_dockerfile(content: str) -> List[Tuple[str, str]]:
        instructions = []
        current_instruction = None
        current_args = []
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith("\\"):
                if current_instruction is None:
                    instruction, arg = line.split(None, 1)
                    current_instruction = instruction
                    current_args = [arg.rstrip("\\").strip()]
                else:
                    current_args.append(line.rstrip("\\").strip())
            else:
                if current_instruction is not None:
                    current_args.append(line)
                    instructions.append((current_instruction, " ".join(current_args)))
                    current_instruction = None
                    current_args = []
                else:
                    instruction, arg = line.split(None, 1)
                    instructions.append((instruction, arg))
        return instructions

    def check_base_image(self, instructions: List[Tuple[str, str]]) -> List[str]:
        errors = []
        if not instructions or instructions[0][0] != "FROM":
            errors.append("Dockerfile must start with FROM instruction")
            return errors
        base_image = instructions[0][1]
        if not base_image.startswith(self.config.base_image_prefix):
            errors.append(f"Base image must be {self.config.base_image_prefix}")
        return errors

    def check_environment_variables(
        self, instructions: List[Tuple[str, str]]
    ) -> List[str]:
        errors = []
        required_env_vars = set(self.config.required_env_vars)
        found_env_vars = set()
        for instruction, args in instructions:
            if instruction == "ENV":
                # Split on backslashes for multi-line ENV
                env_lines = args.replace("\\", "\n").split("\n")
                for env_line in env_lines:
                    env_line = env_line.strip()
                    if not env_line:
                        continue
                    # Split line into key=value pairs (can be multiple per line)
                    for pair in env_line.split():
                        if "=" in pair:
                            key = pair.split("=", 1)[0].strip()
                            found_env_vars.add(key)
                        else:
                            # Handle KEY VALUE (rare, but possible)
                            key = pair.strip()
                            found_env_vars.add(key)
        for var in required_env_vars:
            if var not in found_env_vars:
                errors.append(f"Missing required environment variable: {var}")
        return errors

    def check_poetry_installation(
        self, instructions: List[Tuple[str, str]]
    ) -> List[str]:
        errors = []
        poetry_install_found = any(
            instruction == "RUN"
            and "curl -sSL https://install.python-poetry.org" in args
            for instruction, args in instructions
        )
        if not poetry_install_found:
            errors.append("Poetry installation command not found")
        return errors

    def check_dependencies_installation(
        self, instructions: List[Tuple[str, str]]
    ) -> List[str]:
        errors = []
        poetry_install_found = False
        copy_requirements_found = False
        for instruction, args in instructions:
            if (
                instruction == "COPY"
                and "pyproject.toml" in args
                and "poetry.lock" in args
            ):
                copy_requirements_found = True
            elif instruction == "RUN" and "poetry install" in args:
                poetry_install_found = True
        if not copy_requirements_found:
            errors.append("Must copy pyproject.toml and poetry.lock files")
        if not poetry_install_found:
            errors.append("Must install dependencies using poetry install")
        return errors

    def check_healthcheck(self, instructions: List[Tuple[str, str]]) -> List[str]:
        errors = []
        healthcheck_found = False
        for instruction, args in instructions:
            if instruction == "HEALTHCHECK":
                healthcheck_found = True
                if (
                    "--interval" not in args
                    or "--timeout" not in args
                    or "--retries" not in args
                ):
                    errors.append(
                        "Healthcheck must specify interval, timeout, and retries"
                    )
                break
        if not healthcheck_found:
            errors.append("Healthcheck configuration not found")
        return errors

    def check_labels(self, instructions: List[Tuple[str, str]]) -> List[str]:
        errors = []
        required_labels = set(self.config.required_labels)
        found_labels = set()
        for instruction, args in instructions:
            if instruction == "LABEL":
                for label in args.split():
                    if "=" in label:
                        found_labels.add(label.split("=")[0].strip())
        for label in required_labels:
            if label not in found_labels:
                errors.append(f"Missing required label: {label}")
        return errors

    def check_multi_stage_build(self, instructions: List[Tuple[str, str]]) -> List[str]:
        errors = []
        from_count = sum(1 for instr, _ in instructions if instr == "FROM")
        if from_count < 2:
            errors.append(
                "Dockerfile should use a multi-stage build (at least two FROM statements)"
            )
        return errors

    def check_system_cleanup(self, instructions: List[Tuple[str, str]]) -> List[str]:
        errors = []
        found_cleanup = any(
            instr == "RUN"
            and ("rm -rf /var/lib/apt/lists/*" in args or "apt-get clean" in args)
            for instr, args in instructions
        )
        if not found_cleanup:
            errors.append(
                "Dockerfile must clean up apt cache with 'rm -rf /var/lib/apt/lists/*' after apt-get install"
            )
        return errors

    def check_non_root_user(self, instructions: List[Tuple[str, str]]) -> List[str]:
        errors = []
        found_user = any(
            instr == "USER" and args.strip() != "root" for instr, args in instructions
        )
        if not found_user:
            errors.append("Dockerfile must specify a non-root USER in the final image")
        return errors

    def check_base_image_pinning(
        self, instructions: List[Tuple[str, str]]
    ) -> List[str]:
        errors = []
        for instr, args in instructions:
            if instr == "FROM":
                if ":" not in args or any(
                    tag in args for tag in [":latest", ":3.11-slim", ":slim"]
                ):
                    errors.append(
                        f"Base image should be pinned to a specific version, not floating: {args}"
                    )
        return errors

    def check_standardized_copy(self, instructions: List[Tuple[str, str]]) -> List[str]:
        errors = []
        found_src = any(
            instr == "COPY" and ("src/" in args or "./src/" in args)
            for instr, args in instructions
        )
        found_pyproject = any(
            instr == "COPY" and ("pyproject.toml" in args and "poetry.lock" in args)
            for instr, args in instructions
        )
        if not found_src:
            errors.append(
                "Dockerfile must copy source code to a standardized location (e.g., /app/src)"
            )
        if not found_pyproject:
            errors.append(
                "Dockerfile must copy pyproject.toml and poetry.lock to a standardized location (e.g., /app)"
            )
        return errors

    def check_env_secrets_and_ports(
        self, instructions: List[Tuple[str, str]]
    ) -> List[str]:
        errors = []
        secret_patterns = [
            re.compile(r"(secret|token|password|api[_-]?key)", re.IGNORECASE),
            re.compile(r"(AKIA[0-9A-Z]{16})"),  # AWS Access Key ID
            re.compile(r"(AIza[0-9A-Za-z\-_]{35})"),  # Google API Key
        ]
        ip_pattern = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
        # Only flag port numbers that are 4 or 5 digits (likely to be actual ports)
        port_pattern = re.compile(r"\b([0-9]{4,5})\b")
        # Hostname: must not be part of an email address
        hostname_pattern = re.compile(r"\b([a-zA-Z0-9\-]+\.[a-zA-Z]{2,})\b")
        email_pattern = re.compile(
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        )
        for instr, args in instructions:
            if instr in {"ENV", "ARG", "LABEL"}:
                lines = args.replace("\\", "\n").split("\n")
                for line in lines:
                    line = line.strip()
                    if not line or ("=" not in line and instr != "ARG"):
                        continue
                    if instr == "ARG" and "=" not in line:
                        key = line
                        value = ""
                    else:
                        key, value = line.split("=", 1)
                    value = value.strip('"')
                    # Check for secrets
                    for pat in secret_patterns:
                        if pat.search(key) or pat.search(value):
                            errors.append(
                                f"Potential secret/token/password/API key found in {instr}: {key}"
                            )
                    # Check for hardcoded IP addresses
                    if ip_pattern.search(value):
                        errors.append(
                            f"Hardcoded IP address found in {instr} {key}: {value}"
                        )
                    # Check for hardcoded port numbers (only 4 or 5 digits)
                    for match in port_pattern.findall(value):
                        if match not in {"8000", "8080", "5432", "6379"}:
                            errors.append(
                                f"Hardcoded port number found in {instr} {key}: {value}"
                            )
                    # Check for hardcoded hostnames (not part of email, not maintainer label)
                    if (
                        hostname_pattern.search(value)
                        and not email_pattern.search(value)
                        and key.lower() not in {"maintainer"}
                    ):
                        errors.append(
                            f"Hardcoded hostname found in {instr} {key}: {value}"
                        )
        return errors

    def check_warnings(self, instructions: List[Tuple[str, str]]) -> List[str]:
        warnings = []
        # 1. PYTHONPATH set if using non-standard source directory
        pythonpath_set = any(
            instr == "ENV" and "PYTHONPATH" in args for instr, args in instructions
        )
        src_copied = any(
            instr == "COPY" and ("src/" in args or "./src/" in args)
            for instr, args in instructions
        )
        if src_copied and not pythonpath_set:
            warnings.append(
                "PYTHONPATH not set for non-standard source directory (src/)"
            )
        # 2. Entrypoint/production server for Python web apps
        entrypoint_found = any(
            instr in {"CMD", "ENTRYPOINT"} for instr, _ in instructions
        )
        if not entrypoint_found:
            warnings.append(
                "No CMD or ENTRYPOINT found; production server may not be configured"
            )
        # 3. Layer ordering for cache efficiency (copy dependencies before source)
        copy_pyproject_idx = next(
            (
                i
                for i, (instr, args) in enumerate(instructions)
                if instr == "COPY" and "pyproject.toml" in args
            ),
            None,
        )
        copy_src_idx = next(
            (
                i
                for i, (instr, args) in enumerate(instructions)
                if instr == "COPY" and ("src/" in args or "./src/" in args)
            ),
            None,
        )
        if (
            copy_pyproject_idx is not None
            and copy_src_idx is not None
            and copy_src_idx < copy_pyproject_idx
        ):
            warnings.append(
                "Source code copied before dependencies; consider copying dependencies first for better cache efficiency"
            )
        # 4. Use .dockerignore to exclude unnecessary files (cannot check file existence here, recommend)
        warnings.append(
            "Ensure .dockerignore is present to exclude unnecessary files (manual check)"
        )
        # 5. Avoid root-owned files in final image (cannot check at build time, recommend)
        warnings.append("Avoid root-owned files in final image (manual check)")
        # 6. Use COPY --chown for non-root images
        non_root_user = any(
            instr == "USER" and args.strip() != "root" for instr, args in instructions
        )
        copy_chown = any(
            instr == "COPY" and "--chown" in args for instr, args in instructions
        )
        if non_root_user and not copy_chown:
            warnings.append(
                "COPY --chown not used with non-root USER; consider using it to avoid root-owned files"
            )
        # 7. Avoid ADD unless necessary
        add_found = any(instr == "ADD" for instr, _ in instructions)
        if add_found:
            warnings.append(
                "ADD used instead of COPY; prefer COPY unless ADD is required"
            )
        # 8. Avoid apt-get upgrade
        upgrade_found = any(
            instr == "RUN" and "apt-get upgrade" in args for instr, args in instructions
        )
        if upgrade_found:
            warnings.append(
                "apt-get upgrade used; avoid upgrading base image in Dockerfile"
            )
        # 9. Expose only necessary ports (warn if more than one, unless justified)
        exposed_ports = [args for instr, args in instructions if instr == "EXPOSE"]
        if len(exposed_ports) > 1:
            warnings.append(
                f"Multiple ports exposed: {', '.join(exposed_ports)}; expose only necessary ports"
            )
        # 10. Use CMD/ENTRYPOINT appropriately (already checked above)
        # 11. Use reproducible install commands
        pip_install = any(
            instr == "RUN" and "pip install" in args for instr, args in instructions
        )
        poetry_install = any(
            instr == "RUN" and "poetry install" in args for instr, args in instructions
        )
        if pip_install and not any(
            "--no-cache-dir" in args for instr, args in instructions if instr == "RUN"
        ):
            warnings.append("pip install should use --no-cache-dir for reproducibility")
        if poetry_install and not any(
            "--no-interaction" in args and "--no-ansi" in args
            for instr, args in instructions
            if instr == "RUN"
        ):
            warnings.append(
                "poetry install should use --no-interaction --no-ansi for reproducibility"
            )
        return warnings

    def _validate(self, target: Path) -> bool:
        # Use the same logic as the validate method, but return True/False
        result = self.validate(target)
        return result.is_valid

    def get_name(self) -> str:
        return "dockerfile"


# Register the validator
ValidatorRegistry().register(
    name="dockerfile",
    version="1.0.0",
    validator_cls=DockerfileValidator,
    meta={
        "name": "dockerfile",
        "version": "1.0.0",
        "group": "container",
        "description": "Validates Dockerfile for OmniNode platform compliance.",
    },
)
