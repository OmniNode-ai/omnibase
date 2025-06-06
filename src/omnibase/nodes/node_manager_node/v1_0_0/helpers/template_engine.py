"""
Template processing engine for NodeGeneratorNode.

Handles template file processing, placeholder replacement, and customization
of generated node files.
"""

import re
from pathlib import Path
from typing import Any, Dict, List

from omnibase.core.core_structured_logging import emit_log_event_sync
from omnibase.enums import LogLevelEnum
from omnibase.runtimes.onex_runtime.v1_0_0.utils.logging_utils import make_log_context


class TemplateEngine:
    """
    Engine for processing template files and replacing placeholders.

    Handles template placeholder replacement, file content customization,
    and template-specific transformations for node generation.
    """

    def __init__(self, event_bus=None):
        """Initialize the template engine."""
        self.placeholder_pattern = re.compile("TEMPLATE[_A-Z]*")
        self.template_comment_pattern = re.compile(".*TEMPLATE:.*")
        self._event_bus = event_bus

    def process_templates(
        self,
        target_path: Path,
        node_name: str,
        author: str,
        customizations: Dict[str, Any],
    ) -> List[str]:
        """
        Process all template files in the target directory.

        Args:
            target_path: Path to the generated node directory
            node_name: Name of the new node
            author: Author name for metadata
            customizations: Custom values for placeholder replacement

        Returns:
            List of processed file paths
        """
        processed_files = []
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Processing templates in {target_path}",
            context=make_log_context(node_id=node_name),
            event_bus=self._event_bus,
        )
        for py_file in target_path.rglob("*.py"):
            if self._process_python_file(py_file, node_name, author, customizations):
                processed_files.append(str(py_file))
        for yaml_file in target_path.rglob("*.yaml"):
            if self._process_yaml_file(yaml_file, node_name, author, customizations):
                processed_files.append(str(yaml_file))
        for md_file in target_path.rglob("*.md"):
            if self._process_markdown_file(md_file, node_name, author, customizations):
                processed_files.append(str(md_file))
        emit_log_event_sync(
            LogLevelEnum.INFO,
            f"Processed {len(processed_files)} template files",
            context=make_log_context(
                node_id=node_name, processed_files=processed_files
            ),
            event_bus=self._event_bus,
        )
        return processed_files

    def _process_python_file(
        self,
        file_path: Path,
        node_name: str,
        author: str,
        customizations: Dict[str, Any],
    ) -> bool:
        """
        Process a Python template file.

        Args:
            file_path: Path to the Python file
            node_name: Name of the new node
            author: Author name
            customizations: Custom values

        Returns:
            True if file was modified, False otherwise
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            replacements = {
                "node_template": f"{node_name}_node",
                "NodeTemplate": self._to_pascal_case(node_name) + "Node",
                "template": node_name,
                "TEMPLATE": node_name.upper(),
                "Template": self._to_pascal_case(node_name),
                "OmniNode Team": author,
            }
            replacements.update(customizations)
            for old, new in replacements.items():
                content = content.replace(old, str(new))
            lines = content.split("\n")
            filtered_lines = []
            for line in lines:
                if not self.template_comment_pattern.match(line.strip()):
                    filtered_lines.append(line)
            content = "\n".join(filtered_lines)
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                return True
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"Failed to process Python file {file_path}: {e}",
                context=make_log_context(node_id=node_name, file_path=str(file_path)),
                event_bus=self._event_bus,
            )
        return False

    def _process_yaml_file(
        self,
        file_path: Path,
        node_name: str,
        author: str,
        customizations: Dict[str, Any],
    ) -> bool:
        """
        Process a YAML template file.

        Args:
            file_path: Path to the YAML file
            node_name: Name of the new node
            author: Author name
            customizations: Custom values

        Returns:
            True if file was modified, False otherwise
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            replacements = {
                "node_template": f"{node_name}_node",
                "template": node_name,
                "TEMPLATE": node_name.upper(),
                "Template": self._to_pascal_case(node_name),
                "OmniNode Team": author,
            }
            replacements.update(customizations)
            for old, new in replacements.items():
                content = content.replace(old, str(new))
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                return True
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"Failed to process YAML file {file_path}: {e}",
                context=make_log_context(node_id=node_name, file_path=str(file_path)),
                event_bus=self._event_bus,
            )
        return False

    def _process_markdown_file(
        self,
        file_path: Path,
        node_name: str,
        author: str,
        customizations: Dict[str, Any],
    ) -> bool:
        """
        Process a Markdown template file.

        Args:
            file_path: Path to the Markdown file
            node_name: Name of the new node
            author: Author name
            customizations: Custom values

        Returns:
            True if file was modified, False otherwise
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            replacements = {
                "node_template": f"{node_name}_node",
                "template": node_name,
                "TEMPLATE": node_name.upper(),
                "Template": self._to_pascal_case(node_name),
                "OmniNode Team": author,
            }
            replacements.update(customizations)
            for old, new in replacements.items():
                content = content.replace(old, str(new))
            if content != original_content:
                file_path.write_text(content, encoding="utf-8")
                return True
        except Exception as e:
            emit_log_event_sync(
                LogLevelEnum.WARNING,
                f"Failed to process Markdown file {file_path}: {e}",
                context=make_log_context(node_id=node_name, file_path=str(file_path)),
                event_bus=self._event_bus,
            )
        return False

    def _to_pascal_case(self, snake_str: str) -> str:
        """
        Convert snake_case to PascalCase.

        Args:
            snake_str: String in snake_case format

        Returns:
            String in PascalCase format
        """
        components = snake_str.split("_")
        return "".join(word.capitalize() for word in components)
