# === OmniNode:Metadata ===
# metadata_version: 0.1.0
# protocol_version: 1.1.0
# owner: OmniNode Team
# copyright: OmniNode Team
# schema_version: 1.1.0
# name: function_discovery.py
# version: 1.0.0
# uuid: 0f5ef0c1-f5cc-4a44-92e0-5f529fd28040
# author: OmniNode Team
# created_at: 2025-05-26T08:32:26.686429
# last_modified_at: 2025-05-26T13:52:12.278762
# description: Stamped by PythonHandler
# state_contract: state_contract://default
# lifecycle: active
# hash: d40e95c5f1588e98b347633bb95a4995703ffe81286ea78e8fcbe3cfe4548732
# entrypoint: python@function_discovery.py
# runtime_language_hint: python>=3.11
# namespace: onex.stamped.function_discovery
# meta_type: tool
# === /OmniNode:Metadata ===


"""
Language-agnostic function discovery utilities for the unified tools approach.
Supports parsing functions from multiple programming languages and extracting
metadata for inclusion in ONEX metadata blocks.
"""

import ast
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

from omnibase.enums import FunctionLanguageEnum
from omnibase.model.model_node_metadata import FunctionTool

logger = logging.getLogger(__name__)


class BaseFunctionDiscoverer(ABC):
    """
    Base class for language-specific function discoverers.

    Uses ABC because:
    - Provides shared logic (_extract_onex_marker method)
    - Internal inheritance pattern within core codebase
    - Subclasses use super() semantics for shared functionality
    """

    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """List of supported language identifiers."""
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """List of supported file extensions."""
        pass

    def can_handle_language(self, language: str) -> bool:
        """Check if this discoverer can handle the specified language."""
        return language.lower() in [lang.lower() for lang in self.supported_languages]

    def can_handle_extension(self, extension: str) -> bool:
        """Check if this discoverer can handle the specified file extension."""
        return extension.lower() in [ext.lower() for ext in self.supported_extensions]

    @abstractmethod
    def discover_functions(
        self, content: str, file_path: Optional[Path] = None
    ) -> Dict[str, FunctionTool]:
        """Discover functions in the given content and return function tools."""
        pass

    def _extract_onex_marker(self, docstring: Optional[str]) -> bool:
        """Check if function has ONEX marker indicating it should be stamped."""
        if not docstring:
            return False

        # Look for @onex:function or @onex_function as standalone annotations
        # Split by lines and check each line for the marker at the beginning (after whitespace)
        for line in docstring.split("\n"):
            line = line.strip()
            if line.startswith("@onex:function") or line.startswith("@onex_function"):
                return True

        return False


class PythonFunctionDiscoverer(BaseFunctionDiscoverer):
    """Function discoverer for Python files using AST parsing."""

    @property
    def supported_languages(self) -> List[str]:
        return ["python", "py"]

    @property
    def supported_extensions(self) -> List[str]:
        return [".py", ".pyx"]

    def discover_functions(
        self, content: str, file_path: Optional[Path] = None
    ) -> Dict[str, FunctionTool]:
        """Discover Python functions using AST parsing."""
        functions: dict[str, FunctionTool] = {}

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"Failed to parse Python content: {e}")
            return functions

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extract function metadata
                func_name = node.name
                line_number = node.lineno

                # Extract docstring
                docstring = ast.get_docstring(node)

                # Only include functions with ONEX marker (opt-in)
                if not self._extract_onex_marker(docstring):
                    continue

                # Extract description from docstring
                description = self._extract_description(docstring)

                # Extract type hints for inputs and outputs
                inputs = self._extract_inputs(node)
                outputs = self._extract_outputs(node)

                # Extract error codes and side effects from docstring
                error_codes = self._extract_error_codes(docstring)
                side_effects = self._extract_side_effects(docstring)

                function_tool = FunctionTool(
                    type="function",
                    language=FunctionLanguageEnum.PYTHON,
                    line=line_number,
                    description=description,
                    inputs=inputs,
                    outputs=outputs,
                    error_codes=error_codes,
                    side_effects=side_effects,
                )

                functions[func_name] = function_tool

        return functions

    def _extract_description(self, docstring: Optional[str]) -> str:
        """Extract description from docstring."""
        if not docstring:
            return "No description available"

        # Take first line or paragraph as description
        lines = docstring.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("@"):
                return line

        return "No description available"

    def _extract_inputs(self, node: ast.FunctionDef) -> List[str]:
        """Extract input parameters with type hints."""
        inputs = []

        for arg in node.args.args:
            if arg.arg == "self":  # Skip self parameter
                continue

            param_str = arg.arg

            # Add type annotation if available
            if arg.annotation:
                type_str = ast.unparse(arg.annotation)
                param_str += f": {type_str}"

            inputs.append(param_str)

        return inputs

    def _extract_outputs(self, node: ast.FunctionDef) -> List[str]:
        """Extract return type hints."""
        outputs = []

        if node.returns:
            return_type = ast.unparse(node.returns)
            outputs.append(return_type)

        return outputs

    def _extract_error_codes(self, docstring: Optional[str]) -> List[str]:
        """Extract error codes from docstring."""
        if not docstring:
            return []

        error_codes = []

        # Look for @raises or @error patterns
        for line in docstring.split("\n"):
            line = line.strip()
            if line.startswith("@raises") or line.startswith("@error"):
                # Extract error code from line
                parts = line.split()
                if len(parts) > 1:
                    error_codes.append(parts[1])

        return error_codes

    def _extract_side_effects(self, docstring: Optional[str]) -> List[str]:
        """Extract side effects from docstring."""
        if not docstring:
            return []

        side_effects = []

        # Look for @side_effect or @effects patterns
        for line in docstring.split("\n"):
            line = line.strip()
            if line.startswith("@side_effect") or line.startswith("@effects"):
                # Extract side effect description
                parts = line.split(maxsplit=1)
                if len(parts) > 1:
                    side_effects.append(parts[1])

        return side_effects


class JavaScriptFunctionDiscoverer(BaseFunctionDiscoverer):
    """Function discoverer for JavaScript/TypeScript files using regex parsing."""

    @property
    def supported_languages(self) -> List[str]:
        return ["javascript", "typescript", "js", "ts"]

    @property
    def supported_extensions(self) -> List[str]:
        return [".js", ".ts", ".jsx", ".tsx"]

    def discover_functions(
        self, content: str, file_path: Optional[Path] = None
    ) -> Dict[str, FunctionTool]:
        """Discover JavaScript/TypeScript functions using regex parsing."""
        functions: dict[str, FunctionTool] = {}

        # Regex patterns for different function declarations
        patterns = [
            # function name() {}
            r"function\s+(\w+)\s*\([^)]*\)\s*{",
            # const name = function() {}
            r"const\s+(\w+)\s*=\s*function\s*\([^)]*\)\s*{",
            # const name = () => {}
            r"const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{",
            # name: function() {}
            r"(\w+)\s*:\s*function\s*\([^)]*\)\s*{",
        ]

        lines = content.split("\n")

        for i, line in enumerate(lines):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    line_number = i + 1

                    # Look for JSDoc comment above function
                    jsdoc = self._extract_jsdoc(lines, i)

                    # Only include functions with ONEX marker (opt-in)
                    if not self._extract_onex_marker(jsdoc):
                        continue

                    # Extract metadata from JSDoc
                    description = self._extract_js_description(jsdoc)
                    inputs = self._extract_js_inputs(jsdoc, line)
                    outputs = self._extract_js_outputs(jsdoc)
                    error_codes = self._extract_js_error_codes(jsdoc)
                    side_effects = self._extract_js_side_effects(jsdoc)

                    # Determine language (js vs ts)
                    language = (
                        FunctionLanguageEnum.TYPESCRIPT
                        if file_path and file_path.suffix in [".ts", ".tsx"]
                        else FunctionLanguageEnum.JAVASCRIPT
                    )

                    function_tool = FunctionTool(
                        type="function",
                        language=language,
                        line=line_number,
                        description=description,
                        inputs=inputs,
                        outputs=outputs,
                        error_codes=error_codes,
                        side_effects=side_effects,
                    )

                    functions[func_name] = function_tool

        return functions

    def _extract_jsdoc(self, lines: List[str], func_line: int) -> Optional[str]:
        """Extract JSDoc comment above function."""
        jsdoc_lines: list[str] = []

        # Look backwards for JSDoc comment
        for i in range(func_line - 1, -1, -1):
            line = lines[i].strip()
            if line.endswith("*/"):
                jsdoc_lines.insert(0, line)
                break
            elif line.startswith("*") or line.startswith("/**"):
                jsdoc_lines.insert(0, line)
            elif not line:
                continue
            else:
                break

        return "\n".join(jsdoc_lines) if jsdoc_lines else None

    def _extract_js_description(self, jsdoc: Optional[str]) -> str:
        """Extract description from JSDoc."""
        if not jsdoc:
            return "No description available"

        lines = jsdoc.split("\n")
        for line in lines:
            line = line.strip().lstrip("*").strip()
            if line and not line.startswith("@"):
                return line

        return "No description available"

    def _extract_js_inputs(self, jsdoc: Optional[str], func_line: str) -> List[str]:
        """Extract input parameters from JSDoc and function signature."""
        inputs = []

        if jsdoc:
            # Extract @param annotations
            for line in jsdoc.split("\n"):
                line = line.strip().lstrip("*").strip()
                if line.startswith("@param"):
                    # Parse @param {type} name description
                    match = re.match(r"@param\s+\{([^}]+)\}\s+(\w+)", line)
                    if match:
                        param_type, param_name = match.groups()
                        inputs.append(f"{param_name}: {param_type}")

        return inputs

    def _extract_js_outputs(self, jsdoc: Optional[str]) -> List[str]:
        """Extract return type from JSDoc."""
        if not jsdoc:
            return []

        for line in jsdoc.split("\n"):
            line = line.strip().lstrip("*").strip()
            if line.startswith("@returns") or line.startswith("@return"):
                # Parse @returns {type} description
                match = re.match(r"@returns?\s+\{([^}]+)\}", line)
                if match:
                    return [match.group(1)]

        return []

    def _extract_js_error_codes(self, jsdoc: Optional[str]) -> List[str]:
        """Extract error codes from JSDoc."""
        if not jsdoc:
            return []

        error_codes = []
        for line in jsdoc.split("\n"):
            line = line.strip().lstrip("*").strip()
            if line.startswith("@throws") or line.startswith("@error"):
                parts = line.split()
                if len(parts) > 1:
                    error_codes.append(parts[1])

        return error_codes

    def _extract_js_side_effects(self, jsdoc: Optional[str]) -> List[str]:
        """Extract side effects from JSDoc."""
        if not jsdoc:
            return []

        side_effects = []
        for line in jsdoc.split("\n"):
            line = line.strip().lstrip("*").strip()
            if line.startswith("@side_effect") or line.startswith("@effects"):
                parts = line.split(maxsplit=1)
                if len(parts) > 1:
                    side_effects.append(parts[1])

        return side_effects


class BashFunctionDiscoverer(BaseFunctionDiscoverer):
    """Function discoverer for Bash/Shell scripts using regex parsing."""

    @property
    def supported_languages(self) -> List[str]:
        return ["bash", "shell", "sh"]

    @property
    def supported_extensions(self) -> List[str]:
        return [".sh", ".bash"]

    def discover_functions(
        self, content: str, file_path: Optional[Path] = None
    ) -> Dict[str, FunctionTool]:
        """Discover Bash functions using regex parsing."""
        functions: dict[str, FunctionTool] = {}

        # Regex patterns for bash function declarations
        patterns = [
            # function name() { ... }
            r"function\s+(\w+)\s*\(\)\s*{",
            # name() { ... }
            r"^(\w+)\s*\(\)\s*{",
        ]

        lines = content.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    line_number = i + 1

                    # Look for comment block above function
                    comments = self._extract_bash_comments(lines, i)

                    # Only include functions with ONEX marker (opt-in)
                    if not self._extract_onex_marker(comments):
                        continue

                    # Extract metadata from comments
                    description = self._extract_bash_description(comments)
                    inputs = self._extract_bash_inputs(comments)
                    outputs = self._extract_bash_outputs(comments)
                    error_codes = self._extract_bash_error_codes(comments)
                    side_effects = self._extract_bash_side_effects(comments)

                    function_tool = FunctionTool(
                        type="function",
                        language=FunctionLanguageEnum.BASH,
                        line=line_number,
                        description=description,
                        inputs=inputs,
                        outputs=outputs,
                        error_codes=error_codes,
                        side_effects=side_effects,
                    )

                    functions[func_name] = function_tool

        return functions

    def _extract_bash_comments(self, lines: List[str], func_line: int) -> Optional[str]:
        """Extract comment block above function."""
        comment_lines: list[str] = []

        # Look backwards for comment block
        for i in range(func_line - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith("#"):
                comment_lines.insert(0, line)
            elif not line:
                continue
            else:
                break

        return "\n".join(comment_lines) if comment_lines else None

    def _extract_bash_description(self, comments: Optional[str]) -> str:
        """Extract description from comments."""
        if not comments:
            return "No description available"

        lines = comments.split("\n")
        for line in lines:
            line = line.strip().lstrip("#").strip()
            if line and not line.startswith("@"):
                return line

        return "No description available"

    def _extract_bash_inputs(self, comments: Optional[str]) -> List[str]:
        """Extract input parameters from comments."""
        if not comments:
            return []

        inputs = []
        for line in comments.split("\n"):
            line = line.strip().lstrip("#").strip()
            if line.startswith("@param"):
                parts = line.split(maxsplit=2)
                if len(parts) >= 2:
                    inputs.append(f"{parts[1]}: string")

        return inputs

    def _extract_bash_outputs(self, comments: Optional[str]) -> List[str]:
        """Extract return type from comments."""
        if not comments:
            return []

        for line in comments.split("\n"):
            line = line.strip().lstrip("#").strip()
            if line.startswith("@returns") or line.startswith("@return"):
                return ["exit_code: number"]

        return []

    def _extract_bash_error_codes(self, comments: Optional[str]) -> List[str]:
        """Extract error codes from comments."""
        if not comments:
            return []

        error_codes = []
        for line in comments.split("\n"):
            line = line.strip().lstrip("#").strip()
            if line.startswith("@error"):
                parts = line.split()
                if len(parts) > 1:
                    error_codes.append(parts[1])

        return error_codes

    def _extract_bash_side_effects(self, comments: Optional[str]) -> List[str]:
        """Extract side effects from comments."""
        if not comments:
            return []

        side_effects = []
        for line in comments.split("\n"):
            line = line.strip().lstrip("#").strip()
            if line.startswith("@side_effect") or line.startswith("@effects"):
                parts = line.split(maxsplit=1)
                if len(parts) > 1:
                    side_effects.append(parts[1])

        return side_effects


class FunctionDiscoveryRegistry:
    """Registry for managing language-specific function discoverers."""

    def __init__(self) -> None:
        self._discoverers: List[BaseFunctionDiscoverer] = []
        self._register_default_discoverers()

    def _register_default_discoverers(self) -> None:
        """Register default discoverers for supported languages."""
        self._discoverers.extend(
            [
                PythonFunctionDiscoverer(),
                JavaScriptFunctionDiscoverer(),
                BashFunctionDiscoverer(),
            ]
        )

    def register_discoverer(self, discoverer: BaseFunctionDiscoverer) -> None:
        """Register a custom function discoverer."""
        self._discoverers.append(discoverer)

    def get_discoverer_for_language(
        self, language: str
    ) -> Optional[BaseFunctionDiscoverer]:
        """Get discoverer for specified language."""
        for discoverer in self._discoverers:
            if discoverer.can_handle_language(language):
                return discoverer
        return None

    def get_discoverer_for_extension(
        self, extension: str
    ) -> Optional[BaseFunctionDiscoverer]:
        """Get discoverer for specified file extension."""
        for discoverer in self._discoverers:
            if discoverer.can_handle_extension(extension):
                return discoverer
        return None

    def discover_functions_in_file(
        self, file_path: Path, content: str
    ) -> Dict[str, FunctionTool]:
        """Discover functions in file using appropriate discoverer."""
        discoverer = self.get_discoverer_for_extension(file_path.suffix)
        if discoverer:
            return discoverer.discover_functions(content, file_path)
        return {}

    def discover_functions_for_language(
        self, language: str, content: str
    ) -> Dict[str, FunctionTool]:
        """Discover functions for specified language."""
        discoverer = self.get_discoverer_for_language(language)
        if discoverer:
            return discoverer.discover_functions(content)
        return {}


# Global registry instance
function_discovery_registry = FunctionDiscoveryRegistry()
