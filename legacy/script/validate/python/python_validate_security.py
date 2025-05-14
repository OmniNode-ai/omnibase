#!/usr/bin/env python3

# === OmniNode:Tool_Metadata ===
# metadata_version: "0.1"
# schema_version: "1.0.0"
# name: "python_validate_security"
# namespace: "omninode.tools.python_validate_security"
# meta_type: "model"
# version: "0.1.0"
# author: "OmniNode Team"
# owner: "jonah@omninode.ai"
# copyright: "Copyright (c) 2025 OmniNode.ai"
# created_at: "2025-05-05T12:44:02+00:00"
# last_modified_at: "2025-05-05T12:44:02+00:00"
# entrypoint: "python_validate_security.py"
# protocols_supported: ["O.N.E. v0.1"]
# protocol_class: ['ProtocolValidate']
# base_class: ['ProtocolValidate']
# mock_safe: true
# === /OmniNode:Tool_Metadata ===

"""validate_security.py
containers.foundation.src.foundation.script.validate.validate_security.

Module that handles functionality for the OmniNode platform.

Provides core interfaces and validation logic.
"""

import ast
import re
from pathlib import Path

from foundation.protocol.protocol_validate import ProtocolValidate
from foundation.model.model_validate import ValidationResult, ValidatorMetadata
from foundation.script.validate.common.common_file_utils import find_files


class SecurityValidator(ProtocolValidate):
    """Validates security practices and requirements."""

    @classmethod
    def metadata(cls) -> ValidatorMetadata:
        return ValidatorMetadata(
            name="security",
            group="security",
            description="Validates security practices including AI model security, secrets management, API security, and data protection.",
            version="v1",
        )

    def get_name(self) -> str:
        """Get the validator name."""
        return "security"

    def validate(self, target: Path, config: dict = None):
        # Get rules from config
        rules = (
            self.config.get("rules", {})
            if hasattr(self, "config") and self.config
            else {}
        )
        python_files = find_files(
            target,
            pattern="*.py",
            ignore_patterns=["**/__pycache__/**", "**/tests/**", "**/venv/**"],
        )
        if not python_files:
            self.add_error(
                message="No Python files found", file=str(target), type="error"
            )
            return ValidationResult(
                is_valid=False, errors=self.errors, warnings=self.warnings, version="v1"
            )
        for file in python_files:
            file_failed = False
            try:
                with open(file) as f:
                    content = f.read()
                tree = ast.parse(content)
                # Validate banned functions
                if not self._validate_banned_functions(tree, file):
                    file_failed = True
                # Validate secrets management
                if not self._validate_secrets_management(tree, content, file):
                    file_failed = True
                # Validate AI model security
                if not self._validate_ai_security(tree, content, file):
                    file_failed = True
                # Validate API security
                if not self._validate_api_security(tree, content, file):
                    file_failed = True
                # Validate data protection
                if not self._validate_data_protection(tree, content, file):
                    file_failed = True
            except Exception as e:
                self.add_error(
                    message=f"Failed to analyze {file.name}: {e}",
                    file=str(file),
                    type="error",
                )
                file_failed = True
            if file_failed:
                self.add_failed_file(str(file))
        return ValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            version="v1",
        )

    def _validate_banned_functions(self, tree: ast.AST, file: Path) -> bool:
        """Validate that banned functions are not used."""
        is_valid = True
        banned_functions = {
            "eval": "Use of eval() is prohibited for security reasons",
            "exec": "Use of exec() is prohibited for security reasons",
            "os.system": "Use subprocess module instead of os.system",
            "subprocess.call": "Use subprocess.run with check=True instead",
            "subprocess.Popen": "Use subprocess.run with appropriate security flags",
        }

        def get_full_attr_name(attr):
            parts = []
            while isinstance(attr, ast.Attribute):
                parts.append(attr.attr)
                attr = attr.value
            if isinstance(attr, ast.Name):
                parts.append(attr.id)
            return list(reversed(parts))

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in banned_functions:
                        self.add_error(
                            message=banned_functions[func_name],
                            file=str(file),
                            line=node.lineno,
                            type="error",
                        )
                        return False
                elif isinstance(node.func, ast.Attribute):
                    parts = get_full_attr_name(node.func)
                    # Check for exact match or last two parts match (e.g., *.subprocess.call)
                    for banned in banned_functions:
                        banned_parts = banned.split(".")
                        if (
                            len(parts) >= len(banned_parts)
                            and parts[-len(banned_parts) :] == banned_parts
                        ):
                            self.add_error(
                                message=banned_functions[banned],
                                file=str(file),
                                line=node.lineno,
                                type="error",
                            )
                            return False
        return True

    def _validate_secrets_management(
        self, tree: ast.AST, content: str, file: Path
    ) -> bool:
        """Validate secrets management practices."""
        is_valid = True

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]',
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
        ]

        for pattern in secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                self.add_error(
                    message="Hardcoded secret detected",
                    file=str(file),
                    line=content[: match.start()].count("\n") + 1,
                    details={"pattern": pattern},
                    type="error",
                )
                return False

        return True

    def _validate_ai_security(self, tree: ast.AST, content: str, file: Path) -> bool:
        """Validate AI model security practices."""
        is_valid = True
        input_validation_required = [
            "predict",
            "generate",
            "create_embedding",
            "create_completion",
        ]
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Detect both direct calls (predict(x)) and attribute calls (model.predict(x))
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                if func_name in input_validation_required:
                    parent_func = self._find_enclosing_function(node, tree)
                    if parent_func and not self._function_has_input_validation(
                        parent_func
                    ):
                        self.add_error(
                            message=f"Missing input validation for AI model call: {func_name}",
                            file=str(file),
                            line=node.lineno,
                            type="error",
                        )
                        return False
        return True

    def _find_enclosing_function(self, node, tree):
        # Find the enclosing function definition for a node
        for parent in ast.walk(tree):
            if isinstance(parent, ast.FunctionDef):
                if node in ast.walk(parent):
                    return parent
        return None

    def _function_has_input_validation(self, func_node):
        # Look for isinstance, type, or raise ValueError for input
        for n in ast.walk(func_node):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if n.func.id in {"isinstance", "issubclass", "type"}:
                    return True
            if isinstance(n, ast.Raise):
                if isinstance(n.exc, ast.Call) and isinstance(n.exc.func, ast.Name):
                    if n.exc.func.id == "ValueError":
                        return True
        return False

    def _validate_api_security(self, tree: ast.AST, content: str, file: Path) -> bool:
        """Validate API security practices."""
        is_valid = True
        auth_decorators = {
            "requires_auth",
            "login_required",
            "authenticated",
            "requires_token",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self._is_api_endpoint(node):
                    has_auth = False
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name):
                            if decorator.id in auth_decorators:
                                has_auth = True
                                break
                        elif isinstance(decorator, ast.Attribute):
                            if decorator.attr in auth_decorators:
                                has_auth = True
                                break
                        elif isinstance(decorator, ast.Call):
                            # Handle decorator calls like @router.get(..)
                            if isinstance(decorator.func, ast.Attribute):
                                if decorator.func.attr in {
                                    "get",
                                    "post",
                                    "put",
                                    "delete",
                                    "route",
                                }:
                                    # Still need to check for auth decorator in the list
                                    continue
                    if not has_auth:
                        self.add_error(
                            message="API endpoint missing authentication decorator",
                            file=str(file),
                            line=node.lineno,
                            type="error",
                        )
                        return False
        return True

    def _validate_data_protection(
        self, tree: ast.AST, content: str, file: Path
    ) -> bool:
        """Validate data protection practices."""
        is_valid = True
        # Look for open(.., 'w') or open(.., 'wb') without encryption
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "open"
            ):
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Str):
                    mode = node.args[1].s
                    if "w" in mode:
                        # Check if encryption is used in the function
                        parent_func = self._find_enclosing_function(node, tree)
                        if parent_func and not self._function_has_encryption(
                            parent_func
                        ):
                            self.add_error(
                                message="Missing encryption for file write operation",
                                file=str(file),
                                line=node.lineno,
                                type="error",
                            )
                            return False
        return True

    def _function_has_encryption(self, func_node):
        # Look for encrypt or encrypt_data call in the function
        for n in ast.walk(func_node):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if n.func.id in {"encrypt", "encrypt_data"}:
                    return True
        return False

    def _is_api_endpoint(self, node: ast.FunctionDef) -> bool:
        """Check if a function is an API endpoint."""
        for decorator in node.decorator_list:
            # Direct decorator call: @router.get(..)
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr in {"get", "post", "put", "delete", "route"}:
                        return True
            # Direct decorator: @get, @post, etc.
            if isinstance(decorator, ast.Name):
                if decorator.id in {"get", "post", "put", "delete", "route"}:
                    return True
        return False

    def _validate(self, target: Path) -> bool:
        result = self.validate(target)
        return (
            result.get("is_valid")
            if isinstance(result, dict)
            else getattr(result, "is_valid", False)
        )