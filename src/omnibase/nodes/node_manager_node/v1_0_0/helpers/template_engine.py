# === OmniNode:Metadata ===
# author: OmniNode Team
# copyright: OmniNode Team
# created_at: '2025-05-28T09:37:45.142242'
# description: Stamped by PythonHandler
# entrypoint: python://template_engine.py
# hash: 420a8d5c84baaec2a99fd485b9bdf9d1b26a0720d17bd9fb1986d8975f2e9d47
# last_modified_at: '2025-05-29T11:50:11.414887+00:00'
# lifecycle: active
# meta_type: tool
# metadata_version: 0.1.0
# name: template_engine.py
# namespace: omnibase.template_engine
# owner: OmniNode Team
# protocol_version: 0.1.0
# runtime_language_hint: python>=3.11
# schema_version: 0.1.0
# state_contract: state_contract://default
# tools: null
# uuid: 3116c402-10cf-49f7-ae6f-f364ad5eeb3d
# version: 1.0.0
# === /OmniNode:Metadata ===


"""
Template processing engine for NodeGeneratorNode.

Handles template file processing, placeholder replacement, and customization
of generated node files.
"""

import re
from pathlib import Path
from typing import Any, Dict, List

from omnibase.core.core_structured_logging import emit_log_event
from omnibase.enums import LogLevelEnum


class TemplateEngine:
    """
    Engine for processing template files and replacing placeholders.
    
    Handles template placeholder replacement, file content customization,
    and template-specific transformations for node generation.
    """
    
    def __init__(self):
        """Initialize the template engine."""
        self.placeholder_pattern = re.compile(r'TEMPLATE[_A-Z]*')
        self.template_comment_pattern = re.compile(r'.*TEMPLATE:.*')
        
    def process_templates(
        self,
        target_path: Path,
        node_name: str,
        author: str,
        customizations: Dict[str, Any]
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
        
        emit_log_event(
            LogLevelEnum.INFO,
            f"Processing templates in {target_path}",
            context={"node_name": node_name}
        )
        
        # Process all Python files
        for py_file in target_path.rglob("*.py"):
            if self._process_python_file(py_file, node_name, author, customizations):
                processed_files.append(str(py_file))
                
        # Process YAML files
        for yaml_file in target_path.rglob("*.yaml"):
            if self._process_yaml_file(yaml_file, node_name, author, customizations):
                processed_files.append(str(yaml_file))
                
        # Process Markdown files
        for md_file in target_path.rglob("*.md"):
            if self._process_markdown_file(md_file, node_name, author, customizations):
                processed_files.append(str(md_file))
                
        emit_log_event(
            LogLevelEnum.INFO,
            f"Processed {len(processed_files)} template files",
            context={"processed_files": processed_files}
        )
        
        return processed_files
    
    def _process_python_file(
        self,
        file_path: Path,
        node_name: str,
        author: str,
        customizations: Dict[str, Any]
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
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Replace template-specific patterns
            replacements = {
                'template_node': f'{node_name}_node',
                'TemplateNode': self._to_pascal_case(node_name) + 'Node',
                'template': node_name,
                'TEMPLATE': node_name.upper(),
                'Template': self._to_pascal_case(node_name),
                'OmniNode Team': author,
            }
            
            # Apply custom replacements
            replacements.update(customizations)
            
            # Perform replacements
            for old, new in replacements.items():
                content = content.replace(old, str(new))
            
            # Remove template comments
            lines = content.split('\n')
            filtered_lines = []
            for line in lines:
                if not self.template_comment_pattern.match(line.strip()):
                    filtered_lines.append(line)
            content = '\n'.join(filtered_lines)
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            emit_log_event(
                LogLevelEnum.WARNING,
                f"Failed to process Python file {file_path}: {e}",
                context={"file_path": str(file_path)}
            )
            
        return False
    
    def _process_yaml_file(
        self,
        file_path: Path,
        node_name: str,
        author: str,
        customizations: Dict[str, Any]
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
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Replace template-specific patterns
            replacements = {
                'template_node': f'{node_name}_node',
                'template': node_name,
                'TEMPLATE': node_name.upper(),
                'Template': self._to_pascal_case(node_name),
                'OmniNode Team': author,
            }
            
            # Apply custom replacements
            replacements.update(customizations)
            
            # Perform replacements
            for old, new in replacements.items():
                content = content.replace(old, str(new))
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            emit_log_event(
                LogLevelEnum.WARNING,
                f"Failed to process YAML file {file_path}: {e}",
                context={"file_path": str(file_path)}
            )
            
        return False
    
    def _process_markdown_file(
        self,
        file_path: Path,
        node_name: str,
        author: str,
        customizations: Dict[str, Any]
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
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Replace template-specific patterns
            replacements = {
                'template_node': f'{node_name}_node',
                'template': node_name,
                'TEMPLATE': node_name.upper(),
                'Template': self._to_pascal_case(node_name),
                'OmniNode Team': author,
            }
            
            # Apply custom replacements
            replacements.update(customizations)
            
            # Perform replacements
            for old, new in replacements.items():
                content = content.replace(old, str(new))
            
            # Write back if changed
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
                
        except Exception as e:
            emit_log_event(
                LogLevelEnum.WARNING,
                f"Failed to process Markdown file {file_path}: {e}",
                context={"file_path": str(file_path)}
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
        components = snake_str.split('_')
        return ''.join(word.capitalize() for word in components)
