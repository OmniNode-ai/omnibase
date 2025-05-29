# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T12:36:28.016122'
# description: Stamped by PythonHandler
# entrypoint: python://test_handler_metadata_enforcement.py
# hash: 4e6253e1f85a6beece110869662b8bd29b66a07bbf6f214af6ed3e71a1a3b1c8
# last_modified_at: '2025-05-29T11:50:12.663437+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: test_handler_metadata_enforcement.py
# namespace: omnibase.test_handler_metadata_enforcement
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 9c5121e9-0307-411a-a9b1-edd64abc21dc
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
CI enforcement tests for handler metadata requirements.

This module contains tests that enforce the requirement that all handlers
implement the metadata properties defined in ProtocolFileTypeHandler.
These tests are designed to run in CI and fail if any handler is missing
required metadata properties.
"""

import ast
import importlib
import inspect
from pathlib import Path
from typing import Any, List, Type

import pytest

from omnibase.protocol.protocol_file_type_handler import ProtocolFileTypeHandler


class HandlerMetadataEnforcer:
    """Utility class to discover and validate handler metadata compliance."""

    REQUIRED_METADATA_PROPERTIES = [
        "handler_name",
        "handler_version",
        "handler_author",
        "handler_description",
        "supported_extensions",
        "supported_filenames",
        "handler_priority",
        "requires_content_analysis",
    ]

    def discover_handler_classes(self) -> List[Type[ProtocolFileTypeHandler]]:
        """
        Discover all classes that implement ProtocolFileTypeHandler.

        Returns:
            List of handler classes found in the codebase
        """
        handler_classes = []

        # Search in known handler locations
        handler_paths = [
            "omnibase.handlers",
            "omnibase.runtimes.onex_runtime.v1_0_0.handlers",
            "omnibase.fixtures.mocks.dummy_handlers",
        ]

        for module_path in handler_paths:
            try:
                module = importlib.import_module(module_path)
                handler_classes.extend(self._find_handlers_in_module(module))
            except ImportError:
                continue

        # Also search for handlers in node-local directories
        src_path = Path("src")
        if src_path.exists():
            for handler_file in src_path.rglob("*handler*.py"):
                if "test" not in str(handler_file) and "__pycache__" not in str(
                    handler_file
                ):
                    handler_classes.extend(self._find_handlers_in_file(handler_file))

        return handler_classes

    def _find_handlers_in_module(
        self, module: Any
    ) -> List[Type[ProtocolFileTypeHandler]]:
        """Find handler classes in a given module."""
        handlers = []

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                obj.__module__ == module.__name__
                and self._implements_protocol(obj, ProtocolFileTypeHandler)
                and name != "ProtocolFileTypeHandler"
            ):
                handlers.append(obj)

        return handlers

    def _find_handlers_in_file(
        self, file_path: Path
    ) -> List[Type[ProtocolFileTypeHandler]]:
        """Find handler classes in a Python file using AST parsing."""
        handlers = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if class has ProtocolFileTypeHandler in bases
                    for base in node.bases:
                        if (
                            isinstance(base, ast.Name)
                            and base.id == "ProtocolFileTypeHandler"
                        ) or (
                            isinstance(base, ast.Attribute)
                            and base.attr == "ProtocolFileTypeHandler"
                        ):
                            # Try to import and get the actual class
                            try:
                                module_path = self._file_path_to_module_path(file_path)
                                module = importlib.import_module(module_path)
                                if hasattr(module, node.name):
                                    cls = getattr(module, node.name)
                                    if self._implements_protocol(
                                        cls, ProtocolFileTypeHandler
                                    ):
                                        handlers.append(cls)
                            except (ImportError, AttributeError):
                                pass

        except (SyntaxError, UnicodeDecodeError):
            pass

        return handlers

    def _file_path_to_module_path(self, file_path: Path) -> str:
        """Convert a file path to a Python module path."""
        # Remove src/ prefix and .py suffix, replace / with .
        path_str = str(file_path)
        if path_str.startswith("src/"):
            path_str = path_str[4:]
        if path_str.endswith(".py"):
            path_str = path_str[:-3]
        return path_str.replace("/", ".")

    def _implements_protocol(self, cls: Type, protocol: Type) -> bool:
        """Check if a class implements a protocol."""
        try:
            # Check if it's a subclass or implements the protocol
            return hasattr(cls, "__mro__") and any(
                base.__name__ == protocol.__name__ for base in cls.__mro__
            )
        except (TypeError, AttributeError):
            return False

    def validate_handler_metadata(
        self, handler_class: Type[ProtocolFileTypeHandler]
    ) -> List[str]:
        """
        Validate that a handler class has all required metadata properties.

        Args:
            handler_class: The handler class to validate

        Returns:
            List of missing or invalid metadata properties
        """
        errors = []

        try:
            # Try to instantiate the handler
            handler = handler_class()
        except Exception as e:
            errors.append(f"Cannot instantiate handler {handler_class.__name__}: {e}")
            return errors

        # Check each required property
        for prop_name in self.REQUIRED_METADATA_PROPERTIES:
            if not hasattr(handler, prop_name):
                errors.append(f"Missing property: {prop_name}")
                continue

            try:
                value = getattr(handler, prop_name)

                # Validate property types
                if prop_name in [
                    "handler_name",
                    "handler_version",
                    "handler_author",
                    "handler_description",
                ]:
                    if not isinstance(value, str) or not value.strip():
                        errors.append(
                            f"Property {prop_name} must be a non-empty string, got: {type(value).__name__}"
                        )
                elif prop_name in ["supported_extensions", "supported_filenames"]:
                    if not isinstance(value, list):
                        errors.append(
                            f"Property {prop_name} must be a list, got: {type(value).__name__}"
                        )
                    elif not all(isinstance(item, str) for item in value):
                        errors.append(f"Property {prop_name} must be a list of strings")
                elif prop_name == "handler_priority":
                    if not isinstance(value, int):
                        errors.append(
                            f"Property {prop_name} must be an integer, got: {type(value).__name__}"
                        )
                elif prop_name == "requires_content_analysis":
                    if not isinstance(value, bool):
                        errors.append(
                            f"Property {prop_name} must be a boolean, got: {type(value).__name__}"
                        )

            except Exception as e:
                errors.append(f"Error accessing property {prop_name}: {e}")

        return errors


class TestHandlerMetadataEnforcement:
    """CI enforcement tests for handler metadata requirements."""

    def test_all_handlers_have_required_metadata(self) -> None:
        """
        CI enforcement test: All handlers must implement required metadata properties.

        This test discovers all handler classes in the codebase and validates that
        they implement all required metadata properties from ProtocolFileTypeHandler.
        """
        enforcer = HandlerMetadataEnforcer()
        handler_classes = enforcer.discover_handler_classes()

        # Ensure we found some handlers
        assert (
            len(handler_classes) > 0
        ), "No handler classes found - discovery may be broken"

        all_errors = {}

        for handler_class in handler_classes:
            errors = enforcer.validate_handler_metadata(handler_class)
            if errors:
                all_errors[handler_class.__name__] = errors

        # If any handlers have errors, fail the test with detailed information
        if all_errors:
            error_msg = "Handler metadata validation failed:\n\n"
            for handler_name, errors in all_errors.items():
                error_msg += f"❌ {handler_name}:\n"
                for error in errors:
                    error_msg += f"   - {error}\n"
                error_msg += "\n"

            error_msg += (
                "All handlers must implement the required metadata properties:\n"
            )
            for prop in HandlerMetadataEnforcer.REQUIRED_METADATA_PROPERTIES:
                error_msg += f"   - {prop}\n"

            pytest.fail(error_msg)

    def test_handler_metadata_property_types(self) -> None:
        """
        CI enforcement test: Handler metadata properties must have correct types.

        This test validates that all metadata properties return the expected types
        and contain valid values.
        """
        enforcer = HandlerMetadataEnforcer()
        handler_classes = enforcer.discover_handler_classes()

        type_errors = {}

        for handler_class in handler_classes:
            try:
                handler = handler_class()
                errors = []

                # Test string properties are non-empty
                for prop in [
                    "handler_name",
                    "handler_version",
                    "handler_author",
                    "handler_description",
                ]:
                    if hasattr(handler, prop):
                        value = getattr(handler, prop)
                        if not isinstance(value, str) or not value.strip():
                            errors.append(f"{prop} must be a non-empty string")

                # Test list properties contain only strings
                for prop in ["supported_extensions", "supported_filenames"]:
                    if hasattr(handler, prop):
                        value = getattr(handler, prop)
                        if not isinstance(value, list):
                            errors.append(f"{prop} must be a list")
                        elif not all(isinstance(item, str) for item in value):
                            errors.append(f"{prop} must contain only strings")

                # Test priority is a valid integer
                if hasattr(handler, "handler_priority"):
                    value = getattr(handler, "handler_priority")
                    if not isinstance(value, int) or value < 0:
                        errors.append("handler_priority must be a non-negative integer")

                # Test requires_content_analysis is boolean
                if hasattr(handler, "requires_content_analysis"):
                    value = getattr(handler, "requires_content_analysis")
                    if not isinstance(value, bool):
                        errors.append("requires_content_analysis must be a boolean")

                if errors:
                    type_errors[handler_class.__name__] = errors

            except Exception as e:
                type_errors[handler_class.__name__] = [
                    f"Error instantiating handler: {e}"
                ]

        if type_errors:
            error_msg = "Handler metadata type validation failed:\n\n"
            for handler_name, errors in type_errors.items():
                error_msg += f"❌ {handler_name}:\n"
                for error in errors:
                    error_msg += f"   - {error}\n"
                error_msg += "\n"

            pytest.fail(error_msg)

    def test_handler_discovery_finds_known_handlers(self) -> None:
        """
        Sanity test: Ensure handler discovery finds known handlers.

        This test validates that our discovery mechanism is working by checking
        that it finds handlers we know should exist.
        """
        enforcer = HandlerMetadataEnforcer()
        handler_classes = enforcer.discover_handler_classes()

        handler_names = [cls.__name__ for cls in handler_classes]

        # Check for known handlers
        expected_handlers = [
            "PythonHandler",
            "MarkdownHandler",
            "MetadataYAMLHandler",
            "IgnoreFileHandler",
        ]

        missing_handlers = []
        for expected in expected_handlers:
            if expected not in handler_names:
                missing_handlers.append(expected)

        if missing_handlers:
            pytest.fail(
                f"Handler discovery failed to find known handlers: {missing_handlers}\n"
                f"Found handlers: {handler_names}"
            )
